"""Feature parity validation for batch vs stream consistency.

This module provides feature parity validation capabilities for the banking analytics
platform, validating consistency between batch and streaming features.

Assumptions:
- Batch features are retrieved from PostgreSQL
- Streaming features are retrieved from Redis
- Parity is validated using statistical tests (KS test, t-test)

Limitations:
- Parity validation requires historical data for comparison
- Statistical tests may have false positives/negatives
- No support for time-series feature parity

Fairness Considerations:
- Parity thresholds should be validated across demographic groups
- Monitor parity failures across customer segments for bias
- Ensure parity validation doesn't mask systematic errors
"""

from datetime import datetime, timezone, date, timedelta
from typing import Dict, Any, Optional, List, Tuple
from collections import defaultdict
from dataclasses import dataclass
import logging
import numpy as np
from scipy import stats

from src.streaming.config import StreamingConfig
from src.streaming.features.feature_store import FeatureStore

logger = logging.getLogger(__name__)


@dataclass
class DriftReport:
    """Feature drift report."""
    feature_name: str
    drift_detected: bool
    drift_magnitude: float
    drift_direction: str  # 'increase', 'decrease', 'none'
    batch_mean: float
    stream_mean: float
    batch_std: float
    stream_std: float
    p_value: float
    timestamp: datetime


@dataclass
class ReconciliationAction:
    """Reconciliation action record."""
    customer_key: str
    feature_name: str
    action_type: str  # 'sync_to_batch', 'sync_to_stream', 'flag_for_review'
    reason: str
    batch_value: Any
    stream_value: Any
    resolved_value: Any
    timestamp: datetime


class FeatureDriftDetector:
    """Detect feature drift between batch and streaming pipelines."""
    
    def __init__(
        self,
        window_size: int = 1000,
        drift_threshold: float = 0.1,
        statistical_threshold: float = 0.05
    ):
        """Initialize drift detector.
        
        Args:
            window_size: Number of samples for drift detection
            drift_threshold: Threshold for drift magnitude
            statistical_threshold: P-value threshold for statistical tests
        """
        self.window_size = window_size
        self.drift_threshold = drift_threshold
        self.statistical_threshold = statistical_threshold
        self.history = defaultdict(list)
    
    def detect_drift(
        self,
        feature_name: str,
        batch_value: float,
        stream_value: float,
        timestamp: Optional[datetime] = None
    ) -> DriftReport:
        """Detect drift for a single feature value.
        
        Args:
            feature_name: Feature name
            batch_value: Batch feature value
            stream_value: Streaming feature value
            timestamp: Event timestamp
        
        Returns:
            Drift report
        """
        timestamp = timestamp or datetime.now(timezone.utc).replace(tzinfo=None)
        
        # Add to history
        self.history[feature_name].append({
            'batch': batch_value,
            'stream': stream_value,
            'timestamp': timestamp
        })
        
        # Keep window size
        if len(self.history[feature_name]) > self.window_size:
            self.history[feature_name].pop(0)
        
        # Calculate statistics
        batch_values = [h['batch'] for h in self.history[feature_name]]
        stream_values = [h['stream'] for h in self.history[feature_name]]
        
        batch_mean = np.mean(batch_values)
        stream_mean = np.mean(stream_values)
        batch_std = np.std(batch_values)
        stream_std = np.std(stream_values)
        
        # Calculate drift magnitude
        if batch_std > 0:
            drift_magnitude = abs(batch_mean - stream_mean) / batch_std
        else:
            drift_magnitude = 0.0
        
        # Determine drift direction
        if stream_mean > batch_mean:
            drift_direction = 'increase'
        elif stream_mean < batch_mean:
            drift_direction = 'decrease'
        else:
            drift_direction = 'none'
        
        # Statistical test
        if len(batch_values) >= 30:
            statistic, p_value = stats.ttest_ind(batch_values, stream_values)
        else:
            statistic, p_value = 0.0, 1.0
        
        # Determine if drift detected
        drift_detected = (
            drift_magnitude > self.drift_threshold or
            p_value < self.statistical_threshold
        )
        
        return DriftReport(
            feature_name=feature_name,
            drift_detected=drift_detected,
            drift_magnitude=drift_magnitude,
            drift_direction=drift_direction,
            batch_mean=batch_mean,
            stream_mean=stream_mean,
            batch_std=batch_std,
            stream_std=stream_std,
            p_value=p_value,
            timestamp=timestamp
        )
    
    def get_drift_summary(self) -> Dict[str, Any]:
        """Get summary of drift across all features.
        
        Returns:
            Drift summary dictionary
        """
        summary = {
            'features_monitored': len(self.history),
            'features_with_drift': 0,
            'by_feature': {}
        }
        
        for feature_name, history in self.history.items():
            if not history:
                continue
            
            batch_values = [h['batch'] for h in history]
            stream_values = [h['stream'] for h in history]
            
            batch_mean = np.mean(batch_values)
            stream_mean = np.mean(stream_values)
            batch_std = np.std(batch_values)
            
            if batch_std > 0:
                drift_magnitude = abs(batch_mean - stream_mean) / batch_std
            else:
                drift_magnitude = 0.0
            
            has_drift = drift_magnitude > self.drift_threshold
            
            if has_drift:
                summary['features_with_drift'] += 1
            
            summary['by_feature'][feature_name] = {
                'drift_magnitude': drift_magnitude,
                'has_drift': has_drift,
                'sample_count': len(history)
            }
        
        return summary


class FeatureReconciler:
    """Reconcile differences between batch and streaming features."""
    
    def __init__(
        self,
        feature_store: FeatureStore,
        auto_sync: bool = False,
        sync_threshold: float = 0.05
    ):
        """Initialize feature reconciler.
        
        Args:
            feature_store: Redis feature store
            auto_sync: Whether to automatically sync features
            sync_threshold: Threshold for automatic sync
        """
        self.feature_store = feature_store
        self.auto_sync = auto_sync
        self.sync_threshold = sync_threshold
        self.reconciliation_history = []
    
    def reconcile_feature(
        self,
        customer_key: str,
        feature_name: str,
        batch_value: Any,
        stream_value: Any,
        action: str = 'auto'
    ) -> ReconciliationAction:
        """Reconcile a single feature.
        
        Args:
            customer_key: Customer key
            feature_name: Feature name
            batch_value: Batch feature value
            stream_value: Streaming feature value
            action: Reconciliation action type
        
        Returns:
            Reconciliation action record
        """
        timestamp = datetime.now(timezone.utc).replace(tzinfo=None)
        
        # Determine action if auto
        if action == 'auto':
            action = self._determine_action(batch_value, stream_value)
        
        # Execute action
        resolved_value = None
        reason = ""
        
        if action == 'sync_to_batch':
            # Update streaming feature to match batch
            self.feature_store.store_feature(
                entity_key=customer_key,
                feature_name=feature_name,
                feature_value=batch_value
            )
            resolved_value = batch_value
            reason = "Streaming feature synced to batch value"
        
        elif action == 'sync_to_stream':
            # Keep streaming value (batch is stale)
            resolved_value = stream_value
            reason = "Streaming value retained (batch is stale)"
        
        elif action == 'flag_for_review':
            # Flag for manual review
            resolved_value = stream_value
            reason = "Significant difference flagged for manual review"
        
        # Record action
        action_record = ReconciliationAction(
            customer_key=customer_key,
            feature_name=feature_name,
            action_type=action,
            reason=reason,
            batch_value=batch_value,
            stream_value=stream_value,
            resolved_value=resolved_value,
            timestamp=timestamp
        )
        
        self.reconciliation_history.append(action_record)
        
        logger.info(
            f"Reconciled {feature_name} for {customer_key}: "
            f"action={action}, reason={reason}"
        )
        
        return action_record
    
    def _determine_action(self, batch_value: Any, stream_value: Any) -> str:
        """Determine reconciliation action automatically.
        
        Args:
            batch_value: Batch feature value
            stream_value: Streaming feature value
        
        Returns:
            Action type
        """
        # Handle numeric values
        if isinstance(batch_value, (int, float)) and isinstance(stream_value, (int, float)):
            if batch_value != 0:
                rel_diff = abs(batch_value - stream_value) / abs(batch_value)
            else:
                rel_diff = 0.0
            
            if rel_diff < self.sync_threshold:
                return 'sync_to_batch'
            elif rel_diff > self.sync_threshold * 2:
                return 'flag_for_review'
            else:
                return 'sync_to_stream'
        
        # Handle categorical values
        elif batch_value == stream_value:
            return 'sync_to_batch'
        else:
            return 'flag_for_review'
    
    def batch_reconcile(
        self,
        batch_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Reconcile features for a batch of customers.
        
        Args:
            batch_data: List of customer data with batch and stream features
        
        Returns:
            Reconciliation summary
        """
        summary = {
            'total_customers': len(batch_data),
            'total_actions': 0,
            'actions_by_type': defaultdict(int),
            'actions': []
        }
        
        for customer_data in batch_data:
            customer_key = customer_data.get('customer_key')
            batch_features = customer_data.get('batch_features', {})
            stream_features = customer_data.get('stream_features', {})
            
            for feature_name in set(batch_features.keys()) | set(stream_features.keys()):
                batch_value = batch_features.get(feature_name)
                stream_value = stream_features.get(feature_name)
                
                if batch_value is None or stream_value is None:
                    continue
                
                action_record = self.reconcile_feature(
                    customer_key=customer_key,
                    feature_name=feature_name,
                    batch_value=batch_value,
                    stream_value=stream_value,
                    action='auto'
                )
                
                summary['total_actions'] += 1
                summary['actions_by_type'][action_record.action_type] += 1
                summary['actions'].append(action_record)
        
        return dict(summary)
    
    def get_reconciliation_history(
        self,
        customer_key: Optional[str] = None,
        feature_name: Optional[str] = None,
        since: Optional[datetime] = None
    ) -> List[ReconciliationAction]:
        """Get reconciliation history with optional filters.
        
        Args:
            customer_key: Optional customer key filter
            feature_name: Optional feature name filter
            since: Optional timestamp filter
        
        Returns:
            Filtered reconciliation history
        """
        filtered = self.reconciliation_history
        
        if customer_key:
            filtered = [a for a in filtered if a.customer_key == customer_key]
        
        if feature_name:
            filtered = [a for a in filtered if a.feature_name == feature_name]
        
        if since:
            filtered = [a for a in filtered if a.timestamp >= since]
        
        return filtered


class FeatureParityChecker:
    """Feature parity checker for batch vs stream validation.
    
    This checker validates consistency between batch and streaming features
    to ensure the real-time pipeline produces equivalent results to the
    batch pipeline.
    
    Key Features:
    - Compares batch vs streaming features
    - Performs statistical tests (KS test, t-test)
    - Generates parity reports
    - Configurable tolerance thresholds
    - Tracks parity history
    """
    
    # Default tolerance thresholds
    DEFAULT_TOLERANCES = {
        'absolute_tolerance': 0.01,  # Absolute difference
        'relative_tolerance': 0.05,  # 5% relative difference
        'ks_test_p_value': 0.05,  # KS test p-value threshold
        't_test_p_value': 0.05,  # t-test p-value threshold
    }
    
    def __init__(
        self,
        config: StreamingConfig,
        feature_store: FeatureStore,
        tolerances: Optional[Dict[str, float]] = None
    ):
        """Initialize feature parity checker.
        
        Args:
            config: Streaming configuration
            feature_store: Redis feature store for streaming features
            tolerances: Custom tolerance thresholds
        """
        self.config = config
        self.feature_store = feature_store
        self.tolerances = tolerances or self.DEFAULT_TOLERANCES
    
    def check_feature_parity(
        self,
        customer_key: str,
        batch_features: Dict[str, Any],
        stream_features: Dict[str, Any],
        feature_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Check parity between batch and streaming features.
        
        Args:
            customer_key: Customer identifier
            batch_features: Features from batch pipeline
            stream_features: Features from streaming pipeline
            feature_names: List of features to check (None = all)
        
        Returns:
            Parity report dictionary
        """
        logger.debug(f"Checking feature parity for customer {customer_key}")
        
        # Determine features to check
        if feature_names is None:
            feature_names = list(set(batch_features.keys()) & set(stream_features.keys()))
        
        parity_results = []
        all_passed = True
        
        for feature_name in feature_names:
            batch_value = batch_features.get(feature_name)
            stream_value = stream_features.get(feature_name)
            
            if batch_value is None or stream_value is None:
                logger.warning(f"Feature {feature_name} missing in one pipeline")
                continue
            
            # Check parity
            result = self._check_single_feature_parity(
                feature_name, batch_value, stream_value
            )
            parity_results.append(result)
            
            if not result['passed']:
                all_passed = False
        
        return {
            'customer_key': customer_key,
            'checked_at': datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
            'features_checked': len(parity_results),
            'features_passed': sum(1 for r in parity_results if r['passed']),
            'all_passed': all_passed,
            'results': parity_results,
            'tolerances': self.tolerances
        }
    
    def check_batch_parity(
        self,
        batch_data: List[Dict[str, Any]],
        reconciliation_date: date
    ) -> Dict[str, Any]:
        """Check parity for a batch of customers.
        
        Args:
            batch_data: List of customer data with batch and stream features
            reconciliation_date: Date of reconciliation
        
        Returns:
            Batch parity report
        """
        logger.info(f"Checking batch parity for {len(batch_data)} customers")
        
        all_results = []
        summary = {
            'total_customers': len(batch_data),
            'total_features_checked': 0,
            'total_features_passed': 0,
            'customers_with_failures': 0,
            'by_feature': {}
        }
        
        for customer_data in batch_data:
            customer_key = customer_data.get('customer_key')
            batch_features = customer_data.get('batch_features', {})
            stream_features = customer_data.get('stream_features', {})
            
            # Check parity
            parity_report = self.check_feature_parity(
                customer_key, batch_features, stream_features
            )
            
            all_results.append(parity_report)
            
            # Update summary
            summary['total_features_checked'] += parity_report['features_checked']
            summary['total_features_passed'] += parity_report['features_passed']
            
            if not parity_report['all_passed']:
                summary['customers_with_failures'] += 1
            
            # Track by feature
            for result in parity_report['results']:
                feature_name = result['feature_name']
                if feature_name not in summary['by_feature']:
                    summary['by_feature'][feature_name] = {
                        'checked': 0,
                        'passed': 0,
                        'failed': 0
                    }
                
                summary['by_feature'][feature_name]['checked'] += 1
                if result['passed']:
                    summary['by_feature'][feature_name]['passed'] += 1
                else:
                    summary['by_feature'][feature_name]['failed'] += 1
        
        # Calculate overall pass rate
        if summary['total_features_checked'] > 0:
            summary['overall_pass_rate'] = (
                summary['total_features_passed'] / summary['total_features_checked']
            )
        else:
            summary['overall_pass_rate'] = 0.0
        
        # Determine status
        if summary['overall_pass_rate'] >= 0.95:
            status = 'pass'
        elif summary['overall_pass_rate'] >= 0.90:
            status = 'warning'
        else:
            status = 'fail'
        
        return {
            'reconciliation_date': reconciliation_date.isoformat(),
            'status': status,
            'summary': summary,
            'customer_results': all_results,
            'checked_at': datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
        }
    
    def _check_single_feature_parity(
        self,
        feature_name: str,
        batch_value: Any,
        stream_value: Any
    ) -> Dict[str, Any]:
        """Check parity for a single feature.
        
        Args:
            feature_name: Feature name
            batch_value: Batch feature value
            stream_value: Streaming feature value
        
        Returns:
            Parity result dictionary
        """
        result = {
            'feature_name': feature_name,
            'batch_value': batch_value,
            'stream_value': stream_value,
            'passed': True,
            'absolute_difference': None,
            'relative_difference': None,
            'ks_test_p_value': None,
            't_test_p_value': None,
            'failure_reason': None
        }
        
        # Handle numeric values
        if isinstance(batch_value, (int, float)) and isinstance(stream_value, (int, float)):
            # Calculate absolute difference
            abs_diff = abs(batch_value - stream_value)
            result['absolute_difference'] = abs_diff
            
            # Calculate relative difference
            if batch_value != 0:
                rel_diff = abs_diff / abs(batch_value)
                result['relative_difference'] = rel_diff
            else:
                rel_diff = 0.0
                result['relative_difference'] = 0.0
            
            # Check absolute tolerance
            if abs_diff > self.tolerances['absolute_tolerance']:
                result['passed'] = False
                result['failure_reason'] = f"Absolute difference {abs_diff} exceeds tolerance"
            
            # Check relative tolerance
            if rel_diff > self.tolerances['relative_tolerance']:
                result['passed'] = False
                result['failure_reason'] = f"Relative difference {rel_diff:.2%} exceeds tolerance"
        
        # Handle categorical values
        elif batch_value != stream_value:
            result['passed'] = False
            result['failure_reason'] = f"Categorical mismatch: {batch_value} vs {stream_value}"
        
        return result
    
    def perform_statistical_test(
        self,
        batch_values: List[float],
        stream_values: List[float],
        test_type: str = 'ks'
    ) -> Dict[str, Any]:
        """Perform statistical test on feature distributions.
        
        Args:
            batch_values: Batch feature values
            stream_values: Streaming feature values
            test_type: Type of test (ks, ttest)
        
        Returns:
            Statistical test result
        """
        result = {
            'test_type': test_type,
            'p_value': None,
            'statistic': None,
            'passed': True,
            'failure_reason': None
        }
        
        try:
            if test_type == 'ks':
                # Kolmogorov-Smirnov test
                statistic, p_value = stats.ks_2samp(batch_values, stream_values)
                result['statistic'] = float(statistic)
                result['p_value'] = float(p_value)
                
                if p_value < self.tolerances['ks_test_p_value']:
                    result['passed'] = False
                    result['failure_reason'] = f"KS test p-value {p_value} below threshold"
            
            elif test_type == 'ttest':
                # Two-sample t-test
                statistic, p_value = stats.ttest_ind(batch_values, stream_values)
                result['statistic'] = float(statistic)
                result['p_value'] = float(p_value)
                
                if p_value < self.tolerances['t_test_p_value']:
                    result['passed'] = False
                    result['failure_reason'] = f"t-test p-value {p_value} below threshold"
        
        except Exception as e:
            logger.error(f"Statistical test failed: {e}")
            result['passed'] = False
            result['failure_reason'] = f"Test failed: {str(e)}"
        
        return result
