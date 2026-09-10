"""Unit tests for anomaly adapter."""

import pytest
from datetime import datetime
from unittest.mock import Mock
from src.streaming.anomaly.anomaly_adapter import (
    StreamingAnomalyAdapter,
    MLAnomalyDetector,
    AnomalyAlertIntegrator
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
    return store


@pytest.fixture
def anomaly_adapter(mock_config, mock_feature_store):
    """Anomaly adapter fixture."""
    return StreamingAnomalyAdapter(mock_config, mock_feature_store)


class TestStreamingAnomalyAdapter:
    """Test StreamingAnomalyAdapter class."""
    
    def test_detect_amount_anomaly(self, anomaly_adapter):
        """Test amount anomaly detection."""
        features = {
            'amount': 5000.0,
            'customer_key': 'CUST_001'
        }
        
        result = anomaly_adapter.detect_anomaly(
            customer_key='CUST_001',
            anomaly_type='amount',
            features=features
        )
        
        assert result is not None
        assert result['customer_key'] == 'CUST_001'
        assert result['anomaly_type'] == 'amount'
        assert 'anomaly_score' in result
        assert 'severity' in result
    
    def test_detect_frequency_anomaly(self, anomaly_adapter):
        """Test frequency anomaly detection."""
        features = {
            'transaction_count': 15,
            'window_minutes': 60,
            'customer_key': 'CUST_001'
        }
        
        result = anomaly_adapter.detect_anomaly(
            customer_key='CUST_001',
            anomaly_type='frequency',
            features=features
        )
        
        assert result is not None
        assert result['anomaly_type'] == 'frequency'
    
    def test_detect_velocity_anomaly(self, anomaly_adapter):
        """Test velocity anomaly detection."""
        features = {
            'amount': 10000.0,
            'previous_amount': 100.0,
            'time_delta_minutes': 5,
            'customer_key': 'CUST_001'
        }
        
        result = anomaly_adapter.detect_anomaly(
            customer_key='CUST_001',
            anomaly_type='velocity',
            features=features
        )
        
        assert result is not None
        assert result['anomaly_type'] == 'velocity'
    
    def test_severity_classification(self, anomaly_adapter):
        """Test anomaly severity classification."""
        # Test low severity
        low_severity = anomaly_adapter._classify_severity(0.2)
        assert low_severity == 'low'
        
        # Test high severity
        high_severity = anomaly_adapter._classify_severity(0.8)
        assert high_severity == 'high'
        
        # Test critical severity
        critical_severity = anomaly_adapter._classify_severity(0.95)
        assert critical_severity == 'critical'


class TestMLAnomalyDetector:
    """Test MLAnomalyDetector class."""
    
    def test_train_isolation_forest(self):
        """Test training isolation forest model."""
        detector = MLAnomalyDetector()
        
        import numpy as np
        X = np.random.rand(100, 5)
        
        detector.train_isolation_forest(X)
        
        assert detector.model is not None
    
    def test_detect_anomaly_ml(self):
        """Test ML-based anomaly detection."""
        detector = MLAnomalyDetector()
        
        import numpy as np
        X_train = np.random.rand(100, 5)
        detector.train_isolation_forest(X_train)
        
        X_test = np.random.rand(10, 5)
        anomalies = detector.detect_anomaly(X_test)
        
        assert len(anomalies) == 10
        assert all('is_anomaly' in a for a in anomalies)
    
    def test_calculate_anomaly_score(self):
        """Test anomaly score calculation."""
        detector = MLAnomalyDetector()
        
        import numpy as np
        X_train = np.random.rand(100, 5)
        detector.train_isolation_forest(X_train)
        
        X_test = np.random.rand(1, 5)
        score = detector.calculate_anomaly_score(X_test[0])
        
        assert 0 <= score <= 1


class TestAnomalyAlertIntegrator:
    """Test AnomalyAlertIntegrator class."""
    
    def test_should_alert(self):
        """Test alert decision logic."""
        integrator = AnomalyAlertIntegrator()
        
        should_alert, reason = integrator.should_alert(
            customer_key='CUST_001',
            anomaly_type='amount',
            severity='high'
        )
        
        assert should_alert is True
        assert reason == "Alert allowed"
    
    def test_rate_limiting(self):
        """Test rate limiting."""
        integrator = AnomalyAlertIntegrator(max_alerts_per_customer_per_hour=2)
        
        # Record 2 alerts
        integrator.record_alert('CUST_001', 'amount', 'high', 'ANOM_001')
        integrator.record_alert('CUST_001', 'amount', 'high', 'ANOM_002')
        
        # Third alert should be rate limited
        should_alert, reason = integrator.should_alert(
            customer_key='CUST_001',
            anomaly_type='amount',
            severity='high'
        )
        
        assert should_alert is False
        assert reason == "Rate limit exceeded"
    
    def test_deduplication(self):
        """Test alert deduplication."""
        integrator = AnomalyAlertIntegrator(dedup_window_seconds=3600)
        
        # Record an alert
        integrator.record_alert('CUST_001', 'amount', 'high', 'ANOM_001')
        
        # Same alert should be deduplicated
        should_alert, reason = integrator.should_alert(
            customer_key='CUST_001',
            anomaly_type='amount',
            severity='high'
        )
        
        assert should_alert is False
        assert reason == "Duplicate alert within deduplication window"
    
    def test_alert_summary(self):
        """Test alert summary."""
        integrator = AnomalyAlertIntegrator()
        
        integrator.record_alert('CUST_001', 'amount', 'high', 'ANOM_001')
        integrator.record_alert('CUST_002', 'frequency', 'medium', 'ANOM_002')
        
        summary = integrator.get_alert_summary()
        
        assert summary['total_customers'] == 2
        assert summary['total_alerts'] == 2
