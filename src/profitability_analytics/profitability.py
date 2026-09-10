"""Profitability calculators for profitability analytics."""

from datetime import date
from typing import Dict, Any, Optional
import logging

import pandas as pd

from src.profitability_analytics.base import (
    ProfitabilityBase,
    ValueType,
    ProfitabilityValue,
)
from src.profitability_analytics.revenue import RevenueCalculator
from src.profitability_analytics.costs import CostCalculator

logger = logging.getLogger(__name__)


class ProfitabilityCalculator(ProfitabilityBase):
    """Calculate profitability metrics from revenue and costs."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize profitability calculator.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
        self.revenue_calculator = RevenueCalculator(as_of_date)
        self.cost_calculator = CostCalculator(as_of_date)
    
    def calculate_net_profit(
        self,
        gross_revenue: ProfitabilityValue,
        total_cost: ProfitabilityValue
    ) -> ProfitabilityValue:
        """Calculate net profit from revenue and costs.
        
        Args:
            gross_revenue: Gross revenue value
            total_cost: Total cost value
        
        Returns:
            ProfitabilityValue with net profit
        """
        if gross_revenue.value_type == ValueType.MISSING or total_cost.value_type == ValueType.MISSING:
            return ProfitabilityValue(
                value=0.0,
                value_type=ValueType.MISSING,
                source="not_available",
                metadata={"reason": "Missing revenue or cost data"}
            )
        
        net_profit = gross_revenue.value - total_cost.value
        
        # Value type is estimated if either component is estimated or modeled
        if gross_revenue.value_type == ValueType.OBSERVED and total_cost.value_type == ValueType.OBSERVED:
            value_type = ValueType.OBSERVED
            confidence = 1.0
        else:
            value_type = ValueType.ESTIMATED
            # Confidence is minimum of component confidences
            confidence = min(gross_revenue.confidence, total_cost.confidence)
        
        return ProfitabilityValue(
            value=net_profit,
            value_type=value_type,
            source="calculated",
            confidence=confidence,
            metadata={
                "gross_revenue": gross_revenue.to_dict(),
                "total_cost": total_cost.to_dict()
            }
        )
    
    def calculate_profit_margin(
        self,
        net_profit: ProfitabilityValue,
        gross_revenue: ProfitabilityValue
    ) -> ProfitabilityValue:
        """Calculate profit margin percentage.
        
        Args:
            net_profit: Net profit value
            gross_revenue: Gross revenue value
        
        Returns:
            ProfitabilityValue with profit margin
        """
        if gross_revenue.value_type == ValueType.MISSING or gross_revenue.value == 0:
            return ProfitabilityValue(
                value=0.0,
                value_type=ValueType.MISSING,
                source="not_available",
                metadata={"reason": "Missing or zero revenue data"}
            )
        
        profit_margin = (net_profit.value / gross_revenue.value) * 100
        
        # Value type follows net_profit type
        value_type = net_profit.value_type
        confidence = net_profit.confidence
        
        return ProfitabilityValue(
            value=profit_margin,
            value_type=value_type,
            source="calculated",
            confidence=confidence,
            metadata={
                "net_profit": net_profit.to_dict(),
                "gross_revenue": gross_revenue.to_dict()
            }
        )
    
    def calculate_return_on_assets(
        self,
        net_profit: ProfitabilityValue,
        average_assets: float
    ) -> ProfitabilityValue:
        """Calculate return on assets (ROA).
        
        Args:
            net_profit: Net profit value
            average_assets: Average assets deployed
        
        Returns:
            ProfitabilityValue with ROA
        """
        if average_assets == 0:
            return ProfitabilityValue(
                value=0.0,
                value_type=ValueType.MISSING,
                source="not_available",
                metadata={"reason": "Zero assets"}
            )
        
        roa = (net_profit.value / average_assets) * 100
        
        return ProfitabilityValue(
            value=roa,
            value_type=net_profit.value_type,
            source="calculated",
            confidence=net_profit.confidence,
            metadata={
                "net_profit": net_profit.to_dict(),
                "average_assets": average_assets
            }
        )
    
    def calculate_return_on_equity(
        self,
        net_profit: ProfitabilityValue,
        average_equity: float
    ) -> ProfitabilityValue:
        """Calculate return on equity (ROE).
        
        Args:
            net_profit: Net profit value
            average_equity: Average equity capital
        
        Returns:
            ProfitabilityValue with ROE
        """
        if average_equity == 0:
            return ProfitabilityValue(
                value=0.0,
                value_type=ValueType.MISSING,
                source="not_available",
                metadata={"reason": "Zero equity"}
            )
        
        roe = (net_profit.value / average_equity) * 100
        
        return ProfitabilityValue(
            value=roe,
            value_type=net_profit.value_type,
            source="calculated",
            confidence=net_profit.confidence,
            metadata={
                "net_profit": net_profit.to_dict(),
                "average_equity": average_equity
            }
        )
    
    def calculate_comprehensive_profitability(
        self,
        revenue_df: pd.DataFrame,
        cost_df: pd.DataFrame,
        revenue_columns: Dict[str, str],
        cost_columns: Dict[str, str],
        total_operational_overhead: Optional[float] = None,
        average_assets: Optional[float] = None,
        average_equity: Optional[float] = None
    ) -> Dict[str, ProfitabilityValue]:
        """Calculate comprehensive profitability metrics.
        
        Args:
            revenue_df: DataFrame with revenue data
            cost_df: DataFrame with cost data
            revenue_columns: Revenue column mappings
            cost_columns: Cost column mappings
            total_operational_overhead: Total operational overhead
            average_assets: Average assets for ROA
            average_equity: Average equity for ROE
        
        Returns:
            Dictionary of ProfitabilityValues for all metrics
        """
        results = {}
        
        # Calculate revenue breakdown
        revenue_breakdown = self.revenue_calculator.calculate_revenue_breakdown(
            revenue_df, revenue_columns
        )
        results.update(revenue_breakdown)
        
        # Calculate cost breakdown
        cost_breakdown = self.cost_calculator.calculate_cost_breakdown(
            cost_df, cost_columns, total_operational_overhead
        )
        results.update(cost_breakdown)
        
        # Calculate net profit
        results["net_profit"] = self.calculate_net_profit(
            revenue_breakdown["gross_revenue"],
            cost_breakdown["total_cost"]
        )
        
        # Calculate profit margin
        results["profit_margin"] = self.calculate_profit_margin(
            results["net_profit"],
            revenue_breakdown["gross_revenue"]
        )
        
        # Calculate ROA if assets provided
        if average_assets is not None:
            results["return_on_assets"] = self.calculate_return_on_assets(
                results["net_profit"],
                average_assets
            )
        
        # Calculate ROE if equity provided
        if average_equity is not None:
            results["return_on_equity"] = self.calculate_return_on_equity(
                results["net_profit"],
                average_equity
            )
        
        return results
