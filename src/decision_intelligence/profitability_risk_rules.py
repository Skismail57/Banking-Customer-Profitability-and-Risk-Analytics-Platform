"""Profitability + risk combination rules."""

from typing import Dict, Any, List
import logging
from datetime import date

from src.decision_intelligence.base import DecisionBase, Recommendation, Priority, ConfidenceLevel

logger = logging.getLogger(__name__)


class ProfitabilityRiskRules(DecisionBase):
    """Rules combining profitability and risk metrics."""
    
    def high_profitability_low_risk(self, customer_data: Dict[str, Any]) -> Recommendation:
        """High profitability + low risk → retention / premium product opportunity.
        
        Args:
            customer_data: Dictionary with customer metrics
        
        Returns:
            Recommendation
        """
        profitability = customer_data.get("net_profit", 0)
        risk_level = customer_data.get("risk_level", "medium")
        
        return Recommendation(
            customer_key=customer_data.get("customer_key"),
            segment=customer_data.get("segment"),
            triggering_metrics={
                "net_profit": profitability,
                "risk_level": risk_level
            },
            reason="Customer has high profitability and low risk profile",
            recommended_action="Prioritize retention and offer premium product opportunities",
            priority=Priority.HIGH,
            confidence=ConfidenceLevel.HIGH,
            limitations=[
                "Based on current snapshot, may not capture future behavior",
                "Risk level may change over time",
                "Profitability may be influenced by one-time events"
            ],
            generated_at=date.today()
        )
    
    def high_profitability_rising_risk(self, customer_data: Dict[str, Any]) -> Recommendation:
        """High profitability + rising risk → risk monitoring / relationship review.
        
        Args:
            customer_data: Dictionary with customer metrics
        
        Returns:
            Recommendation
        """
        profitability = customer_data.get("net_profit", 0)
        risk_level = customer_data.get("risk_level", "medium")
        risk_trend = customer_data.get("risk_trend", "stable")
        
        return Recommendation(
            customer_key=customer_data.get("customer_key"),
            segment=customer_data.get("segment"),
            triggering_metrics={
                "net_profit": profitability,
                "risk_level": risk_level,
                "risk_trend": risk_trend
            },
            reason="Customer has high profitability but risk is increasing",
            recommended_action="Initiate enhanced risk monitoring and relationship review",
            priority=Priority.HIGH,
            confidence=ConfidenceLevel.MEDIUM,
            limitations=[
                "Risk trend based on limited historical data",
                "May not capture sudden risk events",
                "Profitability may mask underlying risk"
            ],
            generated_at=date.today()
        )
    
    def low_profitability_low_risk(self, customer_data: Dict[str, Any]) -> Recommendation:
        """Low profitability + low risk → cost-efficient servicing / targeted cross-sell.
        
        Args:
            customer_data: Dictionary with customer metrics
        
        Returns:
            Recommendation
        """
        profitability = customer_data.get("net_profit", 0)
        risk_level = customer_data.get("risk_level", "medium")
        
        return Recommendation(
            customer_key=customer_data.get("customer_key"),
            segment=customer_data.get("segment"),
            triggering_metrics={
                "net_profit": profitability,
                "risk_level": risk_level
            },
            reason="Customer has low profitability but low risk profile",
            recommended_action="Provide cost-efficient servicing and targeted cross-sell opportunities",
            priority=Priority.MEDIUM,
            confidence=ConfidenceLevel.HIGH,
            limitations=[
                "Low profitability may be temporary",
                "Cross-sell success depends on customer needs",
                "Cost-efficient servicing may affect customer experience"
            ],
            generated_at=date.today()
        )
