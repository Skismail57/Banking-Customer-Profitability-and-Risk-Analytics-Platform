"""Real-time API endpoints for streaming analytics.

This module provides REST API endpoints for real-time analytics,
including alerts, risk scores, watchlist, and streaming metrics.
"""

from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
import random

from api.database import get_db
from sqlalchemy.orm import Session
from api.auth.dependencies import require_permission
from api.auth.models import Permission
from api.config import settings

router = APIRouter(prefix="/api/v1/realtime", tags=["realtime"])


# Pydantic schemas
class AlertResponse(BaseModel):
    alert_id: str
    alert_type: str
    customer_key: Optional[str]
    severity: str
    alert_source: str
    alert_message: str
    triggered_at: datetime
    status: str
    context_data: dict


class RiskScoreResponse(BaseModel):
    customer_key: str
    risk_level: str
    risk_score: float
    updated_at: datetime


class WatchlistResponse(BaseModel):
    customer_key: str
    on_watchlist: bool
    warning_level: Optional[str]
    warning_score: Optional[float]
    updated_at: datetime


class StreamingMetricsResponse(BaseModel):
    events_processed: int
    events_per_second: float
    alerts_generated: int
    anomalies_detected: int
    risk_events: int
    processing_latency_ms: float
    uptime_percentage: float


@router.get("/alerts", response_model=List[AlertResponse])
async def get_realtime_alerts(
    customer_key: Optional[str] = Query(None, description="Filter by customer"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results"),
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(Permission.ALERTS_VIEW))
):
    """Get real-time alerts.

    Args:
        customer_key: Filter by customer key
        severity: Filter by severity (low, medium, high, critical)
        status: Filter by status (open, acknowledged, resolved, closed)
        limit: Maximum number of results
        db: Database session

    Returns:
        List of alerts
    """
    # Query fact_alerts table
    query = """
        SELECT
            alert_id,
            alert_type,
            customer_key,
            severity,
            alert_source,
            alert_message,
            triggered_at,
            status,
            context_data
        FROM fact_alerts
        WHERE 1=1
    """

    params = {}

    if customer_key:
        query += " AND customer_key = :customer_key"
        params['customer_key'] = customer_key

    if severity:
        query += " AND severity = :severity"
        params['severity'] = severity

    if status:
        query += " AND status = :status"
        params['status'] = status

    query += " ORDER BY triggered_at DESC LIMIT :limit"
    params['limit'] = limit

    result = db.execute(query, params)

    alerts = []
    for row in result:
        alerts.append(AlertResponse(
            alert_id=row.alert_id,
            alert_type=row.alert_type,
            customer_key=row.customer_key,
            severity=row.severity,
            alert_source=row.alert_source,
            alert_message=row.alert_message,
            triggered_at=row.triggered_at,
            status=row.status,
            context_data=row.context_data or {}
        ))

    return alerts


@router.get("/alerts/mock", response_model=List[AlertResponse])
async def get_mock_alerts(
    limit: int = Query(20, ge=1, le=100, description="Maximum results")
):
    """Get mock real-time alerts for development.

    Args:
        limit: Maximum number of results

    Returns:
        List of mock alerts
    """
    alert_types = ["high_transaction", "unusual_location", "suspicious_activity", "velocity_breach"]
    severities = ["low", "medium", "high", "critical"]
    sources = ["fraud_detection", "aml_monitoring", "risk_engine", "transaction_monitoring"]
    statuses = ["open", "acknowledged", "resolved", "closed"]

    alerts = []
    for i in range(min(limit, 20)):
        alerts.append(AlertResponse(
            alert_id=f"alert_{i}",
            alert_type=random.choice(alert_types),
            customer_key=f"CUST_{random.randint(1, 1000):04d}",
            severity=random.choice(severities),
            alert_source=random.choice(sources),
            alert_message=f"Mock alert message {i}",
            triggered_at=datetime.now(),
            status=random.choice(statuses),
            context_data={"mock": True}
        ))

    return alerts


@router.get("/alerts/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(Permission.ALERTS_VIEW))
):
    """Get a specific alert by ID.
    
    Args:
        alert_id: Alert identifier
        db: Database session
    
    Returns:
        Alert details
    """
    query = """
        SELECT 
            alert_id,
            alert_type,
            customer_key,
            severity,
            alert_source,
            alert_message,
            triggered_at,
            status,
            acknowledged_at,
            acknowledged_by,
            context_data
        FROM fact_alerts
        WHERE alert_id = :alert_id
    """
    
    result = db.execute(query, {'alert_id': alert_id}).fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return AlertResponse(
        alert_id=result.alert_id,
        alert_type=result.alert_type,
        customer_key=result.customer_key,
        severity=result.severity,
        alert_source=result.alert_source,
        alert_message=result.alert_message,
        triggered_at=result.triggered_at,
        status=result.status,
        context_data=result.context_data or {}
    )


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    acknowledged_by: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(Permission.ALERTS_ACKNOWLEDGE))
):
    """Acknowledge an alert.
    
    Args:
        alert_id: Alert identifier
        acknowledged_by: User acknowledging the alert
        db: Database session
    
    Returns:
        Success message
    """
    query = """
        UPDATE fact_alerts
        SET status = 'acknowledged',
            acknowledged_at = :acknowledged_at,
            acknowledged_by = :acknowledged_by
        WHERE alert_id = :alert_id
    """
    
    result = db.execute(query, {
        'alert_id': alert_id,
        'acknowledged_at': datetime.now(timezone.utc).replace(tzinfo=None),
        'acknowledged_by': acknowledged_by
    })
    
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    db.commit()
    
    return {"message": "Alert acknowledged successfully"}


@router.get("/risk/{customer_key}", response_model=RiskScoreResponse)
async def get_realtime_risk(
    customer_key: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(Permission.RISK_READ))
):
    """Get real-time risk score for a customer.

    Args:
        customer_key: Customer identifier
        db: Database session

    Returns:
        Risk score information
    """
    # Query dim_customer for realtime risk fields
    query = """
        SELECT
            customer_key,
            realtime_risk_level,
            realtime_risk_score,
            last_realtime_event_time
        FROM dim_customer
        WHERE customer_key = :customer_key
    """

    result = db.execute(query, {'customer_key': customer_key}).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Customer not found")

    return RiskScoreResponse(
        customer_key=result.customer_key,
        risk_level=result.realtime_risk_level or "unknown",
        risk_score=float(result.realtime_risk_score or 0.0),
        updated_at=result.last_realtime_event_time or datetime.now(timezone.utc).replace(tzinfo=None)
    )


@router.get("/risk/{customer_key}/mock", response_model=RiskScoreResponse)
async def get_mock_risk(customer_key: str):
    """Get mock real-time risk score for development.

    Args:
        customer_key: Customer identifier

    Returns:
        Mock risk score information
    """
    risk_levels = ["low", "medium", "high", "critical"]

    return RiskScoreResponse(
        customer_key=customer_key,
        risk_level=random.choice(risk_levels),
        risk_score=random.uniform(0, 1),
        updated_at=datetime.now()
    )


@router.get("/watchlist", response_model=List[WatchlistResponse])
async def get_watchlist(
    limit: int = Query(100, ge=1, le=1000, description="Maximum results"),
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(Permission.RISK_READ))
):
    """Get customers on watchlist.

    Args:
        limit: Maximum number of results
        db: Database session

    Returns:
        List of watchlist customers
    """
    query = """
        SELECT
            customer_key,
            on_watchlist,
            realtime_risk_level as warning_level,
            realtime_risk_score as warning_score,
            last_realtime_event_time as updated_at
        FROM dim_customer
        WHERE on_watchlist = true
        ORDER BY realtime_risk_score DESC
        LIMIT :limit
    """

    result = db.execute(query, {'limit': limit})

    watchlist = []
    for row in result:
        watchlist.append(WatchlistResponse(
            customer_key=row.customer_key,
            on_watchlist=row.on_watchlist,
            warning_level=row.warning_level,
            warning_score=float(row.warning_score or 0.0) if row.warning_score else None,
            updated_at=row.updated_at or datetime.now(timezone.utc).replace(tzinfo=None)
        ))

    return watchlist


@router.get("/watchlist/mock", response_model=List[WatchlistResponse])
async def get_mock_watchlist(
    limit: int = Query(50, ge=1, le=100, description="Maximum results")
):
    """Get mock watchlist for development.

    Args:
        limit: Maximum number of results

    Returns:
        List of mock watchlist customers
    """
    warning_levels = ["low", "medium", "high", "critical"]

    watchlist = []
    for i in range(min(limit, 50)):
        watchlist.append(WatchlistResponse(
            customer_key=f"CUST_{random.randint(1, 1000):04d}",
            on_watchlist=True,
            warning_level=random.choice(warning_levels),
            warning_score=random.uniform(0.5, 1.0),
            updated_at=datetime.now()
        ))

    return watchlist


@router.get("/metrics", response_model=StreamingMetricsResponse)
async def get_streaming_metrics(
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(Permission.ANALYTICS_READ))
):
    """Get streaming metrics.

    Args:
        db: Database session

    Returns:
        Streaming metrics
    """
    # Calculate metrics from fact tables
    # Events processed in last hour
    events_query = """
        SELECT COUNT(*) as count
        FROM fact_realtime_events
        WHERE processing_timestamp >= NOW() - INTERVAL '1 hour'
    """
    events_result = db.execute(events_query).fetchone()
    events_processed = events_result.count if events_result else 0

    # Alerts generated in last hour
    alerts_query = """
        SELECT COUNT(*) as count
        FROM fact_alerts
        WHERE triggered_at >= NOW() - INTERVAL '1 hour'
    """
    alerts_result = db.execute(alerts_query).fetchone()
    alerts_generated = alerts_result.count if alerts_result else 0

    # Anomalies detected in last hour
    anomalies_query = """
        SELECT COUNT(*) as count
        FROM fact_streaming_anomalies
        WHERE detected_at >= NOW() - INTERVAL '1 hour'
    """
    anomalies_result = db.execute(anomalies_query).fetchone()
    anomalies_detected = anomalies_result.count if anomalies_result else 0

    # Risk events in last hour
    risk_query = """
        SELECT COUNT(*) as count
        FROM fact_risk_events
        WHERE triggered_at >= NOW() - INTERVAL '1 hour'
    """
    risk_result = db.execute(risk_query).fetchone()
    risk_events = risk_result.count if risk_result else 0

    # Average processing latency
    latency_query = """
        SELECT AVG(processing_timestamp - event_timestamp) as avg_latency
        FROM fact_realtime_events
        WHERE processing_timestamp >= NOW() - INTERVAL '1 hour'
        AND processing_timestamp IS NOT NULL
        AND event_timestamp IS NOT NULL
    """
    latency_result = db.execute(latency_query).fetchone()
    processing_latency_ms = (
        float(latency_result.avg_latency.total_seconds() * 1000)
        if latency_result and latency_result.avg_latency
        else 0.0
    )

    # Calculate events per second
    events_per_second = events_processed / 3600.0

    # Uptime (simplified - assumes 100% for now)
    uptime_percentage = 100.0

    return StreamingMetricsResponse(
        events_processed=events_processed,
        events_per_second=events_per_second,
        alerts_generated=alerts_generated,
        anomalies_detected=anomalies_detected,
        risk_events=risk_events,
        processing_latency_ms=processing_latency_ms,
        uptime_percentage=uptime_percentage
    )


@router.get("/metrics/mock", response_model=StreamingMetricsResponse)
async def get_mock_metrics():
    """Get mock streaming metrics for development.

    Returns:
        Mock streaming metrics
    """
    return StreamingMetricsResponse(
        events_processed=random.randint(1000, 10000),
        events_per_second=random.uniform(10, 100),
        alerts_generated=random.randint(0, 20),
        anomalies_detected=random.randint(0, 10),
        risk_events=random.randint(0, 15),
        processing_latency_ms=random.uniform(10, 100),
        uptime_percentage=random.uniform(95, 100)
    )


@router.get("/decisions/{customer_key}")
async def get_customer_decisions(
    customer_key: str,
    decision_type: Optional[str] = Query(None, description="Filter by decision type"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results"),
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(Permission.AUDIT_READ))
):
    """Get decision audit trail for a customer.
    
    Args:
        customer_key: Customer identifier
        decision_type: Filter by decision type (alert, risk_score, early_warning)
        limit: Maximum number of results
        db: Database session
    
    Returns:
        List of decision records
    """
    query = """
        SELECT 
            decision_id,
            event_id,
            decision_type,
            decision_timestamp,
            model_version,
            feature_version,
            anomaly_score,
            risk_score,
            threshold,
            decision_outcome,
            reason_codes,
            processing_latency_ms
        FROM fact_decision_audit
        WHERE customer_key = :customer_key
    """
    
    params = {'customer_key': customer_key}
    
    if decision_type:
        query += " AND decision_type = :decision_type"
        params['decision_type'] = decision_type
    
    query += " ORDER BY decision_timestamp DESC LIMIT :limit"
    params['limit'] = limit
    
    result = db.execute(query, params)
    
    decisions = []
    for row in result:
        decisions.append({
            'decision_id': row.decision_id,
            'event_id': row.event_id,
            'decision_type': row.decision_type,
            'decision_timestamp': row.decision_timestamp,
            'model_version': row.model_version,
            'feature_version': row.feature_version,
            'anomaly_score': float(row.anomaly_score) if row.anomaly_score else None,
            'risk_score': float(row.risk_score) if row.risk_score else None,
            'threshold': float(row.threshold) if row.threshold else None,
            'decision_outcome': row.decision_outcome,
            'reason_codes': row.reason_codes,
            'processing_latency_ms': row.processing_latency_ms
        })
    
    return decisions
