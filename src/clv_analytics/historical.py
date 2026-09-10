"""Historical CLV calculation."""

from datetime import date, timedelta
from typing import Dict, Any, Optional
import logging

import pandas as pd
import numpy as np

from src.clv_analytics.base import CLVBase, CLVType, CLVParameters, CLVResult

logger = logging.getLogger(__name__)


class HistoricalCLVCalculator(CLVBase):
    """Calculate Historical CLV (actual historical value)."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize historical CLV calculator.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
    
    def calculate(
        self,
        df: pd.DataFrame,
        customer_column: str = "customer_key",
        profit_column: str = "net_profit",
        date_column: str = "as_of_date",
        params: Optional[CLVParameters] = None
    ) -> CLVResult:
        """Calculate historical CLV for a single customer.
        
        Args:
            df: DataFrame with customer profit data
            customer_column: Name of customer column
            profit_column: Name of profit column
            date_column: Name of date column
            params: CLV parameters (optional)
        
        Returns:
            CLVResult with historical CLV value
        """
        if params is None:
            params = self.get_default_parameters()
        
        # Validate parameters
        if not self.validate_parameters(params):
            raise ValueError("Invalid CLV parameters")
        
        # Get customer key
        customer_key = df[customer_column].iloc[0]
        
        # Calculate historical profit
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])
        
        # Sum all historical profit
        historical_profit = df[profit_column].sum()
        
        # Calculate tenure in years
        if len(df) > 0:
            first_date = df[date_column].min()
            last_date = df[date_column].max()
            tenure_years = (last_date - first_date).days / 365.25
        else:
            tenure_years = 0
        
        # Calculate average annual profit
        if tenure_years > 0:
            average_annual_profit = historical_profit / tenure_years
        else:
            average_annual_profit = historical_profit
        
        # Historical CLV is the sum of historical profit (no discounting for historical)
        clv_value = historical_profit
        
        return CLVResult(
            customer_key=customer_key,
            clv_type=CLVType.HISTORICAL,
            clv_value=clv_value,
            parameters=params,
            calculation_date=self.as_of_date,
            components={
                "historical_profit": historical_profit,
                "tenure_years": tenure_years,
                "average_annual_profit": average_annual_profit,
                "period_count": len(df)
            },
            assumptions=[
                "Historical CLV is sum of actual profits",
                "No discounting applied to historical values",
                "All historical periods included"
            ],
            limitations=[
                "Does not reflect future value",
                "May not be representative of future behavior",
                "Does not account for inflation"
            ]
        )
    
    def calculate_batch(
        self,
        df: pd.DataFrame,
        customer_column: str = "customer_key",
        profit_column: str = "net_profit",
        date_column: str = "as_of_date",
        params: Optional[CLVParameters] = None
    ) -> pd.DataFrame:
        """Calculate historical CLV for multiple customers.
        
        Args:
            df: DataFrame with customer profit data
            customer_column: Name of customer column
            profit_column: Name of profit column
            date_column: Name of date column
            params: CLV parameters (optional)
        
        Returns:
            DataFrame with historical CLV for each customer
        """
        results = []
        
        for customer_key in df[customer_column].unique():
            customer_df = df[df[customer_column] == customer_key]
            result = self.calculate(
                customer_df, customer_column, profit_column, date_column, params
            )
            results.append(result.to_dict())
        
        return pd.DataFrame(results)
