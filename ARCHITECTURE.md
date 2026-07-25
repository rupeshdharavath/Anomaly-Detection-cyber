# Anomaly Detection System - Architecture Diagram

## System Architecture Overview

```mermaid
graph TB
    subgraph Data["Data Generation & Processing"]
        DG["Dataset Generator<br/>45,000 synthetic events"]
        UG["User Generator<br/>500 unique users"]
        DEV["Device Generator<br/>700 unique devices"]
        PG["Profile Generator<br/>Baseline behaviors"]
        AG["Attack Generator<br/>900 injected attacks"]
        EG["Event Generator<br/>Normal baseline events"]
    end
    
    subgraph Feature["Feature Engineering"]
        FE["Feature Engineering<br/>23 processed features"]
        SS["StandardScaler<br/>Numeric normalization"]
        LE["LabelEncoder<br/>Categorical encoding"]
    end
    
    subgraph Models["Detection Models"]
        BP["Baseline Profiling<br/>Statistical anomalies<br/>40% weight"]
        LSTM["LSTM Sequence Model<br/>Deep learning detector<br/>60% weight"]
    end
    
    subgraph Training["Model Training"]
        LSTM_Train["LSTM Training<br/>Epochs: 15<br/>Batch Size: 32<br/>Class Weighted"]
        BP_Train["Baseline Profile Building<br/>Per-entity statistics"]
        CAL["Threshold Calibration<br/>F1 score optimization"]
    end
    
    subgraph Persistence["Model Persistence"]
        LSTM_Model["lstm_model.keras<br/>Stacked LSTM architecture"]
        LSTM_Meta["lstm_metadata.pkl<br/>Training metadata"]
        BP_Profile["baseline_profile.pkl<br/>500 entity profiles"]
        Scaler["scaler.pkl<br/>Feature normalization"]
    end
    
    subgraph Inference["Inference Pipeline"]
        Predict["Prediction Engine<br/>Weighted Ensemble Voting<br/>40% Baseline + 60% LSTM"]
        Confidence["Confidence Scoring<br/>0-1 normalized scale"]
        Attribution["Source Attribution<br/>Baseline/LSTM/Both"]
    end
    
    subgraph Output["Output & Explanation"]
        Dashboard["Alert Dashboard<br/>Risk ranking & alerts"]
        Explain["Explainability Engine<br/>Detailed anomaly reasons"]
        History["Entity History View<br/>Temporal context"]
    end
    
    Data -->|Raw Events| Feature
    Feature -->|23 Features| Models
    Models -->|Profiles & Sequences| Training
    Training -->|Trained Models| Persistence
    Persistence -->|Load Models| Inference
    Inference -->|Predictions| Output
    Models -->|Reference| Inference
    
    style Data fill:#e1f5ff
    style Feature fill:#f3e5f5
    style Models fill:#fff3e0
    style Training fill:#f1f8e9
    style Persistence fill:#fce4ec
    style Inference fill:#ffe0b2
    style Output fill:#c8e6c9
```

## Data Flow

```mermaid
sequenceDiagram
    participant User as End User/Analyst
    participant Inf as Inference Engine
    participant BP as Baseline Profiler
    participant LSTM as LSTM Model
    participant Expl as Explainability Engine
    participant Dash as Dashboard
    
    User->>Inf: New Event Batch
    activate Inf
    Inf->>BP: Score Against Baseline
    activate BP
    BP-->>Inf: Baseline Score + Reasons
    deactivate BP
    
    Inf->>LSTM: Check Sequence Pattern
    activate LSTM
    LSTM-->>Inf: LSTM Confidence Score
    deactivate LSTM
    
    Inf->>Inf: Weighted Ensemble Voting<br/>(40% Baseline + 60% LSTM)
    Inf->>Inf: Generate Confidence Score<br/>& Source Attribution
    Inf-->>User: Prediction Result
    deactivate Inf
    
    User->>Expl: Request Explanation
    activate Expl
    Expl-->>User: Baseline Reasons + LSTM Context
    deactivate Expl
    
    User->>Dash: View Alerts
    activate Dash
    Dash-->>User: Top Alerts Ranked by Risk
    deactivate Dash
```

## Component Interactions

```mermaid
graph LR
    subgraph Generation["Generation Phase"]
        SynData["Synthetic Data<br/>45,000 events"]
    end
    
    subgraph Processing["Processing Phase"]
        FeatEng["Feature Engineering<br/>23 features"]
    end
    
    subgraph Detection["Detection Phase"]
        BP["Baseline<br/>Profiling"]
        LSTM["LSTM Deep<br/>Learning"]
    end
    
    subgraph Ensemble["Ensemble Decision"]
        Voting["Weighted Voting<br/>40/60 split"]
    end
    
    subgraph Analysis["Analysis Phase"]
        Confidence["Confidence<br/>Scoring"]
        Attribution["Source<br/>Attribution"]
    end
    
    subgraph Presentation["Presentation Phase"]
        Dashboard["Alert<br/>Dashboard"]
        Explain["Anomaly<br/>Explanation"]
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

## Baseline Profiling Architecture

```mermaid
graph TD
    Event["Event Input"]
    Event -->|Entity ID| Lookup["Profile Lookup<br/>500 profiles"]
    
    Lookup -->|User Profile| Check1["Check Baseline Behaviors"]
    Check1 -->|Unauthorized Resource?| Score1["Score: +2.0 points<br/>Insider Threat"]
    Check1 -->|Impossible Travel?| Score2["Score: +1.5 points<br/>Location anomaly"]
    Check1 -->|Unknown Device?| Score3["Score: +1.0 point<br/>Device anomaly"]
    Check1 -->|Unknown Auth Method?| Score4["Score: +1.0 point<br/>Auth anomaly"]
    
    Check1 -->|Session Duration| Drift["Calculate Drift<br/>σ × 1.5 tolerance"]
    Drift -->|>2.5σ| Score5["Score: +1.5 points<br/>High drift"]
    Drift -->|>1.5σ| Score6["Score: +0.5 points<br/>Moderate drift"]
    
    Score1 --> Sum["Sum All Weights"]
    Score2 --> Sum
    Score3 --> Sum
    Score4 --> Sum
    Score5 --> Sum
    Score6 --> Sum
    
    Sum -->|Score > 1.5| Flag["🚨 ANOMALY<br/>Return: Flagged"]
    Sum -->|Score ≤ 1.5| Normal["✅ NORMAL<br/>Return: Clean"]
    
    style Flag fill:#ffcdd2
    style Normal fill:#c8e6c9
```

## LSTM Architecture

```mermaid
graph TD
    Input["Input: 5-Event Sequences<br/>Shape: 5 × 23 features"]
    
    Input --> LSTM1["LSTM Layer 1<br/>Units: 128<br/>return_sequences=True"]
    LSTM1 --> Drop1["Dropout<br/>Rate: 0.4"]
    
    Drop1 --> LSTM2["LSTM Layer 2<br/>Units: 64"]
    LSTM2 --> Drop2["Dropout<br/>Rate: 0.3"]
    
    Drop2 --> Dense1["Dense Layer<br/>Units: 64<br/>Activation: ReLU"]
    Dense1 --> Drop3["Dropout<br/>Rate: 0.3"]
    
    Drop3 --> Dense2["Dense Layer<br/>Units: 32<br/>Activation: ReLU"]
    Dense2 --> Drop4["Dropout<br/>Rate: 0.2"]
    
    Drop4 --> Output["Output Layer<br/>Units: 1<br/>Activation: Sigmoid"]
    
    Output -->|Threshold: Calibrated| Predict["Anomaly Score<br/>0.0 - 1.0"]
    
    style Input fill:#e3f2fd
    style LSTM1 fill:#fff3e0
    style LSTM2 fill:#fff3e0
    style Dense1 fill:#f3e5f5
    style Dense2 fill:#f3e5f5
    style Output fill:#c8e6c9
    style Predict fill:#ffccbc
```

## Ensemble Decision Logic

```mermaid
graph TD
    Event["New Event"]
    
    Event --> BP_Score["Baseline Score"]
    Event --> LSTM_Score["LSTM Score"]
    
    BP_Score -->|Threshold: 0.5| BP_Flag{"BP<br/>Anomaly?"}
    LSTM_Score -->|Threshold: 0.5| LSTM_Flag{"LSTM<br/>Anomaly?"}
    
    BP_Flag -->|YES| BP_Y["✅ Baseline"]
    BP_Flag -->|NO| BP_N["❌ Baseline"]
    
    LSTM_Flag -->|YES| LSTM_Y["✅ LSTM"]
    LSTM_Flag -->|NO| LSTM_N["❌ LSTM"]
    
    BP_Y --> Both{"Both<br/>Agree?"}
    LSTM_Y --> Both
    
    BP_Y --> BPOnly{"Only<br/>LSTM?"}
    LSTM_Y --> BPOnly
    
    Both -->|YES| Confidence_H["🔴 HIGH CONFIDENCE<br/>Confidence: 0.95<br/>Flagged By: Both"]
    Both -->|NO| Confidence_M{"Single<br/>≥0.7?"}
    
    Confidence_M -->|YES| Confidence_M2["🟠 MEDIUM CONFIDENCE<br/>Confidence: 0.75<br/>Flagged By: LSTM/Baseline"]
    Confidence_M -->|NO| Confidence_L["🟢 LOW CONFIDENCE<br/>Confidence: 0.3<br/>Status: Normal"]
    
    BPOnly -->|Only BP| Confidence_B["🟠 BEHAVIORAL ANOMALY<br/>Flagged By: Baseline"]
    BPOnly -->|Neither| Confidence_L
    
    style Confidence_H fill:#ffcdd2
    style Confidence_M2 fill:#ffe0b2
    style Confidence_L fill:#c8e6c9
    style Confidence_B fill:#fff9c4
```

## Attack Type Detection Patterns

```mermaid
graph TB
    Attack["Attack Detected"]
    
    Attack -->|Multiple Failed<br/>Logins 20-50| BF["🔴 Brute Force<br/>Odd hours 1-4 AM"]
    Attack -->|Location Change<br/>Impossible Travel| IT["🔴 Impossible Travel<br/>New IP + Location"]
    Attack -->|Many Failures<br/>15-40 Off-hours| CS["🔴 Credential Stuffing<br/>0-5 AM window"]
    Attack -->|Unknown Device<br/>New IP| DS["🔴 Device Spoofing<br/>No prior device"]
    Attack -->|Unusual Resources<br/>Extended Session| LM["🔴 Lateral Movement<br/>+60-180 min duration"]
    Attack -->|Subtle Failures<br/>4-8 Normal hours| LSB["🟡 Low-and-Slow<br/>Subtle gradient"]
    Attack -->|Single Unauthorized<br/>Resource| IT2["🟡 Insider Threat<br/>Resource access only"]
    Attack -->|Moderate Failures<br/>6-12| SCS["🟡 Slow Credential<br/>Prolonged attack"]
    
    style BF fill:#ffcdd2
    style IT fill:#ffcdd2
    style CS fill:#ffcdd2
    style DS fill:#ffcdd2
    style LM fill:#ffcdd2
    style LSB fill:#fff9c4
    style IT2 fill:#fff9c4
    style SCS fill:#fff9c4
```

## Key Statistics

| Component | Value |
|-----------|-------|
| **Data Size** | 45,000 events |
| **Unique Users** | 500 |
| **Unique Devices** | 700 |
| **Attack Percentage** | 2% (900 events) |
| **Features Engineered** | 23 |
| **Baseline Profiles** | 500 |
| **LSTM Epochs** | 15 |
| **LSTM Layers** | 2 LSTM + 2 Dense |
| **Sequence Window** | 5 events |
| **Ensemble Weight Split** | Baseline 40% / LSTM 60% |
| **Attack Types Detected** | 8 types |
| **Confidence Scale** | 0.0 - 1.0 |

## Implementation Files

### Core Detection
- [src/baseline_profiling.py](src/baseline_profiling.py) - Baseline statistical detector
- [src/lstm_sequence_model.py](src/lstm_sequence_model.py) - LSTM deep learning detector
- [src/inference.py](src/inference.py) - Ensemble weighted voting

### Data Processing
- [src/dataset_generator.py](src/dataset_generator.py) - Synthetic data generation
- [src/feature_engineering.py](src/feature_engineering.py) - 23-feature engineering pipeline

### Generation & Attacks
- [src/user_generator.py](src/user_generator.py) - 500 user profiles
- [src/device_generator.py](src/device_generator.py) - 700 device profiles
- [src/attack_generator.py](src/attack_generator.py) - 8 attack types
- [src/event_generator.py](src/event_generator.py) - 45,000 baseline events

### Output & Explanation
- [src/dashboard.py](src/dashboard.py) - Alert dashboard with ranking
- [src/explainability.py](src/explainability.py) - Anomaly explanations

### Models
- [trained_models/lstm_model.keras](trained_models/lstm_model.keras) - Trained LSTM model
- [trained_models/baseline_profile.pkl](trained_models/baseline_profile.pkl) - Baseline profiles
