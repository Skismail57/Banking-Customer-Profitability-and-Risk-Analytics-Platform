"""Churn + CLV combination rules."""

from datetime import date
from typing import Dict, Any, List
import logging

from src.decision_intelligence.base import DecisionBase, Recommendation, Priority, ConfidenceLevel

logger = logging.getLogger(__name__)


class ChurnCLVRules(DecisionBase):
    """Rules combining churn probability and CLV."""
    
    def high_churn_high_clv(self, customer_data: Dict[str, Any]) -> Recommendation:
        """High churn probability + high CLV → retention intervention.
        
        Args:
            customer_data: Dictionary with customer metrics
        
        Returns:
            Recommendation
        """
        churn_probability = customer_data.get("churn_probability", 0)
        clv = customer_data.get("clv", 0)
        
        return Recommendation(
            customer_key=customer_data.get("customer_key"),
            segment=customer_data.get("segment"),
            triggering_metrics={
                "churn_probability": churn_probability,
                "clv": clv
            },
            reason="Customer has high churn probability and high lifetime value",
            recommended_action="Initiate immediate retention intervention with personalized offers",
            priority=Priority.CRITICAL,
            confidence=ConfidenceLevel.MEDIUM,
            limitations=[
                "Churn prediction model accuracy may vary",
                "CLV estimates based on assumptions",
                "Retention intervention success not guaranteed",
                "Customer may have already decided to leave"
            ],
            generated_at=date.today()
        )
    
    def high_churn_low_clv(self, customer_data: Dict[str, Any]) -> Recommendation:
        """High churn probability + low CLV → monitor or let churn.
        
        Args:
            customer_data: Dictionary with customer metrics
        
        Returns:
            Recommendation
        """
        churn_probability = customer_data.get("churn_probability", 0)
        clv = customer_data.get("clv", 0)
        
        return Recommendation(
            customer_key=customer_data.get("customer_key"),
            segment=customer_data.get("segment"),
            triggering_metrics={
                "churn_probability": churn_probability,
                "clv": clv
            },
            reason="Customer has high churn probability but low lifetime value",
            recommended_action="Monitor churn or consider allowing natural attrition",
            priority=Priority.LOW,
            confidence=ConfidenceLevel.HIGH,
            limitations=[
                "May miss opportunities for profitable retention",
                "Low CLV may be temporary",
                "Customer may become more valuable over time"
            ],
            generated_at=date.today()
        )
