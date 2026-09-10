# Streaming Architecture Documentation

This document describes the streaming architecture of the Banking Customer Profitability and Risk Analytics Platform.

## Overview

The streaming architecture enables real-time event processing, risk assessment, and alerting for the banking analytics platform. It follows an event-driven architecture pattern with Kafka as the central event bus.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Event Sources                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ Banking  │  │ Payment  │  │ Customer │  │ External │      │
│  │ Systems  │  │ Gateway  │  │ Portal   │  │ APIs     │      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
└───────┼────────────┼────────────┼────────────┼─────────────────┘
        │            │            │            │
        └────────────┼────────────┼────────────┘
                     │            │
        ┌────────────▼────────────▼────────────┐
        │         Kafka / Redpanda             │
        │  ┌──────────────────────────────┐    │
        │  │  Topics:                     │    │
        │  │  - transactions              │    │
        │  │  - customer_events           │    │
        │  │  - risk_events               │    │
        │  │  - alerts                    │    │
        │  └──────────────────────────────┘    │
        └────────────┬─────────────────────────┘
                     │
        ┌────────────▼─────────────────────────┐
        │       Streaming Orchestrator         │
        │  ┌──────────────────────────────┐    │
        │  │  Event Consumer              │    │
        │  │  Feature Store Adapter       │    │
        │  │  Risk Engine                 │    │
        │  │  Anomaly Detector            │    │
        │  │  Early Warning System        │    │
        │  │  Alert Engine                │    │
        │  │  Decision Auditor            │    │
        │  └──────────────────────────────┘    │
        └────────────┬─────────────────────────┘
                     │
        ┌────────────▼─────────────────────────┐
        │         Feature Store (Redis)        │
        │  ┌──────────────────────────────┐    │
        │  │  Real-time Features           │    │
        │  │  Feature Snapshots           │    │
        │  │  State Management            │    │
        │  └──────────────────────────────┘    │
        └────────────┬─────────────────────────┘
                     │
        ┌────────────▼─────────────────────────┐
        │         PostgreSQL Database          │
        │  ┌──────────────────────────────┐    │
        │  │  fact_realtime_events        │    │
        │  │  fact_replay_runs            │    │
        │  │  fact_reconciliation         │    │
        │  │  dim_customers               │    │
        │  └──────────────────────────────┘    │
        └───────────────────────────────────────┘
```

## Components

### 1. Event Sources

External systems that produce events:

- **Banking Systems**: Core banking platform events
- **Payment Gateway**: Transaction events
- **Customer Portal**: Customer interaction events
- **External APIs**: Third-party service events

### 2. Kafka / Redpanda

Event streaming platform that provides:

- **Event Bus**: Central message broker
- **Topic Management**: Event categorization
- **Partitioning**: Parallel processing
- **Replication**: High availability
- **Schema Registry**: Event schema validation

#### Topics

- `transactions`: Transaction events
- `customer_events`: Customer lifecycle events
- `risk_events`: Risk assessment events
- `alerts`: Alert notifications
- `dlq`: Dead letter queue for failed events

### 3. Streaming Orchestrator

Central coordinator for streaming pipeline:

#### Event Consumer
- Consumes events from Kafka topics
- Handles message deserialization
- Manages consumer group coordination
- Tracks consumer lag

#### Feature Store Adapter
- Stores real-time features in Redis
- Retrieves features for prediction
- Creates feature snapshots
- Manages feature versioning

#### Risk Engine
- Computes real-time risk scores
- Aggregates multi-type risks
- Manages dynamic thresholds
- Updates customer risk levels

#### Anomaly Detector
- Detects real-time anomalies
- Tracks streaming statistics
- Classifies anomaly severity
- Integrates ML-based detection

#### Early Warning System
- Detects warning signals
- Tracks leading indicators
- Manages warning escalation
- Updates customer watchlist

#### Alert Engine
- Generates alerts from events
- Deduplicates alerts
- Routes alerts to channels
- Manages alert lifecycle

#### Decision Auditor
- Captures decision context
- Stores feature snapshots
- Tracks processing latency
- Maintains audit trail

### 4. Feature Store (Redis)

High-performance feature storage:

- **Real-time Features**: Current customer features
- **Feature Snapshots**: Point-in-time feature states
- **State Management**: Streaming state tracking
- **TTL Management**: Automatic data expiration

### 5. PostgreSQL Database

Persistent data storage:

- **fact_realtime_events**: Event history
- **fact_replay_runs**: Replay execution records
- **fact_reconciliation**: Reconciliation results
- **dim_customers**: Customer dimension data

## Reliability Patterns

### 1. Retry Logic
- Exponential backoff for failed operations
- Configurable retry limits
- Circuit breaker integration

### 2. Dead Letter Queue
- Failed message handling
- Error categorization
- Replay capability

### 3. Circuit Breaker
- Fault tolerance
- Automatic recovery
- State monitoring

### 4. Backpressure
- Flow rate control
- Consumer throttling
- Resource protection

## Data Flow

### Event Processing Flow

1. **Event Ingestion**
   - Event published to Kafka topic
   - Schema validation
   - Topic partitioning

2. **Event Consumption**
   - Consumer group assignment
   - Message deserialization
   - Offset management

3. **Feature Extraction**
   - Feature computation
   - Feature storage in Redis
   - Feature snapshot creation

4. **Risk Assessment**
   - Risk score computation
   - Risk aggregation
   - Risk level assignment

5. **Anomaly Detection**
   - Statistical anomaly detection
   - ML-based detection
   - Severity classification

6. **Alert Generation**
   - Alert rule evaluation
   - Alert deduplication
   - Alert routing

7. **Audit Logging**
   - Decision context capture
   - Feature snapshot storage
   - Latency tracking

### Replay Flow

1. **Replay Configuration**
   - Time range selection
   - Event criteria
   - Speed multiplier

2. **Event Retrieval**
   - Query historical events
   - Sort by timestamp
   - Apply filters

3. **Event Reprocessing**
   - Process with speed multiplier
   - Track results
   - Compare with original

4. **Validation**
   - Result comparison
   - Discrepancy analysis
   - Validation report

## Observability

### Metrics Collection

- **Performance Metrics**: Latency, throughput
- **Business Metrics**: Alert counts, anomaly rates
- **System Metrics**: Consumer lag, error rates
- **Custom Metrics**: Domain-specific metrics

### Structured Logging

- JSON-formatted logs
- Trace ID propagation
- Context enrichment
- Log level filtering

### Distributed Tracing

- Request tracking across services
- Span creation for operations
- Trace context propagation
- Performance analysis

## Security

### Authentication

- JWT token validation
- WebSocket authentication
- Service-to-service auth

### Authorization

- Role-based access control
- Resource-level permissions
- API endpoint protection

### Data Protection

- Encryption at rest
- Encryption in transit
- Secure secret management

## Scalability

### Horizontal Scaling

- Kafka partitioning
- Consumer group scaling
- Feature store sharding
- Database read replicas

### Vertical Scaling

- Resource allocation
- Performance tuning
- Query optimization

## Deployment

### Docker Deployment

- Containerized components
- Docker Compose orchestration
- Health checks
- Resource limits

### Kubernetes Deployment

- Deployment manifests
- Service configuration
- ConfigMap management
- Secret management

### CI/CD Integration

- Automated builds
- Automated testing
- Automated deployment
- Rollback support
