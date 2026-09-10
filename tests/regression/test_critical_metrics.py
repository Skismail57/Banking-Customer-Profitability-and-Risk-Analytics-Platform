"""Regression tests for critical analytical metrics."""

import pytest
import pandas as pd


@pytest.mark.regression
class TestCriticalMetricsRegression:
    """Regression tests for critical metrics to ensure stability."""
    
    def test_total_profit_calculation_regression(self, sample_customer_metrics):
        """Regression test for total profit calculation."""
        df = sample_customer_metrics
        
        total_profit = df["net_profit"].sum()
        
        # Expected value based on sample data
        expected_total = 39500.0
        
        assert total_profit == expected_total, f"Total profit changed from {expected_total} to {total_profit}"
    
    def test_risk_level_distribution_regression(self, sample_customer_metrics):
        """Regression test for risk level distribution."""
        df = sample_customer_metrics
        
        risk_counts = df["risk_level"].value_counts().to_dict()
        
        # Expected distribution
        expected_counts = {"low": 2, "medium": 2, "high": 1}
        
        for risk_level, expected_count in expected_counts.items():
            actual_count = risk_counts.get(risk_level, 0)
            assert actual_count == expected_count, \
                f"Risk level {risk_level} count changed from {expected_count} to {actual_count}"
    
    def test_churn_probability_average_regression(self, sample_customer_metrics):
        """Regression test for average churn probability."""
        df = sample_customer_metrics
        
        avg_churn = df["churn_probability"].mean()
        
        # Expected average (updated after sample data change)
        expected_avg = 0.284
        
        assert abs(avg_churn - expected_avg) < 0.01, \
            f"Average churn changed from {expected_avg} to {avg_churn}"
    
    def test_exposure_aggregation_regression(self, sample_customer_metrics):
        """Regression test for exposure aggregation."""
        df = sample_customer_metrics
        
        total_exposure = df["exposure_amount"].sum()
        
        # Expected total
        expected_total = 245000.0
        
        assert total_exposure == expected_total, \
            f"Total exposure changed from {expected_total} to {total_exposure}"
    
    def test_segment_profitability_regression(self, sample_customer_metrics):
        """Regression test for segment profitability."""
        df = sample_customer_metrics
        
        segment_profit = df.groupby("segment")["net_profit"].sum().to_dict()
        
        # Expected segment profits
        expected_profits = {
            "premium": 35000.0,
            "standard": 3500.0,
            "basic": 1000.0
        }
        
        for segment, expected_profit in expected_profits.items():
            actual_profit = segment_profit.get(segment, 0)
            assert actual_profit == expected_profit, \
                f"Segment {segment} profit changed from {expected_profit} to {actual_profit}"
