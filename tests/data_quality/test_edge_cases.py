"""Data quality tests for edge cases."""

import pytest
import pandas as pd


@pytest.mark.data_quality
class TestEdgeCases:
    """Tests for edge case handling."""
    
    def test_zero_profitability(self, sample_edge_case_data):
        """Test handling of zero profitability."""
        df = sample_edge_case_data
        
        # Check for zero profit
        zero_profit = df[df["net_profit"] == 0.0]
        assert len(zero_profit) == 1
    
    def test_negative_profitability(self, sample_edge_case_data):
        """Test handling of negative profitability."""
        df = sample_edge_case_data
        
        # Check for negative profit
        negative_profit = df[df["net_profit"] < 0]
        assert len(negative_profit) == 2  # CUST_002 (-1000) and CUST_005 (-0.01)
    
    def test_extreme_profitability(self, sample_edge_case_data):
        """Test handling of extreme profitability values."""
        df = sample_edge_case_data
        
        # Check for extreme profit
        extreme_profit = df[df["net_profit"] > 100000]
        assert len(extreme_profit) == 1
    
    def test_churn_probability_bounds(self, sample_edge_case_data):
        """Test churn probability bounds (should be 0-1)."""
        df = sample_edge_case_data
        
        # Check bounds
        assert df["churn_probability"].min() >= 0
        assert df["churn_probability"].max() <= 1
    
    def test_zero_churn_probability(self, sample_edge_case_data):
        """Test handling of zero churn probability."""
        df = sample_edge_case_data
        
        zero_churn = df[df["churn_probability"] == 0.0]
        assert len(zero_churn) == 1
    
    def test_max_churn_probability(self, sample_edge_case_data):
        """Test handling of maximum churn probability."""
        df = sample_edge_case_data
        
        max_churn = df[df["churn_probability"] == 1.0]
        assert len(max_churn) == 1
    
    def test_zero_exposure(self, sample_edge_case_data):
        """Test handling of zero exposure."""
        df = sample_edge_case_data
        
        zero_exposure = df[df["exposure_amount"] == 0.0]
        assert len(zero_exposure) == 1
    
    def test_negative_exposure(self, sample_edge_case_data):
        """Test handling of negative exposure (should be invalid)."""
        df = sample_edge_case_data
        
        negative_exposure = df[df["exposure_amount"] < 0]
        assert len(negative_exposure) == 1
    
    def test_utilization_bounds(self, sample_edge_case_data):
        """Test credit utilization bounds (should be 0-1)."""
        df = sample_edge_case_data
        
        # Check for out-of-bounds values
        out_of_bounds = df[(df["credit_utilization"] < 0) | (df["credit_utilization"] > 1)]
        assert len(out_of_bounds) == 2
    
    def test_invalid_utilization_handling(self, sample_edge_case_data):
        """Test handling of invalid utilization values."""
        df = sample_edge_case_data.copy()
        
        # Clip to valid range
        df["credit_utilization"] = df["credit_utilization"].clip(0, 1)
        
        assert df["credit_utilization"].min() >= 0
        assert df["credit_utilization"].max() <= 1
