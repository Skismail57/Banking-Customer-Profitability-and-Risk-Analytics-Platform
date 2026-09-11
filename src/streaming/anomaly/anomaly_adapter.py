"""Streaming anomaly detection adapter.

This module adapts the batch anomaly detection algorithms for real-time streaming
event processing. It maintains streaming statistics and provides single-event
anomaly scoring capabilities with ML-based detection.

Assumptions:
- Streaming statistics are maintained in Redis for persistence
- Anomaly detection uses the same mathematical algorithms as batch (IQR, Z-score)
- State is updated incrementally for efficiency
- ML models are trained on historical batch data

Limitations:
- Streaming statistics may differ slightly from batch due to incremental updates
- No support for complex pattern detection in streaming mode (requires historical context)
- Velocity anomalies require recent event history
- ML models require periodic retraining

Fairness Considerations:
- Anomaly thresholds should be calibrated per customer segment to avoid bias
- Consider demographic factors when setting anomaly thresholds
- Monitor anomaly rates across customer segments for fairness
- ML models should be evaluated for bias across demographic groups
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple, List
import logging
import uuid
from dataclasses import dataclass
from collections import deque
import numpy as np

from src.streaming.config import StreamingConfig
from src.streaming.features.feature_store import FeatureStore
from src.transaction_analytics.anomaly import AnomalyDetector

logger = logging.getLogger(__name__)


@dataclass
class AnomalyResult:
    """Result of streaming anomaly detection."""
    anomaly_id: str
    event_id: str
    customer_key: str
    anomaly_type: str
    anomaly_score: float
    severity: str  # low, medium, high, critical
    detected_at: datetime
    context_data: Dict[str, Any]
    threshold_violated: Optional[str] = None


class StreamingAnomalyAdapter:
    """Adapter for streaming anomaly detection.
    
    This adapter adapts the batch AnomalyDetector for real-time streaming
    by maintaining streaming statistics and providing single-event scoring.
    
    Key Features:
    - Reuses batch algorithms (IQR, Z-score) for consistency
    - Maintains streaming statistics in Redis
    - Supports amount, frequency, and velocity anomaly detection
    - Provides severity classification based on score thresholds
    """
    
    # Severity thresholds
    SEVERITY_THRESHOLDS = {
        "critical": 0.95,
        "high": 0.90,
        "medium": 0.80,
        "low": 0.70
    }
    
    def __init__(
        self,
        config: StreamingConfig,
        feature_store: FeatureStore,
        anomaly_detector: Optional[AnomalyDetector] = None
    ):
        """Initialize streaming anomaly adapter.
        
        Args:
            config: Streaming configuration
            feature_store: Redis feature store for state persistence
            anomaly_detector: Batch anomaly detector (for algorithm reuse)
        """
        self.config = config
        self.feature_store = feature_store
        self.anomaly_detector = anomaly_detector or AnomalyDetector()
        
        # State key patterns
        self.STATS_KEY_PATTERN = "anomaly_stats:{customer_key}:{anomaly_type}"
        self.VELOCITY_KEY_PATTERN = "anomaly_velocity:{customer_key}"
    
    def detect_amount_anomaly(
        self,
        event_id: str,
        customer_key: str,
        amount: float,
        timestamp: datetime,
        method: str = "iqr",
        threshold: float = 3.0
    ) -> Optional[AnomalyResult]:
        """Detect amount anomaly for a single transaction.
        
        Args:
            event_id: Event identifier
            customer_key: Customer identifier
            amount: Transaction amount
            timestamp: Event timestamp
            method: Detection method (iqr, zscore)
            threshold: Threshold for anomaly detection
        
        Returns:
            AnomalyResult if anomaly detected, None otherwise
        """
        logger.debug(f"Detecting amount anomaly for customer {customer_key}, amount {amount}")
        
        # Get or initialize streaming statistics
        stats = self._get_streaming_stats(customer_key, "amount")
        
        # Update statistics with new value
        stats = self._update_streaming_stats(stats, amount)
        self._save_streaming_stats(customer_key, "amount", stats)
        
        # Detect anomaly using batch algorithm adapted for streaming
        is_anomaly, anomaly_score = self._detect_streaming_anomaly(
            amount, stats, method, threshold
        )
        
        if is_anomaly:
            severity = self._classify_severity(anomaly_score)
            
            return AnomalyResult(
                anomaly_id=str(uuid.uuid4()),
                event_id=event_id,
                customer_key=customer_key,
                anomaly_type="amount_outlier",
                anomaly_score=anomaly_score,
                severity=severity,
                detected_at=datetime.now(timezone.utc).replace(tzinfo=None),
                context_data={
                    "amount": amount,
                    "method": method,
                    "threshold": threshold,
                    "stats": {
                        "mean": stats.get("mean"),
                        "std": stats.get("std"),
                        "q1": stats.get("q1"),
                        "q3": stats.get("q3"),
                        "count": stats.get("count")
                    }
                },
                threshold_violated=f"amount {amount} exceeds threshold {threshold}"
            )
        
        return None
    
    def detect_velocity_anomaly(
        self,
        event_id: str,
        customer_key: str,
        timestamp: datetime,
        window_minutes: int = 60,
        max_transactions: int = 10
    ) -> Optional[AnomalyResult]:
        """Detect velocity anomaly (rapid transactions).
        
        Args:
            event_id: Event identifier
            customer_key: Customer identifier
            timestamp: Event timestamp
            window_minutes: Time window for velocity check
            max_transactions: Maximum allowed transactions in window
        
        Returns:
            AnomalyResult if anomaly detected, None otherwise
        """
        logger.debug(f"Detecting velocity anomaly for customer {customer_key}")
        
        # Get recent transaction timestamps from Redis
        velocity_key = self.VELOCITY_KEY_PATTERN.format(customer_key=customer_key)
        recent_timestamps = self.feature_store.redis_client.lrange(velocity_key, 0, -1)
        
        # Convert to datetime objects
        recent_timestamps = [
            datetime.fromisoformat(ts.decode()) 
            for ts in recent_timestamps 
            if ts
        ]
        
        # Filter to window
        window_start = timestamp.timestamp() - (window_minutes * 60)
        window_timestamps = [
            ts for ts in recent_timestamps 
            if ts.timestamp() >= window_start
        ]
        
        # Add current timestamp
        window_timestamps.append(timestamp)
        
        # Check if exceeds threshold
        transaction_count = len(window_timestamps)
        if transaction_count > max_transactions:
            anomaly_score = min(transaction_count / max_transactions, 1.0)
            severity = self._classify_severity(anomaly_score)
            
            return AnomalyResult(
                anomaly_id=str(uuid.uuid4()),
                event_id=event_id,
                customer_key=customer_key,
                anomaly_type="velocity_anomaly",
                anomaly_score=anomaly_score,
                severity=severity,
                detected_at=datetime.now(timezone.utc).replace(tzinfo=None),
                context_data={
                    "transaction_count": transaction_count,
                    "window_minutes": window_minutes,
                    "max_transactions": max_transactions,
                    "timestamps": [ts.isoformat() for ts in window_timestamps]
                },
                threshold_violated=f"{transaction_count} transactions in {window_minutes}min window exceeds {max_transactions}"
            )
        
        # Update velocity history
        self.feature_store.redis_client.lpush(velocity_key, timestamp.isoformat())
        self.feature_store.redis_client.ltrim(velocity_key, 0, 99)  # Keep last 100
        self.feature_store.redis_client.expire(velocity_key, window_minutes * 60 * 2)
        
        return None
    
    def detect_frequency_anomaly(
        self,
        event_id: str,
        customer_key: str,
        timestamp: datetime,
        window_days: int = 30,
        threshold_multiplier: float = 2.0
    ) -> Optional[AnomalyResult]:
        """Detect frequency anomaly (unusual transaction frequency).
        
        Args:
            event_id: Event identifier
            customer_key: Customer identifier
            timestamp: Event timestamp
            window_days: Window size for frequency calculation
            threshold_multiplier: Threshold multiplier for anomaly detection
        
        Returns:
            AnomalyResult if anomaly detected, None otherwise
        """
        logger.debug(f"Detecting frequency anomaly for customer {customer_key}")
        
        # Get streaming frequency statistics
        stats = self._get_streaming_stats(customer_key, "frequency")
        
        # Increment transaction count
        stats["count"] = stats.get("count", 0) + 1
        stats["last_transaction"] = timestamp.isoformat()
        
        # Calculate mean and std (simplified for streaming)
        if stats.get("count", 0) > 1:
            # Use historical mean/std if available
            mean = stats.get("mean", 1.0)
            std = stats.get("std", 0.5)
            
            # Detect anomaly if count exceeds threshold
            threshold = mean + threshold_multiplier * std
            if stats["count"] > threshold:
                anomaly_score = min(stats["count"] / threshold, 1.0)
                severity = self._classify_severity(anomaly_score)
                
                return AnomalyResult(
                    anomaly_id=str(uuid.uuid4()),
                    event_id=event_id,
                    customer_key=customer_key,
                    anomaly_type="frequency_anomaly",
                    anomaly_score=anomaly_score,
                    severity=severity,
                    detected_at=datetime.now(timezone.utc).replace(tzinfo=None),
                    context_data={
                        "transaction_count": stats["count"],
                        "window_days": window_days,
                        "threshold": threshold,
                        "mean": mean,
                        "std": std
                    },
                    threshold_violated=f"{stats['count']} transactions exceeds threshold {threshold}"
                )
        
        # Save updated statistics
        self._save_streaming_stats(customer_key, "frequency", stats)
        
        return None
    
    def _get_streaming_stats(self, customer_key: str, anomaly_type: str) -> Dict[str, Any]:
        """Get streaming statistics from Redis.
        
        Args:
            customer_key: Customer identifier
            anomaly_type: Type of anomaly (amount, frequency)
        
        Returns:
            Dictionary with streaming statistics
        """
        stats_key = self.STATS_KEY_PATTERN.format(
            customer_key=customer_key,
            anomaly_type=anomaly_type
        )
        
        stats_data = self.feature_store.redis_client.get(stats_key)
        
        if stats_data:
            import json
            return json.loads(stats_data)
        
        # Initialize empty statistics
        return {
            "count": 0,
            "sum": 0.0,
            "sum_sq": 0.0,
            "mean": 0.0,
            "std": 0.0,
            "min": float('inf'),
            "max": float('-inf'),
            "q1": 0.0,
            "q3": 0.0,
            "values": []
        }
    
    def _update_streaming_stats(self, stats: Dict[str, Any], value: float) -> Dict[str, Any]:
        """Update streaming statistics with new value.
        
        Uses Welford's algorithm for online mean and variance calculation.
        
        Args:
            stats: Current statistics
            value: New value to add
        
        Returns:
            Updated statistics
        """
        stats["count"] += 1
        stats["sum"] += value
        stats["sum_sq"] += value * value
        stats["min"] = min(stats["min"], value)
        stats["max"] = max(stats["max"], value)
        
        # Update mean and std using Welford's algorithm
        n = stats["count"]
        if n == 1:
            stats["mean"] = value
            stats["std"] = 0.0
        else:
            delta = value - stats["mean"]
            stats["mean"] += delta / n
            delta2 = value - stats["mean"]
            stats["std"] += delta * delta2
        
        # Calculate std from sum of squared deviations
        if n > 1:
            stats["std"] = (stats["std"] / (n - 1)) ** 0.5
        
        # Update quantiles (simplified - keep last 1000 values)
        stats["values"].append(value)
        if len(stats["values"]) > 1000:
            stats["values"] = stats["values"][-1000:]
        
        # Calculate quantiles
        if len(stats["values"]) >= 4:
            import numpy as np
            stats["q1"] = float(np.percentile(stats["values"], 25))
            stats["q3"] = float(np.percentile(stats["values"], 75))
        
        return stats
    
    def _save_streaming_stats(self, customer_key: str, anomaly_type: str, stats: Dict[str, Any]):
        """Save streaming statistics to Redis.
        
        Args:
            customer_key: Customer identifier
            anomaly_type: Type of anomaly
            stats: Statistics to save
        """
        stats_key = self.STATS_KEY_PATTERN.format(
            customer_key=customer_key,
            anomaly_type=anomaly_type
        )
        
        import json
        stats_json = json.dumps(stats)
        
        # Save with TTL from config
        ttl = self.config.event_processing.idempotency_ttl_seconds
        self.feature_store.redis_client.setex(stats_key, ttl, stats_json)
    
    def _detect_streaming_anomaly(
        self,
        value: float,
        stats: Dict[str, Any],
        method: str,
        threshold: float
    ) -> Tuple[bool, float]:
        """Detect anomaly using streaming statistics.
        
        Reuses batch algorithms (IQR, Z-score) with streaming statistics.
        
        Args:
            value: Value to check
            stats: Streaming statistics
            method: Detection method
            threshold: Threshold
        
        Returns:
            Tuple of (is_anomaly, anomaly_score)
        """
        if method == "iqr":
            # Use IQR method from batch detector
            q1 = stats.get("q1", 0.0)
            q3 = stats.get("q3", 0.0)
            iqr = q3 - q1
            
            if iqr == 0:
                return False, 0.0
            
            lower_bound = q1 - threshold * iqr
            upper_bound = q3 + threshold * iqr
            
            is_anomaly = value < lower_bound or value > upper_bound
            
            # Calculate anomaly score based on distance from bounds
            if is_anomaly:
                distance = max(abs(value - lower_bound), abs(value - upper_bound))
                anomaly_score = min(distance / iqr, 1.0)
            else:
                anomaly_score = 0.0
            
            return is_anomaly, anomaly_score
        
        elif method == "zscore":
            # Use Z-score method from batch detector
            mean = stats.get("mean", 0.0)
            std = stats.get("std", 1.0)
            
            if std == 0:
                return False, 0.0
            
            z_score = abs(value - mean) / std
            is_anomaly = z_score > threshold
            anomaly_score = min(z_score / threshold, 1.0)
            
            return is_anomaly, anomaly_score
        
        else:
            logger.warning(f"Unsupported method: {method}")
            return False, 0.0
    
    def _classify_severity(self, anomaly_score: float) -> str:
        """Classify anomaly severity based on score.
        
        Args:
            anomaly_score: Anomaly score (0-1)
        
        Returns:
            Severity level (low, medium, high, critical)
        """
        if anomaly_score >= self.SEVERITY_THRESHOLDS["critical"]:
            return "critical"
        elif anomaly_score >= self.SEVERITY_THRESHOLDS["high"]:
            return "high"
        elif anomaly_score >= self.SEVERITY_THRESHOLDS["medium"]:
            return "medium"
        else:
            return "low"
    
    def reset_customer_stats(self, customer_key: str):
        """Reset streaming statistics for a customer.
        
        Args:
            customer_key: Customer identifier
        """
        logger.info(f"Resetting anomaly statistics for customer {customer_key}")
        
        # Delete all stats keys for customer
        for anomaly_type in ["amount", "frequency"]:
            stats_key = self.STATS_KEY_PATTERN.format(
                customer_key=customer_key,
                anomaly_type=anomaly_type
            )
            self.feature_store.redis_client.delete(stats_key)
        
        # Delete velocity history
        velocity_key = self.VELOCITY_KEY_PATTERN.format(customer_key=customer_key)
        self.feature_store.redis_client.delete(velocity_key)


class MLAnomalyDetector:
    """ML-based anomaly detection for complex patterns.
    
    Uses isolation forest and autoencoder approaches for detecting
    complex anomalies that statistical methods may miss.
    """
    
    def __init__(
        self,
        model_type: str = "isolation_forest",
        window_size: int = 100,
        contamination: float = 0.1
    ):
        """Initialize ML anomaly detector.
        
        Args:
            model_type: Type of ML model (isolation_forest, autoencoder)
            window_size: Window size for feature extraction
            contamination: Expected contamination rate
        """
        self.model_type = model_type
        self.window_size = window_size
        self.contamination = contamination
        self.model = None
        self.is_trained = False
        self.feature_history = defaultdict(lambda: deque(maxlen=window_size))
    
    def extract_features(self, value: float, history: deque) -> np.ndarray:
        """Extract features from value and history.
        
        Args:
            value: Current value
            history: Historical values
        
        Returns:
            Feature vector
        """
        features = []
        
        # Statistical features
        if len(history) > 0:
            history_array = np.array(list(history))
            features.extend([
                np.mean(history_array),
                np.std(history_array),
                np.min(history_array),
                np.max(history_array),
                np.median(history_array),
                np.percentile(history_array, 25),
                np.percentile(history_array, 75)
            ])
        else:
            features.extend([value, 0.0, value, value, value, value, value])
        
        # Current value
        features.append(value)
        
        # Difference features
        if len(history) > 0:
            features.append(value - history[-1])
            if len(history) > 1:
                features.append(value - history[-2])
            else:
                features.append(0.0)
        else:
            features.extend([0.0, 0.0])
        
        return np.array(features)
    
    def train(self, normal_data: List[float]):
        """Train the ML model on normal data.
        
        Args:
            normal_data: List of normal (non-anomalous) values
        """
        logger.info(f"Training {self.model_type} model on {len(normal_data)} samples")
        
        # Extract features
        features = []
        history = deque(maxlen=self.window_size)
        
        for value in normal_data:
            feature_vector = self.extract_features(value, history)
            features.append(feature_vector)
            history.append(value)
        
        features_array = np.array(features)
        
        if self.model_type == "isolation_forest":
            from sklearn.ensemble import IsolationForest
            self.model = IsolationForest(
                contamination=self.contamination,
                random_state=42
            )
            self.model.fit(features_array)
        
        elif self.model_type == "autoencoder":
            from sklearn.preprocessing import StandardScaler
            from sklearn.neural_network import MLPRegressor
            
            self.scaler = StandardScaler()
            features_scaled = self.scaler.fit_transform(features_array)
            
            self.model = MLPRegressor(
                hidden_layer_sizes=(8, 4),
                max_iter=100,
                random_state=42
            )
            self.model.fit(features_scaled, features_scaled)
        
        self.is_trained = True
        logger.info(f"{self.model_type} model trained successfully")
    
    def detect(self, value: float, feature_name: str) -> Tuple[bool, float]:
        """Detect anomaly using ML model.
        
        Args:
            value: Current value
            feature_name: Feature name for history tracking
        
        Returns:
            Tuple of (is_anomaly, anomaly_score)
        """
        if not self.is_trained:
            logger.warning("ML model not trained, returning no anomaly")
            return False, 0.0
        
        # Update history
        self.feature_history[feature_name].append(value)
        
        # Extract features
        feature_vector = self.extract_features(value, self.feature_history[feature_name])
        feature_array = feature_vector.reshape(1, -1)
        
        if self.model_type == "isolation_forest":
            prediction = self.model.predict(feature_array)[0]
            anomaly_score = self.model.score_samples(feature_array)[0]
            is_anomaly = prediction == -1
            # Convert score to 0-1 range
            anomaly_score = max(0, min(1, (anomaly_score + 0.5)))
        
        elif self.model_type == "autoencoder":
            feature_scaled = self.scaler.transform(feature_array)
            reconstruction = self.model.predict(feature_scaled)
            reconstruction_error = np.mean((feature_scaled - reconstruction) ** 2)
            anomaly_score = min(reconstruction_error * 10, 1.0)
            is_anomaly = anomaly_score > 0.5
        
        return is_anomaly, anomaly_score


class AnomalyAlertIntegrator:
    """Integrate anomaly detection with alerting system.
    
    Routes anomaly results to appropriate alert channels and
    manages alert deduplication and escalation.
    """
    
    def __init__(
        self,
        dedup_window_seconds: int = 3600,
        max_alerts_per_customer_per_hour: int = 10
    ):
        """Initialize anomaly alert integrator.
        
        Args:
            dedup_window_seconds: Deduplication window in seconds
            max_alerts_per_customer_per_hour: Maximum alerts per customer per hour
        """
        self.dedup_window_seconds = dedup_window_seconds
        self.max_alerts_per_customer_per_hour = max_alerts_per_customer_per_hour
        self.alert_history = defaultdict(list)
    
    def should_alert(
        self,
        customer_key: str,
        anomaly_type: str,
        severity: str
    ) -> Tuple[bool, str]:
        """Determine if alert should be sent.
        
        Args:
            customer_key: Customer identifier
            anomaly_type: Type of anomaly
            severity: Anomaly severity
        
        Returns:
            Tuple of (should_alert, reason)
        """
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        
        # Get recent alerts for customer
        recent_alerts = [
            a for a in self.alert_history[customer_key]
            if (now - a['timestamp']).total_seconds() < 3600
        ]
        
        # Check rate limit
        if len(recent_alerts) >= self.max_alerts_per_customer_per_hour:
            return False, "Rate limit exceeded"
        
        # Check deduplication
        dedup_cutoff = now.timestamp() - self.dedup_window_seconds
        for alert in recent_alerts:
            if (alert['anomaly_type'] == anomaly_type and
                alert['severity'] == severity and
                alert['timestamp'].timestamp() > dedup_cutoff):
                return False, "Duplicate alert within deduplication window"
        
        return True, "Alert allowed"
    
    def record_alert(
        self,
        customer_key: str,
        anomaly_type: str,
        severity: str,
        anomaly_id: str
    ):
        """Record that an alert was sent.
        
        Args:
            customer_key: Customer identifier
            anomaly_type: Type of anomaly
            severity: Anomaly severity
            anomaly_id: Anomaly identifier
        """
        self.alert_history[customer_key].append({
            'anomaly_type': anomaly_type,
            'severity': severity,
            'anomaly_id': anomaly_id,
            'timestamp': datetime.now(timezone.utc).replace(tzinfo=None)
        })
        
        # Clean old alerts
        cutoff = datetime.now(timezone.utc).replace(tzinfo=None).timestamp() - 86400  # 24 hours
        self.alert_history[customer_key] = [
            a for a in self.alert_history[customer_key]
            if a['timestamp'].timestamp() > cutoff
        ]
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get summary of alert activity.
        
        Returns:
            Alert summary dictionary
        """
        summary = {
            'total_customers': len(self.alert_history),
            'total_alerts': sum(len(alerts) for alerts in self.alert_history.values()),
            'alerts_by_customer': {
                customer: len(alerts)
                for customer, alerts in self.alert_history.items()
            },
            'alerts_by_type': defaultdict(int),
            'alerts_by_severity': defaultdict(int)
        }
        
        for alerts in self.alert_history.values():
            for alert in alerts:
                summary['alerts_by_type'][alert['anomaly_type']] += 1
                summary['alerts_by_severity'][alert['severity']] += 1
        
        return dict(summary)
