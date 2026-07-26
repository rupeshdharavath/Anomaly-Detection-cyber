#!/usr/bin/env python3
"""
Test that feature extraction now produces correct 57-length vectors using lstm_feature_columns.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app', 'backend'))

from services.inference_service import InferenceService

print("=" * 70)
print("LSTM INFERENCE FIX VERIFICATION")
print("=" * 70)

# Initialize inference service
service = InferenceService()

print(f"\n✓ Service initialized")
print(f"  - LSTM model loaded: {service.lstm_model is not None}")
print(f"  - Baseline profiles loaded: {service.baseline_profiles is not None}")
print(f"  - Scaler loaded: {service.scaler is not None}")
print(f"  - Feature columns (baseline): {len(service.feature_columns) if service.feature_columns else 'Not loaded'}")
print(f"  - LSTM feature columns: {len(service.lstm_feature_columns) if service.lstm_feature_columns else 'Not loaded'}")

# Create a test event
test_event = {
    'entity_id': 'user_001',
    'session_duration': 3600,
    'failed_login_attempts': 2,
    'normal_login_start': 1000,
    'normal_failed_login_attempts': 500,
    'login_hour': 14,
    'risk_score': 0.3,
    'location_changed': 0,
    'device_changed': 0,
    'auth_changed': 0,
    'login_time_changed': 0,
    'long_session': 0,
    'high_failed_login': 0,
    'resource_changed': 0,
    'entity_type': 'user',
    'geo_location': 'Mumbai',
    'resource_accessed': 'Email',
    'auth_method': 'Password',
    'department': 'Engineering',
    'office': 'Mumbai',
    'device_type': 'Laptop',
    'operating_system': 'Windows 10',
    'browser': 'Chrome',
}

print(f"\n✓ Created test event for entity: {test_event['entity_id']}")

# Extract features
features = service._extract_features(test_event)

print(f"\n✓ Feature extraction result:")
if features is None:
    print(f"  ❌ FAILED - returned None")
    sys.exit(1)

print(f"  - Extracted length: {len(features)}")
print(f"  - Expected length: {len(service.lstm_feature_columns)}")

if len(features) == len(service.lstm_feature_columns) == 57:
    print(f"  ✅ Length matches LSTM expectations (57)")
else:
    print(f"  ❌ Length mismatch!")
    sys.exit(1)

# Try scoring with LSTM
lstm_score = service._score_lstm(test_event)
print(f"\n✓ LSTM scoring:")
print(f"  - Result: {lstm_score}")
if lstm_score is None:
    print(f"  ⚠️  LSTM returned None (model may not be loaded)")
else:
    print(f"  ✅ LSTM produced score: {lstm_score:.4f}")

print(f"\n" + "=" * 70)
print(f"✅ FIX VERIFIED: LSTM feature extraction now uses correct 57-column schema")
print(f"=" * 70)
