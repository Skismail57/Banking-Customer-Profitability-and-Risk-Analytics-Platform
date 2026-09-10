"""Base classes for decision intelligence."""

from dataclasses import dataclass
from datetime import date
from typing import Dict, Any, List, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Priority(Enum):
    """Priority levels for recommendations."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ConfidenceLevel(Enum):
    """Confidence levels for recommendations."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Recommendation:
    """Business action recommendation."""
    
    customer_key: Optional[str]  # None for segment-level recommendations
    segment: Optional[str]  # None for customer-level recommendations
    triggering_metrics: Dict[str, Any]
    reason: str
    recommended_action: str
    priority: Priority
    confidence: ConfidenceLevel
    limitations: List[str]
    generated_at: date
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "customer_key": self.customer_key,
            "segment": self.segment,
            "triggering_metrics": self.triggering_metrics,
            "reason": self.reason,
            "recommended_action": self.recommended_action,
            "priority": self.priority.value,
            "confidence": self.confidence.value,
            "limitations": self.limitations,
            "generated_at": self.generated_at.isoformat(),
            "disclaimer": "This is an analytical decision-support recommendation, not a banking decision."
        }


class DecisionBase:
    """Base class for decision intelligence."""
    
    def __init__(self):
        """Initialize decision base."""
        pass
    
    def calculate_priority(
        self,
        risk_level: str,
        exposure_amount: float,
        profitability: float,
        churn_probability: Optional[float] = None
    ) -> Priority:
        """Calculate priority based on metrics.
        
        Args:
            risk_level: Risk level (low, medium, high, critical)
            exposure_amount: Exposure amount
            profitability: Profitability value
            churn_probability: Churn probability (optional)
        
        Returns:
            Priority level
        """
        score = 0
        
        # Risk contribution
        if risk_level == "critical":
            score += 4
        elif risk_level == "high":
            score += 3
        elif risk_level == "medium":
            score += 2
        elif risk_level == "low":
            score += 1
        
        # Exposure contribution
        if exposure_amount > 100000:  # High exposure
            score += 3
        elif exposure_amount > 50000:  # Medium exposure
            score += 2
        elif exposure_amount > 10000:  # Low exposure
            score += 1
        
        # Profitability contribution (inverse - high profitability reduces priority)
        if profitability < 0:  # Negative profitability
            score += 3
        elif profitability < 1000:  # Low profitability
            score += 2
        elif profitability < 5000:  # Medium profitability
            score += 1
        
        # Churn contribution
        if churn_probability is not None:
            if churn_probability > 0.7:  # High churn risk
                score += 3
            elif churn_probability > 0.5:  # Medium churn risk
                score += 2
            elif churn_probability > 0.3:  # Low churn risk
                score += 1
        
        # Determine priority
        if score >= 8:
            return Priority.CRITICAL
        elif score >= 6:
            return Priority.HIGH
        elif score >= 4:
            return Priority.MEDIUM
        else:
            return Priority.LOW
    
    def calculate_confidence(
        self,
        data_quality: str = "high",
        model_accuracy: Optional[float] = None,
        rule_complexity: str = "simple"
    ) -> ConfidenceLevel:
        """Calculate confidence level.
        
        Args:
            data_quality: Data quality (high, medium, low)
            model_accuracy: Model accuracy (optional)
            rule_complexity: Rule complexity (simple, complex)
        
        Returns:
            Confidence level
        """
        score = 0
        
        # Data quality contribution
        if data_quality == "high":
            score += 2
        elif data_quality == "medium":
            score += 1
        
        # Model accuracy contribution
        if model_accuracy is not None:
            if model_accuracy > 0.85:
                score += 2
            elif model_accuracy > 0.75:
                score += 1
        
        # Rule complexity contribution (simple rules have higher confidence)
        if rule_complexity == "simple":
            score += 1
        
        # Determine confidence
        if score >= 4:
            return ConfidenceLevel.HIGH
        elif score >= 2:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW
