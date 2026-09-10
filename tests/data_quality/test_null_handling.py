"""Data quality tests for null handling."""

import pytest
import pandas as pd
import numpy as np


@pytest.mark.data_quality
class TestNullHandling:
    """Tests for null value handling."""
    
    def test_null_customer_key_handling(self, sample_null_data):
        """Test handling of null customer keys."""
        df = sample_null_data
        
        # Count null customer keys
        null_count = df["customer_key"].isna().sum()
        assert null_count == 1
        
        # Filter out null customer keys
        filtered_df = df[df["customer_key"].notna()]
        assert len(filtered_df) == 4
    
    def test_null_profitability_handling(self, sample_null_data):
        """Test handling of null profitability values."""
        df = sample_null_data
        
        # Count null profits
        null_count = df["net_profit"].isna().sum()
        assert null_count == 2
        
        # Fill null with 0
        filled_df = df["net_profit"].fillna(0)
        assert filled_df.isna().sum() == 0
    
    def test_null_risk_level_handling(self, sample_null_data):
        """Test handling of null risk levels."""
        df = sample_null_data
        
        # Count null risk levels
        null_count = df["risk_level"].isna().sum()
        assert null_count == 1
        
        # Fill null with 'unknown'
        filled_df = df["risk_level"].fillna("unknown")
        assert filled_df.isna().sum() == 0
    
    def test_null_churn_probability_handling(self, sample_null_data):
        """Test handling of null churn probabilities."""
        df = sample_null_data
        
        # Count null churn probabilities
        null_count = df["churn_probability"].isna().sum()
        assert null_count == 1
        
        # Fill null with mean
        mean_value = df["churn_probability"].mean()
        filled_df = df["churn_probability"].fillna(mean_value)
        assert filled_df.isna().sum() == 0
    
    def test_all_null_row_handling(self):
        """Test handling of rows with all null values."""
        df = pd.DataFrame({
            "customer_key": [None, "CUST_002"],
            "net_profit": [None, 1000.0],
            "risk_level": [None, "low"]
        })
        
        # Drop all-null rows
        filtered_df = df.dropna(how="all")
        assert len(filtered_df) == 1
        assert filtered_df.iloc[0]["customer_key"] == "CUST_002"
