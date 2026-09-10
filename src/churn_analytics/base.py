"""Base classes for churn analytics."""

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ChurnType(Enum):
    """Types of churn definitions."""
    ACCOUNT_CLOSURE = "account_closure"
    INACTIVITY = "inactivity"
    BALANCE_DEPLETION = "balance_depletion"
    PRODUCT_CANCELLATION = "product_cancellation"
    COMPOSITE = "composite"


@dataclass
class ChurnDefinition:
    """Definition of churn based on available data."""
    
    name: str
    churn_type: ChurnType
    definition: str
    criteria: Dict[str, Any]
    lookback_period_days: int
    observation_window_days: int
    data_requirements: List[str]
    assumptions: List[str]
    limitations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "churn_type": self.churn_type.value,
            "definition": self.definition,
            "criteria": self.criteria,
            "lookback_period_days": self.lookback_period_days,
            "observation_window_days": self.observation_window_days,
            "data_requirements": self.data_requirements,
            "assumptions": self.assumptions,
            "limitations": self.limitations
        }


class ChurnBase:
    """Base class for churn analytics."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize churn base.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        self.as_of_date = as_of_date or date.today()
        self.churn_definitions: Dict[str, ChurnDefinition] = {}
        
        # Register standard churn definitions
        self._register_standard_definitions()
    
    def _register_standard_definitions(self) -> None:
        """Register standard churn definitions."""
        definitions = [
            ChurnDefinition(
                name="account_closure",
                churn_type=ChurnType.ACCOUNT_CLOSURE,
                definition="Customer closes all accounts",
                criteria={
                    "account_status": "closed",
                    "closure_reason": "customer_initiated"
                },
                lookback_period_days=90,
                observation_window_days=30,
                data_requirements=["account_status", "closure_date", "closure_reason"],
                assumptions=["Closure is customer-initiated", "All accounts considered"],
                limitations=["May miss partial churn", "Closure reasons may be incomplete"]
            ),
            ChurnDefinition(
                name="inactivity_churn",
                churn_type=ChurnType.INACTIVITY,
                definition="Customer shows no activity for extended period",
                criteria={
                    "no_transaction_days": 90,
                    "no_login_days": 60
                },
                lookback_period_days=90,
                observation_window_days=30,
                data_requirements=["last_transaction_date", "last_login_date"],
                assumptions=["Inactivity indicates churn intent", "No external factors"],
                limitations=["May miss active but low-value customers", "Thresholds may vary"]
            ),
            ChurnDefinition(
                name="balance_depletion_churn",
                churn_type=ChurnType.BALANCE_DEPLETION,
                definition="Customer depletes all balances",
                criteria={
                    "balance_threshold": 100,
                    "balance_decline_pct": 90
                },
                lookback_period_days=90,
                observation_window_days=30,
                data_requirements=["current_balance", "historical_balances"],
                assumptions=["Balance depletion indicates churn", "Thresholds appropriate"],
                limitations=["May miss balance transfers", "Seasonal variations not considered"]
            ),
            ChurnDefinition(
                name="composite_churn",
                churn_type=ChurnType.COMPOSITE,
                definition="Multiple indicators of churn",
                criteria={
                    "min_indicators": 2,
                    "indicators": ["account_closure", "inactivity", "balance_depletion"]
                },
                lookback_period_days=90,
                observation_window_days=30,
                data_requirements=["account_status", "activity_data", "balance_data"],
                assumptions=["Multiple indicators stronger signal", "Indicators independent"],
                limitations=["Complex to implement", "May overfit to historical patterns"]
            ),
        ]
        
        for definition in definitions:
            self.churn_definitions[definition.name] = definition
    
    def get_churn_definition(self, name: str) -> Optional[ChurnDefinition]:
        """Get churn definition by name.
        
        Args:
            name: Name of churn definition
        
        Returns:
            ChurnDefinition if found, None otherwise
        """
        return self.churn_definitions.get(name)
    
    def get_all_churn_definitions(self) -> Dict[str, ChurnDefinition]:
        """Get all registered churn definitions.
        
        Returns:
            Dictionary of churn definitions
        """
        return self.churn_definitions.copy()
