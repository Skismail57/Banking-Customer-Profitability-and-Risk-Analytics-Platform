"""Streaming models for real-time analytics.

This module contains SQLAlchemy models for the streaming infrastructure tables.
These models follow the existing banking analytics architecture and conventions.
"""

from datetime import datetime
from typing import Optional
from enum import Enum

from sqlalchemy import (
    String,
    Integer,
    Numeric,
    DateTime,
    Text,
    Boolean,
    Index,
    CheckConstraint,
    JSON as JSONType,
    ARRAY,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.models.base import Base, TimestampMixin


class EventStatus(str, Enum):
    """Event processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessingStatus(str, Enum):
    """Processing stage status."""
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"


class Severity(str, Enum):
    """Severity levels for alerts and anomalies."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    """Alert status."""
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    CLOSED = "closed"


class ModelValidationStatus(str, Enum):
    """Model validation status."""
    PENDING = "pending"
    VALIDATED = "validated"
    FAILED = "failed"


class ModelDeploymentStatus(str, Enum):
    """Model deployment status."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    ARCHIVED = "archived"


class ReconciliationStatus(str, Enum):
    """Reconciliation status."""
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"


class ReplayStatus(str, Enum):
    """Replay run status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class FactRealtimeEvent(Base, TimestampMixin):
    """Real-time banking events fact table.
    
    Stores raw banking events from the streaming pipeline with timestamps
    for event-time processing and audit trails.
    """
    
    __tablename__ = "fact_realtime_events"
    
    # Primary key
    event_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    
    # Event details
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    customer_key: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    
    # Timestamps
    event_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    ingestion_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    processing_timestamp: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Event data
    event_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    source_system: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Processing status
    status: Mapped[str] = mapped_column(
        String(20),
        server_default="pending",
        nullable=False,
        index=True
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'processing', 'completed', 'failed')",
            name="ck_realtime_events_status"
        ),
        Index("ix_realtime_events_customer_key", "customer_key"),
        Index("ix_realtime_events_event_timestamp", "event_timestamp"),
        Index("ix_realtime_events_status", "status"),
        Index("ix_realtime_events_event_type", "event_type"),
    )


class FactEventProcessingLog(Base, TimestampMixin):
    """Event processing log fact table.
    
    Tracks the processing stages for each event through the streaming pipeline.
    Provides audit trail and performance monitoring.
    """
    
    __tablename__ = "fact_event_processing_log"
    
    # Primary key
    log_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    
    # Foreign key
    event_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Processing details
    processing_stage: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    processing_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    
    # Performance metrics
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('started', 'completed', 'failed')",
            name="ck_event_processing_status"
        ),
        Index("ix_event_processing_event_id", "event_id"),
        Index("ix_event_processing_timestamp", "processing_timestamp"),
        Index("ix_event_processing_status", "status"),
    )


class FactStreamingPrediction(Base, TimestampMixin):
    """Streaming predictions fact table.
    
    Stores real-time ML predictions from the streaming pipeline.
    Links predictions to events and models for auditability.
    """
    
    __tablename__ = "fact_streaming_predictions"
    
    # Primary key
    prediction_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    
    # Foreign keys
    event_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    customer_key: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Model information
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Prediction details
    prediction_type: Mapped[str] = mapped_column(String(50), nullable=False)
    prediction_value: Mapped[Optional[float]] = mapped_column(Numeric(15, 6), nullable=True)
    prediction_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    
    # Feature snapshot reference
    feature_snapshot_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "prediction_value >= 0 AND prediction_value <= 1",
            name="ck_prediction_value_range"
        ),
        Index("ix_streaming_predictions_event_id", "event_id"),
        Index("ix_streaming_predictions_customer_key", "customer_key"),
        Index("ix_streaming_predictions_timestamp", "prediction_timestamp"),
        Index("ix_streaming_predictions_model_version", "model_version"),
    )


class FactStreamingAnomaly(Base, TimestampMixin):
    """Streaming anomalies fact table.
    
    Stores real-time anomaly detection results from the streaming pipeline.
    Includes fraud detection and behavioral anomalies.
    """
    
    __tablename__ = "fact_streaming_anomalies"
    
    # Primary key
    anomaly_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    
    # Foreign keys
    event_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    customer_key: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Anomaly details
    anomaly_type: Mapped[str] = mapped_column(String(50), nullable=False)
    anomaly_score: Mapped[Optional[float]] = mapped_column(Numeric(10, 6), nullable=True)
    severity: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    
    # Context data
    context_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "severity IN ('low', 'medium', 'high', 'critical')",
            name="ck_anomaly_severity"
        ),
        Index("ix_streaming_anomalies_event_id", "event_id"),
        Index("ix_streaming_anomalies_customer_key", "customer_key"),
        Index("ix_streaming_anomalies_detected_at", "detected_at"),
        Index("ix_streaming_anomalies_severity", "severity"),
    )


class FactRiskEvent(Base, TimestampMixin):
    """Risk events fact table.
    
    Stores real-time risk events and escalations from the streaming pipeline.
    Includes credit risk, operational risk, and concentration risk events.
    """
    
    __tablename__ = "fact_risk_events"
    
    # Primary key
    risk_event_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    
    # Foreign keys
    event_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    customer_key: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Risk details
    risk_type: Mapped[str] = mapped_column(String(50), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    risk_score: Mapped[Optional[float]] = mapped_column(Numeric(10, 6), nullable=True)
    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    
    # Threshold information
    threshold_violated: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Context data
    context_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "risk_level IN ('low', 'medium', 'high', 'critical')",
            name="ck_risk_level"
        ),
        Index("ix_risk_events_event_id", "event_id"),
        Index("ix_risk_events_customer_key", "customer_key"),
        Index("ix_risk_events_triggered_at", "triggered_at"),
        Index("ix_risk_events_risk_level", "risk_level"),
    )


class FactAlert(Base, TimestampMixin):
    """Alerts fact table.
    
    Stores alert management and tracking for risk, anomaly, and business alerts.
    Includes acknowledgment and resolution tracking.
    """
    
    __tablename__ = "fact_alerts"
    
    # Primary key
    alert_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    
    # Alert details
    alert_type: Mapped[str] = mapped_column(String(50), nullable=False)
    customer_key: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    alert_source: Mapped[str] = mapped_column(String(50), nullable=False)
    alert_message: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Timing
    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    acknowledged_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        server_default="open",
        nullable=False,
        index=True
    )
    
    # Context data
    context_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "severity IN ('low', 'medium', 'high', 'critical')",
            name="ck_alert_severity"
        ),
        CheckConstraint(
            "status IN ('open', 'acknowledged', 'resolved', 'closed')",
            name="ck_alert_status"
        ),
        Index("ix_alerts_customer_key", "customer_key"),
        Index("ix_alerts_triggered_at", "triggered_at"),
        Index("ix_alerts_severity", "severity"),
        Index("ix_alerts_status", "status"),
    )


class FactDecisionAudit(Base, TimestampMixin):
    """Decision audit fact table.
    
    Stores decision audit trail for regulatory compliance.
    Tracks why decisions were made with full context.
    """
    
    __tablename__ = "fact_decision_audit"
    
    # Primary key
    decision_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    
    # Foreign keys
    event_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    customer_key: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    
    # Decision details
    decision_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    decision_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    
    # Model and feature information
    model_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    feature_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    feature_snapshot_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Scores and thresholds
    anomaly_score: Mapped[Optional[float]] = mapped_column(Numeric(10, 6), nullable=True)
    risk_score: Mapped[Optional[float]] = mapped_column(Numeric(10, 6), nullable=True)
    threshold: Mapped[Optional[float]] = mapped_column(Numeric(10, 6), nullable=True)
    
    # Decision outcome
    decision_outcome: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    reason_codes: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)
    
    # Performance
    processing_latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Constraints
    __table_args__ = (
        Index("ix_decision_audit_event_id", "event_id"),
        Index("ix_decision_audit_customer_key", "customer_key"),
        Index("ix_decision_audit_timestamp", "decision_timestamp"),
        Index("ix_decision_audit_decision_type", "decision_type"),
    )


class DimModelRegistry(Base, TimestampMixin):
    """Model registry dimension table.
    
    Stores ML model lifecycle management information.
    Tracks model versions, deployments, and performance metrics.
    """
    
    __tablename__ = "dim_model_registry"
    
    # Primary key
    model_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    
    # Model identification
    model_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    model_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    framework: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Artifact location
    artifact_location: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Training information
    training_dataset_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    feature_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Model parameters and metrics
    hyperparameters: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    metrics: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Lifecycle status
    validation_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    deployment_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)
    
    # Lifecycle timestamps
    promoted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    archived_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "validation_status IN ('pending', 'validated', 'failed')",
            name="ck_model_validation_status"
        ),
        CheckConstraint(
            "deployment_status IN ('development', 'staging', 'production', 'archived')",
            name="ck_model_deployment_status"
        ),
        Index("ix_model_registry_model_name", "model_name"),
        Index("ix_model_registry_model_type", "model_type"),
        Index("ix_model_registry_deployment_status", "deployment_status"),
    )


class FactReconciliationResult(Base, TimestampMixin):
    """Reconciliation results fact table.
    
    Stores batch-stream reconciliation results for data consistency validation.
    """
    
    __tablename__ = "fact_reconciliation_results"
    
    # Primary key
    reconciliation_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    
    # Reconciliation details
    reconciliation_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    reconciliation_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    
    # Count comparisons
    batch_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    streaming_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    difference_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    difference_percentage: Mapped[Optional[float]] = mapped_column(Numeric(10, 6), nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    
    # Detailed results
    details: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('pass', 'warning', 'fail')",
            name="ck_reconciliation_status"
        ),
        Index("ix_reconciliation_date", "reconciliation_date"),
        Index("ix_reconciliation_type", "reconciliation_type"),
        Index("ix_reconciliation_status", "status"),
    )


class FactReplayRun(Base, TimestampMixin):
    """Replay runs fact table.
    
    Stores historical replay run tracking for testing and validation.
    """
    
    __tablename__ = "fact_replay_runs"
    
    # Primary key
    replay_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    
    # Replay configuration
    replay_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    source_range_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    source_range_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    event_selection_criteria: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    speed_multiplier: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    target_environment: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Model and feature versions for replay
    model_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    feature_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Execution tracking
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)
    events_processed: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Results
    results_summary: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'running', 'completed', 'failed', 'cancelled')",
            name="ck_replay_status"
        ),
        Index("ix_replay_started_at", "started_at"),
        Index("ix_replay_status", "status"),
    )