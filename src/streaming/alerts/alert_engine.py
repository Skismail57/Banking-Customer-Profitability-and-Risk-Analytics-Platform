"""Real-time alert generation engine.

This module provides real-time alert generation capabilities for the banking analytics
platform, generating alerts from risk, anomaly, and warning signals.

Assumptions:
- Alerts are generated from risk events, anomaly results, and warning signals
- Alert deduplication is based on customer, type, and time window
- Alert severity is derived from source signal severity

Limitations:
- Alert fatigue may occur if too many alerts are generated
- Deduplication window may need tuning per alert type
- No support for alert escalation or auto-resolution

Fairness Considerations:
- Alert thresholds should be calibrated per customer segment to avoid bias
- Monitor alert rates across customer segments for fairness
- Provide context for alerts to avoid stereotyping
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable
from abc import ABC, abstractmethod
import logging
import uuid
from dataclasses import dataclass
from enum import Enum

from src.streaming.config import StreamingConfig
from src.streaming.features.feature_store import FeatureStore

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Alert status values."""
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    CLOSED = "closed"


@dataclass
class Alert:
    """Real-time alert."""
    alert_id: str
    alert_type: str
    customer_key: Optional[str]
    severity: str
    alert_source: str
    alert_message: str
    triggered_at: datetime
    context_data: Dict[str, Any]
    status: str = AlertStatus.OPEN.value
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None


class AlertEngine:
    """Real-time alert generation engine.
    
    This engine generates alerts from risk events, anomaly results, and warning signals.
    It provides deduplication, aggregation, and severity classification.
    
    Key Features:
    - Generates alerts from multiple sources (risk, anomaly, warning)
    - Deduplicates alerts within time window
    - Classifies severity based on source signal
    - Maintains alert history in Redis
    - Supports alert acknowledgment and resolution
    """
    
    def __init__(
        self,
        config: StreamingConfig,
        feature_store: FeatureStore
    ):
        """Initialize alert engine.
        
        Args:
            config: Streaming configuration
            feature_store: Redis feature store for state persistence
        """
        self.config = config
        self.feature_store = feature_store
        
        # Deduplication key pattern
        self.DEDUP_KEY_PATTERN = "alert_dedup:{customer_key}:{alert_type}"
    
    def generate_alert_from_risk(
        self,
        risk_event: Dict[str, Any]
    ) -> Optional[Alert]:
        """Generate alert from risk event.
        
        Args:
            risk_event: Risk event dictionary from RealTimeRiskEngine
        
        Returns:
            Alert if alert should be generated, None if deduplicated
        """
        logger.debug(f"Generating alert from risk event for customer {risk_event.get('customer_key')}")
        
        # Check deduplication
        if self._is_deduplicated(
            risk_event.get('customer_key'),
            'risk',
            risk_event.get('risk_type')
        ):
            logger.debug(f"Risk alert deduplicated for customer {risk_event.get('customer_key')}")
            return None
        
        # Map risk level to alert severity
        severity = self._map_risk_to_severity(risk_event.get('risk_level'))
        
        # Generate alert message
        alert_message = self._generate_risk_alert_message(risk_event)
        
        # Create alert
        alert = Alert(
            alert_id=str(uuid.uuid4()),
            alert_type=f"risk_{risk_event.get('risk_type')}",
            customer_key=risk_event.get('customer_key'),
            severity=severity,
            alert_source="risk_engine",
            alert_message=alert_message,
            triggered_at=datetime.utcnow(),
            context_data=risk_event
        )
        
        # Store deduplication key
        self._store_dedup_key(
            risk_event.get('customer_key'),
            'risk',
            risk_event.get('risk_type')
        )
        
        return alert
    
    def generate_alert_from_anomaly(
        self,
        anomaly_result: Dict[str, Any]
    ) -> Optional[Alert]:
        """Generate alert from anomaly result.
        
        Args:
            anomaly_result: Anomaly result dictionary from StreamingAnomalyAdapter
        
        Returns:
            Alert if alert should be generated, None if deduplicated
        """
        logger.debug(f"Generating alert from anomaly for customer {anomaly_result.get('customer_key')}")
        
        # Only generate alerts for high/critical anomalies
        severity = anomaly_result.get('severity')
        if severity not in ['high', 'critical']:
            logger.debug(f"Anomaly severity {severity} below alert threshold")
            return None
        
        # Check deduplication
        if self._is_deduplicated(
            anomaly_result.get('customer_key'),
            'anomaly',
            anomaly_result.get('anomaly_type')
        ):
            logger.debug(f"Anomaly alert deduplicated for customer {anomaly_result.get('customer_key')}")
            return None
        
        # Generate alert message
        alert_message = self._generate_anomaly_alert_message(anomaly_result)
        
        # Create alert
        alert = Alert(
            alert_id=str(uuid.uuid4()),
            alert_type=f"anomaly_{anomaly_result.get('anomaly_type')}",
            customer_key=anomaly_result.get('customer_key'),
            severity=severity,
            alert_source="anomaly_detector",
            alert_message=alert_message,
            triggered_at=datetime.utcnow(),
            context_data=anomaly_result
        )
        
        # Store deduplication key
        self._store_dedup_key(
            anomaly_result.get('customer_key'),
            'anomaly',
            anomaly_result.get('anomaly_type')
        )
        
        return alert
    
    def generate_alert_from_warning(
        self,
        warning_signal: Dict[str, Any]
    ) -> Optional[Alert]:
        """Generate alert from warning signal.
        
        Args:
            warning_signal: Warning signal dictionary from StreamingWarningAdapter
        
        Returns:
            Alert if alert should be generated, None if deduplicated
        """
        logger.debug(f"Generating alert from warning for customer {warning_signal.get('customer_key')}")
        
        # Only generate alerts for high/critical warnings
        warning_level = warning_signal.get('warning_level')
        if warning_level not in ['high', 'critical']:
            logger.debug(f"Warning level {warning_level} below alert threshold")
            return None
        
        # Check deduplication
        if self._is_deduplicated(
            warning_signal.get('customer_key'),
            'warning',
            warning_signal.get('signal_type')
        ):
            logger.debug(f"Warning alert deduplicated for customer {warning_signal.get('customer_key')}")
            return None
        
        # Map warning level to alert severity
        severity = self._map_warning_to_severity(warning_level)
        
        # Generate alert message
        alert_message = self._generate_warning_alert_message(warning_signal)
        
        # Create alert
        alert = Alert(
            alert_id=str(uuid.uuid4()),
            alert_type=f"warning_{warning_signal.get('signal_type')}",
            customer_key=warning_signal.get('customer_key'),
            severity=severity,
            alert_source="early_warning",
            alert_message=alert_message,
            triggered_at=datetime.utcnow(),
            context_data=warning_signal
        )
        
        # Store deduplication key
        self._store_dedup_key(
            warning_signal.get('customer_key'),
            'warning',
            warning_signal.get('signal_type')
        )
        
        return alert
    
    def acknowledge_alert(
        self,
        alert_id: str,
        acknowledged_by: str
    ) -> bool:
        """Acknowledge an alert.
        
        Args:
            alert_id: Alert identifier
            acknowledged_by: User who acknowledged
        
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Acknowledging alert {alert_id} by {acknowledged_by}")
        
        # Update alert in Redis
        alert_key = f"alert:{alert_id}"
        alert_data = self.feature_store.redis_client.get(alert_key)
        
        if alert_data:
            import json
            alert_dict = json.loads(alert_data)
            alert_dict['status'] = AlertStatus.ACKNOWLEDGED.value
            alert_dict['acknowledged_at'] = datetime.utcnow().isoformat()
            alert_dict['acknowledged_by'] = acknowledged_by
            
            self.feature_store.redis_client.setex(
                alert_key,
                self.config.feature_store.ttl_seconds,
                json.dumps(alert_dict)
            )
            return True
        
        return False
    
    def resolve_alert(
        self,
        alert_id: str
    ) -> bool:
        """Resolve an alert.
        
        Args:
            alert_id: Alert identifier
        
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Resolving alert {alert_id}")
        
        # Update alert in Redis
        alert_key = f"alert:{alert_id}"
        alert_data = self.feature_store.redis_client.get(alert_key)
        
        if alert_data:
            import json
            alert_dict = json.loads(alert_data)
            alert_dict['status'] = AlertStatus.RESOLVED.value
            
            self.feature_store.redis_client.setex(
                alert_key,
                self.config.feature_store.ttl_seconds,
                json.dumps(alert_dict)
            )
            return True
        
        return False
    
    def get_customer_alerts(
        self,
        customer_key: str,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get alerts for a customer.
        
        Args:
            customer_key: Customer identifier
            status: Filter by status (optional)
            limit: Maximum number of alerts to return
        
        Returns:
            List of alert dictionaries
        """
        # Get all alert keys for customer
        pattern = f"alert:*"
        alert_keys = self.feature_store.redis_client.keys(pattern)
        
        alerts = []
        for alert_key in alert_keys:
            alert_data = self.feature_store.redis_client.get(alert_key)
            if alert_data:
                import json
                alert_dict = json.loads(alert_data)
                
                # Filter by customer
                if alert_dict.get('customer_key') == customer_key:
                    # Filter by status if specified
                    if status is None or alert_dict.get('status') == status:
                        alerts.append(alert_dict)
        
        # Sort by triggered_at (most recent first)
        alerts.sort(key=lambda x: x.get('triggered_at', ''), reverse=True)
        
        return alerts[:limit]
    
    def _is_deduplicated(
        self,
        customer_key: Optional[str],
        source: str,
        alert_type: str
    ) -> bool:
        """Check if alert should be deduplicated.
        
        Args:
            customer_key: Customer identifier
            source: Alert source (risk, anomaly, warning)
            alert_type: Alert type
        
        Returns:
            True if deduplicated, False otherwise
        """
        if customer_key is None:
            return False
        
        dedup_key = self.DEDUP_KEY_PATTERN.format(
            customer_key=customer_key,
            alert_type=f"{source}_{alert_type}"
        )
        
        # Check if dedup key exists
        exists = self.feature_store.redis_client.exists(dedup_key)
        
        return bool(exists)
    
    def _store_dedup_key(
        self,
        customer_key: Optional[str],
        source: str,
        alert_type: str
    ):
        """Store deduplication key.
        
        Args:
            customer_key: Customer identifier
            source: Alert source
            alert_type: Alert type
        """
        if customer_key is None:
            return
        
        dedup_key = self.DEDUP_KEY_PATTERN.format(
            customer_key=customer_key,
            alert_type=f"{source}_{alert_type}"
        )
        
        # Store with deduplication window from config
        dedup_window = self.config.alerts.deduplication_window_seconds
        self.feature_store.redis_client.setex(dedup_key, dedup_window, "1")
    
    def _map_risk_to_severity(self, risk_level: str) -> str:
        """Map risk level to alert severity.
        
        Args:
            risk_level: Risk level (low, medium, high, critical)
        
        Returns:
            Alert severity
        """
        mapping = {
            'low': AlertSeverity.LOW.value,
            'medium': AlertSeverity.MEDIUM.value,
            'high': AlertSeverity.HIGH.value,
            'critical': AlertSeverity.CRITICAL.value
        }
        return mapping.get(risk_level, AlertSeverity.MEDIUM.value)
    
    def _map_warning_to_severity(self, warning_level: str) -> str:
        """Map warning level to alert severity.
        
        Args:
            warning_level: Warning level (low, medium, high, critical)
        
        Returns:
            Alert severity
        """
        mapping = {
            'low': AlertSeverity.LOW.value,
            'medium': AlertSeverity.MEDIUM.value,
            'high': AlertSeverity.HIGH.value,
            'critical': AlertSeverity.CRITICAL.value
        }
        return mapping.get(warning_level, AlertSeverity.MEDIUM.value)
    
    def _generate_risk_alert_message(self, risk_event: Dict[str, Any]) -> str:
        """Generate alert message for risk event.
        
        Args:
            risk_event: Risk event dictionary
        
        Returns:
            Alert message
        """
        risk_type = risk_event.get('risk_type', 'unknown')
        risk_level = risk_event.get('risk_level', 'unknown')
        threshold_violated = risk_event.get('threshold_violated', 'multiple thresholds')
        
        return (
            f"Risk Alert: {risk_type.upper()} risk level {risk_level.upper()} detected. "
            f"Threshold violated: {threshold_violated}."
        )
    
    def _generate_anomaly_alert_message(self, anomaly_result: Dict[str, Any]) -> str:
        """Generate alert message for anomaly result.
        
        Args:
            anomaly_result: Anomaly result dictionary
        
        Returns:
            Alert message
        """
        anomaly_type = anomaly_result.get('anomaly_type', 'unknown')
        severity = anomaly_result.get('severity', 'unknown')
        threshold_violated = anomaly_result.get('threshold_violated', 'threshold')
        
        return (
            f"Anomaly Alert: {anomaly_type} anomaly detected with {severity.upper()} severity. "
            f"Threshold violated: {threshold_violated}."
        )
    
    def _generate_warning_alert_message(self, warning_signal: Dict[str, Any]) -> str:
        """Generate alert message for warning signal.
        
        Args:
            warning_signal: Warning signal dictionary
        
        Returns:
            Alert message
        """
        signal_type = warning_signal.get('signal_type', 'unknown')
        warning_level = warning_signal.get('warning_level', 'unknown')
        threshold_violated = warning_signal.get('threshold_violated', 'threshold')
        
        return (
            f"Early Warning Alert: {signal_type} warning with {warning_level.upper()} level. "
            f"Threshold violated: {threshold_violated}."
        )


class AlertChannel(ABC):
    """Abstract base class for alert channels."""
    
    @abstractmethod
    def send(self, alert: Alert) -> bool:
        """Send alert through this channel.
        
        Args:
            alert: Alert to send
        
        Returns:
            True if sent successfully, False otherwise
        """
        pass


class EmailChannel(AlertChannel):
    """Email alert channel."""
    
    def __init__(self, smtp_config: Dict[str, Any]):
        """Initialize email channel.
        
        Args:
            smtp_config: SMTP configuration
        """
        self.smtp_config = smtp_config
    
    def send(self, alert: Alert) -> bool:
        """Send alert via email.
        
        Args:
            alert: Alert to send
        
        Returns:
            True if sent successfully, False otherwise
        """
        logger.info(f"Sending email alert {alert.alert_id} to {alert.customer_key}")
        # Implementation would use SMTP to send email
        return True


class SlackChannel(AlertChannel):
    """Slack alert channel."""
    
    def __init__(self, webhook_url: str):
        """Initialize Slack channel.
        
        Args:
            webhook_url: Slack webhook URL
        """
        self.webhook_url = webhook_url
    
    def send(self, alert: Alert) -> bool:
        """Send alert via Slack webhook.
        
        Args:
            alert: Alert to send
        
        Returns:
            True if sent successfully, False otherwise
        """
        logger.info(f"Sending Slack alert {alert.alert_id}")
        # Implementation would send to Slack webhook
        return True


class WebSocketChannel(AlertChannel):
    """WebSocket alert channel for real-time UI updates."""
    
    def __init__(self, websocket_manager):
        """Initialize WebSocket channel.
        
        Args:
            websocket_manager: WebSocket connection manager
        """
        self.websocket_manager = websocket_manager
    
    def send(self, alert: Alert) -> bool:
        """Send alert via WebSocket.
        
        Args:
            alert: Alert to send
        
        Returns:
            True if sent successfully, False otherwise
        """
        logger.info(f"Sending WebSocket alert {alert.alert_id}")
        # Implementation would broadcast via WebSocket
        return True


class AlertRouter:
    """Route alerts to appropriate channels based on rules."""
    
    def __init__(self):
        """Initialize alert router."""
        self.routing_rules = []
        self.channels: Dict[str, AlertChannel] = {}
    
    def add_channel(self, name: str, channel: AlertChannel):
        """Add an alert channel.
        
        Args:
            name: Channel name
            channel: Channel instance
        """
        self.channels[name] = channel
    
    def add_routing_rule(
        self,
        condition: Callable[[Alert], bool],
        channels: List[str]
    ):
        """Add a routing rule.
        
        Args:
            condition: Function that returns True if rule matches
            channels: List of channel names to route to
        """
        self.routing_rules.append({
            'condition': condition,
            'channels': channels
        })
    
    def route_alert(self, alert: Alert) -> List[str]:
        """Route alert to appropriate channels.
        
        Args:
            alert: Alert to route
        
        Returns:
            List of channel names alert was sent to
        """
        routed_channels = []
        
        for rule in self.routing_rules:
            if rule['condition'](alert):
                for channel_name in rule['channels']:
                    if channel_name in self.channels:
                        self.channels[channel_name].send(alert)
                        routed_channels.append(channel_name)
        
        return routed_channels


class AlertTemplate:
    """Alert message template with variable substitution."""
    
    def __init__(self, template: str):
        """Initialize alert template.
        
        Args:
            template: Template string with {variable} placeholders
        """
        self.template = template
    
    def render(self, context: Dict[str, Any]) -> str:
        """Render template with context.
        
        Args:
            context: Dictionary of variable values
        
        Returns:
            Rendered message
        """
        try:
            return self.template.format(**context)
        except KeyError as e:
            logger.warning(f"Template variable missing: {e}")
            return self.template


class AlertTemplateManager:
    """Manage alert templates for different alert types."""
    
    def __init__(self):
        """Initialize template manager."""
        self.templates: Dict[str, AlertTemplate] = {}
        self._load_default_templates()
    
    def _load_default_templates(self):
        """Load default alert templates."""
        self.templates = {
            'risk_credit': AlertTemplate(
                "Risk Alert: Credit risk level {risk_level} detected for customer {customer_key}. "
                "Threshold violated: {threshold_violated}. Risk score: {risk_score:.2f}"
            ),
            'risk_payment': AlertTemplate(
                "Risk Alert: Payment risk level {risk_level} detected for customer {customer_key}. "
                "DPD: {dpd} days, Payment score: {payment_history_score:.2f}"
            ),
            'risk_concentration': AlertTemplate(
                "Risk Alert: Concentration risk level {risk_level} detected for customer {customer_key}. "
                "Concentration ratio: {concentration_ratio:.2%}"
            ),
            'anomaly_amount': AlertTemplate(
                "Anomaly Alert: Amount anomaly detected for customer {customer_key}. "
                "Amount: {amount}, Method: {method}, Severity: {severity}"
            ),
            'anomaly_velocity': AlertTemplate(
                "Anomaly Alert: Velocity anomaly detected for customer {customer_key}. "
                "{transaction_count} transactions in {window_minutes} minutes"
            ),
            'warning_utilization': AlertTemplate(
                "Early Warning: Credit utilization increased by {change:.2%} for customer {customer_key}. "
                "Current: {current_utilization:.2%}, Previous: {previous_utilization:.2%}"
            ),
            'warning_payment': AlertTemplate(
                "Early Warning: Payment rate declined by {decline:.2%} for customer {customer_key}. "
                "Current: {current_payment_rate:.2%}, Previous: {previous_payment_rate:.2%}"
            )
        }
    
    def get_template(self, alert_type: str) -> Optional[AlertTemplate]:
        """Get template for alert type.
        
        Args:
            alert_type: Alert type
        
        Returns:
            AlertTemplate or None if not found
        """
        return self.templates.get(alert_type)
    
    def add_template(self, alert_type: str, template: AlertTemplate):
        """Add a custom template.
        
        Args:
            alert_type: Alert type
            template: AlertTemplate instance
        """
        self.templates[alert_type] = template
    
    def render_alert(self, alert: Alert) -> str:
        """Render alert message using template.
        
        Args:
            alert: Alert to render
        
        Returns:
            Rendered message
        """
        template = self.get_template(alert.alert_type)
        
        if template:
            context = {
                'customer_key': alert.customer_key,
                'severity': alert.severity,
                'alert_type': alert.alert_type,
                **alert.context_data
            }
            return template.render(context)
        
        # Fallback to default message
        return alert.alert_message
