"""Orchestrator for transaction analytics."""

from datetime import date
from typing import Dict, Any, List, Optional
import logging

import pandas as pd

from src.transaction_analytics.aggregation import TimeSeriesAggregator
from src.transaction_analytics.kpis import TransactionKPICalculator
from src.transaction_analytics.trends import TrendAnalyzer
from src.transaction_analytics.behavior import BehaviorAnalyzer
from src.transaction_analytics.anomaly import AnomalyDetector
from src.transaction_analytics.base import AggregationPeriod

logger = logging.getLogger(__name__)


class TransactionAnalyticsOrchestrator:
    """Orchestrates transaction analytics operations."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize transaction analytics orchestrator.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        self.as_of_date = as_of_date or date.today()
        
        # Initialize components
        self.aggregator = TimeSeriesAggregator(self.as_of_date)
        self.kpi_calculator = TransactionKPICalculator(self.as_of_date)
        self.trend_analyzer = TrendAnalyzer(self.as_of_date)
        self.behavior_analyzer = BehaviorAnalyzer(self.as_of_date)
        self.anomaly_detector = AnomalyDetector(self.as_of_date)
    
    def generate_comprehensive_report(
        self,
        df: pd.DataFrame,
        date_column: str = "transaction_date",
        amount_column: str = "amount",
        customer_column: str = "customer_key"
    ) -> Dict[str, Any]:
        """Generate comprehensive transaction analytics report.
        
        Args:
            df: DataFrame with transaction data
            date_column: Name of date column
            amount_column: Name of amount column
            customer_column: Name of customer column
        
        Returns:
            Dictionary with comprehensive analytics results
        """
        logger.info("Generating comprehensive transaction analytics report")
        
        report = {
            "metadata": {
                "as_of_date": self.as_of_date.isoformat(),
                "total_transactions": len(df),
                "date_range": self._get_date_range(df, date_column)
            },
            "overall_kpis": {},
            "time_series": {},
            "behavior": {},
            "trends": {},
            "anomalies": {}
        }
        
        # Overall KPIs
        report["overall_kpis"] = self.kpi_calculator.calculate_kpis(
            df, date_column, amount_column
        )
        
        # Time series aggregations
        report["time_series"]["daily"] = self._generate_time_series(
            df, date_column, amount_column, AggregationPeriod.DAILY
        )
        report["time_series"]["monthly"] = self._generate_time_series(
            df, date_column, amount_column, AggregationPeriod.MONTHLY
        )
        
        # Behavior analysis
        report["behavior"]["debit_credit"] = self.behavior_analyzer.analyze_debit_credit_behavior(
            df, date_column, amount_column
        )
        report["behavior"]["inflow_outflow"] = self.behavior_analyzer.analyze_inflow_outflow(
            df, date_column, amount_column
        )
        
        # Trend analysis
        monthly_agg = self._generate_time_series(df, date_column, amount_column, AggregationPeriod.MONTHLY)
        report["trends"]["monthly"] = self.trend_analyzer.calculate_trend_metrics(
            monthly_agg, "transaction_value"
        )
        report["trends"]["seasonality"] = self.trend_analyzer.detect_seasonality(
            monthly_agg, "transaction_value", "monthly"
        )
        
        # Anomaly detection
        report["anomalies"] = self.anomaly_detector.generate_anomaly_report(
            df, date_column, amount_column, customer_column
        )
        
        return report
    
    def _generate_time_series(
        self,
        df: pd.DataFrame,
        date_column: str,
        amount_column: str,
        period: AggregationPeriod
    ) -> pd.DataFrame:
        """Generate time series aggregation.
        
        Args:
            df: DataFrame with transaction data
            date_column: Name of date column
            amount_column: Name of amount column
            period: Aggregation period
        
        Returns:
            Aggregated DataFrame
        """
        return self.aggregator.aggregate(
            df=df,
            date_column=date_column,
            period=period,
            value_column=amount_column
        )
    
    def _get_date_range(
        self,
        df: pd.DataFrame,
        date_column: str
    ) -> Dict[str, str]:
        """Get date range of transaction data.
        
        Args:
            df: DataFrame with transaction data
            date_column: Name of date column
        
        Returns:
            Dictionary with min and max dates
        """
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])
        
        return {
            "min_date": df[date_column].min().isoformat(),
            "max_date": df[date_column].max().isoformat()
        }
    
    def generate_customer_level_report(
        self,
        df: pd.DataFrame,
        customer_key: int,
        date_column: str = "transaction_date",
        amount_column: str = "amount",
        customer_column: str = "customer_key"
    ) -> Dict[str, Any]:
        """Generate customer-specific transaction analytics report.
        
        Args:
            df: DataFrame with transaction data
            customer_key: Customer key to analyze
            date_column: Name of date column
            amount_column: Name of amount column
            customer_column: Name of customer column
        
        Returns:
            Dictionary with customer-specific analytics
        """
        logger.info(f"Generating report for customer {customer_key}")
        
        # Filter to customer
        customer_df = df[df[customer_column] == customer_key].copy()
        
        if len(customer_df) == 0:
            return {"error": f"No transactions found for customer {customer_key}"}
        
        report = {
            "customer_key": customer_key,
            "metadata": {
                "as_of_date": self.as_of_date.isoformat(),
                "transaction_count": len(customer_df)
            },
            "kpis": self.kpi_calculator.calculate_kpis(
                customer_df, date_column, amount_column
            ),
            "time_series": self._generate_time_series(
                customer_df, date_column, amount_column, AggregationPeriod.MONTHLY
            ),
            "behavior": self.behavior_analyzer.analyze_debit_credit_behavior(
                customer_df, date_column, amount_column
            )
        }
        
        return report
    
    def get_kpi_registry(self) -> Dict[str, Any]:
        """Get all registered KPI definitions.
        
        Returns:
            Dictionary of KPI definitions
        """
        return self.kpi_calculator.get_all_kpi_definitions()
