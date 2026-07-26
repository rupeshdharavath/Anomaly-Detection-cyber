import pickle

# Check what FEATURE_COLUMNS actually contains
with open('trained_models/feature_columns.pkl', 'rb') as f:
    baseline_cols = pickle.load(f)
    
with open('trained_models/lstm_feature_columns.pkl', 'rb') as f:
    lstm_cols = pickle.load(f)

print(f'baseline feature_columns.pkl: {len(baseline_cols)} columns')
print(f'  All: {baseline_cols}')
print()
print(f'lstm_feature_columns.pkl: {len(lstm_cols)} columns') 
print(f'  First 20: {lstm_cols[:20]}')
print()
print('One-hot format check:')
has_onehot_baseline = any(c.startswith('entity_type_') for c in baseline_cols)
has_onehot_lstm = any(c.startswith('entity_type_') for c in lstm_cols)
print(f'  baseline has one-hot: {has_onehot_baseline}')
print(f'  lstm has one-hot: {has_onehot_lstm}')
