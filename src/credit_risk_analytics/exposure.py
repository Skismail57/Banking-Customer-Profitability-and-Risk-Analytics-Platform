"""Loan exposure and outstanding balance analysis."""

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


class ExposureAnalyzer(CreditRiskBase):
    """Analyze loan exposure and outstanding balances."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize exposure analyzer.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
    
    def calculate_total_exposure(
        self,
        df: pd.DataFrame,
        balance_column: str = "current_balance",
        status_column: str = "loan_status",
        active_statuses: Optional[list] = None
    ) -> RiskIndicatorValue:
        """Calculate total loan exposure.
        
        Args:
            df: DataFrame with loan data
            balance_column: Name of balance column
            status_column: Name of status column
            active_statuses: List of statuses considered active
        
        Returns:
            RiskIndicatorValue with total exposure
        """
        if active_statuses is None:
            active_statuses = ["active", "current"]
        
        # Filter to active loans
        if status_column in df.columns:
            df_filtered = df[df[status_column].isin(active_statuses)]
        else:
            df_filtered = df.copy()
            logger.warning(f"Status column {status_column} not found, using all loans")
        
        if balance_column not in df_filtered.columns:
            logger.warning(f"Balance column {balance_column} not found")
            return RiskIndicatorValue(
                indicator=RiskIndicator.TOTAL_LOAN_EXPOSURE,
                value=0.0,
                is_available=False,
                data_completeness=0.0,
                confidence=0.0,
                metadata={"reason": f"Column {balance_column} not found"}
            )
        
        total_exposure = df_filtered[balance_column].sum()
        
        # Calculate data completeness
        total_rows = len(df)
        active_rows = len(df_filtered)
        completeness = active_rows / total_rows if total_rows > 0 else 0
        
        return RiskIndicatorValue(
            indicator=RiskIndicator.TOTAL_LOAN_EXPOSURE,
            value=total_exposure,
            is_available=True,
            data_completeness=completeness,
            confidence=0.9 if completeness > 0.8 else 0.6,
            metadata={
                "active_loan_count": active_rows,
                "total_loan_count": total_rows,
                "active_statuses": active_statuses
            }
        )
    
    def calculate_outstanding_balance(
        self,
        df: pd.DataFrame,
        balance_column: str = "current_balance"
    ) -> RiskIndicatorValue:
        """Calculate outstanding balance.
        
        Args:
            df: DataFrame with loan data
            balance_column: Name of balance column
        
        Returns:
            RiskIndicatorValue with outstanding balance
        """
        if balance_column not in df.columns:
            logger.warning(f"Balance column {balance_column} not found")
            return RiskIndicatorValue(
                indicator=RiskIndicator.OUTSTANDING_BALANCE,
                value=0.0,
                is_available=False,
                data_completeness=0.0,
                confidence=0.0,
                metadata={"reason": f"Column {balance_column} not found"}
            )
        
        outstanding_balance = df[balance_column].sum()
        
        return RiskIndicatorValue(
            indicator=RiskIndicator.OUTSTANDING_BALANCE,
            value=outstanding_balance,
            is_available=True,
            data_completeness=1.0,
            confidence=0.9,
            metadata={"row_count": len(df)}
        )
    
    def calculate_average_balance(
        self,
        df: pd.DataFrame,
        balance_column: str = "current_balance"
    ) -> RiskIndicatorValue:
        """Calculate average balance.
        
        Args:
            df: DataFrame with loan data
            balance_column: Name of balance column
        
        Returns:
            RiskIndicatorValue with average balance
        """
        if balance_column not in df.columns:
            logger.warning(f"Balance column {balance_column} not found")
            return RiskIndicatorValue(
                indicator=RiskIndicator.AVERAGE_BALANCE,
                value=0.0,
                is_available=False,
                data_completeness=0.0,
                confidence=0.0,
                metadata={"reason": f"Column {balance_column} not found"}
            )
        
        average_balance = df[balance_column].mean()
        
        return RiskIndicatorValue(
            indicator=RiskIndicator.AVERAGE_BALANCE,
            value=average_balance,
            is_available=True,
            data_completeness=1.0,
            confidence=0.9,
            metadata={"row_count": len(df)}
        )
    
    def calculate_exposure_by_customer(
        self,
        df: pd.DataFrame,
        customer_column: str = "customer_key",
        balance_column: str = "current_balance"
    ) -> pd.DataFrame:
        """Calculate exposure per customer.
        
        Args:
            df: DataFrame with loan data
            customer_column: Name of customer column
            balance_column: Name of balance column
        
        Returns:
            DataFrame with customer-level exposure
        """
        if balance_column not in df.columns:
            logger.warning(f"Balance column {balance_column} not found")
            return pd.DataFrame()
        
        customer_exposure = df.groupby(customer_column).agg({
            balance_column: ["sum", "mean", "count"]
        }).reset_index()
        
        customer_exposure.columns = [
            customer_column,
            "total_exposure",
            "average_balance",
            "loan_count"
        ]
        
        return customer_exposure
