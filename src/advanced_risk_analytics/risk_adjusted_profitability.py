"""Risk-adjusted profitability calculation."""

from typing import Dict, Any, List, Optional
import logging

import pandas as pd
import numpy as np

from src.advanced_risk_analytics.base import RiskBase, RiskLevel

logger = logging.getLogger(__name__)


class RiskAdjustedProfitability(RiskBase):
    """Calculate risk-adjusted profitability."""
    
    def calculate_risk_adjusted_profitability(
        self,
        df: pd.DataFrame,
        profitability_column: str = "net_profit",
        risk_column: str = "risk_level",
        risk_adjustment_factors: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """Calculate risk-adjusted profitability.
        
        Args:
            df: DataFrame with profitability and risk data
            profitability_column: Name of profitability column
            risk_column: Name of risk level column
            risk_adjustment_factors: Risk adjustment factors per risk level
        
        Returns:
            Dictionary with risk-adjusted profitability analysis
        """
        if risk_adjustment_factors is None:
            risk_adjustment_factors = {
                "low": 1.0,      # No adjustment
                "medium": 0.9,    # 10% reduction
                "high": 0.7,      # 30% reduction
                "critical": 0.5    # 50% reduction
            }
        
        df = df.copy()
        
        # Apply risk adjustment
        df["risk_adjustment_factor"] = df[risk_column].map(risk_adjustment_factors)
        df["risk_adjusted_profit"] = df[profitability_column] * df["risk_adjustment_factor"]
        
        # Calculate summary statistics
        total_profit = df[profitability_column].sum()
        total_risk_adjusted_profit = df["risk_adjusted_profit"].sum()
        risk_adjustment = (total_risk_adjusted_profit / total_profit) if total_profit != 0 else 0
        
        # Calculate by risk level
        by_risk = df.groupby(risk_column).agg({
            profitability_column: "sum",
            "risk_adjusted_profit": "sum"
        }).to_dict()
        
        return {
            "total_profit": total_profit,
            "total_risk_adjusted_profit": total_risk_adjusted_profit,
            "risk_adjustment_factor": risk_adjustment,
            "risk_adjustment_factors": risk_adjustment_factors,
            "profitability_by_risk": by_risk
        }
