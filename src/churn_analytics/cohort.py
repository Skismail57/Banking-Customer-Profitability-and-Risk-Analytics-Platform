"""Cohort retention analysis."""

from datetime import date, timedelta
from typing import Dict, Any, Optional
import logging

import pandas as pd

from src.churn_analytics.base import ChurnBase

logger = logging.getLogger(__name__)


class CohortRetentionAnalyzer(ChurnBase):
    """Analyze cohort retention over time."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize cohort retention analyzer.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
    
    def create_cohorts(
        self,
        df: pd.DataFrame,
        customer_column: str = "customer_key",
        cohort_column: str = "cohort_month",
        period_column: str = "period_month"
    ) -> pd.DataFrame:
        """Create cohort groups based on acquisition month.
        
        Args:
            df: DataFrame with customer data
            customer_column: Name of customer column
            cohort_column: Name of cohort month column
            period_column: Name of period month column
        
        Returns:
            DataFrame with cohort assignments
        """
        df = df.copy()
        
        # Ensure cohort and period columns are datetime
        df[cohort_column] = pd.to_datetime(df[cohort_column])
        df[period_column] = pd.to_datetime(df[period_column])
        
        # Calculate cohort period number
        df["cohort_period"] = (
            (df[period_column].dt.year - df[cohort_column].dt.year) * 12 +
            (df[period_column].dt.month - df[cohort_column].dt.month)
        )
        
        return df
    
    def calculate_cohort_retention(
        self,
        df: pd.DataFrame,
        customer_column: str = "customer_key",
        cohort_column: str = "cohort_month",
        period_column: str = "period_month",
        activity_column: str = "has_activity"
    ) -> pd.DataFrame:
        """Calculate cohort retention rates over time.
        
        Args:
            df: DataFrame with customer data
            customer_column: Name of customer column
            cohort_column: Name of cohort month column
            period_column: Name of period month column
            activity_column: Name of activity indicator column
        
        Returns:
            DataFrame with cohort retention matrix
        """
        df = self.create_cohorts(df, customer_column, cohort_column, period_column)
        
        # Calculate retention per cohort per period
        cohort_data = df.groupby([cohort_column, "cohort_period"]).agg({
            customer_column: "nunique",
            activity_column: "sum"
        }).reset_index()
        
        cohort_data.columns = [cohort_column, "cohort_period", "total_customers", "active_customers"]
        
        # Calculate retention rate
        cohort_data["retention_rate"] = (
            cohort_data["active_customers"] / cohort_data["total_customers"] * 100
        )
        
        # Pivot to create retention matrix
        retention_matrix = cohort_data.pivot(
            index=cohort_column,
            columns="cohort_period",
            values="retention_rate"
        )
        
        return retention_matrix
    
    def calculate_cohort_size(
        self,
        df: pd.DataFrame,
        customer_column: str = "customer_key",
        cohort_column: str = "cohort_month"
    ) -> pd.DataFrame:
        """Calculate cohort sizes.
        
        Args:
            df: DataFrame with customer data
            customer_column: Name of customer column
            cohort_column: Name of cohort month column
        
        Returns:
            DataFrame with cohort sizes
        """
        cohort_sizes = df.groupby(cohort_column)[customer_column].nunique()
        
        return cohort_sizes.reset_index()
