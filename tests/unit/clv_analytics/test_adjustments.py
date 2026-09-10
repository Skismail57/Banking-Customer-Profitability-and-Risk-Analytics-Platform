"""Unit tests for CLV adjustments."""

import pytest

from src.clv_analytics.adjustments import RetentionAdjustedCLV, ProfitabilityAdjustedCLV


class TestRetentionAdjustedCLV:
    """Tests for RetentionAdjustedCLV."""
    
    def test_calculate_retention_adjusted_clv(self):
        """Test retention-adjusted CLV calculation."""
        adjuster = RetentionAdjustedCLV()
        
        result = adjuster.calculate(
            base_clv=100,
            retention_rate=0.80,
            discount_rate=0.10,
            time_horizon_years=5
        )
        
        assert "retention_adjusted_clv" in result
        assert result["retention_adjusted_clv"] > 0
        assert result["retention_rate"] == 0.80
        assert len(result["components"]["retention_probabilities"]) == 5
    
    def test_calculate_with_churn_rate(self):
        """Test retention-adjusted CLV using churn rate."""
        adjuster = RetentionAdjustedCLV()
        
        result = adjuster.calculate_with_churn_rate(
            base_clv=100,
            churn_rate=0.20,  # 20% churn = 80% retention
            discount_rate=0.10,
            time_horizon_years=5
        )
        
        assert "retention_adjusted_clv" in result
        assert result["retention_adjusted_clv"] > 0


class TestProfitabilityAdjustedCLV:
    """Tests for ProfitabilityAdjustedCLV."""
    
    def test_calculate_profitability_adjusted_clv(self):
        """Test profitability-adjusted CLV calculation."""
        adjuster = ProfitabilityAdjustedCLV()
        
        result = adjuster.calculate(
            base_clv=1000,
            profit_margin=0.20,
            retention_rate=0.80,
            discount_rate=0.10,
            time_horizon_years=5
        )
        
        assert "profitability_adjusted_clv" in result
        assert result["profit_margin"] == 0.20
        assert result["profit_adjusted_base"] == 200  # 1000 * 0.20
    
    def test_calculate_with_revenue_and_cost(self):
        """Test profitability-adjusted CLV from revenue and cost."""
        adjuster = ProfitabilityAdjustedCLV()
        
        result = adjuster.calculate_with_revenue_and_cost(
            average_revenue=1000,
            average_cost=800,
            retention_rate=0.80,
            discount_rate=0.10,
            time_horizon_years=5
        )
        
        assert "profitability_adjusted_clv" in result
        assert result["profit_margin"] == 0.20  # (1000 - 800) / 1000
