# 🦠 MBT Probiotics Screening Logic

## Design Philosophy

The screening system reframes Kampo from "empirical formula matching" to **"microbial metabolic pathway compensation"**. The core question is:

> "Which Meta-Strain consortium can supply the missing metabolic function indicated by low PATH scores?"

## Screening Algorithm

### Step 1: Identify Deficient PATHs

PATH scores < 40 are flagged as "要改善 (Needs Improvement)".

### Step 2: Map PATH → Meta-Strain

```
PATH_01 (Digestion/Gut Barrier)      → MBT_META_01 (Primary Decomposition)
PATH_02 (Liver Detoxification)       → MBT_META_02 (Refractory Degradation)
PATH_03 (Glucose/Energy Metabolism)  → MBT_META_05 (Butyrate Cross-Feeding)
PATH_04 (Redox Balance)              → MBT_META_04 (Electron Drive)
PATH_05 (Neuro-Mitochondrial)        → MBT_META_03 (Equol/Active Metabolite)
```

### Step 3: Priority Ranking

Strains are ranked by:
1. Number of deficient PATHs addressed
2. Cascade stage compatibility (Stage 1→2→3 sequence)
3. Substrate compatibility with recommended Kampo/herbs

### Step 4: Combination Proposal

Strains are proposed in staged administration:
- **Stage 1 strains first** (0-6h): Substrate preparation
- **Stage 2 strains second** (6-24h): Active metabolite generation
- **Stage 3 strains third** (24-72h): Deep synthesis and stabilization

## Substrate → Strain Compatibility

| Substrate | Compatible Meta-Strain | Produced Metabolite |
|-----------|------------------------|---------------------|
| Kudzu (Puerarin) | META_01, META_03 | Equol |
| Coptis (Berberine) | META_02 | Dihydroberberine derivatives |
| Soy Isoflavones | META_01, META_03 | Equol |
| Green Tea Catechins | META_02 | Pyrogallol + Quinones |
| Deer Velvet Antler | META_01, META_02, META_03 | Novel steroids, Sialic acid |
| Earthworm | META_01, META_04 | Lumbrokinase fragments, Oxylipins |
| Astragalus | META_01, META_03 | Immunostimulatory oligosaccharides |
| Red Ginseng | META_03 | Compound K |
| Artemisia apiacea | META_02, META_04 | Sialic acid-conjugated artemisinin |
| Licorice | META_02 | High-activity glycyrrhetinic acid |

## Clinical Rationale per Meta-Strain

### MBT_META_01: Primary Decomposition & Lactate Consortium
- **Indication**: Poor digestion, bloating, constipation, low appetite
- **Mechanism**: Supplements missing primary degraders; produces lactate as interface currency
- **Gut effect**: Lactate → butyrate cross-feeding → gut barrier repair

### MBT_META_02: Refractory Degradation & Electron Shuttle
- **Indication**: Chemical sensitivity, skin issues, fatigue, poor alcohol tolerance
- **Mechanism**: Lignin degraders open polyphenol rings; quinones shuttle electrons
- **Systemic effect**: Enhanced Phase I/II detoxification

### MBT_META_03: Equol & Active Metabolite Consortium
- **Indication**: Cognitive decline, mood disorders, hormonal imbalance
- **Mechanism**: Isoflavone → equol conversion; mitochondrial complementation
- **Neuro effect**: Quinone bio-battery supports electron transport chain

### MBT_META_04: Electron Drive & Mineral Solubilization
- **Indication**: Chronic inflammation, autoimmune conditions, allergies
- **Mechanism**: Multi-pathway electron dissipation (O₂, NO₃⁻, SO₄²⁻, Fe³⁺); dH₂/dt≈0 restoration
- **Anti-putrefaction**: Eliminates electron stagnation that causes inflammatory cascades

### MBT_META_05: Butyrate Cross-Feeding Group
- **Indication**: Sugar cravings, energy crashes, cold extremities, edema
- **Mechanism**: Lactate → butyrate conversion; SCFA synthesis activation
- **Metabolic effect**: Improved insulin sensitivity, mitochondrial energy production