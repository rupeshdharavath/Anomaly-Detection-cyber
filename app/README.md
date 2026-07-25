# Anomaly Detection - SOC Dashboard

This workspace contains a FastAPI backend and a React + Tailwind frontend for a cybersecurity anomaly detection system (LSTM + Baseline ensemble). The system uses CSV/model artifacts (no database required) stored under `data/` and `trained_models/`.

## Project layout (important files)

- `app/backend/` - FastAPI application
  - `main.py` - FastAPI app entry
  - `routers/` - API endpoints (anomalies, alerts, analytics, entities, models, health)
  - `services/` - inference, alert, data services
  - `config.py` - application configuration and paths
  - `requirements.txt` - Python dependencies

- `app/frontend/` - React + Tailwind single-page application
  - `src/` - React source (components, pages, store)
  - `public/` - `index.html`
  - `package.json` - JS dependencies

- `data/raw/` - CSV artifacts (users.csv, devices.csv, user_profiles.csv, cybersecurity_dataset.csv)
- `data/processed/` - processed dataset (processed_logs.csv)
- `trained_models/` - model artifacts (lstm_model.keras, baseline_profile.pkl, scaler.pkl, feature_columns.pkl)

## How it works

- Backend loads CSVs and model artifacts at startup via `DataService` and `InferenceService`.
- `InferenceService` applies baseline scoring and optionally LSTM scoring (if TensorFlow installed).
- `AlertService` generates alerts from anomalies and stores them in-memory (no DB required).
- Frontend queries the backend APIs to display alerts, anomalies, analytics, and entity details.

## Run backend (development)

1. Create a Python virtual environment and activate it.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies

```powershell
pip install -r app/backend/requirements.txt
```

3. Start the FastAPI server

```powershell
cd app/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Open API docs at: http://localhost:8000/docs

## Run frontend (development)

1. Install Node.js (16+ recommended)
2. Install npm packages

```bash
cd app/frontend
npm install
```

3. Start the development server

```bash
npm start
```

Open the frontend at http://localhost:3000 (default CRA port).

## Notes & Hackathon constraints

- No database: all data is read from CSVs in `data/raw/` and model artifacts in `trained_models/`.
- The system uses in-memory alert storage (`AlertService`) for demo/hackathon purposes.
- If TensorFlow is not available, the system gracefully falls back to baseline-only detection.
- To update models or CSV artifacts, replace files in `trained_models/` and `data/raw/` and restart the backend.

## Next steps & tests

- Add CI to run linting and unit tests.
- Add optional Redis for caching and persistent alert store for production.
- Add authentication for the dashboard.

