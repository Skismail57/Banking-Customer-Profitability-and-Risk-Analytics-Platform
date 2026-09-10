"""Loan-to-income and debt burden analysis (where data available)."""

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


class DebtBurdenAnalyzer(CreditRiskBase):
    """Analyze loan-to-income and debt burden where data is available."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize debt burden analyzer.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
    
    def calculate_loan_to_income(
        self,
        df: pd.DataFrame,
        loan_amount_column: str = "loan_amount",
        annual_income_column: str = "annual_income"
    ) -> RiskIndicatorValue:
        """Calculate loan-to-income ratio.
        
        Args:
            df: DataFrame with loan and income data
            loan_amount_column: Name of loan amount column
            annual_income_column: Name of annual income column
        
        Returns:
            RiskIndicatorValue with loan-to-income ratio
        """
        if loan_amount_column not in df.columns or annual_income_column not in df.columns:
            logger.warning("Required columns not found for LTI calculation")
            return RiskIndicatorValue(
                indicator=RiskIndicator.LOAN_TO_INCOME,
                value=0.0,
                is_available=False,
                data_completeness=0.0,
                confidence=0.0,
                metadata={
                    "reason": "Required columns not found",
                    "has_loan_amount": loan_amount_column in df.columns,
                    "has_income": annual_income_column in df.columns
                }
            )
        
        total_loan_amount = df[loan_amount_column].sum()
        annual_income = df[annual_income_column].iloc[0] if len(df) > 0 else 0
        
        if annual_income == 0:
            logger.warning("Annual income is zero")
            return RiskIndicatorValue(
                indicator=RiskIndicator.LOAN_TO_INCOME,
                value=0.0,
                is_available=False,
                data_completeness=0.0,
                confidence=0.0,
                metadata={"reason": "Annual income is zero"}
            )
        
        lti = (total_loan_amount / annual_income) * 100
        
        return RiskIndicatorValue(
            indicator=RiskIndicator.LOAN_TO_INCOME,
            value=lti,
            is_available=True,
            data_completeness=1.0,
            confidence=0.7,  # Lower confidence due to income volatility
            metadata={
                "total_loan_amount": total_loan_amount,
                "annual_income": annual_income
            }
        )
    
    def calculate_debt_to_income(
        self,
        df: pd.DataFrame,
        debt_payment_column: str = "monthly_debt_payment",
        monthly_income_column: str = "monthly_income"
    ) -> RiskIndicatorValue:
        """Calculate debt-to-income ratio.
        
        Args:
            df: DataFrame with debt and income data
            debt_payment_column: Name of debt payment column
            monthly_income_column: Name of monthly income column
        
        Returns:
            RiskIndicatorValue with debt-to-income ratio
        """
        if debt_payment_column not in df.columns or monthly_income_column not in df.columns:
            logger.warning("Required columns not found for DTI calculation")
            return RiskIndicatorValue(
                indicator=RiskIndicator.DEBT_TO_INCOME,
                value=0.0,
                is_available=False,
                data_completeness=0.0,
                confidence=0.0,
                metadata={
                    "reason": "Required columns not found",
                    "has_debt_payment": debt_payment_column in df.columns,
                    "has_income": monthly_income_column in df.columns
                }
            )
        
        total_debt_payment = df[debt_payment_column].sum()
        monthly_income = df[monthly_income_column].iloc[0] if len(df) > 0 else 0
        
        if monthly_income == 0:
            logger.warning("Monthly income is zero")
            return RiskIndicatorValue(
                indicator=RiskIndicator.DEBT_TO_INCOME,
                value=0.0,
                is_available=False,
                data_completeness=0.0,
                confidence=0.0,
                metadata={"reason": "Monthly income is zero"}
            )
        
        dti = (total_debt_payment / monthly_income) * 100
        
        return RiskIndicatorValue(
            indicator=RiskIndicator.DEBT_TO_INCOME,
            value=dti,
            is_available=True,
            data_completeness=1.0,
            confidence=0.7,  # Lower confidence due to income volatility
            metadata={
                "total_debt_payment": total_debt_payment,
                "monthly_income": monthly_income
            }
        )
    
    def calculate_debt_burden(
        self,
        df: pd.DataFrame,
        balance_column: str = "current_balance",
        income_column: str = "annual_income"
    ) -> RiskIndicatorValue:
        """Calculate debt burden (total debt as percentage of income).
        
        Args:
            df: DataFrame with debt and income data
            balance_column: Name of balance column
            income_column: Name of income column
        
        Returns:
            RiskIndicatorValue with debt burden
        """
        if balance_column not in df.columns or income_column not in df.columns:
            logger.warning("Required columns not found for debt burden calculation")
            return RiskIndicatorValue(
                indicator=RiskIndicator.DEBT_BURDEN,
                value=0.0,
                is_available=False,
                data_completeness=0.0,
                confidence=0.0,
                metadata={
                    "reason": "Required columns not found",
                    "has_balance": balance_column in df.columns,
                    "has_income": income_column in df.columns
                }
            )
        
        total_debt = df[balance_column].sum()
        annual_income = df[income_column].iloc[0] if len(df) > 0 else 0
        
        if annual_income == 0:
            logger.warning("Annual income is zero")
            return RiskIndicatorValue(
                indicator=RiskIndicator.DEBT_BURDEN,
                value=0.0,
                is_available=False,
                data_completeness=0.0,
                confidence=0.0,
                metadata={"reason": "Annual income is zero"}
            )
        
        debt_burden = (total_debt / annual_income) * 100
        
        return RiskIndicatorValue(
            indicator=RiskIndicator.DEBT_BURDEN,
            value=debt_burden,
            is_available=True,
            data_completeness=1.0,
            confidence=0.7,  # Lower confidence due to income volatility
            metadata={
                "total_debt": total_debt,
                "annual_income": annual_income
            }
        )
