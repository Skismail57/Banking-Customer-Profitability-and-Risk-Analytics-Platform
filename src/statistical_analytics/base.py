"""Base classes for statistical analytics."""

from dataclasses import dataclass
from datetime import date
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Result of a statistical test."""
    
    test_name: str
    null_hypothesis: str
    alternative_hypothesis: str
    assumptions: List[str]
    test_statistic: float
    p_value: float
    confidence_interval: Optional[tuple] = None
    effect_size: Optional[float] = None
    effect_size_type: Optional[str] = None
    business_interpretation: str = ""
    additional_info: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "test_name": self.test_name,
            "null_hypothesis": self.null_hypothesis,
            "alternative_hypothesis": self.alternative_hypothesis,
            "assumptions": self.assumptions,
            "test_statistic": self.test_statistic,
            "p_value": self.p_value,
            "confidence_interval": self.confidence_interval,
            "effect_size": self.effect_size,
            "effect_size_type": self.effect_size_type,
            "business_interpretation": self.business_interpretation,
            "additional_info": self.additional_info or {}
        }


class StatisticalBase:
    """Base class for statistical analytics."""
    
    def __init__(self, alpha: float = 0.05):
        """Initialize statistical base.
        
        Args:
            alpha: Significance level (default 0.05)
        """
        self.alpha = alpha
    
    def interpret_p_value(self, p_value: float) -> str:
        """Interpret p-value beyond just significance.
        
        Args:
            p_value: P-value from test
        
        Returns:
            Interpretation string
        """
        if p_value < 0.001:
            return "Very strong evidence against null hypothesis"
        elif p_value < 0.01:
            return "Strong evidence against null hypothesis"
        elif p_value < self.alpha:
            return "Moderate evidence against null hypothesis"
        elif p_value < 0.10:
            return "Weak evidence against null hypothesis"
        else:
            return "Insufficient evidence to reject null hypothesis"
    
    def interpret_effect_size(self, effect_size: float, effect_type: str) -> str:
        """Interpret effect size.
        
        Args:
            effect_size: Effect size value
            effect_type: Type of effect size (cohens_d, eta_squared, etc.)
        
        Returns:
            Interpretation string
        """
        if effect_type == "cohens_d":
            if abs(effect_size) < 0.2:
                return "Small effect"
            elif abs(effect_size) < 0.5:
                return "Medium effect"
            elif abs(effect_size) < 0.8:
                return "Large effect"
            else:
                return "Very large effect"
        elif effect_type == "eta_squared":
            if effect_size < 0.01:
                return "Small effect"
            elif effect_size < 0.06:
                return "Medium effect"
            elif effect_size < 0.14:
                return "Large effect"
            else:
                return "Very large effect"
        elif effect_type == "phi":
            if abs(effect_size) < 0.10:
                return "Small effect"
            elif abs(effect_size) < 0.30:
                return "Medium effect"
            elif abs(effect_size) < 0.50:
                return "Large effect"
            else:
                return "Very large effect"
        else:
            return f"Effect size: {effect_size:.4f}"
