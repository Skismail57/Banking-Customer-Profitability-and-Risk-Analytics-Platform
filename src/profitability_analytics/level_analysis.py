"""Level-based profitability analysis (product, account, customer)."""

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
from src.profitability_analytics.profitability import ProfitabilityCalculator

logger = logging.getLogger(__name__)


class LevelProfitabilityAnalyzer(ProfitabilityBase):
    """Analyze profitability at different levels (product, account, customer)."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize level profitability analyzer.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
        self.revenue_calculator = RevenueCalculator(as_of_date)
        self.cost_calculator = CostCalculator(as_of_date)
        self.profitability_calculator = ProfitabilityCalculator(as_of_date)
    
    def analyze_product_profitability(
        self,
        df: pd.DataFrame,
        product_column: str = "product_key",
        revenue_columns: Dict[str, str] = None,
        cost_columns: Dict[str, str] = None
    ) -> pd.DataFrame:
        """Analyze profitability at product level.
        
        Args:
            df: DataFrame with profitability data
            product_column: Name of product column
            revenue_columns: Revenue column mappings
            cost_columns: Cost column mappings
        
        Returns:
            DataFrame with product-level profitability
        """
        logger.info("Analyzing product-level profitability")
        
        if revenue_columns is None:
            revenue_columns = {}
        if cost_columns is None:
            cost_columns = {}
        
        results = []
        
        for product_key, product_df in df.groupby(product_column):
            # Calculate revenue for this product
            revenue_breakdown = self.revenue_calculator.calculate_revenue_breakdown(
                product_df, revenue_columns
            )
            
            # Calculate cost for this product
            cost_breakdown = self.cost_calculator.calculate_cost_breakdown(
                product_df, cost_columns
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
                "product_key": product_key,
                "gross_revenue": revenue_breakdown["gross_revenue"].value,
                "gross_revenue_type": revenue_breakdown["gross_revenue"].value_type.value,
                "total_cost": cost_breakdown["total_cost"].value,
                "total_cost_type": cost_breakdown["total_cost"].value_type.value,
                "net_profit": net_profit.value,
                "net_profit_type": net_profit.value_type.value,
                "profit_margin": profit_margin.value,
                "profit_margin_type": profit_margin.value_type.value,
            })
        
        return pd.DataFrame(results)
    
    def analyze_account_profitability(
        self,
        df: pd.DataFrame,
        account_column: str = "account_id",
        revenue_columns: Dict[str, str] = None,
        cost_columns: Dict[str, str] = None
    ) -> pd.DataFrame:
        """Analyze profitability at account level.
        
        Args:
            df: DataFrame with profitability data
            account_column: Name of account column
            revenue_columns: Revenue column mappings
            cost_columns: Cost column mappings
        
        Returns:
            DataFrame with account-level profitability
        """
        logger.info("Analyzing account-level profitability")
        
        if revenue_columns is None:
            revenue_columns = {}
        if cost_columns is None:
            cost_columns = {}
        
        results = []
        
        for account_id, account_df in df.groupby(account_column):
            # Calculate revenue for this account
            revenue_breakdown = self.revenue_calculator.calculate_revenue_breakdown(
                account_df, revenue_columns
            )
            
            # Calculate cost for this account
            cost_breakdown = self.cost_calculator.calculate_cost_breakdown(
                account_df, cost_columns
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
                "account_id": account_id,
                "gross_revenue": revenue_breakdown["gross_revenue"].value,
                "gross_revenue_type": revenue_breakdown["gross_revenue"].value_type.value,
                "total_cost": cost_breakdown["total_cost"].value,
                "total_cost_type": cost_breakdown["total_cost"].value_type.value,
                "net_profit": net_profit.value,
                "net_profit_type": net_profit.value_type.value,
                "profit_margin": profit_margin.value,
                "profit_margin_type": profit_margin.value_type.value,
            })
        
        return pd.DataFrame(results)
    
    def analyze_customer_profitability(
        self,
        df: pd.DataFrame,
        customer_column: str = "customer_key",
        revenue_columns: Dict[str, str] = None,
        cost_columns: Dict[str, str] = None,
        total_operational_overhead: Optional[float] = None
    ) -> pd.DataFrame:
        """Analyze profitability at customer level.
        
        Args:
            df: DataFrame with profitability data
            customer_column: Name of customer column
            revenue_columns: Revenue column mappings
            cost_columns: Cost column mappings
            total_operational_overhead: Total operational overhead for allocation
        
        Returns:
            DataFrame with customer-level profitability
        """
        logger.info("Analyzing customer-level profitability")
        
        if revenue_columns is None:
            revenue_columns = {}
        if cost_columns is None:
            cost_columns = {}
        
        results = []
        
        for customer_key, customer_df in df.groupby(customer_column):
            # Calculate revenue for this customer
            revenue_breakdown = self.revenue_calculator.calculate_revenue_breakdown(
                customer_df, revenue_columns
            )
            
            # Calculate cost for this customer
            cost_breakdown = self.cost_calculator.calculate_cost_breakdown(
                customer_df, cost_columns, total_operational_overhead
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
                "customer_key": customer_key,
                "gross_revenue": revenue_breakdown["gross_revenue"].value,
                "gross_revenue_type": revenue_breakdown["gross_revenue"].value_type.value,
                "total_cost": cost_breakdown["total_cost"].value,
                "total_cost_type": cost_breakdown["total_cost"].value_type.value,
                "net_profit": net_profit.value,
                "net_profit_type": net_profit.value_type.value,
                "profit_margin": profit_margin.value,
                "profit_margin_type": profit_margin.value_type.value,
            })
        
        return pd.DataFrame(results)
