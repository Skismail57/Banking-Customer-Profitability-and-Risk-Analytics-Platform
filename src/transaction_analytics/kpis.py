"""Transaction KPI calculators."""

from datetime import date, timedelta
from typing import Dict, Any, List, Optional
import logging

import pandas as pd
import numpy as np

from src.transaction_analytics.base import (
    TransactionAnalyticsBase,
    TransactionKPI,
)

logger = logging.getLogger(__name__)


class TransactionKPICalculator(TransactionAnalyticsBase):
    """Calculate transaction KPIs at various levels."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize KPI calculator.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
    
    def calculate_kpis(
        self,
        df: pd.DataFrame,
        date_column: str = "transaction_date",
        amount_column: str = "amount",
        period_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """Calculate all transaction KPIs for a dataset.
        
        Args:
            df: DataFrame with transaction data
            date_column: Name of date column
            amount_column: Name of amount column
            period_days: Optional period in days for frequency calculation
        
        Returns:
            Dictionary of KPI values
        """
        logger.info(f"Calculating transaction KPIs for {len(df)} transactions")
        
        # Apply temporal safety
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])
        df = df[df[date_column] <= pd.Timestamp(self.as_of_date)]
        
        kpis = {}
        
        # Basic KPIs
        kpis["transaction_count"] = len(df)
        kpis["transaction_value"] = df[amount_column].sum()
        kpis["avg_transaction_value"] = df[amount_column].mean()
        kpis["median_transaction_value"] = df[amount_column].median()
        
        # Frequency
        if period_days:
            kpis["transaction_frequency"] = len(df) / period_days
        elif len(df) > 0:
            date_range = (df[date_column].max() - df[date_column].min()).days + 1
            kpis["transaction_frequency"] = len(df) / max(date_range, 1)
        else:
            kpis["transaction_frequency"] = 0
        
        # Inflow/Outflow
        kpis["total_inflow"] = df[df[amount_column] > 0][amount_column].sum()
        kpis["outflow"] = abs(df[df[amount_column] < 0][amount_column].sum())
        kpis["net_flow"] = kpis["total_inflow"] - kpis["outflow"]
        
        # Debit/Credit
        kpis["debit_count"] = len(df[df[amount_column] < 0])
        kpis["credit_count"] = len(df[df[amount_column] > 0])
        kpis["debit_value"] = abs(df[df[amount_column] < 0][amount_column].sum())
        kpis["credit_value"] = df[df[amount_column] > 0][amount_column].sum()
        
        # Ratios
        if kpis["debit_count"] > 0:
            kpis["debit_to_credit_ratio"] = kpis["debit_count"] / kpis["credit_count"]
        else:
            kpis["debit_to_credit_ratio"] = 0
        
        if kpis["credit_value"] > 0:
            kpis["credit_to_debit_value_ratio"] = kpis["credit_value"] / kpis["debit_value"] if kpis["debit_value"] > 0 else float('inf')
        else:
            kpis["credit_to_debit_value_ratio"] = 0
        
        return kpis
    
    def calculate_kpis_by_customer(
        self,
        df: pd.DataFrame,
        date_column: str = "transaction_date",
        amount_column: str = "amount",
        customer_column: str = "customer_key"
    ) -> pd.DataFrame:
        """Calculate KPIs per customer.
        
        Args:
            df: DataFrame with transaction data
            date_column: Name of date column
            amount_column: Name of amount column
            customer_column: Name of customer column
        
        Returns:
            DataFrame with KPIs per customer
        """
        logger.info(f"Calculating KPIs per customer for {len(df)} transactions")
        
        # Apply temporal safety
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])
        df = df[df[date_column] <= pd.Timestamp(self.as_of_date)]
        
        # Aggregate by customer
        kpis_df = df.groupby(customer_column).agg({
            amount_column: ["count", "sum", "mean", "median"]
        }).reset_index()
        
        # Flatten columns
        kpis_df.columns = [
            "_".join(col).strip("_") if col[1] else col[0]
            for col in kpis_df.columns.values
        ]
        
        kpis_df = kpis_df.rename(columns={
            f"{amount_column}_count": "transaction_count",
            f"{amount_column}_sum": "transaction_value",
            f"{amount_column}_mean": "avg_transaction_value",
            f"{amount_column}_median": "median_transaction_value"
        })
        
        # Calculate inflow/outflow per customer
        inflow_outflow = df.groupby(customer_column).apply(
            lambda x: pd.Series({
                "total_inflow": x[x[amount_column] > 0][amount_column].sum(),
                "outflow": abs(x[x[amount_column] < 0][amount_column].sum()),
                "debit_count": len(x[x[amount_column] < 0]),
                "credit_count": len(x[x[amount_column] > 0])
            })
        ).reset_index()
        
        kpis_df = kpis_df.merge(inflow_outflow, on=customer_column, how="left")
        
        kpis_df["net_flow"] = kpis_df["total_inflow"] - kpis_df["outflow"]
        
        return kpis_df
    
    def calculate_kpis_by_period(
        self,
        df: pd.DataFrame,
        date_column: str = "transaction_date",
        amount_column: str = "amount",
        period: str = "monthly"  # daily, weekly, monthly, quarterly, yearly
    ) -> pd.DataFrame:
        """Calculate KPIs by time period.
        
        Args:
            df: DataFrame with transaction data
            date_column: Name of date column
            amount_column: Name of amount column
            period: Aggregation period
        
        Returns:
            DataFrame with KPIs per period
        """
        logger.info(f"Calculating KPIs by {period} period")
        
        # Apply temporal safety
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])
        df = df[df[date_column] <= pd.Timestamp(self.as_of_date)]
        
        # Add period column
        if period == "daily":
            df["period"] = df[date_column].dt.date
        elif period == "weekly":
            df["period"] = df[date_column].dt.to_period("W").dt.start_time.dt.date
        elif period == "monthly":
            df["period"] = df[date_column].dt.to_period("M").dt.start_time.dt.date
        elif period == "quarterly":
            df["period"] = df[date_column].dt.to_period("Q").dt.start_time.dt.date
        elif period == "yearly":
            df["period"] = df[date_column].dt.year
        else:
            raise ValueError(f"Unsupported period: {period}")
        
        # Aggregate by period
        kpis_df = df.groupby("period").agg({
            amount_column: ["count", "sum", "mean", "median"]
        }).reset_index()
        
        # Flatten columns
        kpis_df.columns = [
            "_".join(col).strip("_") if col[1] else col[0]
            for col in kpis_df.columns.values
        ]
        
        kpis_df = kpis_df.rename(columns={
            f"{amount_column}_count": "transaction_count",
            f"{amount_column}_sum": "transaction_value",
            f"{amount_column}_mean": "avg_transaction_value",
            f"{amount_column}_median": "median_transaction_value"
        })
        
        # Calculate inflow/outflow per period
        inflow_outflow = df.groupby("period").apply(
            lambda x: pd.Series({
                "total_inflow": x[x[amount_column] > 0][amount_column].sum(),
                "outflow": abs(x[x[amount_column] < 0][amount_column].sum()),
                "debit_count": len(x[x[amount_column] < 0]),
                "credit_count": len(x[x[amount_column] > 0])
            })
        ).reset_index()
        
        kpis_df = kpis_df.merge(inflow_outflow, on="period", how="left")
        
        kpis_df["net_flow"] = kpis_df["total_inflow"] - kpis_df["outflow"]
        
        kpis_df["period_type"] = period
        
        return kpis_df.sort_values("period")
