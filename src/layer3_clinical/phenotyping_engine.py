"""
PhenotypingEngine — JSON不要・コード内データで確実動作
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


# ★★★ コード内に直接埋め込み（JSON不要） ★★★
PATH_SYMPTOMS = {
    "PATH_01": {
        "name": "消化吸収・腸管バリア",
        "symptoms": ["朝食欠食", "胃もたれ", "便秘", "下痢", "腹部膨満感", "消化不良", "食欲不振", "胸やけ", "吐き気",
                      "食事の時間が不定である", "朝食を抜くことがよくある", "よく寝る前に夜食を食べる", "早食いである",
                      "腹いっぱい食べる", "食後に眠くなる", "空腹時に胃が痛む", "げっぷが多い", "脂っこいものが苦手"],
        "weight": 0.25,
    },
    "PATH_02": {
        "name": "肝解毒・フェーズI/II",
        "symptoms": ["疲れやすい", "酒に弱い", "肌荒れ", "吹き出物", "目の疲れ", "頭痛", "金属アレルギー", "薬疹",
                      "二日酔いしやすい", "右肋骨下の張り", "苦味を感じやすい", "慢性的な炎症", "化学物質過敏症"],
        "weight": 0.20,
    },
    "PATH_03": {
        "name": "糖代謝・エネルギー産生",
        "symptoms": ["甘いもの依存", "午後眠気", "冷え", "むくみ", "運動不足", "肥満傾向", "血糖値変動", "脱力感",
                      "朝起きられない", "食後急激な眠気", "喉が渇きやすい", "低血糖症状（手の震え・冷や汗）"],
        "weight": 0.20,
    },
    "PATH_04": {
        "name": "酸化還元バランス・電子散逸",
        "symptoms": ["炎症", "アレルギー", "自己免疫疾患", "慢性疲労", "敏感肌", "関節痛", "筋肉痛",
                      "アレルギー性鼻炎", "花粉症", "食物アレルギー", "アトピー性皮膚炎", "原因不明の微熱",
                      "自己免疫疾患の診断あり", "湿疹", "じんましん"],
        "weight": 0.20,
    },
    "PATH_05": {
        "name": "脳神経・ミトコンドリア機能",
        "symptoms": ["集中力低下", "気分落込", "不眠", "記憶力低下", "自律神経失調", "うつ傾向", "不安感", "パニック",
                      "イライラ", "ブレインフォグ", "寝つきが悪い", "中途覚醒", "悪夢をよく見る", "やる気が出ない",
                      "めまい", "立ちくらみ", "耳鳴り"],
        "weight": 0.15,
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
    """JSON不要のフェノタイピングエンジン"""

    def __init__(self, weight_matrix_path=None, language="ja"):
        self.language = language
        logger.info("PhenotypingEngine ready (code-embedded data)")

    def score_phenotype(self, answers: Dict[str, bool]) -> PhenotypeResult:
        scores = {}
        low_paths = []

        for pid, path_data in PATH_SYMPTOMS.items():
            symptoms = path_data["symptoms"]
            if not symptoms:
                score = 100.0
            else:
                positive = sum(1 for s in symptoms if answers.get(s, False))
                ratio = positive / len(symptoms)
                score = max(0.0, 100.0 * (1.0 - ratio))

            # PATH_04増幅：炎症症状が2個以上で悪化
            if pid == "PATH_04":
                inflam_keywords = ["炎症", "アレルギー", "自己免疫疾患", "敏感肌"]
                inflam_count = sum(1 for kw in inflam_keywords if answers.get(kw, False))
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
            name = PATH_SYMPTOMS.get(pid, {}).get("name", pid)
            recommendations.append(f"【{name}】の改善が必要です。推奨: {meta_name}（{meta_id}）")

        logger.info(f"Phenotype: overall={overall}, low={low_paths}, avg={avg:.1f}")
        return PhenotypeResult(scores, overall, low_paths, recommendations, self.language)
