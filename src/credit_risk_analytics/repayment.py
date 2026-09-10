"""Repayment history analysis."""

from datetime import date
from typing import Dict, Any, Optional
import logging

import pandas as pd

from src.credit_risk_analytics.base import (
    CreditRiskBase,
    RiskIndicator,
    RiskIndicatorValue,
)

logger = logging.getLogger(__name__)


class RepaymentHistoryAnalyzer(CreditRiskBase):
    """Analyze repayment history."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize repayment history analyzer.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
    
    def calculate_on_time_payment_rate(
        self,
        df: pd.DataFrame,
        payment_date_column: str = "payment_date",
        due_date_column: str = "due_date",
        grace_period_days: int = 0
    ) -> RiskIndicatorValue:
        """Calculate on-time payment rate.
        
        Args:
            df: DataFrame with payment data
            payment_date_column: Name of payment date column
            due_date_column: Name of due date column
            grace_period_days: Grace period in days
        
        Returns:
            RiskIndicatorValue with on-time payment rate
        """
        if payment_date_column not in df.columns or due_date_column not in df.columns:
            logger.warning("Required columns not found")
            return RiskIndicatorValue(
                indicator=RiskIndicator.ON_TIME_PAYMENT_RATE,
                value=0.0,
                is_available=False,
                data_completeness=0.0,
                confidence=0.0,
                metadata={"reason": "Required columns not found"}
            )
        
        df = df.copy()
        df[payment_date_column] = pd.to_datetime(df[payment_date_column])
        df[due_date_column] = pd.to_datetime(df[due_date_column])
        
        # Calculate days difference
        df["days_diff"] = (df[payment_date_column] - df[due_date_column]).dt.days
        
        # On-time if payment date <= due date + grace period
        df["on_time"] = df["days_diff"] <= grace_period_days
        
        if len(df) == 0:
            return RiskIndicatorValue(
                indicator=RiskIndicator.ON_TIME_PAYMENT_RATE,
                value=0.0,
                is_available=False,
                data_completeness=0.0,
                confidence=0.0,
                metadata={"reason": "No payment data"}
            )
        
        on_time_rate = (df["on_time"].sum() / len(df)) * 100
        
        return RiskIndicatorValue(
            indicator=RiskIndicator.ON_TIME_PAYMENT_RATE,
            value=on_time_rate,
            is_available=True,
            data_completeness=1.0,
            confidence=0.9,
            metadata={
                "total_payments": len(df),
                "on_time_payments": df["on_time"].sum(),
                "grace_period_days": grace_period_days
            }
        )
    
    def calculate_late_payment_count(
        self,
        df: pd.DataFrame,
        payment_date_column: str = "payment_date",
        due_date_column: str = "due_date",
        grace_period_days: int = 0
    ) -> RiskIndicatorValue:
        """Calculate late payment count.
        
        Args:
            df: DataFrame with payment data
            payment_date_column: Name of payment date column
            due_date_column: Name of due date column
            grace_period_days: Grace period in days
        
        Returns:
            RiskIndicatorValue with late payment count
        """
        if payment_date_column not in df.columns or due_date_column not in df.columns:
            logger.warning("Required columns not found")
            return RiskIndicatorValue(
                indicator=RiskIndicator.LATE_PAYMENT_COUNT,
                value=0.0,
                is_available=False,
                data_completeness=0.0,
                confidence=0.0,
                metadata={"reason": "Required columns not found"}
            )
        
        df = df.copy()
        df[payment_date_column] = pd.to_datetime(df[payment_date_column])
        df[due_date_column] = pd.to_datetime(df[due_date_column])
        
        # Calculate days difference
        df["days_diff"] = (df[payment_date_column] - df[due_date_column]).dt.days
        
        # Late if payment date > due date + grace period
        df["late"] = df["days_diff"] > grace_period_days
        
        late_count = df["late"].sum()
        
        return RiskIndicatorValue(
            indicator=RiskIndicator.LATE_PAYMENT_COUNT,
            value=float(late_count),
            is_available=True,
            data_completeness=1.0,
            confidence=0.9,
            metadata={
                "total_payments": len(df),
                "late_payments": late_count,
                "grace_period_days": grace_period_days
            }
        )
    
    def calculate_missed_payment_count(
        self,
        df: pd.DataFrame,
        payment_date_column: str = "payment_date",
        due_date_column: str = "due_date",
        missed_threshold_days: int = 30
    ) -> RiskIndicatorValue:
        """Calculate missed payment count (severely late).
        
        Args:
            df: DataFrame with payment data
            payment_date_column: Name of payment date column
            due_date_column: Name of due date column
            missed_threshold_days: Threshold for missed payment
        
        Returns:
            RiskIndicatorValue with missed payment count
        """
        if payment_date_column not in df.columns or due_date_column not in df.columns:
            logger.warning("Required columns not found")
            return RiskIndicatorValue(
                indicator=RiskIndicator.MISSED_PAYMENT_COUNT,
                value=0.0,
                is_available=False,
                data_completeness=0.0,
                confidence=0.0,
                metadata={"reason": "Required columns not found"}
            )
        
        df = df.copy()
        df[payment_date_column] = pd.to_datetime(df[payment_date_column])
        df[due_date_column] = pd.to_datetime(df[due_date_column])
        
        # Calculate days difference
        df["days_diff"] = (df[payment_date_column] - df[due_date_column]).dt.days
        
        # Missed if payment date > due date + threshold
        df["missed"] = df["days_diff"] > missed_threshold_days
        
        missed_count = df["missed"].sum()
        
        return RiskIndicatorValue(
            indicator=RiskIndicator.MISSED_PAYMENT_COUNT,
            value=float(missed_count),
            is_available=True,
            data_completeness=1.0,
            confidence=0.9,
            metadata={
                "total_payments": len(df),
                "missed_payments": missed_count,
                "missed_threshold_days": missed_threshold_days
            }
        )
