"""Orchestrator for Customer Lifetime Value analytics."""

from datetime import date
from typing import Dict, Any, List, Optional
import logging

import pandas as pd

from src.clv_analytics.base import CLVBase, CLVType, CLVParameters
from src.clv_analytics.historical import HistoricalCLVCalculator
from src.clv_analytics.predicted import PredictedCLVCalculator
from src.clv_analytics.estimated import EstimatedCLVCalculator
from src.clv_analytics.adjustments import RetentionAdjustedCLV, ProfitabilityAdjustedCLV
from src.clv_analytics.sensitivity import CLVSensitivityAnalyzer

logger = logging.getLogger(__name__)


class CLVOrchestrator(CLVBase):
    """Orchestrates CLV calculations and analysis."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize CLV orchestrator.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
        
        # Initialize components
        self.historical_calculator = HistoricalCLVCalculator(as_of_date)
        self.predicted_calculator = PredictedCLVCalculator(as_of_date)
        self.estimated_calculator = EstimatedCLVCalculator(as_of_date)
        self.retention_adjuster = RetentionAdjustedCLV(as_of_date)
        self.profitability_adjuster = ProfitabilityAdjustedCLV(as_of_date)
        self.sensitivity_analyzer = CLVSensitivityAnalyzer(as_of_date)
    
    def calculate_all_clv_types(
        self,
        df: pd.DataFrame,
        customer_column: str = "customer_key",
        profit_column: str = "net_profit",
        date_column: str = "as_of_date",
        params: Optional[CLVParameters] = None
    ) -> Dict[str, Any]:
        """Calculate all CLV types for comparison.
        
        Args:
            df: DataFrame with customer data
            customer_column: Name of customer column
            profit_column: Name of profit column
            date_column: Name of date column
            params: CLV parameters
        
        Returns:
            Dictionary with all CLV types
        """
        if params is None:
            params = self.get_default_parameters()
        
        logger.info("Calculating all CLV types")
        
        results = {
            "metadata": {
                "as_of_date": self.as_of_date.isoformat(),
                "parameters": params.to_dict()
            }
        }
        
        # Historical CLV
        historical_results = self.historical_calculator.calculate_batch(
            df, customer_column, profit_column, date_column, params
        )
        results["historical_clv"] = historical_results.to_dict("records")
        
        # Predicted CLV
        predicted_results = self.predicted_calculator.calculate_batch(
            df, customer_column, profit_column, date_column, params
        )
        results["predicted_clv"] = predicted_results.to_dict("records")
        
        # Estimated CLV
        estimated_results = self.estimated_calculator.calculate_batch(
            df, customer_column, params
        )
        results["estimated_clv"] = estimated_results.to_dict("records")
        
        return results
    
    def calculate_adjusted_clv(
        self,
        base_clv: float,
        retention_rate: float,
        profit_margin: Optional[float] = None,
        discount_rate: float = 0.10,
        time_horizon_years: int = 5
    ) -> Dict[str, Any]:
        """Calculate retention-adjusted and profitability-adjusted CLV.
        
        Args:
            base_clv: Base CLV value
            retention_rate: Annual retention rate
            profit_margin: Profit margin (optional)
            discount_rate: Annual discount rate
            time_horizon_years: Projection horizon
        
        Returns:
            Dictionary with adjusted CLV values
        """
        logger.info("Calculating adjusted CLV")
        
        results = {}
        
        # Retention-adjusted CLV
        retention_adjusted = self.retention_adjuster.calculate(
            base_clv, retention_rate, discount_rate, time_horizon_years
        )
        results["retention_adjusted"] = retention_adjusted
        
        # Profitability-adjusted CLV (if profit margin provided)
        if profit_margin is not None:
            profitability_adjusted = self.profitability_adjuster.calculate(
                base_clv, profit_margin, retention_rate, discount_rate, time_horizon_years
            )
            results["profitability_adjusted"] = profitability_adjusted
        
        return results
    
    def run_sensitivity_analysis(
        self,
        base_clv: float,
        params: CLVParameters,
        analysis_types: List[str] = None
    ) -> Dict[str, Any]:
        """Run sensitivity analysis on CLV parameters.
        
        Args:
            base_clv: Base CLV value
            params: CLV parameters
            analysis_types: Types of analysis to run (retention, revenue, cost, discount)
        
        Returns:
            Dictionary with sensitivity analysis results
        """
        if analysis_types is None:
            analysis_types = ["retention", "discount"]
        
        logger.info(f"Running sensitivity analysis: {analysis_types}")
        
        results = {}
        
        if "retention" in analysis_types:
            results["retention_sensitivity"] = self.sensitivity_analyzer.analyze_retention_sensitivity(
                base_clv, params.retention_rate, None, params.discount_rate, params.time_horizon_years
            ).to_dict("records")
        
        if "discount" in analysis_types:
            results["discount_sensitivity"] = self.sensitivity_analyzer.analyze_discount_rate_sensitivity(
                base_clv, params.discount_rate, None, params.retention_rate, params.time_horizon_years
            ).to_dict("records")
        
        if "revenue" in analysis_types and params.average_revenue is not None:
            results["revenue_sensitivity"] = self.sensitivity_analyzer.analyze_revenue_sensitivity(
                params.average_revenue, None, 
                (params.average_profit / params.average_revenue) if params.average_revenue > 0 else 0.2,
                params.retention_rate, params.discount_rate, params.time_horizon_years
            ).to_dict("records")
        
        if "cost" in analysis_types and params.average_cost is not None:
            results["cost_sensitivity"] = self.sensitivity_analyzer.analyze_cost_sensitivity(
                params.average_revenue or 0, params.average_cost, None,
                params.retention_rate, params.discount_rate, params.time_horizon_years
            ).to_dict("records")
        
        return results
    
    def generate_clv_report(
        self,
        df: pd.DataFrame,
        customer_column: str = "customer_key",
        profit_column: str = "net_profit",
        date_column: str = "as_of_date",
        params: Optional[CLVParameters] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive CLV report.
        
        Args:
            df: DataFrame with customer data
            customer_column: Name of customer column
            profit_column: Name of profit column
            date_column: Name of date column
            params: CLV parameters
        
        Returns:
            Dictionary with comprehensive CLV report
        """
        logger.info("Generating CLV report")
        
        if params is None:
            params = self.get_default_parameters()
        
        report = {
            "metadata": {
                "as_of_date": self.as_of_date.isoformat(),
                "parameters": params.to_dict(),
                "customer_count": len(df[customer_column].unique())
            },
            "clv_calculations": self.calculate_all_clv_types(
                df, customer_column, profit_column, date_column, params
            )
        }
        
        # Calculate average CLV across customers
        historical_df = pd.DataFrame(report["clv_calculations"]["historical_clv"])
        predicted_df = pd.DataFrame(report["clv_calculations"]["predicted_clv"])
        estimated_df = pd.DataFrame(report["clv_calculations"]["estimated_clv"])
        
        report["summary"] = {
            "average_historical_clv": historical_df["clv_value"].mean() if len(historical_df) > 0 else 0,
            "average_predicted_clv": predicted_df["clv_value"].mean() if len(predicted_df) > 0 else 0,
            "average_estimated_clv": estimated_df["clv_value"].mean() if len(estimated_df) > 0 else 0
        }
        
        return report
