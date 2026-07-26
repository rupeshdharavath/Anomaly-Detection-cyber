from pathlib import Path
import json
import os
import pandas as pd
from src.evaluate_models import load_dataset, split_time_based, build_results

ROOT = Path(__file__).resolve().parents[0]
raw = load_dataset(ROOT / 'data' / 'raw' / 'cybersecurity_dataset.csv')
_, test_df = split_time_based(raw, 0.2)
results = build_results(test_df)
print('lstm_available', results['flags']['lstm_available'])
print('baseline auc', results['metrics']['baseline']['auc_roc'])
print('ensemble auc', results['metrics']['ensemble']['auc_roc'])
print('baseline alert', results['alert_budget_evaluation']['baseline'])
print('ensemble alert', results['alert_budget_evaluation']['ensemble'])
print('ensemble score example', results['ensemble_score'][:20] if 'ensemble_score' in results else 'none')
print('first 20 ensemble preds', [r.get('status') for r in results['ensemble_results'][:20]] if 'ensemble_results' in results else 'no ensemble_results')
