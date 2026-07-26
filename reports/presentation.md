# AI-Powered Behavioral Anomaly Detection

## Slide 1: Title
- AI-Powered Behavioral Anomaly Detection for Cybersecurity
- Synthetic access-log generation, anomaly detection, and explainability

## Slide 2: Problem
- Access logs are sequential and highly imbalanced
- Need to detect anomalies in near real time
- Must explain why events were flagged

## Slide 3: Data Generation
- 500 synthetic users with realistic profiles (department, location, device)
- 700 edge devices with unique fingerprints
- 90-day access log simulation with 2% attack rate (spec range: 0.5%–3%)
- 45,000 events with realistic behavioral variance

## Slide 4: Attack Types Implemented
- **Loud attacks** (30%): Brute Force, Impossible Travel, Credential Stuffing, Device Spoofing, Lateral Movement
- **Stealthy attacks** (70%): Low-and-Slow Brute Force, Insider Threat, Slow Credential Stuffing
- 8 attack types total, each with a distinct single-event mutation signature

## Slide 5: Baseline Profiling
- Per-entity normal behavior baseline (mode resource, mode location, mean/std session duration)
- History-based statistics with cold-start handling (unknown entities get a flat fallback score)
- Used as the normality reference layer

## Slide 6: Detection Models
- **Baseline Profiler** (40% weight): Per-entity statistical profiling, fast rule-based anomaly scoring
- **LSTM Sequence Model** (60% weight): Stacked LSTM (128→64 units), sliding window of 5 events, 57 engineered input features
- **Ensemble**: Either model flagging independently raises an alert (OR-based); weighted blend ranks severity
- Real, trained artifacts on disk (`lstm_model.keras`, `baseline_profile.pkl`) — a working prototype, not yet hardened for production deployment (see Slide 12)

## Slide 7: Explainability
- Rule-based deviation attribution — not SHAP
- Each flagged event lists the specific triggering factors: unauthorized resource access, location change, unusual auth method, session duration drift
- Every alert also reports `flagged_by` (baseline / LSTM / both), so the analyst sees which detection mechanism caught it
- Analyst sees the reason for each alert, in plain language, without needing to interpret a raw score

## Slide 8: Alert Budget
- Evaluate the top 1% highest-risk events — the realistic volume a SOC analyst can review
- Measure true attack hit rate (precision) and false-positive rate within that budget
- Directly aligns with the brief's named evaluation criterion
- [Insert real numbers here once `python -m src.evaluate_models` has been run against the held-out test set]

## Slide 9: Concept Drift and Cold Start
- **Cold start**: new/unknown entities receive a flat fallback baseline score rather than being silently ignored or crashing the pipeline
- **Concept drift**: not yet implemented in the current system — legitimate behavior change over time is not automatically re-baselined
- Identified as a priority next step, not a solved problem, ahead of any production deployment

## Slide 10: Scalability
- Current implementation: batch/on-demand scoring over file-backed CSV data and a live-scoring FastAPI service
- Streaming-ready design direction: ingest → feature extraction → model scoring → alert queue
- Would require a message queue (e.g. Kafka) and an incremental feature store for true real-time production use — not yet built

## Slide 11: Results
- **Dataset**: 45,000 events, 2% attack injection rate (spec range: 0.5%–3%)
- **Evaluation**: real precision/recall/F1/AUC and top-1%-alert-budget false-positive rate are computed by `src/evaluate_models.py` against a held-out, time-based 20% test split, using the actual production `InferenceService`
- [Insert real numbers here once the script has been run — do not present placeholder/example figures as measured results]
- All 8 attack types implemented and detected by at least one of the two models

## Slide 12: Limitations & Future Enhancements
- **Current**: single-event stealthy attacks; true multi-day gradual patterns (low-and-slow exfiltration, insider drift) need correlation across multiple sessions, not yet implemented
- **Concept drift**: no automated re-baselining exists yet
- **Data**: synthetic, rule-based generation — real deployment data would benefit from domain-expert validation
- **Future work**: multi-session pattern detection, automated drift retraining, streaming ingestion, real held-out evaluation wired into the live dashboard
- **Production readiness**: this is a working prototype — moving to production would require a persistent alert store (Redis/PostgreSQL), authentication, and containerization, none of which are implemented yet