"""
PhenotypingEngine — 200項目問診→PATH_01〜05スコア変換
MBT55電子散逸理論（dH₂/dt≈0）をPATH_04に統合
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from ..core.config import (
    config, PathID, Language, PATH_DEFINITIONS
)

logger = logging.getLogger(__name__)


@dataclass
class PhenotypeScore:
    """単一PATHのスコア"""
    path_id: PathID
    score: float  # 0-100
    level: str    # "良好" / "注意" / "要改善"
    
    @property
    def is_low(self) -> bool:
        return self.score < config.path_thresholds[self.path_id.value]


@dataclass
class PhenotypeResult:
    """フェノタイピング全体結果"""
    scores: Dict[PathID, PhenotypeScore]
    overall_status: str
    low_paths: List[PathID]
    recommendations: List[str]
    language: Language = Language.JA
    
    def to_dict(self) -> Dict:
        defs = PATH_DEFINITIONS[self.language]
        return {
            "scores": {
                pid.value: {
                    "score": ps.score,
                    "level": ps.level,
                    "name": defs[pid]["name"],
                    "short": defs[pid]["short"],
                    "is_low": ps.is_low,
                    "meaning": defs[pid]["high_meaning"] if ps.score >= 50 else defs[pid]["low_meaning"],
                }
                for pid, ps in self.scores.items()
            },
            "overall_status": self.overall_status,
            "low_paths": [p.value for p in self.low_paths],
            "recommendations": self.recommendations,
        }


class PhenotypingEngine:
    """
    フェノタイピングエンジン
    問診回答 → PATH_01〜05スコア（0-100）計算
    """
    
    def __init__(
        self,
        weight_matrix_path: Optional[Path] = None,
        language: Language = Language.JA,
    ):
        self.language = language
        self.weight_matrix_path = weight_matrix_path or config.get_phenotype_weight_path()
        self.weight_matrix: Dict = {}
        self._load_weight_matrix()
        logger.info(f"PhenotypingEngine initialized (lang={language.value})")
    
    def _load_weight_matrix(self):
        """重み行列の読み込み"""
        if self.weight_matrix_path.exists():
            with open(self.weight_matrix_path, "r", encoding="utf-8") as f:
                self.weight_matrix = json.load(f)
        else:
            logger.warning(f"Weight matrix not found: {self.weight_matrix_path}")
            self._use_default_weights()
    
    def _use_default_weights(self):
        """デフォルト重み行列"""
        self.weight_matrix = {
            "PATH_01_消化吸収": {
                "related_symptoms": ["胃もたれ", "便秘", "下痢", "朝食欠食", "消化不良", "食欲不振", "腹部膨満感"],
                "weight": 0.25,
            },
            "PATH_02_肝解毒": {
                "related_symptoms": ["疲れやすい", "酒に弱い", "肌荒れ", "吹き出物", "目の疲れ", "頭痛"],
                "weight": 0.20,
            },
            "PATH_03_糖代謝エネルギ": {
                "related_symptoms": ["甘いもの依存", "午後眠気", "冷え", "むくみ", "運動不足", "肥満傾向"],
                "weight": 0.20,
            },
            "PATH_04_酸化還元バランス": {
                "related_symptoms": ["炎症", "アレルギー", "関節痛", "筋肉痛", "敏感肌", "慢性疲労"],
                "weight": 0.20,
            },
            "PATH_05_脳神経ミトコンドリア": {
                "related_symptoms": ["集中力低下", "気分落込", "不眠", "記憶力低下", "不安感"],
                "weight": 0.15,
            },
        }
    
    def score_phenotype(self, answers: Dict[str, bool]) -> PhenotypeResult:
        """
        問診回答からPATH_01〜05スコアを計算
        
        Args:
            answers: {症状名: True/False} の形式
        Returns:
            PhenotypeResult（全PATHスコア）
        """
        path_defs = PATH_DEFINITIONS[self.language]
        
        # PATH名→PathIDのマッピング
        path_name_to_id = {
            "PATH_01_消化吸収": PathID.PATH_01,
            "PATH_02_肝解毒": PathID.PATH_02,
            "PATH_03_糖代謝エネルギ": PathID.PATH_03,
            "PATH_04_酸化還元バランス": PathID.PATH_04,
            "PATH_05_脳神経ミトコンドリア": PathID.PATH_05,
        }
        
        scores: Dict[PathID, PhenotypeScore] = {}
        low_paths: List[PathID] = []
        
        for path_key, path_data in self.weight_matrix.items():
            related = path_data.get("related_symptoms", [])
            weight = path_data.get("weight", 0.2)
            
            # 関連症状のうち、回答で「あり」とされたものの割合
            if not related:
                score = 100.0
            else:
                positive_count = sum(1 for s in related if answers.get(s, False))
                ratio = positive_count / len(related)
                # 症状が多いほどスコア低下（100→0）
                score = max(0.0, 100.0 * (1.0 - ratio))
            
            # PATH_04増幅：D012系（免疫・炎症）症状が多い場合
            if path_key == "PATH_04_酸化還元バランス":
                inflammation_keywords = ["炎症", "アレルギー", "自己免疫", "敏感肌"]
                inflammation_count = sum(1 for k in inflammation_keywords if answers.get(k, False))
                if inflammation_count >= 2:
                    score = max(0.0, score * 0.7)  # スコアを30%悪化
            
            pid = path_name_to_id.get(path_key, PathID.PATH_01)
            
            # レベル判定
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
        
        # 全体ステータス
        avg_score = sum(s.score for s in scores.values()) / len(scores)
        if avg_score >= 70:
            overall = "良好（Good）"
        elif avg_score >= 40:
            overall = "注意（Caution）"
        else:
            overall = "要改善（Needs Improvement）"
        
        # 推奨事項生成
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
        self, scores: Dict[PathID, PhenotypeScore], low_paths: List[PathID]
    ) -> List[str]:
        """不足PATHに基づく推奨事項生成"""
        path_defs = PATH_DEFINITIONS[self.language]
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
                    f"【{defn.get('name', pid.value)}】の改善が必要です。"
                    f"推奨MBT55メタ株: {meta_name}（{meta_id}）\n"
                    f"  理由: {defn.get('mb55_link', '')}"
                )
        else:
            for pid in low_paths:
                meta_id, meta_name = path_to_meta.get(pid, ("", ""))
                defn = path_defs.get(pid, {})
                recommendations.append(
                    f"[{defn.get('name', pid.value)}] needs improvement. "
                    f"Recommended MBT55 Meta-Strain: {meta_name} ({meta_id})\n"
                    f"  Reason: {defn.get('mb55_link', '')}"
                )
        
        return recommendations


def demo_phenotype() -> PhenotypeResult:
    """デモ用：典型的な問診パターンでフェノタイピング"""
    engine = PhenotypingEngine(language=Language.JA)
    
    # 典型的な「糖代謝低下＋酸化ストレス」パターン
    demo_answers = {
        "甘いもの依存": True,
        "午後眠気": True,
        "冷え": True,
        "疲れやすい": True,
        "肌荒れ": True,
        "炎症": True,
        "アレルギー": True,
        "集中力低下": True,
        "不眠": False,
        "便秘": True,
        "胃もたれ": False,
        "朝食欠食": True,
        "酒に弱い": False,
        "関節痛": True,
        "気分落込": False,
        "むくみ": True,
    }
    
    result = engine.score_phenotype(demo_answers)
    return result