"""Analytics tests for profitability calculations."""

import pytest
import pandas as pd
import numpy as np


@pytest.mark.analytics
class TestProfitabilityCalculations:
    """Tests for profitability calculation accuracy."""
    
    def test_net_profit_calculation(self, sample_customer_metrics):
        """Test net profit calculation (revenue - cost)."""
        df = sample_customer_metrics
        
        calculated_profit = df["revenue"] - df["cost"]
        
        # Should match the net_profit column
        pd.testing.assert_series_equal(
            calculated_profit,
            df["net_profit"],
            check_names=False
        )
    
    def test_profit_margin_calculation(self, sample_customer_metrics):
        """Test profit margin calculation (profit / revenue)."""
        df = sample_customer_metrics
        
        profit_margin = df["net_profit"] / df["revenue"]
        
        # All margins should be positive
        assert (profit_margin > 0).all()
    
    def test_total_profit_aggregation(self, sample_customer_metrics):
        """Test total profit aggregation."""
        df = sample_customer_metrics
        
        total_profit = df["net_profit"].sum()
        expected_total = 15000 + 3000 + 20000 + 500 + 1000
        
        assert total_profit == expected_total
    
    def test_average_profit_calculation(self, sample_customer_metrics):
        """Test average profit calculation."""
        df = sample_customer_metrics
        
        avg_profit = df["net_profit"].mean()
        expected_avg = (15000 + 3000 + 20000 + 500 + 1000) / 5
        
        assert avg_profit == expected_avg
    
    def test_profit_by_segment_aggregation(self, sample_customer_metrics):
        """Test profit aggregation by segment."""
        df = sample_customer_metrics
        
        segment_profit = df.groupby("segment")["net_profit"].sum()
        
        # Premium segment should have higher profit
        assert segment_profit["premium"] > segment_profit["standard"]
        assert segment_profit["premium"] > segment_profit["basic"]
    
    def test_profit_variance_calculation(self, sample_customer_metrics):
        """Test profit variance calculation."""
        df = sample_customer_metrics
        
        profit_variance = df["net_profit"].var()
        
        assert profit_variance > 0
    
    def test_profit_distribution(self, sample_customer_metrics):
        """Test profit distribution statistics."""
        df = sample_customer_metrics
        
        profit_stats = df["net_profit"].describe()
        
        assert profit_stats["count"] == 5
        assert profit_stats["min"] >= 0
        assert profit_stats["max"] > profit_stats["min"]
