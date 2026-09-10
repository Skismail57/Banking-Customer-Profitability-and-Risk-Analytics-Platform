"""Rules-based recommendation engine."""

from typing import Dict, Any, List, Callable
import logging
from datetime import date

import pandas as pd

from src.decision_intelligence.base import DecisionBase, Recommendation, Priority, ConfidenceLevel

logger = logging.getLogger(__name__)


class RulesEngine(DecisionBase):
    """Rules-based recommendation engine."""
    
    def __init__(self):
        """Initialize rules engine."""
        super().__init__()
        self.rules = []
    
    def register_rule(
        self,
        rule_name: str,
        condition: Callable[[Dict[str, Any]], bool],
        action_generator: Callable[[Dict[str, Any]], Dict[str, Any]]
    ):
        """Register a rule.
        
        Args:
            rule_name: Name of the rule
            condition: Function that returns True if rule should trigger
            action_generator: Function that generates recommendation details
        """
        self.rules.append({
            "name": rule_name,
            "condition": condition,
            "action_generator": action_generator
        })
    
    def evaluate_rules(
        self,
        customer_data: Dict[str, Any],
        customer_key: str = None
    ) -> List[Recommendation]:
        """Evaluate all rules against customer data.
        
        Args:
            customer_data: Dictionary with customer metrics
            customer_key: Customer identifier
        
        Returns:
            List of triggered recommendations
        """
        recommendations = []
        
        for rule in self.rules:
            try:
                if rule["condition"](customer_data):
                    action_details = rule["action_generator"](customer_data)
                    
                    recommendation = Recommendation(
                        customer_key=customer_key,
                        segment=customer_data.get("segment"),
                        triggering_metrics=action_details.get("triggering_metrics", {}),
                        reason=action_details["reason"],
                        recommended_action=action_details["recommended_action"],
                        priority=action_details.get("priority", Priority.MEDIUM),
                        confidence=action_details.get("confidence", ConfidenceLevel.MEDIUM),
                        limitations=action_details.get("limitations", []),
                        generated_at=date.today()
                    )
                    recommendations.append(recommendation)
            except Exception as e:
                logger.warning(f"Error evaluating rule {rule['name']}: {e}")
        
        return recommendations
