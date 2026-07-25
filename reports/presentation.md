# AI-Powered Behavioral Anomaly Detection

## Slide 1: Title
- AI-Powered Behavioral Anomaly Detection for Cybersecurity
- Synthetic access-log generation, anomaly detection, and explainability

## Slide 2: Problem
- Access logs are sequential and highly imbalanced
- Need to detect anomalies in near real time
- Must explain why events were flagged

## Slide 3: Data Generation
- Synthetic users, devices, and profiles
- Normal access events generated per entity
- Attack taxonomy injected at controlled rate

## Slide 4: Attack Types
- Brute Force
- Impossible Travel
- Credential Stuffing
- Device Spoofing
- Lateral Movement
- Low-and-slow variants for stealth

## Slide 5: Baseline Profiling
- Per-entity normal behavior baseline
- History-based statistics and cold-start handling
- Used as the normality reference layer

## Slide 6: Detection Models
- Tabular XGBoost baseline
- Sequence-aware temporal detector using rolling history features
- Note: deep LSTM/GRU/Transformer implementation requires a supported TensorFlow/PyTorch runtime

## Slide 7: Explainability
- SHAP-based feature attribution
- Example factors: risk score, resource change, failed logins, unusual hours
- Analyst sees the reason for each alert

## Slide 8: Alert Budget
- Evaluate top 1% highest-risk events
- Measure true attack hit rate in that alert budget
- Aligns with SOC operational constraints

## Slide 9: Concept Drift and Cold Start
- New entities begin with population baselines
- Existing entities update using rolling windows
- Drift monitored by alert rate and feature distribution changes

## Slide 10: Scalability
- Batch scoring for historical data
- Streaming-ready design: ingest -> feature extraction -> model scoring -> alert queue
- Suitable for Kafka or queue-based deployment later

## Slide 11: Results
- Dataset regenerated with 2% attack rate
- Sequence-aware detector trained successfully
- SHAP and analyst queue modules verified

## Slide 12: Limitations
- Synthetic data is easier than real telemetry
- Rule-based attacks may be more separable than live attacks
- Deep sequence model still needs a supported ML runtime
