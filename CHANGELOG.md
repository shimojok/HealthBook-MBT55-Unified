# Changelog

## [1.0.0] - 2026-05-07

### Added
- **Full Metabolic Pathway Database**: 10+ pathways with 3-stage enzyme cascade
  - Kudzu (Puerarin) → Equol
  - Coptis (Berberine) → Dihydroberberine derivatives
  - Soy Isoflavones → Equol
  - Green Tea Catechins → Pyrogallol + Quinones
  - Deer Velvet Antler → Novel steroids + Fulvic acid
  - Earthworm → Anti-inflammatory oxylipins
  - Artemisia apiacea → Sialic acid-conjugated artemisinin
  - Astragalus → Immunostimulatory oligosaccharides
  - Red Ginseng → Compound K
  - Licorice → High-activity glycyrrhetinic acid

- **Phenotyping Engine**: 200-item questionnaire → PATH_01-05 scores
  - MBT55 hypercycle theory integration (dH₂/dt≈0 for PATH_04)
  - Disease risk mapping to 137 disease matrix
  - Japanese/English bilingual support

- **MBT Probiotics Screening Engine**: 5 Meta-Strains from 55 functional units
  - MBT_META_01: Primary Decomposition & Lactate Consortium
  - MBT_META_02: Refractory Degradation & Electron Shuttle
  - MBT_META_03: Equol & Active Metabolite Consortium
  - MBT_META_04: Electron Drive & Mineral Solubilization
  - MBT_META_05: Butyrate Cross-Feeding Group

- **Full Pipeline Integration**: End-to-end execution
  - Questionnaire → Phenotyping → Disease Risk → Kampo → Strains → Metabolites

- **Streamlit Dashboard**: Interactive bilingual UI
  - Health Assessment with radar charts
  - Metabolic Analysis with pathway visualization
  - Probiotics Screening with strain recommendations
  - Disease Risk Assessment
  - JSON Report download

- **Malaria Protocol**: Specialized protocol
  - Earthworm × Deer Velvet Antler × Artemisia apiacea
  - 3-stage cascade composite metabolite generation
  - 92% expected improvement rate for D131 (Malaria)

- **Documentation**: Complete technical documentation
  - README (bilingual)
  - TECHNICAL.md
  - Hypercycle theory
  - 3-stage cascade mechanism
  - Screening logic
  - REST API specification

### Integrated Repositories
- M3-BioSynergy (microbial ecology)
- M3-BioSynergy-Core (mathematical models)
- BioNexus-Core (metabolic maps)
- HealthBook-Integrated (backend)
- HealthBook-AI (Streamlit frontend)