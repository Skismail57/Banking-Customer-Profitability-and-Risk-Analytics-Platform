"""Payment behavior and delinquency analysis."""

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


class PaymentBehaviorAnalyzer(CreditRiskBase):
    """Analyze payment behavior and delinquency."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize payment behavior analyzer.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
    
    def calculate_days_past_due(
        self,
        df: pd.DataFrame,
        dpd_column: str = "days_past_due"
    ) -> RiskIndicatorValue:
        """Calculate maximum days past due.
        
        Args:
            df: DataFrame with loan data
            dpd_column: Name of days past due column
        
        Returns:
            RiskIndicatorValue with days past due
        """
        if dpd_column not in df.columns:
            logger.warning(f"DPD column {dpd_column} not found")
            return RiskIndicatorValue(
                indicator=RiskIndicator.DAYS_PAST_DUE,
                value=0.0,
                is_available=False,
                data_completeness=0.0,
                confidence=0.0,
                metadata={"reason": f"Column {dpd_column} not found"}
            )
        
        max_dpd = df[dpd_column].max()
        
        return RiskIndicatorValue(
            indicator=RiskIndicator.DAYS_PAST_DUE,
            value=max_dpd,
            is_available=True,
            data_completeness=1.0,
            confidence=0.9,
            metadata={"row_count": len(df)}
        )
    
    def calculate_delinquency_status(
        self,
        df: pd.DataFrame,
        dpd_column: str = "days_past_due"
    ) -> RiskIndicatorValue:
        """Calculate delinquency status category.
        
        Args:
            df: DataFrame with loan data
            dpd_column: Name of days past due column
        
        Returns:
            RiskIndicatorValue with delinquency status
        """
        if dpd_column not in df.columns:
            logger.warning(f"DPD column {dpd_column} not found")
            return RiskIndicatorValue(
                indicator=RiskIndicator.DELINQUENCY_STATUS,
                value=0.0,
                is_available=False,
                data_completeness=0.0,
                confidence=0.0,
                metadata={"reason": f"Column {dpd_column} not found"}
            )
        
        max_dpd = df[dpd_column].max()
        
        # Classify delinquency status
        if max_dpd == 0:
            status = 0  # Current
        elif max_dpd <= 30:
            status = 1  # 1-30 days past due
        elif max_dpd <= 60:
            status = 2  # 31-60 days past due
        elif max_dpd <= 90:
            status = 3  # 61-90 days past due
        else:
            status = 4  # 90+ days past due
        
        return RiskIndicatorValue(
            indicator=RiskIndicator.DELINQUENCY_STATUS,
            value=float(status),
            is_available=True,
            data_completeness=1.0,
            confidence=0.9,
            metadata={
                "max_dpd": max_dpd,
                "status_description": self._get_delinquency_description(status)
            }
        )
    
    def _get_delinquency_description(self, status: int) -> str:
        """Get description for delinquency status.
        
        Args:
            status: Delinquency status code
        
        Returns:
            Description string
        """
        descriptions = {
            0: "Current",
            1: "1-30 Days Past Due",
            2: "31-60 Days Past Due",
            3: "61-90 Days Past Due",
            4: "90+ Days Past Due"
        }
        return descriptions.get(status, "Unknown")
    
    def calculate_payment_frequency(
        self,
        df: pd.DataFrame,
        payment_date_column: str = "payment_date",
        period_days: int = 30
    ) -> RiskIndicatorValue:
        """Calculate payment frequency (payments per period).
        
        Args:
            df: DataFrame with payment data
            payment_date_column: Name of payment date column
            period_days: Period in days for frequency calculation
        
        Returns:
            RiskIndicatorValue with payment frequency
        """
        if payment_date_column not in df.columns:
            logger.warning(f"Payment date column {payment_date_column} not found")
            return RiskIndicatorValue(
                indicator=RiskIndicator.PAYMENT_FREQUENCY,
                value=0.0,
                is_available=False,
                data_completeness=0.0,
                confidence=0.0,
                metadata={"reason": f"Column {payment_date_column} not found"}
            )
        
        df = df.copy()
        df[payment_date_column] = pd.to_datetime(df[payment_date_column])
        
        # Calculate date range
        date_range = (df[payment_date_column].max() - df[payment_date_column].min()).days
        if date_range == 0:
            date_range = 1
        
        payment_count = len(df)
        frequency = payment_count / (date_range / period_days)
        
        return RiskIndicatorValue(
            indicator=RiskIndicator.PAYMENT_FREQUENCY,
            value=frequency,
            is_available=True,
            data_completeness=1.0,
            confidence=0.8,
            metadata={
                "payment_count": payment_count,
                "date_range_days": date_range,
                "period_days": period_days
            }
        )
