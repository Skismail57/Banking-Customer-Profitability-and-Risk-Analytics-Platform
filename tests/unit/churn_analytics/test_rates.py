"""Unit tests for churn rate calculations."""

import pytest
import pandas as pd

from src.churn_analytics.rates import ChurnRateCalculator


class TestChurnRateCalculator:
    """Tests for ChurnRateCalculator."""
    
    def test_calculate_churn_rate(self):
        """Test churn rate calculation."""
        calculator = ChurnRateCalculator()
        
        df = pd.DataFrame({
            "customer_key": [1, 2, 3, 4, 5],
            "is_churned": [1, 0, 0, 1, 0]
        })
        
        result = calculator.calculate_churn_rate(df)
        
        assert result["churn_rate"] == 40.0
        assert result["total_customers"] == 5
        assert result["churned_customers"] == 2
        assert result["retained_customers"] == 3
    
    def test_calculate_retention_rate(self):
        """Test retention rate calculation."""
        calculator = ChurnRateCalculator()
        
        df = pd.DataFrame({
            "customer_key": [1, 2, 3, 4, 5],
            "is_churned": [1, 0, 0, 1, 0]
        })
        
        result = calculator.calculate_retention_rate(df)
        
        assert result["retention_rate"] == 60.0
        assert result["retained_customers"] == 3
        assert result["churned_customers"] == 2
    
    def test_empty_dataframe(self):
        """Test with empty DataFrame."""
        calculator = ChurnRateCalculator()
        
        df = pd.DataFrame({"customer_key": [], "is_churned": []})
        
        churn_result = calculator.calculate_churn_rate(df)
        retention_result = calculator.calculate_retention_rate(df)
        
        assert churn_result["churn_rate"] == 0.0
        assert churn_result["total_customers"] == 0
        assert retention_result["retention_rate"] == 0.0
