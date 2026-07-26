# Anomaly Detection — SOC Behavioral Anomaly Detection System

AI-powered behavioral anomaly detection for cybersecurity access logs, built for the
"AI-Powered Behavioral Anomaly Detection for Cybersecurity" hackathon brief. The system
learns per-entity "normal" access behavior and flags deviations using a **Baseline
profiling model + LSTM sequence model ensemble**, with an explainable, ranked
analyst-facing dashboard.

---

## What this is

- **Synthetic data generator** producing realistic access-log events for users, service
  accounts, and edge devices, with 8 injected attack patterns.
- **Baseline profiling model** — a per-entity statistical "normal" behavior reference
  (mode resource, mode location, mean/std session duration).
- **LSTM sequence model** — a real, trained stacked LSTM (128→64 units) over sliding
  5-event windows per entity, to catch anomalies defined by *pattern over time* rather
  than any single event.
- **Ensemble scoring** — baseline and LSTM scores are combined; either model flagging
  independently is enough to raise an alert (OR-based), while a weighted blend ranks
  severity for the analyst queue.
- **Explainability** — every alert carries human-readable reasons (e.g. "Impossible
  travel detected", "Unauthorized resource access", "Extreme session duration
  anomaly") and reports which model(s) flagged it (`baseline`, `lstm`, or `both`).
- **FastAPI backend + React/Tailwind frontend** — a SOC-style dashboard with an alert
  queue, entity history view, live simulation, and model comparison page.

---

## Tech stack

| Layer | Tech |
|---|---|
| Backend | FastAPI, Pydantic, scikit-learn, TensorFlow/Keras, pandas |
| Frontend | React, React Router, Tailwind CSS, lucide-react icons, Axios |
| Data | CSV files (no database) — `data/raw/`, `data/processed/` |
| Models | `trained_models/*.pkl` (baseline, scaler, encoders) + `lstm_model.keras` |

No database is used — all data and model artifacts are file-based, and alerts are
generated/stored in memory for demo purposes.

---

## Project structure

```
├── src/                        # Data generation + model training pipeline
│   ├── user_generator.py       # Synthetic users
│   ├── device_generator.py     # Synthetic devices
│   ├── profile_generator.py    # Per-entity "normal" profiles
│   ├── event_generator.py      # Normal access events
│   ├── attack_generator.py     # Injects 8 attack patterns into events
│   ├── dataset_generator.py    # Orchestrates generation, computes risk_score
│   ├── feature_engineering.py  # Feature prep for baseline/LSTM
│   ├── baseline_profiling.py   # Per-entity statistical baseline model
│   ├── lstm_sequence_model.py  # LSTM training (sliding-window sequences)
│   ├── explainability.py       # Per-alert reason generation
│   ├── inference.py            # Offline scoring utilities
│   └── dashboard.py            # CLI alert-queue printer
│
├── notebooks/                  # EDA, data generation, feature engineering, LSTM training
│
├── data/
│   ├── raw/                    # Generated CSVs (users, devices, events, attacks)
│   └── processed/              # Feature-engineered dataset
│
├── trained_models/             # Saved model artifacts (see below)
│
├── app/
│   ├── backend/                 # FastAPI application
│   │   ├── main.py              # App entry, router registration
│   │   ├── config.py            # Paths, thresholds, ensemble weights
│   │   ├── routers/             # anomalies, alerts, analytics, entities, health, models
│   │   └── services/            # inference_service, alert_service, data_service
│   └── frontend/                # React + Tailwind SPA
│       └── src/
│           ├── pages/            # Dashboard, Alerts, Simulate, Models, EntityHistory
│           ├── components/       # AlertCard, AlertDetail, StatCard, RiskBadge, AnomalyTable
│           ├── layout/            # Sidebar
│           ├── api/                # client.js (Axios API wrappers)
│           └── store/               # Zustand store
│
├── reports/                    # Project report, presentation slides, environment notes
├── ARCHITECTURE.md             # System architecture diagram (Mermaid)
├── FINAL_REPORT.md             # Detailed technical report
├── ATTACK_TAXONOMY_MAPPING.md  # Spec vs. implementation mapping for attack types
└── app/HACKATHON_REQUIREMENTS.md  # Requirements → implementation mapping
```

---

## Attack taxonomy

Injected at a controlled rate (~2% of events) via `src/attack_generator.py`:

| Attack type | Signal |
|---|---|
| Brute Force | Rapid failed logins in an off-hours window |
| Impossible Travel | Same entity, geographically distant location + new IP |
| Credential Stuffing | High failed attempts, new source IP, off-hours |
| Device Spoofing | Device fingerprint mismatch + new IP |
| Lateral Movement | Access to resources outside the entity's normal set, unusual command sequence |
| Low and Slow Brute Force | Moderate failed attempts within normal hours (stealthy) |
| Insider Threat | Single unusual resource access, otherwise normal signals (edge case) |
| Slow Credential Stuffing | Moderate failed attempts, no location/device change (stealthy) |

> The hackathon brief describes "Low-and-slow exfiltration" and "Insider drift" as
> multi-day/multi-session gradual patterns. This implementation uses single-event
> stealthy variants instead — see `ATTACK_TAXONOMY_MAPPING.md` for the full rationale
> and what a true multi-session version would require.

---

## Getting started

### Prerequisites
- Python 3.10+ (3.12 recommended for TensorFlow compatibility)
- Node.js 16+
- npm

### 1. Generate the dataset (optional — pre-generated CSVs are already in `data/raw/`)

```bash
python -m src.dataset_generator
```

### 2. Train models (optional — pre-trained artifacts are already in `trained_models/`)

```bash
python -m src.baseline_profiling      # → trained_models/baseline_profile.pkl
pip install tensorflow>=2.14.0
python -m src.lstm_sequence_model     # → trained_models/lstm_model.keras
```

### 3. Run the backend

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
pip install -r app/backend/requirements.txt

cd app/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API docs: http://localhost:8000/docs

### 4. Run the frontend

```bash
cd app/frontend
npm install
npm start
```

Dashboard: http://localhost:3000

---

## Trained model artifacts (`trained_models/`)

| File | Used by |
|---|---|
| `lstm_model.keras` | LSTM sequence model (128→64 stacked LSTM, sigmoid output) |
| `lstm_feature_columns.pkl` | 57 one-hot-expanded column names for LSTM input reconstruction |
| `lstm_threshold.pkl` | Calibrated decision threshold for LSTM confidence |
| `baseline_profile.pkl` | Per-entity statistical "normal" profiles |
| `feature_columns.pkl` | Raw column names used by the baseline scorer (distinct from the LSTM's list above — do not conflate the two) |
| `scaler.pkl` | `StandardScaler` fit on the 6 numeric LSTM input features |
| `label_encoder.pkl`, `attack_type_label_encoder.pkl`, `target_label_encoder.pkl` | Reserved encoders |

---

## API overview

All routes are prefixed `/api/v1` unless noted.

| Router | Endpoints |
|---|---|
| Health | `GET /health`, `/health/ready`, `/health/live` |
| Anomalies | `POST /anomalies/detect`, `POST /anomalies/detect/batch`, `GET /anomalies/list`, `GET /anomalies/{id}`, `GET /anomalies/statistics` |
| Alerts | `GET /alerts/`, `GET /alerts/active`, `GET /alerts/{id}`, `GET /alerts/statistics` |
| Analytics | `GET /analytics/overview`, `/risk-distribution`, `/time-series`, `/top-resources`, `/top-locations`, `/model-performance`, `/entity-risk-summary` |
| Entities | `GET /entities/users`, `/entities/devices`, `/entities/users/{id}`, `/entities/devices/{id}`, `/entities/search` |
| Models | `GET /models/info`, `/models/status`, `/models/performance` |

---

## Explainability — how it actually works

Each alert's `reasons` list is generated by `_score_baseline()` in
`app/backend/services/inference_service.py`, comparing the incoming event against the
entity's stored baseline profile. Examples of the generated reasons:

- `"Unauthorized resource access (Insider threat indicator)"`
- `"Impossible travel detected (Location change)"`
- `"Unusual authentication method"`
- `"Extreme session duration anomaly (Expected ~{mean}s, got {actual}s)"`

Each alert also reports `flagged_by` (`baseline`, `lstm`, or `both`), telling the
analyst which detection mechanism triggered it. This is a deviation-based /
rule-attribution approach, not SHAP — there is no `shap` dependency or usage anywhere
in this codebase.

---

## Known limitations

- **`/models/performance` currently returns fixed example values**, not metrics
  computed from a live evaluation run against the trained models. The frontend's
  Model Comparison page correctly labels this (`⚠ Example metrics` vs `✓ Metrics from
  held-out test set`), but the backend endpoint itself has not yet been wired to a
  real scoring pass. Treat every number sourced from this endpoint — including
  anything repeated in `FINAL_REPORT.md` or the presentation — as illustrative until
  this is implemented.
- **Cold-start entities** get a flat fallback baseline score rather than a
  personalized profile until they accumulate history.
- **TensorFlow availability**: if TensorFlow isn't installed in the runtime
  environment, the system falls back to baseline-only scoring automatically.
- **Attack taxonomy is a simplified mapping** for two of the eight patterns — see
  `ATTACK_TAXONOMY_MAPPING.md`.
- Synthetic data stands in for real access logs; results describe the model's ability
  to separate injected attack patterns from simulated normal behavior, not validated
  traffic from a production environment.

---

## Documentation map

| File | Purpose |
|---|---|
| `README.md` (this file) | Entry point — what the project is, how to run it |
| `app/README.md` | Backend/frontend run instructions (subset of this file) |
| `app/HACKATHON_REQUIREMENTS.md` | Maps each brief requirement to the implementing code |
| `FINAL_REPORT.md` | Full technical report — approach, assumptions, metrics, limitations |
| `ARCHITECTURE.md` | System architecture diagram (Mermaid) |
| `ATTACK_TAXONOMY_MAPPING.md` | Spec vs. implementation mapping for the 8 attack types |
| `reports/presentation.md` | Slide content for the required presentation deliverable |

---

## License

Hackathon submission — no license specified.
