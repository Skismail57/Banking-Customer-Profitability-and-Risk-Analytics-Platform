# Streaming Integration Guide

This guide provides comprehensive instructions for integrating and using the streaming components of the Banking Analytics Platform.

## Table of Contents

1. [Infrastructure Setup](#infrastructure-setup)
2. [Database Migrations](#database-migrations)
3. [Starting the Streaming Pipeline](#starting-the-streaming-pipeline)
4. [Using the Streaming API](#using-the-streaming-api)
5. [Live Monitor Dashboard](#live-monitor-dashboard)
6. [Historical Replay](#historical-replay)
7. [Configuration Reference](#configuration-reference)
8. [Troubleshooting](#troubleshooting)

## Infrastructure Setup

### Prerequisites

- Docker and Docker Compose installed
- Python 3.9+
- PostgreSQL client
- Redis client

### Starting Streaming Infrastructure

The streaming infrastructure uses a separate Docker Compose file for Redpanda (Kafka-compatible) and Redis.

```bash
# Start core services (PostgreSQL, FastAPI, Streamlit)
docker-compose up -d

# Start streaming services (Redpanda, Redis)
docker-compose -f docker-compose.streaming.yml up -d
```

### Environment Configuration

Copy `.env.example` to `.env` and configure the following streaming variables:

```bash
# Redpanda (Kafka-compatible) Configuration
REDPANDA_PORT=9092
REDPANDA_ADMIN_PORT=9644
REDPANDA_SCHEMA_REGISTRY_PORT=8081
REDPANDA_ADVERTISED_ADDRESS=localhost
KAFKA_BROKERS=localhost:9092
KAFKA_GROUP_ID=banking_analytics_group

# Redis Configuration
REDIS_PORT=6379
REDIS_HOST=localhost
REDIS_DB=0
REDIS_MAX_MEMORY=256mb

# Schema Registry Configuration
SCHEMA_REGISTRY_URL=http://localhost:8081

# Real-time Processing Configuration
ALLOWED_LATENESS_SECONDS=300
WATERMARK_DELAY_SECONDS=60
IDEMPOTENCY_TTL_SECONDS=86400
```

## Database Migrations

Run the database migrations to add streaming tables and columns:

```bash
# Apply migration 001: Add streaming tables
alembic upgrade 001_add_streaming_tables

# Apply migration 002: Add real-time columns to existing tables
alembic upgrade 002_add_realtime_columns
```

### Migration Details

**Migration 001** creates the following tables:
- `fact_realtime_events` - Raw banking events
- `fact_event_processing_log` - Event processing tracking
- `fact_streaming_predictions` - Real-time ML predictions
- `fact_streaming_anomalies` - Real-time anomaly detection
- `fact_risk_events` - Real-time risk events
- `fact_alerts` - Alert management
- `fact_decision_audit` - Decision audit trail
- `dim_model_registry` - Model registry
- `fact_reconciliation_results` - Batch-stream reconciliation
- `fact_replay_runs` - Historical replay tracking

**Migration 002** adds real-time columns to existing tables:
- `dim_customer`: `last_realtime_event_time`, `realtime_risk_level`, `realtime_risk_score`, `on_watchlist`
- `fact_transaction`: `event_time`, `processing_time`

## Starting the Streaming Pipeline

### Using the Orchestrator

The `StreamingOrchestrator` is the main entry point for the streaming pipeline:

```python
from src.streaming.config import StreamingConfig
from src.streaming.orchestrator.pipeline_orchestrator import StreamingOrchestrator

# Load configuration
config = StreamingConfig()

# Initialize orchestrator
orchestrator = StreamingOrchestrator(config)

# Start the pipeline
orchestrator.start()

# Process a single event
event_data = {
    'event_id': 'evt_123',
    'event_type': 'transaction',
    'customer_key': 'cust_456',
    'timestamp': '2026-09-08T12:00:00Z',
    'amount': 1000.00,
    'account_id': 'acct_789'
}

result = orchestrator.process_event(event_data)

# Stop the pipeline
orchestrator.stop()
```

### Pipeline Configuration

Create a `config/pipeline.yaml` file to configure the pipeline:

```yaml
components:
  anomaly_detection:
    enabled: true
    methods: ['iqr', 'zscore']
    thresholds:
      amount_threshold: 3.0
      velocity_window_minutes: 60
      velocity_max_transactions: 10
  
  risk_scoring:
    enabled: true
    risk_types: ['credit', 'payment', 'concentration']
  
  early_warning:
    enabled: true
    warning_types: ['utilization', 'payment', 'balance']
  
  alert_generation:
    enabled: true
    min_severity: 'high'
    deduplication_window_seconds: 300
  
  model_inference:
    enabled: true
    models: ['churn_predictor', 'risk_predictor', 'clv_predictor']

processing:
  batch_size: 100
  max_latency_ms: 1000
  parallel_workers: 4
```

## Using the Streaming API

### Base URL

```
http://localhost:8000/api/v1/realtime
```

### Endpoints

#### Get Real-Time Alerts

```bash
GET /api/v1/realtime/alerts?limit=20&severity=high&status=open
```

Response:
```json
[
  {
    "alert_id": "alert_123",
    "alert_type": "risk_credit",
    "customer_key": "cust_456",
    "severity": "high",
    "alert_source": "risk_engine",
    "alert_message": "Risk Alert: CREDIT risk level HIGH detected.",
    "triggered_at": "2026-09-08T12:00:00Z",
    "status": "open",
    "context_data": {...}
  }
]
```

#### Acknowledge an Alert

```bash
POST /api/v1/realtime/alerts/{alert_id}/acknowledge
Content-Type: application/json

{
  "acknowledged_by": "user_123"
}
```

#### Get Real-Time Risk Score

```bash
GET /api/v1/realtime/risk/{customer_key}
```

Response:
```json
{
  "customer_key": "cust_456",
  "risk_level": "high",
  "risk_score": 0.75,
  "updated_at": "2026-09-08T12:00:00Z"
}
```

#### Get Watchlist

```bash
GET /api/v1/realtime/watchlist?limit=50
```

#### Get Streaming Metrics

```bash
GET /api/v1/realtime/metrics
```

Response:
```json
{
  "events_processed": 1250,
  "events_per_second": 0.35,
  "alerts_generated": 15,
  "anomalies_detected": 8,
  "risk_events": 12,
  "processing_latency_ms": 45.2,
  "uptime_percentage": 100.0
}
```

#### Get Decision Audit Trail

```bash
GET /api/v1/realtime/decisions/{customer_key}?decision_type=risk_score&limit=100
```

### WebSocket Support

WebSocket endpoints are available for real-time updates:

```python
import websockets

async def connect():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        await websocket.send({"client_id": "client_123"})
        while True:
            message = await websocket.recv()
            print(f"Received: {message}")
```

## Live Monitor Dashboard

Access the live monitor dashboard through the Streamlit application:

1. Navigate to http://localhost:8501
2. Select "Live Monitor" from the sidebar
3. The dashboard provides:
   - Real-time metrics (events processed, alerts, anomalies, latency)
   - Recent alerts with severity indicators
   - Watchlist with warning level distribution
   - Customer risk score lookup with gauge visualization
   - Auto-refresh every 5 seconds (configurable)

### Dashboard Features

- **Metrics Overview**: Key performance indicators at a glance
- **Alert Feed**: Real-time alert stream with severity color-coding
- **Watchlist Management**: View customers on watchlist with warning levels
- **Risk Score Lookup**: Search for specific customer risk scores
- **Auto-Refresh**: Configurable auto-refresh for real-time updates

## Historical Replay

### Creating a Replay Run

```python
from src.streaming.replay.replay_engine import ReplayEngine
from datetime import datetime

# Initialize replay engine
replay_engine = ReplayEngine(config, orchestrator, db_session)

# Create replay run
replay_id = replay_engine.create_replay_run(
    replay_name="Model Validation Test",
    source_range_start=datetime(2026, 9, 1),
    source_range_end=datetime(2026, 9, 7),
    speed_multiplier=10.0,  # 10x faster than real-time
    event_selection_criteria={
        'customer_key': 'cust_456'
    },
    model_version='v1.2.0',
    feature_version='v1.0.0'
)

# Execute replay
results = replay_engine.execute_replay(replay_id)
```

### Replay Scenarios

The `config/replay.yaml` file includes pre-configured scenarios:

- **model_validation**: Validate new model version against historical data
- **feature_parity**: Validate feature parity between batch and streaming
- **debugging**: Debug specific customer issues
- **regression_testing**: Test pipeline changes for regressions

### Replay Configuration

```yaml
defaults:
  speed_multiplier: 1.0
  target_environment: development
  max_events_per_run: 100000
  timeout_minutes: 60

selection_templates:
  all_events:
    criteria: {}
  
  specific_customer:
    criteria:
      customer_key: null
  
  high_value_customers:
    criteria:
      customer_segment: "high_value"
```

## Configuration Reference

### Streaming Configuration (`config/streaming.yaml`)

```yaml
broker:
  brokers: localhost:9092
  group_id: banking_analytics_group
  auto_offset_reset: earliest

schema_registry:
  url: http://localhost:8081

redis:
  host: localhost
  port: 6379
  db: 0
  max_memory: 256mb

feature_store:
  ttl_seconds: 86400
  snapshot_ttl_seconds: 604800

event_processing:
  allowed_lateness_seconds: 300
  watermark_delay_seconds: 60
  idempotency_ttl_seconds: 86400

alerts:
  deduplication_window_seconds: 300
```

### Logging Configuration (`config/logging.yaml`)

The logging configuration supports:
- Console output (standard and detailed)
- File output with rotation
- JSON format for log aggregation
- Component-specific log levels

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `KAFKA_BROKERS` | Kafka broker addresses | `localhost:9092` |
| `REDIS_HOST` | Redis host | `localhost` |
| `REDIS_PORT` | Redis port | `6379` |
| `SCHEMA_REGISTRY_URL` | Schema registry URL | `http://localhost:8081` |
| `ALLOWED_LATENESS_SECONDS` | Allowed event lateness | `300` |
| `WATERMARK_DELAY_SECONDS` | Watermark delay | `60` |
| `IDEMPOTENCY_TTL_SECONDS` | Idempotency TTL | `86400` |

## Troubleshooting

### Common Issues

#### Redis Connection Failed

**Error**: `redis.exceptions.ConnectionError`

**Solution**:
```bash
# Check if Redis is running
docker-compose -f docker-compose.streaming.yml ps redis

# Check Redis logs
docker-compose -f docker-compose.streaming.yml logs redis

# Restart Redis
docker-compose -f docker-compose.streaming.yml restart redis
```

#### Kafka Connection Failed

**Error**: `KafkaError: Connection failed`

**Solution**:
```bash
# Check if Redpanda is running
docker-compose -f docker-compose.streaming.yml ps redpanda

# Check Redpanda logs
docker-compose -f docker-compose.streaming.yml logs redpanda

# Restart Redpanda
docker-compose -f docker-compose.streaming.yml restart redpanda
```

#### Migration Failed

**Error**: `alembic.util.exc.CommandError`

**Solution**:
```bash
# Check current migration status
alembic current

# Rollback if needed
alembic downgrade base

# Re-run migration
alembic upgrade head
```

#### High Processing Latency

**Symptom**: Processing latency > 1000ms

**Solutions**:
1. Check system resources (CPU, memory)
2. Increase `parallel_workers` in pipeline config
3. Reduce batch size
4. Check Redis connection latency
5. Profile slow components

#### Alert Fatigue

**Symptom**: Too many alerts generated

**Solutions**:
1. Increase `deduplication_window_seconds` in config
2. Raise `min_severity` threshold
3. Adjust anomaly detection thresholds
4. Review and tune risk thresholds

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Or modify `config/logging.yaml` to set component log levels to `DEBUG`.

### Health Checks

Check system health:

```bash
# Overall health
curl http://localhost:8000/health

# Readiness check
curl http://localhost:8000/health/ready

# Liveness check
curl http://localhost:8000/health/live
```

## Next Steps

1. **Testing**: Run the test suite to verify streaming components
2. **Monitoring**: Set up Prometheus/Grafana for metrics visualization
3. **Alerting**: Configure external alerting (PagerDuty, Slack, etc.)
4. **Scaling**: Configure horizontal scaling for production
5. **Security**: Enable authentication and authorization for API endpoints

## Support

For issues or questions:
- Check logs in `logs/` directory
- Review health check endpoints
- Consult the main README.md
- Check component-specific documentation in `docs/`
