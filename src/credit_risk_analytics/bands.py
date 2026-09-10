"""Risk band classification (Low, Medium, High, Critical)."""

from dataclasses import dataclass
from datetime import date
from typing import Dict, Any, Optional
import logging

from src.credit_risk_analytics.base import (
    CreditRiskBase,
    RiskBand,
)

logger = logging.getLogger(__name__)


@dataclass
class RiskBandThreshold:
    """Threshold configuration for risk band."""
    
    band: RiskBand
    min_score: float
    max_score: float
    description: str
    recommended_actions: list
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "band": self.band.value,
            "min_score": self.min_score,
            "max_score": self.max_score,
            "description": self.description,
            "recommended_actions": self.recommended_actions
        }


class RiskBandClassifier(CreditRiskBase):
    """Classify customers into risk bands."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize risk band classifier.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
        self.thresholds = self._default_thresholds()
    
    def _default_thresholds(self) -> list:
        """Default risk band thresholds.
        
        Returns:
            List of default threshold configurations
        
        Note:
            These thresholds are for portfolio analytics only.
        """
        return [
            RiskBandThreshold(
                band=RiskBand.LOW,
                min_score=0.0,
                max_score=25.0,
                description="Low risk profile with strong credit behavior",
                recommended_actions=["Monitor regularly", "Maintain relationship"]
            ),
            RiskBandThreshold(
                band=RiskBand.MEDIUM,
                min_score=25.0,
                max_score=50.0,
                description="Medium risk profile with acceptable credit behavior",
                recommended_actions=["Monitor closely", "Review periodically", "Consider risk mitigation"]
            ),
            RiskBandThreshold(
                band=RiskBand.HIGH,
                min_score=50.0,
                max_score=75.0,
                description="High risk profile with concerning credit behavior",
                recommended_actions=["Intensive monitoring", "Risk mitigation required", "Review exposure limits"]
            ),
            RiskBandThreshold(
                band=RiskBand.CRITICAL,
                min_score=75.0,
                max_score=100.0,
                description="Critical risk profile with severe credit concerns",
                recommended_actions=["Immediate action required", "Exposure reduction", "Enhanced monitoring", "Consider collection"]
            ),
        ]
    
    def classify(
        self,
        risk_score: float
    ) -> RiskBand:
        """Classify risk score into risk band.
        
        Args:
            risk_score: Risk score (0-100)
        
        Returns:
            Risk band classification
        """
        for threshold in self.thresholds:
            if threshold.min_score <= risk_score < threshold.max_score:
                return threshold.band
        
        # Handle edge case of score = 100
        if risk_score >= 100.0:
            return RiskBand.CRITICAL
        
        return RiskBand.LOW
    
    def classify_batch(
        self,
        risk_scores: list
    ) -> list:
        """Classify multiple risk scores into bands.
        
        Args:
            risk_scores: List of risk scores
        
        Returns:
            List of risk bands
        """
        return [self.classify(score) for score in risk_scores]
    
    def get_band_definition(self, band: RiskBand) -> Optional[RiskBandThreshold]:
        """Get band definition by band.
        
        Args:
            band: Risk band
        
        Returns:
            RiskBandThreshold if found, None otherwise
        """
        for threshold in self.thresholds:
            if threshold.band == band:
                return threshold
        return None
    
    def get_all_bands(self) -> list:
        """Get all band definitions.
        
        Returns:
            List of all band thresholds
        """
        return self.thresholds.copy()
    
    def update_thresholds(self, thresholds: list) -> None:
        """Update risk band thresholds.
        
        Args:
            thresholds: New list of threshold configurations
        """
        self.thresholds = thresholds
        logger.info("Updated risk band thresholds")
