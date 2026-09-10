"""Risk trend monitoring."""

from typing import Dict, Any, List
import logging

import pandas as pd
import numpy as np

from src.advanced_risk_analytics.base import RiskBase, RiskLevel

logger = logging.getLogger(__name__)


class RiskTrendMonitor(RiskBase):
    """Monitor risk trends over time."""
    
    def calculate_risk_trend(
        self,
        df: pd.DataFrame,
        customer_column: str = "customer_key",
        date_column: str = "as_of_date",
        utilization_column: str = "credit_utilization",
        dpd_column: str = "days_past_due",
        credit_score_column: Optional[str] = None
    ) -> Dict[str, Any]:
        """Calculate risk trend for a customer over time.
        
        Args:
            df: DataFrame with customer risk data
            customer_column: Name of customer column
            date_column: Name of date column
            utilization_column: Name of utilization column
            dpd_column: Name of DPD column
            credit_score_column: Name of credit score column (optional)
        
        Returns:
            Dictionary with risk trend analysis
        """
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])
        df = df.sort_values(date_column)
        
        # Calculate risk level for each period
        risk_levels = []
        for _, row in df.iterrows():
            risk_level = self.determine_risk_level(
                utilization=row[utilization_column],
                dpd=row[dpd_column],
                credit_score=row.get(credit_score_column) if credit_score_column else None
            )
            risk_levels.append(risk_level.value)
        
        df["risk_level"] = risk_levels
        
        # Calculate trend direction
        if len(df) >= 2:
            first_risk = df["risk_level"].iloc[0]
            last_risk = df["risk_level"].iloc[-1]
            
            risk_order = {"low": 0, "medium": 1, "high": 2, "critical": 3}
            trend_direction = "increasing" if risk_order[last_risk] > risk_order[first_risk] else "decreasing" if risk_order[last_risk] < risk_order[first_risk] else "stable"
        else:
            trend_direction = "insufficient_data"
        
        # Calculate risk level changes
        transitions = []
        for i in range(1, len(df)):
            if df["risk_level"].iloc[i] != df["risk_level"].iloc[i-1]:
                transitions.append({
                    "from": df["risk_level"].iloc[i-1],
                    "to": df["risk_level"].iloc[i],
                    "date": df[date_column].iloc[i].isoformat()
                })
        
        return {
            "current_risk_level": df["risk_level"].iloc[-1] if len(df) > 0 else None,
            "risk_history": df[["risk_level", date_column]].to_dict("records"),
            "trend_direction": trend_direction,
            "transitions": transitions,
            "period_count": len(df)
        }
