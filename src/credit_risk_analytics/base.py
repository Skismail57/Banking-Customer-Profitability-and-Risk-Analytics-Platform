"""Base classes for credit risk analytics."""

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, Any, List, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RiskIndicator(Enum):
    """Credit risk indicator definitions."""
    # Exposure indicators
    TOTAL_LOAN_EXPOSURE = "total_loan_exposure"
    OUTSTANDING_BALANCE = "outstanding_balance"
    AVERAGE_BALANCE = "average_balance"
    
    # Payment behavior indicators
    DAYS_PAST_DUE = "days_past_due"
    DELINQUENCY_STATUS = "delinquency_status"
    PAYMENT_FREQUENCY = "payment_frequency"
    PAYMENT_REGULARITY = "payment_regularity"
    
    # Utilization indicators
    CREDIT_UTILIZATION = "credit_utilization"
    UTILIZATION_TREND = "utilization_trend"
    
    # Repayment history indicators
    ON_TIME_PAYMENT_RATE = "on_time_payment_rate"
    LATE_PAYMENT_COUNT = "late_payment_count"
    MISSED_PAYMENT_COUNT = "missed_payment_count"
    
    # Debt burden indicators
    LOAN_TO_INCOME = "loan_to_income"
    DEBT_TO_INCOME = "debt_to_income"
    DEBT_BURDEN = "debt_burden"
    
    # Default indicators
    DEFAULT_FLAG = "default_flag"
    DEFAULT_COUNT = "default_count"
    RECOVERY_RATE = "recovery_rate"
    
    # Trend indicators
    BALANCE_TREND = "balance_trend"
    PAYMENT_TREND = "payment_trend"
    UTILIZATION_TREND_30D = "utilization_trend_30d"


class RiskBand(Enum):
    """Risk band classifications for portfolio analytics."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class IndicatorDefinition:
    """Definition of a risk indicator with transparency metadata."""
    
    name: RiskIndicator
    description: str
    data_type: str  # numeric, percentage, categorical
    calculation_method: str
    business_definition: str
    data_requirements: List[str]
    assumptions: List[str]
    limitations: List[str]
    interpretation: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name.value,
            "description": self.description,
            "data_type": self.data_type,
            "calculation_method": self.calculation_method,
            "business_definition": self.business_definition,
            "data_requirements": self.data_requirements,
            "assumptions": self.assumptions,
            "limitations": self.limitations,
            "interpretation": self.interpretation
        }


@dataclass
class RiskIndicatorValue:
    """Container for risk indicator values with transparency metadata."""
    
    indicator: RiskIndicator
    value: float
    is_available: bool
    data_completeness: float  # 0-1 score of data completeness
    confidence: float  # 0-1 confidence score
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "indicator": self.indicator.value,
            "value": self.value,
            "is_available": self.is_available,
            "data_completeness": self.data_completeness,
            "confidence": self.confidence,
            "metadata": self.metadata
        }


class CreditRiskBase:
    """Base class for credit risk analytics."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize credit risk base.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        self.as_of_date = as_of_date or date.today()
        self.indicator_registry: Dict[str, IndicatorDefinition] = {}
        
        # Register standard indicators
        self._register_indicators()
    
    def _register_indicators(self) -> None:
        """Register standard risk indicators."""
        indicators = [
            # Exposure indicators
            IndicatorDefinition(
                name=RiskIndicator.TOTAL_LOAN_EXPOSURE,
                description="Total loan exposure across all loans",
                data_type="currency",
                calculation_method="SUM(current_balance)",
                business_definition="Sum of outstanding balances across all active loans",
                data_requirements=["current_balance", "loan_status"],
                assumptions=["Only active loans included", "Balance as of as_of_date"],
                limitations=["Does not include contingent liabilities", "May not reflect off-balance sheet exposure"],
                interpretation="Higher values indicate greater credit exposure"
            ),
            IndicatorDefinition(
                name=RiskIndicator.OUTSTANDING_BALANCE,
                description="Current outstanding loan balance",
                data_type="currency",
                calculation_method="current_balance",
                business_definition="Principal amount currently outstanding on loan",
                data_requirements=["current_balance"],
                assumptions=["Balance is current and accurate"],
                limitations=["May not include accrued interest", "Subject to accounting policies"],
                interpretation="Higher values indicate larger outstanding obligation"
            ),
            # Payment behavior indicators
            IndicatorDefinition(
                name=RiskIndicator.DAYS_PAST_DUE,
                description="Days past due on loan payments",
                data_type="numeric",
                calculation_method="MAX(days_past_due)",
                business_definition="Number of days payments are past due",
                data_requirements=["days_past_due", "payment_due_date"],
                assumptions=["Days calculated from payment due date"],
                limitations=["May not reflect partial payments", "Grace periods not considered"],
                interpretation="Higher values indicate more severe delinquency"
            ),
            IndicatorDefinition(
                name=RiskIndicator.DELINQUENCY_STATUS,
                description="Current delinquency status",
                data_type="categorical",
                calculation_method="CLASSIFY(days_past_due)",
                business_definition="Categorical delinquency classification",
                data_requirements=["days_past_due"],
                assumptions=["Standard delinquency buckets used"],
                limitations=["Bucket definitions may vary by institution"],
                interpretation="Higher categories indicate more severe delinquency"
            ),
            # Utilization indicators
            IndicatorDefinition(
                name=RiskIndicator.CREDIT_UTILIZATION,
                description="Credit utilization ratio",
                data_type="percentage",
                calculation_method="(current_balance / credit_limit) * 100",
                business_definition="Percentage of available credit being used",
                data_requirements=["current_balance", "credit_limit"],
                assumptions=["Credit limit is accurate and current"],
                limitations=["Does not consider utilization across multiple products", "May not reflect authorized but unused credit"],
                interpretation="Higher values indicate higher credit usage"
            ),
            # Repayment history indicators
            IndicatorDefinition(
                name=RiskIndicator.ON_TIME_PAYMENT_RATE,
                description="Percentage of payments made on time",
                data_type="percentage",
                calculation_method="(on_time_payments / total_payments) * 100",
                business_definition="Rate of payments made by due date",
                data_requirements=["payment_history", "payment_due_date", "payment_date"],
                assumptions=["Payment history is complete and accurate"],
                limitations=["May not reflect payment amount", "Grace periods not considered"],
                interpretation="Higher values indicate better payment history"
            ),
            # Debt burden indicators
            IndicatorDefinition(
                name=RiskIndicator.LOAN_TO_INCOME,
                description="Loan-to-income ratio",
                data_type="percentage",
                calculation_method="(loan_amount / annual_income) * 100",
                business_definition="Loan amount as percentage of annual income",
                data_requirements=["loan_amount", "annual_income"],
                assumptions=["Income is current and accurate"],
                limitations=["Does not consider other debt obligations", "Income may not reflect current situation"],
                interpretation="Higher values indicate higher debt burden relative to income"
            ),
            IndicatorDefinition(
                name=RiskIndicator.DEBT_TO_INCOME,
                description="Debt-to-income ratio",
                data_type="percentage",
                calculation_method="(total_debt_payments / monthly_income) * 100",
                business_definition="Total debt payments as percentage of monthly income",
                data_requirements=["total_debt_payments", "monthly_income"],
                assumptions=["All debt obligations included", "Income is current"],
                limitations=["May not include all debt types", "Income volatility not considered"],
                interpretation="Higher values indicate higher debt burden"
            ),
            # Default indicators
            IndicatorDefinition(
                name=RiskIndicator.DEFAULT_FLAG,
                description="Default status indicator",
                data_type="categorical",
                calculation_method="CLASSIFY(default_status)",
                business_definition="Whether loan is in default",
                data_requirements=["default_status", "days_past_due"],
                assumptions=["Default definition follows institutional policy"],
                limitations=["Default definitions vary by institution", "May not reflect partial recoveries"],
                interpretation="True indicates loan is in default"
            ),
        ]
        
        for indicator in indicators:
            self.indicator_registry[indicator.name.value] = indicator
    
    def get_indicator_definition(self, indicator_name: str) -> Optional[IndicatorDefinition]:
        """Get indicator definition by name.
        
        Args:
            indicator_name: Name of the indicator
        
        Returns:
            IndicatorDefinition if found, None otherwise
        """
        return self.indicator_registry.get(indicator_name)
    
    def get_all_indicator_definitions(self) -> Dict[str, IndicatorDefinition]:
        """Get all registered indicator definitions.
        
        Returns:
            Dictionary of indicator definitions
        """
        return self.indicator_registry.copy()
