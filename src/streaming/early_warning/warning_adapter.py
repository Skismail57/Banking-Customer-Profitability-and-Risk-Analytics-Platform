"""Streaming early warning adapter.

This module adapts the batch early warning indicators for real-time streaming
event processing. It maintains streaming state and provides single-event
warning detection capabilities.

Assumptions:
- Streaming state is maintained in Redis for persistence
- Warning detection uses the same mathematical algorithms as batch
- State is updated incrementally for efficiency

Limitations:
- Streaming warning scores may differ slightly from batch due to incremental updates
- Trend analysis requires historical context (limited in streaming mode)
- Some warning signals require time-series analysis (not suitable for single-event)

Fairness Considerations:
- Warning thresholds should be calibrated per customer segment to avoid bias
- Consider demographic factors when setting warning thresholds
- Monitor warning rates across customer segments for fairness
"""

from collections import defaultdict, deque
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List, Tuple
import logging
import uuid
from dataclasses import dataclass
import numpy as np

from src.streaming.config import StreamingConfig
from src.streaming.features.feature_store import FeatureStore
from src.advanced_risk_analytics.early_warning import EarlyWarningIndicators, WarningSeverity

logger = logging.getLogger(__name__)


@dataclass
class WarningSignal:
    """Result of streaming early warning detection."""
    warning_id: str
    event_id: str
    customer_key: str
    signal_type: str
    warning_level: str
    warning_score: float
    detected_at: datetime
    context_data: Dict[str, Any]
    threshold_violated: Optional[str] = None


class StreamingWarningAdapter:
    """Adapter for streaming early warning detection.
    
    This adapter adapts the batch EarlyWarningIndicators for real-time streaming
    by maintaining streaming state and providing single-event warning detection.
    
    Key Features:
    - Reuses batch warning algorithms for consistency
    - Maintains streaming state in Redis
    - Supports utilization, payment, balance, and risk score warnings
    - Provides severity classification based on score thresholds
    - Generates watchlist updates
    """
    
    # Warning thresholds (configurable)
    THRESHOLDS = {
        'utilization_increase_threshold': 0.15,  # 15% increase
        'payment_decline_threshold': 0.10,  # 10% decline
        'balance_increase_threshold': 0.20,  # 20% increase
        'risk_score_decline_threshold': 0.10,  # 10% decline
    }
    
    def __init__(
        self,
        config: StreamingConfig,
        feature_store: FeatureStore,
        early_warning: Optional[EarlyWarningIndicators] = None
    ):
        """Initialize streaming warning adapter.
        
        Args:
            config: Streaming configuration
            feature_store: Redis feature store for state persistence
            early_warning: Batch early warning indicators (for algorithm reuse)
        """
        self.config = config
        self.feature_store = feature_store
        self.early_warning = early_warning or EarlyWarningIndicators()
        
        # State key patterns
        self.STATE_KEY_PATTERN = "warning_state:{customer_key}"
        self.HISTORY_KEY_PATTERN = "warning_history:{customer_key}"
    
    def detect_utilization_warning(
        self,
        event_id: str,
        customer_key: str,
        current_utilization: float,
        timestamp: datetime
    ) -> Optional[WarningSignal]:
        """Detect credit utilization increase warning.
        
        Args:
            event_id: Event identifier
            customer_key: Customer identifier
            current_utilization: Current credit utilization
            timestamp: Event timestamp
        
        Returns:
            WarningSignal if warning detected, None otherwise
        """
        logger.debug(f"Detecting utilization warning for customer {customer_key}")
        
        # Get historical utilization state
        state = self._get_warning_state(customer_key)
        previous_utilization = state.get("utilization", current_utilization)
        
        # Calculate change
        utilization_change = current_utilization - previous_utilization
        
        # Check threshold
        if utilization_change >= self.THRESHOLDS['utilization_increase_threshold']:
            warning_level = self._determine_severity(
                utilization_change,
                self.THRESHOLDS['utilization_increase_threshold']
            )
            warning_score = min(utilization_change / self.THRESHOLDS['utilization_increase_threshold'], 3.0)
            
            return WarningSignal(
                warning_id=str(uuid.uuid4()),
                event_id=event_id,
                customer_key=customer_key,
                signal_type="utilization_increase",
                warning_level=warning_level.value,
                warning_score=warning_score,
                detected_at=datetime.now(timezone.utc).replace(tzinfo=None),
                context_data={
                    "current_utilization": current_utilization,
                    "previous_utilization": previous_utilization,
                    "change": utilization_change,
                    "threshold": self.THRESHOLDS['utilization_increase_threshold']
                },
                threshold_violated=f"Utilization increased by {utilization_change:.2%}"
            )
        
        # Update state
        state["utilization"] = current_utilization
        state["utilization_updated_at"] = timestamp.isoformat()
        self._save_warning_state(customer_key, state)
        
        return None
    
    def detect_payment_warning(
        self,
        event_id: str,
        customer_key: str,
        payment_rate: float,
        timestamp: datetime
    ) -> Optional[WarningSignal]:
        """Detect payment rate decline warning.
        
        Args:
            event_id: Event identifier
            customer_key: Customer identifier
            payment_rate: Current on-time payment rate
            timestamp: Event timestamp
        
        Returns:
            WarningSignal if warning detected, None otherwise
        """
        logger.debug(f"Detecting payment warning for customer {customer_key}")
        
        # Get historical payment state
        state = self._get_warning_state(customer_key)
        previous_payment_rate = state.get("payment_rate", payment_rate)
        
        # Calculate decline
        payment_decline = previous_payment_rate - payment_rate
        
        # Check threshold
        if payment_decline >= self.THRESHOLDS['payment_decline_threshold']:
            warning_level = self._determine_severity(
                payment_decline,
                self.THRESHOLDS['payment_decline_threshold']
            )
            warning_score = min(payment_decline / self.THRESHOLDS['payment_decline_threshold'], 3.0)
            
            return WarningSignal(
                warning_id=str(uuid.uuid4()),
                event_id=event_id,
                customer_key=customer_key,
                signal_type="payment_decline",
                warning_level=warning_level.value,
                warning_score=warning_score,
                detected_at=datetime.now(timezone.utc).replace(tzinfo=None),
                context_data={
                    "current_payment_rate": payment_rate,
                    "previous_payment_rate": previous_payment_rate,
                    "decline": payment_decline,
                    "threshold": self.THRESHOLDS['payment_decline_threshold']
                },
                threshold_violated=f"Payment rate declined by {payment_decline:.2%}"
            )
        
        # Update state
        state["payment_rate"] = payment_rate
        state["payment_updated_at"] = timestamp.isoformat()
        self._save_warning_state(customer_key, state)
        
        return None
    
    def detect_balance_warning(
        self,
        event_id: str,
        customer_key: str,
        current_balance: float,
        timestamp: datetime
    ) -> Optional[WarningSignal]:
        """Detect balance accumulation warning.
        
        Args:
            event_id: Event identifier
            customer_key: Customer identifier
            current_balance: Current balance
            timestamp: Event timestamp
        
        Returns:
            WarningSignal if warning detected, None otherwise
        """
        logger.debug(f"Detecting balance warning for customer {customer_key}")
        
        # Get historical balance state
        state = self._get_warning_state(customer_key)
        previous_balance = state.get("balance", current_balance)
        
        # Calculate change (relative)
        if abs(previous_balance) > 0:
            balance_change = (current_balance - previous_balance) / abs(previous_balance)
        else:
            balance_change = 0.0
        
        # Check threshold
        if balance_change >= self.THRESHOLDS['balance_increase_threshold']:
            warning_level = self._determine_severity(
                balance_change,
                self.THRESHOLDS['balance_increase_threshold']
            )
            warning_score = min(balance_change / self.THRESHOLDS['balance_increase_threshold'], 3.0)
            
            return WarningSignal(
                warning_id=str(uuid.uuid4()),
                event_id=event_id,
                customer_key=customer_key,
                signal_type="balance_increase",
                warning_level=warning_level.value,
                warning_score=warning_score,
                detected_at=datetime.now(timezone.utc).replace(tzinfo=None),
                context_data={
                    "current_balance": current_balance,
                    "previous_balance": previous_balance,
                    "change": balance_change,
                    "threshold": self.THRESHOLDS['balance_increase_threshold']
                },
                threshold_violated=f"Balance increased by {balance_change:.2%}"
            )
        
        # Update state
        state["balance"] = current_balance
        state["balance_updated_at"] = timestamp.isoformat()
        self._save_warning_state(customer_key, state)
        
        return None
    
    def calculate_composite_warning_score(
        self,
        event_id: str,
        customer_key: str,
        features: Dict[str, Any],
        timestamp: datetime
    ) -> Optional[WarningSignal]:
        """Calculate composite warning score from customer metrics.
        
        Reuses batch algorithm for consistency.
        
        Args:
            event_id: Event identifier
            customer_key: Customer identifier
            features: Customer features from Redis
            timestamp: Event timestamp
        
        Returns:
            WarningSignal if warning detected, None otherwise
        """
        logger.debug(f"Calculating composite warning score for customer {customer_key}")
        
        # Use batch algorithm to calculate warning score
        warning_result = self.early_warning.calculate_warning_score(features)
        
        warning_score = warning_result['warning_score']
        warning_level = warning_result['warning_level']
        
        # Generate warning if not low
        if warning_level != "low":
            return WarningSignal(
                warning_id=str(uuid.uuid4()),
                event_id=event_id,
                customer_key=customer_key,
                signal_type="composite_warning",
                warning_level=warning_level,
                warning_score=warning_score / 100.0,  # Normalize to 0-1
                detected_at=datetime.now(timezone.utc).replace(tzinfo=None),
                context_data={
                    "factors": warning_result['factors'],
                    "interpretation": warning_result['interpretation'],
                    "features": features
                },
                threshold_violated=f"Composite warning score {warning_score}"
            )
        
        return None
    
    def update_watchlist(
        self,
        customer_key: str,
        warning_level: str,
        warning_score: float,
        timestamp: datetime
    ):
        """Update customer watchlist status.
        
        Args:
            customer_key: Customer identifier
            warning_level: Warning level
            warning_score: Warning score
            timestamp: Update timestamp
        """
        logger.info(f"Updating watchlist for customer {customer_key}, level {warning_level}")
        
        # Store watchlist status in Redis
        watchlist_key = f"watchlist:{customer_key}"
        watchlist_data = {
            "on_watchlist": warning_level != "low",
            "warning_level": warning_level,
            "warning_score": warning_score,
            "updated_at": timestamp.isoformat()
        }
        
        import json
        self.feature_store.redis_client.setex(
            watchlist_key,
            self.config.feature_store.ttl_seconds,
            json.dumps(watchlist_data)
        )
    
    def _get_warning_state(self, customer_key: str) -> Dict[str, Any]:
        """Get warning state from Redis.
        
        Args:
            customer_key: Customer identifier
        
        Returns:
            Dictionary with warning state
        """
        state_key = self.STATE_KEY_PATTERN.format(customer_key=customer_key)
        
        state_data = self.feature_store.redis_client.get(state_key)
        
        if state_data:
            import json
            return json.loads(state_data)
        
        # Initialize empty state
        return {
            "utilization": 0.0,
            "utilization_updated_at": None,
            "payment_rate": 1.0,
            "payment_updated_at": None,
            "balance": 0.0,
            "balance_updated_at": None,
            "risk_score": 0.0,
            "risk_score_updated_at": None
        }
    
    def _save_warning_state(self, customer_key: str, state: Dict[str, Any]):
        """Save warning state to Redis.
        
        Args:
            customer_key: Customer identifier
            state: State to save
        """
        state_key = self.STATE_KEY_PATTERN.format(customer_key=customer_key)
        
        import json
        state_json = json.dumps(state)
        
        # Save with TTL from config
        ttl = self.config.feature_store.ttl_seconds
        self.feature_store.redis_client.setex(state_key, ttl, state_json)
    
    def _determine_severity(self, value: float, threshold: float) -> WarningSeverity:
        """Determine severity of warning signal.
        
        Reuses batch algorithm for consistency.
        
        Args:
            value: Actual value
            threshold: Threshold value
        
        Returns:
            WarningSeverity enum
        """
        ratio = value / threshold
        
        if ratio >= 3.0:
            return WarningSeverity.CRITICAL
        elif ratio >= 2.0:
            return WarningSeverity.HIGH
        elif ratio >= 1.5:
            return WarningSeverity.MEDIUM
        else:
            return WarningSeverity.LOW
    
    def reset_customer_state(self, customer_key: str):
        """Reset warning state for a customer.
        
        Args:
            customer_key: Customer identifier
        """
        logger.info(f"Resetting warning state for customer {customer_key}")
        
        # Delete state key
        state_key = self.STATE_KEY_PATTERN.format(customer_key=customer_key)
        self.feature_store.redis_client.delete(state_key)
        
        # Delete watchlist status
        watchlist_key = f"watchlist:{customer_key}"
        self.feature_store.redis_client.delete(watchlist_key)


class LeadingIndicators:
    """Leading indicators for early warning detection.
    
    Tracks metrics that tend to lead to future problems, allowing
    proactive intervention before issues materialize.
    """
    
    def __init__(self, window_size: int = 30):
        """Initialize leading indicators tracker.
        
        Args:
            window_size: Window size for indicator calculation
        """
        self.window_size = window_size
        self.indicator_history = defaultdict(lambda: deque(maxlen=window_size))
    
    def track_indicator(
        self,
        customer_key: str,
        indicator_type: str,
        value: float,
        timestamp: datetime
    ):
        """Track a leading indicator value.
        
        Args:
            customer_key: Customer identifier
            indicator_type: Type of indicator
            value: Indicator value
            timestamp: Event timestamp
        """
        self.indicator_history[f"{customer_key}:{indicator_type}"].append({
            'value': value,
            'timestamp': timestamp
        })
    
    def calculate_trend(
        self,
        customer_key: str,
        indicator_type: str
    ) -> Dict[str, Any]:
        """Calculate trend for a leading indicator.
        
        Args:
            customer_key: Customer identifier
            indicator_type: Type of indicator
        
        Returns:
            Trend information
        """
        key = f"{customer_key}:{indicator_type}"
        history = list(self.indicator_history[key])
        
        if len(history) < 3:
            return {
                'indicator_type': indicator_type,
                'trend': 'insufficient_data',
                'current_value': history[-1]['value'] if history else None,
                'change': 0.0,
                'direction': 'none'
            }
        
        values = [h['value'] for h in history]
        current_value = values[-1]
        previous_value = values[0]
        change = current_value - previous_value
        
        # Calculate trend direction
        if change > 0:
            direction = 'increasing'
        elif change < 0:
            direction = 'decreasing'
        else:
            direction = 'stable'
        
        # Calculate trend strength using linear regression
        import numpy as np
        x = np.arange(len(values))
        y = np.array(values)
        slope, _ = np.polyfit(x, y, 1)
        
        return {
            'indicator_type': indicator_type,
            'trend': direction,
            'current_value': current_value,
            'change': change,
            'direction': direction,
            'slope': slope,
            'average': np.mean(values),
            'std': np.std(values)
        }
    
    def detect_early_warning(
        self,
        customer_key: str,
        indicator_type: str,
        threshold: float
    ) -> Tuple[bool, float, str]:
        """Detect early warning from leading indicator.
        
        Args:
            customer_key: Customer identifier
            indicator_type: Type of indicator
            threshold: Warning threshold
        
        Returns:
            Tuple of (is_warning, warning_score, reason)
        """
        trend_info = self.calculate_trend(customer_key, indicator_type)
        
        if trend_info['trend'] == 'insufficient_data':
            return False, 0.0, "insufficient_data"
        
        # Check if trend exceeds threshold
        warning_score = abs(trend_info['slope']) / threshold if threshold > 0 else 0.0
        is_warning = warning_score > 1.0
        
        reason = f"{indicator_type} {trend_info['trend']} trend with slope {trend_info['slope']:.4f}"
        
        return is_warning, warning_score, reason


class WarningEscalation:
    """Warning escalation logic for early warning system.
    
    Manages escalation of warnings based on severity, duration,
    and frequency to ensure appropriate attention.
    """
    
    def __init__(
        self,
        escalation_rules: Optional[Dict[str, Dict[str, Any]]] = None
    ):
        """Initialize warning escalation manager.
        
        Args:
            escalation_rules: Custom escalation rules
        """
        self.escalation_rules = escalation_rules or self._default_rules()
        self.escalation_history = defaultdict(list)
    
    def _default_rules(self) -> Dict[str, Dict[str, Any]]:
        """Default escalation rules.
        
        Returns:
            Default escalation rules
        """
        return {
            'low': {
                'escalation_time_hours': 48,
                'max_occurrences': 5,
                'escalate_to': 'medium'
            },
            'medium': {
                'escalation_time_hours': 24,
                'max_occurrences': 3,
                'escalate_to': 'high'
            },
            'high': {
                'escalation_time_hours': 12,
                'max_occurrences': 2,
                'escalate_to': 'critical'
            },
            'critical': {
                'escalation_time_hours': 1,
                'max_occurrences': 1,
                'escalate_to': 'critical'
            }
        }
    
    def should_escalate(
        self,
        customer_key: str,
        warning_level: str,
        warning_type: str,
        timestamp: datetime
    ) -> Tuple[bool, str, str]:
        """Determine if warning should be escalated.
        
        Args:
            customer_key: Customer identifier
            warning_level: Current warning level
            warning_type: Type of warning
            timestamp: Warning timestamp
        
        Returns:
            Tuple of (should_escalate, new_level, reason)
        """
        # Get rule for current level
        rule = self.escalation_rules.get(warning_level, self.escalation_rules['medium'])
        
        # Get recent warnings for customer
        recent_warnings = [
            w for w in self.escalation_history[customer_key]
            if (timestamp - w['timestamp']).total_seconds() < rule['escalation_time_hours'] * 3600
        ]
        
        # Count occurrences of same warning type
        same_type_count = sum(
            1 for w in recent_warnings
            if w['warning_type'] == warning_type
        )
        
        # Check escalation criteria
        if same_type_count >= rule['max_occurrences']:
            new_level = rule['escalate_to']
            reason = f"Escalated due to {same_type_count} occurrences in {rule['escalation_time_hours']}h"
            return True, new_level, reason
        
        # Check if already at critical
        if warning_level == 'critical':
            return False, warning_level, "Already at critical level"
        
        return False, warning_level, "Escalation criteria not met"
    
    def record_warning(
        self,
        customer_key: str,
        warning_level: str,
        warning_type: str,
        timestamp: datetime
    ):
        """Record a warning for escalation tracking.
        
        Args:
            customer_key: Customer identifier
            warning_level: Warning level
            warning_type: Type of warning
            timestamp: Warning timestamp
        """
        self.escalation_history[customer_key].append({
            'warning_level': warning_level,
            'warning_type': warning_type,
            'timestamp': timestamp
        })
        
        # Clean old history
        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=7)
        self.escalation_history[customer_key] = [
            w for w in self.escalation_history[customer_key]
            if w['timestamp'] > cutoff
        ]
    
    def get_escalation_summary(self, customer_key: str) -> Dict[str, Any]:
        """Get escalation summary for a customer.
        
        Args:
            customer_key: Customer identifier
        
        Returns:
            Escalation summary
        """
        history = self.escalation_history[customer_key]
        
        if not history:
            return {
                'customer_key': customer_key,
                'total_warnings': 0,
                'by_level': {},
                'by_type': {},
                'current_level': 'none'
            }
        
        by_level = defaultdict(int)
        by_type = defaultdict(int)
        
        for warning in history:
            by_level[warning['warning_level']] += 1
            by_type[warning['warning_type']] += 1
        
        # Determine current level
        current_level = history[-1]['warning_level'] if history else 'none'
        
        return {
            'customer_key': customer_key,
            'total_warnings': len(history),
            'by_level': dict(by_level),
            'by_type': dict(by_type),
            'current_level': current_level,
            'last_warning': history[-1]['timestamp'].isoformat() if history else None
        }
