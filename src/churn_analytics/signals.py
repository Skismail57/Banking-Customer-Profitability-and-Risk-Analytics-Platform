"""Churn signal detection (activity, transaction, balance, complaints)."""

from datetime import date, timedelta
from typing import Dict, Any, Optional
import logging

import pandas as pd
import numpy as np

from src.churn_analytics.base import ChurnBase

logger = logging.getLogger(__name__)


class ActivityDeclineDetector(ChurnBase):
    """Detect customer activity decline and product disengagement."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize activity decline detector.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
    
    def detect_activity_decline(
        self,
        df: pd.DataFrame,
        customer_column: str = "customer_key",
        date_column: str = "activity_date",
        lookback_days: int = 90,
        comparison_days: int = 30
    ) -> pd.DataFrame:
        """Detect customer activity decline.
        
        Args:
            df: DataFrame with activity data
            customer_column: Name of customer column
            date_column: Name of date column
            lookback_days: Lookback period for recent activity
            comparison_days: Comparison period for baseline
        
        Returns:
            DataFrame with activity decline indicators
        """
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])
        
        cutoff_date = self.as_of_date - timedelta(days=lookback_days)
        comparison_start = self.as_of_date - timedelta(days=lookback_days + comparison_days)
        
        # Calculate activity counts
        recent_activity = df[df[date_column] >= cutoff_date].groupby(customer_column).size()
        baseline_activity = df[
            (df[date_column] >= comparison_start) & (df[date_column] < cutoff_date)
        ].groupby(customer_column).size()
        
        # Calculate decline
        results = []
        for customer in set(df[customer_column]):
            recent = recent_activity.get(customer, 0)
            baseline = baseline_activity.get(customer, 0)
            
            if baseline > 0:
                decline_pct = ((baseline - recent) / baseline) * 100
            else:
                decline_pct = 0
            
            is_decline = decline_pct > 50 and recent < baseline / 2
            
            results.append({
                customer_column: customer,
                "recent_activity_count": recent,
                "baseline_activity_count": baseline,
                "activity_decline_pct": decline_pct,
                "is_activity_decline": is_decline
            })
        
        return pd.DataFrame(results)
    
    def detect_product_disengagement(
        self,
        df: pd.DataFrame,
        customer_column: str = "customer_key",
        product_column: str = "product_key",
        date_column: str = "usage_date",
        inactivity_threshold_days: int = 60
    ) -> pd.DataFrame:
        """Detect product disengagement.
        
        Args:
            df: DataFrame with product usage data
            customer_column: Name of customer column
            product_column: Name of product column
            date_column: Name of date column
            inactivity_threshold_days: Days of inactivity to consider disengaged
        
        Returns:
            DataFrame with product disengagement indicators
        """
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])
        
        # Find last usage per customer-product
        last_usage = df.groupby([customer_column, product_column])[date_column].max().reset_index()
        last_usage["days_since_last_use"] = (self.as_of_date - last_usage[date_column]).dt.days
        
        # Identify disengaged products
        last_usage["is_disengaged"] = last_usage["days_since_last_use"] > inactivity_threshold_days
        
        # Aggregate to customer level
        customer_disengagement = last_usage.groupby(customer_column).agg({
            "is_disengaged": "sum",
            product_column: "count",
            "days_since_last_use": "max"
        }).reset_index()
        
        customer_disengagement["disengagement_rate"] = (
            customer_disengagement["is_disengaged"] / customer_disengagement[product_column] * 100
        )
        
        return customer_disengagement


class TransactionDeclineDetector(ChurnBase):
    """Detect transaction decline."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize transaction decline detector.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
    
    def detect_transaction_decline(
        self,
        df: pd.DataFrame,
        customer_column: str = "customer_key",
        date_column: str = "transaction_date",
        amount_column: str = "amount",
        lookback_days: int = 90,
        comparison_days: int = 30
    ) -> pd.DataFrame:
        """Detect transaction decline.
        
        Args:
            df: DataFrame with transaction data
            customer_column: Name of customer column
            date_column: Name of date column
            amount_column: Name of amount column
            lookback_days: Lookback period for recent transactions
            comparison_days: Comparison period for baseline
        
        Returns:
            DataFrame with transaction decline indicators
        """
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])
        
        cutoff_date = self.as_of_date - timedelta(days=lookback_days)
        comparison_start = self.as_of_date - timedelta(days=lookback_days + comparison_days)
        
        # Calculate transaction metrics
        recent_transactions = df[df[date_column] >= cutoff_date]
        baseline_transactions = df[
            (df[date_column] >= comparison_start) & (df[date_column] < cutoff_date)
        ]
        
        recent_metrics = recent_transactions.groupby(customer_column).agg({
            amount_column: ["count", "sum", "mean"]
        }).reset_index()
        recent_metrics.columns = [customer_column, "recent_count", "recent_sum", "recent_mean"]
        
        baseline_metrics = baseline_transactions.groupby(customer_column).agg({
            amount_column: ["count", "sum", "mean"]
        }).reset_index()
        baseline_metrics.columns = [customer_column, "baseline_count", "baseline_sum", "baseline_mean"]
        
        # Merge and calculate decline
        metrics = recent_metrics.merge(baseline_metrics, on=customer_column, how="outer").fillna(0)
        
        metrics["count_decline_pct"] = (
            (metrics["baseline_count"] - metrics["recent_count"]) / 
            (metrics["baseline_count"] + 1) * 100
        )
        metrics["sum_decline_pct"] = (
            (metrics["baseline_sum"] - metrics["recent_sum"]) / 
            (metrics["baseline_sum"] + 1) * 100
        )
        
        metrics["is_transaction_decline"] = (
            (metrics["count_decline_pct"] > 50) & 
            (metrics["recent_count"] < metrics["baseline_count"] / 2)
        )
        
        return metrics


class BalanceDeclineDetector(ChurnBase):
    """Detect balance decline."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize balance decline detector.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
    
    def detect_balance_decline(
        self,
        df: pd.DataFrame,
        customer_column: str = "customer_key",
        balance_column: str = "balance",
        date_column: str = "as_of_date",
        lookback_days: int = 90,
        decline_threshold_pct: float = 50.0
    ) -> pd.DataFrame:
        """Detect balance decline.
        
        Args:
            df: DataFrame with balance data
            customer_column: Name of customer column
            balance_column: Name of balance column
            date_column: Name of date column
            lookback_days: Lookback period
            decline_threshold_pct: Percentage decline threshold
        
        Returns:
            DataFrame with balance decline indicators
        """
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])
        
        cutoff_date = self.as_of_date - timedelta(days=lookback_days)
        
        # Get current and historical balances
        current_balances = df[df[date_column] >= cutoff_date].groupby(customer_column)[balance_column].last()
        historical_balances = df[df[date_column] < cutoff_date].groupby(customer_column)[balance_column].last()
        
        # Calculate decline
        results = []
        for customer in set(df[customer_column]):
            current = current_balances.get(customer, 0)
            historical = historical_balances.get(customer, current)
            
            if historical > 0:
                decline_pct = ((historical - current) / historical) * 100
            else:
                decline_pct = 0
            
            is_decline = decline_pct > decline_threshold_pct
            
            results.append({
                customer_column: customer,
                "current_balance": current,
                "historical_balance": historical,
                "balance_decline_pct": decline_pct,
                "is_balance_decline": is_decline
            })
        
        return pd.DataFrame(results)


class ComplaintSignalDetector(ChurnBase):
    """Detect complaint-related churn signals."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize complaint signal detector.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
    
    def detect_complaint_signals(
        self,
        df: pd.DataFrame,
        customer_column: str = "customer_key",
        date_column: str = "complaint_date",
        severity_column: str = "severity",
        lookback_days: int = 90
    ) -> pd.DataFrame:
        """Detect complaint-related churn signals.
        
        Args:
            df: DataFrame with complaint data
            customer_column: Name of customer column
            date_column: Name of date column
            severity_column: Name of severity column
            lookback_days: Lookback period for complaints
        
        Returns:
            DataFrame with complaint signals
        """
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])
        
        cutoff_date = self.as_of_date - timedelta(days=lookback_days)
        recent_complaints = df[df[date_column] >= cutoff_date]
        
        if severity_column in df.columns:
            # Weight complaints by severity
            severity_weights = {"high": 3, "medium": 2, "low": 1}
            recent_complaints["severity_weight"] = recent_complaints[severity_column].map(
                severity_weights
            ).fillna(1)
        else:
            recent_complaints["severity_weight"] = 1
        
        # Aggregate complaints per customer
        complaint_metrics = recent_complaints.groupby(customer_column).agg({
            "severity_weight": "sum",
            date_column: "count"
        }).reset_index()
        complaint_metrics.columns = [customer_column, "complaint_score", "complaint_count"]
        
        # Identify high-risk customers
        complaint_metrics["high_complaint_risk"] = complaint_metrics["complaint_score"] >= 5
        
        return complaint_metrics
