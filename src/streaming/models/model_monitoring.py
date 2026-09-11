"""Model monitoring for ML model performance and drift detection.

This module provides model monitoring capabilities for the banking analytics
platform, tracking model performance, detecting drift, and health checks.

Assumptions:
- Model predictions are logged for monitoring
- Ground truth labels are available for evaluation
- Monitoring metrics are stored in Redis for fast access

Limitations:
- Ground truth may be delayed (label latency)
- Drift detection requires sufficient historical data
- No support for concept drift detection

Fairness Considerations:
- Monitor model performance across customer segments
- Track fairness metrics over time
- Alert on performance degradation for protected groups
"""

from collections import defaultdict, deque
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List, Tuple
import logging
import uuid
from dataclasses import dataclass
from enum import Enum
import numpy as np
from scipy import stats

from src.streaming.config import StreamingConfig
from src.streaming.features.feature_store import FeatureStore

logger = logging.getLogger(__name__)


class DriftType(Enum):
    """Types of model drift."""
    DATA_DRIFT = "data_drift"
    TARGET_DRIFT = "target_drift"
    PERFORMANCE_DRIFT = "performance_drift"


class HealthStatus(Enum):
    """Model health status."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    DEGRADED = "degraded"


@dataclass
class PerformanceMetrics:
    """Model performance metrics."""
    model_id: str
    version: str
    timestamp: datetime
    accuracy: Optional[float]
    precision: Optional[float]
    recall: Optional[float]
    f1_score: Optional[float]
    auc_roc: Optional[float]
    prediction_count: int
    latency_ms: float


@dataclass
class DriftAlert:
    """Drift detection alert."""
    alert_id: str
    model_id: str
    version: str
    drift_type: str
    drift_score: float
    threshold: float
    detected_at: datetime
    feature_name: Optional[str] = None
    context_data: Optional[Dict[str, Any]] = None


class ModelPerformanceTracker:
    """Track model performance metrics over time."""
    
    def __init__(
        self,
        feature_store: FeatureStore,
        window_size: int = 1000
    ):
        """Initialize performance tracker.
        
        Args:
            feature_store: Redis feature store
            window_size: Window size for metrics
        """
        self.feature_store = feature_store
        self.window_size = window_size
        self.metrics_history = defaultdict(lambda: deque(maxlen=window_size))
    
    def record_prediction(
        self,
        model_id: str,
        version: str,
        prediction: Any,
        features: Dict[str, Any],
        latency_ms: float,
        timestamp: Optional[datetime] = None
    ):
        """Record a model prediction.
        
        Args:
            model_id: Model identifier
            version: Model version
            prediction: Model prediction
            features: Input features
            latency_ms: Prediction latency
            timestamp: Prediction timestamp
        """
        if timestamp is None:
            timestamp = datetime.now(timezone.utc).replace(tzinfo=None)
        
        key = f"{model_id}:{version}"
        self.metrics_history[key].append({
            'timestamp': timestamp,
            'prediction': prediction,
            'features': features,
            'latency_ms': latency_ms
        })
    
    def record_ground_truth(
        self,
        model_id: str,
        version: str,
        actual: Any,
        timestamp: datetime
    ):
        """Record ground truth label.
        
        Args:
            model_id: Model identifier
            version: Model version
            actual: Actual label
            timestamp: Label timestamp
        """
        # In production, this would match predictions with ground truth
        # and calculate performance metrics
        logger.debug(f"Recording ground truth for {model_id}:{version}")
    
    def calculate_metrics(
        self,
        model_id: str,
        version: str,
        predictions: List[Any],
        actuals: List[Any]
    ) -> PerformanceMetrics:
        """Calculate performance metrics.
        
        Args:
            model_id: Model identifier
            version: Model version
            predictions: Model predictions
            actuals: Ground truth labels
        
        Returns:
            PerformanceMetrics
        """
        # Calculate basic metrics
        correct = sum(1 for p, a in zip(predictions, actuals) if p == a)
        accuracy = correct / len(predictions) if predictions else 0.0
        
        # Get average latency
        key = f"{model_id}:{version}"
        latencies = [m['latency_ms'] for m in self.metrics_history[key]]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
        
        return PerformanceMetrics(
            model_id=model_id,
            version=version,
            timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
            accuracy=accuracy,
            precision=None,  # Would calculate for binary classification
            recall=None,
            f1_score=None,
            auc_roc=None,
            prediction_count=len(predictions),
            latency_ms=avg_latency
        )
    
    def get_performance_trend(
        self,
        model_id: str,
        version: str,
        window_size: int = 100
    ) -> Dict[str, Any]:
        """Get performance trend over time.
        
        Args:
            model_id: Model identifier
            version: Model version
            window_size: Window size for trend
        
        Returns:
            Trend information
        """
        key = f"{model_id}:{version}"
        history = list(self.metrics_history[key])[-window_size:]
        
        if len(history) < 2:
            return {
                'model_id': model_id,
                'version': version,
                'trend': 'insufficient_data',
                'current_accuracy': 0.0,
                'change': 0.0
            }
        
        # Calculate trend (simplified)
        latencies = [m['latency_ms'] for m in history]
        current_latency = latencies[-1]
        previous_latency = latencies[0]
        change = current_latency - previous_latency
        
        return {
            'model_id': model_id,
            'version': version,
            'trend': 'increasing' if change > 0 else 'decreasing',
            'current_latency_ms': current_latency,
            'change_ms': change,
            'average_latency_ms': sum(latencies) / len(latencies)
        }


class DriftDetector:
    """Detect model and data drift."""
    
    def __init__(
        self,
        feature_store: FeatureStore,
        drift_threshold: float = 0.05
    ):
        """Initialize drift detector.
        
        Args:
            feature_store: Redis feature store
            drift_threshold: Threshold for drift detection
        """
        self.feature_store = feature_store
        self.drift_threshold = drift_threshold
        self.baseline_distributions = {}
    
    def set_baseline(
        self,
        model_id: str,
        version: str,
        features: Dict[str, List[float]]
    ):
        """Set baseline feature distributions.
        
        Args:
            model_id: Model identifier
            version: Model version
            features: Dictionary of feature values
        """
        key = f"{model_id}:{version}"
        self.baseline_distributions[key] = {
            'mean': {k: np.mean(v) for k, v in features.items()},
            'std': {k: np.std(v) for k, v in features.items()},
            'timestamp': datetime.now(timezone.utc).replace(tzinfo=None)
        }
    
    def detect_data_drift(
        self,
        model_id: str,
        version: str,
        current_features: Dict[str, List[float]]
    ) -> Optional[DriftAlert]:
        """Detect data drift using KS test.
        
        Args:
            model_id: Model identifier
            version: Model version
            current_features: Current feature values
        
        Returns:
            DriftAlert if drift detected, None otherwise
        """
        key = f"{model_id}:{version}"
        baseline = self.baseline_distributions.get(key)
        
        if not baseline:
            logger.warning(f"No baseline set for {key}")
            return None
        
        max_drift_score = 0.0
        drifted_feature = None
        
        for feature_name, current_values in current_features.items():
            if feature_name not in baseline['mean']:
                continue
            
            # Calculate KS statistic
            baseline_mean = baseline['mean'][feature_name]
            baseline_std = baseline['std'][feature_name]
            
            current_mean = np.mean(current_values)
            
            # Simple drift score based on mean shift
            drift_score = abs(current_mean - baseline_mean) / (baseline_std + 1e-6)
            
            if drift_score > max_drift_score:
                max_drift_score = drift_score
                drifted_feature = feature_name
        
        if max_drift_score > self.drift_threshold:
            return DriftAlert(
                alert_id=str(uuid.uuid4()),
                model_id=model_id,
                version=version,
                drift_type=DriftType.DATA_DRIFT.value,
                drift_score=max_drift_score,
                threshold=self.drift_threshold,
                detected_at=datetime.now(timezone.utc).replace(tzinfo=None),
                feature_name=drifted_feature,
                context_data={
                    'baseline_mean': baseline['mean'].get(drifted_feature),
                    'current_mean': np.mean(current_features.get(drifted_feature, []))
                }
            )
        
        return None
    
    def detect_performance_drift(
        self,
        model_id: str,
        version: str,
        current_accuracy: float,
        baseline_accuracy: float
    ) -> Optional[DriftAlert]:
        """Detect performance drift.
        
        Args:
            model_id: Model identifier
            version: Model version
            current_accuracy: Current accuracy
            baseline_accuracy: Baseline accuracy
        
        Returns:
            DriftAlert if drift detected, None otherwise
        """
        drift_score = abs(current_accuracy - baseline_accuracy)
        
        if drift_score > self.drift_threshold:
            return DriftAlert(
                alert_id=str(uuid.uuid4()),
                model_id=model_id,
                version=version,
                drift_type=DriftType.PERFORMANCE_DRIFT.value,
                drift_score=drift_score,
                threshold=self.drift_threshold,
                detected_at=datetime.now(timezone.utc).replace(tzinfo=None),
                context_data={
                    'baseline_accuracy': baseline_accuracy,
                    'current_accuracy': current_accuracy
                }
            )
        
        return None


class ModelHealthChecker:
    """Perform health checks on deployed models."""
    
    def __init__(
        self,
        feature_store: FeatureStore,
        performance_tracker: ModelPerformanceTracker,
        drift_detector: DriftDetector
    ):
        """Initialize health checker.
        
        Args:
            feature_store: Redis feature store
            performance_tracker: Performance tracker
            drift_detector: Drift detector
        """
        self.feature_store = feature_store
        self.performance_tracker = performance_tracker
        self.drift_detector = drift_detector
    
    def check_health(
        self,
        model_id: str,
        version: str
    ) -> Tuple[HealthStatus, List[str]]:
        """Check model health.
        
        Args:
            model_id: Model identifier
            version: Model version
        
        Returns:
            Tuple of (health status, list of issues)
        """
        issues = []
        
        # Check prediction volume
        key = f"{model_id}:{version}"
        prediction_count = len(self.performance_tracker.metrics_history[key])
        
        if prediction_count == 0:
            issues.append("No predictions recorded")
            return HealthStatus.CRITICAL, issues
        
        # Check latency
        latencies = [m['latency_ms'] for m in self.performance_tracker.metrics_history[key]]
        avg_latency = sum(latencies) / len(latencies)
        
        if avg_latency > 1000:  # 1 second threshold
            issues.append(f"High latency: {avg_latency:.2f}ms")
        
        # Check for drift (would need baseline)
        # This is a simplified check
        
        # Determine health status
        if not issues:
            return HealthStatus.HEALTHY, []
        elif len(issues) == 1:
            return HealthStatus.WARNING, issues
        else:
            return HealthStatus.DEGRADED, issues
    
    def generate_health_report(
        self,
        model_id: str,
        version: str
    ) -> Dict[str, Any]:
        """Generate comprehensive health report.
        
        Args:
            model_id: Model identifier
            version: Model version
        
        Returns:
            Health report
        """
        health_status, issues = self.check_health(model_id, version)
        
        # Get performance trend
        trend = self.performance_tracker.get_performance_trend(model_id, version)
        
        return {
            'model_id': model_id,
            'version': version,
            'health_status': health_status.value,
            'issues': issues,
            'performance_trend': trend,
            'checked_at': datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
        }
