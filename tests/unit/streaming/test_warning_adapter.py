"""Unit tests for early warning adapter."""

import pytest
from datetime import datetime, timezone
from unittest.mock import Mock
from src.streaming.early_warning.warning_adapter import (
    StreamingWarningAdapter,
    LeadingIndicators,
    WarningEscalation
)


@pytest.fixture
def mock_config():
    """Mock streaming config."""
    config = Mock()
    config.feature_store.ttl_seconds = 3600
    return config


@pytest.fixture
def mock_feature_store():
    """Mock feature store."""
    store = Mock()
    store.redis_client = Mock()
    store.redis_client.hget = Mock(return_value=None)
    store.redis_client.hset = Mock()
    store.redis_client.hgetall = Mock(return_value={})
    store.redis_client.keys = Mock(return_value=[])
    return store


@pytest.fixture
def warning_adapter(mock_config, mock_feature_store):
    """Warning adapter fixture."""
    return StreamingWarningAdapter(mock_config, mock_feature_store)


class TestStreamingWarningAdapter:
    """Test StreamingWarningAdapter class."""
    
    def test_detect_utilization_warning(self, warning_adapter):
        """Test utilization warning detection."""
        features = {
            'current_utilization': 0.85,
            'previous_utilization': 0.65,
            'customer_key': 'CUST_001'
        }
        
        signal = warning_adapter.detect_warning(
            customer_key='CUST_001',
            signal_type='utilization',
            features=features
        )
        
        assert signal is not None
        assert signal['customer_key'] == 'CUST_001'
        assert signal['signal_type'] == 'utilization'
        assert 'warning_level' in signal
    
    def test_detect_payment_warning(self, warning_adapter):
        """Test payment warning detection."""
        features = {
            'current_payment_rate': 0.75,
            'previous_payment_rate': 0.95,
            'customer_key': 'CUST_001'
        }
        
        signal = warning_adapter.detect_warning(
            customer_key='CUST_001',
            signal_type='payment',
            features=features
        )
        
        assert signal is not None
        assert signal['signal_type'] == 'payment'
    
    def test_detect_balance_warning(self, warning_adapter):
        """Test balance warning detection."""
        features = {
            'current_balance': 5000.0,
            'previous_balance': 10000.0,
            'customer_key': 'CUST_001'
        }
        
        signal = warning_adapter.detect_warning(
            customer_key='CUST_001',
            signal_type='balance',
            features=features
        )
        
        assert signal is not None
        assert signal['signal_type'] == 'balance'
    
    def test_warning_level_classification(self, warning_adapter):
        """Test warning level classification."""
        # Test low level
        low_level = warning_adapter._classify_warning_level(0.2)
        assert low_level == 'low'
        
        # Test high level
        high_level = warning_adapter._classify_warning_level(0.8)
        assert high_level == 'high'
        
        # Test critical level
        critical_level = warning_adapter._classify_warning_level(0.95)
        assert critical_level == 'critical'


class TestLeadingIndicators:
    """Test LeadingIndicators class."""
    
    def test_track_indicator(self):
        """Test tracking leading indicator."""
        indicators = LeadingIndicators(window_size=30)
        
        indicators.track_indicator(
            customer_key='CUST_001',
            indicator_type='utilization',
            value=0.75,
            timestamp=datetime.now(timezone.utc).replace(tzinfo=None)
        )
        
        history = indicators.get_indicator_history('CUST_001', 'utilization')
        assert len(history) > 0
    
    def test_calculate_trend(self):
        """Test trend calculation."""
        indicators = LeadingIndicators(window_size=30)
        
        # Add some data points
        for i in range(10):
            indicators.track_indicator(
                customer_key='CUST_001',
                indicator_type='utilization',
                value=0.5 + (i * 0.05),
                timestamp=datetime.now(timezone.utc).replace(tzinfo=None)
            )
        
        trend = indicators.calculate_trend('CUST_001', 'utilization')
        
        assert trend is not None
        assert 'trend_direction' in trend
        assert 'slope' in trend
    
    def test_detect_early_warning(self):
        """Test early warning detection."""
        indicators = LeadingIndicators(window_size=30)
        
        # Add data points with increasing trend
        for i in range(10):
            indicators.track_indicator(
                customer_key='CUST_001',
                indicator_type='utilization',
                value=0.5 + (i * 0.1),
                timestamp=datetime.now(timezone.utc).replace(tzinfo=None)
            )
        
        is_warning, score, message = indicators.detect_early_warning(
            'CUST_001',
            'utilization',
            threshold=0.8
        )
        
        assert isinstance(is_warning, bool)
        assert isinstance(score, float)


class TestWarningEscalation:
    """Test WarningEscalation class."""
    
    def test_should_escalate(self):
        """Test warning escalation logic."""
        escalation = WarningEscalation()
        
        # First warning should not escalate
        should_esc, level, reason = escalation.should_escalate(
            'CUST_001',
            'medium',
            'utilization',
            datetime.now(timezone.utc).replace(tzinfo=None)
        )
        
        assert should_esc is False
        
        # Multiple warnings should escalate
        for _ in range(5):
            escalation.record_warning(
                'CUST_001',
                'medium',
                'utilization',
                datetime.now(timezone.utc).replace(tzinfo=None)
            )
        
        should_esc, level, reason = escalation.should_escalate(
            'CUST_001',
            'medium',
            'utilization',
            datetime.now(timezone.utc).replace(tzinfo=None)
        )
        
        assert should_esc is True
    
    def test_record_warning(self):
        """Test recording warning."""
        escalation = WarningEscalation()
        
        escalation.record_warning(
            'CUST_001',
            'high',
            'utilization',
            datetime.now(timezone.utc).replace(tzinfo=None)
        )
        
        summary = escalation.get_escalation_summary('CUST_001')
        
        assert summary is not None
        assert 'total_warnings' in summary
        assert summary['total_warnings'] > 0
    
    def test_get_escalation_summary(self):
        """Test getting escalation summary."""
        escalation = WarningEscalation()
        
        # Record multiple warnings
        for i in range(3):
            escalation.record_warning(
                'CUST_001',
                'medium',
                'utilization',
                datetime.now(timezone.utc).replace(tzinfo=None)
            )
        
        summary = escalation.get_escalation_summary('CUST_001')
        
        assert summary['customer_key'] == 'CUST_001'
        assert summary['total_warnings'] == 3
        assert 'by_level' in summary
