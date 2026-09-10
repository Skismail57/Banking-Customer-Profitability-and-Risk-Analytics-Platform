"""Behavioral Change Detection.

This module detects significant changes in customer behavior patterns,
which can indicate:
- Financial distress
- Lifestyle changes
- Fraud potential
- Churn risk
- Cross-sell opportunities

Key Detection Methods:
- Transaction pattern changes
- Spending habit shifts
- Account activity changes
- Payment behavior modifications

NOTE: This is an analytical/educational model for decision support.
It does not make actual lending decisions.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import date, timedelta
from enum import Enum
import logging

import pandas as pd
import numpy as np
from scipy import stats
from scipy.signal import find_peaks

logger = logging.getLogger(__name__)


class ChangeType(Enum):
    """Types of behavioral changes."""
    SPENDING_INCREASE = "spending_increase"
    SPENDING_DECREASE = "spending_decrease"
    TRANSACTION_FREQUENCY_CHANGE = "transaction_frequency_change"
    MERCHANT_CATEGORY_SHIFT = "merchant_category_shift"
    PAYMENT_PATTERN_CHANGE = "payment_pattern_change"
    ACCOUNT_INACTIVITY = "account_inactivity"
    UNUSUAL_ACTIVITY = "unusual_activity"


class ChangeSeverity(Enum):
    """Severity levels for behavioral changes."""
    MINOR = "minor"
    MODERATE = "moderate"
    SIGNIFICANT = "significant"
    SEVERE = "severe"


class BehavioralChangeDetector:
    """Detect behavioral changes in customer patterns.
    
    This class uses statistical methods to detect significant changes
    in customer behavior over time.
    
    Assumptions:
    - Sufficient historical data is available for comparison
    - Behavioral patterns are relatively stable under normal conditions
    - Changes are statistically significant when they exceed thresholds
    
    Limitations:
    - May flag seasonal changes as anomalies
    - Requires sufficient data for statistical significance
    - Does not account for external events (holidays, promotions)
    - May miss gradual changes over long periods
    
    Fairness Considerations:
    - Behavioral baselines should be established per segment
    - Avoid penalizing legitimate lifestyle changes
    - Consider cultural differences in spending patterns
    - Regular audit for bias in change detection
    """
    
    def __init__(self, significance_level: float = 0.05):
        """Initialize Behavioral Change Detector.
        
        Args:
            significance_level: Statistical significance level for change detection
        """
        self.significance_level = significance_level
        
        # Change thresholds (configurable)
        self.thresholds = {
            'spending_change_threshold': 0.30,  # 30% change
            'frequency_change_threshold': 0.25,  # 25% change
            'inactivity_days_threshold': 30,  # 30 days of inactivity
            'merchant_category_change_threshold': 0.40  # 40% shift
        }
    
    def detect_spending_changes(
        self,
        transactions_df: pd.DataFrame,
        customer_column: str = "customer_key",
        date_column: str = "transaction_date",
        amount_column: str = "amount",
        window_days: int = 90
    ) -> pd.DataFrame:
        """Detect significant changes in spending patterns.
        
        Args:
            transactions_df: DataFrame with transaction data
            customer_column: Name of customer column
            date_column: Name of date column
            amount_column: Name of amount column
            window_days: Window for comparison (days)
        
        Returns:
            DataFrame with detected spending changes
        """
        transactions_df[date_column] = pd.to_datetime(transactions_df[date_column])
        transactions_df = transactions_df.sort_values(date_column)
        
        cutoff_date = transactions_df[date_column].max() - timedelta(days=window_days)
        
        changes = []
        
        for customer in transactions_df[customer_column].unique():
            customer_txns = transactions_df[transactions_df[customer_column] == customer]
            
            recent_txns = customer_txns[customer_txns[date_column] > cutoff_date]
            historical_txns = customer_txns[customer_txns[date_column] <= cutoff_date]
            
            if len(historical_txns) < 5 or len(recent_txns) < 5:
                continue
            
            # Calculate average spending
            recent_avg = recent_txns[amount_column].abs().mean()
            historical_avg = historical_txns[amount_column].abs().mean()
            
            if historical_avg == 0:
                continue
            
            # Calculate percent change
            percent_change = (recent_avg - historical_avg) / historical_avg
            
            # Perform statistical test
            stat, p_value = stats.ttest_ind(
                recent_txns[amount_column].abs(),
                historical_txns[amount_column].abs()
            )
            
            # Determine if change is significant
            if abs(percent_change) >= self.thresholds['spending_change_threshold'] and p_value < self.significance_level:
                change_type = ChangeType.SPENDING_INCREASE if percent_change > 0 else ChangeType.SPENDING_DECREASE
                severity = self._determine_change_severity(abs(percent_change), self.thresholds['spending_change_threshold'])
                
                changes.append({
                    'customer_key': customer,
                    'change_type': change_type.value,
                    'recent_avg': recent_avg,
                    'historical_avg': historical_avg,
                    'percent_change': percent_change,
                    'p_value': p_value,
                    'severity': severity.value,
                    'window_days': window_days
                })
        
        return pd.DataFrame(changes)
    
    def detect_frequency_changes(
        self,
        transactions_df: pd.DataFrame,
        customer_column: str = "customer_key",
        date_column: str = "transaction_date",
        window_days: int = 30
    ) -> pd.DataFrame:
        """Detect changes in transaction frequency.
        
        Args:
            transactions_df: DataFrame with transaction data
            customer_column: Name of customer column
            date_column: Name of date column
            window_days: Window for comparison (days)
        
        Returns:
            DataFrame with detected frequency changes
        """
        transactions_df[date_column] = pd.to_datetime(transactions_df[date_column])
        transactions_df = transactions_df.sort_values(date_column)
        
        cutoff_date = transactions_df[date_column].max() - timedelta(days=window_days)
        previous_cutoff = cutoff_date - timedelta(days=window_days)
        
        changes = []
        
        for customer in transactions_df[customer_column].unique():
            customer_txns = transactions_df[transactions_df[customer_column] == customer]
            
            recent_count = len(customer_txns[customer_txns[date_column] > cutoff_date])
            previous_count = len(customer_txns[
                (customer_txns[date_column] > previous_cutoff) & 
                (customer_txns[date_column] <= cutoff_date)
            ])
            
            if previous_count == 0:
                continue
            
            # Calculate percent change
            percent_change = (recent_count - previous_count) / previous_count
            
            # Determine if change is significant
            if abs(percent_change) >= self.thresholds['frequency_change_threshold']:
                change_type = ChangeType.TRANSACTION_FREQUENCY_CHANGE
                severity = self._determine_change_severity(abs(percent_change), self.thresholds['frequency_change_threshold'])
                
                changes.append({
                    'customer_key': customer,
                    'change_type': change_type.value,
                    'recent_count': recent_count,
                    'previous_count': previous_count,
                    'percent_change': percent_change,
                    'severity': severity.value,
                    'window_days': window_days
                })
        
        return pd.DataFrame(changes)
    
    def detect_merchant_category_shifts(
        self,
        transactions_df: pd.DataFrame,
        customer_column: str = "customer_key",
        category_column: str = "merchant_category",
        date_column: str = "transaction_date",
        window_days: int = 90
    ) -> pd.DataFrame:
        """Detect shifts in merchant category preferences.
        
        Args:
            transactions_df: DataFrame with transaction data
            customer_column: Name of customer column
            category_column: Name of merchant category column
            date_column: Name of date column
            window_days: Window for comparison (days)
        
        Returns:
            DataFrame with detected merchant category shifts
        """
        transactions_df[date_column] = pd.to_datetime(transactions_df[date_column])
        transactions_df = transactions_df.sort_values(date_column)
        
        cutoff_date = transactions_df[date_column].max() - timedelta(days=window_days)
        
        shifts = []
        
        for customer in transactions_df[customer_column].unique():
            customer_txns = transactions_df[transactions_df[customer_column] == customer]
            
            recent_txns = customer_txns[customer_txns[date_column] > cutoff_date]
            historical_txns = customer_txns[customer_txns[date_column] <= cutoff_date]
            
            if len(historical_txns) < 10 or len(recent_txns) < 10:
                continue
            
            # Calculate category distributions
            historical_dist = historical_txns[category_column].value_counts(normalize=True)
            recent_dist = recent_txns[category_column].value_counts(normalize=True)
            
            # Calculate distribution shift
            all_categories = set(historical_dist.index) | set(recent_dist.index)
            max_shift = 0
            
            for category in all_categories:
                hist_pct = historical_dist.get(category, 0)
                recent_pct = recent_dist.get(category, 0)
                shift = abs(recent_pct - hist_pct)
                max_shift = max(max_shift, shift)
            
            # Determine if shift is significant
            if max_shift >= self.thresholds['merchant_category_change_threshold']:
                severity = self._determine_change_severity(max_shift, self.thresholds['merchant_category_change_threshold'])
                
                shifts.append({
                    'customer_key': customer,
                    'change_type': ChangeType.MERCHANT_CATEGORY_SHIFT.value,
                    'max_shift': max_shift,
                    'historical_categories': list(historical_dist.index),
                    'recent_categories': list(recent_dist.index),
                    'severity': severity.value,
                    'window_days': window_days
                })
        
        return pd.DataFrame(shifts)
    
    def detect_account_inactivity(
        self,
        transactions_df: pd.DataFrame,
        customer_column: str = "customer_key",
        date_column: str = "transaction_date"
    ) -> pd.DataFrame:
        """Detect accounts with unusual inactivity.
        
        Args:
            transactions_df: DataFrame with transaction data
            customer_column: Name of customer column
            date_column: Name of date column
        
        Returns:
            DataFrame with inactive accounts
        """
        transactions_df[date_column] = pd.to_datetime(transactions_df[date_column])
        transactions_df = transactions_df.sort_values(date_column)
        
        max_date = transactions_df[date_column].max()
        inactivity_threshold = max_date - timedelta(days=self.thresholds['inactivity_days_threshold'])
        
        inactive = []
        
        for customer in transactions_df[customer_column].unique():
            customer_txns = transactions_df[transactions_df[customer_column] == customer]
            last_activity = customer_txns[date_column].max()
            
            if last_activity < inactivity_threshold:
                days_inactive = (max_date - last_activity).days
                severity = self._determine_inactivity_severity(days_inactive)
                
                inactive.append({
                    'customer_key': customer,
                    'change_type': ChangeType.ACCOUNT_INACTIVITY.value,
                    'last_activity_date': last_activity.isoformat(),
                    'days_inactive': days_inactive,
                    'severity': severity.value
                })
        
        return pd.DataFrame(inactive)
    
    def detect_unusual_activity(
        self,
        transactions_df: pd.DataFrame,
        customer_column: str = "customer_key",
        date_column: str = "transaction_date",
        amount_column: str = "amount",
        std_threshold: float = 3.0
    ) -> pd.DataFrame:
        """Detect unusual transaction activity using statistical methods.
        
        Args:
            transactions_df: DataFrame with transaction data
            customer_column: Name of customer column
            date_column: Name of date column
            amount_column: Name of amount column
            std_threshold: Standard deviation threshold for anomaly detection
        
        Returns:
            DataFrame with unusual transactions
        """
        transactions_df[date_column] = pd.to_datetime(transactions_df[date_column])
        transactions_df = transactions_df.sort_values(date_column)
        
        unusual = []
        
        for customer in transactions_df[customer_column].unique():
            customer_txns = transactions_df[transactions_df[customer_column] == customer].copy()
            
            if len(customer_txns) < 10:
                continue
            
            # Calculate z-scores
            amounts = customer_txns[amount_column].abs()
            mean_amount = amounts.mean()
            std_amount = amounts.std()
            
            if std_amount == 0:
                continue
            
            customer_txns['z_score'] = np.abs((amounts - mean_amount) / std_amount)
            
            # Find anomalies
            anomalies = customer_txns[customer_txns['z_score'] > std_threshold]
            
            for _, row in anomalies.iterrows():
                severity = self._determine_anomaly_severity(row['z_score'], std_threshold)
                
                unusual.append({
                    'customer_key': customer,
                    'change_type': ChangeType.UNUSUAL_ACTIVITY.value,
                    'transaction_id': row.get('transaction_id', 'unknown'),
                    'amount': row[amount_column],
                    'z_score': row['z_score'],
                    'mean_amount': mean_amount,
                    'severity': severity.value,
                    'transaction_date': row[date_column].isoformat()
                })
        
        return pd.DataFrame(unusual)
    
    def generate_behavioral_change_report(
        self,
        transactions_df: pd.DataFrame
    ) -> Dict[str, Any]:
        """Generate comprehensive behavioral change report.
        
        Args:
            transactions_df: DataFrame with transaction data
        
        Returns:
            Dictionary with comprehensive change report
        """
        logger.info("Generating behavioral change report")
        
        # Run all detection methods
        spending_changes = self.detect_spending_changes(transactions_df)
        frequency_changes = self.detect_frequency_changes(transactions_df)
        merchant_shifts = self.detect_merchant_category_shifts(transactions_df)
        inactive_accounts = self.detect_account_inactivity(transactions_df)
        unusual_activity = self.detect_unusual_activity(transactions_df)
        
        # Aggregate results
        report = {
            'summary': {
                'total_customers_analyzed': transactions_df['customer_key'].nunique(),
                'spending_changes_detected': len(spending_changes),
                'frequency_changes_detected': len(frequency_changes),
                'merchant_shifts_detected': len(merchant_shifts),
                'inactive_accounts_detected': len(inactive_accounts),
                'unusual_activity_detected': len(unusual_activity)
            },
            'spending_changes': spending_changes.to_dict('records') if not spending_changes.empty else [],
            'frequency_changes': frequency_changes.to_dict('records') if not frequency_changes.empty else [],
            'merchant_shifts': merchant_shifts.to_dict('records') if not merchant_shifts.empty else [],
            'inactive_accounts': inactive_accounts.to_dict('records') if not inactive_accounts.empty else [],
            'unusual_activity': unusual_activity.to_dict('records') if not unusual_activity.empty else [],
            'assumptions': [
                'Statistical significance level: ' + str(self.significance_level),
                'Spending change threshold: ' + str(self.thresholds['spending_change_threshold']),
                'Frequency change threshold: ' + str(self.thresholds['frequency_change_threshold']),
                'Inactivity threshold: ' + str(self.thresholds['inactivity_days_threshold']) + ' days'
            ],
            'limitations': [
                'May flag seasonal changes as anomalies',
                'Requires sufficient historical data',
                'Does not account for external events',
                'May miss gradual long-term changes'
            ]
        }
        
        logger.info("Behavioral change report generated")
        return report
    
    def _determine_change_severity(self, value: float, threshold: float) -> ChangeSeverity:
        """Determine severity of behavioral change.
        
        Args:
            value: Actual change value
            threshold: Threshold value
        
        Returns:
            ChangeSeverity enum
        """
        ratio = value / threshold
        
        if ratio >= 3.0:
            return ChangeSeverity.SEVERE
        elif ratio >= 2.0:
            return ChangeSeverity.SIGNIFICANT
        elif ratio >= 1.5:
            return ChangeSeverity.MODERATE
        else:
            return ChangeSeverity.MINOR
    
    def _determine_inactivity_severity(self, days_inactive: int) -> ChangeSeverity:
        """Determine severity of account inactivity.
        
        Args:
            days_inactive: Number of days inactive
        
        Returns:
            ChangeSeverity enum
        """
        if days_inactive >= 90:
            return ChangeSeverity.SEVERE
        elif days_inactive >= 60:
            return ChangeSeverity.SIGNIFICANT
        elif days_inactive >= 45:
            return ChangeSeverity.MODERATE
        else:
            return ChangeSeverity.MINOR
    
    def _determine_anomaly_severity(self, z_score: float, threshold: float) -> ChangeSeverity:
        """Determine severity of anomaly.
        
        Args:
            z_score: Z-score of anomaly
            threshold: Threshold z-score
        
        Returns:
            ChangeSeverity enum
        """
        ratio = z_score / threshold
        
        if ratio >= 3.0:
            return ChangeSeverity.SEVERE
        elif ratio >= 2.0:
            return ChangeSeverity.SIGNIFICANT
        elif ratio >= 1.5:
            return ChangeSeverity.MODERATE
        else:
            return ChangeSeverity.MINOR
