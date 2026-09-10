"""Orchestrator for profitability analytics."""

from datetime import date
from typing import Dict, Any, Optional
import logging

import pandas as pd

from src.profitability_analytics.base import (
    ProfitabilityBase,
    ValueType,
)
from src.profitability_analytics.revenue import RevenueCalculator
from src.profitability_analytics.costs import CostCalculator
from src.profitability_analytics.profitability import ProfitabilityCalculator
from src.profitability_analytics.level_analysis import LevelProfitabilityAnalyzer
from src.profitability_analytics.temporal import TemporalProfitabilityAnalyzer
from src.profitability_analytics.tiers import ProfitabilityTierEngine

logger = logging.getLogger(__name__)


class ProfitabilityOrchestrator(ProfitabilityBase):
    """Orchestrates profitability analytics operations."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize profitability orchestrator.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
        
        # Initialize components
        self.revenue_calculator = RevenueCalculator(as_of_date)
        self.cost_calculator = CostCalculator(as_of_date)
        self.profitability_calculator = ProfitabilityCalculator(as_of_date)
        self.level_analyzer = LevelProfitabilityAnalyzer(as_of_date)
        self.temporal_analyzer = TemporalProfitabilityAnalyzer(as_of_date)
        self.tier_engine = ProfitabilityTierEngine()
    
    def generate_comprehensive_profitability_report(
        self,
        revenue_df: pd.DataFrame,
        cost_df: pd.DataFrame,
        revenue_columns: Dict[str, str],
        cost_columns: Dict[str, str],
        total_operational_overhead: Optional[float] = None,
        average_assets: Optional[float] = None,
        average_equity: Optional[float] = None,
        customer_column: str = "customer_key",
        date_column: str = "period_date"
    ) -> Dict[str, Any]:
        """Generate comprehensive profitability analytics report.
        
        Args:
            revenue_df: DataFrame with revenue data
            cost_df: DataFrame with cost data
            revenue_columns: Revenue column mappings
            cost_columns: Cost column mappings
            total_operational_overhead: Total operational overhead
            average_assets: Average assets for ROA
            average_equity: Average equity for ROE
            customer_column: Name of customer column
            date_column: Name of date column
        
        Returns:
            Dictionary with comprehensive analytics results
        """
        logger.info("Generating comprehensive profitability report")
        
        report = {
            "metadata": {
                "as_of_date": self.as_of_date.isoformat(),
                "value_type_system": "observed/estimated/modeled"
            },
            "overall_profitability": {},
            "customer_level": {},
            "monthly_trends": {},
            "annualized": {},
            "tiers": {}
        }
        
        # Overall profitability
        report["overall_profitability"] = self.profitability_calculator.calculate_comprehensive_profitability(
            revenue_df, cost_df, revenue_columns, cost_columns,
            total_operational_overhead, average_assets, average_equity
        )
        
        # Customer-level profitability
        merged_df = self._merge_dataframes(revenue_df, cost_df)
        if customer_column in merged_df.columns:
            customer_profitability = self.level_analyzer.analyze_customer_profitability(
                merged_df, customer_column, revenue_columns, cost_columns, total_operational_overhead
            )
            report["customer_level"] = customer_profitability.to_dict("records")
        
        # Monthly trends
        if date_column in merged_df.columns:
            monthly_profitability = self.temporal_analyzer.analyze_monthly_profitability(
                merged_df, date_column, revenue_columns, cost_columns, total_operational_overhead
            )
            report["monthly_trends"] = monthly_profitability.to_dict("records")
            
            # Annualized profitability
            months_available = len(monthly_profitability)
            report["annualized"] = self.temporal_analyzer.calculate_annualized_profitability_with_variance(
                monthly_profitability, months_available
            )
        
        # Tier classification
        if "customer_level" in report and len(report["customer_level"]) > 0:
            net_profits = [c["net_profit"] for c in report["customer_level"]]
            margins = [c["profit_margin"] for c in report["customer_level"]]
            tiers = self.tier_engine.classify_batch(net_profits, margins)
            for i, customer in enumerate(report["customer_level"]):
                customer["profitability_tier"] = tiers[i]
        
        return report
    
    def _merge_dataframes(
        self,
        revenue_df: pd.DataFrame,
        cost_df: pd.DataFrame
    ) -> pd.DataFrame:
        """Merge revenue and cost DataFrames.
        
        Args:
            revenue_df: Revenue DataFrame
            cost_df: Cost DataFrame
        
        Returns:
            Merged DataFrame
        """
        # Simple merge on common columns
        common_cols = list(set(revenue_df.columns) & set(cost_df.columns))
        if common_cols:
            return revenue_df.merge(cost_df, on=common_cols, how="outer")
        else:
            # If no common columns, concatenate
            return pd.concat([revenue_df, cost_df], axis=1)
    
    def generate_customer_profitability_report(
        self,
        df: pd.DataFrame,
        customer_key: int,
        revenue_columns: Dict[str, str],
        cost_columns: Dict[str, str],
        total_operational_overhead: Optional[float] = None,
        customer_column: str = "customer_key"
    ) -> Dict[str, Any]:
        """Generate customer-specific profitability report.
        
        Args:
            df: DataFrame with profitability data
            customer_key: Customer key to analyze
            revenue_columns: Revenue column mappings
            cost_columns: Cost column mappings
            total_operational_overhead: Total operational overhead
            customer_column: Name of customer column
        
        Returns:
            Dictionary with customer-specific analytics
        """
        logger.info(f"Generating report for customer {customer_key}")
        
        # Filter to customer
        customer_df = df[df[customer_column] == customer_key].copy()
        
        if len(customer_df) == 0:
            return {"error": f"No data found for customer {customer_key}"}
        
        report = {
            "customer_key": customer_key,
            "metadata": {
                "as_of_date": self.as_of_date.isoformat()
            }
        }
        
        # Calculate profitability
        profitability = self.profitability_calculator.calculate_comprehensive_profitability(
            customer_df, customer_df, revenue_columns, cost_columns,
            total_operational_overhead
        )
        
        # Convert ProfitabilityValues to dictionaries
        for key, value in profitability.items():
            if hasattr(value, 'to_dict'):
                report[key] = value.to_dict()
            else:
                report[key] = value
        
        # Classify tier
        net_profit = profitability.get("net_profit")
        profit_margin = profitability.get("profit_margin")
        
        if net_profit and profit_margin:
            tier = self.tier_engine.classify(
                net_profit.value if hasattr(net_profit, 'value') else net_profit,
                profit_margin.value if hasattr(profit_margin, 'value') else profit_margin
            )
            report["profitability_tier"] = tier
        
        return report
    
    def update_tier_thresholds(self, thresholds) -> None:
        """Update profitability tier thresholds.
        
        Args:
            thresholds: New list of tier thresholds
        """
        self.tier_engine.update_thresholds(thresholds)
        logger.info("Updated profitability tier thresholds")
    
    def get_metric_registry(self) -> Dict[str, Any]:
        """Get all registered metric definitions.
        
        Returns:
            Dictionary of metric definitions
        """
        return self.get_all_metric_definitions()
