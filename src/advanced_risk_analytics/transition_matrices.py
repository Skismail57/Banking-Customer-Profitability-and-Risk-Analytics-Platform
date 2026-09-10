"""Risk transition matrices."""

from typing import Dict, Any, List
import logging

import pandas as pd

from src.advanced_risk_analytics.base import RiskBase, RiskLevel

logger = logging.getLogger(__name__)


class RiskTransitionMatrices(RiskBase):
    """Calculate risk transition matrices."""
    
    def calculate_transition_matrix(
        self,
        df: pd.DataFrame,
        customer_column: str = "customer_key",
        period_column: str = "period",
        utilization_column: str = "credit_utilization",
        dpd_column: str = "days_past_due"
    ) -> Dict[str, Any]:
        """Calculate risk transition matrix across periods.
        
        Args:
            df: DataFrame with customer data over multiple periods
            customer_column: Name of customer column
            period_column: Name of period column
            utilization_column: Name of utilization column
            dpd_column: Name of DPD column
        
        Returns:
            Dictionary with transition matrix
        """
        # Calculate risk level for each customer-period
        risk_levels = []
        for _, row in df.iterrows():
            risk_level = self.determine_risk_level(
                utilization=row[utilization_column],
                dpd=row[dpd_column]
            )
            risk_levels.append(risk_level.value)
        
        df["risk_level"] = risk_levels
        
        # Create transition matrix
        risk_order = ["low", "medium", "high", "critical"]
        transition_matrix = pd.DataFrame(0, index=risk_order, columns=risk_order)
        
        # Count transitions
        for customer in df[customer_column].unique():
            customer_df = df[df[customer_column] == customer].sort_values(period_column)
            for i in range(1, len(customer_df)):
                from_risk = customer_df["risk_level"].iloc[i-1]
                to_risk = customer_df["risk_level"].iloc[i]
                if from_risk in risk_order and to_risk in risk_order:
                    transition_matrix.loc[from_risk, to_risk] += 1
        
        # Normalize to probabilities
        transition_matrix_norm = transition_matrix.div(transition_matrix.sum(axis=1), axis=0)
        
        return {
            "transition_counts": transition_matrix.to_dict(),
            "transition_probabilities": transition_matrix_norm.to_dict(),
            "risk_levels": risk_order
        }
