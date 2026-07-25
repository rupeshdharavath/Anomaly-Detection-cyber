import json

async def app(scope, receive, send):
    assert scope['type'] == 'http'
    path = scope.get('path', '/')
    method = scope.get('method', 'GET').upper()

    # Handle CORS preflight for any route
    if method == 'OPTIONS':
        await send({
            'type': 'http.response.start',
            'status': 204,
            'headers': [
                (b'access-control-allow-origin', b'*'),
                (b'access-control-allow-headers', b'*'),
                (b'access-control-allow-methods', b'*'),
            ],
        })
        await send({'type': 'http.response.body', 'body': b''})
        return

    if path.startswith('/api/v1/anomalies/detect') and method == 'POST':
        # read body
        body = b''
        more_body = True
        while more_body:
            event = await receive()
            if event['type'] == 'http.request':
                body += event.get('body', b'')
                more_body = event.get('more_body', False)
        try:
            payload = json.loads(body.decode('utf-8') or '{}')
        except Exception:
            payload = {}
        response = {
            'status': 'ok',
            'mock': True,
            'input': payload,
            'anomaly': {
                'flagged': False,
                'risk_score': 0.1,
                'confidence': 0.6,
                'reasons': ['dev-mode sample']
            }
        }
        body_bytes = json.dumps(response).encode('utf-8')
        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [
                (b'content-type', b'application/json'),
                (b'access-control-allow-origin', b'*'),
                (b'access-control-allow-headers', b'*'),
                (b'access-control-allow-methods', b'*'),
            ],
        })
        await send({'type': 'http.response.body', 'body': body_bytes})
        return

    if path == '/' or path.startswith('/health'):
        body = json.dumps({'status': 'ok', 'dev_mode': True}).encode('utf-8')
        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [
                (b'content-type', b'application/json'),
                (b'access-control-allow-origin', b'*'),
                (b'access-control-allow-headers', b'*'),
                (b'access-control-allow-methods', b'*'),
            ],
        })
        await send({'type': 'http.response.body', 'body': body})
        return

    # Mock analytics endpoint
    if path.startswith('/api/v1/analytics/overview') and method == 'GET':
        payload = {
            'total_events': 12345,
            'anomalies': 12,
            'alerts': 5,
            'top_resources': [{'name': 'server-1', 'count': 4}],
        }
        body = json.dumps(payload).encode('utf-8')
        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [
                (b'content-type', b'application/json'),
                (b'access-control-allow-origin', b'*'),
                (b'access-control-allow-headers', b'*'),
                (b'access-control-allow-methods', b'*'),
            ],
        })
        await send({'type': 'http.response.body', 'body': body})
        return

    # Mock analytics time-series
    if path.startswith('/api/v1/analytics/time-series') and method == 'GET':
        # simple timeseries mock
        payload = {'series': [{'ts': i, 'value': i % 5} for i in range(24)], 'hours': 24}
        body = json.dumps(payload).encode('utf-8')
        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [
                (b'content-type', b'application/json'),
                (b'access-control-allow-origin', b'*'),
                (b'access-control-allow-headers', b'*'),
                (b'access-control-allow-methods', b'*'),
            ],
        })
        await send({'type': 'http.response.body', 'body': body})
        return

    # Mock analytics model performance
    if path.startswith('/api/v1/analytics/model-performance') and method == 'GET':
        payload = {'models': [{'name': 'baseline', 'precision': 0.7, 'recall': 0.5}, {'name': 'lstm', 'precision': 0.85, 'recall': 0.78}]}
        body = json.dumps(payload).encode('utf-8')
        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [
                (b'content-type', b'application/json'),
                (b'access-control-allow-origin', b'*'),
                (b'access-control-allow-headers', b'*'),
                (b'access-control-allow-methods', b'*'),
            ],
        })
        await send({'type': 'http.response.body', 'body': body})
        return

    # Mock analytics risk-distribution
    if path.startswith('/api/v1/analytics/risk-distribution') and method == 'GET':
        payload = {'low': 80, 'medium': 15, 'high': 5}
        body = json.dumps(payload).encode('utf-8')
        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [
                (b'content-type', b'application/json'),
                (b'access-control-allow-origin', b'*'),
                (b'access-control-allow-headers', b'*'),
                (b'access-control-allow-methods', b'*'),
            ],
        })
        await send({'type': 'http.response.body', 'body': body})
        return

    # Mock analytics top-resources and top-locations
    if path.startswith('/api/v1/analytics/top-resources') and method == 'GET':
        payload = {'items': [{'name': 'server-1', 'count': 10}, {'name': 'db-1', 'count': 5}]}
        body = json.dumps(payload).encode('utf-8')
        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [
                (b'content-type', b'application/json'),
                (b'access-control-allow-origin', b'*'),
                (b'access-control-allow-headers', b'*'),
                (b'access-control-allow-methods', b'*'),
            ],
        })
        await send({'type': 'http.response.body', 'body': body})
        return

    if path.startswith('/api/v1/analytics/top-locations') and method == 'GET':
        payload = {'items': [{'location': 'US', 'count': 20}, {'location': 'EU', 'count': 8}]}
        body = json.dumps(payload).encode('utf-8')
        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [
                (b'content-type', b'application/json'),
                (b'access-control-allow-origin', b'*'),
                (b'access-control-allow-headers', b'*'),
                (b'access-control-allow-methods', b'*'),
            ],
        })
        await send({'type': 'http.response.body', 'body': body})
        return

    # Mock analytics entity-risk-summary
    if path.startswith('/api/v1/analytics/entity-risk-summary') and method == 'GET':
        payload = {'users': 2, 'devices': 1}
        body = json.dumps(payload).encode('utf-8')
        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [
                (b'content-type', b'application/json'),
                (b'access-control-allow-origin', b'*'),
                (b'access-control-allow-headers', b'*'),
                (b'access-control-allow-methods', b'*'),
            ],
        })
        await send({'type': 'http.response.body', 'body': body})
        return

    # Mock anomalies list
    if path.startswith('/api/v1/anomalies/list') and method == 'GET':
        payload = {'items': [], 'total': 0}
        body = json.dumps(payload).encode('utf-8')
        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [
                (b'content-type', b'application/json'),
                (b'access-control-allow-origin', b'*'),
                (b'access-control-allow-headers', b'*'),
                (b'access-control-allow-methods', b'*'),
            ],
        })
        await send({'type': 'http.response.body', 'body': body})
        return

    # Mock anomalies statistics
    if path.startswith('/api/v1/anomalies/statistics') and method == 'GET':
        payload = {'by_type': {'login_failure': 3, 'data_exfil': 1}, 'total': 4}
        body = json.dumps(payload).encode('utf-8')
        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [
                (b'content-type', b'application/json'),
                (b'access-control-allow-origin', b'*'),
                (b'access-control-allow-headers', b'*'),
                (b'access-control-allow-methods', b'*'),
            ],
        })
        await send({'type': 'http.response.body', 'body': body})
        return

    # Mock alerts active
    if path.startswith('/api/v1/alerts/active') and method == 'GET':
        payload = {'items': [], 'total': 0}
        body = json.dumps(payload).encode('utf-8')
        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [
                (b'content-type', b'application/json'),
                (b'access-control-allow-origin', b'*'),
                (b'access-control-allow-headers', b'*'),
                (b'access-control-allow-methods', b'*'),
            ],
        })
        await send({'type': 'http.response.body', 'body': body})
        return

    # Mock entities users list
    if path.startswith('/api/v1/entities/users') and method == 'GET':
        payload = {'data': [], 'total': 0}
        body = json.dumps(payload).encode('utf-8')
        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [
                (b'content-type', b'application/json'),
                (b'access-control-allow-origin', b'*'),
                (b'access-control-allow-headers', b'*'),
                (b'access-control-allow-methods', b'*'),
            ],
        })
        await send({'type': 'http.response.body', 'body': body})
        return

    # Mock entities devices list
    if path.startswith('/api/v1/entities/devices') and method == 'GET':
        payload = {'data': [], 'total': 0}
        body = json.dumps(payload).encode('utf-8')
        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [
                (b'content-type', b'application/json'),
                (b'access-control-allow-origin', b'*'),
                (b'access-control-allow-headers', b'*'),
                (b'access-control-allow-methods', b'*'),
            ],
        })
        await send({'type': 'http.response.body', 'body': body})
        return

    # Mock entities search
    if path.startswith('/api/v1/entities/search') and method == 'GET':
        params = {}
        # return empty results
        payload = {'data': [], 'total': 0}
        body = json.dumps(payload).encode('utf-8')
        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [
                (b'content-type', b'application/json'),
                (b'access-control-allow-origin', b'*'),
                (b'access-control-allow-headers', b'*'),
                (b'access-control-allow-methods', b'*'),
            ],
        })
        await send({'type': 'http.response.body', 'body': body})
        return

    # Mock models endpoints
    if path.startswith('/api/v1/models/info') and method == 'GET':
        payload = {
            'models': [
                {'name': 'baseline', 'version': '1.0', 'loaded': True},
                {'name': 'lstm', 'version': '1.2', 'loaded': False}
            ]
        }
        body = json.dumps(payload).encode('utf-8')
        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [
                (b'content-type', b'application/json'),
                (b'access-control-allow-origin', b'*'),
                (b'access-control-allow-headers', b'*'),
                (b'access-control-allow-methods', b'*'),
            ],
        })
        await send({'type': 'http.response.body', 'body': body})
        return

    if path.startswith('/api/v1/models/status') and method == 'GET':
        payload = {'status': 'degraded', 'models_loaded': False}
        body = json.dumps(payload).encode('utf-8')
        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [
                (b'content-type', b'application/json'),
                (b'access-control-allow-origin', b'*'),
                (b'access-control-allow-headers', b'*'),
                (b'access-control-allow-methods', b'*'),
            ],
        })
        await send({'type': 'http.response.body', 'body': body})
        return

    if path.startswith('/api/v1/models/performance') and method == 'GET':
        payload = {'baseline': {'precision': 0.7, 'recall': 0.5}, 'lstm': {'precision': 0.85, 'recall': 0.78}}
        body = json.dumps(payload).encode('utf-8')
        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [
                (b'content-type', b'application/json'),
                (b'access-control-allow-origin', b'*'),
                (b'access-control-allow-headers', b'*'),
                (b'access-control-allow-methods', b'*'),
            ],
        })
        await send({'type': 'http.response.body', 'body': body})
        return

    # default 404
    await send({
        'type': 'http.response.start',
        'status': 404,
        'headers': [(b'content-type', b'text/plain')],
    })
    await send({'type': 'http.response.body', 'body': b'Not Found'})
