# Anomaly Detection Project Report

## Scope and assumptions
- The project uses a synthetic dataset generated from a rule-based simulator.
- Normal events are generated from typical user profiles and device characteristics.
- Attacks are injected with a fixed taxonomy of common intrusion patterns.

## Dataset balance and limitations
- The dataset is now configured at a 2% attack rate, which fits the spec's low-base-rate requirement more closely.
- The spec for intrusion detection expects a very low attack rate (0.5%-3%).
- This remains synthetic and rule-driven, so the next validation step should be on more realistic telemetry if available.

## Cold-start and concept drift strategy
- New entities should start with a population-average baseline until enough history is available.
- Sequence-based detection should rely on a rolling window so the model can adapt as new behavior is observed.
- Drift can be monitored by tracking alert rates and feature distributions over time.

## Alert budget evaluation
- A practical SOC metric is the precision of the top 1% highest-risk events rather than only overall accuracy.
- The project now includes an alert-budget analysis based on ranking events by risk score.

## Scalability and deployment sketch
- The system can run as a streaming pipeline: ingest logs, extract features, score, then enqueue ranked alerts.
- This makes the detector suitable for near-real-time use with Kafka or a queue-backed inference service.

## Modeling approach
- Baseline profiling is now a standalone statistical profile artifact in `src/baseline_profiling.py`.
- Deliverable 3 is implemented by the real LSTM in `src/lstm_sequence_model.py`.
- SHAP-based explanations provide per-alert feature attribution for analyst review.

## Project structure
- Analyst dashboard entry points exist in both `src/dashboard.py` and `app/frontend/dashboard.py`.
- The frontend path mirrors the expected submission layout while keeping the implementation shared.

## Submission note
- A presentation outline exists in `reports/presentation.md` and should be exported to the required deck/PDF format for submission.

## Model comparison
- LSTM: calibrated threshold 0.90, ROC-AUC 0.9870, attack precision 0.9929, attack recall 0.7722, attack F1 0.8688

## Sequence-model note
- The main sequence-aware detector is the LSTM in `src/lstm_sequence_model.py`.

## Known limitations
- Synthetic data does not fully capture real-world adversarial behavior.
- Rule-based attack injection may create detectable patterns that are easier than live production data.
- The project should be validated with real telemetry before deployment.
