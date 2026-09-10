"""Unit tests for decision intelligence base classes."""

import pytest

from src.decision_intelligence.base import Priority, ConfidenceLevel, Recommendation, DecisionBase


class TestPriority:
    """Tests for Priority enum."""
    
    def test_priority_enum_values(self):
        """Test Priority enum has expected values."""
        assert Priority.CRITICAL.value == "critical"
        assert Priority.HIGH.value == "high"
        assert Priority.MEDIUM.value == "medium"
        assert Priority.LOW.value == "low"


class TestConfidenceLevel:
    """Tests for ConfidenceLevel enum."""
    
    def test_confidence_level_enum_values(self):
        """Test ConfidenceLevel enum has expected values."""
        assert ConfidenceLevel.HIGH.value == "high"
        assert ConfidenceLevel.MEDIUM.value == "medium"
        assert ConfidenceLevel.LOW.value == "low"


class TestRecommendation:
    """Tests for Recommendation dataclass."""
    
    def test_recommendation_creation(self):
        """Test creating recommendation."""
        from datetime import date
        
        recommendation = Recommendation(
            customer_key="cust_001",
            segment="premium",
            triggering_metrics={"profit": 1000},
            reason="Test reason",
            recommended_action="Test action",
            priority=Priority.HIGH,
            confidence=ConfidenceLevel.MEDIUM,
            limitations=["Limitation 1"],
            generated_at=date.today()
        )
        
        assert recommendation.customer_key == "cust_001"
        assert recommendation.priority == Priority.HIGH
    
    def test_to_dict(self):
        """Test serialization to dictionary."""
        from datetime import date
        
        recommendation = Recommendation(
            customer_key="cust_001",
            segment="premium",
            triggering_metrics={"profit": 1000},
            reason="Test reason",
            recommended_action="Test action",
            priority=Priority.HIGH,
            confidence=ConfidenceLevel.MEDIUM,
            limitations=["Limitation 1"],
            generated_at=date.today()
        )
        
        data_dict = recommendation.to_dict()
        
        assert data_dict["customer_key"] == "cust_001"
        assert "disclaimer" in data_dict


class TestDecisionBase:
    """Tests for DecisionBase class."""
    
    def test_calculate_priority_critical(self):
        """Test calculating critical priority."""
        base = DecisionBase()
        priority = base.calculate_priority(
            risk_level="critical",
            exposure_amount=150000,
            profitability=-1000,
            churn_probability=0.8
        )
        
        assert priority == Priority.CRITICAL
    
    def test_calculate_priority_low(self):
        """Test calculating low priority."""
        base = DecisionBase()
        priority = base.calculate_priority(
            risk_level="low",
            exposure_amount=5000,
            profitability=10000,
            churn_probability=0.1
        )
        
        assert priority == Priority.LOW
    
    def test_calculate_confidence_high(self):
        """Test calculating high confidence."""
        base = DecisionBase()
        confidence = base.calculate_confidence(
            data_quality="high",
            model_accuracy=0.9,
            rule_complexity="simple"
        )
        
        assert confidence == ConfidenceLevel.HIGH
