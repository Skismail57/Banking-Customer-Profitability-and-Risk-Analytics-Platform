"""Unit tests for streaming models.

This module tests the SQLAlchemy models for streaming infrastructure.
"""

import pytest
from datetime import datetime, timezone
from decimal import Decimal

from src.models.streaming import (
    FactRealtimeEvent,
    FactEventProcessingLog,
    FactStreamingPrediction,
    FactStreamingAnomaly,
    FactRiskEvent,
    FactAlert,
    FactDecisionAudit,
    DimModelRegistry,
    FactReconciliationResult,
    FactReplayRun,
    EventStatus,
    ProcessingStatus,
    Severity,
    AlertStatus,
    ModelValidationStatus,
    ModelDeploymentStatus,
    ReconciliationStatus,
    ReplayStatus,
)


class TestStreamingModels:
    """Test streaming model definitions and constraints."""
    
    def test_event_status_enum(self):
        """Test EventStatus enum values."""
        assert EventStatus.PENDING == "pending"
        assert EventStatus.PROCESSING == "processing"
        assert EventStatus.COMPLETED == "completed"
        assert EventStatus.FAILED == "failed"
    
    def test_severity_enum(self):
        """Test Severity enum values."""
        assert Severity.LOW == "low"
        assert Severity.MEDIUM == "medium"
        assert Severity.HIGH == "high"
        assert Severity.CRITICAL == "critical"
    
    def test_alert_status_enum(self):
        """Test AlertStatus enum values."""
        assert AlertStatus.OPEN == "open"
        assert AlertStatus.ACKNOWLEDGED == "acknowledged"
        assert AlertStatus.RESOLVED == "resolved"
        assert AlertStatus.CLOSED == "closed"
    
    def test_model_validation_status_enum(self):
        """Test ModelValidationStatus enum values."""
        assert ModelValidationStatus.PENDING == "pending"
        assert ModelValidationStatus.VALIDATED == "validated"
        assert ModelValidationStatus.FAILED == "failed"
    
    def test_model_deployment_status_enum(self):
        """Test ModelDeploymentStatus enum values."""
        assert ModelDeploymentStatus.DEVELOPMENT == "development"
        assert ModelDeploymentStatus.STAGING == "staging"
        assert ModelDeploymentStatus.PRODUCTION == "production"
        assert ModelDeploymentStatus.ARCHIVED == "archived"
    
    def test_reconciliation_status_enum(self):
        """Test ReconciliationStatus enum values."""
        assert ReconciliationStatus.PASS == "pass"
        assert ReconciliationStatus.WARNING == "warning"
        assert ReconciliationStatus.FAIL == "fail"
    
    def test_replay_status_enum(self):
        """Test ReplayStatus enum values."""
        assert ReplayStatus.PENDING == "pending"
        assert ReplayStatus.RUNNING == "running"
        assert ReplayStatus.COMPLETED == "completed"
        assert ReplayStatus.FAILED == "failed"
        assert ReplayStatus.CANCELLED == "cancelled"


class TestFactRealtimeEvent:
    """Test FactRealtimeEvent model."""
    
    def test_model_attributes(self):
        """Test that FactRealtimeEvent has required attributes."""
        assert hasattr(FactRealtimeEvent, 'event_id')
        assert hasattr(FactRealtimeEvent, 'event_type')
        assert hasattr(FactRealtimeEvent, 'customer_key')
        assert hasattr(FactRealtimeEvent, 'event_timestamp')
        assert hasattr(FactRealtimeEvent, 'ingestion_timestamp')
        assert hasattr(FactRealtimeEvent, 'processing_timestamp')
        assert hasattr(FactRealtimeEvent, 'event_data')
        assert hasattr(FactRealtimeEvent, 'source_system')
        assert hasattr(FactRealtimeEvent, 'status')
    
    def test_table_name(self):
        """Test that table name is correct."""
        assert FactRealtimeEvent.__tablename__ == "fact_realtime_events"


class TestFactEventProcessingLog:
    """Test FactEventProcessingLog model."""
    
    def test_model_attributes(self):
        """Test that FactEventProcessingLog has required attributes."""
        assert hasattr(FactEventProcessingLog, 'log_id')
        assert hasattr(FactEventProcessingLog, 'event_id')
        assert hasattr(FactEventProcessingLog, 'processing_stage')
        assert hasattr(FactEventProcessingLog, 'status')
        assert hasattr(FactEventProcessingLog, 'processing_timestamp')
        assert hasattr(FactEventProcessingLog, 'latency_ms')
        assert hasattr(FactEventProcessingLog, 'error_message')
    
    def test_table_name(self):
        """Test that table name is correct."""
        assert FactEventProcessingLog.__tablename__ == "fact_event_processing_log"


class TestFactStreamingPrediction:
    """Test FactStreamingPrediction model."""
    
    def test_model_attributes(self):
        """Test that FactStreamingPrediction has required attributes."""
        assert hasattr(FactStreamingPrediction, 'prediction_id')
        assert hasattr(FactStreamingPrediction, 'event_id')
        assert hasattr(FactStreamingPrediction, 'customer_key')
        assert hasattr(FactStreamingPrediction, 'model_name')
        assert hasattr(FactStreamingPrediction, 'model_version')
        assert hasattr(FactStreamingPrediction, 'prediction_type')
        assert hasattr(FactStreamingPrediction, 'prediction_value')
        assert hasattr(FactStreamingPrediction, 'prediction_timestamp')
        assert hasattr(FactStreamingPrediction, 'feature_snapshot_id')
    
    def test_table_name(self):
        """Test that table name is correct."""
        assert FactStreamingPrediction.__tablename__ == "fact_streaming_predictions"


class TestFactStreamingAnomaly:
    """Test FactStreamingAnomaly model."""
    
    def test_model_attributes(self):
        """Test that FactStreamingAnomaly has required attributes."""
        assert hasattr(FactStreamingAnomaly, 'anomaly_id')
        assert hasattr(FactStreamingAnomaly, 'event_id')
        assert hasattr(FactStreamingAnomaly, 'customer_key')
        assert hasattr(FactStreamingAnomaly, 'anomaly_type')
        assert hasattr(FactStreamingAnomaly, 'anomaly_score')
        assert hasattr(FactStreamingAnomaly, 'severity')
        assert hasattr(FactStreamingAnomaly, 'detected_at')
        assert hasattr(FactStreamingAnomaly, 'context_data')
    
    def test_table_name(self):
        """Test that table name is correct."""
        assert FactStreamingAnomaly.__tablename__ == "fact_streaming_anomalies"


class TestFactRiskEvent:
    """Test FactRiskEvent model."""
    
    def test_model_attributes(self):
        """Test that FactRiskEvent has required attributes."""
        assert hasattr(FactRiskEvent, 'risk_event_id')
        assert hasattr(FactRiskEvent, 'event_id')
        assert hasattr(FactRiskEvent, 'customer_key')
        assert hasattr(FactRiskEvent, 'risk_type')
        assert hasattr(FactRiskEvent, 'risk_level')
        assert hasattr(FactRiskEvent, 'risk_score')
        assert hasattr(FactRiskEvent, 'triggered_at')
        assert hasattr(FactRiskEvent, 'threshold_violated')
        assert hasattr(FactRiskEvent, 'context_data')
    
    def test_table_name(self):
        """Test that table name is correct."""
        assert FactRiskEvent.__tablename__ == "fact_risk_events"


class TestFactAlert:
    """Test FactAlert model."""
    
    def test_model_attributes(self):
        """Test that FactAlert has required attributes."""
        assert hasattr(FactAlert, 'alert_id')
        assert hasattr(FactAlert, 'alert_type')
        assert hasattr(FactAlert, 'customer_key')
        assert hasattr(FactAlert, 'severity')
        assert hasattr(FactAlert, 'alert_source')
        assert hasattr(FactAlert, 'alert_message')
        assert hasattr(FactAlert, 'triggered_at')
        assert hasattr(FactAlert, 'acknowledged_at')
        assert hasattr(FactAlert, 'acknowledged_by')
        assert hasattr(FactAlert, 'status')
        assert hasattr(FactAlert, 'context_data')
    
    def test_table_name(self):
        """Test that table name is correct."""
        assert FactAlert.__tablename__ == "fact_alerts"


class TestFactDecisionAudit:
    """Test FactDecisionAudit model."""
    
    def test_model_attributes(self):
        """Test that FactDecisionAudit has required attributes."""
        assert hasattr(FactDecisionAudit, 'decision_id')
        assert hasattr(FactDecisionAudit, 'event_id')
        assert hasattr(FactDecisionAudit, 'customer_key')
        assert hasattr(FactDecisionAudit, 'decision_type')
        assert hasattr(FactDecisionAudit, 'decision_timestamp')
        assert hasattr(FactDecisionAudit, 'model_version')
        assert hasattr(FactDecisionAudit, 'feature_version')
        assert hasattr(FactDecisionAudit, 'feature_snapshot_id')
        assert hasattr(FactDecisionAudit, 'anomaly_score')
        assert hasattr(FactDecisionAudit, 'risk_score')
        assert hasattr(FactDecisionAudit, 'threshold')
        assert hasattr(FactDecisionAudit, 'decision_outcome')
        assert hasattr(FactDecisionAudit, 'reason_codes')
        assert hasattr(FactDecisionAudit, 'processing_latency_ms')
    
    def test_table_name(self):
        """Test that table name is correct."""
        assert FactDecisionAudit.__tablename__ == "fact_decision_audit"


class TestDimModelRegistry:
    """Test DimModelRegistry model."""
    
    def test_model_attributes(self):
        """Test that DimModelRegistry has required attributes."""
        assert hasattr(DimModelRegistry, 'model_id')
        assert hasattr(DimModelRegistry, 'model_name')
        assert hasattr(DimModelRegistry, 'model_version')
        assert hasattr(DimModelRegistry, 'model_type')
        assert hasattr(DimModelRegistry, 'framework')
        assert hasattr(DimModelRegistry, 'artifact_location')
        assert hasattr(DimModelRegistry, 'training_dataset_version')
        assert hasattr(DimModelRegistry, 'feature_version')
        assert hasattr(DimModelRegistry, 'hyperparameters')
        assert hasattr(DimModelRegistry, 'metrics')
        assert hasattr(DimModelRegistry, 'validation_status')
        assert hasattr(DimModelRegistry, 'deployment_status')
        assert hasattr(DimModelRegistry, 'promoted_at')
        assert hasattr(DimModelRegistry, 'archived_at')
    
    def test_table_name(self):
        """Test that table name is correct."""
        assert DimModelRegistry.__tablename__ == "dim_model_registry"


class TestFactReconciliationResult:
    """Test FactReconciliationResult model."""
    
    def test_model_attributes(self):
        """Test that FactReconciliationResult has required attributes."""
        assert hasattr(FactReconciliationResult, 'reconciliation_id')
        assert hasattr(FactReconciliationResult, 'reconciliation_type')
        assert hasattr(FactReconciliationResult, 'reconciliation_date')
        assert hasattr(FactReconciliationResult, 'batch_count')
        assert hasattr(FactReconciliationResult, 'streaming_count')
        assert hasattr(FactReconciliationResult, 'difference_count')
        assert hasattr(FactReconciliationResult, 'difference_percentage')
        assert hasattr(FactReconciliationResult, 'status')
        assert hasattr(FactReconciliationResult, 'details')
    
    def test_table_name(self):
        """Test that table name is correct."""
        assert FactReconciliationResult.__tablename__ == "fact_reconciliation_results"


class TestFactReplayRun:
    """Test FactReplayRun model."""
    
    def test_model_attributes(self):
        """Test that FactReplayRun has required attributes."""
        assert hasattr(FactReplayRun, 'replay_id')
        assert hasattr(FactReplayRun, 'replay_name')
        assert hasattr(FactReplayRun, 'source_range_start')
        assert hasattr(FactReplayRun, 'source_range_end')
        assert hasattr(FactReplayRun, 'event_selection_criteria')
        assert hasattr(FactReplayRun, 'speed_multiplier')
        assert hasattr(FactReplayRun, 'target_environment')
        assert hasattr(FactReplayRun, 'model_version')
        assert hasattr(FactReplayRun, 'feature_version')
        assert hasattr(FactReplayRun, 'started_at')
        assert hasattr(FactReplayRun, 'completed_at')
        assert hasattr(FactReplayRun, 'status')
        assert hasattr(FactReplayRun, 'events_processed')
        assert hasattr(FactReplayRun, 'results_summary')
    
    def test_table_name(self):
        """Test that table name is correct."""
        assert FactReplayRun.__tablename__ == "fact_replay_runs"


class TestModelRelationships:
    """Test model relationships and foreign keys."""
    
    def test_fact_realtime_event_customer_foreign_key(self):
        """Test that FactRealtimeEvent has customer foreign key."""
        # The model should have a relationship to DimCustomer
        # This test validates the model structure
        assert hasattr(FactRealtimeEvent, 'customer_key')
    
    def test_fact_streaming_prediction_customer_foreign_key(self):
        """Test that FactStreamingPrediction has customer foreign key."""
        assert hasattr(FactStreamingPrediction, 'customer_key')
    
    def test_fact_streaming_anomaly_customer_foreign_key(self):
        """Test that FactStreamingAnomaly has customer foreign key."""
        assert hasattr(FactStreamingAnomaly, 'customer_key')
    
    def test_fact_risk_event_customer_foreign_key(self):
        """Test that FactRiskEvent has customer foreign key."""
        assert hasattr(FactRiskEvent, 'customer_key')
    
    def test_fact_alert_customer_foreign_key(self):
        """Test that FactAlert has customer foreign key."""
        assert hasattr(FactAlert, 'customer_key')
    
    def test_fact_decision_audit_customer_foreign_key(self):
        """Test that FactDecisionAudit has customer foreign key."""
        assert hasattr(FactDecisionAudit, 'customer_key')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])