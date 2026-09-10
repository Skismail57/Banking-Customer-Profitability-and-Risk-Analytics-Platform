"""Time-series aggregation layer for transaction analytics."""

from datetime import date, datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import logging

import pandas as pd

from src.transaction_analytics.base import AggregationPeriod

logger = logging.getLogger(__name__)


class TimeSeriesAggregator:
    """Reusable aggregation layer for time-based transaction analysis."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize time-series aggregator.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        self.as_of_date = as_of_date or date.today()
    
    def aggregate(
        self,
        df: pd.DataFrame,
        date_column: str,
        period: AggregationPeriod,
        group_by_columns: Optional[List[str]] = None,
        value_column: str = "amount"
    ) -> pd.DataFrame:
        """Aggregate transactions by time period.
        
        Args:
            df: DataFrame with transaction data
            date_column: Name of date column
            period: Aggregation period (daily, weekly, monthly, quarterly, yearly)
            group_by_columns: Optional columns to group by (e.g., customer_id, category)
            value_column: Column to aggregate (default: amount)
        
        Returns:
            Aggregated DataFrame
        """
        logger.info(f"Aggregating transactions by {period.value}")
        
        # Ensure date column is datetime
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])
        
        # Filter to as_of_date
        df = df[df[date_column] <= pd.Timestamp(self.as_of_date)]
        
        # Add period column
        df["period"] = self._get_period_column(df[date_column], period)
        
        # Determine group by columns
        group_cols = ["period"]
        if group_by_columns:
            group_cols.extend(group_by_columns)
        
        # Aggregate
        agg_df = df.groupby(group_cols).agg({
            value_column: ["count", "sum", "mean", "median"]
        }).reset_index()
        
        # Flatten multi-index columns
        agg_df.columns = [
            "_".join(col).strip("_") if col[1] else col[0]
            for col in agg_df.columns.values
        ]
        
        # Rename columns
        agg_df = agg_df.rename(columns={
            f"{value_column}_count": "transaction_count",
            f"{value_column}_sum": "transaction_value",
            f"{value_column}_mean": "avg_transaction_value",
            f"{value_column}_median": "median_transaction_value"
        })
        
        # Add period metadata
        agg_df["period_type"] = period.value
        
        return agg_df
    
    def _get_period_column(self, dates: pd.Series, period: AggregationPeriod) -> pd.Series:
        """Get period column based on aggregation period.
        
        Args:
            dates: Series of dates
            period: Aggregation period
        
        Returns:
            Series of period identifiers
        """
        if period == AggregationPeriod.DAILY:
            return dates.dt.date
        elif period == AggregationPeriod.WEEKLY:
            # Week start (Monday)
            return dates.dt.to_period("W").dt.start_time.dt.date
        elif period == AggregationPeriod.MONTHLY:
            return dates.dt.to_period("M").dt.start_time.dt.date
        elif period == AggregationPeriod.QUARTERLY:
            return dates.dt.to_period("Q").dt.start_time.dt.date
        elif period == AggregationPeriod.YEARLY:
            return dates.dt.year
        else:
            raise ValueError(f"Unsupported period: {period}")
    
    def aggregate_by_customer(
        self,
        df: pd.DataFrame,
        date_column: str,
        period: AggregationPeriod,
        customer_column: str = "customer_key"
    ) -> pd.DataFrame:
        """Aggregate transactions by customer and time period.
        
        Args:
            df: DataFrame with transaction data
            date_column: Name of date column
            period: Aggregation period
            customer_column: Name of customer column
        
        Returns:
            Aggregated DataFrame per customer
        """
        return self.aggregate(
            df=df,
            date_column=date_column,
            period=period,
            group_by_columns=[customer_column]
        )
    
    def aggregate_by_category(
        self,
        df: pd.DataFrame,
        date_column: str,
        period: AggregationPeriod,
        category_column: str = "transaction_category"
    ) -> pd.DataFrame:
        """Aggregate transactions by category and time period.
        
        Args:
            df: DataFrame with transaction data
            date_column: Name of date column
            period: Aggregation period
            category_column: Name of category column
        
        Returns:
            Aggregated DataFrame per category
        """
        return self.aggregate(
            df=df,
            date_column=date_column,
            period=period,
            group_by_columns=[category_column]
        )
    
    def aggregate_by_channel(
        self,
        df: pd.DataFrame,
        date_column: str,
        period: AggregationPeriod,
        channel_column: str = "channel"
    ) -> pd.DataFrame:
        """Aggregate transactions by channel and time period.
        
        Args:
            df: DataFrame with transaction data
            date_column: Name of date column
            period: Aggregation period
            channel_column: Name of channel column
        
        Returns:
            Aggregated DataFrame per channel
        """
        return self.aggregate(
            df=df,
            date_column=date_column,
            period=period,
            group_by_columns=[channel_column]
        )
    
    def aggregate_multi_dimension(
        self,
        df: pd.DataFrame,
        date_column: str,
        period: AggregationPeriod,
        group_by_columns: List[str]
    ) -> pd.DataFrame:
        """Aggregate transactions by multiple dimensions and time period.
        
        Args:
            df: DataFrame with transaction data
            date_column: Name of date column
            period: Aggregation period
            group_by_columns: List of columns to group by
        
        Returns:
            Aggregated DataFrame
        """
        return self.aggregate(
            df=df,
            date_column=date_column,
            period=period,
            group_by_columns=group_by_columns
        )
    
    def calculate_period_growth(
        self,
        agg_df: pd.DataFrame,
        value_column: str = "transaction_value"
    ) -> pd.DataFrame:
        """Calculate period-over-period growth rates.
        
        Args:
            agg_df: Aggregated DataFrame from aggregate()
            value_column: Column to calculate growth for
        
        Returns:
            DataFrame with growth rates
        """
        # Sort by period
        agg_df = agg_df.sort_values("period")
        
        # Calculate growth
        agg_df["prev_period_value"] = agg_df.groupby(
            agg_df.columns.drop(["period", value_column, "transaction_count", 
                               "avg_transaction_value", "median_transaction_value", "period_type"]).tolist()
        )[value_column].shift(1)
        
        agg_df["growth_rate"] = (
            (agg_df[value_column] - agg_df["prev_period_value"]) / 
            agg_df["prev_period_value"].replace(0, pd.NA)
        ).fillna(0)
        
        agg_df["growth_percentage"] = (agg_df["growth_rate"] * 100).round(2)
        
        return agg_df.drop(columns=["prev_period_value"])
    
    def calculate_moving_average(
        self,
        agg_df: pd.DataFrame,
        value_column: str = "transaction_value",
        window: int = 3
    ) -> pd.DataFrame:
        """Calculate moving average over periods.
        
        Args:
            agg_df: Aggregated DataFrame from aggregate()
            value_column: Column to calculate MA for
            window: Window size for moving average
        
        Returns:
            DataFrame with moving average
        """
        agg_df = agg_df.sort_values("period")
        
        agg_df[f"{value_column}_ma_{window}"] = agg_df.groupby(
            agg_df.columns.drop(["period", value_column, "transaction_count", 
                               "avg_transaction_value", "median_transaction_value", "period_type"]).tolist()
        )[value_column].transform(
            lambda x: x.rolling(window=window, min_periods=1).mean()
        )
        
        return agg_df
