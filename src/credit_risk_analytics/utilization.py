"""Credit utilization analysis."""

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


class UtilizationAnalyzer(CreditRiskBase):
    """Analyze credit utilization."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize utilization analyzer.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
    
    def calculate_credit_utilization(
        self,
        df: pd.DataFrame,
        balance_column: str = "current_balance",
        limit_column: str = "credit_limit"
    ) -> RiskIndicatorValue:
        """Calculate credit utilization ratio.
        
        Args:
            df: DataFrame with credit data
            balance_column: Name of balance column
            limit_column: Name of credit limit column
        
        Returns:
            RiskIndicatorValue with credit utilization
        """
        if balance_column not in df.columns or limit_column not in df.columns:
            logger.warning(f"Required columns not found")
            return RiskIndicatorValue(
                indicator=RiskIndicator.CREDIT_UTILIZATION,
                value=0.0,
                is_available=False,
                data_completeness=0.0,
                confidence=0.0,
                metadata={
                    "reason": "Required columns not found",
                    "has_balance": balance_column in df.columns,
                    "has_limit": limit_column in df.columns
                }
            )
        
        total_balance = df[balance_column].sum()
        total_limit = df[limit_column].sum()
        
        if total_limit == 0:
            logger.warning("Total credit limit is zero")
            return RiskIndicatorValue(
                indicator=RiskIndicator.CREDIT_UTILIZATION,
                value=0.0,
                is_available=False,
                data_completeness=0.0,
                confidence=0.0,
                metadata={"reason": "Total credit limit is zero"}
            )
        
        utilization = (total_balance / total_limit) * 100
        
        return RiskIndicatorValue(
            indicator=RiskIndicator.CREDIT_UTILIZATION,
            value=utilization,
            is_available=True,
            data_completeness=1.0,
            confidence=0.9,
            metadata={
                "total_balance": total_balance,
                "total_limit": total_limit
            }
        )
    
    def calculate_utilization_trend(
        self,
        df: pd.DataFrame,
        balance_column: str = "current_balance",
        limit_column: str = "credit_limit",
        date_column: str = "as_of_date"
    ) -> RiskIndicatorValue:
        """Calculate utilization trend over time.
        
        Args:
            df: DataFrame with credit data
            balance_column: Name of balance column
            limit_column: Name of credit limit column
            date_column: Name of date column
        
        Returns:
            RiskIndicatorValue with utilization trend
        """
        if date_column not in df.columns:
            logger.warning(f"Date column {date_column} not found")
            return RiskIndicatorValue(
                indicator=RiskIndicator.UTILIZATION_TREND,
                value=0.0,
                is_available=False,
                data_completeness=0.0,
                confidence=0.0,
                metadata={"reason": f"Column {date_column} not found"}
            )
        
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])
        df = df.sort_values(date_column)
        
        # Calculate utilization over time
        df["utilization"] = (df[balance_column] / df[limit_column]) * 100
        
        # Calculate trend (simple linear slope)
        if len(df) < 2:
            return RiskIndicatorValue(
                indicator=RiskIndicator.UTILIZATION_TREND,
                value=0.0,
                is_available=False,
                data_completeness=0.0,
                confidence=0.0,
                metadata={"reason": "Insufficient data points"}
            )
        
        # Simple trend: last - first
        trend = df["utilization"].iloc[-1] - df["utilization"].iloc[0]
        
        return RiskIndicatorValue(
            indicator=RiskIndicator.UTILIZATION_TREND,
            value=trend,
            is_available=True,
            data_completeness=1.0,
            confidence=0.7,
            metadata={
                "period_count": len(df),
                "start_utilization": df["utilization"].iloc[0],
                "end_utilization": df["utilization"].iloc[-1]
            }
        )
