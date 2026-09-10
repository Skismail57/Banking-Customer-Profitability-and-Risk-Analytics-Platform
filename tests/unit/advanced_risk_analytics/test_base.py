"""Unit tests for advanced risk analytics base classes."""

import pytest

from src.advanced_risk_analytics.base import RiskLevel, RiskThresholds, RiskBase


class TestRiskLevel:
    """Tests for RiskLevel enum."""
    
    def test_risk_level_enum_values(self):
        """Test RiskLevel enum has expected values."""
        assert RiskLevel.LOW.value == "low"
        assert RiskLevel.MEDIUM.value == "medium"
        assert RiskLevel.HIGH.value == "high"
        assert RiskLevel.CRITICAL.value == "critical"


class TestRiskThresholds:
    """Tests for RiskThresholds dataclass."""
    
    def test_default_thresholds(self):
        """Test default threshold values."""
        thresholds = RiskThresholds()
        
        assert thresholds.utilization_low_threshold == 0.30
        assert thresholds.dpd_critical_threshold == 90
        assert thresholds.concentration_warning_threshold == 0.20
    
    def test_to_dict(self):
        """Test serialization to dictionary."""
        thresholds = RiskThresholds()
        data_dict = thresholds.to_dict()
        
        assert "utilization_low_threshold" in data_dict
        assert data_dict["utilization_low_threshold"] == 0.30


class TestRiskBase:
    """Tests for RiskBase class."""
    
    def test_initialization(self):
        """Test base class initialization."""
        base = RiskBase()
        
        assert base.thresholds is not None
        assert base.thresholds.utilization_low_threshold == 0.30
    
    def test_custom_thresholds(self):
        """Test custom thresholds."""
        custom_thresholds = RiskThresholds(utilization_low_threshold=0.25)
        base = RiskBase(thresholds=custom_thresholds)
        
        assert base.thresholds.utilization_low_threshold == 0.25
    
    def test_determine_risk_level_low(self):
        """Test determining low risk level."""
        base = RiskBase()
        risk_level = base.determine_risk_level(
            utilization=0.20,
            dpd=0,
            credit_score=750
        )
        
        assert risk_level == RiskLevel.LOW
    
    def test_determine_risk_level_critical(self):
        """Test determining critical risk level."""
        base = RiskBase()
        risk_level = base.determine_risk_level(
            utilization=0.90,
            dpd=120,
            credit_score=400
        )
        
        assert risk_level == RiskLevel.CRITICAL
