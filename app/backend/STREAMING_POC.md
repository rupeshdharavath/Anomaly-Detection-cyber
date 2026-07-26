Streaming PoC
===========

This repository includes a lightweight proof-of-concept for streaming ingestion and near-real-time inference.

- Design: events are published to a queue (Kafka/Redis/Cloud PubSub). A pool of workers consumes events, calls the `InferenceService.predict()` API, and writes alerts to a durable store.
- Implemented: background worker pattern (see `app/backend/services/cold_start_service.py` and `app/backend/services/drift_monitor.py`). These demonstrate how to run background processors alongside FastAPI.
- Next steps for production: replace the in-process queue with a durable broker (Kafka/Redis Streams), add idempotency and acknowledgements, scale workers horizontally, and persist state to a DB.

Example lightweight worker pseudocode:

```python
from kafka import KafkaConsumer
from requests import post

consumer = KafkaConsumer('events', bootstrap_servers=['kafka:9092'])
for msg in consumer:
    event = json.loads(msg.value)
    # send to local inference API
    post('http://localhost:8000/api/v1/anomalies/detect', json=event)
```
