"""Base classes for transaction analytics."""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AggregationPeriod(Enum):
    """Time aggregation periods."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class TransactionKPI(Enum):
    """Transaction KPI definitions."""
    TRANSACTION_COUNT = "transaction_count"
    TRANSACTION_VALUE = "transaction_value"
    AVG_TRANSACTION_VALUE = "avg_transaction_value"
    MEDIAN_TRANSACTION_VALUE = "median_transaction_value"
    TRANSACTION_FREQUENCY = "transaction_frequency"
    TOTAL_INFLOW = "total_inflow"
    OUTFLOW = "total_outflow"
    NET_FLOW = "net_flow"
    DEBIT_COUNT = "debit_count"
    CREDIT_COUNT = "credit_count"
    DEBIT_VALUE = "debit_value"
    CREDIT_VALUE = "credit_value"


@dataclass
class KPIDefinition:
    """Definition of a transaction KPI."""
    
    name: TransactionKPI
    description: str
    data_type: str  # numeric, percentage, currency
    calculation_method: str
    business_definition: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name.value,
            "description": self.description,
            "data_type": self.data_type,
            "calculation_method": self.calculation_method,
            "business_definition": self.business_definition
        }


class TransactionAnalyticsBase:
    """Base class for transaction analytics."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize transaction analytics base.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        self.as_of_date = as_of_date or date.today()
        self.kpi_registry: Dict[str, KPIDefinition] = {}
        
        # Register standard KPIs
        self._register_kpis()
    
    def _register_kpis(self) -> None:
        """Register standard transaction KPIs."""
        kpis = [
            KPIDefinition(
                name=TransactionKPI.TRANSACTION_COUNT,
                description="Total number of transactions",
                data_type="numeric",
                calculation_method="COUNT(transaction_id)",
                business_definition="Count of all transactions in the period"
            ),
            KPIDefinition(
                name=TransactionKPI.TRANSACTION_VALUE,
                description="Total transaction value",
                data_type="currency",
                calculation_method="SUM(amount)",
                business_definition="Sum of transaction amounts in the period"
            ),
            KPIDefinition(
                name=TransactionKPI.AVG_TRANSACTION_VALUE,
                description="Average transaction value",
                data_type="currency",
                calculation_method="AVG(amount)",
                business_definition="Mean transaction amount in the period"
            ),
            KPIDefinition(
                name=TransactionKPI.MEDIAN_TRANSACTION_VALUE,
                description="Median transaction value",
                data_type="currency",
                calculation_method="MEDIAN(amount)",
                business_definition="Median transaction amount in the period"
            ),
            KPIDefinition(
                name=TransactionKPI.TRANSACTION_FREQUENCY,
                description="Transactions per day",
                data_type="numeric",
                calculation_method="COUNT / period_days",
                business_definition="Daily transaction rate"
            ),
            KPIDefinition(
                name=TransactionKPI.TOTAL_INFLOW,
                description="Total inflow (credits)",
                data_type="currency",
                calculation_method="SUM(amount WHERE amount > 0)",
                business_definition="Sum of positive transaction amounts"
            ),
            KPIDefinition(
                name=TransactionKPI.OUTFLOW,
                description="Total outflow (debits)",
                data_type="currency",
                calculation_method="SUM(ABS(amount) WHERE amount < 0)",
                business_definition="Sum of absolute values of negative transactions"
            ),
            KPIDefinition(
                name=TransactionKPI.NET_FLOW,
                description="Net flow (inflow - outflow)",
                data_type="currency",
                calculation_method="SUM(amount)",
                business_definition="Net transaction amount (credits minus debits)"
            ),
            KPIDefinition(
                name=TransactionKPI.DEBIT_COUNT,
                description="Number of debit transactions",
                data_type="numeric",
                calculation_method="COUNT(amount < 0)",
                business_definition="Count of negative transaction amounts"
            ),
            KPIDefinition(
                name=TransactionKPI.CREDIT_COUNT,
                description="Number of credit transactions",
                data_type="numeric",
                calculation_method="COUNT(amount > 0)",
                business_definition="Count of positive transaction amounts"
            ),
            KPIDefinition(
                name=TransactionKPI.DEBIT_VALUE,
                description="Total debit value",
                data_type="currency",
                calculation_method="SUM(ABS(amount) WHERE amount < 0)",
                business_definition="Sum of absolute values of debit transactions"
            ),
            KPIDefinition(
                name=TransactionKPI.CREDIT_VALUE,
                description="Total credit value",
                data_type="currency",
                calculation_method="SUM(amount WHERE amount > 0)",
                business_definition="Sum of credit transaction amounts"
            ),
        ]
        
        for kpi in kpis:
            self.kpi_registry[kpi.name.value] = kpi
    
    def get_kpi_definition(self, kpi_name: str) -> Optional[KPIDefinition]:
        """Get KPI definition by name.
        
        Args:
            kpi_name: Name of the KPI
        
        Returns:
            KPIDefinition if found, None otherwise
        """
        return self.kpi_registry.get(kpi_name)
    
    def get_all_kpi_definitions(self) -> Dict[str, KPIDefinition]:
        """Get all registered KPI definitions.
        
        Returns:
            Dictionary of KPI definitions
        """
        return self.kpi_registry.copy()
