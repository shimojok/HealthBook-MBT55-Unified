"""
PhenotypingEngine — 200項目問診→PATH_01〜05スコア変換
MBT55電子散逸理論（dH₂/dt≈0）をPATH_04に統合
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

from ..core.config import (
    config, PathID, Language, PATH_DEFINITIONS
)

logger = logging.getLogger(__name__)


@dataclass
class PhenotypeScore:
    """単一PATHのスコア"""
    path_id: PathID
    score: float
    level: str

    @property
    def is_low(self) -> bool:
        threshold = config.path_thresholds.get(self.path_id.value, 40.0)
        return self.score < threshold


@dataclass
class PhenotypeResult:
    """フェノタイピング全体結果"""
    scores: Dict[PathID, PhenotypeScore]
    overall_status: str
    low_paths: List[PathID]
    recommendations: List[str]
    language: Language = Language.JA

    def to_dict(self) -> Dict:
        defs = PATH_DEFINITIONS.get(self.language, {})
        result_scores = {}
        for pid, ps in self.scores.items():
            path_def = defs.get(pid, {})
            result_scores[pid.value] = {
                "score": ps.score,
                "level": ps.level,
                "name": path_def.get("name", pid.value),
                "short": path_def.get("short", pid.value),
                "is_low": ps.is_low,
                "meaning": (
                    path_def.get("high_meaning", "")
                    if ps.score >= 50
                    else path_def.get("low_meaning", "")
                ),
            }
        return {
            "scores": result_scores,
            "overall_status": self.overall_status,
            "low_paths": [p.value for p in self.low_paths],
            "recommendations": self.recommendations,
        }


class PhenotypingEngine:
    """フェノタイピングエンジン"""

    PATH_KEY_MAP = {
        "PATH_01_消化吸収": PathID.PATH_01,
        "PATH_02_肝解毒": PathID.PATH_02,
        "PATH_03_糖代謝エネルギ": PathID.PATH_03,
        "PATH_04_酸化還元バランス": PathID.PATH_04,
        "PATH_05_脳神経ミトコンドリア": PathID.PATH_05,
    }

    def __init__(
        self,
        weight_matrix_path: Optional[Path] = None,
        language: Language = Language.JA,
    ):
        self.language = language
        self.weight_matrix_path = (
            weight_matrix_path or config.get_phenotype_weight_path()
        )
        self.weight_matrix: Dict = {}
        self._load_weight_matrix()
        logger.info(f"PhenotypingEngine initialized (lang={language.value})")

    def _load_weight_matrix(self):
        """重み行列の読み込み"""
        loaded = False
        if self.weight_matrix_path.exists():
            try:
                with open(self.weight_matrix_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if "path_definitions" in data:
                    self.weight_matrix = data["path_definitions"]
                else:
                    self.weight_matrix = data
                loaded = True
                logger.info(f"Weight matrix loaded: {len(self.weight_matrix)} keys")
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                logger.warning(f"Failed to load weight matrix: {e}")

        if not loaded or not self.weight_matrix:
            logger.warning("Using default weight matrix")
            self.weight_matrix = self._default_weights()

    def _default_weights(self) -> Dict:
        """デフォルト重み行列"""
        return {
            "PATH_01_消化吸収": {
                "related_symptoms": [
                    "朝食欠食", "胃もたれ", "便秘", "下痢", "腹部膨満感",
                    "消化不良", "食欲不振", "胸やけ", "吐き気",
                ],
                "weight": 0.25,
            },
            "PATH_02_肝解毒": {
                "related_symptoms": [
                    "疲れやすい", "酒に弱い", "肌荒れ", "吹き出物",
                    "目の疲れ", "頭痛", "金属アレルギー", "薬疹",
                ],
                "weight": 0.20,
            },
            "PATH_03_糖代謝エネルギ": {
                "related_symptoms": [
                    "甘いもの依存", "午後眠気", "冷え", "むくみ",
                    "運動不足", "肥満傾向", "血糖値変動", "脱力感",
                ],
                "weight": 0.20,
            },
            "PATH_04_酸化還元バランス": {
                "related_symptoms": [
                    "炎症", "アレルギー", "自己免疫疾患", "慢性疲労",
                    "敏感肌", "化学物質過敏症", "関節痛", "筋肉痛",
                ],
                "weight": 0.20,
            },
            "PATH_05_脳神経ミトコンドリア": {
                "related_symptoms": [
                    "集中力低下", "気分落込", "不眠", "記憶力低下",
                    "自律神経失調", "うつ傾向", "不安感", "パニック",
                ],
                "weight": 0.15,
            },
        }

    def score_phenotype(self, answers: Dict[str, bool]) -> PhenotypeResult:
        """問診回答からPATH_01〜05スコアを計算"""
        path_defs = PATH_DEFINITIONS.get(self.language, {})
        scores: Dict[PathID, PhenotypeScore] = {}
        low_paths: List[PathID] = []

        for path_key, path_data in self.weight_matrix.items():
            # 辞書型のみ処理
            if not isinstance(path_data, dict):
                continue
            # PATH_ で始まるキーのみ処理
            if not path_key.startswith("PATH_"):
                continue

            related = path_data.get("related_symptoms", [])
            if not isinstance(related, list):
                related = []

            # 安全にanswersから値を取得
            if not related:
                score = 100.0
            else:
                positive_count = 0
                for symptom in related:
                    try:
                        if answers.get(symptom, False):
                            positive_count += 1
                    except Exception:
                        pass
                ratio = positive_count / len(related)
                score = max(0.0, 100.0 * (1.0 - ratio))

            # PATH_04増幅
            if path_key == "PATH_04_酸化還元バランス":
                inflam_count = 0
                for kw in ["炎症", "アレルギー", "自己免疫疾患", "敏感肌"]:
                    try:
                        if answers.get(kw, False):
                            inflam_count += 1
                    except Exception:
                        pass
                if inflam_count >= 2:
                    score = max(0.0, score * 0.7)

            pid = self.PATH_KEY_MAP.get(path_key)
            if pid is None:
                continue

            if score >= 70:
                level = "良好"
            elif score >= 40:
                level = "注意"
            else:
                level = "要改善"
                low_paths.append(pid)

            scores[pid] = PhenotypeScore(
                path_id=pid,
                score=round(score, 1),
                level=level,
            )

        # フォールバック
        if not scores:
            for pid in PathID:
                scores[pid] = PhenotypeScore(
                    path_id=pid, score=100.0, level="良好"
                )

        # 全体ステータス
        total = sum(s.score for s in scores.values())
        count = max(len(scores), 1)
        avg_score = total / count
        if avg_score >= 70:
            overall = "良好（Good）"
        elif avg_score >= 40:
            overall = "注意（Caution）"
        else:
            overall = "要改善（Needs Improvement）"

        recommendations = self._generate_recommendations(scores, low_paths)

        logger.info(
            f"Phenotype scored: overall={overall}, "
            f"low_paths={[p.value for p in low_paths]}"
        )

        return PhenotypeResult(
            scores=scores,
            overall_status=overall,
            low_paths=low_paths,
            recommendations=recommendations,
            language=self.language,
        )

    def _generate_recommendations(
        self,
        scores: Dict[PathID, PhenotypeScore],
        low_paths: List[PathID],
    ) -> List[str]:
        """不足PATHに基づく推奨事項生成"""
        path_defs = PATH_DEFINITIONS.get(self.language, {})
        recommendations = []

        path_to_meta = {
            PathID.PATH_01: ("MBT_META_01", "一次分解・乳酸生成コンソーシアム"),
            PathID.PATH_02: ("MBT_META_02", "難分解物破砕・電子シャトル形成"),
            PathID.PATH_03: ("MBT_META_05", "安定化・酪酸生成グループ"),
            PathID.PATH_04: ("MBT_META_04", "電子駆動・ミネラル可溶化"),
            PathID.PATH_05: ("MBT_META_03", "エクオール・活性代謝物特化"),
        }

        if self.language == Language.JA:
            for pid in low_paths:
                meta_id, meta_name = path_to_meta.get(pid, ("", ""))
                defn = path_defs.get(pid, {})
                recommendations.append(
                    f"【{defn.get('name', pid.value)}】の改善が必要です。\n"
                    f"推奨MBT55メタ株: {meta_name}（{meta_id}）\n"
                    f"理由: {defn.get('mb55_link', '代謝経路の補完が必要')}"
                )
        else:
            for pid in low_paths:
                meta_id, meta_name = path_to_meta.get(pid, ("", ""))
                defn = path_defs.get(pid, {})
                recommendations.append(
                    f"[{defn.get('name', pid.value)}] needs improvement.\n"
                    f"Recommended MBT55 Meta-Strain: {meta_name} ({meta_id})\n"
                    f"Reason: {defn.get('mb55_link', 'Metabolic pathway compensation needed')}"
                )

        return recommendations