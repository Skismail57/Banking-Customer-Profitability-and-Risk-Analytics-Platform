"""Early Warning System.

This module implements an early warning system that identifies customers
at risk of deterioration before they reach critical risk levels.

Key Indicators:
- Credit utilization spikes
- Payment rate declines
- Balance accumulation
- Transaction pattern changes
- Risk score deterioration

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

from src.advanced_risk_analytics.base import RiskBase, RiskLevel

logger = logging.getLogger(__name__)


class WarningSeverity(Enum):
    """Severity levels for early warning signals."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EarlyWarningIndicators(RiskBase):
    """Identify early warning signals before high-risk state.
    
    This class implements a comprehensive early warning system that monitors
    multiple indicators to identify customers at risk of deterioration.
    
    Assumptions:
    - Historical data is available for trend analysis
    - Warning thresholds are based on historical patterns
    - Early indicators correlate with future risk events
    
    Limitations:
    - May generate false positives (customers flagged but don't deteriorate)
    - May miss false negatives (customers not flagged but deteriorate)
    - Thresholds may need calibration for different portfolios
    - Does not account for external economic factors
    
    Fairness Considerations:
    - Warning thresholds should be validated across demographic groups
    - Ensure equal false positive rates across segments
    - Regular audit for bias in warning signals
    - Provide context for warnings to avoid stereotyping
    """
    
    def __init__(self, thresholds: Optional[RiskThresholds] = None, as_of_date: Optional[date] = None):
        """Initialize Early Warning Indicators.
        
        Args:
            thresholds: Configurable risk thresholds
            as_of_date: As-of date for analysis
        """
        super().__init__(thresholds)
        self.as_of_date = as_of_date
        
        # Warning thresholds (configurable)
        self.thresholds = {
            'utilization_increase_threshold': 0.15,  # 15% increase
            'payment_decline_threshold': 0.10,  # 10% decline
            'balance_increase_threshold': 0.20,  # 20% increase
            'risk_score_decline_threshold': 0.10,  # 10% decline
            'transaction_volume_decline_threshold': 0.30  # 30% decline
        }
    
    def detect_early_warning_signals(
        self,
        df: pd.DataFrame,
        customer_column: str = "customer_key",
        date_column: str = "as_of_date",
        utilization_column: str = "credit_utilization",
        payment_rate_column: str = "on_time_payment_rate",
        balance_column: str = "exposure_amount"
    ) -> Dict[str, Any]:
        """Detect early warning signals for risk escalation.
        
        Args:
            df: DataFrame with customer data
            customer_column: Name of customer column
            date_column: Name of date column
            utilization_column: Name of utilization column
            payment_rate_column: Name of payment rate column
            balance_column: Name of balance column
        
        Returns:
            Dictionary with early warning signals
        """
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])
        df = df.sort_values([customer_column, date_column])
        
        warning_signals = []
        
        for customer in df[customer_column].unique():
            customer_df = df[df[customer_column] == customer]
            
            if len(customer_df) < 2:
                continue
            
            # Check utilization increase
            if utilization_column in customer_df.columns:
                utilization_change = (
                    customer_df[utilization_column].iloc[-1] - 
                    customer_df[utilization_column].iloc[0]
                )
                if utilization_change >= self.thresholds['utilization_increase_threshold']:
                    warning_signals.append({
                        "customer_key": customer,
                        "signal_type": "utilization_increase",
                        "value": utilization_change,
                        "threshold": self.thresholds['utilization_increase_threshold'],
                        "severity": self._determine_severity(utilization_change, self.thresholds['utilization_increase_threshold']),
                        "date": customer_df[date_column].iloc[-1].isoformat()
                    })
            
            # Check payment rate decline
            if payment_rate_column in customer_df.columns:
                payment_change = (
                    customer_df[payment_rate_column].iloc[0] - 
                    customer_df[payment_rate_column].iloc[-1]
                )
                if payment_change >= self.thresholds['payment_decline_threshold']:
                    warning_signals.append({
                        "customer_key": customer,
                        "signal_type": "payment_decline",
                        "value": payment_change,
                        "threshold": self.thresholds['payment_decline_threshold'],
                        "severity": self._determine_severity(payment_change, self.thresholds['payment_decline_threshold']),
                        "date": customer_df[date_column].iloc[-1].isoformat()
                    })
            
            # Check balance increase
            if balance_column in customer_df.columns:
                balance_change = (
                    customer_df[balance_column].iloc[-1] - 
                    customer_df[balance_column].iloc[0]
                ) / (abs(customer_df[balance_column].iloc[0]) + 1e-8)
                if balance_change >= self.thresholds['balance_increase_threshold']:
                    warning_signals.append({
                        "customer_key": customer,
                        "signal_type": "balance_increase",
                        "value": balance_change,
                        "threshold": self.thresholds['balance_increase_threshold'],
                        "severity": self._determine_severity(balance_change, self.thresholds['balance_increase_threshold']),
                        "date": customer_df[date_column].iloc[-1].isoformat()
                    })
        
        return {
            "warning_signals": warning_signals,
            "total_warnings": len(warning_signals),
            "customers_with_warnings": len(set(s["customer_key"] for s in warning_signals)),
            "by_severity": self._group_by_severity(warning_signals),
            "by_signal_type": self._group_by_signal_type(warning_signals)
        }
    
    def _determine_severity(self, value: float, threshold: float) -> WarningSeverity:
        """Determine severity of warning signal.
        
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
    
    def _group_by_severity(self, warning_signals: List[Dict[str, Any]]) -> Dict[str, int]:
        """Group warning signals by severity.
        
        Args:
            warning_signals: List of warning signals
        
        Returns:
            Dictionary with counts by severity
        """
        severity_counts = {s.value: 0 for s in WarningSeverity}
        for signal in warning_signals:
            severity_counts[signal['severity']] += 1
        return severity_counts
    
    def _group_by_signal_type(self, warning_signals: List[Dict[str, Any]]) -> Dict[str, int]:
        """Group warning signals by type.
        
        Args:
            warning_signals: List of warning signals
        
        Returns:
            Dictionary with counts by signal type
        """
        type_counts = {}
        for signal in warning_signals:
            signal_type = signal['signal_type']
            type_counts[signal_type] = type_counts.get(signal_type, 0) + 1
        return type_counts
    
    def calculate_warning_score(
        self,
        customer_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate composite warning score for a customer.
        
        Args:
            customer_metrics: Dictionary with customer metrics
        
        Returns:
            Dictionary with warning score and interpretation
        """
        score = 0
        factors = []
        
        # Credit utilization factor
        utilization = customer_metrics.get('credit_utilization', 0)
        if utilization > 0.8:
            score += 30
            factors.append(f"High credit utilization: {utilization:.1%}")
        elif utilization > 0.6:
            score += 15
            factors.append(f"Elevated credit utilization: {utilization:.1%}")
        
        # Days past due factor
        dpd = customer_metrics.get('days_past_due', 0)
        if dpd > 30:
            score += 40
            factors.append(f"Days past due: {dpd}")
        elif dpd > 0:
            score += 20
            factors.append(f"Days past due: {dpd}")
        
        # Churn probability factor
        churn_prob = customer_metrics.get('churn_probability', 0)
        if churn_prob > 0.7:
            score += 25
            factors.append(f"High churn probability: {churn_prob:.1%}")
        elif churn_prob > 0.4:
            score += 10
            factors.append(f"Elevated churn probability: {churn_prob:.1%}")
        
        # Risk level factor
        risk_level = customer_metrics.get('risk_level', 'low')
        risk_scores = {'low': 0, 'medium': 15, 'high': 30, 'critical': 50}
        score += risk_scores.get(risk_level, 0)
        if risk_level != 'low':
            factors.append(f"Risk level: {risk_level}")
        
        # Determine warning level
        if score >= 70:
            warning_level = WarningSeverity.CRITICAL
        elif score >= 50:
            warning_level = WarningSeverity.HIGH
        elif score >= 30:
            warning_level = WarningSeverity.MEDIUM
        else:
            warning_level = WarningSeverity.LOW
        
        return {
            'warning_score': score,
            'warning_level': warning_level.value,
            'factors': factors,
            'interpretation': self._interpret_warning_score(score, warning_level)
        }
    
    def _interpret_warning_score(self, score: int, warning_level: WarningSeverity) -> str:
        """Interpret warning score.
        
        Args:
            score: Warning score
            warning_level: Warning level
        
        Returns:
            Interpretation string
        """
        interpretations = {
            WarningSeverity.LOW: "Customer shows minimal warning signs. Monitor periodically.",
            WarningSeverity.MEDIUM: "Customer shows moderate warning signs. Increase monitoring frequency.",
            WarningSeverity.HIGH: "Customer shows significant warning signs. Consider intervention.",
            WarningSeverity.CRITICAL: "Customer shows critical warning signs. Immediate attention required."
        }
        return interpretations[warning_level]
    
    def generate_watchlist(
        self,
        metrics_df: pd.DataFrame,
        min_warning_level: WarningSeverity = WarningSeverity.MEDIUM
    ) -> pd.DataFrame:
        """Generate watchlist of customers with warning signals.
        
        Args:
            metrics_df: DataFrame with customer metrics
            min_warning_level: Minimum warning level to include
        
        Returns:
            DataFrame with watchlist
        """
        watchlist = []
        
        for _, row in metrics_df.iterrows():
            customer_metrics = row.to_dict()
            warning_result = self.calculate_warning_score(customer_metrics)
            
            # Filter by minimum warning level
            warning_level_order = {'low': 0, 'medium': 1, 'high': 2, 'critical': 3}
            if warning_level_order[warning_result['warning_level']] >= warning_level_order[min_warning_level.value]:
                watchlist.append({
                    'customer_key': customer_metrics.get('customer_key'),
                    'warning_score': warning_result['warning_score'],
                    'warning_level': warning_result['warning_level'],
                    'factors': ', '.join(warning_result['factors']),
                    'interpretation': warning_result['interpretation'],
                    'current_risk_level': customer_metrics.get('risk_level'),
                    'churn_probability': customer_metrics.get('churn_probability'),
                    'credit_utilization': customer_metrics.get('credit_utilization')
                })
        
        return pd.DataFrame(watchlist).sort_values('warning_score', ascending=False)
