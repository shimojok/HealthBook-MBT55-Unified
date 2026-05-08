"""
FullPipeline — 全レイヤー統合エンドツーエンドパイプライン
問診 → フェノタイピング → 疾病リスク → 漢方推奨 → 菌株提案 → 代謝物予測
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field

from ..core.config import (
    config, Language, PathID, MetaStrainID, PATH_DEFINITIONS
)
from ..layer2_metabolism.pathway_database import (
    MetabolicPathwayDatabase, get_pathway_database
)
from ..layer3_clinical.phenotyping_engine import (
    PhenotypingEngine, PhenotypeResult
)
from ..probiotics.screening_engine import (
    ProbioticScreeningEngine, ScreeningResult
)

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    """統合パイプライン全体結果"""
    language: Language
    questionnaire_answers: Dict[str, bool]
    phenotype: PhenotypeResult
    disease_risks: Dict[str, float]
    recommended_kampo: List[str]
    recommended_substrates: List[str]
    probiotic_screening: ScreeningResult
    metabolite_predictions: List[Dict]
    expected_effects: List[str]
    timestamp: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "language": self.language.value,
            "phenotype": self.phenotype.to_dict(),
            "disease_risks": self.disease_risks,
            "recommended_kampo": self.recommended_kampo,
            "recommended_substrates": self.recommended_substrates,
            "probiotic_screening": self.probiotic_screening.to_dict(),
            "metabolite_predictions": self.metabolite_predictions,
            "expected_effects": self.expected_effects,
        }
    
    def format_for_display(self) -> str:
        """ダッシュボード表示用の整形テキスト"""
        lines = []
        
        if self.language == Language.JA:
            lines.append("=" * 60)
            lines.append("🏥 HealthBook-MBT55 統合解析結果")
            lines.append("=" * 60)
            
            # PATHスコア
            lines.append("\n📊 【PATH_01〜05 代謝経路活性スコア】")
            defs = PATH_DEFINITIONS[self.language]
            for pid, ps in self.phenotype.scores.items():
                bar = "█" * int(ps.score // 5) + "░" * (20 - int(ps.score // 5))
                lines.append(f"  {defs[pid]['name']:20s} [{bar}] {ps.score:.1f}% ({ps.level})")
            
            # 疾病リスク
            if self.disease_risks:
                lines.append("\n⚠️ 【疾病リスク評価】")
                for disease, risk in list(self.disease_risks.items())[:5]:
                    lines.append(f"  {disease}: {risk:.1f}%")
            
            # 推奨漢方
            if self.recommended_kampo:
                lines.append(f"\n💊 【推奨漢方・生薬】{', '.join(self.recommended_kampo)}")
            
            # 菌株推奨
            lines.append("\n🦠 【MBT55推奨メタ株】")
            for strain in self.probiotic_screening.recommended_strains:
                lines.append(f"  P{strain.priority}: {strain.name} → {strain.reason}")
            
            # 期待効果
            if self.expected_effects:
                lines.append(f"\n✨ 【期待効果】")
                for effect in self.expected_effects:
                    lines.append(f"  ✅ {effect}")
        else:
            lines.append("=" * 60)
            lines.append("🏥 HealthBook-MBT55 Integrated Analysis Result")
            lines.append("=" * 60)
            
            lines.append("\n📊 [PATH_01-05 Metabolic Pathway Activity Scores]")
            defs = PATH_DEFINITIONS[self.language]
            for pid, ps in self.phenotype.scores.items():
                bar = "█" * int(ps.score // 5) + "░" * (20 - int(ps.score // 5))
                lines.append(f"  {defs[pid]['name']:20s} [{bar}] {ps.score:.1f}% ({ps.level})")
            
            if self.disease_risks:
                lines.append("\n⚠️ [Disease Risk Assessment]")
                for disease, risk in list(self.disease_risks.items())[:5]:
                    lines.append(f"  {disease}: {risk:.1f}%")
            
            if self.recommended_kampo:
                lines.append(f"\n💊 [Recommended Kampo/Herbs] {', '.join(self.recommended_kampo)}")
            
            lines.append("\n🦠 [MBT55 Recommended Meta-Strains]")
            for strain in self.probiotic_screening.recommended_strains:
                lines.append(f"  P{strain.priority}: {strain.name} → {strain.reason}")
            
            if self.expected_effects:
                lines.append(f"\n✨ [Expected Effects]")
                for effect in self.expected_effects:
                    lines.append(f"  ✅ {effect}")
        
        return "\n".join(lines)


class FullPipeline:
    """
    統合パイプライン
    Layer 1-3 + Probiotics を一貫動作させる
    """
    
    def __init__(self, language: Language = Language.JA):
        self.language = language
        self.phenotype_engine = PhenotypingEngine(language=language)
        self.screening_engine = ProbioticScreeningEngine(language=language)
        self.pathway_db = get_pathway_database()
        
        # 簡易疾病リスクマッピング（実際は137疾病マトリックスから読み込み）
        self._disease_map = self._load_disease_map()
        
        # 漢方推奨マッピング
        self._kampo_map = self._load_kampo_map()
        
        logger.info(f"FullPipeline initialized (lang={language.value})")
    
    def _load_disease_map(self) -> Dict:
        """PATH → 疾病リスク簡易マッピング"""
        return {
            PathID.PATH_01: [
                ("D002-001（骨粗鬆症）", 0.3),
                ("D005-002（糖尿病）", 0.2),
            ],
            PathID.PATH_02: [
                ("D012-001（免疫調節）", 0.3),
                ("D012-005（炎症）", 0.25),
            ],
            PathID.PATH_03: [
                ("D005-002（糖尿病）", 0.3),
                ("D003-001（脳梗塞）", 0.2),
            ],
            PathID.PATH_04: [
                ("D012-005（全身性炎症）", 0.35),
                ("D013-001（感染防御低下）", 0.25),
            ],
            PathID.PATH_05: [
                ("D001-005（神経保護低下）", 0.3),
                ("D004-004（成長障害）", 0.2),
            ],
        }
    
    def _load_kampo_map(self) -> Dict:
        """PATH → 推奨漢方簡易マッピング"""
        return {
            PathID.PATH_01: ["六君子湯", "葛根湯", "山薬"],
            PathID.PATH_02: ["黄連解毒湯", "茵蔯蒿湯", "緑茶カテキン"],
            PathID.PATH_03: ["八味地黄丸", "牛車腎気丸", "紅参"],
            PathID.PATH_04: ["十全大補湯", "鹿茸", "黄耆"],
            PathID.PATH_05: ["釣藤散", "抑肝散", "大豆イソフラボン"],
        }
    
    def run(self, questionnaire_answers: Dict[str, bool]) -> PipelineResult:
        """
        統合パイプライン実行
        
        Args:
            questionnaire_answers: {症状名: True/False}
        Returns:
            PipelineResult
        """
        logger.info("FullPipeline execution started")
        
        # Step 1: フェノタイピング
        phenotype = self.phenotype_engine.score_phenotype(questionnaire_answers)
        
        # Step 2: 疾病リスク評価
        disease_risks = self._calculate_disease_risks(phenotype)
        
        # Step 3: 推奨漢方・基質の特定
        kampo_list, substrate_list = self._recommend_kampo(phenotype)
        
        # Step 4: プロバイオティクススクリーニング
        screening = self.screening_engine.screen_probiotics(phenotype)
        
        # Step 5: 代謝物予測
        metabolite_predictions = []
        for substrate in substrate_list[:3]:  # 上位3つ
            pred = self.pathway_db.predict_metabolites(substrate)
            if pred.get("found"):
                metabolite_predictions.append(pred)
        
        # Step 6: 期待効果の集約
        expected_effects = self._aggregate_effects(phenotype, screening)
        
        logger.info("FullPipeline execution completed")
        
        return PipelineResult(
            language=self.language,
            questionnaire_answers=questionnaire_answers,
            phenotype=phenotype,
            disease_risks=disease_risks,
            recommended_kampo=kampo_list,
            recommended_substrates=substrate_list,
            probiotic_screening=screening,
            metabolite_predictions=metabolite_predictions,
            expected_effects=expected_effects,
        )
    
    def _calculate_disease_risks(self, phenotype: PhenotypeResult) -> Dict[str, float]:
        """フェノタイプ → 疾病リスク推定"""
        risks = {}
        for pid, ps in phenotype.scores.items():
            if ps.is_low:
                for disease, weight in self._disease_map.get(pid, []):
                    risk_increase = (config.path_thresholds[pid.value] - ps.score) * weight
                    risks[disease] = min(100.0, 10.0 + risk_increase)
        return risks
    
    def _recommend_kampo(self, phenotype: PhenotypeResult) -> tuple:
        """不足PATH → 推奨漢方・基質"""
        kampo_list = []
        substrate_list = []
        for pid in phenotype.low_paths:
            kampo_items = self._kampo_map.get(pid, [])
            kampo_list.extend(kampo_items)
            substrate_list.extend(kampo_items)
        return list(set(kampo_list)), list(set(substrate_list))
    
    def _aggregate_effects(
        self, phenotype: PhenotypeResult, screening: ScreeningResult
    ) -> List[str]:
        """期待効果の集約"""
        effects = []
        for rs in screening.recommended_strains:
            strain_id = rs.strain_id
            if self.language == Language.JA:
                effect_map = {
                    MetaStrainID.META_01: "消化吸収改善・腸管バリア強化",
                    MetaStrainID.META_02: "解毒促進・抗酸化能向上",
                    MetaStrainID.META_03: "ホルモン調整・神経保護",
                    MetaStrainID.META_04: "電子滞留解消・腐敗防止（dH₂/dt≈0）",
                    MetaStrainID.META_05: "酪酸生成・抗炎症・エネルギ代謝改善",
                }
            else:
                effect_map = {
                    MetaStrainID.META_01: "Improved digestion & gut barrier",
                    MetaStrainID.META_02: "Enhanced detox & antioxidant capacity",
                    MetaStrainID.META_03: "Hormone regulation & neuroprotection",
                    MetaStrainID.META_04: "Electron dissipation, anti-putrefaction (dH₂/dt≈0)",
                    MetaStrainID.META_05: "Butyrate production, anti-inflammatory, energy metabolism",
                }
            effects.append(effect_map.get(strain_id, str(strain_id)))
        return effects


def demo_full_pipeline(language: Language = Language.JA) -> str:
    """デモ実行：全パイプライン"""
    pipeline = FullPipeline(language=language)
    
    # デモ問診データ
    demo_answers = {
        "甘いもの依存": True,
        "午後眠気": True,
        "冷え": True,
        "疲れやすい": True,
        "肌荒れ": True,
        "炎症": True,
        "アレルギー": True,
        "関節痛": True,
        "集中力低下": True,
        "不眠": False,
        "便秘": True,
        "むくみ": True,
        "朝食欠食": True,
        "酒に弱い": False,
        "気分落込": False,
        "胃もたれ": False,
        "食欲不振": True,
        "腹部膨満感": True,
    }
    
    result = pipeline.run(demo_answers)
    return result.format_for_display()


if __name__ == "__main__":
    # デモ実行
    print("=== 日本語版デモ ===")
    print(demo_full_pipeline(Language.JA))
    print("\n=== English Demo ===")
    print(demo_full_pipeline(Language.EN))