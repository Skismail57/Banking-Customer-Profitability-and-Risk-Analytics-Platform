"""Base classes for profitability analytics."""

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, Any, List, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ValueType(Enum):
    """Type of value indicating data source and reliability."""
    OBSERVED = "observed"  # Directly measured from transaction/system data
    ESTIMATED = "estimated"  # Calculated from available data with assumptions
    MODELED = "modeled"  # Generated from statistical/machine learning models
    MISSING = "missing"  # Data not available


@dataclass
class ProfitabilityValue:
    """Container for profitability values with type metadata."""
    
    value: float
    value_type: ValueType
    source: str
    confidence: Optional[float] = None  # 0-1 confidence score for estimated/modeled values
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate value type and confidence."""
        if self.value_type in [ValueType.ESTIMATED, ValueType.MODELED]:
            if self.confidence is None:
                self.confidence = 0.5  # Default confidence for estimated/modeled
        else:
            self.confidence = 1.0  # Observed values have 100% confidence
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "value": self.value,
            "value_type": self.value_type.value,
            "source": self.source,
            "confidence": self.confidence,
            "metadata": self.metadata
        }


class ProfitabilityMetric(Enum):
    """Profitability metric definitions."""
    # Revenue metrics
    INTEREST_INCOME = "interest_income"
    FEE_INCOME = "fee_income"
    SERVICE_CHARGE_INCOME = "service_charge_income"
    PRODUCT_REVENUE = "product_revenue"
    GROSS_REVENUE = "gross_revenue"
    
    # Cost metrics
    SERVICING_COST = "servicing_cost"
    OPERATIONAL_COST = "operational_cost"
    INCENTIVE_COST = "incentive_cost"
    EXPECTED_CREDIT_LOSS = "expected_credit_loss"
    TOTAL_COST = "total_cost"
    
    # Profitability metrics
    NET_PROFIT = "net_profit"
    PROFIT_MARGIN = "profit_margin"
    RETURN_ON_ASSETS = "return_on_assets"
    RETURN_ON_EQUITY = "return_on_equity"


@dataclass
class MetricDefinition:
    """Definition of a profitability metric."""
    
    name: ProfitabilityMetric
    description: str
    data_type: str  # currency, percentage, numeric
    calculation_method: str
    business_definition: str
    default_value_type: ValueType
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name.value,
            "description": self.description,
            "data_type": self.data_type,
            "calculation_method": self.calculation_method,
            "business_definition": self.business_definition,
            "default_value_type": self.default_value_type.value
        }


class ProfitabilityBase:
    """Base class for profitability analytics."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize profitability base.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        self.as_of_date = as_of_date or date.today()
        self.metric_registry: Dict[str, MetricDefinition] = {}
        
        # Register standard metrics
        self._register_metrics()
    
    def _register_metrics(self) -> None:
        """Register standard profitability metrics."""
        metrics = [
            # Revenue metrics
            MetricDefinition(
                name=ProfitabilityMetric.INTEREST_INCOME,
                description="Interest income from loans and deposits",
                data_type="currency",
                calculation_method="SUM(interest_accrued)",
                business_definition="Interest earned on loan portfolios and paid on deposits",
                default_value_type=ValueType.OBSERVED
            ),
            MetricDefinition(
                name=ProfitabilityMetric.FEE_INCOME,
                description="Fee income from various services",
                data_type="currency",
                calculation_method="SUM(fee_amount)",
                business_definition="Fees charged for account maintenance, overdrafts, etc.",
                default_value_type=ValueType.OBSERVED
            ),
            MetricDefinition(
                name=ProfitabilityMetric.SERVICE_CHARGE_INCOME,
                description="Service charge income",
                data_type="currency",
                calculation_method="SUM(service_charge)",
                business_definition="Service charges for specific transactions or services",
                default_value_type=ValueType.OBSERVED
            ),
            MetricDefinition(
                name=ProfitabilityMetric.PRODUCT_REVENUE,
                description="Product-specific revenue",
                data_type="currency",
                calculation_method="SUM(product_revenue)",
                business_definition="Revenue attributed to specific banking products",
                default_value_type=ValueType.OBSERVED
            ),
            MetricDefinition(
                name=ProfitabilityMetric.GROSS_REVENUE,
                description="Total gross revenue",
                data_type="currency",
                calculation_method="SUM(all_revenue_components)",
                business_definition="Sum of all revenue components before costs",
                default_value_type=ValueType.OBSERVED
            ),
            # Cost metrics
            MetricDefinition(
                name=ProfitabilityMetric.SERVICING_COST,
                description="Cost to service accounts",
                data_type="currency",
                calculation_method="SUM(servicing_cost)",
                business_definition="Direct costs associated with account servicing",
                default_value_type=ValueType.OBSERVED
            ),
            MetricDefinition(
                name=ProfitabilityMetric.OPERATIONAL_COST,
                description="Operational overhead costs",
                data_type="currency",
                calculation_method="ALLOCATED(operational_overhead)",
                business_definition="Allocated portion of operational overhead",
                default_value_type=ValueType.ESTIMATED
            ),
            MetricDefinition(
                name=ProfitabilityMetric.INCENTIVE_COST,
                description="Incentive and reward costs",
                data_type="currency",
                calculation_method="SUM(incentive_amount)",
                business_definition="Cost of customer incentives, rewards, and promotions",
                default_value_type=ValueType.OBSERVED
            ),
            MetricDefinition(
                name=ProfitabilityMetric.EXPECTED_CREDIT_LOSS,
                description="Expected credit loss (ECL)",
                data_type="currency",
                calculation_method="CALCULATED_ECL(PD * LGD * EAD)",
                business_definition="Expected loss from credit defaults based on risk models",
                default_value_type=ValueType.MODELED
            ),
            MetricDefinition(
                name=ProfitabilityMetric.TOTAL_COST,
                description="Total cost",
                data_type="currency",
                calculation_method="SUM(all_cost_components)",
                business_definition="Sum of all cost components",
                default_value_type=ValueType.ESTIMATED
            ),
            # Profitability metrics
            MetricDefinition(
                name=ProfitabilityMetric.NET_PROFIT,
                description="Net profit after all costs",
                data_type="currency",
                calculation_method="gross_revenue - total_cost",
                business_definition="Revenue minus all costs including expected credit loss",
                default_value_type=ValueType.ESTIMATED
            ),
            MetricDefinition(
                name=ProfitabilityMetric.PROFIT_MARGIN,
                description="Profit margin percentage",
                data_type="percentage",
                calculation_method="(net_profit / gross_revenue) * 100",
                business_definition="Net profit as percentage of gross revenue",
                default_value_type=ValueType.ESTIMATED
            ),
            MetricDefinition(
                name=ProfitabilityMetric.RETURN_ON_ASSETS,
                description="Return on assets",
                data_type="percentage",
                calculation_method="(net_profit / average_assets) * 100",
                business_definition="Net profit as percentage of average assets deployed",
                default_value_type=ValueType.ESTIMATED
            ),
            MetricDefinition(
                name=ProfitabilityMetric.RETURN_ON_EQUITY,
                description="Return on equity",
                data_type="percentage",
                calculation_method="(net_profit / average_equity) * 100",
                business_definition="Net profit as percentage of equity capital",
                default_value_type=ValueType.ESTIMATED
            ),
        ]
        
        for metric in metrics:
            self.metric_registry[metric.name.value] = metric
    
    def get_metric_definition(self, metric_name: str) -> Optional[MetricDefinition]:
        """Get metric definition by name.
        
        Args:
            metric_name: Name of the metric
        
        Returns:
            MetricDefinition if found, None otherwise
        """
        return self.metric_registry.get(metric_name)
    
    def get_all_metric_definitions(self) -> Dict[str, MetricDefinition]:
        """Get all registered metric definitions.
        
        Returns:
            Dictionary of metric definitions
        """
        return self.metric_registry.copy()
    
    def get_metrics_by_value_type(self, value_type: ValueType) -> List[MetricDefinition]:
        """Get all metrics with a specific default value type.
        
        Args:
            value_type: ValueType to filter by
        
        Returns:
            List of MetricDefinitions
        """
        return [
            m for m in self.metric_registry.values()
            if m.default_value_type == value_type
        ]
