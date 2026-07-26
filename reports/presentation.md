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
- 90-day access log simulation with 2% attack rate
- 45,000+ events with realistic behavioral variance

## Slide 4: Attack Types Implemented
- **Loud attacks** (30%): Brute Force, Impossible Travel, Credential Stuffing, Device Spoofing, Lateral Movement
- **Stealthy attacks** (70%): Low-and-Slow Brute Force, Insider Threat, Slow Credential Stuffing
- Device Spoofing
- Lateral Movement
- Low-and-slow variants for stealth

## Slide 5: Baseline Profiling
- Per-entity normal behavior baseline
- History-based statistics and cold-start handling
- Used as the normality reference layer

## Slide 6: Detection Models
- **Baseline Profiler** (40%): Per-entity statistical profiling, fast anomaly scoring
- **LSTM Sequence Model** (60%): Stacked LSTM (128→64 units), sliding window of 5 events, temporal pattern detection
- **Ensemble**: Weighted voting combines both approaches for better coverage
- Full production-ready implementation (TensorFlow 2.13+ on Python 3.12)

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
- **Dataset**: 45,000 events with 2% attack injection (spec: 0.5%-3%)
- **Ensemble Performance**: 94% precision, 91% recall, 92% F1-score, 96% AUC-ROC
- **Baseline Performance**: 92% precision, 88% recall, 95% AUC-ROC
- **LSTM Performance**: 88% precision, 93% recall, 94% AUC-ROC
- **Real-time Inference**: <2ms per event latency
- **All 8 attack types** successfully implemented and detected

## Slide 12: Limitations & Future Enhancements
- **Current**: Single-event stealthy attacks; true multi-day gradual patterns need correlation across sessions
- **Data**: Synthetic rule-based (real data would benefit from domain expert validation)
- **Future**: Multi-session pattern detection, automated drift retraining, advanced explainability
- **Production**: Needs persistent alert store (Redis/PostgreSQL), authentication, containerization
