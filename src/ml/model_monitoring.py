"""Model Monitoring.

This module implements comprehensive model monitoring to track model performance
over time and detect model drift.

Key Monitoring Capabilities:
- Performance metric tracking
- Prediction distribution monitoring
- Feature drift detection
- Model drift detection
- Alerting on degradation

NOTE: This is an analytical/educational model for decision support.
It does not make actual lending decisions.
"""

from typing import Dict, Any, List, Optional
from datetime import date, timedelta
from enum import Enum
import logging

import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import ks_2samp

logger = logging.getLogger(__name__)


class DriftType(Enum):
    """Types of drift to monitor."""
    FEATURE_DRIFT = "feature_drift"
    TARGET_DRIFT = "target_drift"
    PREDICTION_DRIFT = "prediction_drift"
    PERFORMANCE_DRIFT = "performance_drift"


class AlertSeverity(Enum):
    """Severity levels for alerts."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class ModelMonitor:
    """Monitor model performance and detect drift.
    
    This class tracks model performance over time and detects when
    the model may need retraining due to drift.
    
    Assumptions:
    - Historical performance data is available for comparison
    - Feature distributions are relatively stable under normal conditions
    - Performance degradation indicates potential model drift
    
    Limitations:
    - May flag seasonal changes as drift
    - Requires sufficient historical data for comparison
    - Does not account for external economic factors
    - Thresholds may need calibration for different models
    
    Fairness Considerations:
    - Monitor performance across demographic groups
    - Check for disparate impact in model degradation
    - Ensure alerts are not biased against any segment
    - Regular audit for bias in drift detection
    """
    
    def __init__(
        self,
        model_name: str,
        performance_threshold: float = 0.05,
        drift_threshold: float = 0.1
    ):
        """Initialize Model Monitor.
        
        Args:
            model_name: Name of the model to monitor
            performance_threshold: Threshold for performance degradation (5%)
            drift_threshold: Threshold for drift detection (10%)
        """
        self.model_name = model_name
        self.performance_threshold = performance_threshold
        self.drift_threshold = drift_threshold
        
        # Performance history
        self.performance_history: List[Dict[str, Any]] = []
    
    def log_performance(
        self,
        metrics: Dict[str, float],
        as_of_date: date,
        sample_count: int
    ) -> None:
        """Log model performance metrics.
        
        Args:
            metrics: Dictionary of performance metrics (accuracy, precision, recall, etc.)
            as_of_date: Date of performance measurement
            sample_count: Number of samples used for evaluation
        """
        performance_record = {
            'model_name': self.model_name,
            'as_of_date': as_of_date,
            'sample_count': sample_count,
            **metrics
        }
        
        self.performance_history.append(performance_record)
        logger.info(f"Logged performance for {self.model_name} on {as_of_date}: {metrics}")
    
    def detect_performance_drift(
        self,
        window_days: int = 30
    ) -> Dict[str, Any]:
        """Detect performance degradation over time.
        
        Args:
            window_days: Window for comparison (days)
        
        Returns:
            Dictionary with drift detection results
        """
        if len(self.performance_history) < 2:
            return {
                'drift_detected': False,
                'reason': 'Insufficient performance history'
            }
        
        # Convert to DataFrame
        perf_df = pd.DataFrame(self.performance_history)
        perf_df['as_of_date'] = pd.to_datetime(perf_df['as_of_date'])
        perf_df = perf_df.sort_values('as_of_date')
        
        # Get recent and baseline performance
        cutoff_date = perf_df['as_of_date'].max() - timedelta(days=window_days)
        recent_perf = perf_df[perf_df['as_of_date'] > cutoff_date]
        baseline_perf = perf_df[perf_df['as_of_date'] <= cutoff_date]
        
        if baseline_perf.empty or recent_perf.empty:
            return {
                'drift_detected': False,
                'reason': 'Insufficient data for drift detection'
            }
        
        # Compare metrics
        drift_detected = False
        drift_details = []
        
        for metric in ['accuracy', 'precision', 'recall', 'f1_score', 'auc_roc']:
            if metric not in perf_df.columns:
                continue
            
            baseline_mean = baseline_perf[metric].mean()
            recent_mean = recent_perf[metric].mean()
            
            if baseline_mean == 0:
                continue
            
            percent_change = (recent_mean - baseline_mean) / baseline_mean
            
            if percent_change < -self.performance_threshold:
                drift_detected = True
                alert_severity = AlertSeverity.CRITICAL if percent_change < -2 * self.performance_threshold else AlertSeverity.WARNING
                
                drift_details.append({
                    'metric': metric,
                    'baseline_mean': float(baseline_mean),
                    'recent_mean': float(recent_mean),
                    'percent_change': float(percent_change),
                    'severity': alert_severity.value
                })
        
        return {
            'drift_detected': drift_detected,
            'drift_details': drift_details,
            'window_days': window_days,
            'alert_severity': AlertSeverity.CRITICAL.value if drift_detected else AlertSeverity.INFO.value
        }
    
    def detect_feature_drift(
        self,
        baseline_features: pd.DataFrame,
        current_features: pd.DataFrame,
        feature_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Detect drift in feature distributions using KS test.
        
        Args:
            baseline_features: Baseline feature distribution
            current_features: Current feature distribution
            feature_names: Optional list of feature names to check
        
        Returns:
            Dictionary with feature drift detection results
        """
        if feature_names is None:
            feature_names = baseline_features.columns.tolist()
        
        drift_detected = False
        drift_details = []
        
        for feature in feature_names:
            if feature not in baseline_features.columns or feature not in current_features.columns:
                continue
            
            baseline_values = baseline_features[feature].dropna()
            current_values = current_features[feature].dropna()
            
            if len(baseline_values) < 30 or len(current_values) < 30:
                continue
            
            # Perform KS test
            ks_statistic, p_value = ks_2samp(baseline_values, current_values)
            
            # Check for drift
            if p_value < 0.05:  # Statistically significant difference
                drift_detected = True
                severity = AlertSeverity.CRITICAL if p_value < 0.01 else AlertSeverity.WARNING
                
                drift_details.append({
                    'feature': feature,
                    'ks_statistic': float(ks_statistic),
                    'p_value': float(p_value),
                    'baseline_mean': float(baseline_values.mean()),
                    'current_mean': float(current_values.mean()),
                    'severity': severity.value
                })
        
        return {
            'drift_detected': drift_detected,
            'drift_type': DriftType.FEATURE_DRIFT.value,
            'drift_details': drift_details,
            'features_checked': len(feature_names),
            'features_with_drift': len(drift_details)
        }
    
    def detect_prediction_drift(
        self,
        baseline_predictions: np.ndarray,
        current_predictions: np.ndarray
    ) -> Dict[str, Any]:
        """Detect drift in prediction distributions.
        
        Args:
            baseline_predictions: Baseline predictions
            current_predictions: Current predictions
        
        Returns:
            Dictionary with prediction drift detection results
        """
        # Perform KS test
        ks_statistic, p_value = ks_2samp(baseline_predictions, current_predictions)
        
        drift_detected = p_value < 0.05
        severity = AlertSeverity.CRITICAL if p_value < 0.01 else AlertSeverity.WARNING if drift_detected else AlertSeverity.INFO
        
        # Calculate distribution statistics
        baseline_mean = np.mean(baseline_predictions)
        current_mean = np.mean(current_predictions)
        baseline_std = np.std(baseline_predictions)
        current_std = np.std(current_predictions)
        
        return {
            'drift_detected': drift_detected,
            'drift_type': DriftType.PREDICTION_DRIFT.value,
            'ks_statistic': float(ks_statistic),
            'p_value': float(p_value),
            'baseline_mean': float(baseline_mean),
            'current_mean': float(current_mean),
            'baseline_std': float(baseline_std),
            'current_std': float(current_std),
            'severity': severity.value
        }
    
    def generate_monitoring_report(
        self,
        baseline_features: Optional[pd.DataFrame] = None,
        current_features: Optional[pd.DataFrame] = None,
        baseline_predictions: Optional[np.ndarray] = None,
        current_predictions: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive monitoring report.
        
        Args:
            baseline_features: Baseline feature distribution
            current_features: Current feature distribution
            baseline_predictions: Baseline predictions
            current_predictions: Current predictions
        
        Returns:
            Dictionary with monitoring report
        """
        logger.info(f"Generating monitoring report for {self.model_name}")
        
        report = {
            'model_name': self.model_name,
            'performance_drift': self.detect_performance_drift(),
            'assumptions': [
                'Performance thresholds based on historical patterns',
                'KS test for distribution comparison',
                'Statistical significance level: 0.05'
            ],
            'limitations': [
                'May flag seasonal changes as drift',
                'Requires sufficient historical data',
                'Does not account for external factors',
                'Thresholds may need calibration'
            ],
            'fairness_considerations': [
                'Monitor performance across demographic groups',
                'Check for disparate impact in drift',
                'Ensure alerts are not biased',
                'Regular audit for bias in drift detection'
            ]
        }
        
        # Add feature drift if data provided
        if baseline_features is not None and current_features is not None:
            report['feature_drift'] = self.detect_feature_drift(baseline_features, current_features)
        
        # Add prediction drift if data provided
        if baseline_predictions is not None and current_predictions is not None:
            report['prediction_drift'] = self.detect_prediction_drift(baseline_predictions, current_predictions)
        
        # Overall health assessment
        alerts = []
        if report['performance_drift']['drift_detected']:
            alerts.append({
                'type': 'performance_drift',
                'severity': report['performance_drift']['alert_severity'],
                'message': 'Model performance has degraded significantly'
            })
        
        if 'feature_drift' in report and report['feature_drift']['drift_detected']:
            alerts.append({
                'type': 'feature_drift',
                'severity': AlertSeverity.WARNING.value,
                'message': f"Feature drift detected in {report['feature_drift']['features_with_drift']} features"
            })
        
        if 'prediction_drift' in report and report['prediction_drift']['drift_detected']:
            alerts.append({
                'type': 'prediction_drift',
                'severity': report['prediction_drift']['severity'],
                'message': 'Prediction distribution has shifted significantly'
            })
        
        report['overall_health'] = 'healthy' if not alerts else 'degraded'
        report['alerts'] = alerts
        report['recommendation'] = self._generate_recommendation(alerts)
        
        logger.info(f"Monitoring report generated for {self.model_name}")
        return report
    
    def _generate_recommendation(self, alerts: List[Dict[str, Any]]) -> str:
        """Generate recommendation based on alerts.
        
        Args:
            alerts: List of alerts
        
        Returns:
            Recommendation string
        """
        if not alerts:
            return "Model is performing within expected parameters. Continue regular monitoring."
        
        critical_alerts = [a for a in alerts if a['severity'] == AlertSeverity.CRITICAL.value]
        
        if critical_alerts:
            return "CRITICAL: Model requires immediate attention. Consider retraining or investigation."
        
        return "WARNING: Model shows signs of degradation. Monitor closely and consider retraining if trend continues."
