# Warranty Claim Audit System - Project Plan

## Problem Statement

### Current State

Warranty claims are currently audited using a vector database approach that performs 1:1 similarity matching against historical claims. When a new claim arrives, the system asks: *"Has a very similar claim been submitted before? If so, what was the outcome?"*

While this approach works for straightforward cases, it has significant limitations:

### Key Challenges

1. **Granularity Problem**
   - Claims contain multiple distinct components (symptoms, diagnoses, proposed repairs, labor estimates, parts lists)
   - Current 1:1 matching treats claims as monolithic units
   - A claim with a legitimate symptom but inflated labor estimate gets compared holistically, missing the specific anomaly
   - No ability to independently validate each component against historical norms

2. **Limited Pattern Recognition**
   - Vector similarity only finds "claims that look like this one"
   - Cannot learn complex fraud patterns that span multiple features (e.g., "this combination of vehicle age + repair type + labor hours is suspicious")
   - Struggles with novel fraud schemes that don't closely match historical examples

3. **PII Exposure**
   - Historical claim data contains personally identifiable information (customer names, VINs, dealer info)
   - Current architecture requires PII to flow through the matching pipeline
   - Creates compliance risk and limits ability to use cloud-based or third-party ML services

4. **Training Data Scarcity**
   - Labeled fraud examples are rare and valuable
   - System cannot easily learn from hypothetical or edge-case scenarios
   - No mechanism to systematically generate test cases for known fraud patterns

### Desired Outcome

A hybrid auditing system that:
- Decomposes claims into semantic components and evaluates each independently
- Combines retrieval-based matching with learned ML patterns
- Handles PII appropriately through redaction before processing
- Can be trained on a mix of real historical data and synthetic examples
- Outputs an explainable confidence score with contributing factors

---

## Executive Summary

This document outlines the architecture and implementation plan for a hybrid warranty claim auditing system that combines:
- **Component-level claim decomposition** for granular analysis
- **Vector similarity retrieval** for historical claim matching
- **Supervised ML classification** for pattern-based fraud detection
- **Synthetic + real data training** for robust model performance

---

## 1. High-Level System Architecture

```mermaid
flowchart TB
    subgraph Input
        RC[Raw Claim]
    end

    subgraph Preprocessing
        PII[PII Redaction]
        CD[Component Decomposer]
    end

    subgraph "Dual Scoring Engine"
        direction TB
        subgraph Vector Path
            EMB1[Component Embeddings]
            VS[Vector Similarity Search]
            HS[Historical Score]
        end
        subgraph ML Path
            EMB2[Feature Extraction]
            ML[Supervised ML Model]
            MS[Model Score]
        end
    end

    subgraph Output
        SF[Score Fusion]
        CS[Confidence Score]
        EXP[Explanation Factors]
    end

    RC --> PII --> CD
    CD --> EMB1 --> VS --> HS
    CD --> EMB2 --> ML --> MS
    HS --> SF
    MS --> SF
    SF --> CS
    SF --> EXP
```

---

## 2. Claim Component Decomposition

### 2.1 Component Categories

| Component | Description | Example |
|-----------|-------------|---------|
| **Symptom** | Customer-reported issue | "Vehicle makes grinding noise when braking" |
| **Diagnosis** | Technician findings | "Brake pads worn to 2mm, rotors scored" |
| **Parts** | Components to replace | "Front brake pads, rotors (pair)" |
| **Labor** | Proposed work hours | "2.5 hours book time" |
| **Vehicle Context** | Make/model/year/mileage | "2019 F-150, 45,000 miles" |
| **Verbatim** | Raw customer language | "It's been squealing for weeks" |

### 2.2 Decomposition Pipeline

```mermaid
flowchart LR
    subgraph "Raw Claim Input"
        RAW[Unstructured Claim Text]
    end

    subgraph "Extraction Layer"
        NER[Named Entity Recognition]
        SEC[Section Classifier]
        STRUCT[Structured Field Parser]
    end

    subgraph "Component Outputs"
        SYM[Symptom Vector]
        DIAG[Diagnosis Vector]
        PARTS[Parts Vector]
        LABOR[Labor Features]
        VEH[Vehicle Features]
        VERB[Verbatim Vector]
    end

    RAW --> NER
    RAW --> SEC
    RAW --> STRUCT

    NER --> PARTS
    NER --> VEH
    SEC --> SYM
    SEC --> DIAG
    SEC --> VERB
    STRUCT --> LABOR
```

### 2.3 PII Handling in Decomposition

```mermaid
flowchart LR
    subgraph "PII Detection"
        RAW[Raw Text]
        NER_PII[PII Entity Recognition]
    end

    subgraph "Redaction"
        MASK[Entity Masking]
        PLACEHOLDER["[CUSTOMER_NAME]<br/>[VIN]<br/>[DEALER_ID]"]
    end

    subgraph "Clean Output"
        CLEAN[Redacted Claim]
        MAPPING[PII Mapping Table<br/>Stored Separately]
    end

    RAW --> NER_PII --> MASK --> PLACEHOLDER --> CLEAN
    NER_PII --> MAPPING
```

---

## 3. Dual Scoring System

### 3.1 Why Two Paths?

| Vector Similarity Path | Supervised ML Path |
|------------------------|-------------------|
| "Have we seen this exact situation before?" | "Does this match learned fraud patterns?" |
| Explainable via similar claims | Captures complex non-linear relationships |
| No training required | Requires labeled training data |
| Struggles with novel fraud | Generalizes to unseen patterns |

### 3.2 Vector Similarity Scoring Pipeline

```mermaid
flowchart TB
    subgraph "Incoming Claim"
        IC[Decomposed Components]
    end

    subgraph "Per-Component Search"
        direction TB
        S_SYM[Symptom Search]
        S_DIAG[Diagnosis Search]
        S_PARTS[Parts Search]
        S_LABOR[Labor Comparison]
    end

    subgraph "Historical Matches"
        M_SYM[Top-K Symptom Matches]
        M_DIAG[Top-K Diagnosis Matches]
        M_PARTS[Top-K Parts Matches]
        M_LABOR[Labor Baseline Stats]
    end

    subgraph "Component Scores"
        CS_SYM[Symptom Consistency: 0.85]
        CS_DIAG[Diagnosis Consistency: 0.72]
        CS_PARTS[Parts Appropriateness: 0.91]
        CS_LABOR[Labor Reasonableness: 0.45]
    end

    subgraph "Aggregation"
        WEIGHTED[Weighted Combination]
        VS_SCORE[Vector Similarity Score: 0.73]
    end

    IC --> S_SYM --> M_SYM --> CS_SYM
    IC --> S_DIAG --> M_DIAG --> CS_DIAG
    IC --> S_PARTS --> M_PARTS --> CS_PARTS
    IC --> S_LABOR --> M_LABOR --> CS_LABOR

    CS_SYM --> WEIGHTED
    CS_DIAG --> WEIGHTED
    CS_PARTS --> WEIGHTED
    CS_LABOR --> WEIGHTED
    WEIGHTED --> VS_SCORE
```

### 3.3 Supervised ML Scoring Pipeline

```mermaid
flowchart TB
    subgraph "Feature Engineering"
        COMP[Component Embeddings]
        STRUCT[Structured Features]
        CROSS[Cross-Component Features]
    end

    subgraph "Structured Features"
        direction TB
        F1[Labor hours requested]
        F2[Parts cost total]
        F3[Vehicle age/mileage]
        F4[Dealer history stats]
        F5[Claim frequency for VIN]
    end

    subgraph "Cross-Component Features"
        direction TB
        X1[Symptom-Diagnosis similarity]
        X2[Diagnosis-Parts alignment]
        X3[Labor vs book time delta]
        X4[Parts cost vs historical avg]
    end

    subgraph "Model"
        CONCAT[Feature Concatenation]
        XGB[XGBoost Classifier]
        ML_SCORE[ML Score: 0.68]
    end

    COMP --> CONCAT
    F1 --> STRUCT
    F2 --> STRUCT
    F3 --> STRUCT
    F4 --> STRUCT
    F5 --> STRUCT
    STRUCT --> CONCAT
    X1 --> CROSS
    X2 --> CROSS
    X3 --> CROSS
    X4 --> CROSS
    CROSS --> CONCAT
    CONCAT --> XGB --> ML_SCORE
```

---

## 4. Score Fusion & Final Output

```mermaid
flowchart TB
    subgraph "Input Scores"
        VS[Vector Similarity Score<br/>0.73]
        ML[ML Model Score<br/>0.68]
    end

    subgraph "Confidence Calibration"
        VS_CAL[Calibrated VS: 0.71]
        ML_CAL[Calibrated ML: 0.65]
    end

    subgraph "Fusion Strategy"
        direction TB
        ENSEMBLE[Weighted Ensemble]
        DISAGREE{Significant<br/>Disagreement?}
        FLAG[Flag for Review]
    end

    subgraph "Output"
        FINAL[Final Confidence: 0.68]
        FACTORS[Contributing Factors]
        ACTION[Recommended Action]
    end

    VS --> VS_CAL --> ENSEMBLE
    ML --> ML_CAL --> ENSEMBLE
    ENSEMBLE --> DISAGREE
    DISAGREE -->|Yes| FLAG --> FINAL
    DISAGREE -->|No| FINAL
    ENSEMBLE --> FACTORS
    FINAL --> ACTION

    subgraph "Factor Breakdown"
        direction TB
        FB1["Labor Hours: HIGH CONCERN"]
        FB2["Parts Match: Normal"]
        FB3["Historical Pattern: Normal"]
        FB4["Symptom-Repair Match: Normal"]
    end

    FACTORS --> FB1
    FACTORS --> FB2
    FACTORS --> FB3
    FACTORS --> FB4
```

---

## 5. Training Data Strategy

### 5.1 Hybrid Data Pipeline

```mermaid
flowchart TB
    subgraph "Real Data"
        HIST[Historical Claims]
        LABEL[Human Labels<br/>Approved/Flagged/Fraud]
        CLEAN_REAL[PII-Redacted Dataset]
    end

    subgraph "Synthetic Data"
        TEMPLATES[Claim Templates]
        LLM[LLM Generator]
        RULES[Domain Rules<br/>Book Times, Part Costs]
        SYN_CLAIMS[Synthetic Claims]
    end

    subgraph "Synthetic Categories"
        direction TB
        LEGIT[Legitimate Claims<br/>Varying complexity]
        INFLATE[Labor Inflation<br/>Fraud pattern]
        UNNECESSARY[Unnecessary Parts<br/>Fraud pattern]
        MISMATCH[Symptom-Repair Mismatch<br/>Fraud pattern]
    end

    subgraph "Combined Dataset"
        MERGE[Merged Training Set]
        SPLIT[Train/Val/Test Split]
    end

    HIST --> LABEL --> CLEAN_REAL --> MERGE
    TEMPLATES --> LLM
    RULES --> LLM
    LLM --> SYN_CLAIMS
    SYN_CLAIMS --> LEGIT --> MERGE
    SYN_CLAIMS --> INFLATE --> MERGE
    SYN_CLAIMS --> UNNECESSARY --> MERGE
    SYN_CLAIMS --> MISMATCH --> MERGE
    MERGE --> SPLIT
```

### 5.2 Synthetic Data Generation Detail

```mermaid
flowchart LR
    subgraph "Generation Inputs"
        VEH_DB[Vehicle Database<br/>Make/Model/Year]
        PART_DB[Parts Catalog<br/>Costs, Categories]
        LABOR_DB[Book Time Standards]
        FAILURE_DB[Common Failure Modes]
    end

    subgraph "LLM Generation"
        PROMPT[Structured Prompt]
        LLM[Language Model]
        NARRATIVE[Realistic Narrative]
    end

    subgraph "Validation"
        RULE_CHECK[Rule-Based Validation]
        CONSISTENCY[Internal Consistency Check]
        FINAL_SYN[Validated Synthetic Claim]
    end

    VEH_DB --> PROMPT
    PART_DB --> PROMPT
    LABOR_DB --> PROMPT
    FAILURE_DB --> PROMPT
    PROMPT --> LLM --> NARRATIVE --> RULE_CHECK --> CONSISTENCY --> FINAL_SYN
```

---

## 6. Model Training Pipeline

```mermaid
flowchart TB
    subgraph "Data Preparation"
        RAW_DATA[Combined Dataset]
        DECOMPOSE[Component Decomposition]
        EMBED[Generate Embeddings]
        FEATURES[Extract Features]
    end

    subgraph "Training"
        TRAIN_SET[Training Set 70%]
        VAL_SET[Validation Set 15%]
        TEST_SET[Test Set 15%]

        XGB_TRAIN[XGBoost Training]
        HYPERPARAM[Hyperparameter Tuning]
        CALIBRATE[Probability Calibration]
    end

    subgraph "Evaluation"
        METRICS[Metrics Computation]
        PRECISION[Precision @ K]
        RECALL[Recall on Fraud]
        AUC[ROC-AUC]
        THRESH[Threshold Selection]
    end

    subgraph "Artifacts"
        MODEL[Trained Model]
        EMBED_MODEL[Embedding Model Reference]
        CONFIG[Feature Config]
        THRESH_FILE[Decision Thresholds]
    end

    RAW_DATA --> DECOMPOSE --> EMBED --> FEATURES
    FEATURES --> TRAIN_SET --> XGB_TRAIN
    FEATURES --> VAL_SET --> HYPERPARAM
    FEATURES --> TEST_SET --> METRICS

    XGB_TRAIN --> HYPERPARAM --> CALIBRATE --> MODEL
    METRICS --> PRECISION
    METRICS --> RECALL
    METRICS --> AUC
    METRICS --> THRESH --> THRESH_FILE

    MODEL --> ARTIFACTS
    EMBED_MODEL --> ARTIFACTS
    CONFIG --> ARTIFACTS
```

---

## 7. Inference Pipeline (Production)

```mermaid
flowchart TB
    subgraph "Claim Intake"
        API[API Endpoint]
        QUEUE[Message Queue]
        CLAIM[Raw Claim]
    end

    subgraph "Processing"
        PII_SVC[PII Redaction Service]
        DECOMP_SVC[Decomposition Service]
        EMBED_SVC[Embedding Service]
    end

    subgraph "Scoring Services"
        VEC_SVC[Vector Search Service]
        ML_SVC[ML Scoring Service]
        FUSION_SVC[Score Fusion Service]
    end

    subgraph "Output"
        RESULT[Confidence Score + Factors]
        DB[(Results Database)]
        NOTIFY[Notification Service]
    end

    subgraph "Routing"
        ROUTER{Score Threshold}
        AUTO_APPROVE[Auto-Approve]
        HUMAN_REVIEW[Human Review Queue]
        AUTO_FLAG[Auto-Flag]
    end

    API --> QUEUE --> CLAIM --> PII_SVC --> DECOMP_SVC --> EMBED_SVC
    EMBED_SVC --> VEC_SVC --> FUSION_SVC
    EMBED_SVC --> ML_SVC --> FUSION_SVC
    FUSION_SVC --> RESULT --> DB
    RESULT --> ROUTER
    ROUTER -->|Score > 0.8| AUTO_APPROVE
    ROUTER -->|0.4 < Score < 0.8| HUMAN_REVIEW
    ROUTER -->|Score < 0.4| AUTO_FLAG
    HUMAN_REVIEW --> NOTIFY
    AUTO_FLAG --> NOTIFY
```

---

## 8. Implementation Phases

### Phase 1: Foundation
- [ ] Set up development environment
- [ ] Implement PII redaction pipeline
- [ ] Build claim component decomposer
- [ ] Select and integrate embedding model

### Phase 2: Vector Similarity System
- [ ] Set up vector database (Pinecone, Weaviate, or Qdrant)
- [ ] Implement per-component embedding and indexing
- [ ] Build similarity search and scoring logic
- [ ] Create baseline evaluation metrics

### Phase 3: Synthetic Data Generation
- [ ] Define claim templates and variation parameters
- [ ] Build LLM-based claim generator
- [ ] Implement rule-based validation
- [ ] Generate initial training dataset (legitimate + fraud patterns)

### Phase 4: Supervised ML Model
- [ ] Feature engineering pipeline
- [ ] Model training and hyperparameter tuning
- [ ] Probability calibration
- [ ] Evaluation on held-out test set

### Phase 5: Score Fusion & Integration
- [ ] Implement score fusion logic
- [ ] Build explanation/factor extraction
- [ ] Create API endpoints
- [ ] Set up routing thresholds

### Phase 6: API & Web UI
- [ ] Build REST API with FastAPI exposing `/score` endpoint (accepts claim text, returns detailed confidence scores and contributing factors)
- [ ] Add `/health` and `/status` endpoints for service monitoring
- [ ] Build simple web UI (single-page) with:
  - [ ] Text input area for pasting/typing raw claim text
  - [ ] Submit button to send claim for scoring
  - [ ] Results panel showing overall confidence score, per-component scores (symptom, diagnosis, parts, labor), contributing factor breakdown, and recommended action (auto-approve / review / flag)
  - [ ] History sidebar showing previous submissions in the current session
- [ ] Containerize the web UI (lightweight Nginx + static assets or Node server)
- [ ] Wire web UI to API via OpenAPI-generated client

### Phase 7: Production Hardening
- [ ] Performance optimization
- [ ] Monitoring and alerting
- [ ] A/B testing framework
- [ ] Feedback loop for model retraining

---

## 9. Technology Stack Recommendations

| Component | Recommended Tools |
|-----------|------------------|
| **Embedding Model** | `sentence-transformers/all-MiniLM-L6-v2` or `BAAI/bge-small-en` |
| **Vector Database** | Qdrant (self-hosted) or Pinecone (managed) |
| **ML Framework** | XGBoost + scikit-learn |
| **Synthetic Generation** | Claude API or GPT-4 with structured prompts |
| **PII Detection** | Presidio (Microsoft) or spaCy NER |
| **Orchestration** | FastAPI + Celery or AWS Step Functions |
| **Feature Store** | Feast or custom Postgres-based |
| **Web UI** | React (Vite) or plain HTML/JS with Tailwind CSS |
| **API Documentation** | FastAPI auto-generated OpenAPI/Swagger UI |
| **Containerization** | Docker Compose (API + Qdrant + Embedding Service + Web UI) |

---

## 10. Success Metrics

| Metric | Target | Rationale |
|--------|--------|-----------|
| **Precision @ Human Review** | > 70% | Flagged claims should be worth reviewing |
| **Recall on Known Fraud** | > 90% | Catch most fraudulent claims |
| **Auto-Approve Rate** | > 60% | Reduce human workload |
| **False Flag Rate** | < 5% | Minimize dealer friction |
| **Processing Latency** | < 2 sec | Real-time scoring |

---

## Appendix: Sample Claim Flow

```mermaid
sequenceDiagram
    participant Dealer
    participant API
    participant Preprocessor
    participant VectorDB
    participant MLModel
    participant Fusion
    participant Reviewer

    Dealer->>API: Submit Claim
    API->>Preprocessor: Raw Claim
    Preprocessor->>Preprocessor: PII Redaction
    Preprocessor->>Preprocessor: Component Decomposition

    par Vector Path
        Preprocessor->>VectorDB: Component Embeddings
        VectorDB->>VectorDB: Similarity Search
        VectorDB->>Fusion: Vector Score (0.73)
    and ML Path
        Preprocessor->>MLModel: Features
        MLModel->>MLModel: Inference
        MLModel->>Fusion: ML Score (0.68)
    end

    Fusion->>Fusion: Score Combination
    Fusion->>API: Final Score (0.68) + Factors

    alt Score < 0.4
        API->>Reviewer: Route to Review Queue
    else Score > 0.8
        API->>Dealer: Auto-Approved
    else 0.4 <= Score <= 0.8
        API->>Reviewer: Route to Review Queue
    end
```
