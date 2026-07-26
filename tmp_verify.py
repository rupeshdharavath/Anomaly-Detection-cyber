from pathlib import Path
from src.evaluate_models import load_dataset, split_time_based, build_results, save_results
from src.drift_detector import feature_drift_scores, drift_triggered
import json

ROOT = Path('D:/Anomaly-Detection')
print('Running evaluation...')
df = load_dataset(ROOT / 'data' / 'raw' / 'cybersecurity_dataset.csv')
_, test_df = split_time_based(df, 0.2)
results = build_results(test_df)
save_results(results, ROOT / 'trained_models' / 'evaluation_results.json')
print('Saved evaluation to trained_models/evaluation_results.json')

# Drift check
split_at = int(len(test_df)*0.5)
early = test_df.iloc[:split_at].reset_index(drop=True)
late = test_df.iloc[split_at:].reset_index(drop=True)
features=['risk_score','session_duration','failed_login_attempts','location_changed','device_changed']
scores = feature_drift_scores(early, late, features)
print('Drift scores:')
print(scores.to_string(index=False))
print('Drift triggered?', drift_triggered(early, late, features, threshold=0.05))

# Print some evaluation metrics
print('\nEvaluation flags:', results.get('flags'))
print('Baseline AUC:', results['metrics']['baseline'].get('auc_roc'))
print('Ensemble AUC:', results['metrics']['ensemble'].get('auc_roc'))
print('Baseline alert:', results['alert_budget_evaluation']['baseline'])
print('Ensemble alert:', results['alert_budget_evaluation']['ensemble'])

# Save summary
with open(ROOT / 'trained_models' / 'verification_summary.json', 'w', encoding='utf-8') as f:
    json.dump({'drift_scores': scores.to_dict(orient='records'), 'drift_triggered': drift_triggered(early, late, features, threshold=0.05), 'evaluation_flags': results.get('flags')}, f, indent=2)
print('Saved verification summary to trained_models/verification_summary.json')
