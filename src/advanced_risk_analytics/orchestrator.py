"""Orchestrator for advanced risk analytics."""

from typing import Dict, Any, List, Optional
import logging

import pandas as pd

from src.advanced_risk_analytics.base import RiskBase, RiskThresholds, RiskTrajectory, RiskLevel
from src.advanced_risk_analytics.trend_monitoring import RiskTrendMonitor
from src.advanced_risk_analytics.exposure_concentration import ExposureConcentrationAnalyzer
from src.advanced_risk_analytics.risk_adjusted_profitability import RiskAdjustedProfitability
from src.advanced_risk_analytics.early_warning import EarlyWarningIndicators
from src.advanced_risk_analytics.risk_migration import CustomerRiskMigration
from src.advanced_risk_analytics.portfolio_distribution import PortfolioRiskDistribution
from src.advanced_risk_analytics.transition_matrices import RiskTransitionMatrices
from src.advanced_risk_analytics.delinquency_buckets import DelinquencyBuckets
from src.advanced_risk_analytics.concentration_analysis import ConcentrationAnalyzer

logger = logging.getLogger(__name__)


class AdvancedRiskOrchestrator(RiskBase):
    """Orchestrates advanced risk analytics operations."""
    
    def __init__(self, thresholds: Optional[RiskThresholds] = None):
        """Initialize advanced risk orchestrator.
        
        Args:
            thresholds: Configurable risk thresholds
        """
        super().__init__(thresholds)
        
        # Initialize components
        self.trend_monitor = RiskTrendMonitor(thresholds)
        self.exposure_concentration = ExposureConcentrationAnalyzer(thresholds)
        self.risk_adjusted_profitability = RiskAdjustedProfitability(thresholds)
        self.early_warning = EarlyWarningIndicators(thresholds)
        self.risk_migration = CustomerRiskMigration(thresholds)
        self.portfolio_distribution = PortfolioRiskDistribution(thresholds)
        self.transition_matrices = RiskTransitionMatrices(thresholds)
        self.delinquency_buckets = DelinquencyBuckets(thresholds)
        self.concentration_analyzer = ConcentrationAnalyzer(thresholds)
    
    def generate_risk_report(
        self,
        df: pd.DataFrame,
        customer_column: str = "customer_key",
        exposure_column: str = "exposure_amount"
    ) -> Dict[str, Any]:
        """Generate comprehensive risk report.
        
        Args:
            df: DataFrame with customer data
            customer_column: Name of customer column
            exposure_column: Name of exposure column
        
        Returns:
            Dictionary with comprehensive risk report
        """
        logger.info("Generating comprehensive risk report")
        
        report = {
            "metadata": {
                "thresholds": self.thresholds.to_dict(),
                "total_customers": len(df[customer_column].unique())
            },
            "exposure_concentration": self.exposure_concentration.calculate_exposure_concentration(
                df, customer_column, exposure_column
            )
        }
        
        return report
