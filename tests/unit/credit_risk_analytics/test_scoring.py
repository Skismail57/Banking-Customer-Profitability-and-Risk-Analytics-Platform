"""Unit tests for credit risk scoring."""

import pytest

from src.credit_risk_analytics.base import (
    RiskIndicator,
    RiskBand,
    RiskIndicatorValue,
)
from src.credit_risk_analytics.scoring import (
    RiskScoreWeight,
    CustomerRiskScoreCalculator,
)
from src.credit_risk_analytics.bands import (
    RiskBandThreshold,
    RiskBandClassifier,
)


class TestRiskScoreWeight:
    """Tests for RiskScoreWeight dataclass."""
    
    def test_weight_creation(self):
        """Test creating weight configuration."""
        weight = RiskScoreWeight(
            indicator=RiskIndicator.DAYS_PAST_DUE,
            weight=0.25,
            direction="higher_is_worse",
            max_score=100.0
        )
        
        assert weight.indicator == RiskIndicator.DAYS_PAST_DUE
        assert weight.weight == 0.25
        assert weight.direction == "higher_is_worse"
    
    def test_to_dict(self):
        """Test serialization to dictionary."""
        weight = RiskScoreWeight(
            indicator=RiskIndicator.CREDIT_UTILIZATION,
            weight=0.20,
            direction="higher_is_worse"
        )
        
        data_dict = weight.to_dict()
        
        assert data_dict["indicator"] == "credit_utilization"
        assert data_dict["weight"] == 0.20


class TestCustomerRiskScoreCalculator:
    """Tests for CustomerRiskScoreCalculator."""
    
    def test_default_weights(self):
        """Test default weights are created."""
        calculator = CustomerRiskScoreCalculator()
        
        assert len(calculator.weights) > 0
        total_weight = sum(w.weight for w in calculator.weights)
        assert abs(total_weight - 1.0) < 0.01
    
    def test_normalize_dpd(self):
        """Test DPD normalization."""
        calculator = CustomerRiskScoreCalculator()
        
        # 0 DPD should be 0 score
        score = calculator.normalize_indicator_value(
            RiskIndicator.DAYS_PAST_DUE, 0, "higher_is_worse"
        )
        assert score == 0.0
        
        # 90 DPD should be 100 score
        score = calculator.normalize_indicator_value(
            RiskIndicator.DAYS_PAST_DUE, 90, "higher_is_worse"
        )
        assert score == 100.0
    
    def test_normalize_utilization(self):
        """Test utilization normalization."""
        calculator = CustomerRiskScoreCalculator()
        
        # 0% utilization should be 0 score
        score = calculator.normalize_indicator_value(
            RiskIndicator.CREDIT_UTILIZATION, 0, "higher_is_worse"
        )
        assert score == 0.0
        
        # 100% utilization should be 100 score
        score = calculator.normalize_indicator_value(
            RiskIndicator.CREDIT_UTILIZATION, 100, "higher_is_worse"
        )
        assert score == 100.0
    
    def test_normalize_on_time_payment_rate(self):
        """Test on-time payment rate normalization."""
        calculator = CustomerRiskScoreCalculator()
        
        # 100% on-time should be 0 score (higher_is_better)
        score = calculator.normalize_indicator_value(
            RiskIndicator.ON_TIME_PAYMENT_RATE, 100, "higher_is_better"
        )
        assert score == 0.0
        
        # 0% on-time should be 100 score
        score = calculator.normalize_indicator_value(
            RiskIndicator.ON_TIME_PAYMENT_RATE, 0, "higher_is_better"
        )
        assert score == 100.0
    
    def test_calculate_risk_score(self):
        """Test risk score calculation."""
        calculator = CustomerRiskScoreCalculator()
        
        indicator_values = {
            RiskIndicator.DAYS_PAST_DUE: RiskIndicatorValue(
                indicator=RiskIndicator.DAYS_PAST_DUE,
                value=45,
                is_available=True,
                data_completeness=1.0,
                confidence=0.9
            ),
            RiskIndicator.CREDIT_UTILIZATION: RiskIndicatorValue(
                indicator=RiskIndicator.CREDIT_UTILIZATION,
                value=50,
                is_available=True,
                data_completeness=1.0,
                confidence=0.9
            ),
            RiskIndicator.ON_TIME_PAYMENT_RATE: RiskIndicatorValue(
                indicator=RiskIndicator.ON_TIME_PAYMENT_RATE,
                value=80,
                is_available=True,
                data_completeness=1.0,
                confidence=0.9
            ),
        }
        
        result = calculator.calculate_risk_score(indicator_values)
        
        assert "risk_score" in result
        assert "disclaimer" in result
        assert 0 <= result["risk_score"] <= 100
        assert "portfolio analytics only" in result["disclaimer"].lower()
    
    def test_classify_risk_band(self):
        """Test risk band classification."""
        calculator = CustomerRiskScoreCalculator()
        
        # Low risk
        band = calculator.classify_risk_band(10)
        assert band == RiskBand.LOW
        
        # Medium risk
        band = calculator.classify_risk_band(35)
        assert band == RiskBand.MEDIUM
        
        # High risk
        band = calculator.classify_risk_band(60)
        assert band == RiskBand.HIGH
        
        # Critical risk
        band = calculator.classify_risk_band(80)
        assert band == RiskBand.CRITICAL


class TestRiskBandThreshold:
    """Tests for RiskBandThreshold dataclass."""
    
    def test_threshold_creation(self):
        """Test creating threshold configuration."""
        threshold = RiskBandThreshold(
            band=RiskBand.HIGH,
            min_score=50.0,
            max_score=75.0,
            description="High risk profile",
            recommended_actions=["Monitor closely", "Review exposure"]
        )
        
        assert threshold.band == RiskBand.HIGH
        assert threshold.min_score == 50.0
        assert threshold.max_score == 75.0


class TestRiskBandClassifier:
    """Tests for RiskBandClassifier."""
    
    def test_default_thresholds(self):
        """Test default thresholds are created."""
        classifier = RiskBandClassifier()
        
        thresholds = classifier.get_all_bands()
        
        assert len(thresholds) == 4
        band_names = [t.band for t in thresholds]
        assert RiskBand.LOW in band_names
        assert RiskBand.MEDIUM in band_names
        assert RiskBand.HIGH in band_names
        assert RiskBand.CRITICAL in band_names
    
    def test_classify_low(self):
        """Test low band classification."""
        classifier = RiskBandClassifier()
        
        band = classifier.classify(10)
        assert band == RiskBand.LOW
    
    def test_classify_medium(self):
        """Test medium band classification."""
        classifier = RiskBandClassifier()
        
        band = classifier.classify(35)
        assert band == RiskBand.MEDIUM
    
    def test_classify_high(self):
        """Test high band classification."""
        classifier = RiskBandClassifier()
        
        band = classifier.classify(60)
        assert band == RiskBand.HIGH
    
    def test_classify_critical(self):
        """Test critical band classification."""
        classifier = RiskBandClassifier()
        
        band = classifier.classify(80)
        assert band == RiskBand.CRITICAL
    
    def test_classify_batch(self):
        """Test batch classification."""
        classifier = RiskBandClassifier()
        
        scores = [10, 35, 60, 80]
        bands = classifier.classify_batch(scores)
        
        assert bands == [RiskBand.LOW, RiskBand.MEDIUM, RiskBand.HIGH, RiskBand.CRITICAL]
