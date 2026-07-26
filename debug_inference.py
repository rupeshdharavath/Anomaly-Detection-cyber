import sys
from pathlib import Path
import json
from datetime import datetime

repo_root = Path(__file__).resolve().parent
sys.path.insert(0, str(repo_root))

# Test the inference service
from app.backend.services.inference_service import InferenceService

service = InferenceService()

print(f"Models loaded: {service.models_loaded}")
print(f"Baseline profiles: {len(service.baseline_profiles) if service.baseline_profiles else 0}")
print(f"LSTM model: {service.lstm_model is not None}")
print(f"Attack type model: {service.attack_type_model is not None}")

# Check if U0001 is in baseline profiles
if service.baseline_profiles:
    print(f"\nSample entity IDs from baseline: {list(service.baseline_profiles.keys())[:5]}")
    print(f"U0001 in baseline: {'U0001' in service.baseline_profiles}")
    print(f"u0001 in baseline: {'u0001' in service.baseline_profiles}")

# Test prediction
test_event = {
    "event_id": "EVT-001",
    "timestamp": datetime.now().isoformat(),
    "entity_id": "U0001",
    "resource_accessed": "Internal Server",
    "geo_location": "Bangalore",
    "auth_method": "Password",
    "device_type": "Laptop",
    "failed_login_attempts": 0,
    "session_duration": 120,
}

print("\n\nTesting prediction with U0001:")
result = service.predict(test_event)
print(json.dumps(result, indent=2, default=str))

# Try with lowercase
test_event['entity_id'] = 'u0001'
print("\n\nTesting prediction with u0001:")
result = service.predict(test_event)
print(json.dumps(result, indent=2, default=str))
