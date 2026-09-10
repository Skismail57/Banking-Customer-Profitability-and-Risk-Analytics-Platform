"""Anomaly detection for unusual transaction behavior."""

from datetime import date
from typing import Dict, Any, List, Optional, Tuple
import logging

import pandas as pd
import numpy as np
from scipy import stats

from src.transaction_analytics.base import TransactionAnalyticsBase

logger = logging.getLogger(__name__)


class AnomalyDetector(TransactionAnalyticsBase):
    """Detect unusual transaction behavior patterns."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize anomaly detector.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
    
    def detect_amount_anomalies(
        self,
        df: pd.DataFrame,
        amount_column: str = "amount",
        method: str = "iqr",
        threshold: float = 3.0
    ) -> pd.DataFrame:
        """Detect anomalies in transaction amounts.
        
        Args:
            df: DataFrame with transaction data
            amount_column: Name of amount column
            method: Detection method (iqr, zscore, isolation_forest)
            threshold: Threshold for anomaly detection
        
        Returns:
            DataFrame with anomaly flags
        """
        logger.info(f"Detecting amount anomalies using {method} method")
        
        df = df.copy()
        
        if method == "iqr":
            df["is_anomaly"] = self._detect_iqr_anomalies(df[amount_column], threshold)
            df["anomaly_type"] = "amount_outlier"
        elif method == "zscore":
            df["is_anomaly"] = self._detect_zscore_anomalies(df[amount_column], threshold)
            df["anomaly_type"] = "amount_outlier"
        else:
            logger.warning(f"Unsupported method: {method}")
            df["is_anomaly"] = False
            df["anomaly_type"] = None
        
        anomaly_count = df["is_anomaly"].sum()
        logger.info(f"Detected {anomaly_count} amount anomalies ({anomaly_count/len(df)*100:.2f}%)")
        
        return df
    
    def _detect_iqr_anomalies(self, values: pd.Series, threshold: float = 3.0) -> pd.Series:
        """Detect anomalies using IQR method.
        
        Args:
            values: Series of values
            threshold: IQR multiplier threshold
        
        Returns:
            Boolean series indicating anomalies
        """
        Q1 = values.quantile(0.25)
        Q3 = values.quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        
        return (values < lower_bound) | (values > upper_bound)
    
    def _detect_zscore_anomalies(self, values: pd.Series, threshold: float = 3.0) -> pd.Series:
        """Detect anomalies using Z-score method.
        
        Args:
            values: Series of values
            threshold: Z-score threshold
        
        Returns:
            Boolean series indicating anomalies
        """
        z_scores = np.abs(stats.zscore(values))
        return z_scores > threshold
    
    def detect_frequency_anomalies(
        self,
        df: pd.DataFrame,
        date_column: str = "transaction_date",
        customer_column: str = "customer_key",
        window_days: int = 30,
        threshold_multiplier: float = 2.0
    ) -> pd.DataFrame:
        """Detect anomalies in transaction frequency per customer.
        
        Args:
            df: DataFrame with transaction data
            date_column: Name of date column
            customer_column: Name of customer column
            window_days: Window size for frequency calculation
            threshold_multiplier: Threshold multiplier for anomaly detection
        
        Returns:
            DataFrame with frequency anomaly flags
        """
        logger.info("Detecting frequency anomalies per customer")
        
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])
        
        # Calculate transaction count per customer per window
        df["period"] = df[date_column].dt.to_period(f"{window_days}D")
        customer_freq = df.groupby([customer_column, "period"]).size().reset_index()
        customer_freq.columns = [customer_column, "period", "transaction_count"]
        
        # Calculate mean and std per customer
        freq_stats = customer_freq.groupby(customer_column)["transaction_count"].agg(["mean", "std"]).reset_index()
        
        # Detect anomalies
        customer_freq = customer_freq.merge(freq_stats, on=customer_column, how="left")
        customer_freq["is_frequency_anomaly"] = (
            customer_freq["transaction_count"] > 
            (customer_freq["mean"] + threshold_multiplier * customer_freq["std"])
        )
        
        anomaly_count = customer_freq["is_frequency_anomaly"].sum()
        logger.info(f"Detected {anomaly_count} frequency anomalies")
        
        return customer_freq
    
    def detect_pattern_anomalies(
        self,
        df: pd.DataFrame,
        date_column: str = "transaction_date",
        amount_column: str = "amount",
        customer_column: str = "customer_key"
    ) -> pd.DataFrame:
        """Detect unusual transaction patterns per customer.
        
        Args:
            df: DataFrame with transaction data
            date_column: Name of date column
            amount_column: Name of amount column
            customer_column: Name of customer column
        
        Returns:
            DataFrame with pattern anomaly flags
        """
        logger.info("Detecting pattern anomalies per customer")
        
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])
        
        # Calculate per-customer statistics
        customer_stats = df.groupby(customer_column).agg({
            amount_column: ["mean", "std", "count"]
        }).reset_index()
        
        customer_stats.columns = [customer_column, "mean_amount", "std_amount", "transaction_count"]
        
        # Flag unusual patterns
        customer_stats["has_unusual_pattern"] = (
            (customer_stats["std_amount"] / customer_stats["mean_amount"] > 2) &  # High variability
            (customer_stats["transaction_count"] > 10)  # Sufficient transactions
        )
        
        anomaly_count = customer_stats["has_unusual_pattern"].sum()
        logger.info(f"Detected {anomaly_count} customers with unusual patterns")
        
        return customer_stats
    
    def detect_velocity_anomalies(
        self,
        df: pd.DataFrame,
        date_column: str = "transaction_date",
        amount_column: str = "amount",
        customer_column: str = "customer_key",
        window_minutes: int = 60
    ) -> pd.DataFrame:
        """Detect rapid transaction velocity anomalies.
        
        Args:
            df: DataFrame with transaction data
            date_column: Name of date column
            amount_column: Name of amount column
            customer_column: Name of customer column
            window_minutes: Time window in minutes
        
        Returns:
            DataFrame with velocity anomaly flags
        """
        logger.info(f"Detecting velocity anomalies ({window_minutes}min window)")
        
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])
        df = df.sort_values([customer_column, date_column])
        
        # Calculate time difference between transactions
        df["prev_date"] = df.groupby(customer_column)[date_column].shift(1)
        df["time_diff_minutes"] = (df[date_column] - df["prev_date"]).dt.total_seconds() / 60
        
        # Flag rapid transactions
        df["is_velocity_anomaly"] = df["time_diff_minutes"] < window_minutes
        
        anomaly_count = df["is_velocity_anomaly"].sum()
        logger.info(f"Detected {anomaly_count} rapid transaction events")
        
        return df
    
    def generate_anomaly_report(
        self,
        df: pd.DataFrame,
        date_column: str = "transaction_date",
        amount_column: str = "amount",
        customer_column: str = "customer_key"
    ) -> Dict[str, Any]:
        """Generate comprehensive anomaly report.
        
        Args:
            df: DataFrame with transaction data
            date_column: Name of date column
            amount_column: Name of amount column
            customer_column: Name of customer column
        
        Returns:
            Dictionary with anomaly summary
        """
        logger.info("Generating anomaly report")
        
        report = {
            "total_transactions": len(df),
            "amount_anomalies": {},
            "frequency_anomalies": {},
            "pattern_anomalies": {},
            "velocity_anomalies": {}
        }
        
        # Amount anomalies
        amount_anomalies = self.detect_amount_anomalies(df, amount_column)
        report["amount_anomalies"]["count"] = amount_anomalies["is_anomaly"].sum()
        report["amount_anomalies"]["percentage"] = (report["amount_anomalies"]["count"] / len(df) * 100).round(2)
        
        # Frequency anomalies
        freq_anomalies = self.detect_frequency_anomalies(df, date_column, customer_column)
        report["frequency_anomalies"]["count"] = freq_anomalies["is_frequency_anomaly"].sum()
        
        # Pattern anomalies
        pattern_anomalies = self.detect_pattern_anomalies(df, date_column, amount_column, customer_column)
        report["pattern_anomalies"]["count"] = pattern_anomalies["has_unusual_pattern"].sum()
        
        # Velocity anomalies
        velocity_anomalies = self.detect_velocity_anomalies(df, date_column, amount_column, customer_column)
        report["velocity_anomalies"]["count"] = velocity_anomalies["is_velocity_anomaly"].sum()
        
        return report
