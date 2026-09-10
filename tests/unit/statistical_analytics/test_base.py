"""Unit tests for statistical analytics base classes."""

import pytest
import pandas as pd

from src.statistical_analytics.base import TestResult, StatisticalBase


class TestTestResult:
    """Tests for TestResult dataclass."""
    
    def test_test_result_creation(self):
        """Test creating test result."""
        result = TestResult(
            test_name="Test",
            null_hypothesis="H0",
            alternative_hypothesis="H1",
            assumptions=["Assumption 1"],
            test_statistic=1.5,
            p_value=0.05
        )
        
        assert result.test_name == "Test"
        assert result.p_value == 0.05
    
    def test_to_dict(self):
        """Test serialization to dictionary."""
        result = TestResult(
            test_name="Test",
            null_hypothesis="H0",
            alternative_hypothesis="H1",
            assumptions=["Assumption 1"],
            test_statistic=1.5,
            p_value=0.05
        )
        
        data_dict = result.to_dict()
        
        assert data_dict["test_name"] == "Test"
        assert data_dict["p_value"] == 0.05


class TestStatisticalBase:
    """Tests for StatisticalBase class."""
    
    def test_initialization(self):
        """Test base class initialization."""
        base = StatisticalBase()
        
        assert base.alpha == 0.05
    
    def test_custom_alpha(self):
        """Test custom alpha."""
        base = StatisticalBase(alpha=0.01)
        
        assert base.alpha == 0.01
    
    def test_interpret_p_value_very_strong(self):
        """Test p-value interpretation for very strong evidence."""
        base = StatisticalBase()
        interpretation = base.interpret_p_value(0.0001)
        
        assert "Very strong" in interpretation
    
    def test_interpret_p_value_strong(self):
        """Test p-value interpretation for strong evidence."""
        base = StatisticalBase()
        interpretation = base.interpret_p_value(0.005)
        
        assert "Strong" in interpretation
    
    def test_interpret_p_value_moderate(self):
        """Test p-value interpretation for moderate evidence."""
        base = StatisticalBase()
        interpretation = base.interpret_p_value(0.03)
        
        assert "Moderate" in interpretation
    
    def test_interpret_p_value_insufficient(self):
        """Test p-value interpretation for insufficient evidence."""
        base = StatisticalBase()
        interpretation = base.interpret_p_value(0.15)
        
        assert "Insufficient" in interpretation
    
    def test_interpret_effect_size_cohens_d(self):
        """Test effect size interpretation for Cohen's d."""
        base = StatisticalBase()
        
        assert "Small" in base.interpret_effect_size(0.1, "cohens_d")
        assert "Medium" in base.interpret_effect_size(0.4, "cohens_d")
        assert "Large" in base.interpret_effect_size(0.7, "cohens_d")
    
    def test_interpret_effect_size_eta_squared(self):
        """Test effect size interpretation for eta-squared."""
        base = StatisticalBase()
        
        assert "Small" in base.interpret_effect_size(0.005, "eta_squared")
        assert "Medium" in base.interpret_effect_size(0.04, "eta_squared")
        assert "Large" in base.interpret_effect_size(0.10, "eta_squared")
