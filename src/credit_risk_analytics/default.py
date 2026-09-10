"""Default indicators and credit behavior trends."""

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


class DefaultAnalyzer(CreditRiskBase):
    """Analyze default indicators and credit behavior trends."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize default analyzer.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
    
    def calculate_default_flag(
        self,
        df: pd.DataFrame,
        default_status_column: str = "default_status",
        dpd_column: str = "days_past_due",
        default_dpd_threshold: int = 90
    ) -> RiskIndicatorValue:
        """Calculate default flag.
        
        Args:
            df: DataFrame with loan data
            default_status_column: Name of default status column
            dpd_column: Name of days past due column
            default_dpd_threshold: DPD threshold for default
        
        Returns:
            RiskIndicatorValue with default flag
        """
        # Try to use explicit default status first
        if default_status_column in df.columns:
            default_count = df[default_status_column].isin(["default", "Y", "yes", True]).sum()
            has_default = default_count > 0
        elif dpd_column in df.columns:
            # Use DPD threshold as fallback
            max_dpd = df[dpd_column].max()
            has_default = max_dpd >= default_dpd_threshold
        else:
            logger.warning("No default status or DPD data available")
            return RiskIndicatorValue(
                indicator=RiskIndicator.DEFAULT_FLAG,
                value=0.0,
                is_available=False,
                data_completeness=0.0,
                confidence=0.0,
                metadata={"reason": "No default data available"}
            )
        
        return RiskIndicatorValue(
            indicator=RiskIndicator.DEFAULT_FLAG,
            value=1.0 if has_default else 0.0,
            is_available=True,
            data_completeness=1.0,
            confidence=0.9,
            metadata={
                "has_default": has_default,
                "used_dpd_fallback": default_status_column not in df.columns
            }
        )
    
    def calculate_default_count(
        self,
        df: pd.DataFrame,
        default_status_column: str = "default_status",
        customer_column: str = "customer_key"
    ) -> RiskIndicatorValue:
        """Calculate count of defaults.
        
        Args:
            df: DataFrame with loan data
            default_status_column: Name of default status column
            customer_column: Name of customer column
        
        Returns:
            RiskIndicatorValue with default count
        """
        if default_status_column not in df.columns:
            logger.warning(f"Default status column {default_status_column} not found")
            return RiskIndicatorValue(
                indicator=RiskIndicator.DEFAULT_COUNT,
                value=0.0,
                is_available=False,
                data_completeness=0.0,
                confidence=0.0,
                metadata={"reason": f"Column {default_status_column} not found"}
            )
        
        # Count defaults per customer if customer column exists
        if customer_column in df.columns:
            default_count = df[df[default_status_column].isin(["default", "Y", "yes", True])].groupby(customer_column).size()
            total_defaults = default_count.sum()
        else:
            total_defaults = df[default_status_column].isin(["default", "Y", "yes", True]).sum()
        
        return RiskIndicatorValue(
            indicator=RiskIndicator.DEFAULT_COUNT,
            value=float(total_defaults),
            is_available=True,
            data_completeness=1.0,
            confidence=0.9,
            metadata={"total_defaults": total_defaults}
        )
    
    def calculate_recovery_rate(
        self,
        df: pd.DataFrame,
        recovery_amount_column: str = "recovery_amount",
        default_amount_column: str = "default_amount"
    ) -> RiskIndicatorValue:
        """Calculate recovery rate on defaults.
        
        Args:
            df: DataFrame with recovery data
            recovery_amount_column: Name of recovery amount column
            default_amount_column: Name of default amount column
        
        Returns:
            RiskIndicatorValue with recovery rate
        """
        if recovery_amount_column not in df.columns or default_amount_column not in df.columns:
            logger.warning("Required columns not found for recovery rate")
            return RiskIndicatorValue(
                indicator=RiskIndicator.RECOVERY_RATE,
                value=0.0,
                is_available=False,
                data_completeness=0.0,
                confidence=0.0,
                metadata={"reason": "Required columns not found"}
            )
        
        total_recovery = df[recovery_amount_column].sum()
        total_default = df[default_amount_column].sum()
        
        if total_default == 0:
            logger.warning("Total default amount is zero")
            return RiskIndicatorValue(
                indicator=RiskIndicator.RECOVERY_RATE,
                value=0.0,
                is_available=False,
                data_completeness=0.0,
                confidence=0.0,
                metadata={"reason": "Total default amount is zero"}
            )
        
        recovery_rate = (total_recovery / total_default) * 100
        
        return RiskIndicatorValue(
            indicator=RiskIndicator.RECOVERY_RATE,
            value=recovery_rate,
            is_available=True,
            data_completeness=1.0,
            confidence=0.8,
            metadata={
                "total_recovery": total_recovery,
                "total_default": total_default
            }
        )
    
    def calculate_balance_trend(
        self,
        df: pd.DataFrame,
        balance_column: str = "current_balance",
        date_column: str = "as_of_date"
    ) -> RiskIndicatorValue:
        """Calculate balance trend over time.
        
        Args:
            df: DataFrame with balance data
            balance_column: Name of balance column
            date_column: Name of date column
        
        Returns:
            RiskIndicatorValue with balance trend
        """
        if date_column not in df.columns:
            logger.warning(f"Date column {date_column} not found")
            return RiskIndicatorValue(
                indicator=RiskIndicator.BALANCE_TREND,
                value=0.0,
                is_available=False,
                data_completeness=0.0,
                confidence=0.0,
                metadata={"reason": f"Column {date_column} not found"}
            )
        
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])
        df = df.sort_values(date_column)
        
        if len(df) < 2:
            return RiskIndicatorValue(
                indicator=RiskIndicator.BALANCE_TREND,
                value=0.0,
                is_available=False,
                data_completeness=0.0,
                confidence=0.0,
                metadata={"reason": "Insufficient data points"}
            )
        
        # Simple trend: last - first
        trend = df[balance_column].iloc[-1] - df[balance_column].iloc[0]
        
        return RiskIndicatorValue(
            indicator=RiskIndicator.BALANCE_TREND,
            value=trend,
            is_available=True,
            data_completeness=1.0,
            confidence=0.7,
            metadata={
                "period_count": len(df),
                "start_balance": df[balance_column].iloc[0],
                "end_balance": df[balance_column].iloc[-1]
            }
        )
