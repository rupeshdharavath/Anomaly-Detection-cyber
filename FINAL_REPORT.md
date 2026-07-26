# Final Report — Anomaly Detection System

**Status:** Working prototype. All statements below were verified against the actual
codebase; no metric is reported unless it was either read directly from code or
computed by `src/evaluate_models.py`. Where a number has not yet been computed, this
report says so explicitly rather than estimating it.

---

## 1. Problem Statement

Detect anomalous access behavior across users, service accounts, and devices from
synthetic access logs, classify the type of anomaly, and surface it to a SOC analyst
with an explainable, ranked risk score — addressing the brief's five named
challenges: sequential/behavioral data, extreme class imbalance, concept drift,
explainability, and cold-start entities.

---

## 2. Approach — what the code actually implements

| Stage | File | What it does |
|---|---|---|
| Data generation | `src/dataset_generator.py`, `src/user_generator.py`, `src/device_generator.py`, `src/profile_generator.py`, `src/event_generator.py` | Generates 500 synthetic users, 700 devices, and normal access events over a simulated window |
| Attack injection | `src/attack_generator.py` | Injects 8 labeled attack patterns at a controlled rate (~2% of events) |
| Feature engineering | `src/feature_engineering.py` | Builds the 23-feature matrix (6 numeric, 7 boolean, ~38 one-hot categorical after expansion) used by both models |
| Baseline profiler | `src/baseline_profiling.py` | Builds a per-entity statistical profile (mode resource/location/auth method, mean/std session duration) |
| Sequence model | `src/lstm_sequence_model.py` | Builds sliding 5-event windows per entity and trains a stacked LSTM |
| Ensemble & inference | `app/backend/services/inference_service.py` | Combines baseline + LSTM scores into a final decision, served live by the FastAPI backend |
| Explainability | `src/explainability.py`, `_score_baseline()` in `inference_service.py` | Produces human-readable reasons per alert. **No SHAP or other external attribution library is used anywhere in this codebase.** |
| Concept drift | `src/drift_detector.py`, `app/backend/services/drift_monitor.py` | Periodically measures feature-distribution drift and triggers retraining when a threshold is crossed |
| Cold start | `app/backend/services/cold_start_service.py` | Buffers events for unrecognized entities and builds a real baseline profile once enough history accumulates |
| Evaluation | `src/evaluate_models.py` | Runs the real `InferenceService` against a held-out, time-based 20% slice of the dataset to compute genuine metrics (see §4) |

### 2.1 Baseline model — detection logic

The baseline compares each incoming event against the entity's stored profile with
additive point penalties (from `_score_baseline()` in `inference_service.py`):

| Deviation | Points |
|---|---|
| Resource not in entity's normal set | +2.0 |
| Location differs from normal | +1.5 |
| Auth method not normally used | +1.0 |
| Session duration > 2.5× tolerance from mean | +1.5 |
| Session duration > 1.5× tolerance | smaller partial penalty |
| Unknown entity (cold start) | flat score of 2.0 |

An event is flagged if the summed score exceeds `settings.ANOMALY_THRESHOLD` (0.5,
normalized against a max baseline score of ~4.0).

### 2.2 Sequence model — architecture

```
Input: sequences of 5 events × 57 engineered features
  ↓
Masking Layer (for zero-padded cold-start sequences)
  ↓
LSTM(128, return_sequences=True) + Dropout(0.4)
  ↓
LSTM(64, return_sequences=False) + Dropout(0.3)
  ↓
Dense(64, relu) + Dropout(0.3)
  ↓
Dense(32, relu) + Dropout(0.2)
  ↓
Dense(1, sigmoid) → anomaly confidence [0,1]
```

Trained with class-weighted binary crossentropy (`compute_class_weight("balanced")`)
to address the extreme class-imbalance challenge. Verified as a real, trained
artifact at `trained_models/lstm_model.keras` (confirmed via direct inspection of the
Keras model config — genuine `LSTM` layers, not a stub). **As trained, however, it
is not currently learning a useful signal** — see §4.

### 2.3 Ensemble — decision logic

```python
baseline_flag = baseline_score > baseline_threshold
lstm_flag = lstm_confidence > lstm_threshold
is_anomaly = baseline_flag OR lstm_flag          # either model can trigger an alert

ensemble_score = 0.4 × baseline_normalized + 0.6 × lstm_normalized
```

(Weights from `app/backend/config.py`: `BASELINE_WEIGHT: 0.4`, `LSTM_WEIGHT: 0.6`.)
The OR-based flagging is a deliberate recall-first design — missing a real intrusion
is treated as worse than one extra alert for an analyst to dismiss. If the LSTM is
unavailable (e.g. TensorFlow not installed), the system falls back to baseline-only
scoring automatically.

Each result reports `flagged_by` (`baseline`, `lstm`, or `both`) so the analyst can
see which mechanism triggered the alert, alongside the `reasons` list. **Note:**
given the LSTM's current performance (§4), the OR-based flagging currently *hurts*
precision at the alert budget rather than helping — see §4 for the numbers and §7
for the implication.

---

## 3. Deliverables status

| # | Deliverable | Status |
|---|---|---|
| 1 | Synthetic data generator + attack taxonomy | ✅ Implemented — 500 users, 700 devices, synthetic events with 8 injected attack types |
| 2 | Baseline profiling model | ✅ Implemented — per-entity statistical profile |
| 3 | Sequence-aware detection model | ⚠️ Implemented and trained, but not currently learning a useful signal (AUC 0.500 — see §4) |
| 4 | Anomaly-type classification | ✅ Implemented — label encoders + classifier in `trained_models/` |
| 5 | Explainability layer | ✅ Implemented — rule-based deviation reasons + `flagged_by` attribution (not SHAP) |
| 6 | Analyst-facing dashboard | ✅ Implemented — ranked alert queue, risk score, entity history view, model comparison page |
| 7 | Report | This document |

---

## 4. Evaluation

Real metrics have been computed by `python -m src.evaluate_models` and are stored in
`trained_models/evaluation_results.json`, which remains the single source of truth
and can be regenerated at any time. This script:

- Loads the real, trained `InferenceService` (the same code path the live API uses)
- Takes a **time-based held-out 20%** slice of `data/raw/cybersecurity_dataset.csv`
  (45,000 events, 900 attacks / 2% attack rate overall)
- Scores every held-out event through the actual baseline, LSTM, and ensemble logic
- Computes precision, recall, F1, and AUC-ROC for each of the three scorers
- Computes the specific metric the hackathon brief names explicitly: **false positive
  rate at a top-1% analyst alert budget**

### 4.1 Results (from the latest `evaluation_results.json`)

| Model | Precision | Recall | F1 | AUC-ROC |
|---|---|---|---|---|
| Baseline | 1.000 | 0.530 | 0.693 | 0.835 |
| LSTM | 0.034 | 0.006 | 0.010 | 0.500 |
| Ensemble | 0.814 | 0.530 | 0.642 | 0.833 |

**Top-1% analyst alert budget (90 alerts):**

| Model | True positives | False positives | FPR at budget |
|---|---|---|---|
| Baseline | 90 | 0 | 0.0% |
| LSTM | 3 | 87 | 96.7% |
| Ensemble | 68 | 22 | 24.4% |

### 4.2 What these numbers mean

The baseline profiler is doing essentially all of the real detection work. The
LSTM's AUC of 0.500 means it is not separating attacks from normal behavior any
better than chance on this dataset — its high recall on paper is not present here
because it was never a strong classifier to begin with. Because the ensemble uses
OR-based flagging (§2.3), the LSTM's false positives leak into the ensemble's alert
budget: the ensemble's FPR (24.4%) is *worse* than the baseline alone (0.0%), even
though the ensemble's recall matches the baseline's (0.530) since the baseline
already catches everything the baseline catches. In its current trained state, the
LSTM is not adding detection value and is actively costing precision at the alert
budget.

This is reported here rather than smoothed over, per this report's stated
verification standard. See §7 for the implication and possible next steps.

### Known-accurate structural facts (not dependent on future evaluation runs)
- Total dataset: 45,000 events, 900 labeled attacks (2.0% attack rate)
- Feature matrix: 23 raw engineered columns → 57 columns after one-hot expansion for
  LSTM input
- Train/test approach: time-based split (not random), to avoid leakage from future
  events into training

---

## 5. How the five named challenges are addressed

| Challenge | Status | Detail |
|---|---|---|
| Sequential/behavioral data | ✅ Addressed | LSTM sliding 5-event window per entity (architecture correct; current training result is weak — see §4) |
| Extreme class imbalance | ✅ Addressed | `compute_class_weight("balanced")` at LSTM training time |
| Explainability | ✅ Addressed | Rule-based deviation reasons + `flagged_by`, surfaced per alert in the dashboard |
| Cold-start | ✅ Addressed | Unknown entities get a flat fallback baseline score (2.0) rather than crashing or silently passing, and `ColdStartService` builds a real profile once enough events accumulate |
| Concept drift | ⚠️ Partially addressed | A background `DriftMonitor` computes feature-distribution drift on a handful of features and triggers retraining (attack-type classifier + baseline profiles) when a threshold is crossed. This is a basic, unvalidated mechanism — it has not been tested against real drift scenarios and does not cover drift in the LSTM's input distribution. It is a real, working starting point, not a mature production drift-detection system. |

---

## 6. Attack taxonomy — coverage vs. brief

The brief names 8 patterns: Normal baseline, Brute force, Impossible travel,
Credential stuffing, Lateral movement, Device spoofing, Low-and-slow exfiltration,
Insider drift. This codebase implements all 8, but two are simplified:

- **Low-and-slow exfiltration** → implemented as `Low and Slow Brute Force` /
  `Slow Credential Stuffing`: single-event stealthy variants, not literal
  multi-day/multi-session gradual campaigns.
- **Insider drift** → implemented as `Insider Threat`: a single unusual
  resource-access event, not a gradually-expanding-privilege pattern across
  multiple sessions.

Full mapping and rationale in `ATTACK_TAXONOMY_MAPPING.md`.

---

## 7. Known limitations

- **The LSTM is not currently learning a useful signal** (AUC 0.500, §4). The
  ensemble's alert-budget precision is worse than the baseline alone as a direct
  result. Possible next steps: more training epochs, revisiting the feature set fed
  to the LSTM, a longer or shorter sequence window, or gating the LSTM's
  contribution to the ensemble by a minimum confidence/validation AUC before it's
  allowed to independently trigger an alert.
- **Concept-drift handling is basic, not production-grade.** The `DriftMonitor`
  (§5) is real and functional but has not been validated against realistic drift
  scenarios and doesn't cover LSTM input drift specifically.
- **Attack taxonomy is a simplified proxy** for 2 of 8 patterns (§6).
- **File-based, batch/on-demand system** — not a real-time streaming service. No
  Kafka/queue ingestion or incremental feature store is implemented; this would be
  required for a production deployment at real-time SOC scale.
- **Cold-start fallback is a flat score** until the `ColdStartService` accumulates
  enough events for a real profile, not a personalized cold-start model from the
  first event.
- Synthetic data stands in for real access logs; results describe the model's
  ability to separate injected attack patterns from simulated normal behavior, not
  validated traffic from a production environment.

---

## 8. How to reproduce

```bash
# 1. Generate the dataset
python -m src.dataset_generator

# 2. Build the baseline profile
python -m src.baseline_profiling

# 3. Train the LSTM (requires TensorFlow)
pip install tensorflow>=2.14.0
python -m src.lstm_sequence_model

# 4. Generate real evaluation metrics
python -m src.evaluate_models

# 5. Run the backend and frontend (see README.md)
```

---

## 9. Conclusion

The system implements a working baseline-profiling + LSTM ensemble with real,
verified model artifacts and a functioning explainability and dashboard layer,
addressing all five challenges named in the brief to varying degrees of maturity:
sequential modeling, class imbalance handling, explainability, and cold-start are
solidly addressed; concept-drift detection exists and functions but is basic; and
the LSTM sequence model, while architecturally correct and genuinely trained, is
not currently contributing useful detection signal (§4).

The two areas most worth further work before a production claim would be:
(1) improving LSTM training so it contributes positively to the ensemble rather
than adding noise, and (2) hardening concept-drift detection with validation
against realistic drift scenarios. Both are called out explicitly rather than
glossed over, consistent with this report's verification standard.