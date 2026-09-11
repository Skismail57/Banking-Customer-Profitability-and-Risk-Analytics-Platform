"""Configurable customer risk score for portfolio analytics."""

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, Any, List, Optional
import logging

import pandas as pd

from src.credit_risk_analytics.base import (
    CreditRiskBase,
    RiskIndicator,
    RiskBand,
    RiskIndicatorValue,
)

logger = logging.getLogger(__name__)


@dataclass
class RiskScoreWeight:
    """Weight configuration for risk score components."""
    
    indicator: RiskIndicator
    weight: float
    direction: str  # "higher_is_worse" or "higher_is_better"
    max_score: float = 100.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "indicator": self.indicator.value,
            "weight": self.weight,
            "direction": self.direction,
            "max_score": self.max_score
        }


class CustomerRiskScoreCalculator(CreditRiskBase):
    """Calculate configurable customer risk score for portfolio analytics."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize risk score calculator.
        
        Args:
            as_of_date: As-of date for temporal analysis
        
        Note:
            This is a portfolio analytics tool, not a real-world banking credit decision model.
        """
        super().__init__(as_of_date)
        self.weights = self._default_weights()
    
    def _default_weights(self) -> List[RiskScoreWeight]:
        """Default risk score weights.
        
        Returns:
            List of default weight configurations
        
        Note:
            These weights are for portfolio analytics only, not credit decision making.
        """
        return [
            RiskScoreWeight(
                indicator=RiskIndicator.DAYS_PAST_DUE,
                weight=0.25,
                direction="higher_is_worse",
                max_score=100.0
            ),
            RiskScoreWeight(
                indicator=RiskIndicator.CREDIT_UTILIZATION,
                weight=0.20,
                direction="higher_is_worse",
                max_score=100.0
            ),
            RiskScoreWeight(
                indicator=RiskIndicator.ON_TIME_PAYMENT_RATE,
                weight=0.20,
                direction="higher_is_better",
                max_score=100.0
            ),
            RiskScoreWeight(
                indicator=RiskIndicator.DELINQUENCY_STATUS,
                weight=0.15,
                direction="higher_is_worse",
                max_score=100.0
            ),
            RiskScoreWeight(
                indicator=RiskIndicator.DEBT_TO_INCOME,
                weight=0.10,
                direction="higher_is_worse",
                max_score=100.0
            ),
            RiskScoreWeight(
                indicator=RiskIndicator.DEFAULT_FLAG,
                weight=0.10,
                direction="higher_is_worse",
                max_score=100.0
            ),
        ]
    
    def normalize_indicator_value(
        self,
        indicator: RiskIndicator,
        value: float,
        direction: str,
        max_score: float = 100.0
    ) -> float:
        """Normalize indicator value to 0-100 scale.
        
        Args:
            indicator: Risk indicator
            value: Raw indicator value
            direction: Direction of risk ("higher_is_worse" or "higher_is_better")
            max_score: Maximum score
        
        Returns:
            Normalized score (0-100)
        
        Note:
            Simplified normalization for portfolio analytics.
        """
        # Indicator-specific normalization logic
        if indicator == RiskIndicator.DAYS_PAST_DUE:
            # 0 DPD = 0 score, 90+ DPD = 100 score
            normalized = min(value / 90.0 * 100, 100.0)
        elif indicator == RiskIndicator.CREDIT_UTILIZATION:
            # 0% utilization = 0 score, 100%+ utilization = 100 score
            normalized = min(value, 100.0)
        elif indicator == RiskIndicator.ON_TIME_PAYMENT_RATE:
            # 0% on-time = 0 raw, 100% on-time = 100 raw
            # higher_is_better direction will invert: 100% → 0 score (low risk), 0% → 100 score (high risk)
            normalized = min(max(value, 0.0), 100.0)
        elif indicator == RiskIndicator.DELINQUENCY_STATUS:
            # Current (0) = 0 score, 90+ DPD (4) = 100 score
            normalized = (value / 4.0) * 100.0
        elif indicator == RiskIndicator.DEBT_TO_INCOME:
            # 0% DTI = 0 score, 50%+ DTI = 100 score
            normalized = min(value / 50.0 * 100, 100.0)
        elif indicator == RiskIndicator.DEFAULT_FLAG:
            # No default = 0 score, Default = 100 score
            normalized = value * 100.0
        else:
            # Default normalization
            normalized = min(value, 100.0)
        
        # Apply direction
        if direction == "higher_is_better":
            normalized = 100.0 - normalized
        
        return max(0.0, min(normalized, max_score))
    
    def calculate_risk_score(
        self,
        indicator_values: Dict[RiskIndicator, RiskIndicatorValue]
    ) -> Dict[str, Any]:
        """Calculate customer risk score from indicator values.
        
        Args:
            indicator_values: Dictionary of indicator values
        
        Returns:
            Dictionary with risk score and components
        
        Note:
            This is for portfolio analytics only, not credit decision making.
        """
        total_weight = sum(w.weight for w in self.weights)
        weighted_score = 0.0
        components = []
        available_indicators = 0
        
        for weight_config in self.weights:
            indicator = weight_config.indicator
            
            if indicator in indicator_values and indicator_values[indicator].is_available:
                available_indicators += 1
                normalized = self.normalize_indicator_value(
                    indicator,
                    indicator_values[indicator].value,
                    weight_config.direction,
                    weight_config.max_score
                )
                component_score = normalized * weight_config.weight
                weighted_score += component_score
                
                components.append({
                    "indicator": indicator.value,
                    "value": indicator_values[indicator].value,
                    "normalized": normalized,
                    "weight": weight_config.weight,
                    "component_score": component_score,
                    "confidence": indicator_values[indicator].confidence
                })
            else:
                components.append({
                    "indicator": indicator.value,
                    "value": None,
                    "normalized": None,
                    "weight": weight_config.weight,
                    "component_score": 0.0,
                    "confidence": 0.0,
                    "missing": True
                })
        
        # Normalize by total weight
        if total_weight > 0:
            final_score = weighted_score / total_weight
        else:
            final_score = 0.0
        
        # Adjust confidence based on data availability
        data_completeness = available_indicators / len(self.weights)
        confidence = data_completeness * 0.9  # Max 0.9 confidence
        
        return {
            "risk_score": final_score,
            "data_completeness": data_completeness,
            "confidence": confidence,
            "available_indicators": available_indicators,
            "total_indicators": len(self.weights),
            "components": components,
            "disclaimer": "This risk score is for portfolio analytics only, not for real-world banking credit decisions."
        }
    
    def classify_risk_band(
        self,
        risk_score: float,
        custom_thresholds: Optional[Dict[str, float]] = None
    ) -> RiskBand:
        """Classify risk score into risk band.
        
        Args:
            risk_score: Risk score (0-100)
            custom_thresholds: Custom thresholds for bands
        
        Returns:
            Risk band classification
        """
        thresholds = custom_thresholds or {
            "critical": 75.0,
            "high": 50.0,
            "medium": 25.0,
            "low": 0.0
        }
        
        if risk_score >= thresholds["critical"]:
            return RiskBand.CRITICAL
        elif risk_score >= thresholds["high"]:
            return RiskBand.HIGH
        elif risk_score >= thresholds["medium"]:
            return RiskBand.MEDIUM
        else:
            return RiskBand.LOW
    
    def update_weights(self, weights: List[RiskScoreWeight]) -> None:
        """Update risk score weights.
        
        Args:
            weights: New list of weight configurations
        
        Note:
            Weights should sum to 1.0 for proper normalization.
        """
        total_weight = sum(w.weight for w in weights)
        if abs(total_weight - 1.0) > 0.01:
            logger.warning(f"Weights sum to {total_weight}, should sum to 1.0")
        
        self.weights = weights
        logger.info("Updated risk score weights")
