"""
PhenotypingEngine — 質問文完全一致 + キーワード部分一致のハイブリッド
"""
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class PhenotypeScore:
    def __init__(self, path_id: str, score: float, level: str):
        self.path_id = path_id
        self.score = score
        self.level = level

    @property
    def is_low(self) -> bool:
        return self.score < 40.0


class PhenotypeResult:
    def __init__(self, scores: Dict, overall: str, low_paths: List, recommendations: List, language="ja"):
        self.scores = scores
        self.overall_status = overall
        self.low_paths = low_paths
        self.recommendations = recommendations
        self.language = language

    def to_dict(self):
        names = {
            "PATH_01": "消化吸収・腸管バリア", "PATH_02": "肝解毒・フェーズI/II",
            "PATH_03": "糖代謝・エネルギー産生", "PATH_04": "酸化還元バランス・電子散逸",
            "PATH_05": "脳神経・ミトコンドリア機能",
        }
        return {
            "scores": {
                pid: {"score": ps.score, "level": ps.level, "name": names.get(pid, pid),
                      "short": names.get(pid, pid), "is_low": ps.is_low}
                for pid, ps in self.scores.items()
            },
            "overall_status": self.overall_status,
            "low_paths": self.low_paths,
            "recommendations": self.recommendations,
        }


# ★★★ 質問文に含まれるキーワードでマッチング ★★★
PATH_KEYWORDS = {
    "PATH_01": {
        "name": "消化吸収・腸管バリア",
        "keywords": [
            "食事の時間", "朝食を抜く", "夜食", "早食い", "腹いっぱい",
            "食後に眠くなる", "空腹時に胃", "げっぷ", "脂っこい",
            "胃もたれ", "胸やけ", "吐き気", "便秘", "下痢",
            "腹部膨満感", "消化不良", "食欲不振", "口渇", "口内炎",
            "歯ぐき", "喉がつかえる",
        ],
    },
    "PATH_02": {
        "name": "肝解毒・フェーズI/II",
        "keywords": [
            "酒に弱い", "二日酔い", "肌荒れ", "吹き出物", "目の疲れ",
            "頭痛", "金属アレルギー", "薬疹", "右肋骨", "苦味",
            "化学物質過敏症", "慢性の咳", "喘息", "痰", "鼻づまり",
            "疲れやすい",
        ],
    },
    "PATH_03": {
        "name": "糖代謝・エネルギー産生",
        "keywords": [
            "甘いもの", "午後眠気", "冷え", "むくみ", "運動不足",
            "肥満", "血糖値", "脱力感", "朝起きられない",
            "食後急激な眠気", "喉が渇きやすい", "低血糖", "手の震え",
            "冷や汗", "体重変動", "痩せすぎ",
        ],
    },
    "PATH_04": {
        "name": "酸化還元バランス・電子散逸",
        "keywords": [
            "炎症", "アレルギー", "自己免疫", "慢性疲労", "敏感肌",
            "関節痛", "筋肉痛", "花粉症", "アトピー", "微熱",
            "湿疹", "じんましん", "皮膚の色素沈着", "微熱が続く",
            "リンパの腫れ",
        ],
    },
    "PATH_05": {
        "name": "脳神経・ミトコンドリア機能",
        "keywords": [
            "集中力", "気分", "不眠", "記憶力", "自律神経", "うつ",
            "不安", "パニック", "イライラ", "ブレインフォグ",
            "寝つき", "中途覚醒", "悪夢", "やる気", "めまい",
            "立ちくらみ", "耳鳴り", "寝汗", "ドライアイ",
        ],
    },
}

PATH_META = {
    "PATH_01": ("MBT_META_01", "一次分解・乳酸生成コンソーシアム"),
    "PATH_02": ("MBT_META_02", "難分解物破砕・電子シャトル形成"),
    "PATH_03": ("MBT_META_05", "安定化・酪酸生成グループ"),
    "PATH_04": ("MBT_META_04", "電子駆動・ミネラル可溶化"),
    "PATH_05": ("MBT_META_03", "エクオール・活性代謝物特化"),
}


class PhenotypingEngine:
    """キーワード部分一致方式（質問文に対応）"""

    def __init__(self, weight_matrix_path=None, language="ja"):
        self.language = language
        logger.info(f"PhenotypingEngine ready (keyword matching, lang={language})")

    def score_phenotype(self, answers: Dict[str, bool]) -> PhenotypeResult:
        scores = {}
        low_paths = []

        # True の質問文だけ抽出
        true_questions = [q for q, v in answers.items() if v]
        logger.info(f"True answers: {len(true_questions)} / {len(answers)}")

        if not true_questions:
            # 何もチェックなし → 全PATH=100%
            for pid, path_data in PATH_KEYWORDS.items():
                scores[pid] = PhenotypeScore(pid, 100.0, "良好")
            return PhenotypeResult(scores, "良好（Good）", [], [], self.language)

        for pid, path_data in PATH_KEYWORDS.items():
            keywords = path_data["keywords"]

            # いくつのキーワードがtrue_questionsのいずれかに部分一致するか
            matched = 0
            for kw in keywords:
                if any(kw in q for q in true_questions):
                    matched += 1

            ratio = matched / len(keywords) if keywords else 0
            score = max(0.0, 100.0 * (1.0 - ratio))

            # PATH_04増幅：炎症系キーワードが2個以上で悪化
            if pid == "PATH_04":
                inflam_kw = ["炎症", "アレルギー", "自己免疫", "敏感肌"]
                inflam_count = sum(1 for kw in inflam_kw if any(kw in q for q in true_questions))
                if inflam_count >= 2:
                    score = max(0.0, score * 0.7)

            if score >= 70:
                level = "良好"
            elif score >= 40:
                level = "注意"
            else:
                level = "要改善"
                low_paths.append(pid)

            scores[pid] = PhenotypeScore(pid, round(score, 1), level)
            logger.info(f"{pid}: matched={matched}/{len(keywords)}, score={score:.1f}, level={level}")

        total = sum(s.score for s in scores.values())
        avg = total / max(len(scores), 1)
        if avg >= 70:
            overall = "良好（Good）"
        elif avg >= 40:
            overall = "注意（Caution）"
        else:
            overall = "要改善（Needs Improvement）"

        recommendations = []
        for pid in low_paths:
            meta_id, meta_name = PATH_META.get(pid, ("", ""))
            name = PATH_KEYWORDS.get(pid, {}).get("name", pid)
            recommendations.append(f"【{name}】の改善が必要です。推奨: {meta_name}（{meta_id}）")

        logger.info(f"Phenotype: overall={overall}, low={low_paths}, avg={avg:.1f}")
        return PhenotypeResult(scores, overall, low_paths, recommendations, self.language)
