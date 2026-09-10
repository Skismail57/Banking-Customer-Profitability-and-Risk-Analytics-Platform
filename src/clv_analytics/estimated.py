"""Estimated CLV calculation (simplified estimate based on averages)."""

from datetime import date
from typing import Dict, Any, Optional
import logging

import pandas as pd
import numpy as np

from src.clv_analytics.base import CLVBase, CLVType, CLVParameters, CLVResult

logger = logging.getLogger(__name__)


class EstimatedCLVCalculator(CLVBase):
    """Calculate Estimated CLV (simplified estimate based on averages)."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize estimated CLV calculator.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
    
    def calculate(
        self,
        df: pd.DataFrame,
        customer_column: str = "customer_key",
        params: Optional[CLVParameters] = None
    ) -> CLVResult:
        """Calculate estimated CLV for a single customer.
        
        Args:
            df: DataFrame with customer data
            customer_column: Name of customer column
            params: CLV parameters
        
        Returns:
            CLVResult with estimated CLV value
        
        Note:
            This uses simple averages and assumptions for quick estimation.
            Less accurate than Predicted CLV but requires less data.
        """
        if params is None:
            params = self.get_default_parameters()
        
        # Validate parameters
        if not self.validate_parameters(params):
            raise ValueError("Invalid CLV parameters")
        
        # Get customer key
        customer_key = df[customer_column].iloc[0]
        
        # Use parameter averages
        average_revenue = params.average_revenue or 0
        average_cost = params.average_cost or 0
        average_profit = params.average_profit or (average_revenue - average_cost)
        
        # Calculate estimated CLV using simple formula
        # CLV = (Average Profit * Retention Rate) / (1 + Discount Rate - Retention Rate)
        # This is the perpetuity formula with retention
        
        if params.retention_rate >= (1 + params.discount_rate):
            logger.warning(
                f"Retention rate ({params.retention_rate}) >= 1 + discount rate "
                f"({1 + params.discount_rate}), using time horizon instead"
            )
            # Use finite horizon instead
            clv_value = self._calculate_finite_horizon_clv(
                average_profit,
                params.retention_rate,
                params.discount_rate,
                params.time_horizon_years
            )
        else:
            # Use perpetuity formula
            clv_value = (average_profit * params.retention_rate) / (
                1 + params.discount_rate - params.retention_rate
            )
        
        return CLVResult(
            customer_key=customer_key,
            clv_type=CLVType.ESTIMATED,
            clv_value=clv_value,
            parameters=params,
            calculation_date=self.as_of_date,
            components={
                "average_revenue": average_revenue,
                "average_cost": average_cost,
                "average_profit": average_profit,
                "retention_rate": params.retention_rate,
                "discount_rate": params.discount_rate,
                "formula": "perpetuity_with_retention"
            },
            assumptions=[
                "Average profit representative of customer",
                "Retention rate constant over time",
                "Discount rate appropriate for time value",
                "Simple perpetuity formula applicable"
            ],
            limitations=[
                "Uses averages, not customer-specific data",
                "Assumes constant retention and discount rates",
                "Less accurate than Predicted CLV",
                "Perpetuity formula assumes infinite horizon"
            ]
        )
    
    def _calculate_finite_horizon_clv(
        self,
        average_profit: float,
        retention_rate: float,
        discount_rate: float,
        time_horizon_years: int
    ) -> float:
        """Calculate CLV with finite time horizon.
        
        Args:
            average_profit: Average annual profit
            retention_rate: Annual retention rate
            discount_rate: Annual discount rate
            time_horizon_years: Projection horizon
        
        Returns:
            CLV with finite horizon
        """
        clv = 0.0
        
        for year in range(1, time_horizon_years + 1):
            retention_probability = retention_rate ** year
            discount_factor = 1 / ((1 + discount_rate) ** year)
            present_value = average_profit * retention_probability * discount_factor
            clv += present_value
        
        return clv
    
    def calculate_batch(
        self,
        df: pd.DataFrame,
        customer_column: str = "customer_key",
        params: Optional[CLVParameters] = None
    ) -> pd.DataFrame:
        """Calculate estimated CLV for multiple customers.
        
        Args:
            df: DataFrame with customer data
            customer_column: Name of customer column
            params: CLV parameters
        
        Returns:
            DataFrame with estimated CLV for each customer
        """
        results = []
        
        for customer_key in df[customer_column].unique():
            customer_df = df[df[customer_column] == customer_key]
            result = self.calculate(customer_df, customer_column, params)
            results.append(result.to_dict())
        
        return pd.DataFrame(results)
