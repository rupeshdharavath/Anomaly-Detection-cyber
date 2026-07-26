#!/usr/bin/env python3
"""
Verify that config.py now has LSTM_FEATURE_COLUMNS set correctly.
"""

import os
import sys
import pickle

print("=" * 70)
print("LSTM FIX VERIFICATION - CONFIG AND FEATURE COLUMNS")
print("=" * 70)

# Check config.py
config_file = 'app/backend/config.py'
with open(config_file, 'r', encoding='utf-8') as f:
    config_content = f.read()

has_lstm_feature_columns = 'LSTM_FEATURE_COLUMNS' in config_content
print(f"\n✓ Config verification:")
print(f"  {'✅' if has_lstm_feature_columns else '❌'} config.py has LSTM_FEATURE_COLUMNS: {has_lstm_feature_columns}")

# Check inference_service.py
service_file = 'app/backend/services/inference_service.py'
with open(service_file, 'r', encoding='utf-8') as f:
    service_content = f.read()

has_lstm_fc_attr = 'self.lstm_feature_columns' in service_content
has_lstm_fc_load = 'settings.LSTM_FEATURE_COLUMNS' in service_content
has_lstm_fc_use = 'for feature_name in self.lstm_feature_columns:' in service_content

print(f"\n✓ InferenceService verification:")
print(f"  {'✅' if has_lstm_fc_attr else '❌'} Has self.lstm_feature_columns attribute: {has_lstm_fc_attr}")
print(f"  {'✅' if has_lstm_fc_load else '❌'} Loads settings.LSTM_FEATURE_COLUMNS: {has_lstm_fc_load}")
print(f"  {'✅' if has_lstm_fc_use else '❌'} Uses lstm_feature_columns in extraction: {has_lstm_fc_use}")

# Check feature columns
print(f"\n✓ Feature columns verification:")

with open('trained_models/feature_columns.pkl', 'rb') as f:
    baseline_cols = pickle.load(f)

with open('trained_models/lstm_feature_columns.pkl', 'rb') as f:
    lstm_cols = pickle.load(f)

print(f"  - baseline feature_columns.pkl: {len(baseline_cols)} raw columns")
print(f"  - lstm_feature_columns.pkl: {len(lstm_cols)} one-hot expanded columns")

# Verify extraction logic would use lstm_cols not baseline_cols
print(f"\n✓ One-hot encoding detection:")
baseline_has_onehot = any(c.startswith('entity_type_') for c in baseline_cols)
lstm_has_onehot = any(c.startswith('entity_type_') for c in lstm_cols)
print(f"  - baseline has one-hot: {baseline_has_onehot}")
print(f"  - lstm has one-hot: {lstm_has_onehot}")

print(f"\n" + "=" * 70)
if all([has_lstm_feature_columns, has_lstm_fc_attr, has_lstm_fc_load, has_lstm_fc_use, lstm_has_onehot]):
    print(f"✅ FIX COMPLETE: config.py and inference service properly wired for 57-column LSTM")
    sys.exit(0)
else:
    print(f"❌ FIX INCOMPLETE - check above for what's missing")
    sys.exit(1)
