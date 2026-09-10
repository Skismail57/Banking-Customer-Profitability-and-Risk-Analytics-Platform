# Streaming Database Schema Documentation

## Overview

This document describes the database schema extensions for the streaming infrastructure that extends the existing Banking Analytics Platform with real-time event processing capabilities.

## Architecture Principle

The streaming schema follows the existing architectural principles:
- **Extend, don't replace**: New tables complement existing batch tables
- **Regulatory compliance**: Audit trails with 7-year retention where required
- **Banking domain**: Tables designed for banking-specific use cases
- **Separation of concerns**: Batch and streaming data are kept separate
- **Reconciliation**: Support for batch-stream consistency validation

## New Tables

### 1. fact_realtime_events

**Purpose**: Store raw banking events from the streaming pipeline with event-time processing support.

**Key Columns**:
- `event_id` (PK): Unique event identifier
- `event_type`: Type of banking event (transaction, account_update, etc.)
- `customer_key` (FK): Reference to customer dimension
- `event_timestamp`: When the event actually occurred (event-time)
- `ingestion_timestamp`: When the event was ingested into the system
- `processing_timestamp`: When the event was processed
- `event_data` (JSONB): Full event payload
- `source_system`: Source system that generated the event
- `status`: Processing status (pending, processing, completed, failed)

**Indexes**:
- `customer_key`: For customer-based queries
- `event_timestamp`: For time-based queries
- `status`: For status-based filtering
- `event_type`: For event type filtering

**Constraints**:
- Status check constraint
- Foreign key to `dim_customer.customer_key`

**Retention**: 90 days

**Use Cases**:
- Event replay and backtesting
- Audit trail for regulatory compliance
- Debugging and incident investigation
- Event-time processing validation

---

### 2. fact_event_processing_log

**Purpose**: Track event processing stages through the streaming pipeline for audit and performance monitoring.

**Key Columns**:
- `log_id` (PK): Unique log entry identifier
- `event_id` (FK): Reference to event
- `processing_stage`: Pipeline stage (validation, feature engineering, prediction, etc.)
- `status`: Stage status (started, completed, failed)
- `processing_timestamp`: When the stage was processed
- `latency_ms`: Processing latency in milliseconds
- `error_message`: Error details if failed

**Indexes**:
- `event_id`: For event-based queries
- `processing_timestamp`: For time-based analysis
- `status`: For status-based filtering

**Constraints**:
- Status check constraint
- Foreign key to `fact_realtime_events.event_id`

**Retention**: 30 days

**Use Cases**:
- Pipeline performance monitoring
- Debugging failed events
- SLA tracking
- Processing stage analysis

---

### 3. fact_streaming_predictions

**Purpose**: Store real-time ML predictions from the streaming pipeline with model version tracking.

**Key Columns**:
- `prediction_id` (PK): Unique prediction identifier
- `event_id` (FK): Reference to triggering event
- `customer_key` (FK): Reference to customer
- `model_name`: Name of the ML model
- `model_version`: Version of the model used
- `prediction_type`: Type of prediction (risk, churn, etc.)
- `prediction_value`: Prediction score (0-1 for probabilities)
- `prediction_timestamp`: When prediction was made
- `feature_snapshot_id`: Reference to feature snapshot used

**Indexes**:
- `event_id`: For event-based queries
- `customer_key`: For customer-based queries
- `prediction_timestamp`: For time-based analysis
- `model_version`: For model version tracking

**Constraints**:
- Prediction value range check (0-1)
- Foreign keys to `fact_realtime_events` and `dim_customer`

**Retention**: 1 year

**Use Cases**:
- Real-time decision support
- Model performance monitoring
- Prediction audit trail
- Model A/B testing

---

### 4. fact_streaming_anomalies

**Purpose**: Store real-time anomaly detection results (fraud, behavioral anomalies, etc.).

**Key Columns**:
- `anomaly_id` (PK): Unique anomaly identifier
- `event_id` (FK): Reference to triggering event
- `customer_key` (FK): Reference to customer
- `anomaly_type`: Type of anomaly (fraud, behavioral, etc.)
- `anomaly_score`: Anomaly score
- `severity`: Severity level (low, medium, high, critical)
- `detected_at`: When anomaly was detected
- `context_data` (JSONB): Additional context

**Indexes**:
- `event_id`: For event-based queries
- `customer_key`: For customer-based queries
- `detected_at`: For time-based analysis
- `severity`: For severity-based filtering

**Constraints**:
- Severity check constraint
- Foreign keys to `fact_realtime_events` and `dim_customer`

**Retention**: 2 years

**Use Cases**:
- Real-time fraud detection
- Behavioral anomaly monitoring
- Risk escalation
- Fraud investigation

---

### 5. fact_risk_events

**Purpose**: Store real-time risk events and escalations (credit risk, operational risk, etc.).

**Key Columns**:
- `risk_event_id` (PK): Unique risk event identifier
- `event_id` (FK): Reference to triggering event
- `customer_key` (FK): Reference to customer
- `risk_type`: Type of risk (credit, operational, concentration)
- `risk_level`: Risk level (low, medium, high, critical)
- `risk_score`: Calculated risk score
- `triggered_at`: When risk event was triggered
- `threshold_violated`: Which threshold was violated
- `context_data` (JSONB): Additional context

**Indexes**:
- `event_id`: For event-based queries
- `customer_key`: For customer-based queries
- `triggered_at`: For time-based analysis
- `risk_level`: For risk level filtering

**Constraints**:
- Risk level check constraint
- Foreign keys to `fact_realtime_events` and `dim_customer`

**Retention**: 5 years

**Use Cases**:
- Real-time risk monitoring
- Risk escalation
- Regulatory reporting
- Risk concentration analysis

---

### 6. fact_alerts

**Purpose**: Store alert management and tracking for risk, anomaly, and business alerts.

**Key Columns**:
- `alert_id` (PK): Unique alert identifier
- `alert_type`: Type of alert (risk, anomaly, business)
- `customer_key` (FK): Reference to customer (nullable for system alerts)
- `severity`: Alert severity (low, medium, high, critical)
- `alert_source`: Source of the alert (model, rule, threshold)
- `alert_message`: Alert message text
- `triggered_at`: When alert was triggered
- `acknowledged_at`: When alert was acknowledged
- `acknowledged_by`: Who acknowledged the alert
- `status`: Alert status (open, acknowledged, resolved, closed)
- `context_data` (JSONB): Additional context

**Indexes**:
- `customer_key`: For customer-based queries
- `triggered_at`: For time-based analysis
- `severity`: For severity-based filtering
- `status`: For status-based filtering

**Constraints**:
- Severity check constraint
- Status check constraint
- Foreign key to `dim_customer.customer_key`

**Retention**: 2 years

**Use Cases**:
- Alert management
- SLA tracking
- Operational monitoring
- Compliance reporting

---

### 7. fact_decision_audit

**Purpose**: Store decision audit trail for regulatory compliance and explainability.

**Key Columns**:
- `decision_id` (PK): Unique decision identifier
- `event_id` (FK): Reference to triggering event
- `customer_key` (FK): Reference to customer
- `decision_type`: Type of decision (risk_alert, fraud_detection, etc.)
- `decision_timestamp`: When decision was made
- `model_version`: Model version used
- `feature_version`: Feature version used
- `feature_snapshot_id`: Reference to feature snapshot
- `anomaly_score`: Anomaly score if applicable
- `risk_score`: Risk score if applicable
- `threshold`: Threshold used for decision
- `decision_outcome`: Final decision outcome
- `reason_codes`: Array of reason codes explaining the decision
- `processing_latency_ms`: Decision processing latency

**Indexes**:
- `event_id`: For event-based queries
- `customer_key`: For customer-based queries
- `decision_timestamp`: For time-based analysis
- `decision_type`: For decision type filtering

**Constraints**:
- Foreign keys to `fact_realtime_events` and `dim_customer`

**Retention**: 7 years (regulatory requirement)

**Use Cases**:
- Regulatory compliance
- Decision explainability
- Audit trails
- Incident investigation
- "Why was this decision made?" queries

---

### 8. dim_model_registry

**Purpose**: Store ML model lifecycle management information (model registry).

**Key Columns**:
- `model_id` (PK): Unique model identifier
- `model_name`: Name of the model
- `model_version`: Version of the model (unique)
- `model_type`: Type of model (classification, regression, anomaly_detection)
- `framework`: ML framework (scikit-learn, tensorflow, etc.)
- `artifact_location`: Location of model artifact
- `training_dataset_version`: Version of training dataset
- `feature_version`: Version of features used
- `hyperparameters` (JSONB): Model hyperparameters
- `metrics` (JSONB): Model performance metrics
- `validation_status`: Validation status (pending, validated, failed)
- `deployment_status`: Deployment status (development, staging, production, archived)
- `promoted_at`: When model was promoted
- `archived_at`: When model was archived

**Indexes**:
- `model_name`: For model-based queries
- `model_type`: For model type filtering
- `deployment_status`: For deployment status filtering

**Constraints**:
- Model version unique constraint
- Validation status check constraint
- Deployment status check constraint

**Retention**: Permanent (model registry)

**Use Cases**:
- Model lifecycle management
- Model promotion and rollback
- Model performance tracking
- Model deployment governance

---

### 9. fact_reconciliation_results

**Purpose**: Store batch-stream reconciliation results for data consistency validation.

**Key Columns**:
- `reconciliation_id` (PK): Unique reconciliation identifier
- `reconciliation_type`: Type of reconciliation (event_count, feature_value, prediction, alert)
- `reconciliation_date`: Date of reconciliation
- `batch_count`: Count from batch processing
- `streaming_count`: Count from streaming processing
- `difference_count`: Absolute difference
- `difference_percentage`: Percentage difference
- `status`: Reconciliation status (pass, warning, fail)
- `details` (JSONB): Detailed reconciliation results

**Indexes**:
- `reconciliation_date`: For date-based queries
- `reconciliation_type`: For type-based filtering
- `status`: For status-based filtering

**Constraints**:
- Status check constraint

**Retention**: 2 years

**Use Cases**:
- Batch-stream consistency validation
- Data quality monitoring
- Incident investigation
- Process improvement

---

### 10. fact_replay_runs

**Purpose**: Store historical replay run tracking for testing and validation.

**Key Columns**:
- `replay_id` (PK): Unique replay identifier
- `replay_name`: Name of the replay run
- `source_range_start`: Start of replay time range
- `source_range_end`: End of replay time range
- `event_selection_criteria` (JSONB): Criteria for event selection
- `speed_multiplier`: Speed multiplier for replay
- `target_environment`: Target environment for replay
- `model_version`: Model version to use in replay
- `feature_version`: Feature version to use in replay
- `started_at`: When replay started
- `completed_at`: When replay completed
- `status`: Replay status (pending, running, completed, failed, cancelled)
- `events_processed`: Number of events processed
- `results_summary` (JSONB): Summary of replay results

**Indexes**:
- `started_at`: For time-based queries
- `status`: For status-based filtering

**Constraints**:
- Status check constraint

**Retention**: 1 year

**Use Cases**:
- Regression testing
- Model validation
- Feature validation
- Pipeline testing
- Incident investigation
- Backtesting

---

## Relationship to Existing Tables

### Foreign Key Relationships

All streaming fact tables that reference customers use the existing `dim_customer.customer_key` as a foreign key:

- `fact_realtime_events.customer_key` → `dim_customer.customer_key`
- `fact_streaming_predictions.customer_key` → `dim_customer.customer_key`
- `fact_streaming_anomalies.customer_key` → `dim_customer.customer_key`
- `fact_risk_events.customer_key` → `dim_customer.customer_key`
- `fact_alerts.customer_key` → `dim_customer.customer_key`
- `fact_decision_audit.customer_key` → `dim_customer.customer_key`

### Event Relationship

Streaming predictions, anomalies, and risk events reference the originating event:

- `fact_streaming_predictions.event_id` → `fact_realtime_events.event_id`
- `fact_streaming_anomalies.event_id` → `fact_realtime_events.event_id`
- `fact_risk_events.event_id` → `fact_realtime_events.event_id`
- `fact_event_processing_log.event_id` → `fact_realtime_events.event_id`
- `fact_decision_audit.event_id` → `fact_realtime_events.event_id`

---

## Batch vs Streaming Data Flow

### Batch Pipeline (Existing)
```
Banking Data → ETL → PostgreSQL → Batch Analytics → Batch Tables
```

### Streaming Pipeline (New)
```
Banking Events → Redpanda → Stream Processor → Redis → Streaming Tables
```

### Reconciliation
```
Batch Tables + Streaming Tables → Reconciliation Engine → fact_reconciliation_results
```

---

## Data Retention Policy

| Table | Retention | Reason |
|-------|-----------|--------|
| fact_realtime_events | 90 days | Event replay window |
| fact_event_processing_log | 30 days | Performance monitoring |
| fact_streaming_predictions | 1 year | Prediction audit trail |
| fact_streaming_anomalies | 2 years | Fraud investigation |
| fact_risk_events | 5 years | Risk reporting |
| fact_alerts | 2 years | Alert management |
| fact_decision_audit | 7 years | Regulatory compliance |
| dim_model_registry | Permanent | Model registry |
| fact_reconciliation_results | 2 years | Quality monitoring |
| fact_replay_runs | 1 year | Testing records |

---

## Migration Process

### Applying the Migration

```bash
# Apply the migration
alembic upgrade head

# Verify the migration
alembic current

# Rollback if needed
alembic downgrade -1
```

### Testing the Migration

```bash
# Run unit tests for streaming models
pytest tests/unit/models/test_streaming.py -v

# Run integration tests with actual database
pytest tests/integration/test_streaming_database.py -v
```

---

## Key Design Decisions

### 1. Event-Time Processing
- `event_timestamp` represents when the event actually occurred
- `ingestion_timestamp` represents when the event entered the system
- `processing_timestamp` represents when the event was processed
- This distinction is critical for out-of-order and late event handling

### 2. Regulatory Compliance
- `fact_decision_audit` has 7-year retention for regulatory compliance
- Full context is stored to answer "why was this decision made?"
- Feature snapshots are referenced to preserve exact feature values

### 3. Separation of Concerns
- Streaming tables are separate from existing batch tables
- Reconciliation is explicit via `fact_reconciliation_results`
- No modification to existing batch tables

### 4. Banking Domain Specificity
- Event types are banking-specific (transaction, account_update, loan_application)
- Risk events support credit risk, operational risk, concentration risk
- Alerts support banking-specific alert types

### 5. Performance Considerations
- All foreign key columns are indexed
- Timestamp columns are indexed for time-based queries
- Status columns are indexed for filtering
- JSONB columns for flexible context storage

---

## Future Extensions

### Potential Future Tables
- `fact_feature_snapshots`: Store feature snapshots for audit
- `fact_model_performance_history`: Historical model performance
- `fact_data_quality_streaming`: Streaming data quality metrics
- `fact_consumer_lag`: Consumer lag metrics for monitoring

### Potential Future Columns
- `fact_realtime_events.partition_key`: For event partitioning
- `fact_streaming_predictions.confidence_score`: Prediction confidence
- `fact_alerts.escalation_level`: Alert escalation tracking

---

## Backup and Recovery

### Backup Strategy
- Streaming tables are included in regular PostgreSQL backups
- Point-in-time recovery (PITR) is supported
- Separate backup schedules for different retention requirements

### Recovery Procedures
- In case of data loss, restore from backup
- Replay events from `fact_realtime_events` to rebuild streaming state
- Use `fact_replay_runs` to validate recovery

---

## Security Considerations

### Access Control
- Streaming tables should have appropriate row-level security
- `fact_decision_audit` requires restricted access (compliance)
- `dim_model_registry` requires restricted access (model governance)

### Data Masking
- PII in `event_data` should be masked in non-production environments
- `context_data` may contain sensitive information and should be protected

### Audit Logging
- All modifications to streaming tables should be logged
- Schema changes should be tracked
- Data access should be audited

---

## Monitoring and Observability

### Key Metrics
- Event ingestion rate (events per second)
- Processing latency (event to prediction)
- Consumer lag (how far behind)
- Alert rate (alerts per time period)
- Reconciliation pass rate

### Alerting
- High processing latency
- High consumer lag
- High DLQ rate
- Reconciliation failures
- Model performance degradation

---

## References

- [Main Architecture Documentation](../ARCHITECTURE.md)
- [Data Dictionary](../DATA_DICTIONARY.md)
- [Streaming Configuration](../config/streaming.yaml)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)