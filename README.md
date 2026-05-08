# 🏥 HealthBook-MBT55-Unified

**Next-Generation Healthcare Platform Integrating Full Metabolic Pathway Analysis, Phenotyping, and MBT Probiotics Screening**

**全代謝経路解析・フェノタイピング・MBTプロバイオティクススクリーニングを統合した次世代ヘルスケアプラットフォーム**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-green.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)

---

## 🌐 Overview / 概要

HealthBook-MBT55-Unified is a three-layer healthcare platform that traces how the MBT55 microbial consortium (120-2,000+ species from the Tateyama mountain range, Japan) metabolizes Kampo herbs, polyphenols, and animal-derived natural products into therapeutically active compounds for human health.

HealthBook-MBT55-Unifiedは、立山連峰山麓由来のMBT55微生物群（120〜2,000+菌種）が、漢方生薬・ポリフェノール・動物性生薬をヒト有用代謝産物へ変換する全プロセスをトレースする3層構造のヘルスケアプラットフォームです。

### 🎯 Core Features / 主要機能

| Feature | Description |
|---------|-------------|
| **Full Metabolic Pathway Analysis** | Trace 20+ substrates (Kudzu, Coptis, Soy, Green Tea, Deer Velvet Antler, etc.) through MBT55 3-stage enzyme cascade |
| **Phenotyping (PATH_01-05)** | Convert 200-item questionnaire to 5 metabolic pathway activity scores with MBT55 hypercycle theory |
| **MBT Probiotics Screening** | Recommend optimal 5 Meta-Strain consortia based on deficient metabolic pathways |
| **Disease Risk Assessment** | Map phenotype to 137-disease matrix with Kampo/herb recommendations |
| **Malaria Protocol** | Specialized protocol: Earthworm × Deer Velvet Antler × Artemisia apiacea (MKS16) |
| **日英バイリンガル** | Full Japanese/English support with i18n translation engine |

---

## 🏗️ System Architecture / システム構造

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: Clinical Application (HealthBook Demo)            │
│  200-item Questionnaire → Phenotyping → Disease Risk        │
│  → Kampo Recommendation → Expected Effects                  │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: Metabolic Analysis (Full Pathway + Probiotics)    │
│  Herb/Polyphenol → Microbial Degradation → Active           │
│  Metabolites → PATH_01-05 Activation Map                    │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: Microbial Ecology (M3-BioSynergy)                 │
│  55 Functional Units / Hypercycle / Nutrient Cascade        │
│  dH₂/dt≈0 Electron Dissipation Theory                       │
└─────────────────────────────────────────────────────────────┘
```

### The 5 PATH Scores (MBT55 Hypercycle Theory)

| PATH | Name (EN/JP) | MBT55 Link |
|------|--------------|------------|
| PATH_01 | Digestion & Gut Barrier / 消化吸収・腸管バリア | META_01: Primary Decomposition & Lactate Consortium |
| PATH_02 | Liver Detoxification / 肝解毒 | META_02: Refractory Degradation & Electron Shuttle |
| PATH_03 | Glucose & Energy Metabolism / 糖代謝エネルギー | META_05: Butyrate Cross-Feeding Group |
| PATH_04 | Redox Balance & Electron Dissipation / 酸化還元バランス | META_04: Electron Drive & Mineral Solubilization |
| PATH_05 | Neuro-Mitochondrial Function / 脳神経ミトコンドリア | META_03: Equol & Active Metabolite Consortium |

### The 5 Meta-Strains (From 55 Functional Units)

| Meta-Strain | Key Species | Core Currency |
|-------------|-------------|---------------|
| MBT_META_01 | *Tateyama-Jodo (Bacillus sp.)* | **Lactate** (Interface Currency) |
| MBT_META_02 | *Tateyama-Menami (Atopostipes sp.)* | **Quinone** (Electron Currency) |
| MBT_META_03 | *Tateyama-Tsurugi/Yakushi (Bacillus sp.)* | Equol, Compound K |
| MBT_META_04 | *Tateyama-Ryuo (Clostridium sp.)* | **Fulvic Acid** (Mineral Currency) |
| MBT_META_05 | Lactic acid bacteria, Butyrate producers | Butyrate (Anti-inflammatory) |

---

## 🚀 Quick Start / クイックスタート

### Prerequisites / 前提条件

- Python 3.11+
- Git

### Installation / インストール

```bash
# Clone repository
git clone https://github.com/shimojok/HealthBook-MBT55-Unified.git
cd HealthBook-MBT55-Unified

# Install dependencies
pip install -r requirements.txt

# Run dashboard (Japanese)
streamlit run dashboard/app.py -- --lang=ja

# Run dashboard (English)
streamlit run dashboard/app.py -- --lang=en
```

### Docker Deployment / Dockerデプロイ

```bash
# Build and start all services
docker-compose up -d

# Access dashboard
open http://localhost:8501
```

### CLI Demo / コマンドライン実行

```python
from src.integration.full_pipeline import FullPipeline, demo_full_pipeline
from src.core.config import Language

# Japanese demo
print(demo_full_pipeline(Language.JA))

# English demo
print(demo_full_pipeline(Language.EN))
```

---

## 📁 Repository Structure / リポジトリ構成

```
HealthBook-MBT55-Unified/
├── README.md                           # This file / 本ファイル
├── README_JA.md                        # Japanese detailed guide
├── TECHNICAL.md                        # Technical deep-dive
├── docs/                               # Documentation hub
│   ├── index.md                        # Documentation index
│   ├── architecture/                   # System architecture
│   ├── metabolic_pathways/             # Pathway details
│   ├── phenotyping/                    # Phenotyping methodology
│   ├── probiotics/                     # Probiotics knowledge base
│   └── api/                            # API specifications
├── src/                                # Source code
│   ├── core/                           # Core configuration
│   ├── layer1_microbiome/              # Layer 1: M3-BioSynergy
│   ├── layer2_metabolism/              # Layer 2: Metabolic Analysis
│   ├── layer3_clinical/                # Layer 3: Clinical Application
│   ├── probiotics/                     # MBT Probiotics Screening
│   ├── integration/                    # Full Pipeline
│   └── api/                            # REST/GraphQL API
├── data/                               # Data files (JSON)
│   ├── questionnaires/                 # 200-item questionnaire
│   ├── diseases/                       # 137 disease matrix
│   ├── kampo/                          # 294 Kampo library
│   ├── pathways/                       # Master pathway map
│   ├── probiotics/                     # Probiotic matrix
│   ├── phenotyping/                    # Weight matrix
│   └── mbt55/                          # MBT55 strain database
├── dashboard/                          # Streamlit dashboard
│   ├── app.py                          # Main app (日英切替)
│   ├── components/                     # UI components
│   ├── pages/                          # Multi-page views
│   └── i18n/                           # Internationalization
├── tests/                              # Unit & integration tests
├── scripts/                            # Utility scripts
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## 📊 Data Assets / データ資産

| Data File | Content | Status |
|-----------|---------|--------|
| `healthbook_200_ja.json` | 200-item questionnaire (JP) | ✅ Complete |
| `healthbook_200_en.json` | 200-item questionnaire (EN) | ✅ Complete |
| `disease_matrix_137.json` | 137 disease risk matrix | ✅ Complete |
| `kampo_294_library.json` | 294 Kampo formula library | ✅ Complete |
| `master_pathways.json` | 20+ metabolic pathway maps | ✅ Complete |
| `probiotic_matrix.json` | 5 Meta-Strain function matrix | ✅ Complete |
| `phenotype_weight_matrix.json` | Questionnaire→PATH weight matrix | ✅ Complete |
| `animal_derived_library.json` | Deer Velvet Antler, Earthworm library | ✅ Complete |

---

## 🔬 Key Scientific References / 主要科学的参照

| Document | Topic |
|----------|-------|
| ■MBT55技術解説レポート | 55 Functional Units & Hypercycle Theory |
| ■MBT55_酵素カスケード反応の3段階メカニズム | 3-Stage Enzyme Cascade |
| M1-M3 | Core Metabolites & Carbon Core of Hypercycle |
| MKS6 | Deer Velvet Antler Metabolic Transformation |
| MKS8 | Predicted Active Molecular Structures |
| MKS10 | Category 13 Infection Pathway Analysis |
| MKS12 | Formulation Design (Malaria Protocol) |
| MKS16 | 3-Stage Cascade Composite Metabolite Generation |
| Gem3 | Dynamic Phenotyping Mathematical Model |

---

## 📖 Documentation Index / ドキュメント目次

- [README_JA.md](README_JA.md) — 日本語詳細ガイド
- [TECHNICAL.md](TECHNICAL.md) — 技術仕様・アーキテクチャ
- [docs/architecture/hypercycle_theory.md](docs/architecture/hypercycle_theory.md) — ハイパーサイクル理論
- [docs/architecture/three_layer_model.md](docs/architecture/three_layer_model.md) — 3層構造詳細
- [docs/metabolic_pathways/cascade_mechanism.md](docs/metabolic_pathways/cascade_mechanism.md) — 3段階カスケード機構
- [docs/phenotyping/scoring_methodology.md](docs/phenotyping/scoring_methodology.md) — スコアリング方法論
- [docs/probiotics/screening_logic.md](docs/probiotics/screening_logic.md) — スクリーニングロジック
- [docs/api/rest_api_spec.md](docs/api/rest_api_spec.md) — REST API仕様

---

## 🤝 Contributing / 貢献

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License / ライセンス

MIT License — See [LICENSE](LICENSE) for details.

## 👤 Author / 作成者

**shimojok** — [GitHub Profile](https://github.com/shimojok)

---

*MBT55: From Tateyama's soil microbiome to planetary health platform.*  
*MBT55：立山の土壌微生物群から、地球規模のヘルスケアプラットフォームへ。*