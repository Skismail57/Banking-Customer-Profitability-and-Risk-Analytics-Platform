"""Base classes for advanced risk analytics."""

from dataclasses import dataclass
from datetime import date
from typing import Dict, Any, List, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Customer risk levels in trajectory."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class RiskThresholds:
    """Configurable risk thresholds."""
    
    # Credit utilization thresholds
    utilization_low_threshold: float = 0.30
    utilization_medium_threshold: float = 0.60
    utilization_high_threshold: float = 0.85
    
    # Payment behavior thresholds (days past due)
    dpd_low_threshold: int = 0
    dpd_medium_threshold: int = 30
    dpd_high_threshold: int = 60
    dpd_critical_threshold: int = 90
    
    # Credit score thresholds
    credit_score_low_threshold: int = 700
    credit_score_medium_threshold: int = 600
    credit_score_high_threshold: int = 500
    
    # Balance-to-income ratio thresholds
    bti_low_threshold: float = 0.20
    bti_medium_threshold: float = 0.40
    bti_high_threshold: float = 0.60
    
    # Delinquency buckets (days past due)
    delinquency_current: int = 0
    delinquency_30_days: int = 30
    delinquency_60_days: int = 60
    delinquency_90_days: int = 90
    delinquency_120_days: int = 120
    
    # Concentration thresholds
    concentration_warning_threshold: float = 0.20  # 20% of exposure
    concentration_critical_threshold: float = 0.30  # 30% of exposure
    
    # Early warning thresholds
    utilization_increase_threshold: float = 0.15  # 15% increase
    payment_decline_threshold: float = 0.20  # 20% decline in on-time payment rate
    balance_increase_threshold: float = 0.25  # 25% increase in balance
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "utilization_low_threshold": self.utilization_low_threshold,
            "utilization_medium_threshold": self.utilization_medium_threshold,
            "utilization_high_threshold": self.utilization_high_threshold,
            "dpd_low_threshold": self.dpd_low_threshold,
            "dpd_medium_threshold": self.dpd_medium_threshold,
            "dpd_high_threshold": self.dpd_high_threshold,
            "dpd_critical_threshold": self.dpd_critical_threshold,
            "credit_score_low_threshold": self.credit_score_low_threshold,
            "credit_score_medium_threshold": self.credit_score_medium_threshold,
            "credit_score_high_threshold": self.credit_score_high_threshold,
            "bti_low_threshold": self.bti_low_threshold,
            "bti_medium_threshold": self.bti_medium_threshold,
            "bti_high_threshold": self.bti_high_threshold,
            "delinquency_current": self.delinquency_current,
            "delinquency_30_days": self.delinquency_30_days,
            "delinquency_60_days": self.delinquency_60_days,
            "delinquency_90_days": self.delinquency_90_days,
            "delinquency_120_days": self.delinquency_120_days,
            "concentration_warning_threshold": self.concentration_warning_threshold,
            "concentration_critical_threshold": self.concentration_critical_threshold,
            "utilization_increase_threshold": self.utilization_increase_threshold,
            "payment_decline_threshold": self.payment_decline_threshold,
            "balance_increase_threshold": self.balance_increase_threshold
        }


@dataclass
class RiskTrajectory:
    """Customer risk trajectory over time."""
    
    customer_key: str
    current_risk_level: RiskLevel
    risk_history: List[Dict[str, Any]]
    transitions: List[Dict[str, Any]]
    early_warning_signals: List[str]
    last_updated: date
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "customer_key": self.customer_key,
            "current_risk_level": self.current_risk_level.value,
            "risk_history": self.risk_history,
            "transitions": self.transitions,
            "early_warning_signals": self.early_warning_signals,
            "last_updated": self.last_updated.isoformat()
        }


class RiskBase:
    """Base class for advanced risk analytics."""
    
    def __init__(self, thresholds: Optional[RiskThresholds] = None):
        """Initialize risk base.
        
        Args:
            thresholds: Configurable risk thresholds
        """
        self.thresholds = thresholds or RiskThresholds()
    
    def determine_risk_level(
        self,
        utilization: float,
        dpd: int,
        credit_score: Optional[int] = None,
        bti: Optional[float] = None
    ) -> RiskLevel:
        """Determine risk level based on metrics.
        
        Args:
            utilization: Credit utilization ratio
            dpd: Days past due
            credit_score: Credit score (optional)
            bti: Balance-to-income ratio (optional)
        
        Returns:
            Risk level
        """
        risk_score = 0
        
        # Utilization contribution
        if utilization >= self.thresholds.utilization_high_threshold:
            risk_score += 3
        elif utilization >= self.thresholds.utilization_medium_threshold:
            risk_score += 2
        elif utilization >= self.thresholds.utilization_low_threshold:
            risk_score += 1
        
        # DPD contribution
        if dpd >= self.thresholds.dpd_critical_threshold:
            risk_score += 4
        elif dpd >= self.thresholds.dpd_high_threshold:
            risk_score += 3
        elif dpd >= self.thresholds.dpd_medium_threshold:
            risk_score += 2
        elif dpd > self.thresholds.dpd_low_threshold:
            risk_score += 1
        
        # Credit score contribution (if available)
        if credit_score is not None:
            if credit_score < self.thresholds.credit_score_high_threshold:
                risk_score += 3
            elif credit_score < self.thresholds.credit_score_medium_threshold:
                risk_score += 2
            elif credit_score < self.thresholds.credit_score_low_threshold:
                risk_score += 1
        
        # BTI contribution (if available)
        if bti is not None:
            if bti >= self.thresholds.bti_high_threshold:
                risk_score += 3
            elif bti >= self.thresholds.bti_medium_threshold:
                risk_score += 2
            elif bti >= self.thresholds.bti_low_threshold:
                risk_score += 1
        
        # Determine risk level based on score
        if risk_score >= 7:
            return RiskLevel.CRITICAL
        elif risk_score >= 5:
            return RiskLevel.HIGH
        elif risk_score >= 3:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
