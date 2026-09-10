"""Analytics tests for risk calculations."""

import pytest
import pandas as pd


@pytest.mark.analytics
class TestRiskCalculations:
    """Tests for risk calculation accuracy."""
    
    def test_risk_level_distribution(self, sample_customer_metrics):
        """Test risk level distribution calculation."""
        df = sample_customer_metrics
        
        risk_counts = df["risk_level"].value_counts()
        
        assert "low" in risk_counts
        assert "medium" in risk_counts
        assert "high" in risk_counts
    
    def test_high_risk_customer_count(self, sample_customer_metrics):
        """Test high risk customer count."""
        df = sample_customer_metrics
        
        high_risk_count = len(df[df["risk_level"] == "high"])
        assert high_risk_count == 1
    
    def test_exposure_aggregation(self, sample_customer_metrics):
        """Test exposure aggregation."""
        df = sample_customer_metrics
        
        total_exposure = df["exposure_amount"].sum()
        expected_total = 75000 + 30000 + 100000 + 15000 + 25000
        
        assert total_exposure == expected_total
    
    def test_exposure_by_risk_level(self, sample_customer_metrics):
        """Test exposure by risk level."""
        df = sample_customer_metrics
        
        exposure_by_risk = df.groupby("risk_level")["exposure_amount"].sum()
        
        # High risk should have lower exposure than low risk in this sample
        assert exposure_by_risk["low"] > exposure_by_risk["high"]
    
    def test_utilization_calculation(self, sample_customer_metrics):
        """Test credit utilization calculation."""
        df = sample_customer_metrics
        
        # All utilizations should be between 0 and 1
        assert df["credit_utilization"].between(0, 1).all()
    
    def test_high_utilization_threshold(self, sample_customer_metrics):
        """Test high utilization threshold (>0.85)."""
        df = sample_customer_metrics
        
        high_utilization = df[df["credit_utilization"] > 0.85]
        assert len(high_utilization) == 1  # CUST_004 has 0.90
    
    def test_dpd_calculation(self, sample_customer_metrics):
        """Test days past due calculation."""
        df = sample_customer_metrics
        
        # DPD should be non-negative
        assert (df["days_past_due"] >= 0).all()
    
    def test_dpd_30_plus_count(self, sample_customer_metrics):
        """Test count of customers with DPD > 30."""
        df = sample_customer_metrics
        
        dpd_30_plus = len(df[df["days_past_due"] > 30])
        assert dpd_30_plus == 1
    
    def test_credit_score_range(self, sample_customer_metrics):
        """Test credit score range (typically 300-850)."""
        df = sample_customer_metrics
        
        # All scores should be in valid range
        assert df["credit_score"].between(300, 850).all()
    
    def test_risk_score_mapping(self, sample_customer_metrics):
        """Test risk level to score mapping."""
        df = sample_customer_metrics
        
        risk_score_map = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        df["risk_score"] = df["risk_level"].map(risk_score_map)
        
        # All scores should be mapped
        assert df["risk_score"].notna().all()
