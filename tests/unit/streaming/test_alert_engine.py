"""Unit tests for alert engine."""

import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock
from src.streaming.alerts.alert_engine import (
    AlertEngine,
    Alert,
    AlertSeverity,
    AlertStatus,
    AlertRouter,
    EmailChannel,
    SlackChannel,
    WebSocketChannel,
    AlertTemplate,
    AlertTemplateManager
)


@pytest.fixture
def mock_config():
    """Mock streaming config."""
    config = Mock()
    config.alerts.deduplication_window_seconds = 300
    config.feature_store.ttl_seconds = 3600
    return config


@pytest.fixture
def mock_feature_store():
    """Mock feature store."""
    store = Mock()
    store.redis_client = Mock()
    store.redis_client.exists = Mock(return_value=False)
    store.redis_client.setex = Mock()
    store.redis_client.get = Mock(return_value=None)
    return store


@pytest.fixture
def alert_engine(mock_config, mock_feature_store):
    """Alert engine fixture."""
    return AlertEngine(mock_config, mock_feature_store)


class TestAlertEngine:
    """Test AlertEngine class."""
    
    def test_generate_alert_from_risk(self, alert_engine):
        """Test alert generation from risk event."""
        risk_event = {
            'customer_key': 'CUST_001',
            'risk_type': 'credit',
            'risk_level': 'high',
            'threshold_violated': 'credit_score_threshold',
            'risk_score': 0.85
        }
        
        alert = alert_engine.generate_alert_from_risk(risk_event)
        
        assert alert is not None
        assert alert.alert_type == 'risk_credit'
        assert alert.customer_key == 'CUST_001'
        assert alert.severity == AlertSeverity.HIGH.value
        assert alert.alert_source == 'risk_engine'
    
    def test_alert_deduplication(self, alert_engine, mock_feature_store):
        """Test alert deduplication."""
        risk_event = {
            'customer_key': 'CUST_001',
            'risk_type': 'credit',
            'risk_level': 'high',
            'threshold_violated': 'credit_score_threshold'
        }
        
        # First alert should be generated
        alert1 = alert_engine.generate_alert_from_risk(risk_event)
        assert alert1 is not None
        
        # Mock dedup key exists
        mock_feature_store.redis_client.exists = Mock(return_value=True)
        
        # Second alert should be deduplicated
        alert2 = alert_engine.generate_alert_from_risk(risk_event)
        assert alert2 is None
    
    def test_generate_alert_from_anomaly(self, alert_engine):
        """Test alert generation from anomaly."""
        anomaly_result = {
            'customer_key': 'CUST_001',
            'anomaly_type': 'amount',
            'severity': 'high',
            'threshold_violated': 'amount_threshold',
            'anomaly_score': 0.95
        }
        
        alert = alert_engine.generate_alert_from_anomaly(anomaly_result)
        
        assert alert is not None
        assert alert.alert_type == 'anomaly_amount'
        assert alert.severity == 'high'
    
    def test_anomaly_below_threshold(self, alert_engine):
        """Test anomaly below alert threshold."""
        anomaly_result = {
            'customer_key': 'CUST_001',
            'anomaly_type': 'amount',
            'severity': 'low',  # Below threshold
            'threshold_violated': 'amount_threshold'
        }
        
        alert = alert_engine.generate_alert_from_anomaly(anomaly_result)
        assert alert is None


class TestAlertRouter:
    """Test AlertRouter class."""
    
    def test_add_channel(self):
        """Test adding alert channel."""
        router = AlertRouter()
        channel = EmailChannel({'smtp_host': 'localhost'})
        
        router.add_channel('email', channel)
        
        assert 'email' in router.channels
        assert router.channels['email'] == channel
    
    def test_add_routing_rule(self):
        """Test adding routing rule."""
        router = AlertRouter()
        
        def condition(alert):
            return alert.severity == 'critical'
        
        router.add_routing_rule(condition, ['email', 'slack'])
        
        assert len(router.routing_rules) == 1
        assert router.routing_rules[0]['channels'] == ['email', 'slack']
    
    def test_route_alert(self):
        """Test alert routing."""
        router = AlertRouter()
        
        # Add mock channel
        mock_channel = Mock()
        mock_channel.send = Mock(return_value=True)
        router.add_channel('email', mock_channel)
        
        # Add routing rule
        def condition(alert):
            return alert.severity == 'critical'
        
        router.add_routing_rule(condition, ['email'])
        
        # Route alert
        alert = Alert(
            alert_id='ALERT_001',
            alert_type='risk_credit',
            customer_key='CUST_001',
            severity='critical',
            alert_source='risk_engine',
            alert_message='Test alert',
            triggered_at=datetime.utcnow(),
            context_data={}
        )
        
        routed = router.route_alert(alert)
        
        assert 'email' in routed
        mock_channel.send.assert_called_once()


class TestAlertTemplate:
    """Test AlertTemplate class."""
    
    def test_render_template(self):
        """Test template rendering."""
        template = AlertTemplate(
            "Alert for customer {customer_key}: {message}"
        )
        
        context = {
            'customer_key': 'CUST_001',
            'message': 'High risk detected'
        }
        
        rendered = template.render(context)
        
        assert 'CUST_001' in rendered
        assert 'High risk detected' in rendered
    
    def test_render_missing_variable(self):
        """Test template with missing variable."""
        template = AlertTemplate(
            "Alert for customer {customer_key}: {missing_var}"
        )
        
        context = {'customer_key': 'CUST_001'}
        
        rendered = template.render(context)
        
        # Should return template string if variable missing
        assert rendered == template.template


class TestAlertTemplateManager:
    """Test AlertTemplateManager class."""
    
    def test_get_template(self):
        """Test getting template."""
        manager = AlertTemplateManager()
        
        template = manager.get_template('risk_credit')
        
        assert template is not None
        assert isinstance(template, AlertTemplate)
    
    def test_render_alert(self):
        """Test rendering alert with template."""
        manager = AlertTemplateManager()
        
        alert = Alert(
            alert_id='ALERT_001',
            alert_type='risk_credit',
            customer_key='CUST_001',
            severity='high',
            alert_source='risk_engine',
            alert_message='Test',
            triggered_at=datetime.utcnow(),
            context_data={
                'risk_level': 'high',
                'threshold_violated': 'credit_score',
                'risk_score': 0.85
            }
        )
        
        rendered = manager.render_alert(alert)
        
        assert 'CUST_001' in rendered
        assert 'high' in rendered
    
    def test_add_custom_template(self):
        """Test adding custom template."""
        manager = AlertTemplateManager()
        
        custom_template = AlertTemplate("Custom: {message}")
        manager.add_template('custom_type', custom_template)
        
        retrieved = manager.get_template('custom_type')
        
        assert retrieved == custom_template
