"""Risk + exposure combination rules."""

from typing import Dict, Any, List
import logging

from src.decision_intelligence.base import DecisionBase, Recommendation, Priority, ConfidenceLevel

logger = logging.getLogger(__name__)


class RiskExposureRules(DecisionBase):
    """Rules combining risk level and exposure."""
    
    def high_risk_high_exposure(self, customer_data: Dict[str, Any]) -> Recommendation:
        """High risk + high exposure → early-warning review.
        
        Args:
            customer_data: Dictionary with customer metrics
        
        Returns:
            Recommendation
        """
        risk_level = customer_data.get("risk_level", "medium")
        exposure = customer_data.get("exposure_amount", 0)
        
        return Recommendation(
            customer_key=customer_data.get("customer_key"),
            segment=customer_data.get("segment"),
            triggering_metrics={
                "risk_level": risk_level,
                "exposure_amount": exposure
            },
            reason="Customer has high risk level and high exposure",
            recommended_action="Initiate early-warning review and risk mitigation measures",
            priority=Priority.CRITICAL,
            confidence=ConfidenceLevel.HIGH,
            limitations=[
                "Exposure may not reflect actual loss given default",
                "Risk level based on current snapshot",
                "May require additional credit review"
            ],
            generated_at=date.today()
        )
    
    def high_risk_low_exposure(self, customer_data: Dict[str, Any]) -> Recommendation:
        """High risk + low exposure → monitor and limit exposure.
        
        Args:
            customer_data: Dictionary with customer metrics
        
        Returns:
            Recommendation
        """
        risk_level = customer_data.get("risk_level", "medium")
        exposure = customer_data.get("exposure_amount", 0)
        
        return Recommendation(
            customer_key=customer_data.get("customer_key"),
            segment=customer_data.get("segment"),
            triggering_metrics={
                "risk_level": risk_level,
                "exposure_amount": exposure
            },
            reason="Customer has high risk level but low exposure",
            recommended_action="Monitor risk and limit additional exposure",
            priority=Priority.MEDIUM,
            confidence=ConfidenceLevel.HIGH,
            limitations=[
                "Low exposure may increase over time",
                "Risk may improve with intervention"
            ],
            generated_at=date.today()
        )
