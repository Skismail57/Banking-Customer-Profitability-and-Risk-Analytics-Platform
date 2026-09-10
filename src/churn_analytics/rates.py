"""Churn rate and retention rate calculations."""

from datetime import date, timedelta
from typing import Dict, Any, Optional
import logging

import pandas as pd

from src.churn_analytics.base import ChurnBase

logger = logging.getLogger(__name__)


class ChurnRateCalculator(ChurnBase):
    """Calculate churn and retention rates."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize churn rate calculator.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
    
    def calculate_churn_rate(
        self,
        df: pd.DataFrame,
        customer_column: str = "customer_key",
        churn_column: str = "is_churned",
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Calculate churn rate for a period.
        
        Args:
            df: DataFrame with customer data
            customer_column: Name of customer column
            churn_column: Name of churn indicator column
            period_days: Period in days for calculation
        
        Returns:
            Dictionary with churn rate metrics
        """
        total_customers = len(df)
        churned_customers = df[churn_column].sum()
        
        if total_customers == 0:
            return {
                "churn_rate": 0.0,
                "total_customers": 0,
                "churned_customers": 0,
                "retained_customers": 0
            }
        
        churn_rate = (churned_customers / total_customers) * 100
        retained_customers = total_customers - churned_customers
        
        return {
            "churn_rate": churn_rate,
            "total_customers": total_customers,
            "churned_customers": int(churned_customers),
            "retained_customers": retained_customers,
            "period_days": period_days
        }
    
    def calculate_retention_rate(
        self,
        df: pd.DataFrame,
        customer_column: str = "customer_key",
        churn_column: str = "is_churned",
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Calculate retention rate for a period.
        
        Args:
            df: DataFrame with customer data
            customer_column: Name of customer column
            churn_column: Name of churn indicator column
            period_days: Period in days for calculation
        
        Returns:
            Dictionary with retention rate metrics
        """
        total_customers = len(df)
        churned_customers = df[churn_column].sum()
        
        if total_customers == 0:
            return {
                "retention_rate": 0.0,
                "total_customers": 0,
                "retained_customers": 0
            }
        
        retained_customers = total_customers - churned_customers
        retention_rate = (retained_customers / total_customers) * 100
        
        return {
            "retention_rate": retention_rate,
            "total_customers": total_customers,
            "retained_customers": retained_customers,
            "churned_customers": int(churned_customers),
            "period_days": period_days
        }
    
    def calculate_monthly_churn_rates(
        self,
        df: pd.DataFrame,
        customer_column: str = "customer_key",
        churn_column: str = "is_churned",
        date_column: str = "period_date"
    ) -> pd.DataFrame:
        """Calculate monthly churn rates.
        
        Args:
            df: DataFrame with customer data
            customer_column: Name of customer column
            churn_column: Name of churn indicator column
            date_column: Name of date column
        
        Returns:
            DataFrame with monthly churn rates
        """
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])
        df["month"] = df[date_column].dt.to_period("M").dt.start_time.dt.date
        
        results = []
        
        for month, month_df in df.groupby("month"):
            churn_metrics = self.calculate_churn_rate(
                month_df, customer_column, churn_column
            )
            churn_metrics["month"] = month
            results.append(churn_metrics)
        
        return pd.DataFrame(results).sort_values("month")
