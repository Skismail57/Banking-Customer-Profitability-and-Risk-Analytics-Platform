"""Segment-level recommendation rules."""

from typing import Dict, Any, List
import logging
from datetime import date

from src.decision_intelligence.base import DecisionBase, Recommendation, Priority, ConfidenceLevel

logger = logging.getLogger(__name__)


class SegmentRules(DecisionBase):
    """Rules for segment-level recommendations."""
    
    def segment_profitability_analysis(self, segment_data: Dict[str, Any]) -> Recommendation:
        """Segment profitability analysis recommendation.
        
        Args:
            segment_data: Dictionary with segment metrics
        
        Returns:
            Recommendation
        """
        segment = segment_data.get("segment", "unknown")
        avg_profitability = segment_data.get("avg_profitability", 0)
        customer_count = segment_data.get("customer_count", 0)
        
        return Recommendation(
            customer_key=None,
            segment=segment,
            triggering_metrics={
                "avg_profitability": avg_profitability,
                "customer_count": customer_count
            },
            reason=f"Segment {segment} profitability analysis",
            recommended_action="Review segment strategy based on profitability and customer base",
            priority=Priority.MEDIUM,
            confidence=ConfidenceLevel.MEDIUM,
            limitations=[
                "Segment averages may mask individual variation",
                "Segment definitions may change over time",
                "Recommendations may not apply to all customers in segment"
            ],
            generated_at=date.today()
        )
    
    def segment_risk_concentration(self, segment_data: Dict[str, Any]) -> Recommendation:
        """Segment risk concentration recommendation.
        
        Args:
            segment_data: Dictionary with segment metrics
        
        Returns:
            Recommendation
        """
        segment = segment_data.get("segment", "unknown")
        avg_risk_level = segment_data.get("avg_risk_level", "medium")
        exposure_concentration = segment_data.get("exposure_concentration", 0)
        
        return Recommendation(
            customer_key=None,
            segment=segment,
            triggering_metrics={
                "avg_risk_level": avg_risk_level,
                "exposure_concentration": exposure_concentration
            },
            reason=f"Segment {segment} has elevated risk and exposure concentration",
            recommended_action="Review risk management and exposure limits for segment",
            priority=Priority.HIGH if exposure_concentration > 0.2 else Priority.MEDIUM,
            confidence=ConfidenceLevel.MEDIUM,
            limitations=[
                "Risk concentration may be acceptable with proper mitigation",
                "Segment-level analysis may not capture individual risks",
                "Exposure concentration thresholds are configurable"
            ],
            generated_at=date.today()
        )
