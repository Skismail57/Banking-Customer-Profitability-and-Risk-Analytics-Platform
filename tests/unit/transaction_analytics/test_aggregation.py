"""Unit tests for transaction analytics aggregation."""

import pytest
from datetime import date, datetime
import pandas as pd

from src.transaction_analytics.aggregation import TimeSeriesAggregator
from src.transaction_analytics.base import AggregationPeriod


class TestTimeSeriesAggregator:
    """Tests for TimeSeriesAggregator."""
    
    def test_aggregate_daily(self):
        """Test daily aggregation."""
        df = pd.DataFrame({
            "transaction_date": pd.to_datetime([
                "2024-01-01", "2024-01-01", "2024-01-02", "2024-01-03"
            ]),
            "amount": [100, 200, 150, 300]
        })
        
        aggregator = TimeSeriesAggregator(as_of_date=date(2024, 1, 15))
        result = aggregator.aggregate(df, "transaction_date", AggregationPeriod.DAILY)
        
        assert "period" in result.columns
        assert "transaction_count" in result.columns
        assert "transaction_value" in result.columns
        assert len(result) == 3  # 3 unique days
    
    def test_aggregate_monthly(self):
        """Test monthly aggregation."""
        df = pd.DataFrame({
            "transaction_date": pd.to_datetime([
                "2024-01-15", "2024-01-20", "2024-02-10", "2024-02-25"
            ]),
            "amount": [100, 200, 150, 300]
        })
        
        aggregator = TimeSeriesAggregator(as_of_date=date(2024, 2, 28))
        result = aggregator.aggregate(df, "transaction_date", AggregationPeriod.MONTHLY)
        
        assert "period" in result.columns
        assert len(result) == 2  # 2 unique months
    
    def test_aggregate_by_customer(self):
        """Test aggregation by customer."""
        df = pd.DataFrame({
            "transaction_date": pd.to_datetime([
                "2024-01-01", "2024-01-01", "2024-01-02"
            ]),
            "customer_key": [1, 1, 2],
            "amount": [100, 200, 150]
        })
        
        aggregator = TimeSeriesAggregator(as_of_date=date(2024, 1, 15))
        result = aggregator.aggregate_by_customer(df, "transaction_date", AggregationPeriod.DAILY)
        
        assert "customer_key" in result.columns
        assert len(result) >= 2
    
    def test_temporal_safety(self):
        """Test temporal safety filtering."""
        df = pd.DataFrame({
            "transaction_date": pd.to_datetime([
                "2024-01-10", "2024-01-15", "2024-01-20"  # Future date
            ]),
            "amount": [100, 200, 300]
        })
        
        aggregator = TimeSeriesAggregator(as_of_date=date(2024, 1, 15))
        result = aggregator.aggregate(df, "transaction_date", AggregationPeriod.DAILY)
        
        # Future date should be filtered
        assert result["transaction_value"].sum() == 300  # Only first two transactions
    
    def test_calculate_period_growth(self):
        """Test period-over-period growth calculation."""
        agg_df = pd.DataFrame({
            "period": pd.to_datetime(["2024-01-01", "2024-02-01", "2024-03-01"]),
            "transaction_value": [1000, 1200, 900]
        })
        
        aggregator = TimeSeriesAggregator()
        result = aggregator.calculate_period_growth(agg_df, "transaction_value")
        
        assert "growth_rate" in result.columns
        assert "growth_percentage" in result.columns
    
    def test_calculate_moving_average(self):
        """Test moving average calculation."""
        agg_df = pd.DataFrame({
            "period": pd.to_datetime(["2024-01-01", "2024-02-01", "2024-03-01", "2024-04-01"]),
            "transaction_value": [1000, 1200, 900, 1100]
        })
        
        aggregator = TimeSeriesAggregator()
        result = aggregator.calculate_moving_average(agg_df, "transaction_value", window=3)
        
        assert "transaction_value_ma_3" in result.columns
