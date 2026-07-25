# Hackathon Requirements Mapping

This file maps the hackathon specification requirements to the implemented components in this repository.

## Requirements -> Implementation

- FastAPI backend architecture and folder structure
  - Implemented: `app/backend/` with `main.py`, `routers/`, `services/`, `config.py`, `models.py`

- React + Tailwind frontend (single-page SOC dashboard)
  - Implemented: `app/frontend/` with React components, Tailwind config, pages, and store

- All API endpoints
  - Implemented routers: `anomalies`, `alerts`, `analytics`, `entities`, `models`, `health`
  - Entry: `GET /`, `GET /health`, `POST /api/v1/anomalies/detect`, `POST /api/v1/anomalies/detect/batch`, `GET /api/v1/anomalies/list`, etc.

- Integration with existing CSV/model artifacts
  - `app/backend/config.py` points to `data/raw/` and `trained_models/` files
  - `DataService` loads `users.csv`, `devices.csv`, `user_profiles.csv`, `cybersecurity_dataset.csv`
  - `InferenceService` loads `lstm_model.keras`, `baseline_profile.pkl`, `scaler.pkl`, `feature_columns.pkl`

- LSTM + Baseline inference pipeline
  - Implemented in `app/backend/services/inference_service.py`
  - Baseline scoring uses weighted rules; LSTM scoring invoked when TensorFlow is available
  - Ensemble weighted voting (Baseline 40% / LSTM 60%) with thresholds and confidence scoring

- Risk scoring, confidence scoring, explainability, alert generation
  - Risk & confidence: returned by `InferenceService.predict()`
  - Explainability: reasons list in anomaly response
  - Alerts: `AlertService` generates in-memory alerts

- Dashboard widgets, charts, tables, UI layout
  - Implemented in `app/frontend/src/pages/*` and `app/frontend/src/components/*`
  - Charts use `recharts` and components use Tailwind theme

- Project structure and coding standards
  - Modular layout with `routers`, `services`, `models` and React `components`, `pages`, `store`
  - Pydantic models for typed request/response schemas

- Component hierarchy
  - Backend: main -> routers -> services -> data/models
  - Frontend: App -> Sidebar -> Pages -> Components -> Store

- Backend service flow
  - DataService loads CSVs -> InferenceService loads models -> Routers call services -> AlertService stores alerts

- Frontend state management
  - Implemented using `zustand` in `app/frontend/src/store/store.js`

- Error handling
  - Global exception handler in FastAPI app
  - Try/catch and HTTPException usage in routers and services
  - Frontend shows minimal error state in store

- Responsive UI
  - Tailwind responsive grid layouts in pages
  - Sidebar collapses on mobile

- Hackathon-focused UX
  - Fast setup (no DB), clear onboarding in `app/README.md`, and exports available from UI
  - In-memory alerts for quick demo

- End-to-end data flow
  - Data generation (offline) -> CSVs in `data/raw/` -> backend loads CSVs and models -> frontend queries APIs -> display

- Avoid using a database
  - All data is loaded from CSVs; alerts are in-memory. To persist, replace `AlertService` with a DB-backed implementation.

- Professional UI theme suitable for a cybersecurity SOC
  - Tailwind theme with `soc-dark`, `soc-accent`, etc. for clean SOC look

- Clean, modular, production-quality code requirements
  - Services are separated, Pydantic models used, configuration centralized in `config.py`.

## Gaps & Next Improvements (optional)

- Authentication/Authorization for API and dashboard
- Persistent alert store (Redis/Postgres)
- More complete feature extraction pipeline used for LSTM inference
- Unit and integration tests (CI)
- Dockerfiles and deployment manifests

