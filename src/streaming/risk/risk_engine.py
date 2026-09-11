"""Real-time risk scoring engine.

This module provides real-time risk scoring capabilities for the banking analytics
platform, adapting batch risk analytics for streaming event processing.

Assumptions:
- Risk scoring uses the same mathematical algorithms as batch (RiskBase)
- Features are retrieved from Redis feature store
- Risk scores are computed incrementally for efficiency

Limitations:
- Real-time risk scores may differ slightly from batch due to incremental feature updates
- Complex risk models (e.g., concentration risk) require historical context
- No support for time-series risk trajectory in streaming mode

Fairness Considerations:
- Risk thresholds should be calibrated per customer segment to avoid bias
- Consider demographic factors when setting risk thresholds
- Monitor risk score distribution across customer segments for fairness
"""

from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import logging
import uuid
from dataclasses import dataclass
import numpy as np

from src.streaming.config import StreamingConfig
from src.streaming.features.feature_store import FeatureStore
from src.advanced_risk_analytics.base import RiskBase, RiskLevel, RiskThresholds

logger = logging.getLogger(__name__)


@dataclass
class RiskEvent:
    """Result of real-time risk scoring."""
    risk_event_id: str
    event_id: str
    customer_key: str
    risk_type: str
    risk_level: str
    risk_score: float
    triggered_at: datetime
    threshold_violated: Optional[str] = None
    context_data: Optional[Dict[str, Any]] = None


class RealTimeRiskEngine:
    """Real-time risk scoring engine.
    
    This engine adapts the batch RiskBase for real-time streaming by:
    - Retrieving features from Redis feature store
    - Computing risk scores using batch algorithms
    - Determining risk levels based on thresholds
    - Generating risk events for downstream processing
    
    Key Features:
    - Reuses batch risk algorithms (RiskBase) for consistency
    - Retrieves streaming features from Redis
    - Supports multiple risk types (credit, payment, concentration)
    - Provides risk level classification
    """
    
    def __init__(
        self,
        config: StreamingConfig,
        feature_store: FeatureStore,
        risk_base: Optional[RiskBase] = None,
        thresholds: Optional[RiskThresholds] = None
    ):
        """Initialize real-time risk engine.
        
        Args:
            config: Streaming configuration
            feature_store: Redis feature store for feature retrieval
            risk_base: Batch risk base (for algorithm reuse)
            thresholds: Risk thresholds
        """
        self.config = config
        self.feature_store = feature_store
        self.risk_base = risk_base or RiskBase(thresholds)
        self.thresholds = thresholds or RiskThresholds()
    
    def compute_risk_score(
        self,
        event_id: str,
        customer_key: str,
        timestamp: datetime,
        risk_type: str = "credit"
    ) -> Optional[RiskEvent]:
        """Compute real-time risk score for an event.
        
        Args:
            event_id: Event identifier
            customer_key: Customer identifier
            timestamp: Event timestamp
            risk_type: Type of risk (credit, payment, concentration)
        
        Returns:
            RiskEvent if risk detected, None otherwise
        """
        logger.debug(f"Computing risk score for customer {customer_key}, type {risk_type}")
        
        # Retrieve streaming features from Redis
        features = self._get_customer_features(customer_key)
        
        if not features:
            logger.warning(f"No features found for customer {customer_key}")
            return None
        
        # Compute risk score based on risk type
        if risk_type == "credit":
            return self._compute_credit_risk(event_id, customer_key, timestamp, features)
        elif risk_type == "payment":
            return self._compute_payment_risk(event_id, customer_key, timestamp, features)
        elif risk_type == "concentration":
            return self._compute_concentration_risk(event_id, customer_key, timestamp, features)
        else:
            logger.warning(f"Unsupported risk type: {risk_type}")
            return None
    
    def _compute_credit_risk(
        self,
        event_id: str,
        customer_key: str,
        timestamp: datetime,
        features: Dict[str, Any]
    ) -> Optional[RiskEvent]:
        """Compute credit risk score.
        
        Args:
            event_id: Event identifier
            customer_key: Customer identifier
            timestamp: Event timestamp
            features: Customer features from Redis
        
        Returns:
            RiskEvent if risk detected, None otherwise
        """
        # Extract credit risk features
        utilization = features.get("credit_utilization", 0.0)
        dpd = features.get("days_overdue", 0)
        credit_score = features.get("credit_score", None)
        bti = features.get("balance_to_income_ratio", None)
        
        # Determine risk level using batch algorithm
        risk_level = self.risk_base.determine_risk_level(
            utilization=utilization,
            dpd=dpd,
            credit_score=credit_score,
            bti=bti
        )
        
        # Compute risk score (0-1)
        risk_score = self._compute_risk_score_from_level(risk_level)
        
        # Generate risk event if not low risk
        if risk_level != RiskLevel.LOW:
            threshold_violated = self._identify_violated_threshold(
                utilization, dpd, credit_score, bti
            )
            
            return RiskEvent(
                risk_event_id=str(uuid.uuid4()),
                event_id=event_id,
                customer_key=customer_key,
                risk_type="credit",
                risk_level=risk_level.value,
                risk_score=risk_score,
                triggered_at=datetime.now(timezone.utc).replace(tzinfo=None),
                threshold_violated=threshold_violated,
                context_data={
                    "utilization": utilization,
                    "dpd": dpd,
                    "credit_score": credit_score,
                    "bti": bti,
                    "features": features
                }
            )
        
        return None
    
    def _compute_payment_risk(
        self,
        event_id: str,
        customer_key: str,
        timestamp: datetime,
        features: Dict[str, Any]
    ) -> Optional[RiskEvent]:
        """Compute payment risk score.
        
        Args:
            event_id: Event identifier
            customer_key: Customer identifier
            timestamp: Event timestamp
            features: Customer features from Redis
        
        Returns:
            RiskEvent if risk detected, None otherwise
        """
        # Extract payment risk features
        dpd = features.get("days_overdue", 0)
        payment_history_score = features.get("payment_history_score", 1.0)
        
        # Compute payment risk score
        risk_score = 0.0
        
        # DPD contribution
        if dpd >= self.thresholds.dpd_critical_threshold:
            risk_score += 0.4
        elif dpd >= self.thresholds.dpd_high_threshold:
            risk_score += 0.3
        elif dpd >= self.thresholds.dpd_medium_threshold:
            risk_score += 0.2
        elif dpd > self.thresholds.dpd_low_threshold:
            risk_score += 0.1
        
        # Payment history contribution
        if payment_history_score < 0.5:
            risk_score += 0.4
        elif payment_history_score < 0.7:
            risk_score += 0.2
        elif payment_history_score < 0.9:
            risk_score += 0.1
        
        # Determine risk level
        if risk_score >= 0.7:
            risk_level = RiskLevel.CRITICAL
        elif risk_score >= 0.5:
            risk_level = RiskLevel.HIGH
        elif risk_score >= 0.3:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW
        
        # Generate risk event if not low risk
        if risk_level != RiskLevel.LOW:
            return RiskEvent(
                risk_event_id=str(uuid.uuid4()),
                event_id=event_id,
                customer_key=customer_key,
                risk_type="payment",
                risk_level=risk_level.value,
                risk_score=risk_score,
                triggered_at=datetime.now(timezone.utc).replace(tzinfo=None),
                threshold_violated=f"DPD {dpd} days, payment score {payment_history_score}",
                context_data={
                    "dpd": dpd,
                    "payment_history_score": payment_history_score,
                    "features": features
                }
            )
        
        return None
    
    def _compute_concentration_risk(
        self,
        event_id: str,
        customer_key: str,
        timestamp: datetime,
        features: Dict[str, Any]
    ) -> Optional[RiskEvent]:
        """Compute concentration risk score.
        
        Args:
            event_id: Event identifier
            customer_key: Customer identifier
            timestamp: Event timestamp
            features: Customer features from Redis
        
        Returns:
            RiskEvent if risk detected, None otherwise
        """
        # Extract concentration risk features
        total_exposure = features.get("total_exposure", 0.0)
        max_single_exposure = features.get("max_single_exposure", 0.0)
        
        # Compute concentration比率
        if total_exposure > 0:
            concentration_ratio = max_single_exposure / total_exposure
        else:
            concentration_ratio = 0.0
        
        # Compute risk score based on concentration
        if concentration_ratio >= self.thresholds.concentration_critical_threshold:
            risk_score = 1.0
            risk_level = RiskLevel.CRITICAL
        elif concentration_ratio >= self.thresholds.concentration_warning_threshold:
            risk_score = 0.7
            risk_level = RiskLevel.HIGH
        else:
            risk_score = 0.0
            risk_level = RiskLevel.LOW
        
        # Generate risk event if not low risk
        if risk_level != RiskLevel.LOW:
            return RiskEvent(
                risk_event_id=str(uuid.uuid4()),
                event_id=event_id,
                customer_key=customer_key,
                risk_type="concentration",
                risk_level=risk_level.value,
                risk_score=risk_score,
                triggered_at=datetime.now(timezone.utc).replace(tzinfo=None),
                threshold_violated=f"Concentration ratio {concentration_ratio:.2%} exceeds threshold",
                context_data={
                    "total_exposure": total_exposure,
                    "max_single_exposure": max_single_exposure,
                    "concentration_ratio": concentration_ratio,
                    "features": features
                }
            )
        
        return None
    
    def _get_customer_features(self, customer_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve customer features from Redis feature store.
        
        Args:
            customer_key: Customer identifier
        
        Returns:
            Dictionary of features or None if not found
        """
        try:
            # Use feature store adapter pattern
            feature_key = f"customer:{customer_key}:features"
            features_data = self.feature_store.redis_client.get(feature_key)
            
            if features_data:
                import json
                return json.loads(features_data)
            
            logger.warning(f"No features found for customer {customer_key}")
            return None
        
        except Exception as e:
            logger.error(f"Error retrieving features for customer {customer_key}: {e}")
            return None
    
    def _compute_risk_score_from_level(self, risk_level: RiskLevel) -> float:
        """Compute risk score from risk level.
        
        Args:
            risk_level: Risk level
        
        Returns:
            Risk score (0-1)
        """
        if risk_level == RiskLevel.CRITICAL:
            return 1.0
        elif risk_level == RiskLevel.HIGH:
            return 0.75
        elif risk_level == RiskLevel.MEDIUM:
            return 0.5
        else:
            return 0.25
    
    def _identify_violated_threshold(
        self,
        utilization: float,
        dpd: int,
        credit_score: Optional[int],
        bti: Optional[float]
    ) -> str:
        """Identify which threshold was violated.
        
        Args:
            utilization: Credit utilization
            dpd: Days past due
            credit_score: Credit score
            bti: Balance-to-income ratio
        
        Returns:
            Description of violated threshold
        """
        violations = []
        
        if utilization >= self.thresholds.utilization_high_threshold:
            violations.append(f"utilization {utilization:.2%}")
        if dpd >= self.thresholds.dpd_high_threshold:
            violations.append(f"DPD {dpd} days")
        if credit_score is not None and credit_score < self.thresholds.credit_score_high_threshold:
            violations.append(f"credit score {credit_score}")
        if bti is not None and bti >= self.thresholds.bti_high_threshold:
            violations.append(f"BTI {bti:.2%}")
        
        return ", ".join(violations) if violations else "multiple thresholds"
    
    def update_customer_risk_level(
        self,
        customer_key: str,
        risk_level: str,
        risk_score: float,
        timestamp: datetime
    ):
        """Update customer's real-time risk level in database.
        
        Args:
            customer_key: Customer identifier
            risk_level: Risk level
            risk_score: Risk score
            timestamp: Update timestamp
        """
        # This would update dim_customer table
        # Implementation depends on database access pattern
        logger.info(
            f"Updating customer {customer_key} risk level to {risk_level}, "
            f"score {risk_score}"
        )
        
        # Store in Redis for immediate access
        risk_key = f"customer:{customer_key}:risk"
        risk_data = {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "updated_at": timestamp.isoformat()
        }
        
        import json
        self.feature_store.redis_client.setex(
            risk_key,
            self.config.feature_store.ttl_seconds,
            json.dumps(risk_data)
        )


class RiskAggregator:
    """Aggregate risk scores across multiple dimensions.
    
    Combines risk scores from different risk types (credit, payment, concentration)
    into a comprehensive risk profile for each customer.
    """
    
    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        aggregation_method: str = "weighted_average"
    ):
        """Initialize risk aggregator.
        
        Args:
            weights: Weights for different risk types
            aggregation_method: Method for aggregation (weighted_average, max, sum)
        """
        self.weights = weights or {
            "credit": 0.5,
            "payment": 0.3,
            "concentration": 0.2
        }
        self.aggregation_method = aggregation_method
        self.risk_history = defaultdict(lambda: deque(maxlen=100))
    
    def aggregate_risk(
        self,
        customer_key: str,
        risk_events: List[RiskEvent]
    ) -> Dict[str, Any]:
        """Aggregate risk events into comprehensive risk profile.
        
        Args:
            customer_key: Customer identifier
            risk_events: List of risk events
        
        Returns:
            Aggregated risk profile
        """
        if not risk_events:
            return {
                "customer_key": customer_key,
                "overall_risk_score": 0.0,
                "overall_risk_level": "low",
                "risk_by_type": {},
                "timestamp": datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
            }
        
        # Extract risk scores by type
        risk_by_type = {}
        for event in risk_events:
            risk_type = event.risk_type
            if risk_type not in risk_by_type:
                risk_by_type[risk_type] = []
            risk_by_type[risk_type].append(event.risk_score)
        
        # Calculate average risk per type
        risk_scores_by_type = {}
        for risk_type, scores in risk_by_type.items():
            risk_scores_by_type[risk_type] = sum(scores) / len(scores)
        
        # Aggregate using specified method
        if self.aggregation_method == "weighted_average":
            overall_score = self._weighted_average(risk_scores_by_type)
        elif self.aggregation_method == "max":
            overall_score = max(risk_scores_by_type.values()) if risk_scores_by_type else 0.0
        elif self.aggregation_method == "sum":
            overall_score = sum(risk_scores_by_type.values()) / len(risk_scores_by_type) if risk_scores_by_type else 0.0
        else:
            overall_score = 0.0
        
        # Determine overall risk level
        overall_risk_level = self._score_to_level(overall_score)
        
        # Store in history
        self.risk_history[customer_key].append({
            "timestamp": datetime.now(timezone.utc).replace(tzinfo=None),
            "overall_score": overall_score,
            "risk_by_type": risk_scores_by_type
        })
        
        return {
            "customer_key": customer_key,
            "overall_risk_score": overall_score,
            "overall_risk_level": overall_risk_level,
            "risk_by_type": risk_scores_by_type,
            "risk_events_count": len(risk_events),
            "timestamp": datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
        }
    
    def _weighted_average(self, risk_scores: Dict[str, float]) -> float:
        """Calculate weighted average of risk scores.
        
        Args:
            risk_scores: Risk scores by type
        
        Returns:
            Weighted average
        """
        weighted_sum = 0.0
        total_weight = 0.0
        
        for risk_type, score in risk_scores.items():
            weight = self.weights.get(risk_type, 0.0)
            weighted_sum += score * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _score_to_level(self, score: float) -> str:
        """Convert risk score to risk level.
        
        Args:
            score: Risk score (0-1)
        
        Returns:
            Risk level string
        """
        if score >= 0.75:
            return "critical"
        elif score >= 0.5:
            return "high"
        elif score >= 0.25:
            return "medium"
        else:
            return "low"
    
    def get_risk_trend(
        self,
        customer_key: str,
        window_size: int = 10
    ) -> Dict[str, Any]:
        """Get risk trend for a customer.
        
        Args:
            customer_key: Customer identifier
            window_size: Number of historical points to consider
        
        Returns:
            Risk trend information
        """
        history = list(self.risk_history[customer_key])
        
        if len(history) < 2:
            return {
                "customer_key": customer_key,
                "trend": "insufficient_data",
                "current_score": history[0]["overall_score"] if history else 0.0,
                "change": 0.0,
                "direction": "none"
            }
        
        recent_history = history[-window_size:]
        scores = [h["overall_score"] for h in recent_history]
        
        current_score = scores[-1]
        previous_score = scores[0]
        change = current_score - previous_score
        
        if change > 0.1:
            trend = "increasing"
            direction = "up"
        elif change < -0.1:
            trend = "decreasing"
            direction = "down"
        else:
            trend = "stable"
            direction = "none"
        
        return {
            "customer_key": customer_key,
            "trend": trend,
            "current_score": current_score,
            "change": change,
            "direction": direction,
            "average_score": sum(scores) / len(scores),
            "min_score": min(scores),
            "max_score": max(scores)
        }


class DynamicRiskThresholds:
    """Dynamic risk threshold management.
    
    Adjusts risk thresholds based on market conditions and
    portfolio performance to maintain consistent risk levels.
    """
    
    def __init__(
        self,
        base_thresholds: Optional[RiskThresholds] = None,
        adjustment_factor: float = 0.1,
        adjustment_window_days: int = 30
    ):
        """Initialize dynamic risk thresholds.
        
        Args:
            base_thresholds: Base risk thresholds
            adjustment_factor: Maximum adjustment factor
            adjustment_window_days: Window for threshold adjustment
        """
        self.base_thresholds = base_thresholds or RiskThresholds()
        self.adjustment_factor = adjustment_factor
        self.adjustment_window_days = adjustment_window_days
        self.current_thresholds = self._copy_thresholds(self.base_thresholds)
        self.adjustment_history = []
    
    def _copy_thresholds(self, thresholds: RiskThresholds) -> RiskThresholds:
        """Create a copy of thresholds.
        
        Args:
            thresholds: Thresholds to copy
        
        Returns:
            Copied thresholds
        """
        return RiskThresholds(
            utilization_high_threshold=thresholds.utilization_high_threshold,
            dpd_high_threshold=thresholds.dpd_high_threshold,
            credit_score_high_threshold=thresholds.credit_score_high_threshold,
            bti_high_threshold=thresholds.bti_high_threshold,
            concentration_warning_threshold=thresholds.concentration_warning_threshold,
            concentration_critical_threshold=thresholds.concentration_critical_threshold
        )
    
    def adjust_thresholds(
        self,
        portfolio_performance: Dict[str, float],
        market_conditions: Dict[str, float]
    ) -> RiskThresholds:
        """Adjust thresholds based on performance and conditions.
        
        Args:
            portfolio_performance: Portfolio performance metrics
            market_conditions: Market condition indicators
        
        Returns:
            Adjusted thresholds
        """
        # Calculate adjustment factor based on inputs
        performance_factor = portfolio_performance.get("default_rate", 0.0)
        market_factor = market_conditions.get("volatility_index", 0.0)
        
        combined_factor = (performance_factor + market_factor) / 2
        
        # Clamp adjustment factor
        combined_factor = max(-self.adjustment_factor, min(self.adjustment_factor, combined_factor))
        
        # Apply adjustments
        self.current_thresholds.utilization_high_threshold *= (1 + combined_factor)
        self.current_thresholds.dpd_high_threshold *= (1 + combined_factor)
        self.current_thresholds.credit_score_high_threshold *= (1 - combined_factor)
        self.current_thresholds.bti_high_threshold *= (1 + combined_factor)
        
        # Record adjustment
        self.adjustment_history.append({
            "timestamp": datetime.now(timezone.utc).replace(tzinfo=None),
            "performance_factor": performance_factor,
            "market_factor": market_factor,
            "combined_factor": combined_factor,
            "thresholds": self._copy_thresholds(self.current_thresholds)
        })
        
        logger.info(
            f"Adjusted risk thresholds by {combined_factor:.2%} "
            f"(performance: {performance_factor:.2%}, market: {market_factor:.2%})"
        )
        
        return self.current_thresholds
    
    def reset_to_base(self):
        """Reset thresholds to base values."""
        self.current_thresholds = self._copy_thresholds(self.base_thresholds)
        logger.info("Reset risk thresholds to base values")
    
    def get_current_thresholds(self) -> RiskThresholds:
        """Get current thresholds.
        
        Returns:
            Current thresholds
        """
        return self.current_thresholds
    
    def get_adjustment_summary(self) -> Dict[str, Any]:
        """Get summary of threshold adjustments.
        
        Returns:
            Adjustment summary
        """
        if not self.adjustment_history:
            return {
                "total_adjustments": 0,
                "last_adjustment": None,
                "current_vs_base": self._compare_thresholds()
            }
        
        last_adjustment = self.adjustment_history[-1]
        
        return {
            "total_adjustments": len(self.adjustment_history),
            "last_adjustment": {
                "timestamp": last_adjustment["timestamp"].isoformat(),
                "combined_factor": last_adjustment["combined_factor"]
            },
            "current_vs_base": self._compare_thresholds()
        }
    
    def _compare_thresholds(self) -> Dict[str, float]:
        """Compare current thresholds to base.
        
        Returns:
            Dictionary of differences
        """
        return {
            "utilization_diff": (
                self.current_thresholds.utilization_high_threshold -
                self.base_thresholds.utilization_high_threshold
            ),
            "dpd_diff": (
                self.current_thresholds.dpd_high_threshold -
                self.base_thresholds.dpd_high_threshold
            ),
            "credit_score_diff": (
                self.current_thresholds.credit_score_high_threshold -
                self.base_thresholds.credit_score_high_threshold
            ),
            "bti_diff": (
                self.current_thresholds.bti_high_threshold -
                self.base_thresholds.bti_high_threshold
            )
        }
