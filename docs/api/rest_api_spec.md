# 📡 HealthBook-MBT55 REST API Specification

## Base URL

```
http://localhost:8000/api/v1
```

## Endpoints

### 1. Full Pipeline Execution

```http
POST /api/v1/pipeline
```

**Description**: Execute the full HealthBook pipeline: questionnaire → phenotyping → disease risk → Kampo recommendation → probiotic screening → metabolite prediction.

**Request Body**:
```json
{
  "language": "ja",
  "questionnaire_answers": {
    "甘いもの依存": true,
    "午後眠気": true,
    "冷え": true,
    "疲れやすい": true,
    "肌荒れ": true,
    "炎症": true,
    "アレルギー": true
  }
}
```

**Response**:
```json
{
  "language": "ja",
  "phenotype": {
    "scores": {
      "PATH_01": { "score": 65.0, "level": "注意", "name": "消化吸収・腸管バリア" },
      "PATH_02": { "score": 45.0, "level": "注意", "name": "肝解毒・フェーズI/II" },
      "PATH_03": { "score": 30.0, "level": "要改善", "name": "糖代謝・エネルギー産生" },
      "PATH_04": { "score": 25.0, "level": "要改善", "name": "酸化還元バランス・電子散逸" },
      "PATH_05": { "score": 55.0, "level": "注意", "name": "脳神経・ミトコンドリア機能" }
    },
    "overall_status": "注意（Caution）",
    "low_paths": ["PATH_03", "PATH_04"]
  },
  "disease_risks": {
    "D005-002（糖尿病）": 25.0,
    "D012-005（全身性炎症）": 35.0
  },
  "recommended_kampo": ["八味地黄丸", "十全大補湯", "鹿茸"],
  "probiotic_screening": {
    "recommended_strains": [
      {
        "strain_id": "MBT_META_04",
        "name": "電子駆動・ミネラル可溶化コンソーシアム",
        "priority": 1,
        "target_path": "PATH_04",
        "reason": "酸化還元不均衡（電子滞留）に対し、多経路電子散逸を回復します。"
      },
      {
        "strain_id": "MBT_META_05",
        "name": "安定化・酪酸生成クロスフィーディンググループ",
        "priority": 2,
        "target_path": "PATH_03",
        "reason": "糖代謝低下に対し、乳酸→酪酸のクロスフィーディングで短鎖脂肪酸合成を活性化します。"
      }
    ]
  },
  "metabolite_predictions": [
    {
      "substrate": "鹿茸",
      "found": true,
      "predictions": [
        {
          "final_metabolite": "新規ステロイド様代謝物 + フルボ酸キレート",
          "human_effects": ["免疫賦活", "組織修復", "骨形成促進"]
        }
      ]
    }
  ],
  "expected_effects": [
    "電子滞留解消・腐敗防止（dH₂/dt≈0）",
    "酪酸生成・抗炎症・エネルギ代謝改善"
  ]
}
```

### 2. Phenotype Scoring

```http
POST /api/v1/phenotype
```

**Request Body**:
```json
{
  "language": "ja",
  "questionnaire_answers": {
    "炎症": true,
    "アレルギー": true
  }
}
```

**Response**: PhenotypeResult object (see pipeline response `phenotype` field).

### 3. Probiotic Screening

```http
POST /api/v1/screening
```

**Request Body**: PhenotypeResult object

**Response**: ScreeningResult object (see pipeline response `probiotic_screening` field).

### 4. Pathway Lookup

```http
GET /api/v1/pathways/{substrate_name}
```

**Example**: `GET /api/v1/pathways/鹿茸`

**Response**: Metabolite prediction for the specified substrate.

### 5. Strain Definitions

```http
GET /api/v1/strains
```

**Response**: Array of all 5 Meta-Strain definitions with enzyme profiles, substrate preferences, and optimal conditions.

## Error Responses

```json
{
  "error": "PATHWAY_NOT_FOUND",
  "message": "No pathway found for 'unknown_substrate'",
  "status_code": 404
}
```

## Rate Limiting

- 100 requests/minute per IP
- Bulk pipeline endpoint: 10 requests/minute

## Authentication

API key required for production use. Pass via header:
```
X-API-Key: your-api-key-here
```