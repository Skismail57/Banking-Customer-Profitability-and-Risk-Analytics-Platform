"""Unit tests for risk engine."""

import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock
from src.streaming.risk.risk_engine import (
    RealTimeRiskEngine,
    RiskAggregator,
    DynamicRiskThresholds
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
def risk_engine(mock_config, mock_feature_store):
    """Risk engine fixture."""
    return RealTimeRiskEngine(mock_config, mock_feature_store)


class TestRealTimeRiskEngine:
    """Test RealTimeRiskEngine class."""
    
    def test_compute_credit_risk(self, risk_engine):
        """Test credit risk computation."""
        features = {
            'credit_score': 750,
            'credit_utilization': 0.35,
            'payment_history_score': 0.95,
            'account_age_months': 60
        }
        
        risk_event = risk_engine.compute_risk(
            customer_key='CUST_001',
            risk_type='credit',
            features=features
        )
        
        assert risk_event is not None
        assert risk_event['customer_key'] == 'CUST_001'
        assert risk_event['risk_type'] == 'credit'
        assert 'risk_score' in risk_event
        assert 'risk_level' in risk_event
    
    def test_compute_payment_risk(self, risk_engine):
        """Test payment risk computation."""
        features = {
            'days_past_due': 15,
            'payment_history_score': 0.85,
            'dpd': 15
        }
        
        risk_event = risk_engine.compute_risk(
            customer_key='CUST_001',
            risk_type='payment',
            features=features
        )
        
        assert risk_event is not None
        assert risk_event['risk_type'] == 'payment'
    
    def test_compute_concentration_risk(self, risk_engine):
        """Test concentration risk computation."""
        features = {
            'concentration_ratio': 0.45,
            'exposure_amount': 75000.0,
            'total_exposure': 150000.0
        }
        
        risk_event = risk_engine.compute_risk(
            customer_key='CUST_001',
            risk_type='concentration',
            features=features
        )
        
        assert risk_event is not None
        assert risk_event['risk_type'] == 'concentration'
    
    def test_risk_level_mapping(self, risk_engine):
        """Test risk level mapping from score."""
        # Test low risk
        low_risk = risk_engine._score_to_level(0.2)
        assert low_risk == 'low'
        
        # Test high risk
        high_risk = risk_engine._score_to_level(0.8)
        assert high_risk == 'high'


class TestRiskAggregator:
    """Test RiskAggregator class."""
    
    def test_aggregate_risk_weighted_average(self):
        """Test risk aggregation with weighted average."""
        aggregator = RiskAggregator(
            weights={'credit': 0.5, 'payment': 0.3, 'concentration': 0.2},
            aggregation_method='weighted_average'
        )
        
        risk_events = [
            {'risk_type': 'credit', 'risk_score': 0.8},
            {'risk_type': 'payment', 'risk_score': 0.6},
            {'risk_type': 'concentration', 'risk_score': 0.4}
        ]
        
        result = aggregator.aggregate_risk('CUST_001', risk_events)
        
        assert 'aggregated_score' in result
        assert 'risk_level' in result
        assert 0 <= result['aggregated_score'] <= 1
    
    def test_aggregate_risk_max(self):
        """Test risk aggregation with max method."""
        aggregator = RiskAggregator(
            aggregation_method='max'
        )
        
        risk_events = [
            {'risk_type': 'credit', 'risk_score': 0.8},
            {'risk_type': 'payment', 'risk_score': 0.6},
            {'risk_type': 'concentration', 'risk_score': 0.4}
        ]
        
        result = aggregator.aggregate_risk('CUST_001', risk_events)
        
        assert result['aggregated_score'] == 0.8  # Max value
    
    def test_score_to_level(self):
        """Test score to level conversion."""
        aggregator = RiskAggregator()
        
        assert aggregator._score_to_level(0.2) == 'low'
        assert aggregator._score_to_level(0.5) == 'medium'
        assert aggregator._score_to_level(0.8) == 'high'
        assert aggregator._score_to_level(0.95) == 'critical'


class TestDynamicRiskThresholds:
    """Test DynamicRiskThresholds class."""
    
    def test_adjust_thresholds(self):
        """Test dynamic threshold adjustment."""
        thresholds = DynamicRiskThresholds()
        
        portfolio_performance = {
            'default_rate': 0.05,
            'profitability': 0.15
        }
        
        market_conditions = {
            'interest_rate': 0.05,
            'inflation': 0.03
        }
        
        adjusted = thresholds.adjust_thresholds(
            portfolio_performance,
            market_conditions
        )
        
        assert adjusted is not None
        assert hasattr(adjusted, 'credit_threshold')
        assert hasattr(adjusted, 'payment_threshold')
    
    def test_reset_to_base(self):
        """Test resetting to base thresholds."""
        thresholds = DynamicRiskThresholds()
        
        # Adjust thresholds first
        thresholds.adjust_thresholds({}, {})
        
        # Reset to base
        thresholds.reset_to_base()
        
        current = thresholds.get_current_thresholds()
        assert current is not None
    
    def test_get_adjustment_summary(self):
        """Test getting adjustment summary."""
        thresholds = DynamicRiskThresholds()
        
        summary = thresholds.get_adjustment_summary()
        
        assert 'base_thresholds' in summary
        assert 'current_thresholds' in summary
