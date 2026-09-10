"""Exposure concentration analysis."""

from typing import Dict, Any, List
import logging

import pandas as pd
import numpy as np

from src.advanced_risk_analytics.base import RiskBase

logger = logging.getLogger(__name__)


class ExposureConcentrationAnalyzer(RiskBase):
    """Analyze exposure concentration across customers and segments."""
    
    def calculate_exposure_concentration(
        self,
        df: pd.DataFrame,
        customer_column: str = "customer_key",
        exposure_column: str = "exposure_amount"
    ) -> Dict[str, Any]:
        """Calculate exposure concentration metrics.
        
        Args:
            df: DataFrame with exposure data
            customer_column: Name of customer column
            exposure_column: Name of exposure column
        
        Returns:
            Dictionary with concentration analysis
        """
        total_exposure = df[exposure_column].sum()
        
        # Calculate concentration for each customer
        df["exposure_pct"] = df[exposure_column] / total_exposure
        
        # Identify concentrated customers
        warning_customers = df[df["exposure_pct"] >= self.thresholds.concentration_warning_threshold]
        critical_customers = df[df["exposure_pct"] >= self.thresholds.concentration_critical_threshold]
        
        # Calculate Herfindahl-Hirschman Index (HHI)
        hhi = (df["exposure_pct"] ** 2).sum()
        
        # Calculate Gini coefficient
        sorted_exposure = df[exposure_column].sort_values().values
        n = len(sorted_exposure)
        cumsum = np.cumsum(sorted_exposure)
        gini = (n + 1 - 2 * np.sum(cumsum) / cumsum[-1]) / n if cumsum[-1] > 0 else 0
        
        return {
            "total_exposure": total_exposure,
            "warning_customers_count": len(warning_customers),
            "warning_customers_exposure_pct": warning_customers["exposure_pct"].sum(),
            "critical_customers_count": len(critical_customers),
            "critical_customers_exposure_pct": critical_customers["exposure_pct"].sum(),
            "hhi": hhi,
            "gini_coefficient": gini,
            "top_10_customers_exposure_pct": df.nlargest(10, exposure_column)[exposure_column].sum() / total_exposure if total_exposure > 0 else 0,
            "top_20_customers_exposure_pct": df.nlargest(20, exposure_column)[exposure_column].sum() / total_exposure if total_exposure > 0 else 0
        }
