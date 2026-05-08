"""
MBT Probiotics Screening Engine
不足PATHスコア → 最適菌株セット提案 + 漢方・ファイトケミカル推奨
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass

from ..core.config import (
    config, PathID, MetaStrainID, Language, META_STRAIN_DEFINITIONS
)
from ..layer3_clinical.phenotyping_engine import PhenotypeResult

logger = logging.getLogger(__name__)


@dataclass
class StrainRecommendation:
    """単一菌株の推奨"""
    strain_id: MetaStrainID
    name: str
    priority: int  # 1=最高, 5=最低
    target_path: PathID
    reason: str
    cascade_stage: int
    optimal_conditions: Dict
    compatible_substrates: List[str]


@dataclass
class ScreeningResult:
    """スクリーニング全体結果"""
    low_paths: List[PathID]
    recommended_strains: List[StrainRecommendation]
    combination_proposal: str
    expected_effects: List[str]
    language: Language = Language.JA
    
    def to_dict(self) -> Dict:
        return {
            "low_paths": [p.value for p in self.low_paths],
            "recommended_strains": [
                {
                    "strain_id": rs.strain_id.value,
                    "name": rs.name,
                    "priority": rs.priority,
                    "target_path": rs.target_path.value,
                    "reason": rs.reason,
                    "cascade_stage": rs.cascade_stage,
                    "optimal_conditions": rs.optimal_conditions,
                    "compatible_substrates": rs.compatible_substrates,
                }
                for rs in self.recommended_strains
            ],
            "combination_proposal": self.combination_proposal,
            "expected_effects": self.expected_effects,
        }


class ProbioticScreeningEngine:
    """
    MBT Probiotics スクリーニングエンジン
    PATHスコア → メタ株推奨 → 処方提案
    """
    
    def __init__(
        self,
        matrix_path: Optional[Path] = None,
        language: Language = Language.JA,
    ):
        self.language = language
        self.matrix_path = matrix_path or config.get_probiotic_matrix_path()
        self.matrix: Dict = {}
        self._load_matrix()
        logger.info(f"ProbioticScreeningEngine initialized (lang={language.value})")
    
    def _load_matrix(self):
        """菌株マトリックス読み込み"""
        if self.matrix_path.exists():
            with open(self.matrix_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.matrix = {s["strain_id"]: s for s in data.get("meta_strains", [])}
        else:
            logger.warning(f"Probiotic matrix not found: {self.matrix_path}")
            self._use_default_matrix()
    
    def _use_default_matrix(self):
        """デフォルトマトリックス"""
        self.matrix = {
            "MBT_META_01": {
                "name": "一次分解・乳酸生成コンソーシアム",
                "target_pathway": "PATH_01",
                "cascade_stage": 1,
                "produces": ["乳酸", "アミノ酸"],
                "substrate_preference": ["葛根", "山薬", "鹿茸"],
                "optimal_conditions": {"temp": 38, "ph": 6.0},
            },
            "MBT_META_02": {
                "name": "難分解物破砕・電子シャトル形成",
                "target_pathway": "PATH_02",
                "cascade_stage": 2,
                "produces": ["キノン化合物", "没食子酸"],
                "substrate_preference": ["緑茶カテキン", "黄連", "ウーロン茶"],
                "optimal_conditions": {"temp": 42, "ph": 5.5},
            },
            "MBT_META_03": {
                "name": "エクオール・活性代謝物特化",
                "target_pathway": "PATH_05",
                "cascade_stage": 2,
                "produces": ["エクオール", "コンパウンドK"],
                "substrate_preference": ["大豆イソフラボン", "葛根", "紅参"],
                "optimal_conditions": {"temp": 40, "ph": 6.5},
            },
            "MBT_META_04": {
                "name": "電子駆動・ミネラル可溶化",
                "target_pathway": "PATH_04",
                "cascade_stage": 3,
                "produces": ["フルボ酸", "可溶化ミネラル"],
                "substrate_preference": ["竜骨", "牡蛎", "鉱物生薬"],
                "optimal_conditions": {"temp": 35, "ph": 6.5},
            },
            "MBT_META_05": {
                "name": "安定化・酪酸生成グループ",
                "target_pathway": "PATH_03",
                "cascade_stage": 3,
                "produces": ["酪酸", "酢酸"],
                "substrate_preference": ["食物繊維", "オリゴ糖"],
                "optimal_conditions": {"temp": 35, "ph": 6.0},
            },
        }
    
    def screen_probiotics(
        self, phenotype_result: PhenotypeResult
    ) -> ScreeningResult:
        """
        フェノタイピング結果から最適菌株をスクリーニング
        
        Args:
            phenotype_result: フェノタイピング結果
        Returns:
            ScreeningResult（推奨菌株リスト）
        """
        low_paths = phenotype_result.low_paths
        
        # PATH → メタ株のマッピング
        path_to_meta: Dict[PathID, MetaStrainID] = {
            PathID.PATH_01: MetaStrainID.META_01,
            PathID.PATH_02: MetaStrainID.META_02,
            PathID.PATH_03: MetaStrainID.META_05,
            PathID.PATH_04: MetaStrainID.META_04,
            PathID.PATH_05: MetaStrainID.META_03,
        }
        
        strain_defs = META_STRAIN_DEFINITIONS[self.language]
        recommendations: List[StrainRecommendation] = []
        
        for priority, path_id in enumerate(low_paths, 1):
            strain_id = path_to_meta.get(path_id)
            if strain_id and strain_id.value in self.matrix:
                matrix_data = self.matrix[strain_id.value]
                strain_def = strain_defs.get(strain_id, {})
                
                reason = self._generate_reason(path_id, strain_id)
                
                recommendations.append(StrainRecommendation(
                    strain_id=strain_id,
                    name=strain_def.get("name", matrix_data.get("name", "")),
                    priority=priority,
                    target_path=path_id,
                    reason=reason,
                    cascade_stage=matrix_data.get("cascade_stage", 1),
                    optimal_conditions=matrix_data.get("optimal_conditions", {}),
                    compatible_substrates=matrix_data.get("substrate_preference", []),
                ))
        
        # 複合提案生成
        combination_proposal = self._generate_combination(recommendations)
        expected_effects = self._generate_expected_effects(recommendations)
        
        logger.info(
            f"Screening complete: {len(recommendations)} strains recommended"
        )
        
        return ScreeningResult(
            low_paths=low_paths,
            recommended_strains=recommendations,
            combination_proposal=combination_proposal,
            expected_effects=expected_effects,
            language=self.language,
        )
    
    def _generate_reason(self, path_id: PathID, strain_id: MetaStrainID) -> str:
        """推奨理由を生成"""
        if self.language == Language.JA:
            reasons = {
                (PathID.PATH_01, MetaStrainID.META_01): "消化吸収不良に対し、一次分解菌群がデンプン・タンパク質を低分子化し、腸管バリアを再構築します。",
                (PathID.PATH_02, MetaStrainID.META_02): "解毒負荷に対し、リグニン分解菌・放線菌が難分解性物質を開環し、キノン電子シャトルで解毒を促進します。",
                (PathID.PATH_03, MetaStrainID.META_05): "糖代謝低下に対し、乳酸菌・酪酸菌が乳酸→酪酸のクロスフィーディングで短鎖脂肪酸合成を活性化します。",
                (PathID.PATH_04, MetaStrainID.META_04): "酸化還元不均衡（電子滞留）に対し、マンガン還元菌・鉄酸化菌が多経路電子散逸（dH₂/dt≈0）を回復します。",
                (PathID.PATH_05, MetaStrainID.META_03): "ミトコンドリア機能低下に対し、放線菌がエクオール・キノン化合物を生成し、電子伝達系を補完します。",
            }
            return reasons.get((path_id, strain_id), "不足代謝経路の補完に最適な菌株です。")
        else:
            reasons_en = {
                (PathID.PATH_01, MetaStrainID.META_01): "For poor digestion: primary decomposers break down starch/protein, rebuilding gut barrier.",
                (PathID.PATH_02, MetaStrainID.META_02): "For detox burden: lignin decomposers and actinomycetes open refractory rings, accelerating detox via quinone shuttle.",
                (PathID.PATH_03, MetaStrainID.META_05): "For low glucose metabolism: lactate→butyrate cross-feeding activates SCFA synthesis.",
                (PathID.PATH_04, MetaStrainID.META_04): "For redox imbalance: Mn-reducing and Fe-oxidizing bacteria restore multi-pathway electron dissipation (dH₂/dt≈0).",
                (PathID.PATH_05, MetaStrainID.META_03): "For mitochondrial dysfunction: actinomycetes produce equol/quinones to complement electron transport chain.",
            }
            return reasons_en.get((path_id, strain_id), "Optimal strain for compensating the deficient metabolic pathway.")
    
    def _generate_combination(self, recommendations: List[StrainRecommendation]) -> str:
        """菌株の組み合わせ提案"""
        if not recommendations:
            if self.language == Language.JA:
                return "全PATHスコア良好。メンテナンスとしてMBT_META_05（酪酸生成）の定期摂取を推奨。"
            return "All PATH scores good. Recommend regular MBT_META_05 (butyrate) for maintenance."
        
        strain_names = [r.name for r in recommendations]
        
        if self.language == Language.JA:
            combo = " + ".join(strain_names)
            return (
                f"【MBT55複合処方提案】\n"
                f"以下のメタ株を段階的に投与：{combo}\n"
                f"投与順序：第1段階（0-6h）→第2段階（6-24h）→第3段階（24-72h）"
            )
        else:
            combo = " + ".join(strain_names)
            return (
                f"[MBT55 Combination Proposal]\n"
                f"Staged administration: {combo}\n"
                f"Sequence: Stage1 (0-6h) → Stage2 (6-24h) → Stage3 (24-72h)"
            )
    
    def _generate_expected_effects(self, recommendations: List[StrainRecommendation]) -> List[str]:
        """期待効果リスト生成"""
        if self.language == Language.JA:
            effects = {
                MetaStrainID.META_01: "消化吸収改善・腸管バリア強化",
                MetaStrainID.META_02: "解毒促進・抗酸化能向上",
                MetaStrainID.META_03: "ホルモン調整・神経保護",
                MetaStrainID.META_04: "電子滞留解消・腐敗防止・ミネラル供給",
                MetaStrainID.META_05: "酪酸生成・抗炎症・エネルギ代謝改善",
            }
            return [effects.get(r.strain_id, "代謝経路補完") for r in recommendations]
        else:
            effects_en = {
                MetaStrainID.META_01: "Improved digestion & gut barrier",
                MetaStrainID.META_02: "Enhanced detox & antioxidant capacity",
                MetaStrainID.META_03: "Hormone regulation & neuroprotection",
                MetaStrainID.META_04: "Electron dissipation, anti-putrefaction, mineral supply",
                MetaStrainID.META_05: "Butyrate production, anti-inflammatory, energy metabolism",
            }
            return [effects_en.get(r.strain_id, "Metabolic pathway compensation") for r in recommendations]
    
    def recommend_strains_for_substrates(
        self, substrate_list: List[str]
    ) -> List[MetaStrainID]:
        """
        基質リストから最適MBT55菌株セットを提案
        
        Args:
            substrate_list: 漢方・生薬名のリスト
        Returns:
            推奨メタ株IDリスト
        """
        recommended: Set[MetaStrainID] = set()
        
        for strain_id, strain_data in self.matrix.items():
            compatible = strain_data.get("substrate_preference", [])
            # 部分一致チェック
            for substrate in substrate_list:
                for comp in compatible:
                    if substrate.lower() in comp.lower() or comp.lower() in substrate.lower():
                        try:
                            recommended.add(MetaStrainID(strain_id))
                        except ValueError:
                            pass
                        break
        
        logger.info(
            f"Strain recommendation for substrates '{substrate_list}': "
            f"{[s.value for s in recommended]}"
        )
        return list(recommended)