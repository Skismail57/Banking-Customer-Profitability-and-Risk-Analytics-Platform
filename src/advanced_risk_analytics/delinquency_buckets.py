"""Delinquency buckets."""

from typing import Dict, Any, List
import logging

import pandas as pd
import numpy as np

from src.advanced_risk_analytics.base import RiskBase

logger = logging.getLogger(__name__)


class DelinquencyBuckets(RiskBase):
    """Categorize customers into delinquency buckets."""
    
    def categorize_delinquency(
        self,
        df: pd.DataFrame,
        dpd_column: str = "days_past_due"
    ) -> pd.DataFrame:
        """Categorize customers into delinquency buckets.
        
        Args:
            df: DataFrame with customer data
            dpd_column: Name of DPD column
        
        Returns:
            DataFrame with delinquency bucket column
        """
        df = df.copy()
        
        conditions = [
            df[dpd_column] <= self.thresholds.delinquency_current,
            (df[dpd_column] > self.thresholds.delinquency_current) & (df[dpd_column] <= self.thresholds.delinquency_30_days),
            (df[dpd_column] > self.thresholds.delinquency_30_days) & (df[dpd_column] <= self.thresholds.delinquency_60_days),
            (df[dpd_column] > self.thresholds.delinquency_60_days) & (df[dpd_column] <= self.thresholds.delinquency_90_days),
            df[dpd_column] > self.thresholds.delinquency_90_days
        ]
        
        choices = ["current", "30_days", "60_days", "90_days", "120_plus_days"]
        
        df["delinquency_bucket"] = np.select(conditions, choices, default="current")
        
        return df
    
    def calculate_bucket_distribution(
        self,
        df: pd.DataFrame,
        dpd_column: str = "days_past_due",
        exposure_column: str = "exposure_amount"
    ) -> Dict[str, Any]:
        """Calculate distribution across delinquency buckets.
        
        Args:
            df: DataFrame with customer data
            dpd_column: Name of DPD column
            exposure_column: Name of exposure column
        
        Returns:
            Dictionary with bucket distribution
        """
        df = self.categorize_delinquency(df, dpd_column)
        
        distribution = df.groupby("delinquency_bucket").agg({
            exposure_column: "sum"
        })
        distribution["customer_count"] = df.groupby("delinquency_bucket").size()
        
        distribution["exposure_pct"] = distribution[exposure_column] / df[exposure_column].sum()
        distribution["customer_pct"] = distribution["customer_count"] / len(df)
        
        return {
            "distribution": distribution.to_dict("index"),
            "total_exposure": df[exposure_column].sum(),
            "total_customers": len(df)
        }
