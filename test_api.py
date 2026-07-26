import requests
import json

base_url = 'http://localhost:8000/api/v1'

# Test analytics overview
try:
    resp = requests.get(f'{base_url}/analytics/overview')
    print("Analytics Overview:")
    print(json.dumps(resp.json(), indent=2))
    print()
except Exception as e:
    print(f"Error fetching analytics: {e}\n")

# Test alerts
try:
    resp = requests.get(f'{base_url}/alerts/active')
    print("Active Alerts:")
    data = resp.json()
    print(f"Status: {data.get('status')}")
    print(f"Total alerts: {data.get('total')}")
    if data.get('items'):
        print(f"Number of alerts: {len(data['items'])}")
        if len(data['items']) > 0:
            print(f"First alert keys: {list(data['items'][0].keys())}")
    print()
except Exception as e:
    print(f"Error fetching alerts: {e}\n")

# Test time-series
try:
    resp = requests.get(f'{base_url}/analytics/time-series?hours=24')
    print("Time Series Data:")
    data = resp.json()
    print(f"Status: {data.get('status')}")
    if data.get('data', {}).get('points'):
        print(f"Total points: {data['data']['total_points']}")
        print(f"First point: {data['data']['points'][0]}")
    else:
        print(f"No points returned")
    print()
except Exception as e:
    print(f"Error fetching time-series: {e}\n")

# Test anomaly detection
try:
    resp = requests.get(f'{base_url}/anomalies/list')
    print("Anomalies List:")
    data = resp.json()
    print(f"Status: {data.get('status')}")
    print(f"Total anomalies: {data.get('total')}")
    print()
except Exception as e:
    print(f"Error fetching anomalies: {e}\n")
