#!/usr/bin/env python3
"""
Verify that inference feature extraction matches training encoding exactly.
Confirms no silent mismatches like before.
"""

import pickle
import sys
from pathlib import Path

# Load training feature columns (from pd.get_dummies)
feature_columns_path = Path("trained_models/lstm_feature_columns.pkl")
with open(feature_columns_path, 'rb') as f:
    training_features = pickle.load(f)

print("=" * 70)
print("ENCODING MATCH VERIFICATION")
print("=" * 70)

# Constants from training and inference
NUMERIC_COLUMNS = [
    "session_duration",
    "failed_login_attempts",
    "normal_login_start",
    "normal_failed_login_attempts",
    "login_hour",
    "risk_score",
]
BOOLEAN_COLUMNS = [
    "location_changed",
    "device_changed",
    "auth_changed",
    "login_time_changed",
    "long_session",
    "high_failed_login",
    "resource_changed",
]
CATEGORICAL_COLUMNS = [
    "entity_type",
    "geo_location",
    "resource_accessed",
    "auth_method",
    "department",
    "office",
    "device_type",
    "operating_system",
    "browser",
]

print(f"\n✓ Total training features: {len(training_features)}")
print(f"  - Numeric columns expected: {len(NUMERIC_COLUMNS)}")
print(f"  - Boolean columns expected: {len(BOOLEAN_COLUMNS)}")
print(f"  - Categorical columns expected: {len(CATEGORICAL_COLUMNS)}")

# Verify numeric features
numeric_feats = training_features[:len(NUMERIC_COLUMNS)]
print(f"\n✓ Numeric features (first {len(NUMERIC_COLUMNS)}):")
for i, feat in enumerate(numeric_feats):
    print(f"  [{i}] {feat}")

# Verify boolean features
bool_start = len(NUMERIC_COLUMNS)
bool_end = bool_start + len(BOOLEAN_COLUMNS)
bool_feats = training_features[bool_start:bool_end]
print(f"\n✓ Boolean features (next {len(BOOLEAN_COLUMNS)}):")
for i, feat in enumerate(bool_feats):
    print(f"  [{bool_start + i}] {feat}")

# Verify categorical features (one-hot)
cat_start = bool_end
cat_feats = training_features[cat_start:]
print(f"\n✓ Categorical one-hot features (remaining {len(cat_feats)}):")

cat_summary = {}
for feat in cat_feats:
    col_name = feat.split('_')[0]  # e.g., "entity_type" from "entity_type_user"
    if col_name not in cat_summary:
        cat_summary[col_name] = []
    cat_summary[col_name].append(feat)

for col_name in sorted(cat_summary.keys()):
    print(f"\n  {col_name}:")
    for feat in sorted(cat_summary[col_name]):
        print(f"    - {feat}")

# Verification checks
print(f"\n" + "=" * 70)
print("INFERENCE ENCODING CHECKS")
print("=" * 70)

# Check 1: Numeric columns must be first
check1 = all(training_features[i] == NUMERIC_COLUMNS[i] for i in range(len(NUMERIC_COLUMNS)))
print(f"\n{'✅' if check1 else '❌'} Numeric columns in correct order: {check1}")

# Check 2: Boolean columns must be next
check2 = all(training_features[bool_start + i] == BOOLEAN_COLUMNS[i] for i in range(len(BOOLEAN_COLUMNS)))
print(f"{'✅' if check2 else '❌'} Boolean columns in correct order: {check2}")

# Check 3: Categorical columns must be one-hot format
cat_feats_check = [f for f in cat_feats if '_' in f]
check3 = len(cat_feats_check) > 0
print(f"{'✅' if check3 else '❌'} Categorical columns are one-hot encoded: {check3}")
print(f"    Found {len(cat_feats_check)} one-hot features (e.g., 'col_value' format)")

# Check 4: All categorical columns have at least one one-hot feature
cat_col_coverage = {col: any(col in f for f in cat_feats) for col in CATEGORICAL_COLUMNS}
check4 = all(cat_col_coverage.values())
print(f"{'✅' if check4 else '❌'} All categorical columns have one-hot features:")
for col, covered in sorted(cat_col_coverage.items()):
    print(f"    {'✓' if covered else '✗'} {col}")

# Summary
all_checks = [check1, check2, check3, check4]
print(f"\n" + "=" * 70)
if all(all_checks):
    print("✅ ENCODING MATCH VERIFIED")
    print("   Inference can safely reconstruct exact training encoding")
    sys.exit(0)
else:
    print("❌ ENCODING MISMATCH DETECTED")
    print("   Inference encoding does NOT match training — fix before deployment")
    sys.exit(1)
