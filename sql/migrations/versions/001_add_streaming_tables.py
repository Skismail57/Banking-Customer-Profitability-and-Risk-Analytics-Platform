"""Add streaming tables for real-time analytics

Revision ID: 001_add_streaming_tables
Revises: 
Create Date: 2026-09-08

This migration adds tables for the streaming infrastructure:
- fact_realtime_events: Raw banking events
- fact_event_processing_log: Event processing tracking
- fact_streaming_predictions: Real-time ML predictions
- fact_streaming_anomalies: Real-time anomaly detection
- fact_risk_events: Real-time risk events
- fact_alerts: Alert management
- fact_decision_audit: Decision audit trail
- dim_model_registry: Model registry
- fact_reconciliation_results: Batch-stream reconciliation
- fact_replay_runs: Historical replay tracking
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_add_streaming_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create fact_realtime_events table
    op.create_table(
        'fact_realtime_events',
        sa.Column('event_id', sa.String(50), primary_key=True),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('customer_key', sa.String(50), nullable=True),
        sa.Column('event_timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('ingestion_timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('processing_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('event_data', postgresql.JSONB, nullable=True),
        sa.Column('source_system', sa.String(50), nullable=True),
        sa.Column('status', sa.String(20), server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['customer_key'], ['dim_customer.customer_key'], ),
        sa.CheckConstraint("status IN ('pending', 'processing', 'completed', 'failed')", name='ck_realtime_events_status'),
    )
    op.create_index('ix_realtime_events_customer_key', 'fact_realtime_events', ['customer_key'])
    op.create_index('ix_realtime_events_event_timestamp', 'fact_realtime_events', ['event_timestamp'])
    op.create_index('ix_realtime_events_status', 'fact_realtime_events', ['status'])
    op.create_index('ix_realtime_events_event_type', 'fact_realtime_events', ['event_type'])

    # Create fact_event_processing_log table
    op.create_table(
        'fact_event_processing_log',
        sa.Column('log_id', sa.String(50), primary_key=True),
        sa.Column('event_id', sa.String(50), nullable=False),
        sa.Column('processing_stage', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('processing_timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('latency_ms', sa.Integer, nullable=True),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.ForeignKeyConstraint(['event_id'], ['fact_realtime_events.event_id'], ),
        sa.CheckConstraint("status IN ('started', 'completed', 'failed')", name='ck_event_processing_status'),
    )
    op.create_index('ix_event_processing_event_id', 'fact_event_processing_log', ['event_id'])
    op.create_index('ix_event_processing_timestamp', 'fact_event_processing_log', ['processing_timestamp'])
    op.create_index('ix_event_processing_status', 'fact_event_processing_log', ['status'])

    # Create fact_streaming_predictions table
    op.create_table(
        'fact_streaming_predictions',
        sa.Column('prediction_id', sa.String(50), primary_key=True),
        sa.Column('event_id', sa.String(50), nullable=False),
        sa.Column('customer_key', sa.String(50), nullable=False),
        sa.Column('model_name', sa.String(100), nullable=False),
        sa.Column('model_version', sa.String(50), nullable=False),
        sa.Column('prediction_type', sa.String(50), nullable=False),
        sa.Column('prediction_value', sa.Numeric(15, 6), nullable=True),
        sa.Column('prediction_timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('feature_snapshot_id', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['event_id'], ['fact_realtime_events.event_id'], ),
        sa.ForeignKeyConstraint(['customer_key'], ['dim_customer.customer_key'], ),
        sa.CheckConstraint("prediction_value >= 0 AND prediction_value <= 1", name='ck_prediction_value_range'),
    )
    op.create_index('ix_streaming_predictions_event_id', 'fact_streaming_predictions', ['event_id'])
    op.create_index('ix_streaming_predictions_customer_key', 'fact_streaming_predictions', ['customer_key'])
    op.create_index('ix_streaming_predictions_timestamp', 'fact_streaming_predictions', ['prediction_timestamp'])
    op.create_index('ix_streaming_predictions_model_version', 'fact_streaming_predictions', ['model_version'])

    # Create fact_streaming_anomalies table
    op.create_table(
        'fact_streaming_anomalies',
        sa.Column('anomaly_id', sa.String(50), primary_key=True),
        sa.Column('event_id', sa.String(50), nullable=False),
        sa.Column('customer_key', sa.String(50), nullable=False),
        sa.Column('anomaly_type', sa.String(50), nullable=False),
        sa.Column('anomaly_score', sa.Numeric(10, 6), nullable=True),
        sa.Column('severity', sa.String(20), nullable=True),
        sa.Column('detected_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('context_data', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['event_id'], ['fact_realtime_events.event_id'], ),
        sa.ForeignKeyConstraint(['customer_key'], ['dim_customer.customer_key'], ),
        sa.CheckConstraint("severity IN ('low', 'medium', 'high', 'critical')", name='ck_anomaly_severity'),
    )
    op.create_index('ix_streaming_anomalies_event_id', 'fact_streaming_anomalies', ['event_id'])
    op.create_index('ix_streaming_anomalies_customer_key', 'fact_streaming_anomalies', ['customer_key'])
    op.create_index('ix_streaming_anomalies_detected_at', 'fact_streaming_anomalies', ['detected_at'])
    op.create_index('ix_streaming_anomalies_severity', 'fact_streaming_anomalies', ['severity'])

    # Create fact_risk_events table
    op.create_table(
        'fact_risk_events',
        sa.Column('risk_event_id', sa.String(50), primary_key=True),
        sa.Column('event_id', sa.String(50), nullable=False),
        sa.Column('customer_key', sa.String(50), nullable=False),
        sa.Column('risk_type', sa.String(50), nullable=False),
        sa.Column('risk_level', sa.String(20), nullable=False),
        sa.Column('risk_score', sa.Numeric(10, 6), nullable=True),
        sa.Column('triggered_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('threshold_violated', sa.String(100), nullable=True),
        sa.Column('context_data', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['event_id'], ['fact_realtime_events.event_id'], ),
        sa.ForeignKeyConstraint(['customer_key'], ['dim_customer.customer_key'], ),
        sa.CheckConstraint("risk_level IN ('low', 'medium', 'high', 'critical')", name='ck_risk_level'),
    )
    op.create_index('ix_risk_events_event_id', 'fact_risk_events', ['event_id'])
    op.create_index('ix_risk_events_customer_key', 'fact_risk_events', ['customer_key'])
    op.create_index('ix_risk_events_triggered_at', 'fact_risk_events', ['triggered_at'])
    op.create_index('ix_risk_events_risk_level', 'fact_risk_events', ['risk_level'])

    # Create fact_alerts table
    op.create_table(
        'fact_alerts',
        sa.Column('alert_id', sa.String(50), primary_key=True),
        sa.Column('alert_type', sa.String(50), nullable=False),
        sa.Column('customer_key', sa.String(50), nullable=True),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('alert_source', sa.String(50), nullable=False),
        sa.Column('alert_message', sa.Text, nullable=False),
        sa.Column('triggered_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('acknowledged_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('acknowledged_by', sa.String(100), nullable=True),
        sa.Column('status', sa.String(20), server_default='open'),
        sa.Column('context_data', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['customer_key'], ['dim_customer.customer_key'], ),
        sa.CheckConstraint("severity IN ('low', 'medium', 'high', 'critical')", name='ck_alert_severity'),
        sa.CheckConstraint("status IN ('open', 'acknowledged', 'resolved', 'closed')", name='ck_alert_status'),
    )
    op.create_index('ix_alerts_customer_key', 'fact_alerts', ['customer_key'])
    op.create_index('ix_alerts_triggered_at', 'fact_alerts', ['triggered_at'])
    op.create_index('ix_alerts_severity', 'fact_alerts', ['severity'])
    op.create_index('ix_alerts_status', 'fact_alerts', ['status'])

    # Create fact_decision_audit table
    op.create_table(
        'fact_decision_audit',
        sa.Column('decision_id', sa.String(50), primary_key=True),
        sa.Column('event_id', sa.String(50), nullable=True),
        sa.Column('customer_key', sa.String(50), nullable=True),
        sa.Column('decision_type', sa.String(50), nullable=False),
        sa.Column('decision_timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('model_version', sa.String(50), nullable=True),
        sa.Column('feature_version', sa.String(50), nullable=True),
        sa.Column('feature_snapshot_id', sa.String(50), nullable=True),
        sa.Column('anomaly_score', sa.Numeric(10, 6), nullable=True),
        sa.Column('risk_score', sa.Numeric(10, 6), nullable=True),
        sa.Column('threshold', sa.Numeric(10, 6), nullable=True),
        sa.Column('decision_outcome', sa.String(50), nullable=True),
        sa.Column('reason_codes', sa.ARRAY(sa.String()), nullable=True),
        sa.Column('processing_latency_ms', sa.Integer, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['event_id'], ['fact_realtime_events.event_id'], ),
        sa.ForeignKeyConstraint(['customer_key'], ['dim_customer.customer_key'], ),
    )
    op.create_index('ix_decision_audit_event_id', 'fact_decision_audit', ['event_id'])
    op.create_index('ix_decision_audit_customer_key', 'fact_decision_audit', ['customer_key'])
    op.create_index('ix_decision_audit_timestamp', 'fact_decision_audit', ['decision_timestamp'])
    op.create_index('ix_decision_audit_decision_type', 'fact_decision_audit', ['decision_type'])

    # Create dim_model_registry table
    op.create_table(
        'dim_model_registry',
        sa.Column('model_id', sa.String(50), primary_key=True),
        sa.Column('model_name', sa.String(200), nullable=False),
        sa.Column('model_version', sa.String(50), nullable=False, unique=True),
        sa.Column('model_type', sa.String(50), nullable=False),
        sa.Column('framework', sa.String(50), nullable=True),
        sa.Column('artifact_location', sa.Text, nullable=True),
        sa.Column('training_dataset_version', sa.String(50), nullable=True),
        sa.Column('feature_version', sa.String(50), nullable=True),
        sa.Column('hyperparameters', postgresql.JSONB, nullable=True),
        sa.Column('metrics', postgresql.JSONB, nullable=True),
        sa.Column('validation_status', sa.String(20), nullable=True),
        sa.Column('deployment_status', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('promoted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('archived_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("validation_status IN ('pending', 'validated', 'failed')", name='ck_model_validation_status'),
        sa.CheckConstraint("deployment_status IN ('development', 'staging', 'production', 'archived')", name='ck_model_deployment_status'),
    )
    op.create_index('ix_model_registry_model_name', 'dim_model_registry', ['model_name'])
    op.create_index('ix_model_registry_model_type', 'dim_model_registry', ['model_type'])
    op.create_index('ix_model_registry_deployment_status', 'dim_model_registry', ['deployment_status'])

    # Create fact_reconciliation_results table
    op.create_table(
        'fact_reconciliation_results',
        sa.Column('reconciliation_id', sa.String(50), primary_key=True),
        sa.Column('reconciliation_type', sa.String(50), nullable=False),
        sa.Column('reconciliation_date', sa.Date, nullable=False),
        sa.Column('batch_count', sa.Integer, nullable=True),
        sa.Column('streaming_count', sa.Integer, nullable=True),
        sa.Column('difference_count', sa.Integer, nullable=True),
        sa.Column('difference_percentage', sa.Numeric(10, 6), nullable=True),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('details', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("status IN ('pass', 'warning', 'fail')", name='ck_reconciliation_status'),
    )
    op.create_index('ix_reconciliation_date', 'fact_reconciliation_results', ['reconciliation_date'])
    op.create_index('ix_reconciliation_type', 'fact_reconciliation_results', ['reconciliation_type'])
    op.create_index('ix_reconciliation_status', 'fact_reconciliation_results', ['status'])

    # Create fact_replay_runs table
    op.create_table(
        'fact_replay_runs',
        sa.Column('replay_id', sa.String(50), primary_key=True),
        sa.Column('replay_name', sa.String(200), nullable=True),
        sa.Column('source_range_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('source_range_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('event_selection_criteria', postgresql.JSONB, nullable=True),
        sa.Column('speed_multiplier', sa.Numeric(5, 2), nullable=True),
        sa.Column('target_environment', sa.String(50), nullable=True),
        sa.Column('model_version', sa.String(50), nullable=True),
        sa.Column('feature_version', sa.String(50), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(20), nullable=True),
        sa.Column('events_processed', sa.Integer, nullable=True),
        sa.Column('results_summary', postgresql.JSONB, nullable=True),
        sa.CheckConstraint("status IN ('pending', 'running', 'completed', 'failed', 'cancelled')", name='ck_replay_status'),
    )
    op.create_index('ix_replay_started_at', 'fact_replay_runs', ['started_at'])
    op.create_index('ix_replay_status', 'fact_replay_runs', ['status'])

    # Add comments to tables
    op.execute("COMMENT ON TABLE fact_realtime_events IS 'Raw banking events from streaming pipeline'")
    op.execute("COMMENT ON TABLE fact_event_processing_log IS 'Event processing tracking and audit trail'")
    op.execute("COMMENT ON TABLE fact_streaming_predictions IS 'Real-time ML predictions from streaming pipeline'")
    op.execute("COMMENT ON TABLE fact_streaming_anomalies IS 'Real-time anomaly detection results'")
    op.execute("COMMENT ON TABLE fact_risk_events IS 'Real-time risk events and escalations'")
    op.execute("COMMENT ON TABLE fact_alerts IS 'Alert management and tracking'")
    op.execute("COMMENT ON TABLE fact_decision_audit IS 'Decision audit trail for regulatory compliance'")
    op.execute("COMMENT ON TABLE dim_model_registry IS 'Model registry for ML model lifecycle management'")
    op.execute("COMMENT ON TABLE fact_reconciliation_results IS 'Batch-stream reconciliation results'")
    op.execute("COMMENT ON TABLE fact_replay_runs IS 'Historical replay run tracking'")


def downgrade():
    # Drop tables in reverse order
    op.drop_table('fact_replay_runs')
    op.drop_table('fact_reconciliation_results')
    op.drop_table('dim_model_registry')
    op.drop_table('fact_decision_audit')
    op.drop_table('fact_alerts')
    op.drop_table('fact_risk_events')
    op.drop_table('fact_streaming_anomalies')
    op.drop_table('fact_streaming_predictions')
    op.drop_table('fact_event_processing_log')
    op.drop_table('fact_realtime_events')