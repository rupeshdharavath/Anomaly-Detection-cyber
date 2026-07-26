import requests
import json
from datetime import datetime

base_url = 'http://localhost:8000/api/v1'

# Test simulate endpoint with different scenarios
scenarios = [
    {
        "event_id": "EVT-001",
        "timestamp": datetime.now().isoformat(),
        "entity_id": "U0001",
        "resource_accessed": "Internal Server",
        "geo_location": "Bangalore",
        "auth_method": "Password",
        "device_type": "Laptop",
        "failed_login_attempts": 0,
        "session_duration": 120,
    },
    {
        "event_id": "EVT-002",
        "timestamp": datetime.now().isoformat(),
        "entity_id": "U0001",
        "resource_accessed": "Finance DB",  # Different resource
        "geo_location": "Bangalore",
        "auth_method": "Password",
        "device_type": "Laptop",
        "failed_login_attempts": 5,  # Multiple failed attempts
        "session_duration": 120,
    },
    {
        "event_id": "EVT-003",
        "timestamp": datetime.now().isoformat(),
        "entity_id": "U9999",  # Unknown entity
        "resource_accessed": "Internal Server",
        "geo_location": "Bangalore",
        "auth_method": "Password",
        "device_type": "Laptop",
        "failed_login_attempts": 0,
        "session_duration": 120,
    },
]

for scenario in scenarios:
    try:
        print(f"\nTesting: {scenario['entity_id']} accessing {scenario['resource_accessed']} (failed logins: {scenario['failed_login_attempts']})")
        resp = requests.post(f'{base_url}/anomalies/detect', json=scenario)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Risk Score: {data.get('risk_score')}")
            print(f"Risk Level: {data.get('risk_level')}")
            print(f"Confidence: {data.get('confidence')}")
            print(f"Attack Type: {data.get('attack_type')}")
            print(f"Reasons: {data.get('reasons')}")
        else:
            print(f"Error: {resp.text}")
    except Exception as e:
        print(f"Exception: {e}")
