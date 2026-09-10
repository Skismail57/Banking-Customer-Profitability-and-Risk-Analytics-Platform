"""Trend analysis for transaction analytics."""

from datetime import date
from typing import Dict, Any, List, Optional
import logging

import pandas as pd
import numpy as np

from src.transaction_analytics.base import TransactionAnalyticsBase

logger = logging.getLogger(__name__)


class TrendAnalyzer(TransactionAnalyticsBase):
    """Analyze transaction trends over time."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize trend analyzer.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
    
    def calculate_trend_metrics(
        self,
        agg_df: pd.DataFrame,
        value_column: str = "transaction_value"
    ) -> Dict[str, Any]:
        """Calculate trend metrics from aggregated data.
        
        Args:
            agg_df: Aggregated DataFrame with period and value columns
            value_column: Column to analyze
        
        Returns:
            Dictionary of trend metrics
        """
        logger.info("Calculating trend metrics")
        
        agg_df = agg_df.sort_values("period")
        values = agg_df[value_column].values
        
        if len(values) < 2:
            return {"error": "Insufficient data for trend analysis"}
        
        # Calculate trend metrics
        trend_metrics = {
            "current_value": values[-1],
            "previous_value": values[-2] if len(values) >= 2 else None,
            "min_value": values.min(),
            "max_value": values.max(),
            "mean_value": values.mean(),
            "std_value": values.std(),
            "trend_direction": self._determine_trend_direction(values),
            "growth_rate": self._calculate_growth_rate(values),
            "volatility": values.std() / values.mean() if values.mean() != 0 else 0,
            "momentum": self._calculate_momentum(values),
        }
        
        return trend_metrics
    
    def _determine_trend_direction(self, values: np.ndarray) -> str:
        """Determine overall trend direction.
        
        Args:
            values: Array of values
        
        Returns:
            Trend direction: increasing, decreasing, stable
        """
        if len(values) < 2:
            return "unknown"
        
        # Calculate linear trend
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        if slope > 0.01 * values.mean():
            return "increasing"
        elif slope < -0.01 * values.mean():
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_growth_rate(self, values: np.ndarray) -> float:
        """Calculate compound annual growth rate.
        
        Args:
            values: Array of values
        
        Returns:
            Growth rate
        """
        if len(values) < 2:
            return 0.0
        
        if values[0] <= 0:
            return 0.0
        
        return (values[-1] / values[0]) - 1
    
    def _calculate_momentum(self, values: np.ndarray, window: int = 3) -> float:
        """Calculate momentum (recent trend).
        
        Args:
            values: Array of values
            window: Window size for momentum
        
        Returns:
            Momentum value
        """
        if len(values) < window:
            return 0.0
        
        recent = values[-window:]
        return (recent[-1] - recent[0]) / recent[0] if recent[0] != 0 else 0.0
    
    def detect_seasonality(
        self,
        agg_df: pd.DataFrame,
        value_column: str = "transaction_value",
        period_type: str = "monthly"
    ) -> Dict[str, Any]:
        """Detect seasonal patterns in transaction data.
        
        Args:
            agg_df: Aggregated DataFrame
            value_column: Column to analyze
            period_type: Type of period (monthly, quarterly)
        
        Returns:
            Dictionary with seasonality information
        """
        logger.info(f"Detecting seasonality for {period_type} data")
        
        agg_df = agg_df.copy()
        
        if period_type == "monthly":
            agg_df["month"] = pd.to_datetime(agg_df["period"]).dt.month
            seasonal_avg = agg_df.groupby("month")[value_column].mean()
            
            # Calculate seasonality strength
            overall_mean = agg_df[value_column].mean()
            seasonal_variance = seasonal_avg.var()
            total_variance = agg_df[value_column].var()
            
            seasonality_strength = seasonal_variance / total_variance if total_variance > 0 else 0
            
            return {
                "seasonal_pattern": seasonal_avg.to_dict(),
                "peak_month": seasonal_avg.idxmax(),
                "trough_month": seasonal_avg.idxmin(),
                "seasonality_strength": seasonality_strength,
                "has_seasonality": seasonality_strength > 0.3
            }
        
        elif period_type == "quarterly":
            agg_df["quarter"] = pd.to_datetime(agg_df["period"]).dt.quarter
            seasonal_avg = agg_df.groupby("quarter")[value_column].mean()
            
            overall_mean = agg_df[value_column].mean()
            seasonal_variance = seasonal_avg.var()
            total_variance = agg_df[value_column].var()
            
            seasonality_strength = seasonal_variance / total_variance if total_variance > 0 else 0
            
            return {
                "seasonal_pattern": seasonal_avg.to_dict(),
                "peak_quarter": seasonal_avg.idxmax(),
                "trough_quarter": seasonal_avg.idxmin(),
                "seasonality_strength": seasonality_strength,
                "has_seasonality": seasonality_strength > 0.3
            }
        
        else:
            return {"error": f"Seasonality detection not supported for {period_type}"}
    
    def calculate_period_comparison(
        self,
        agg_df: pd.DataFrame,
        value_column: str = "transaction_value",
        compare_periods: int = 2
    ) -> pd.DataFrame:
        """Compare current period with previous periods.
        
        Args:
            agg_df: Aggregated DataFrame
            value_column: Column to compare
            compare_periods: Number of previous periods to compare
        
        Returns:
            DataFrame with comparison metrics
        """
        logger.info(f"Calculating period comparison with {compare_periods} previous periods")
        
        agg_df = agg_df.sort_values("period").copy()
        
        for i in range(1, compare_periods + 1):
            agg_df[f"prev_{i}_value"] = agg_df[value_column].shift(i)
            agg_df[f"vs_prev_{i}_pct"] = (
                (agg_df[value_column] - agg_df[f"prev_{i}_value"]) / 
                agg_df[f"prev_{i}_value"].replace(0, pd.NA)
            ) * 100
        
        return agg_df
