"""CLV Sensitivity Analysis.

This module implements sensitivity analysis for Customer Lifetime Value (CLV)
to understand how changes in key parameters affect CLV estimates.

Key Sensitivity Dimensions:
- Retention rate sensitivity
- Revenue sensitivity
- Cost sensitivity
- Discount rate sensitivity
- Time horizon sensitivity

NOTE: This is an analytical/educational model for decision support.
It does not make actual lending decisions.
"""

from datetime import date
from typing import Dict, Any, List, Optional
import logging

import pandas as pd
import numpy as np

from src.clv_analytics.base import CLVBase, CLVParameters

logger = logging.getLogger(__name__)


class CLVSensitivityAnalyzer(CLVBase):
    """Analyze CLV sensitivity to parameter changes.
    
    This class performs sensitivity analysis to understand how CLV estimates
    change with variations in key parameters.
    
    Assumptions:
    - CLV follows a discounted cash flow model
    - Retention rate is constant over time
    - Revenue and costs are stable over time horizon
    - Discount rate reflects time value of money
    
    Limitations:
    - Assumes constant parameters (may not reflect reality)
    - Does not account for customer lifecycle changes
    - Sensitivity ranges are arbitrary
    - May not capture non-linear relationships
    
    Fairness Considerations:
    - Analyze CLV sensitivity across demographic groups
    - Check for disparate impact in CLV assumptions
    - Ensure CLV estimates are not biased
    - Regular audit for bias in CLV calculations
    """
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize CLV sensitivity analyzer.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
    
    def analyze_retention_sensitivity(
        self,
        base_clv: float,
        base_retention_rate: float,
        retention_range: Optional[List[float]] = None,
        discount_rate: float = 0.10,
        time_horizon_years: int = 5
    ) -> pd.DataFrame:
        """Analyze CLV sensitivity to retention rate changes.
        
        Args:
            base_clv: Base CLV value
            base_retention_rate: Base retention rate
            retention_range: Range of retention rates to test
            discount_rate: Annual discount rate
            time_horizon_years: Projection horizon
        
        Returns:
            DataFrame with sensitivity analysis results
        """
        if retention_range is None:
            retention_range = np.linspace(0.5, 0.95, 10)
        
        results = []
        
        for retention_rate in retention_range:
            clv = self._calculate_clv_with_retention(
                base_clv, retention_rate, discount_rate, time_horizon_years
            )
            
            clv_change_pct = ((clv - base_clv) / base_clv * 100) if base_clv != 0 else 0
            retention_change_pct = ((retention_rate - base_retention_rate) / base_retention_rate * 100) if base_retention_rate != 0 else 0
            
            results.append({
                "retention_rate": retention_rate,
                "clv": clv,
                "clv_change_pct": clv_change_pct,
                "retention_change_pct": retention_change_pct
            })
        
        return pd.DataFrame(results)
    
    def analyze_revenue_sensitivity(
        self,
        base_revenue: float,
        revenue_range: Optional[List[float]] = None,
        profit_margin: float = 0.20,
        retention_rate: float = 0.80,
        discount_rate: float = 0.10,
        time_horizon_years: int = 5
    ) -> pd.DataFrame:
        """Analyze CLV sensitivity to revenue changes.
        
        Args:
            base_revenue: Base revenue
            revenue_range: Range of revenue values to test
            profit_margin: Profit margin
            retention_rate: Annual retention rate
            discount_rate: Annual discount rate
            time_horizon_years: Projection horizon
        
        Returns:
            DataFrame with sensitivity analysis results
        """
        if revenue_range is None:
            revenue_range = np.linspace(base_revenue * 0.5, base_revenue * 1.5, 10)
        
        results = []
        
        for revenue in revenue_range:
            profit = revenue * profit_margin
            clv = self._calculate_clv_with_retention(
                profit, retention_rate, discount_rate, time_horizon_years
            )
            
            clv_change_pct = ((clv - (base_revenue * profit_margin)) / (base_revenue * profit_margin) * 100) if base_revenue > 0 else 0
            revenue_change_pct = ((revenue - base_revenue) / base_revenue * 100) if base_revenue != 0 else 0
            
            results.append({
                "revenue": revenue,
                "profit": profit,
                "clv": clv,
                "clv_change_pct": clv_change_pct,
                "revenue_change_pct": revenue_change_pct
            })
        
        return pd.DataFrame(results)
    
    def analyze_cost_sensitivity(
        self,
        base_revenue: float,
        base_cost: float,
        cost_range: Optional[List[float]] = None,
        retention_rate: float = 0.80,
        discount_rate: float = 0.10,
        time_horizon_years: int = 5
    ) -> pd.DataFrame:
        """Analyze CLV sensitivity to cost changes.
        
        Args:
            base_revenue: Base revenue
            base_cost: Base cost
            cost_range: Range of cost values to test
            retention_rate: Annual retention rate
            discount_rate: Annual discount rate
            time_horizon_years: Projection horizon
        
        Returns:
            DataFrame with sensitivity analysis results
        """
        if cost_range is None:
            cost_range = np.linspace(base_cost * 0.5, base_cost * 1.5, 10)
        
        base_profit = base_revenue - base_cost
        results = []
        
        for cost in cost_range:
            profit = base_revenue - cost
            clv = self._calculate_clv_with_retention(
                profit, retention_rate, discount_rate, time_horizon_years
            )
            
            clv_change_pct = ((clv - base_profit) / base_profit * 100) if base_profit != 0 else 0
            cost_change_pct = ((cost - base_cost) / base_cost * 100) if base_cost != 0 else 0
            
            results.append({
                "cost": cost,
                "profit": profit,
                "clv": clv,
                "clv_change_pct": clv_change_pct,
                "cost_change_pct": cost_change_pct
            })
        
        return pd.DataFrame(results)
    
    def analyze_discount_rate_sensitivity(
        self,
        base_clv: float,
        base_discount_rate: float,
        discount_range: Optional[List[float]] = None,
        retention_rate: float = 0.80,
        time_horizon_years: int = 5
    ) -> pd.DataFrame:
        """Analyze CLV sensitivity to discount rate changes.
        
        Args:
            base_clv: Base CLV value
            base_discount_rate: Base discount rate
            discount_range: Range of discount rates to test
            retention_rate: Annual retention rate
            time_horizon_years: Projection horizon
        
        Returns:
            DataFrame with sensitivity analysis results
        """
        if discount_range is None:
            discount_range = np.linspace(0.05, 0.20, 10)
        
        results = []
        
        for discount_rate in discount_range:
            clv = self._calculate_clv_with_retention(
                base_clv, retention_rate, discount_rate, time_horizon_years
            )
            
            base_clv_value = self._calculate_clv_with_retention(
                base_clv, retention_rate, base_discount_rate, time_horizon_years
            )
            
            clv_change_pct = ((clv - base_clv_value) / base_clv_value * 100) if base_clv_value != 0 else 0
            discount_change_pct = ((discount_rate - base_discount_rate) / base_discount_rate * 100) if base_discount_rate != 0 else 0
            
            results.append({
                "discount_rate": discount_rate,
                "clv": clv,
                "clv_change_pct": clv_change_pct,
                "discount_change_pct": discount_change_pct
            })
        
        return pd.DataFrame(results)
    
    def analyze_comprehensive_sensitivity(
        self,
        base_clv: float,
        params: CLVParameters,
        sensitivity_ranges: Optional[Dict[str, List[float]]] = None
    ) -> Dict[str, pd.DataFrame]:
        """Analyze CLV sensitivity to all parameters.
        
        Args:
            base_clv: Base CLV value
            params: Base CLV parameters
            sensitivity_ranges: Custom ranges for each parameter
        
        Returns:
            Dictionary with sensitivity analysis for each parameter
        """
        if sensitivity_ranges is None:
            sensitivity_ranges = {
                "retention": np.linspace(0.5, 0.95, 10),
                "discount": np.linspace(0.05, 0.20, 10)
            }
        
        results = {}
        
        results["retention"] = self.analyze_retention_sensitivity(
            base_clv,
            params.retention_rate,
            sensitivity_ranges.get("retention"),
            params.discount_rate,
            params.time_horizon_years
        )
        
        results["discount"] = self.analyze_discount_rate_sensitivity(
            base_clv,
            params.discount_rate,
            sensitivity_ranges.get("discount"),
            params.retention_rate,
            params.time_horizon_years
        )
        
        return results
    
    def _calculate_clv_with_retention(
        self,
        base_value: float,
        retention_rate: float,
        discount_rate: float,
        time_horizon_years: int
    ) -> float:
        """Calculate CLV with retention adjustment.
        
        Args:
            base_value: Base value
            retention_rate: Annual retention rate
            discount_rate: Annual discount rate
            time_horizon_years: Projection horizon
        
        Returns:
            CLV with retention adjustment
        """
        clv = 0.0
        
        for year in range(1, time_horizon_years + 1):
            retention_probability = retention_rate ** year
            discount_factor = 1 / ((1 + discount_rate) ** year)
            present_value = base_value * retention_probability * discount_factor
            clv += present_value
        
        return clv
