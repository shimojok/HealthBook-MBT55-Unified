# 🔧 HealthBook-MBT55-Unified Technical Documentation

## Core Mathematical Model

### Hypercycle ODE System (from M3-BioSynergy)

The MBT55 hypercycle is governed by the following ordinary differential equations:

**State Variables:**
- `C_p`: Polymer carbon (cellulose, etc.)
- `C_s`: Interface currency (lactate, SCFAs)
- `E`: Reducing power (NADH equivalent)
- `H₂`: Hydrogen partial pressure

**Core Stability Condition (Electron Dissipation):**

```
dH₂/dt = δE - ε(X_m + X_s)H₂ ≈ 0
```

This equation mathematically guarantees zero putrefaction: hydrogen production and consumption rates are balanced, preventing electron stagnation that causes malodor.

### 3-Stage Enzyme Cascade

| Stage | Time | Temperature | Oxygen | Key Action |
|-------|------|-------------|--------|------------|
| Stage 1 | 0-6h | 38°C | Aerobic | High-speed hydrolysis: protein→peptides, polysaccharides→oligosaccharides |
| Stage 2 | 6-24h | 42°C | Microaerophilic | Metabolic transformation: deglycosylation, aglycone exposure |
| Stage 3 | 24-72h | 35°C | Anaerobic | Deep synthesis: reduction, novel steroid formation, fulvic acid chelation |

### Hypercycle Currencies

| Currency | Type | Function | Key Producer |
|----------|------|----------|--------------|
| **Lactate** | Carbon/Interface | Rapid diffusion, Mn/Fe reduction driver, →butyrate via cross-feeding | META_01 |
| **Quinones** | Electron | Electron shuttle between species, mitochondrial complementation | META_02 |
| **Fulvic Acid** | Mineral/Structural | Trace element chelation, "mobile nutrient OS" | META_04 |

---

## Phenotyping Algorithm

### PATH_01-05 Score Calculation

```
PATH_score[i] = 100 × (1 - Σ(symptom_present[j] × weight[j]) / Σ(max_possible[j]))
```

Where:
- `symptom_present[j]` = 1 if reported, 0 otherwise
- `weight[j]` = domain-specific weight from phenotype_weight_matrix.json

**PATH_04 Amplification Rule:**
If ≥2 D012-series symptoms (inflammation, allergy, autoimmune, sensitive skin) are present, PATH_04 score is further reduced by 30% to reflect the MBT55 electron dissipation theory.

### PATH → Disease Risk Mapping

```
disease_risk = 10% + (threshold - PATH_score) × weight
```

Capped at 100%.

---

## Probiotic Screening Algorithm

### PATH → Meta-Strain Mapping

```
PATH_01 (low) → MBT_META_01: Primary Decomposition & Lactate Consortium
PATH_02 (low) → MBT_META_02: Refractory Degradation & Electron Shuttle
PATH_03 (low) → MBT_META_05: Butyrate Cross-Feeding Group
PATH_04 (low) → MBT_META_04: Electron Drive & Mineral Solubilization
PATH_05 (low) → MBT_META_03: Equol & Active Metabolite Consortium
```

### Substrate → Strain Compatibility

The system uses partial string matching between user-provided substrates and `substrate_preference` arrays in `probiotic_matrix.json`. Each Meta-Strain has defined compatible substrates based on enzyme profiles.

---

## API Architecture

### REST API Endpoints (FastAPI)

```
POST /api/v1/phenotype
  - Input: questionnaire_answers (JSON)
  - Output: PhenotypeResult with PATH scores

POST /api/v1/screening
  - Input: PhenotypeResult
  - Output: ScreeningResult with recommended strains

POST /api/v1/pipeline
  - Input: questionnaire_answers (JSON)
  - Output: Full PipelineResult

GET /api/v1/pathways/{substrate_name}
  - Output: Metabolite predictions for substrate

GET /api/v1/strains
  - Output: All 5 Meta-Strain definitions
```

### Internal Module Graph

```
dashboard/app.py
  └── src/integration/full_pipeline.py
        ├── src/layer3_clinical/phenotyping_engine.py
        │     └── data/phenotyping/phenotype_weight_matrix.json
        ├── src/probiotics/screening_engine.py
        │     └── data/probiotics/probiotic_matrix.json
        ├── src/layer2_metabolism/pathway_database.py
        │     └── data/pathways/master_pathways.json
        └── src/core/config.py
              └── All data paths, thresholds, i18n definitions
```

---

## Performance Characteristics

- **Pathway database load time**: <100ms (in-memory index)
- **Phenotype scoring**: <10ms per 200-item questionnaire
- **Screening**: <50ms for 5 Meta-Strain recommendation
- **Full pipeline**: <500ms end-to-end
- **Dashboard render**: <2s initial load (Streamlit)

---

## Docker Deployment

```yaml
services:
  healthbook-api:
    build: .
    ports: ["8000:8000"]
    environment:
      - LANG=ja
    volumes:
      - ./data:/app/data

  healthbook-dashboard:
    build: ./dashboard
    ports: ["8501:8501"]
    environment:
      - API_URL=http://healthbook-api:8000
    depends_on:
      - healthbook-api
```

---

## Testing Strategy

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# E2E scenario tests
python -m tests.integration.test_e2e_scenarios

# Specific protocol tests
python -m tests.integration.test_malaria_protocol
```