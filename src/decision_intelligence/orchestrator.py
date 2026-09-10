"""Orchestrator for decision intelligence."""

from typing import Dict, Any, List
import logging

import pandas as pd

from src.decision_intelligence.base import DecisionBase, Recommendation
from src.decision_intelligence.profitability_risk_rules import ProfitabilityRiskRules
from src.decision_intelligence.churn_clv_rules import ChurnCLVRules
from src.decision_intelligence.risk_exposure_rules import RiskExposureRules
from src.decision_intelligence.segment_rules import SegmentRules

logger = logging.getLogger(__name__)


class DecisionIntelligenceOrchestrator(DecisionBase):
    """Orchestrates decision intelligence operations."""
    
    def __init__(self):
        """Initialize decision intelligence orchestrator."""
        super().__init__()
        
        # Initialize rule sets
        self.profitability_risk_rules = ProfitabilityRiskRules()
        self.churn_clv_rules = ChurnCLVRules()
        self.risk_exposure_rules = RiskExposureRules()
        self.segment_rules = SegmentRules()
    
    def generate_customer_recommendations(
        self,
        customer_data: Dict[str, Any]
    ) -> List[Recommendation]:
        """Generate recommendations for a single customer.
        
        Args:
            customer_data: Dictionary with customer metrics
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Profitability + Risk rules
        profitability = customer_data.get("net_profit", 0)
        risk_level = customer_data.get("risk_level", "medium")
        risk_trend = customer_data.get("risk_trend", "stable")
        
        if profitability > 5000 and risk_level == "low":
            recommendations.append(self.profitability_risk_rules.high_profitability_low_risk(customer_data))
        elif profitability > 5000 and risk_trend == "increasing":
            recommendations.append(self.profitability_risk_rules.high_profitability_rising_risk(customer_data))
        elif profitability < 1000 and risk_level == "low":
            recommendations.append(self.profitability_risk_rules.low_profitability_low_risk(customer_data))
        
        # Churn + CLV rules
        churn_probability = customer_data.get("churn_probability", 0)
        clv = customer_data.get("clv", 0)
        
        if churn_probability > 0.7 and clv > 10000:
            recommendations.append(self.churn_clv_rules.high_churn_high_clv(customer_data))
        elif churn_probability > 0.7 and clv < 2000:
            recommendations.append(self.churn_clv_rules.high_churn_low_clv(customer_data))
        
        # Risk + Exposure rules
        exposure = customer_data.get("exposure_amount", 0)
        
        if risk_level in ["high", "critical"] and exposure > 50000:
            recommendations.append(self.risk_exposure_rules.high_risk_high_exposure(customer_data))
        elif risk_level in ["high", "critical"] and exposure <= 50000:
            recommendations.append(self.risk_exposure_rules.high_risk_low_exposure(customer_data))
        
        return recommendations
    
    def generate_segment_recommendations(
        self,
        segment_data: Dict[str, Any]
    ) -> List[Recommendation]:
        """Generate recommendations for a segment.
        
        Args:
            segment_data: Dictionary with segment metrics
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Segment profitability analysis
        recommendations.append(self.segment_rules.segment_profitability_analysis(segment_data))
        
        # Segment risk concentration
        exposure_concentration = segment_data.get("exposure_concentration", 0)
        if exposure_concentration > 0.15:
            recommendations.append(self.segment_rules.segment_risk_concentration(segment_data))
        
        return recommendations
