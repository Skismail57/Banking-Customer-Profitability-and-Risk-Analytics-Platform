"""Temporal profitability analysis (monthly, annualized)."""

from datetime import date, timedelta
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
from src.profitability_analytics.profitability import ProfitabilityCalculator

logger = logging.getLogger(__name__)


class TemporalProfitabilityAnalyzer(ProfitabilityBase):
    """Analyze profitability over time periods (monthly, annualized)."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize temporal profitability analyzer.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
        self.revenue_calculator = RevenueCalculator(as_of_date)
        self.cost_calculator = CostCalculator(as_of_date)
        self.profitability_calculator = ProfitabilityCalculator(as_of_date)
    
    def analyze_monthly_profitability(
        self,
        df: pd.DataFrame,
        date_column: str = "period_date",
        revenue_columns: Dict[str, str] = None,
        cost_columns: Dict[str, str] = None,
        total_operational_overhead: Optional[float] = None
    ) -> pd.DataFrame:
        """Analyze profitability by month.
        
        Args:
            df: DataFrame with profitability data
            date_column: Name of date column
            revenue_columns: Revenue column mappings
            cost_columns: Cost column mappings
            total_operational_overhead: Total operational overhead
        
        Returns:
            DataFrame with monthly profitability
        """
        logger.info("Analyzing monthly profitability")
        
        if revenue_columns is None:
            revenue_columns = {}
        if cost_columns is None:
            cost_columns = {}
        
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])
        df["month"] = df[date_column].dt.to_period("M").dt.start_time.dt.date
        
        results = []
        
        for month, month_df in df.groupby("month"):
            # Calculate revenue for this month
            revenue_breakdown = self.revenue_calculator.calculate_revenue_breakdown(
                month_df, revenue_columns
            )
            
            # Calculate cost for this month
            cost_breakdown = self.cost_calculator.calculate_cost_breakdown(
                month_df, cost_columns, total_operational_overhead
            )
            
            # Calculate profitability
            net_profit = self.profitability_calculator.calculate_net_profit(
                revenue_breakdown["gross_revenue"],
                cost_breakdown["total_cost"]
            )
            
            profit_margin = self.profitability_calculator.calculate_profit_margin(
                net_profit,
                revenue_breakdown["gross_revenue"]
            )
            
            results.append({
                "period": month,
                "period_type": "monthly",
                "gross_revenue": revenue_breakdown["gross_revenue"].value,
                "gross_revenue_type": revenue_breakdown["gross_revenue"].value_type.value,
                "total_cost": cost_breakdown["total_cost"].value,
                "total_cost_type": cost_breakdown["total_cost"].value_type.value,
                "net_profit": net_profit.value,
                "net_profit_type": net_profit.value_type.value,
                "profit_margin": profit_margin.value,
                "profit_margin_type": profit_margin.value_type.value,
            })
        
        return pd.DataFrame(results).sort_values("period")
    
    def calculate_annualized_profitability(
        self,
        monthly_profitability_df: pd.DataFrame,
        months_available: int
    ) -> Dict[str, Any]:
        """Calculate annualized profitability from monthly data.
        
        Args:
            monthly_profitability_df: DataFrame with monthly profitability
            months_available: Number of months of data available
        
        Returns:
            Dictionary with annualized metrics
        """
        logger.info(f"Calculating annualized profitability from {months_available} months")
        
        if len(monthly_profitability_df) == 0:
            return {"error": "No monthly data available"}
        
        # Sum monthly values
        total_gross_revenue = monthly_profitability_df["gross_revenue"].sum()
        total_cost = monthly_profitability_df["total_cost"].sum()
        total_net_profit = monthly_profitability_df["net_profit"].sum()
        
        # Calculate annualized values
        if months_available > 0:
            annualization_factor = 12 / months_available
            annualized_gross_revenue = total_gross_revenue * annualization_factor
            annualized_cost = total_cost * annualization_factor
            annualized_net_profit = total_net_profit * annualization_factor
        else:
            annualized_gross_revenue = 0
            annualized_cost = 0
            annualized_net_profit = 0
        
        # Calculate annualized margin
        if annualized_gross_revenue != 0:
            annualized_margin = (annualized_net_profit / annualized_gross_revenue) * 100
        else:
            annualized_margin = 0
        
        # Determine value type based on data completeness
        value_type = "observed" if months_available >= 12 else "estimated"
        confidence = min(1.0, months_available / 12)
        
        return {
            "months_available": months_available,
            "annualization_factor": annualization_factor if months_available > 0 else 0,
            "annualized_gross_revenue": annualized_gross_revenue,
            "annualized_cost": annualized_cost,
            "annualized_net_profit": annualized_net_profit,
            "annualized_profit_margin": annualized_margin,
            "value_type": value_type,
            "confidence": confidence,
        }
    
    def calculate_annualized_profitability_with_variance(
        self,
        monthly_profitability_df: pd.DataFrame,
        months_available: int
    ) -> Dict[str, Any]:
        """Calculate annualized profitability with variance statistics.
        
        Args:
            monthly_profitability_df: DataFrame with monthly profitability
            months_available: Number of months of data available
        
        Returns:
            Dictionary with annualized metrics and variance
        """
        logger.info(f"Calculating annualized profitability with variance from {months_available} months")
        
        if len(monthly_profitability_df) == 0:
            return {"error": "No monthly data available"}
        
        # Calculate statistics
        monthly_net_profits = monthly_profitability_df["net_profit"].values
        monthly_margins = monthly_profitability_df["profit_margin"].values
        
        # Annualized values
        annualized = self.calculate_annualized_profitability(
            monthly_profitability_df, months_available
        )
        
        # Add variance statistics
        annualized["monthly_net_profit_std"] = monthly_net_profits.std()
        annualized["monthly_net_profit_mean"] = monthly_net_profits.mean()
        annualized["monthly_margin_std"] = monthly_margins.std()
        annualized["monthly_margin_mean"] = monthly_margins.mean()
        
        # Coefficient of variation (stability measure)
        if monthly_net_profits.mean() != 0:
            annualized["profit_cv"] = monthly_net_profits.std() / abs(monthly_net_profits.mean())
        else:
            annualized["profit_cv"] = 0
        
        return annualized
