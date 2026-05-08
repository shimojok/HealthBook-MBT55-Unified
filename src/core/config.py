"""
HealthBook-MBT55-Unified 統合設定
日英バイリンガル対応・全レイヤー統合設定
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class Language(str, Enum):
    JA = "ja"
    EN = "en"


class PathID(str, Enum):
    PATH_01 = "PATH_01"  # 消化吸収・腸管バリア
    PATH_02 = "PATH_02"  # 肝解毒
    PATH_03 = "PATH_03"  # 糖代謝エネルギー
    PATH_04 = "PATH_04"  # 酸化還元バランス・電子散逸
    PATH_05 = "PATH_05"  # 脳神経ミトコンドリア


class MetaStrainID(str, Enum):
    META_01 = "MBT_META_01"  # 一次分解・乳酸生成
    META_02 = "MBT_META_02"  # 難分解物破砕・電子シャトル
    META_03 = "MBT_META_03"  # エクオール・活性代謝物特化
    META_04 = "MBT_META_04"  # 電子駆動・ミネラル可溶化
    META_05 = "MBT_META_05"  # 安定化・酪酸生成


class CascadeStage(int, Enum):
    STAGE_1 = 1  # 0-6h: 高速加水分解
    STAGE_2 = 2  # 6-24h: 代謝・変換
    STAGE_3 = 3  # 24-72h: 深部合成・熟成


class HypercycleCurrency(str, Enum):
    LACTATE = "lactate"        # 乳酸（界面通貨）
    QUINONE = "quinone"        # キノン化合物（電子通貨）
    FULVIC = "fulvic"          # フルボ酸（ミネラル通貨）


class DiseaseCategory(str, Enum):
    D001 = "D001"  # 神経系
    D002 = "D002"  # 骨・関節・筋肉
    D003 = "D003"  # 循環器
    D004 = "D004"  # 内分泌
    D005 = "D005"  # 代謝
    D012 = "D012"  # 免疫・アレルギー
    D013 = "D013"  # 感染症
    D131 = "D131"  # マラリア


class SystemConfig(BaseModel):
    """システム全体設定"""
    
    # リポジトリルート
    root_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent)
    data_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent / "data")
    
    # 言語設定
    default_language: Language = Language.JA
    supported_languages: List[Language] = [Language.JA, Language.EN]
    
    # データファイルパス
    questionnaire_ja_path: str = "questionnaires/healthbook_200_ja.json"
    questionnaire_en_path: str = "questionnaires/healthbook_200_en.json"
    disease_matrix_path: str = "diseases/disease_matrix_137.json"
    kampo_library_path: str = "kampo/kampo_294_library.json"
    animal_library_path: str = "kampo/animal_derived_library.json"
    master_pathways_path: str = "pathways/master_pathways.json"
    probiotic_matrix_path: str = "probiotics/probiotic_matrix.json"
    phenotype_weight_path: str = "phenotyping/phenotype_weight_matrix.json"
    mbt55_parameters_path: str = "mbt55/hypercycle_parameters.json"
    
    # モデルパラメータ
    mbt55_ode_params: Dict = Field(default_factory=lambda: {
        "C_p_init": 100.0,
        "C_s_init": 10.0,
        "E_init": 1.0,
        "H2_init": 0.001,
    })
    
    # 3段階カスケード条件
    cascade_conditions: Dict[str, Dict] = Field(default_factory=lambda: {
        "stage_1": {"temp": 38.0, "ph": 6.0, "hours": 6, "oxygen": "aerobic"},
        "stage_2": {"temp": 42.0, "ph": 5.5, "hours": 18, "oxygen": "microaerophilic"},
        "stage_3": {"temp": 35.0, "ph": 6.5, "hours": 48, "oxygen": "anaerobic"},
    })
    
    # PATHスコア閾値
    path_thresholds: Dict[str, float] = Field(default_factory=lambda: {
        "PATH_01": 40.0,
        "PATH_02": 40.0,
        "PATH_03": 40.0,
        "PATH_04": 40.0,
        "PATH_05": 40.0,
    })
    
    # MBT55メタ株定義
    meta_strains: List[str] = [
        "MBT_META_01",
        "MBT_META_02",
        "MBT_META_03",
        "MBT_META_04",
        "MBT_META_05",
    ]
    
    @property
    def full_data_dir(self) -> Path:
        return self.root_dir / "data"
    
    def get_questionnaire_path(self, lang: Language = Language.JA) -> Path:
        if lang == Language.JA:
            return self.full_data_dir / self.questionnaire_ja_path
        return self.full_data_dir / self.questionnaire_en_path
    
    def get_pathway_path(self) -> Path:
        return self.full_data_dir / self.master_pathways_path
    
    def get_probiotic_matrix_path(self) -> Path:
        return self.full_data_dir / self.probiotic_matrix_path
    
    def get_phenotype_weight_path(self) -> Path:
        return self.full_data_dir / self.phenotype_weight_path
    
    def get_disease_matrix_path(self) -> Path:
        return self.full_data_dir / self.disease_matrix_path


# グローバル設定インスタンス
config = SystemConfig()


# PATH_01〜05 日本語・英語説明マッピング
PATH_DEFINITIONS = {
    Language.JA: {
        PathID.PATH_01: {
            "name": "消化吸収・腸管バリア",
            "short": "消化吸収",
            "description": "一次分解（でんぷん分解菌・タンパク質分解菌）の活性状態",
            "high_meaning": "消化吸収良好、腸管バリア強固",
            "low_meaning": "消化吸収不良、腸管バリア脆弱",
            "mb55_link": "一次分解・乳酸生成コンソーシアム（MBT_META_01）が関与",
        },
        PathID.PATH_02: {
            "name": "肝解毒・フェーズI/II",
            "short": "肝解毒",
            "description": "難分解物破砕（リグニン分解菌・放線菌）の解毒代謝",
            "high_meaning": "解毒機能良好",
            "low_meaning": "解毒負荷状態",
            "mb55_link": "難分解物破砕・電子シャトル形成コンソーシアム（MBT_META_02）が関与",
        },
        PathID.PATH_03: {
            "name": "糖代謝・エネルギー産生",
            "short": "糖代謝",
            "description": "乳酸ハブを中心とした短鎖脂肪酸合成力",
            "high_meaning": "エネルギー代謝良好",
            "low_meaning": "糖代謝低下",
            "mb55_link": "安定化・酪酸生成クロスフィーディンググループ（MBT_META_05）が関与",
        },
        PathID.PATH_04: {
            "name": "酸化還元バランス・電子散逸",
            "short": "酸化還元",
            "description": "dH₂/dt≈0を維持する電子散逸系の健全性",
            "high_meaning": "酸化還元バランス良好、電子滞留なし",
            "low_meaning": "腐敗（電子滞留）状態",
            "mb55_link": "電子駆動・ミネラル可溶化コンソーシアム（MBT_META_04）が関与",
        },
        PathID.PATH_05: {
            "name": "脳神経・ミトコンドリア機能",
            "short": "脳神経",
            "description": "キノン電子シャトルによるミトコンドリア補完と神経保護",
            "high_meaning": "ミトコンドリア機能良好、神経保護十分",
            "low_meaning": "ミトコンドリア機能低下",
            "mb55_link": "エクオール・活性代謝物特化コンソーシアム（MBT_META_03）が関与",
        },
    },
    Language.EN: {
        PathID.PATH_01: {
            "name": "Digestion & Gut Barrier",
            "short": "Digestion",
            "description": "Primary decomposition activity (starch/protein degrading bacteria)",
            "high_meaning": "Good digestion, strong gut barrier",
            "low_meaning": "Poor digestion, weak gut barrier",
            "mb55_link": "MBT_META_01: Primary Decomposition & Lactate Consortium",
        },
        PathID.PATH_02: {
            "name": "Liver Detoxification Phase I/II",
            "short": "Detox",
            "description": "Refractory compound degradation (lignin decomposers/actinomycetes)",
            "high_meaning": "Good detoxification",
            "low_meaning": "Detox burden state",
            "mb55_link": "MBT_META_02: Refractory Degradation & Electron Shuttle Consortium",
        },
        PathID.PATH_03: {
            "name": "Glucose Metabolism & Energy",
            "short": "Energy",
            "description": "SCFA synthesis centered on lactate hub",
            "high_meaning": "Good energy metabolism",
            "low_meaning": "Low glucose metabolism",
            "mb55_link": "MBT_META_05: Stabilization & Butyrate Cross-Feeding Group",
        },
        PathID.PATH_04: {
            "name": "Redox Balance & Electron Dissipation",
            "short": "Redox",
            "description": "Health of electron dissipation system maintaining dH₂/dt≈0",
            "high_meaning": "Good redox balance, no electron stagnation",
            "low_meaning": "Putrefaction (electron stagnation) state",
            "mb55_link": "MBT_META_04: Electron Drive & Mineral Solubilization Consortium",
        },
        PathID.PATH_05: {
            "name": "Neuro-Mitochondrial Function",
            "short": "Neuro",
            "description": "Mitochondrial complementation via quinone electron shuttle",
            "high_meaning": "Good mitochondrial function, sufficient neuroprotection",
            "low_meaning": "Mitochondrial dysfunction",
            "mb55_link": "MBT_META_03: Equol & Active Metabolite Specialized Consortium",
        },
    },
}


# メタ株定義
META_STRAIN_DEFINITIONS = {
    Language.JA: {
        MetaStrainID.META_01: {
            "name": "一次分解・乳酸生成コンソーシアム",
            "functional_unit": "一次分解",
            "key_species": "タテヤマ浄土（Bacillus sp.）",
            "produces": "乳酸、アミノ酸、ペプチド",
            "target_path": "PATH_01",
        },
        MetaStrainID.META_02: {
            "name": "難分解物破砕・電子シャトル形成コンソーシアム",
            "functional_unit": "難分解物破砕",
            "key_species": "タテヤマ女汝（Atopostipes sp.）",
            "produces": "キノン化合物、没食子酸、ピロガロール",
            "target_path": "PATH_02/PATH_04",
        },
        MetaStrainID.META_03: {
            "name": "エクオール・活性代謝物特化コンソーシアム",
            "functional_unit": "安定化・統合（特化）",
            "key_species": "タテヤマ剣・薬師（Bacillus sp.）",
            "produces": "エクオール、コンパウンドK",
            "target_path": "PATH_05",
        },
        MetaStrainID.META_04: {
            "name": "電子駆動・ミネラル可溶化コンソーシアム",
            "functional_unit": "元素・金属代謝",
            "key_species": "タテヤマ竜王（Clostridium sp.）",
            "produces": "フルボ酸、可溶化ミネラル、シデロフォア",
            "target_path": "PATH_04",
        },
        MetaStrainID.META_05: {
            "name": "安定化・酪酸生成クロスフィーディンググループ",
            "functional_unit": "安定化・統合",
            "key_species": "乳酸菌群、酪酸菌",
            "produces": "酪酸、酢酸、プロピオン酸",
            "target_path": "PATH_03",
        },
    },
    Language.EN: {
        MetaStrainID.META_01: {
            "name": "Primary Decomposition & Lactate Consortium",
            "functional_unit": "Primary Decomposition",
            "key_species": "Tateyama-Jodo (Bacillus sp.)",
            "produces": "Lactate, Amino acids, Peptides",
            "target_path": "PATH_01",
        },
        MetaStrainID.META_02: {
            "name": "Refractory Degradation & Electron Shuttle Consortium",
            "functional_unit": "Refractory Degradation",
            "key_species": "Tateyama-Menami (Atopostipes sp.)",
            "produces": "Quinones, Gallic acid, Pyrogallol",
            "target_path": "PATH_02/PATH_04",
        },
        MetaStrainID.META_03: {
            "name": "Equol & Active Metabolite Specialized Consortium",
            "functional_unit": "Stabilization (Specialized)",
            "key_species": "Tateyama-Tsurugi/Yakushi (Bacillus sp.)",
            "produces": "Equol, Compound K",
            "target_path": "PATH_05",
        },
        MetaStrainID.META_04: {
            "name": "Electron Drive & Mineral Solubilization Consortium",
            "functional_unit": "Element/Metal Metabolism",
            "key_species": "Tateyama-Ryuo (Clostridium sp.)",
            "produces": "Fulvic acid, Solubilized minerals, Siderophores",
            "target_path": "PATH_04",
        },
        MetaStrainID.META_05: {
            "name": "Stabilization & Butyrate Cross-Feeding Group",
            "functional_unit": "Stabilization",
            "key_species": "Lactic acid bacteria, Butyrate-producing bacteria",
            "produces": "Butyrate, Acetate, Propionate",
            "target_path": "PATH_03",
        },
    },
}