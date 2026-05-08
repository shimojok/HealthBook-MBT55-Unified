"""
MetabolicPathwayDatabase — 全代謝経路解析エンジン
MBT55 3段階酵素カスケード対応
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field

from ..core.config import (
    config, CascadeStage, HypercycleCurrency, MetaStrainID, PathID
)

logger = logging.getLogger(__name__)


@dataclass
class CascadeStep:
    """3段階カスケードの1ステップ"""
    stage: CascadeStage
    action: str
    enzymes: List[str] = field(default_factory=list)
    intermediate: str = ""
    key_players: List[str] = field(default_factory=list)
    conditions: Dict = field(default_factory=dict)


@dataclass
class MetabolicPathway:
    """単一の代謝経路定義"""
    pathway_id: str
    substrate: str
    category: str
    cascade_steps: Dict[CascadeStage, CascadeStep] = field(default_factory=dict)
    hypercycle_currency: str = ""
    final_metabolite: str = ""
    human_effects: List[str] = field(default_factory=list)
    disease_targets: List[str] = field(default_factory=list)
    bioavailability_multiplier: float = 1.0
    
    def get_final_metabolite(self) -> str:
        """最終活性代謝物を取得"""
        if CascadeStage.STAGE_3 in self.cascade_steps:
            return self.cascade_steps[CascadeStage.STAGE_3].intermediate
        return self.final_metabolite
    
    def get_all_players(self) -> Set[str]:
        """全関与菌株を取得"""
        players = set()
        for step in self.cascade_steps.values():
            players.update(step.key_players)
        return players
    
    def to_dict(self) -> Dict:
        return {
            "pathway_id": self.pathway_id,
            "substrate": self.substrate,
            "category": self.category,
            "final_metabolite": self.get_final_metabolite(),
            "hypercycle_currency": self.hypercycle_currency,
            "human_effects": self.human_effects,
            "disease_targets": self.disease_targets,
        }


class MetabolicPathwayDatabase:
    """
    全代謝経路データベース
    master_pathways.json を読み込み、経路検索・推定を提供
    """
    
    def __init__(self, data_path: Optional[Path] = None):
        self.data_path = data_path or config.get_pathway_path()
        self.pathways: Dict[str, MetabolicPathway] = {}
        self._substrate_index: Dict[str, List[str]] = {}  # 基質名→経路ID
        self._disease_index: Dict[str, List[str]] = {}    # 疾病→経路ID
        self._metabolite_index: Dict[str, List[str]] = {} # 代謝物→経路ID
        self._currency_index: Dict[str, List[str]] = {}   # 通貨→経路ID
        self._load()
        logger.info(f"MetabolicPathwayDatabase loaded: {len(self.pathways)} pathways")
    
    def _load(self):
        """JSONデータを読み込み、経路オブジェクトを構築"""
        if not self.data_path.exists():
            logger.warning(f"Pathway data not found: {self.data_path}")
            return
        
        with open(self.data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        raw_pathways = data.get("pathways", [])
        
        for raw in raw_pathways:
            pathway = self._parse_pathway(raw)
            self.pathways[pathway.pathway_id] = pathway
            
            # インデックス構築
            substrate_lower = pathway.substrate.lower()
            self._substrate_index.setdefault(substrate_lower, []).append(pathway.pathway_id)
            
            for disease in pathway.disease_targets:
                self._disease_index.setdefault(disease, []).append(pathway.pathway_id)
            
            for effect in pathway.human_effects:
                self._metabolite_index.setdefault(effect, []).append(pathway.pathway_id)
            
            if pathway.hypercycle_currency:
                self._currency_index.setdefault(
                    pathway.hypercycle_currency, []
                ).append(pathway.pathway_id)
    
    def _parse_pathway(self, raw: Dict) -> MetabolicPathway:
        """生JSONデータをMetabolicPathwayオブジェクトに変換"""
        cascade_steps = {}
        
        for stage_key in ["cascade_stage_1", "cascade_stage_2", "cascade_stage_3"]:
            if stage_key in raw:
                stage_data = raw[stage_key]
                stage_num = int(stage_key.split("_")[-1])
                cascade_steps[CascadeStage(stage_num)] = CascadeStep(
                    stage=CascadeStage(stage_num),
                    action=stage_data.get("action", ""),
                    enzymes=stage_data.get("enzymes", []),
                    intermediate=stage_data.get(
                        "final_metabolite", stage_data.get("intermediate", "")
                    ),
                    key_players=stage_data.get("key_players", []),
                )
        
        return MetabolicPathway(
            pathway_id=raw.get("pathway_id", ""),
            substrate=raw.get("substrate", ""),
            category=raw.get("category", ""),
            cascade_steps=cascade_steps,
            hypercycle_currency=raw.get("hypercycle_currency", ""),
            human_effects=raw.get("human_effects", []),
            disease_targets=raw.get("disease_targets", []),
            bioavailability_multiplier=raw.get("bioavailability_multiplier", 1.0),
        )
    
    def find_by_substrate(self, substrate_name: str) -> List[MetabolicPathway]:
        """基質名から経路を検索（部分一致）"""
        substrate_lower = substrate_name.lower()
        results = []
        
        # 完全一致
        if substrate_lower in self._substrate_index:
            for pid in self._substrate_index[substrate_lower]:
                results.append(self.pathways[pid])
        
        # 部分一致
        if not results:
            for pid, pathway in self.pathways.items():
                if substrate_lower in pathway.substrate.lower():
                    results.append(pathway)
        
        return results
    
    def find_by_disease(self, disease_code: str) -> List[MetabolicPathway]:
        """疾病コードから経路を検索"""
        results = []
        if disease_code in self._disease_index:
            for pid in self._disease_index[disease_code]:
                results.append(self.pathways[pid])
        return results
    
    def find_by_currency(self, currency: str) -> List[MetabolicPathway]:
        """代謝通貨から経路を検索"""
        results = []
        if currency in self._currency_index:
            for pid in self._currency_index[currency]:
                results.append(self.pathways[pid])
        return results
    
    def predict_metabolites(self, substrate_name: str) -> Dict:
        """
        基質から予測される活性代謝物を推定
        主要API：入力成分 → 予測活性代謝物
        """
        pathways = self.find_by_substrate(substrate_name)
        
        if not pathways:
            return {
                "substrate": substrate_name,
                "found": False,
                "message": f"No pathway found for '{substrate_name}'",
                "predictions": [],
            }
        
        predictions = []
        for pathway in pathways:
            pred = {
                "pathway_id": pathway.pathway_id,
                "substrate": pathway.substrate,
                "final_metabolite": pathway.get_final_metabolite(),
                "human_effects": pathway.human_effects,
                "disease_targets": pathway.disease_targets,
                "hypercycle_currency": pathway.hypercycle_currency,
                "cascade_summary": {
                    f"stage_{step.stage.value}": {
                        "action": step.action,
                        "key_players": step.key_players,
                    }
                    for step in pathway.cascade_steps.values()
                },
            }
            predictions.append(pred)
        
        return {
            "substrate": substrate_name,
            "found": True,
            "pathway_count": len(predictions),
            "predictions": predictions,
        }
    
    def list_all_substrates(self) -> List[str]:
        """全基質名リスト"""
        return [p.substrate for p in self.pathways.values()]
    
    def list_all_diseases(self) -> List[str]:
        """全標的疾病リスト"""
        return list(self._disease_index.keys())
    
    def get_pathway_count(self) -> int:
        return len(self.pathways)


# シングルトンインスタンス
_pathway_db: Optional[MetabolicPathwayDatabase] = None


def get_pathway_database() -> MetabolicPathwayDatabase:
    """経路データベースのシングルトン取得"""
    global _pathway_db
    if _pathway_db is None:
        _pathway_db = MetabolicPathwayDatabase()
    return _pathway_db