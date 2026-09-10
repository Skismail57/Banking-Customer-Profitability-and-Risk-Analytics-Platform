"""Profitability tier classification with configurable thresholds."""

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class TierThreshold:
    """Threshold configuration for profitability tier."""
    
    name: str
    min_profit: float
    max_profit: Optional[float] = None
    min_margin: Optional[float] = None
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "min_profit": self.min_profit,
            "max_profit": self.max_profit,
            "min_margin": self.min_margin,
            "description": self.description
        }


class ProfitabilityTierEngine:
    """Classify profitability into tiers using configurable thresholds."""
    
    def __init__(self, thresholds: Optional[List[TierThreshold]] = None):
        """Initialize tier engine.
        
        Args:
            thresholds: List of tier thresholds (default: standard tiers)
        """
        self.thresholds = thresholds or self._default_thresholds()
    
    def _default_thresholds(self) -> List[TierThreshold]:
        """Default profitability tier thresholds.
        
        Returns:
            List of default tier thresholds
        """
        return [
            TierThreshold(
                name="platinum",
                min_profit=100000,
                min_margin=25.0,
                description="Top-tier profitable customers"
            ),
            TierThreshold(
                name="gold",
                min_profit=50000,
                max_profit=100000,
                min_margin=15.0,
                description="High-value profitable customers"
            ),
            TierThreshold(
                name="silver",
                min_profit=10000,
                max_profit=50000,
                min_margin=10.0,
                description="Moderately profitable customers"
            ),
            TierThreshold(
                name="bronze",
                min_profit=0,
                max_profit=10000,
                min_margin=5.0,
                description="Low-margin profitable customers"
            ),
            TierThreshold(
                name="unprofitable",
                min_profit=-float("inf"),
                max_profit=0,
                description="Unprofitable customers"
            ),
        ]
    
    def classify(
        self,
        net_profit: float,
        profit_margin: Optional[float] = None
    ) -> str:
        """Classify profitability into tier.
        
        Args:
            net_profit: Net profit value
            profit_margin: Optional profit margin percentage
        
        Returns:
            Tier name
        """
        for tier in self.thresholds:
            # Check profit range
            profit_in_range = tier.min_profit <= net_profit
            if tier.max_profit is not None:
                profit_in_range = profit_in_range and net_profit < tier.max_profit
            
            # Check margin if specified
            margin_in_range = True
            if profit_margin is not None and tier.min_margin is not None:
                margin_in_range = profit_margin >= tier.min_margin
            
            if profit_in_range and margin_in_range:
                return tier.name
        
        return "unknown"
    
    def classify_batch(
        self,
        profits: List[float],
        margins: Optional[List[float]] = None
    ) -> List[str]:
        """Classify multiple profitabilities into tiers.
        
        Args:
            profits: List of net profit values
            margins: Optional list of profit margin percentages
        
        Returns:
            List of tier names
        """
        if margins is None:
            margins = [None] * len(profits)
        
        tiers = []
        for profit, margin in zip(profits, margins):
            tier = self.classify(profit, margin)
            tiers.append(tier)
        
        return tiers
    
    def get_tier_definition(self, tier_name: str) -> Optional[TierThreshold]:
        """Get tier definition by name.
        
        Args:
            tier_name: Name of the tier
        
        Returns:
            TierThreshold if found, None otherwise
        """
        for tier in self.thresholds:
            if tier.name == tier_name:
                return tier
        return None
    
    def get_all_tiers(self) -> List[TierThreshold]:
        """Get all tier definitions.
        
        Returns:
            List of all tier thresholds
        """
        return self.thresholds.copy()
    
    def update_thresholds(self, thresholds: List[TierThreshold]) -> None:
        """Update tier thresholds.
        
        Args:
            thresholds: New list of tier thresholds
        """
        self.thresholds = thresholds
        logger.info(f"Updated {len(thresholds)} tier thresholds")
