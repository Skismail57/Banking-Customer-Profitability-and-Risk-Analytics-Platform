"""Decision audit trail for regulatory compliance.

This module provides decision audit trail capabilities for the banking analytics
platform, tracking all decisions for regulatory compliance and explainability.

Assumptions:
- Every decision (alert, risk score, recommendation) must be auditable
- Feature snapshots are stored in Redis for reference
- Audit records are stored in PostgreSQL for long-term retention

Limitations:
- Audit trail storage may grow large (requires partitioning)
- Feature snapshots may be large (consider compression)
- No support for audit trail anonymization

Fairness Considerations:
- Audit trail should include demographic context for bias analysis
- Ensure audit data is used responsibly for fairness monitoring
- Provide audit access controls for privacy compliance
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from collections import defaultdict
import logging
import uuid
from dataclasses import dataclass

from src.streaming.config import StreamingConfig
from src.streaming.features.feature_store import FeatureStore

logger = logging.getLogger(__name__)


@dataclass
class DecisionRecord:
    """Decision audit record."""
    decision_id: str
    event_id: Optional[str]
    customer_key: Optional[str]
    decision_type: str  # alert, risk_score, recommendation
    decision_timestamp: datetime
    model_version: Optional[str]
    feature_version: Optional[str]
    feature_snapshot_id: Optional[str]
    feature_values: Optional[Dict[str, Any]]
    anomaly_score: Optional[float]
    risk_score: Optional[float]
    threshold: Optional[float]
    decision_outcome: Optional[str]
    reason_codes: Optional[list]
    processing_latency_ms: Optional[int]
    context_data: Dict[str, Any]


class DecisionAuditor:
    """Decision audit trail for regulatory compliance.
    
    This auditor tracks all decisions made by the streaming platform for
    regulatory compliance and explainability.
    
    Key Features:
    - Captures full decision context (features, model version, thresholds)
    - Stores feature snapshots for reproducibility
    - Tracks processing latency for performance monitoring
    - Provides query capability for audit investigations
    - Maintains 7-year retention for regulatory compliance
    """
    
    def __init__(
        self,
        config: StreamingConfig,
        feature_store: FeatureStore
    ):
        """Initialize decision auditor.
        
        Args:
            config: Streaming configuration
            feature_store: Redis feature store for snapshot management
        """
        self.config = config
        self.feature_store = feature_store
        
        # Snapshot key pattern
        self.SNAPSHOT_KEY_PATTERN = "feature_snapshot:{snapshot_id}"
    
    def record_decision(
        self,
        decision_type: str,
        event_id: Optional[str],
        customer_key: Optional[str],
        decision_timestamp: datetime,
        model_version: Optional[str] = None,
        feature_version: Optional[str] = None,
        feature_values: Optional[Dict[str, Any]] = None,
        anomaly_score: Optional[float] = None,
        risk_score: Optional[float] = None,
        threshold: Optional[float] = None,
        decision_outcome: Optional[str] = None,
        reason_codes: Optional[list] = None,
        processing_latency_ms: Optional[int] = None,
        context_data: Optional[Dict[str, Any]] = None
    ) -> DecisionRecord:
        """Record a decision in the audit trail.
        
        Args:
            decision_type: Type of decision (alert, risk_score, recommendation)
            event_id: Event identifier
            customer_key: Customer identifier
            decision_timestamp: When the decision was made
            model_version: Model version used
            feature_version: Feature version used
            feature_values: Feature values used for decision
            anomaly_score: Anomaly score (if applicable)
            risk_score: Risk score (if applicable)
            threshold: Threshold used for decision
            decision_outcome: Outcome of decision
            reason_codes: Reason codes for decision
            processing_latency_ms: Processing latency in milliseconds
            context_data: Additional context
        
        Returns:
            DecisionRecord
        """
        logger.debug(
            f"Recording decision {decision_type} for customer {customer_key}, "
            f"event {event_id}"
        )
        
        # Generate decision ID
        decision_id = str(uuid.uuid4())
        
        # Create feature snapshot if values provided
        feature_snapshot_id = None
        if feature_values:
            feature_snapshot_id = self._create_feature_snapshot(
                decision_id, feature_values
            )
        
        # Create decision record
        record = DecisionRecord(
            decision_id=decision_id,
            event_id=event_id,
            customer_key=customer_key,
            decision_type=decision_type,
            decision_timestamp=decision_timestamp,
            model_version=model_version,
            feature_version=feature_version,
            feature_snapshot_id=feature_snapshot_id,
            feature_values=feature_values,
            anomaly_score=anomaly_score,
            risk_score=risk_score,
            threshold=threshold,
            decision_outcome=decision_outcome,
            reason_codes=reason_codes,
            processing_latency_ms=processing_latency_ms,
            context_data=context_data or {}
        )
        
        # Store in Redis for immediate access
        self._store_decision_record(record)
        
        # Note: In production, this would also write to PostgreSQL
        # for long-term retention (fact_decision_audit table)
        # This is handled by a separate persistence layer
        
        return record
    
    def record_alert_decision(
        self,
        alert: Dict[str, Any],
        event_id: Optional[str],
        processing_latency_ms: Optional[int] = None
    ) -> DecisionRecord:
        """Record an alert decision.
        
        Args:
            alert: Alert dictionary from AlertEngine
            event_id: Event identifier
            processing_latency_ms: Processing latency
        
        Returns:
            DecisionRecord
        """
        return self.record_decision(
            decision_type="alert",
            event_id=event_id,
            customer_key=alert.get('customer_key'),
            decision_timestamp=datetime.utcnow(),
            model_version=None,
            feature_version=None,
            feature_values=alert.get('context_data', {}).get('features'),
            anomaly_score=alert.get('context_data', {}).get('anomaly_score'),
            risk_score=alert.get('context_data', {}).get('risk_score'),
            threshold=None,
            decision_outcome=alert.get('alert_type'),
            reason_codes=[alert.get('alert_source')],
            processing_latency_ms=processing_latency_ms,
            context_data={
                'alert_id': alert.get('alert_id'),
                'severity': alert.get('severity'),
                'alert_message': alert.get('alert_message')
            }
        )
    
    def record_risk_decision(
        self,
        risk_event: Dict[str, Any],
        event_id: str,
        processing_latency_ms: Optional[int] = None
    ) -> DecisionRecord:
        """Record a risk scoring decision.
        
        Args:
            risk_event: Risk event dictionary from RealTimeRiskEngine
            event_id: Event identifier
            processing_latency_ms: Processing latency
        
        Returns:
            DecisionRecord
        """
        return self.record_decision(
            decision_type="risk_score",
            event_id=event_id,
            customer_key=risk_event.get('customer_key'),
            decision_timestamp=datetime.utcnow(),
            model_version=None,  # Would be set if using ML model
            feature_version=None,
            feature_values=risk_event.get('context_data', {}).get('features'),
            anomaly_score=None,
            risk_score=risk_event.get('risk_score'),
            threshold=None,
            decision_outcome=risk_event.get('risk_level'),
            reason_codes=[risk_event.get('threshold_violated')],
            processing_latency_ms=processing_latency_ms,
            context_data={
                'risk_type': risk_event.get('risk_type'),
                'risk_event_id': risk_event.get('risk_event_id')
            }
        )
    
    def record_warning_decision(
        self,
        warning_signal: Dict[str, Any],
        event_id: str,
        processing_latency_ms: Optional[int] = None
    ) -> DecisionRecord:
        """Record an early warning decision.
        
        Args:
            warning_signal: Warning signal dictionary from StreamingWarningAdapter
            event_id: Event identifier
            processing_latency_ms: Processing latency
        
        Returns:
            DecisionRecord
        """
        return self.record_decision(
            decision_type="early_warning",
            event_id=event_id,
            customer_key=warning_signal.get('customer_key'),
            decision_timestamp=datetime.utcnow(),
            model_version=None,
            feature_version=None,
            feature_values=warning_signal.get('context_data', {}).get('features'),
            anomaly_score=None,
            risk_score=None,
            threshold=warning_signal.get('context_data', {}).get('threshold'),
            decision_outcome=warning_signal.get('warning_level'),
            reason_codes=[warning_signal.get('signal_type')],
            processing_latency_ms=processing_latency_ms,
            context_data={
                'warning_id': warning_signal.get('warning_id'),
                'signal_type': warning_signal.get('signal_type')
            }
        )
    
    def get_decision(
        self,
        decision_id: str
    ) -> Optional[DecisionRecord]:
        """Retrieve a decision record.
        
        Args:
            decision_id: Decision identifier
        
        Returns:
            DecisionRecord or None if not found
        """
        decision_key = f"decision:{decision_id}"
        decision_data = self.feature_store.redis_client.get(decision_key)
        
        if decision_data:
            import json
            decision_dict = json.loads(decision_data)
            return DecisionRecord(**decision_dict)
        
        return None
    
    def get_customer_decisions(
        self,
        customer_key: str,
        decision_type: Optional[str] = None,
        limit: int = 100
    ) -> list:
        """Get decisions for a customer.
        
        Args:
            customer_key: Customer identifier
            decision_type: Filter by decision type (optional)
            limit: Maximum number of decisions to return
        
        Returns:
            List of DecisionRecord dictionaries
        """
        # Get all decision keys for customer
        pattern = f"decision:*"
        decision_keys = self.feature_store.redis_client.keys(pattern)
        
        decisions = []
        for decision_key in decision_keys:
            decision_data = self.feature_store.redis_client.get(decision_key)
            if decision_data:
                import json
                decision_dict = json.loads(decision_data)
                
                # Filter by customer
                if decision_dict.get('customer_key') == customer_key:
                    # Filter by decision type if specified
                    if decision_type is None or decision_dict.get('decision_type') == decision_type:
                        decisions.append(decision_dict)
        
        # Sort by decision_timestamp (most recent first)
        decisions.sort(key=lambda x: x.get('decision_timestamp', ''), reverse=True)
        
        return decisions[:limit]
    
    def get_feature_snapshot(
        self,
        snapshot_id: str
    ) -> Optional[Dict[str, Any]]:
        """Retrieve a feature snapshot.
        
        Args:
            snapshot_id: Snapshot identifier
        
        Returns:
            Feature snapshot dictionary or None if not found
        """
        snapshot_key = self.SNAPSHOT_KEY_PATTERN.format(snapshot_id=snapshot_id)
        snapshot_data = self.feature_store.redis_client.get(snapshot_key)
        
        if snapshot_data:
            import json
            return json.loads(snapshot_data)
        
        return None
    
    def _create_feature_snapshot(
        self,
        decision_id: str,
        feature_values: Dict[str, Any]
    ) -> str:
        """Create a feature snapshot for reproducibility.
        
        Args:
            decision_id: Decision identifier
            feature_values: Feature values to snapshot
        
        Returns:
            Snapshot identifier
        """
        snapshot_id = f"{decision_id}_snapshot"
        
        snapshot = {
            'snapshot_id': snapshot_id,
            'decision_id': decision_id,
            'features': feature_values,
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Store in Redis with long TTL (7 years for regulatory)
        snapshot_key = self.SNAPSHOT_KEY_PATTERN.format(snapshot_id=snapshot_id)
        import json
        snapshot_json = json.dumps(snapshot)
        
        # 7 years in seconds
        regulatory_ttl = 7 * 365 * 24 * 60 * 60
        self.feature_store.redis_client.setex(snapshot_key, regulatory_ttl, snapshot_json)
        
        return snapshot_id
    
    def _store_decision_record(self, record: DecisionRecord):
        """Store decision record in Redis.
        
        Args:
            record: Decision record to store
        """
        decision_key = f"decision:{record.decision_id}"
        
        import json
        record_dict = {
            'decision_id': record.decision_id,
            'event_id': record.event_id,
            'customer_key': record.customer_key,
            'decision_type': record.decision_type,
            'decision_timestamp': record.decision_timestamp.isoformat(),
            'model_version': record.model_version,
            'feature_version': record.feature_version,
            'feature_snapshot_id': record.feature_snapshot_id,
            'feature_values': record.feature_values,
            'anomaly_score': record.anomaly_score,
            'risk_score': record.risk_score,
            'threshold': record.threshold,
            'decision_outcome': record.decision_outcome,
            'reason_codes': record.reason_codes,
            'processing_latency_ms': record.processing_latency_ms,
            'context_data': record.context_data
        }
        
        record_json = json.dumps(record_dict)
        
        # Store with TTL from config (shorter than snapshots)
        ttl = self.config.feature_store.ttl_seconds
        self.feature_store.redis_client.setex(decision_key, ttl, record_json)


class AuditQueryEngine:
    """Advanced query engine for audit trail analysis."""
    
    def __init__(self, feature_store: FeatureStore):
        """Initialize audit query engine.
        
        Args:
            feature_store: Redis feature store
        """
        self.feature_store = feature_store
    
    def query_decisions(
        self,
        filters: Dict[str, Any],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Query decisions with filters.
        
        Args:
            filters: Dictionary of field filters
            start_date: Start date for query
            end_date: End date for query
            limit: Maximum results
        
        Returns:
            List of decision records
        """
        # Get all decision keys
        pattern = f"decision:*"
        decision_keys = self.feature_store.redis_client.keys(pattern)
        
        results = []
        for decision_key in decision_keys:
            decision_data = self.feature_store.redis_client.get(decision_key)
            if decision_data:
                import json
                decision_dict = json.loads(decision_data)
                
                # Apply filters
                if self._matches_filters(decision_dict, filters):
                    # Apply date range
                    if self._matches_date_range(decision_dict, start_date, end_date):
                        results.append(decision_dict)
        
        # Sort by timestamp
        results.sort(key=lambda x: x.get('decision_timestamp', ''), reverse=True)
        
        return results[:limit]
    
    def _matches_filters(self, decision: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if decision matches filters.
        
        Args:
            decision: Decision dictionary
            filters: Filter criteria
        
        Returns:
            True if matches, False otherwise
        """
        for key, value in filters.items():
            if decision.get(key) != value:
                return False
        return True
    
    def _matches_date_range(
        self,
        decision: Dict[str, Any],
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> bool:
        """Check if decision matches date range.
        
        Args:
            decision: Decision dictionary
            start_date: Start date
            end_date: End date
        
        Returns:
            True if matches, False otherwise
        """
        if not start_date and not end_date:
            return True
        
        decision_time = datetime.fromisoformat(decision.get('decision_timestamp', ''))
        
        if start_date and decision_time < start_date:
            return False
        
        if end_date and decision_time > end_date:
            return False
        
        return True
    
    def aggregate_decisions(
        self,
        group_by: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, int]:
        """Aggregate decisions by field.
        
        Args:
            group_by: Field to group by
            start_date: Start date
            end_date: End date
        
        Returns:
            Dictionary of counts
        """
        decisions = self.query_decisions({}, start_date, end_date, limit=10000)
        
        counts = defaultdict(int)
        for decision in decisions:
            key = decision.get(group_by, 'unknown')
            counts[key] += 1
        
        return dict(counts)


class ComplianceReporter:
    """Generate compliance reports from audit trail."""
    
    def __init__(self, query_engine: AuditQueryEngine):
        """Initialize compliance reporter.
        
        Args:
            query_engine: Audit query engine
        """
        self.query_engine = query_engine
    
    def generate_decision_report(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate decision compliance report.
        
        Args:
            start_date: Report start date
            end_date: Report end date
        
        Returns:
            Compliance report
        """
        decisions = self.query_engine.query_decisions(
            {}, start_date, end_date, limit=10000
        )
        
        # Aggregate by decision type
        by_type = self.query_engine.aggregate_decisions(
            'decision_type', start_date, end_date
        )
        
        # Aggregate by customer
        by_customer = self.query_engine.aggregate_decisions(
            'customer_key', start_date, end_date
        )
        
        # Calculate statistics
        total_decisions = len(decisions)
        avg_latency = 0.0
        
        if decisions:
            latencies = [d.get('processing_latency_ms', 0) for d in decisions if d.get('processing_latency_ms')]
            if latencies:
                avg_latency = sum(latencies) / len(latencies)
        
        return {
            'report_period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'summary': {
                'total_decisions': total_decisions,
                'unique_customers': len(by_customer),
                'average_latency_ms': avg_latency
            },
            'by_decision_type': by_type,
            'top_customers': dict(sorted(by_customer.items(), key=lambda x: x[1], reverse=True)[:10])
        }
    
    def generate_fairness_report(
        self,
        start_date: datetime,
        end_date: datetime,
        demographic_field: str = None
    ) -> Dict[str, Any]:
        """Generate fairness analysis report.
        
        Args:
            start_date: Report start date
            end_date: Report end date
            demographic_field: Field to analyze for fairness
        
        Returns:
            Fairness report
        """
        decisions = self.query_engine.query_decisions(
            {}, start_date, end_date, limit=10000
        )
        
        # Aggregate by decision outcome
        by_outcome = defaultdict(list)
        for decision in decisions:
            outcome = decision.get('decision_outcome', 'unknown')
            by_outcome[outcome].append(decision)
        
        # Calculate outcome distribution
        outcome_distribution = {
            outcome: len(decisions_list)
            for outcome, decisions_list in by_outcome.items()
        }
        
        return {
            'report_period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'total_decisions': len(decisions),
            'outcome_distribution': outcome_distribution,
            'note': 'Demographic analysis requires additional context data'
        }
    
    def generate_model_performance_report(
        self,
        model_version: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate model performance report.
        
        Args:
            model_version: Model version to analyze
            start_date: Report start date
            end_date: Report end date
        
        Returns:
            Model performance report
        """
        decisions = self.query_engine.query_decisions(
            {'model_version': model_version}, start_date, end_date, limit=10000
        )
        
        # Calculate statistics
        total = len(decisions)
        risk_scores = [d.get('risk_score', 0) for d in decisions if d.get('risk_score') is not None]
        anomaly_scores = [d.get('anomaly_score', 0) for d in decisions if d.get('anomaly_score') is not None]
        
        return {
            'model_version': model_version,
            'report_period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'total_decisions': total,
            'risk_score_statistics': {
                'count': len(risk_scores),
                'average': sum(risk_scores) / len(risk_scores) if risk_scores else 0,
                'min': min(risk_scores) if risk_scores else 0,
                'max': max(risk_scores) if risk_scores else 0
            },
            'anomaly_score_statistics': {
                'count': len(anomaly_scores),
                'average': sum(anomaly_scores) / len(anomaly_scores) if anomaly_scores else 0,
                'min': min(anomaly_scores) if anomaly_scores else 0,
                'max': max(anomaly_scores) if anomaly_scores else 0
            }
        }
