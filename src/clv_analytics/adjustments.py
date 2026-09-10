"""CLV adjustments (retention-adjusted, profitability-adjusted)."""

from datetime import date
from typing import Dict, Any, Optional
import logging

import pandas as pd
import numpy as np

from src.clv_analytics.base import CLVBase, CLVParameters

logger = logging.getLogger(__name__)


class RetentionAdjustedCLV(CLVBase):
    """Calculate retention-adjusted CLV."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize retention-adjusted CLV calculator.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
    
    def calculate(
        self,
        base_clv: float,
        retention_rate: float,
        discount_rate: float = 0.10,
        time_horizon_years: int = 5
    ) -> Dict[str, Any]:
        """Calculate retention-adjusted CLV.
        
        Args:
            base_clv: Base CLV value (e.g., average annual profit)
            retention_rate: Annual retention rate
            discount_rate: Annual discount rate
            time_horizon_years: Projection horizon
        
        Returns:
            Dictionary with retention-adjusted CLV and components
        """
        clv = 0.0
        retention_probabilities = []
        discount_factors = []
        present_values = []
        
        for year in range(1, time_horizon_years + 1):
            # Probability of retention
            retention_probability = retention_rate ** year
            retention_probabilities.append(retention_probability)
            
            # Discount factor
            discount_factor = 1 / ((1 + discount_rate) ** year)
            discount_factors.append(discount_factor)
            
            # Present value of profit in this year
            present_value = base_clv * retention_probability * discount_factor
            present_values.append(present_value)
            
            clv += present_value
        
        return {
            "retention_adjusted_clv": clv,
            "base_clv": base_clv,
            "retention_rate": retention_rate,
            "discount_rate": discount_rate,
            "time_horizon_years": time_horizon_years,
            "components": {
                "retention_probabilities": retention_probabilities,
                "discount_factors": discount_factors,
                "present_values": present_values
            }
        }
    
    def calculate_with_churn_rate(
        self,
        base_clv: float,
        churn_rate: float,
        discount_rate: float = 0.10,
        time_horizon_years: int = 5
    ) -> Dict[str, Any]:
        """Calculate retention-adjusted CLV using churn rate.
        
        Args:
            base_clv: Base CLV value
            churn_rate: Annual churn rate (1 - retention_rate)
            discount_rate: Annual discount rate
            time_horizon_years: Projection horizon
        
        Returns:
            Dictionary with retention-adjusted CLV
        """
        retention_rate = 1 - churn_rate
        return self.calculate(base_clv, retention_rate, discount_rate, time_horizon_years)


class ProfitabilityAdjustedCLV(CLVBase):
    """Calculate profitability-adjusted CLV."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize profitability-adjusted CLV calculator.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
    
    def calculate(
        self,
        base_clv: float,
        profit_margin: float,
        retention_rate: float = 0.80,
        discount_rate: float = 0.10,
        time_horizon_years: int = 5
    ) -> Dict[str, Any]:
        """Calculate profitability-adjusted CLV.
        
        Args:
            base_clv: Base CLV value (e.g., revenue-based)
            profit_margin: Profit margin (profit / revenue)
            retention_rate: Annual retention rate
            discount_rate: Annual discount rate
            time_horizon_years: Projection horizon
        
        Returns:
            Dictionary with profitability-adjusted CLV and components
        """
        # Adjust base CLV by profit margin
        profit_adjusted_base = base_clv * profit_margin
        
        # Apply retention adjustment
        retention_adjusted = self._apply_retention_adjustment(
            profit_adjusted_base,
            retention_rate,
            discount_rate,
            time_horizon_years
        )
        
        return {
            "profitability_adjusted_clv": retention_adjusted,
            "base_clv": base_clv,
            "profit_margin": profit_margin,
            "profit_adjusted_base": profit_adjusted_base,
            "retention_rate": retention_rate,
            "discount_rate": discount_rate,
            "time_horizon_years": time_horizon_years,
            "adjustment_factor": profit_margin
        }
    
    def _apply_retention_adjustment(
        self,
        base_value: float,
        retention_rate: float,
        discount_rate: float,
        time_horizon_years: int
    ) -> float:
        """Apply retention adjustment to base value.
        
        Args:
            base_value: Base value to adjust
            retention_rate: Annual retention rate
            discount_rate: Annual discount rate
            time_horizon_years: Projection horizon
        
        Returns:
            Retention-adjusted value
        """
        clv = 0.0
        
        for year in range(1, time_horizon_years + 1):
            retention_probability = retention_rate ** year
            discount_factor = 1 / ((1 + discount_rate) ** year)
            present_value = base_value * retention_probability * discount_factor
            clv += present_value
        
        return clv
    
    def calculate_with_revenue_and_cost(
        self,
        average_revenue: float,
        average_cost: float,
        retention_rate: float = 0.80,
        discount_rate: float = 0.10,
        time_horizon_years: int = 5
    ) -> Dict[str, Any]:
        """Calculate profitability-adjusted CLV from revenue and cost.
        
        Args:
            average_revenue: Average annual revenue
            average_cost: Average annual cost
            retention_rate: Annual retention rate
            discount_rate: Annual discount rate
            time_horizon_years: Projection horizon
        
        Returns:
            Dictionary with profitability-adjusted CLV
        """
        average_profit = average_revenue - average_cost
        profit_margin = average_profit / average_revenue if average_revenue > 0 else 0
        
        return self.calculate(
            average_revenue,
            profit_margin,
            retention_rate,
            discount_rate,
            time_horizon_years
        )
