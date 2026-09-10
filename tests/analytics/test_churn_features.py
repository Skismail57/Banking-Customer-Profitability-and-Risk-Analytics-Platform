"""Analytics tests for churn features."""

import pytest
import pandas as pd


@pytest.mark.analytics
class TestChurnFeatures:
    """Tests for churn feature engineering and calculations."""
    
    def test_churn_probability_bounds(self, sample_customer_metrics):
        """Test churn probability bounds (0-1)."""
        df = sample_customer_metrics
        
        assert df["churn_probability"].between(0, 1).all()
    
    def test_high_churn_threshold(self, sample_customer_metrics):
        """Test high churn threshold (>0.7)."""
        df = sample_customer_metrics
        
        high_churn = df[df["churn_probability"] > 0.7]
        assert len(high_churn) == 1  # CUST_004 has 0.75
    
    def test_churn_by_segment(self, sample_customer_metrics):
        """Test churn probability by segment."""
        df = sample_customer_metrics
        
        segment_churn = df.groupby("segment")["churn_probability"].mean()
        
        # Premium should have lower churn than standard
        assert segment_churn["premium"] < segment_churn["standard"]
    
    def test_churn_vs_risk_correlation(self, sample_customer_metrics):
        """Test correlation between churn and risk."""
        df = sample_customer_metrics
        
        # Map risk to numeric
        risk_map = {"low": 1, "medium": 2, "high": 3}
        df["risk_score"] = df["risk_level"].map(risk_map)
        
        # Calculate correlation
        correlation = df["churn_probability"].corr(df["risk_score"])
        
        # Should be positive (higher risk, higher churn)
        assert correlation > 0
    
    def test_churn_vs_clv_correlation(self, sample_customer_metrics):
        """Test correlation between churn and CLV."""
        df = sample_customer_metrics
        
        # Calculate correlation
        correlation = df["churn_probability"].corr(df["clv"])
        
        # Should be negative (higher CLV, lower churn)
        assert correlation < 0
    
    def test_retention_rate_calculation(self, sample_customer_metrics):
        """Test retention rate calculation (1 - avg churn)."""
        df = sample_customer_metrics
        
        avg_churn = df["churn_probability"].mean()
        retention_rate = 1 - avg_churn
        
        assert retention_rate > 0
        assert retention_rate < 1
    
    def test_high_churn_high_clv_count(self, sample_customer_metrics):
        """Test count of high churn + high CLV customers."""
        df = sample_customer_metrics
        
        high_churn_high_clv = df[
            (df["churn_probability"] > 0.7) & 
            (df["clv"] > 10000)
        ]
        
        assert len(high_churn_high_clv) == 0  # No such customers in sample
    
    def test_churn_distribution(self, sample_customer_metrics):
        """Test churn probability distribution."""
        df = sample_customer_metrics
        
        churn_stats = df["churn_probability"].describe()
        
        assert churn_stats["min"] >= 0
        assert churn_stats["max"] <= 1
        assert churn_stats["mean"] > 0
