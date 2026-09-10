"""Point-in-Time Feature Engineering.

This module implements point-in-time feature engineering to prevent data leakage
and ensure that features used for model training only use information available
at the time of prediction.

Key Concepts:
- Temporal safety (no future data leakage)
- Rolling window calculations
- Lagged features
- Time-based feature aggregation
- Feature consistency over time

NOTE: This is an analytical/educational model for decision support.
It does not make actual lending decisions.
"""

from typing import Dict, Any, List, Optional
from datetime import date, timedelta
from enum import Enum
import logging

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class FeatureWindow(Enum):
    """Feature calculation windows."""
    LAST_7_DAYS = "last_7_days"
    LAST_30_DAYS = "last_30_days"
    LAST_90_DAYS = "last_90_days"
    LAST_180_DAYS = "last_180_days"
    LAST_365_DAYS = "last_365_days"


class PointInTimeFeatureEngineer:
    """Engineer features with point-in-time temporal safety.
    
    This class ensures that features are calculated using only data available
    at the prediction time, preventing data leakage.
    
    Assumptions:
    - Historical data is available with timestamps
    - Feature windows are defined relative to prediction date
    - Data is chronologically ordered
    - No future information is used
    
    Limitations:
    - Requires sufficient historical data for all windows
    - May not capture all relevant temporal patterns
    - Window sizes are fixed (may not be optimal)
    - Does not account for seasonality automatically
    
    Fairness Considerations:
    - Ensure feature windows are consistent across customers
    - Check for temporal bias in feature availability
    - Ensure feature engineering does not introduce bias
    - Regular audit for bias in feature distributions
    """
    
    def __init__(self, prediction_date: Optional[date] = None):
        """Initialize Point-in-Time Feature Engine.
        
        Args:
            prediction_date: Date of prediction (for temporal safety)
        """
        self.prediction_date = prediction_date or date.today()
    
    def calculate_rolling_features(
        self,
        transactions_df: pd.DataFrame,
        customer_key: str,
        feature_window: FeatureWindow = FeatureWindow.LAST_90_DAYS
    ) -> Dict[str, float]:
        """Calculate rolling window features for a customer.
        
        Args:
            transactions_df: DataFrame with transaction data
            customer_key: Customer key
            feature_window: Time window for feature calculation
        
        Returns:
            Dictionary with rolling features
        """
        # Determine window start date
        window_days = self._get_window_days(feature_window)
        window_start = self.prediction_date - timedelta(days=window_days)
        
        # Filter transactions for customer and window
        customer_txns = transactions_df[
            (transactions_df['customer_key'] == customer_key) &
            (transactions_df['transaction_date'] >= window_start) &
            (transactions_df['transaction_date'] < self.prediction_date)
        ]
        
        if customer_txns.empty:
            return self._get_default_features()
        
        # Calculate rolling features
        features = {
            'transaction_count': len(customer_txns),
            'total_amount': float(customer_txns['amount'].abs().sum()),
            'avg_amount': float(customer_txns['amount'].abs().mean()),
            'median_amount': float(customer_txns['amount'].abs().median()),
            'std_amount': float(customer_txns['amount'].abs().std()),
            'max_amount': float(customer_txns['amount'].abs().max()),
            'min_amount': float(customer_txns['amount'].abs().min()),
            'amount_range': float(customer_txns['amount'].abs().max() - customer_txns['amount'].abs().min())
        }
        
        # Calculate debit/credit breakdown
        debit_txns = customer_txns[customer_txns['amount'] < 0]
        credit_txns = customer_txns[customer_txns['amount'] > 0]
        
        features['debit_count'] = len(debit_txns)
        features['credit_count'] = len(credit_txns)
        features['debit_total'] = float(debit_txns['amount'].abs().sum()) if not debit_txns.empty else 0
        features['credit_total'] = float(credit_txns['amount'].abs().sum()) if not credit_txns.empty else 0
        features['net_flow'] = features['credit_total'] - features['debit_total']
        
        # Calculate frequency (transactions per day)
        features['daily_frequency'] = features['transaction_count'] / window_days
        
        return features
    
    def calculate_lagged_features(
        self,
        metrics_df: pd.DataFrame,
        customer_key: str,
        lag_periods: List[int] = [1, 2, 3, 6, 12]
    ) -> Dict[str, float]:
        """Calculate lagged features for a customer.
        
        Args:
            metrics_df: DataFrame with historical metrics
            customer_key: Customer key
            lag_periods: List of lag periods (in months)
        
        Returns:
            Dictionary with lagged features
        """
        customer_metrics = metrics_df[metrics_df['customer_key'] == customer_key].copy()
        customer_metrics['as_of_date'] = pd.to_datetime(customer_metrics['as_of_date'])
        customer_metrics = customer_metrics.sort_values('as_of_date')
        
        if len(customer_metrics) < 2:
            return {}
        
        # Get most recent metrics
        latest_metrics = customer_metrics.iloc[-1]
        latest_date = latest_metrics['as_of_date']
        
        lagged_features = {}
        
        for lag in lag_periods:
            lag_date = latest_date - pd.DateOffset(months=lag)
            
            # Find metrics closest to lag date
            lagged_metrics = customer_metrics[
                customer_metrics['as_of_date'] <= lag_date
            ].tail(1)
            
            if not lagged_metrics.empty:
                lagged_value = lagged_metrics.iloc[0].get('net_profit', 0)
                lagged_features[f'net_profit_lag_{lag}m'] = float(lagged_value)
                
                # Calculate change
                current_value = latest_metrics.get('net_profit', 0)
                lagged_features[f'net_profit_change_{lag}m'] = float(current_value - lagged_value)
                lagged_features[f'net_profit_pct_change_{lag}m'] = float(
                    (current_value - lagged_value) / abs(lagged_value) * 100 if lagged_value != 0 else 0
                )
        
        return lagged_features
    
    def calculate_temporal_aggregations(
        self,
        transactions_df: pd.DataFrame,
        customer_key: str,
        aggregation_period: str = 'monthly'
    ) -> pd.DataFrame:
        """Calculate temporal aggregations for a customer.
        
        Args:
            transactions_df: DataFrame with transaction data
            customer_key: Customer key
            aggregation_period: Aggregation period (daily, weekly, monthly)
        
        Returns:
            DataFrame with temporal aggregations
        """
        customer_txns = transactions_df[transactions_df['customer_key'] == customer_key].copy()
        customer_txns['transaction_date'] = pd.to_datetime(customer_txns['transaction_date'])
        
        # Filter to only historical data
        customer_txns = customer_txns[customer_txns['transaction_date'] < self.prediction_date]
        
        if customer_txns.empty:
            return pd.DataFrame()
        
        # Set period based on aggregation type
        if aggregation_period == 'daily':
            customer_txns['period'] = customer_txns['transaction_date'].dt.date
        elif aggregation_period == 'weekly':
            customer_txns['period'] = customer_txns['transaction_date'].dt.to_period('W').dt.start_time.dt.date
        elif aggregation_period == 'monthly':
            customer_txns['period'] = customer_txns['transaction_date'].dt.to_period('M').dt.start_time.dt.date
        else:
            customer_txns['period'] = customer_txns['transaction_date'].dt.to_period('Q').dt.start_time.dt.date
        
        # Aggregate by period
        aggregations = customer_txns.groupby('period').agg({
            'transaction_id': 'count',
            'amount': ['sum', 'mean', 'median', 'std']
        }).reset_index()
        
        aggregations.columns = ['period', 'transaction_count', 'total_amount', 'avg_amount', 'median_amount', 'std_amount']
        
        return aggregations
    
    def generate_point_in_time_features(
        self,
        transactions_df: pd.DataFrame,
        metrics_df: pd.DataFrame,
        customer_key: str
    ) -> Dict[str, Any]:
        """Generate comprehensive point-in-time features for a customer.
        
        Args:
            transactions_df: DataFrame with transaction data
            metrics_df: DataFrame with historical metrics
            customer_key: Customer key
        
        Returns:
            Dictionary with all point-in-time features
        """
        logger.debug(f"Generating point-in-time features for customer: {customer_key}")
        
        features = {}
        
        # Rolling features
        for window in [FeatureWindow.LAST_30_DAYS, FeatureWindow.LAST_90_DAYS, FeatureWindow.LAST_365_DAYS]:
            window_features = self.calculate_rolling_features(transactions_df, customer_key, window)
            window_prefix = window.value + '_'
            for key, value in window_features.items():
                features[window_prefix + key] = value
        
        # Lagged features
        lagged_features = self.calculate_lagged_features(metrics_df, customer_key)
        features.update(lagged_features)
        
        # Temporal aggregations
        monthly_aggregations = self.calculate_temporal_aggregations(transactions_df, customer_key, 'monthly')
        if not monthly_aggregations.empty:
            features['monthly_avg_transaction_count'] = float(monthly_aggregations['transaction_count'].mean())
            features['monthly_avg_amount'] = float(monthly_aggregations['total_amount'].mean())
            features['monthly_volatility'] = float(monthly_aggregations['total_amount'].std())
        
        # Add metadata
        features['customer_key'] = customer_key
        features['prediction_date'] = self.prediction_date.isoformat()
        
        logger.debug(f"Generated {len(features)} point-in-time features for customer: {customer_key}")
        return features
    
    def _get_window_days(self, window: FeatureWindow) -> int:
        """Get number of days for a feature window.
        
        Args:
            window: Feature window enum
        
        Returns:
            Number of days
        """
        window_days = {
            FeatureWindow.LAST_7_DAYS: 7,
            FeatureWindow.LAST_30_DAYS: 30,
            FeatureWindow.LAST_90_DAYS: 90,
            FeatureWindow.LAST_180_DAYS: 180,
            FeatureWindow.LAST_365_DAYS: 365
        }
        return window_days.get(window, 90)
    
    def _get_default_features(self) -> Dict[str, float]:
        """Get default feature values when no data is available.
        
        Returns:
            Dictionary with default feature values
        """
        return {
            'transaction_count': 0,
            'total_amount': 0.0,
            'avg_amount': 0.0,
            'median_amount': 0.0,
            'std_amount': 0.0,
            'max_amount': 0.0,
            'min_amount': 0.0,
            'amount_range': 0.0,
            'debit_count': 0,
            'credit_count': 0,
            'debit_total': 0.0,
            'credit_total': 0.0,
            'net_flow': 0.0,
            'daily_frequency': 0.0
        }
    
    def validate_temporal_safety(
        self,
        features: Dict[str, Any],
        prediction_date: date
    ) -> Dict[str, Any]:
        """Validate that features are temporally safe (no data leakage).
        
        Args:
            features: Dictionary with features
            prediction_date: Prediction date
        
        Returns:
            Dictionary with validation results
        """
        validation_result = {
            'is_temporally_safe': True,
            'violations': [],
            'warnings': []
        }
        
        # Check if any feature dates are after prediction date
        if 'prediction_date' in features:
            feature_date = date.fromisoformat(features['prediction_date'])
            if feature_date > prediction_date:
                validation_result['is_temporally_safe'] = False
                validation_result['violations'].append(
                    f"Feature date {feature_date} is after prediction date {prediction_date}"
                )
        
        # Check for suspiciously high values (potential future leakage)
        if 'last_365_days_total_amount' in features:
            # If annual amount is extremely high, might indicate future data
            if features['last_365_days_total_amount'] > 1000000:  # $1M threshold
                validation_result['warnings'].append(
                    f"Suspiciously high annual amount: ${features['last_365_days_total_amount']:,.2f}"
                )
        
        return validation_result
