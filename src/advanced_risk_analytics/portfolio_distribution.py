"""Portfolio risk distribution."""

from typing import Dict, Any, List
import logging

import pandas as pd

from src.advanced_risk_analytics.base import RiskBase, RiskLevel

logger = logging.getLogger(__name__)


class PortfolioRiskDistribution(RiskBase):
    """Analyze portfolio risk distribution."""
    
    def calculate_portfolio_distribution(
        self,
        df: pd.DataFrame,
        customer_column: str = "customer_key",
        utilization_column: str = "credit_utilization",
        dpd_column: str = "days_past_due",
        exposure_column: str = "exposure_amount"
    ) -> Dict[str, Any]:
        """Calculate portfolio risk distribution.
        
        Args:
            df: DataFrame with customer data
            customer_column: Name of customer column
            utilization_column: Name of utilization column
            dpd_column: Name of DPD column
            exposure_column: Name of exposure column
        
        Returns:
            Dictionary with portfolio distribution
        """
        # Calculate risk level for each customer
        risk_levels = []
        for _, row in df.iterrows():
            risk_level = self.determine_risk_level(
                utilization=row[utilization_column],
                dpd=row[dpd_column]
            )
            risk_levels.append(risk_level.value)
        
        df["risk_level"] = risk_levels
        
        # Calculate distribution by risk level
        distribution = df.groupby("risk_level").agg({
            customer_column: "count",
            exposure_column: "sum"
        }).rename(columns={customer_column: "customer_count"})
        
        distribution["customer_pct"] = distribution["customer_count"] / len(df)
        distribution["exposure_pct"] = distribution[exposure_column] / df[exposure_column].sum()
        
        return {
            "distribution": distribution.to_dict("index"),
            "total_customers": len(df),
            "total_exposure": df[exposure_column].sum()
        }
