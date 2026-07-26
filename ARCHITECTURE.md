# Anomaly Detection System — Architecture

## System overview (verified from code)

File-backed, batch/on-demand pipeline: synthetic data generation → feature
engineering → model artifact creation → FastAPI inference → React frontend.
No external queue or database is used — everything is file-backed on disk, and
alerts are held in memory for the demo.

```mermaid
flowchart LR
  DataGen["Data Generation<br/>src/dataset_generator.py, src/attack_generator.py"]
  FeatEng["Feature Engineering<br/>src/feature_engineering.py"]
  Baseline["Baseline Profiling<br/>src/baseline_profiling.py<br/>-> trained_models/baseline_profile.pkl"]
  LSTMTrain["LSTM Training<br/>src/lstm_sequence_model.py<br/>-> trained_models/lstm_model.keras"]
  Artifacts["Trained Artifacts<br/>trained_models/*.pkl, *.keras"]
  Backend["FastAPI Backend<br/>app/backend/main.py<br/>loads DataService, InferenceService, AlertService"]
  API["API Routers<br/>analytics, models, alerts, anomalies, entities, health"]
  Frontend["React Dashboard<br/>app/frontend/src, routes in App.jsx"]

  DataGen --> FeatEng --> Baseline
  FeatEng --> LSTMTrain
  Baseline --> Artifacts
  LSTMTrain --> Artifacts
  Artifacts --> Backend --> API --> Frontend
```

## Data flow

1. `app/backend/main.py` initializes `DataService`, `InferenceService`, and
   `AlertService` on startup.
2. `InferenceService` loads artifacts from `trained_models/`: baseline
   profiles, scaler, both feature-column lists (baseline's 22-column list and
   the LSTM's separate 57-column one-hot-expanded list — these are distinct
   artifacts and are not interchangeable), and the LSTM model if TensorFlow is
   available.
3. Incoming events are scored by the baseline profiler and, if the LSTM is
   available, by the sequence model; both are combined in
   `_ensemble_decision()` in `app/backend/services/inference_service.py`.
4. Results are exposed via REST routers under `/api/v1/*` and consumed by the
   React frontend.

---

## Component pipeline

```mermaid
graph LR
    subgraph Generation["Generation"]
        SynData["Synthetic Data<br/>45,000 events"]
    end
    subgraph Processing["Processing"]
        FeatEng["Feature Engineering<br/>23 raw features"]
    end
    subgraph Detection["Detection"]
        BP["Baseline<br/>Profiling"]
        LSTM["LSTM<br/>Sequence Model"]
    end
    subgraph Ensemble["Ensemble Decision"]
        Voting["Weighted Blend<br/>40% baseline / 60% LSTM<br/>OR-based flagging"]
    end
    subgraph Analysis["Analysis"]
        Confidence["Confidence Scoring"]
        Attribution["Flagged-By Attribution"]
    end
    subgraph Presentation["Presentation"]
        Dashboard["Alert Dashboard"]
        Explain["Reason / Explanation"]
    end

    Generation -->|Raw| Processing
    Processing -->|Features| Detection
    Detection -->|Scores| Ensemble
    Ensemble -->|Result| Analysis
    Analysis -->|Labeled| Presentation

    style Generation fill:#e3f2fd
    style Processing fill:#f3e5f5
    style Detection fill:#fff3e0
    style Ensemble fill:#fce4ec
    style Analysis fill:#e0f2f1
    style Presentation fill:#c8e6c9
```

---

## Baseline profiling — actual scoring logic

Verified against `_score_baseline()` in `inference_service.py`. There are
exactly **four** deviation checks — no device-fingerprint check exists in the
live baseline scorer.

```mermaid
graph TD
    Event["Event Input"]
    Event -->|entity_id| Lookup["Profile Lookup<br/>(per-entity, from baseline_profile.pkl)"]

    Lookup --> Cold{"Entity known?"}
    Cold -->|NO| ColdScore["Score = 2.0 (flat)<br/>'Unknown entity - cold start detected'"]

    Cold -->|YES| Check1["Resource in entity's normal set?"]
    Check1 -->|NO| Score1["+2.0<br/>'Unauthorized resource access'"]

    Check1 --> Check2["Location matches normal?"]
    Check2 -->|NO| Score2["+1.5<br/>'Impossible travel detected'"]

    Check2 --> Check3["Auth method in normal set?"]
    Check3 -->|NO| Score3["+1.0<br/>'Unusual authentication method'"]

    Check3 --> Check4["Session duration vs. mean±std"]
    Check4 -->|">2.5x tolerance"| Score4["+1.5<br/>'Extreme session duration anomaly'"]
    Check4 -->|">1.5x tolerance"| Score5["+0.5<br/>'Moderate session duration drift'"]

    Score1 --> Sum["Sum all triggered points"]
    Score2 --> Sum
    Score3 --> Sum
    Score4 --> Sum
    Score5 --> Sum

    Sum -->|"score > 0.5 (ANOMALY_THRESHOLD)"| Flag["Flagged: baseline_flag = True"]
    Sum -->|"score <= 0.5"| Normal["Not flagged by baseline"]

    style Flag fill:#ffcdd2
    style Normal fill:#c8e6c9
    style ColdScore fill:#fff9c4
```

---

## LSTM architecture

Verified: 57-feature input (confirmed by direct inspection of
`trained_models/lstm_feature_columns.pkl`), 15 training epochs, batch size 32
(`src/lstm_sequence_model.py`).

```mermaid
graph TD
    Input["Input: 5-Event Sequences<br/>Shape: (5, 57)<br/>6 numeric + 7 boolean + 44 one-hot categorical"]

    Input --> Mask["Masking Layer<br/>(for zero-padded cold-start sequences)"]
    Mask --> LSTM1["LSTM Layer 1<br/>Units: 128, return_sequences=True"]
    LSTM1 --> Drop1["Dropout 0.4"]
    Drop1 --> LSTM2["LSTM Layer 2<br/>Units: 64"]
    LSTM2 --> Drop2["Dropout 0.3"]
    Drop2 --> Dense1["Dense 64, ReLU"]
    Dense1 --> Drop3["Dropout 0.3"]
    Drop3 --> Dense2["Dense 32, ReLU"]
    Dense2 --> Drop4["Dropout 0.2"]
    Drop4 --> Output["Dense 1, Sigmoid"]

    Output -->|"Threshold: calibrated (lstm_threshold.pkl)"| Predict["LSTM confidence<br/>0.0 - 1.0"]

    style Input fill:#e3f2fd
    style LSTM1 fill:#fff3e0
    style LSTM2 fill:#fff3e0
    style Dense1 fill:#f3e5f5
    style Dense2 fill:#f3e5f5
    style Output fill:#c8e6c9
    style Predict fill:#ffccbc
```

Trained with class-weighted binary crossentropy
(`compute_class_weight("balanced")`) to address the extreme class-imbalance
challenge from the brief.

---

## Ensemble decision logic

Verified against `_ensemble_decision()` in `inference_service.py`. There are
exactly **four** outcomes — `both`, `lstm`-only, `baseline`-only, `none`. No
separate "medium confidence, ≥0.7" tier exists in the real code.

```mermaid
graph TD
    Event["New Event"]

    Event --> BP_Score["Baseline Score"]
    Event --> LSTM_Score["LSTM Confidence"]

    BP_Score -->|"score > 0.5"| BP_Flag{"Baseline<br/>flagged?"}
    LSTM_Score -->|"confidence > lstm_threshold"| LSTM_Flag{"LSTM<br/>flagged?"}

    BP_Flag -->|YES| Both_Check
    LSTM_Flag -->|YES| Both_Check

    Both_Check{"Both flagged?"}
    Both_Check -->|YES| Both_Out["flagged_by = 'both'<br/>confidence = 0.95"]
    Both_Check -->|"LSTM only"| LSTM_Out["flagged_by = 'lstm'<br/>confidence = lstm_normalized"]
    Both_Check -->|"Baseline only"| BP_Out["flagged_by = 'baseline'<br/>confidence = baseline_normalized"]

    BP_Flag -->|NO| None_Check
    LSTM_Flag -->|NO| None_Check
    None_Check{"Neither flagged?"}
    None_Check -->|YES| None_Out["flagged_by = 'none'<br/>confidence = 1 - ensemble_score"]

    style Both_Out fill:#ffcdd2
    style LSTM_Out fill:#ffe0b2
    style BP_Out fill:#fff9c4
    style None_Out fill:#c8e6c9
```

`ensemble_score = 0.4 × baseline_normalized + 0.6 × lstm_normalized` (used for
ranking severity, not for the flag/no-flag decision itself, which is OR-based
per above).

---

## Key statistics (verified)

| Component | Value | Source |
|---|---|---|
| Data size | 45,000 events | `data/raw/cybersecurity_dataset.csv` |
| Unique users | 500 | `src/user_generator.py` |
| Unique devices | 700 | `src/device_generator.py` |
| Attack rate | 2% (900 events) | dataset label counts |
| Raw features | 23 | `src/feature_engineering.py` |
| LSTM input features | 57 (after one-hot expansion) | `trained_models/lstm_feature_columns.pkl` |
| LSTM training epochs | 15 | `src/lstm_sequence_model.py` |
| LSTM batch size | 32 | `src/lstm_sequence_model.py` |
| LSTM layers | 2 LSTM (128, 64) + 2 Dense (64, 32) | `src/lstm_sequence_model.py` |
| Sequence window | 5 events | `WINDOW_SIZE` in `inference_service.py` |
| Ensemble weight split | Baseline 40% / LSTM 60% | `app/backend/config.py` |
| Baseline flag threshold | 0.5 | `ANOMALY_THRESHOLD` in `config.py` |
| Attack types | 8 | `src/attack_generator.py` |

---

## Implementation files

**Core detection**
- `src/baseline_profiling.py` — baseline statistical detector
- `src/lstm_sequence_model.py` — LSTM training
- `app/backend/services/inference_service.py` — live scoring + ensemble decision

**Data processing**
- `src/dataset_generator.py` — orchestrates synthetic data generation
- `src/feature_engineering.py` — 23-feature pipeline

**Generation & attacks**
- `src/user_generator.py`, `src/device_generator.py`, `src/event_generator.py`
- `src/attack_generator.py` — 8 attack types

**Output & explanation**
- `src/dashboard.py` — CLI alert queue
- `src/explainability.py` — reason generation

**Evaluation**
- `src/evaluate_models.py` — real held-out precision/recall/F1/AUC + alert-budget FPR

**Models**
- `trained_models/lstm_model.keras`
- `trained_models/baseline_profile.pkl`