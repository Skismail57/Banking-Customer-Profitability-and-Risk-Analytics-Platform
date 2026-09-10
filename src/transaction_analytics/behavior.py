"""Behavior analysis for transaction analytics."""

from datetime import date
from typing import Dict, Any, List, Optional
import logging

import pandas as pd
import numpy as np

from src.transaction_analytics.base import TransactionAnalyticsBase

logger = logging.getLogger(__name__)


class BehaviorAnalyzer(TransactionAnalyticsBase):
    """Analyze transaction behavior patterns."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize behavior analyzer.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
    
    def analyze_category_behavior(
        self,
        df: pd.DataFrame,
        date_column: str = "transaction_date",
        amount_column: str = "amount",
        category_column: str = "transaction_category"
    ) -> pd.DataFrame:
        """Analyze transaction behavior by category.
        
        Args:
            df: DataFrame with transaction data
            date_column: Name of date column
            amount_column: Name of amount column
            category_column: Name of category column
        
        Returns:
            DataFrame with category behavior metrics
        """
        logger.info("Analyzing category behavior")
        
        # Apply temporal safety
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])
        df = df[df[date_column] <= pd.Timestamp(self.as_of_date)]
        
        # Aggregate by category
        behavior_df = df.groupby(category_column).agg({
            amount_column: ["count", "sum", "mean", "median", "std"]
        }).reset_index()
        
        # Flatten columns
        behavior_df.columns = [
            "_".join(col).strip("_") if col[1] else col[0]
            for col in behavior_df.columns.values
        ]
        
        behavior_df = behavior_df.rename(columns={
            f"{amount_column}_count": "transaction_count",
            f"{amount_column}_sum": "transaction_value",
            f"{amount_column}_mean": "avg_transaction_value",
            f"{amount_column}_median": "median_transaction_value",
            f"{amount_column}_std": "std_transaction_value"
        })
        
        # Calculate percentage of total
        total_value = behavior_df["transaction_value"].sum()
        behavior_df["value_percentage"] = (behavior_df["transaction_value"] / total_value * 100).round(2)
        
        # Calculate inflow/outflow by category
        category_flow = df.groupby(category_column).apply(
            lambda x: pd.Series({
                "inflow": x[x[amount_column] > 0][amount_column].sum(),
                "outflow": abs(x[x[amount_column] < 0][amount_column].sum()),
                "debit_count": len(x[x[amount_column] < 0]),
                "credit_count": len(x[x[amount_column] > 0])
            })
        ).reset_index()
        
        behavior_df = behavior_df.merge(category_flow, on=category_column, how="left")
        
        return behavior_df.sort_values("transaction_value", ascending=False)
    
    def analyze_channel_behavior(
        self,
        df: pd.DataFrame,
        date_column: str = "transaction_date",
        amount_column: str = "amount",
        channel_column: str = "channel"
    ) -> pd.DataFrame:
        """Analyze transaction behavior by channel.
        
        Args:
            df: DataFrame with transaction data
            date_column: Name of date column
            amount_column: Name of amount column
            channel_column: Name of channel column
        
        Returns:
            DataFrame with channel behavior metrics
        """
        logger.info("Analyzing channel behavior")
        
        # Apply temporal safety
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])
        df = df[df[date_column] <= pd.Timestamp(self.as_of_date)]
        
        # Aggregate by channel
        behavior_df = df.groupby(channel_column).agg({
            amount_column: ["count", "sum", "mean", "median"]
        }).reset_index()
        
        # Flatten columns
        behavior_df.columns = [
            "_".join(col).strip("_") if col[1] else col[0]
            for col in behavior_df.columns.values
        ]
        
        behavior_df = behavior_df.rename(columns={
            f"{amount_column}_count": "transaction_count",
            f"{amount_column}_sum": "transaction_value",
            f"{amount_column}_mean": "avg_transaction_value",
            f"{amount_column}_median": "median_transaction_value"
        })
        
        # Calculate percentage of total
        total_value = behavior_df["transaction_value"].sum()
        behavior_df["value_percentage"] = (behavior_df["transaction_value"] / total_value * 100).round(2)
        
        return behavior_df.sort_values("transaction_value", ascending=False)
    
    def analyze_geographic_behavior(
        self,
        df: pd.DataFrame,
        date_column: str = "transaction_date",
        amount_column: str = "amount",
        location_column: str = "location"
    ) -> pd.DataFrame:
        """Analyze transaction behavior by geographic location.
        
        Args:
            df: DataFrame with transaction data
            date_column: Name of date column
            amount_column: Name of amount column
            location_column: Name of location column
        
        Returns:
            DataFrame with geographic behavior metrics
        """
        logger.info("Analyzing geographic behavior")
        
        # Apply temporal safety
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])
        df = df[df[date_column] <= pd.Timestamp(self.as_of_date)]
        
        if location_column not in df.columns:
            logger.warning(f"Location column {location_column} not found")
            return pd.DataFrame()
        
        # Aggregate by location
        behavior_df = df.groupby(location_column).agg({
            amount_column: ["count", "sum", "mean"]
        }).reset_index()
        
        # Flatten columns
        behavior_df.columns = [
            "_".join(col).strip("_") if col[1] else col[0]
            for col in behavior_df.columns.values
        ]
        
        behavior_df = behavior_df.rename(columns={
            f"{amount_column}_count": "transaction_count",
            f"{amount_column}_sum": "transaction_value",
            f"{amount_column}_mean": "avg_transaction_value"
        })
        
        return behavior_df.sort_values("transaction_value", ascending=False)
    
    def analyze_debit_credit_behavior(
        self,
        df: pd.DataFrame,
        date_column: str = "transaction_date",
        amount_column: str = "amount"
    ) -> Dict[str, Any]:
        """Analyze debit vs credit transaction behavior.
        
        Args:
            df: DataFrame with transaction data
            date_column: Name of date column
            amount_column: Name of amount column
        
        Returns:
            Dictionary with debit/credit behavior metrics
        """
        logger.info("Analyzing debit vs credit behavior")
        
        # Apply temporal safety
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])
        df = df[df[date_column] <= pd.Timestamp(self.as_of_date)]
        
        # Separate debit and credit
        debit_df = df[df[amount_column] < 0]
        credit_df = df[df[amount_column] > 0]
        
        behavior = {
            "debit": {
                "count": len(debit_df),
                "total_value": abs(debit_df[amount_column].sum()),
                "avg_value": abs(debit_df[amount_column].mean()) if len(debit_df) > 0 else 0,
                "median_value": abs(debit_df[amount_column].median()) if len(debit_df) > 0 else 0,
            },
            "credit": {
                "count": len(credit_df),
                "total_value": credit_df[amount_column].sum(),
                "avg_value": credit_df[amount_column].mean() if len(credit_df) > 0 else 0,
                "median_value": credit_df[amount_column].median() if len(credit_df) > 0 else 0,
            },
            "ratios": {
                "debit_to_credit_count": len(debit_df) / len(credit_df) if len(credit_df) > 0 else 0,
                "debit_to_credit_value": abs(debit_df[amount_column].sum()) / credit_df[amount_column].sum() if len(credit_df) > 0 and credit_df[amount_column].sum() > 0 else 0,
            }
        }
        
        return behavior
    
    def analyze_inflow_outflow(
        self,
        df: pd.DataFrame,
        date_column: str = "transaction_date",
        amount_column: str = "amount"
    ) -> Dict[str, Any]:
        """Analyze inflow vs outflow patterns.
        
        Args:
            df: DataFrame with transaction data
            date_column: Name of date column
            amount_column: Name of amount column
        
        Returns:
            Dictionary with inflow/outflow metrics
        """
        logger.info("Analyzing inflow vs outflow")
        
        # Apply temporal safety
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])
        df = df[df[date_column] <= pd.Timestamp(self.as_of_date)]
        
        total_inflow = df[df[amount_column] > 0][amount_column].sum()
        total_outflow = abs(df[df[amount_column] < 0][amount_column].sum())
        net_flow = total_inflow - total_outflow
        
        return {
            "total_inflow": total_inflow,
            "total_outflow": total_outflow,
            "net_flow": net_flow,
            "flow_ratio": total_inflow / total_outflow if total_outflow > 0 else float('inf'),
            "net_flow_percentage": (net_flow / total_inflow * 100) if total_inflow > 0 else 0,
        }
