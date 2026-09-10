"""Batch vs live reconciliation engine.

This module provides reconciliation capabilities for the banking analytics
platform, validating consistency between batch and live data.

Assumptions:
- Batch data is retrieved from PostgreSQL
- Live data is retrieved from streaming pipeline (Redis + PostgreSQL)
- Reconciliation is performed daily for previous day

Limitations:
- Reconciliation requires historical data for comparison
- Discrepancy investigation may require manual review
- No support for automatic discrepancy resolution

Fairness Considerations:
- Reconciliation thresholds should be validated across demographic groups
- Monitor discrepancy rates across customer segments for bias
- Ensure reconciliation doesn't mask systematic errors
"""

from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional, List, Tuple
from collections import defaultdict
import logging
import uuid

from src.streaming.config import StreamingConfig
from src.streaming.features.feature_store import FeatureStore

logger = logging.getLogger(__name__)


class ReconciliationEngine:
    """Batch vs live reconciliation engine.
    
    This engine validates consistency between batch and live (streaming)
    data to ensure the real-time pipeline produces equivalent results
    to the batch pipeline.
    
    Key Features:
    - Compares batch vs live event counts
    - Compares batch vs live feature values
    - Compares batch vs live predictions
    - Compares batch vs live alerts
    - Generates reconciliation reports
    - Tracks discrepancy history
    """
    
    # Default tolerance thresholds
    DEFAULT_TOLERANCES = {
        'count_tolerance': 0,  # Exact match required for counts
        'feature_absolute_tolerance': 0.01,
        'feature_relative_tolerance': 0.05,
        'prediction_absolute_tolerance': 0.1,
        'prediction_relative_tolerance': 0.10,
    }
    
    def __init__(
        self,
        config: StreamingConfig,
        feature_store: FeatureStore,
        tolerances: Optional[Dict[str, float]] = None
    ):
        """Initialize reconciliation engine.
        
        Args:
            config: Streaming configuration
            feature_store: Redis feature store for live data
            tolerances: Custom tolerance thresholds
        """
        self.config = config
        self.feature_store = feature_store
        self.tolerances = tolerances or self.DEFAULT_TOLERANCES
    
    def reconcile_event_counts(
        self,
        reconciliation_date: date,
        batch_count: int,
        live_count: int
    ) -> Dict[str, Any]:
        """Reconcile event counts between batch and live.
        
        Args:
            reconciliation_date: Date of reconciliation
            batch_count: Event count from batch pipeline
            live_count: Event count from live pipeline
        
        Returns:
            Reconciliation result
        """
        logger.debug(f"Reconciling event counts for {reconciliation_date}")
        
        difference = batch_count - live_count
        difference_percentage = (
            abs(difference) / batch_count * 100 if batch_count > 0 else 0
        )
        
        # Determine status
        if difference == 0:
            status = 'pass'
        elif abs(difference) <= self.tolerances['count_tolerance']:
            status = 'pass'
        else:
            status = 'fail'
        
        return {
            'reconciliation_type': 'event_counts',
            'reconciliation_date': reconciliation_date.isoformat(),
            'batch_count': batch_count,
            'live_count': live_count,
            'difference': difference,
            'difference_percentage': difference_percentage,
            'status': status,
            'checked_at': datetime.utcnow().isoformat()
        }
    
    def reconcile_features(
        self,
        reconciliation_date: date,
        batch_features: Dict[str, Any],
        live_features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Reconcile feature values between batch and live.
        
        Args:
            reconciliation_date: Date of reconciliation
            batch_features: Features from batch pipeline
            live_features: Features from live pipeline
        
        Returns:
            Reconciliation result
        """
        logger.debug(f"Reconciling features for {reconciliation_date}")
        
        feature_results = []
        all_passed = True
        
        # Get common features
        common_features = set(batch_features.keys()) & set(live_features.keys())
        
        for feature_name in common_features:
            batch_value = batch_features[feature_name]
            live_value = live_features[feature_name]
            
            result = self._reconcile_single_feature(
                feature_name, batch_value, live_value
            )
            feature_results.append(result)
            
            if not result['passed']:
                all_passed = False
        
        # Determine overall status
        if all_passed:
            status = 'pass'
        elif sum(1 for r in feature_results if r['passed']) / len(feature_results) >= 0.9:
            status = 'warning'
        else:
            status = 'fail'
        
        return {
            'reconciliation_type': 'features',
            'reconciliation_date': reconciliation_date.isoformat(),
            'features_checked': len(feature_results),
            'features_passed': sum(1 for r in feature_results if r['passed']),
            'status': status,
            'results': feature_results,
            'checked_at': datetime.utcnow().isoformat()
        }
    
    def reconcile_predictions(
        self,
        reconciliation_date: date,
        batch_predictions: Dict[str, float],
        live_predictions: Dict[str, float]
    ) -> Dict[str, Any]:
        """Reconcile predictions between batch and live.
        
        Args:
            reconciliation_date: Date of reconciliation
            batch_predictions: Predictions from batch pipeline
            live_predictions: Predictions from live pipeline
        
        Returns:
            Reconciliation result
        """
        logger.debug(f"Reconciling predictions for {reconciliation_date}")
        
        prediction_results = []
        all_passed = True
        
        # Get common predictions
        common_keys = set(batch_predictions.keys()) & set(live_predictions.keys())
        
        for key in common_keys:
            batch_value = batch_predictions[key]
            live_value = live_predictions[key]
            
            result = self._reconcile_single_prediction(
                key, batch_value, live_value
            )
            prediction_results.append(result)
            
            if not result['passed']:
                all_passed = False
        
        # Determine overall status
        if all_passed:
            status = 'pass'
        elif sum(1 for r in prediction_results if r['passed']) / len(prediction_results) >= 0.9:
            status = 'warning'
        else:
            status = 'fail'
        
        return {
            'reconciliation_type': 'predictions',
            'reconciliation_date': reconciliation_date.isoformat(),
            'predictions_checked': len(prediction_results),
            'predictions_passed': sum(1 for r in prediction_results if r['passed']),
            'status': status,
            'results': prediction_results,
            'checked_at': datetime.utcnow().isoformat()
        }
    
    def reconcile_alerts(
        self,
        reconciliation_date: date,
        batch_alerts: List[Dict[str, Any]],
        live_alerts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Reconcile alerts between batch and live.
        
        Args:
            reconciliation_date: Date of reconciliation
            batch_alerts: Alerts from batch pipeline
            live_alerts: Alerts from live pipeline
        
        Returns:
            Reconciliation result
        """
        logger.debug(f"Reconciling alerts for {reconciliation_date}")
        
        batch_count = len(batch_alerts)
        live_count = len(live_alerts)
        
        # Compare counts
        count_result = self.reconcile_event_counts(
            reconciliation_date, batch_count, live_count
        )
        
        # Compare alert types
        batch_types = set(a.get('alert_type') for a in batch_alerts)
        live_types = set(a.get('alert_type') for a in live_alerts)
        
        missing_types = batch_types - live_types
        extra_types = live_types - batch_types
        
        # Determine status
        if count_result['status'] == 'pass' and not missing_types and not extra_types:
            status = 'pass'
        elif count_result['status'] == 'warning' or missing_types or extra_types:
            status = 'warning'
        else:
            status = 'fail'
        
        return {
            'reconciliation_type': 'alerts',
            'reconciliation_date': reconciliation_date.isoformat(),
            'batch_count': batch_count,
            'live_count': live_count,
            'missing_alert_types': list(missing_types),
            'extra_alert_types': list(extra_types),
            'status': status,
            'checked_at': datetime.utcnow().isoformat()
        }
    
    def run_daily_reconciliation(
        self,
        reconciliation_date: date,
        batch_data: Dict[str, Any],
        live_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run full daily reconciliation.
        
        Args:
            reconciliation_date: Date of reconciliation
            batch_data: Batch data (counts, features, predictions, alerts)
            live_data: Live data (counts, features, predictions, alerts)
        
        Returns:
            Full reconciliation report
        """
        logger.info(f"Running daily reconciliation for {reconciliation_date}")
        
        reconciliation_id = str(uuid.uuid4())
        
        # Reconcile event counts
        count_result = self.reconcile_event_counts(
            reconciliation_date,
            batch_data.get('event_count', 0),
            live_data.get('event_count', 0)
        )
        
        # Reconcile features
        feature_result = self.reconcile_features(
            reconciliation_date,
            batch_data.get('features', {}),
            live_data.get('features', {})
        )
        
        # Reconcile predictions
        prediction_result = self.reconcile_predictions(
            reconciliation_date,
            batch_data.get('predictions', {}),
            live_data.get('predictions', {})
        )
        
        # Reconcile alerts
        alert_result = self.reconcile_alerts(
            reconciliation_date,
            batch_data.get('alerts', []),
            live_data.get('alerts', [])
        )
        
        # Determine overall status
        all_results = [count_result, feature_result, prediction_result, alert_result]
        failed_count = sum(1 for r in all_results if r['status'] == 'fail')
        warning_count = sum(1 for r in all_results if r['status'] == 'warning')
        
        if failed_count == 0 and warning_count == 0:
            overall_status = 'pass'
        elif failed_count == 0:
            overall_status = 'warning'
        else:
            overall_status = 'fail'
        
        report = {
            'reconciliation_id': reconciliation_id,
            'reconciliation_date': reconciliation_date.isoformat(),
            'overall_status': overall_status,
            'results': {
                'event_counts': count_result,
                'features': feature_result,
                'predictions': prediction_result,
                'alerts': alert_result
            },
            'summary': {
                'total_checks': len(all_results),
                'passed': sum(1 for r in all_results if r['status'] == 'pass'),
                'warnings': warning_count,
                'failed': failed_count
            },
            'checked_at': datetime.utcnow().isoformat()
        }
        
        # Store reconciliation result
        self._store_reconciliation_result(report)
        
        return report
    
    def _reconcile_single_feature(
        self,
        feature_name: str,
        batch_value: Any,
        live_value: Any
    ) -> Dict[str, Any]:
        """Reconcile a single feature.
        
        Args:
            feature_name: Feature name
            batch_value: Batch feature value
            live_value: Live feature value
        
        Returns:
            Feature reconciliation result
        """
        result = {
            'feature_name': feature_name,
            'batch_value': batch_value,
            'live_value': live_value,
            'passed': True,
            'absolute_difference': None,
            'relative_difference': None,
            'failure_reason': None
        }
        
        # Handle numeric values
        if isinstance(batch_value, (int, float)) and isinstance(live_value, (int, float)):
            abs_diff = abs(batch_value - live_value)
            result['absolute_difference'] = abs_diff
            
            if batch_value != 0:
                rel_diff = abs_diff / abs(batch_value)
                result['relative_difference'] = rel_diff
            else:
                rel_diff = 0.0
                result['relative_difference'] = 0.0
            
            # Check absolute tolerance
            if abs_diff > self.tolerances['feature_absolute_tolerance']:
                result['passed'] = False
                result['failure_reason'] = f"Absolute difference {abs_diff} exceeds tolerance"
            
            # Check relative tolerance
            if rel_diff > self.tolerances['feature_relative_tolerance']:
                result['passed'] = False
                result['failure_reason'] = f"Relative difference {rel_diff:.2%} exceeds tolerance"
        
        # Handle categorical values
        elif batch_value != live_value:
            result['passed'] = False
            result['failure_reason'] = f"Categorical mismatch: {batch_value} vs {live_value}"
        
        return result
    
    def _reconcile_single_prediction(
        self,
        key: str,
        batch_value: float,
        live_value: float
    ) -> Dict[str, Any]:
        """Reconcile a single prediction.
        
        Args:
            key: Prediction key (e.g., customer_id)
            batch_value: Batch prediction value
            live_value: Live prediction value
        
        Returns:
            Prediction reconciliation result
        """
        result = {
            'key': key,
            'batch_value': batch_value,
            'live_value': live_value,
            'passed': True,
            'absolute_difference': None,
            'relative_difference': None,
            'failure_reason': None
        }
        
        abs_diff = abs(batch_value - live_value)
        result['absolute_difference'] = abs_diff
        
        if batch_value != 0:
            rel_diff = abs_diff / abs(batch_value)
            result['relative_difference'] = rel_diff
        else:
            rel_diff = 0.0
            result['relative_difference'] = 0.0
        
        # Check absolute tolerance
        if abs_diff > self.tolerances['prediction_absolute_tolerance']:
            result['passed'] = False
            result['failure_reason'] = f"Absolute difference {abs_diff} exceeds tolerance"
        
        # Check relative tolerance
        if rel_diff > self.tolerances['prediction_relative_tolerance']:
            result['passed'] = False
            result['failure_reason'] = f"Relative difference {rel_diff:.2%} exceeds tolerance"
        
        return result
    
    def _store_reconciliation_result(self, report: Dict[str, Any]):
        """Store reconciliation result in Redis.
        
        Args:
            report: Reconciliation report
        """
        reconciliation_key = f"reconciliation:{report['reconciliation_date']}"
        
        import json
        report_json = json.dumps(report)
        
        # Store with TTL (90 days)
        ttl = 90 * 24 * 60 * 60
        self.feature_store.redis_client.setex(reconciliation_key, ttl, report_json)
    
    def get_reconciliation_result(
        self,
        reconciliation_date: date
    ) -> Optional[Dict[str, Any]]:
        """Get reconciliation result for a date.
        
        Args:
            reconciliation_date: Date of reconciliation
        
        Returns:
            Reconciliation report or None if not found
        """
        reconciliation_key = f"reconciliation:{reconciliation_date.isoformat()}"
        
        report_data = self.feature_store.redis_client.get(reconciliation_key)
        
        if report_data:
            import json
            return json.loads(report_data)
        
        return None


class DiscrepancyInvestigator:
    """Investigate reconciliation discrepancies."""
    
    def __init__(self, feature_store: FeatureStore):
        """Initialize discrepancy investigator.
        
        Args:
            feature_store: Redis feature store
        """
        self.feature_store = feature_store
        self.discrepancy_history = defaultdict(list)
    
    def investigate_discrepancy(
        self,
        reconciliation_report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Investigate discrepancies in reconciliation report.
        
        Args:
            reconciliation_report: Reconciliation report
        
        Returns:
            Investigation findings
        """
        findings = {
            'investigation_id': str(uuid.uuid4()),
            'reconciliation_id': reconciliation_report.get('reconciliation_id'),
            'investigated_at': datetime.utcnow().isoformat(),
            'discrepancies_found': [],
            'root_causes': [],
            'recommendations': []
        }
        
        # Check each reconciliation result
        results = reconciliation_report.get('results', {})
        
        for check_type, result in results.items():
            if result.get('status') in ['fail', 'warning']:
                discrepancy = {
                    'check_type': check_type,
                    'status': result.get('status'),
                    'details': result
                }
                findings['discrepancies_found'].append(discrepancy)
                
                # Analyze potential root causes
                root_cause = self._analyze_root_cause(check_type, result)
                if root_cause:
                    findings['root_causes'].append(root_cause)
        
        # Generate recommendations
        if findings['discrepancies_found']:
            findings['recommendations'] = self._generate_recommendations(
                findings['discrepancies_found']
            )
        
        # Store investigation
        self._store_investigation(findings)
        
        return findings
    
    def _analyze_root_cause(
        self,
        check_type: str,
        result: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Analyze potential root cause of discrepancy.
        
        Args:
            check_type: Type of check
            result: Check result
        
        Returns:
            Root cause analysis or None
        """
        if check_type == 'event_counts':
            if result.get('difference') > 0:
                return {
                    'type': 'missing_events',
                    'description': 'Live pipeline missing events present in batch',
                    'severity': 'high'
                }
            else:
                return {
                    'type': 'extra_events',
                    'description': 'Live pipeline has extra events not in batch',
                    'severity': 'medium'
                }
        
        elif check_type == 'features':
            failed_features = [
                r for r in result.get('results', [])
                if not r.get('passed')
            ]
            if failed_features:
                return {
                    'type': 'feature_drift',
                    'description': f'{len(failed_features)} features have discrepancies',
                    'severity': 'medium',
                    'affected_features': [f['feature_name'] for f in failed_features]
                }
        
        elif check_type == 'predictions':
            failed_predictions = [
                r for r in result.get('results', [])
                if not r.get('passed')
            ]
            if failed_predictions:
                return {
                    'type': 'prediction_drift',
                    'description': f'{len(failed_predictions)} predictions have discrepancies',
                    'severity': 'high'
                }
        
        return None
    
    def _generate_recommendations(
        self,
        discrepancies: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations for discrepancies.
        
        Args:
            discrepancies: List of discrepancies
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        for discrepancy in discrepancies:
            check_type = discrepancy.get('check_type')
            
            if check_type == 'event_counts':
                recommendations.append(
                    'Review event ingestion pipeline for missing or duplicate events'
                )
                recommendations.append(
                    'Check Kafka consumer offset management'
                )
            
            elif check_type == 'features':
                recommendations.append(
                    'Review feature engineering logic in streaming pipeline'
                )
                recommendations.append(
                    'Check feature calculation order and dependencies'
                )
            
            elif check_type == 'predictions':
                recommendations.append(
                    'Review model version consistency between batch and streaming'
                )
                recommendations.append(
                    'Check feature input to model for discrepancies'
                )
            
            elif check_type == 'alerts':
                recommendations.append(
                    'Review alert generation thresholds and logic'
                )
                recommendations.append(
                    'Check alert deduplication settings'
                )
        
        return list(set(recommendations))
    
    def _store_investigation(self, findings: Dict[str, Any]):
        """Store investigation findings.
        
        Args:
            findings: Investigation findings
        """
        investigation_key = f"investigation:{findings['investigation_id']}"
        
        import json
        findings_json = json.dumps(findings)
        
        ttl = 90 * 24 * 60 * 60  # 90 days
        self.feature_store.redis_client.setex(investigation_key, ttl, findings_json)


class ReconciliationTrendAnalyzer:
    """Analyze reconciliation trends over time."""
    
    def __init__(self, feature_store: FeatureStore):
        """Initialize trend analyzer.
        
        Args:
            feature_store: Redis feature store
        """
        self.feature_store = feature_store
    
    def analyze_trends(
        self,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Analyze reconciliation trends over date range.
        
        Args:
            start_date: Start date
            end_date: End date
        
        Returns:
            Trend analysis
        """
        reports = []
        current_date = start_date
        
        while current_date <= end_date:
            report = self._get_reconciliation_report(current_date)
            if report:
                reports.append(report)
            current_date += timedelta(days=1)
        
        if not reports:
            return {
                'error': 'No reconciliation reports found in date range'
            }
        
        # Calculate trend statistics
        total_reports = len(reports)
        passed = sum(1 for r in reports if r.get('overall_status') == 'pass')
        warnings = sum(1 for r in reports if r.get('overall_status') == 'warning')
        failed = sum(1 for r in reports if r.get('overall_status') == 'fail')
        
        # Analyze check type trends
        check_trends = defaultdict(lambda: {'pass': 0, 'warning': 0, 'fail': 0})
        
        for report in reports:
            results = report.get('results', {})
            for check_type, result in results.items():
                status = result.get('status')
                check_trends[check_type][status] += 1
        
        return {
            'analysis_period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'summary': {
                'total_reports': total_reports,
                'passed': passed,
                'warnings': warnings,
                'failed': failed,
                'pass_rate': passed / total_reports if total_reports > 0 else 0
            },
            ' trends_by_check_type': dict(check_trends),
            'analyzed_at': datetime.utcnow().isoformat()
        }
    
    def _get_reconciliation_report(self, reconciliation_date: date) -> Optional[Dict[str, Any]]:
        """Get reconciliation report for a date.
        
        Args:
            reconciliation_date: Date
        
        Returns:
            Reconciliation report or None
        """
        reconciliation_key = f"reconciliation:{reconciliation_date.isoformat()}"
        
        report_data = self.feature_store.redis_client.get(reconciliation_key)
        
        if report_data:
            import json
            return json.loads(report_data)
        
        return None
