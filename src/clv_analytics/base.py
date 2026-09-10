"""Base classes for Customer Lifetime Value analytics."""

from dataclasses import dataclass
from datetime import date
from typing import Dict, Any, List, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class CLVType(Enum):
    """Types of Customer Lifetime Value calculations."""
    HISTORICAL = "historical"  # Actual historical value
    PREDICTED = "predicted"  # Projected future value based on models
    ESTIMATED = "estimated"  # Simplified estimate based on averages


@dataclass
class CLVParameters:
    """Parameters for CLV calculation."""
    
    discount_rate: float = 0.10  # Annual discount rate (10% default)
    retention_rate: float = 0.80  # Annual retention rate (80% default)
    time_horizon_years: int = 5  # Projection horizon in years
    average_revenue: Optional[float] = None  # Average revenue per period
    average_cost: Optional[float] = None  # Average cost per period
    average_profit: Optional[float] = None  # Average profit per period
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "discount_rate": self.discount_rate,
            "retention_rate": self.retention_rate,
            "time_horizon_years": self.time_horizon_years,
            "average_revenue": self.average_revenue,
            "average_cost": self.average_cost,
            "average_profit": self.average_profit
        }


@dataclass
class CLVResult:
    """Result of CLV calculation."""
    
    customer_key: str
    clv_type: CLVType
    clv_value: float
    parameters: CLVParameters
    calculation_date: date
    components: Dict[str, Any]
    assumptions: List[str]
    limitations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "customer_key": self.customer_key,
            "clv_type": self.clv_type.value,
            "clv_value": self.clv_value,
            "parameters": self.parameters.to_dict(),
            "calculation_date": self.calculation_date.isoformat(),
            "components": self.components,
            "assumptions": self.assumptions,
            "limitations": self.limitations
        }


class CLVBase:
    """Base class for CLV calculations."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize CLV base.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        self.as_of_date = as_of_date or date.today()
    
    def validate_parameters(self, params: CLVParameters) -> bool:
        """Validate CLV parameters.
        
        Args:
            params: CLV parameters to validate
        
        Returns:
            True if valid, False otherwise
        """
        if params.discount_rate < 0 or params.discount_rate > 1:
            logger.error(f"Invalid discount rate: {params.discount_rate}")
            return False
        
        if params.retention_rate < 0 or params.retention_rate > 1:
            logger.error(f"Invalid retention rate: {params.retention_rate}")
            return False
        
        if params.time_horizon_years <= 0:
            logger.error(f"Invalid time horizon: {params.time_horizon_years}")
            return False
        
        return True
    
    def get_default_parameters(self) -> CLVParameters:
        """Get default CLV parameters.
        
        Returns:
            Default CLV parameters
        """
        return CLVParameters(
            discount_rate=0.10,
            retention_rate=0.80,
            time_horizon_years=5
        )
