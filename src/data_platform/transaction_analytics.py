"""Transaction Analytics Platform - Data Platform Integration Layer.

This module provides transaction-level analytics and serves as the foundation
for transaction-based insights and behavioral analysis.

Architecture Position:
Banking Data → Data Platform → Transaction Analytics → Core Analytics
"""

from typing import Dict, Any, Optional, List
from datetime import date, timedelta
import logging

import pandas as pd
import numpy as np

from src.data_platform.data_loader import DataLoader
from src.transaction_analytics.base import TransactionAnalyticsBase, TransactionKPI, AggregationPeriod

logger = logging.getLogger(__name__)


class TransactionAnalyticsPlatform(TransactionAnalyticsBase):
    """Transaction Analytics Platform for transaction-level insights.
    
    This class provides comprehensive transaction analytics including KPIs,
    patterns, and behavioral insights.
    """
    
    def __init__(self, as_of_date: Optional[date] = None, data_loader: Optional[DataLoader] = None):
        """Initialize Transaction Analytics Platform.
        
        Args:
            as_of_date: As-of date for temporal analysis
            data_loader: Data loader instance (creates default if not provided)
        """
        super().__init__(as_of_date)
        self.data_loader = data_loader or DataLoader()
    
    def calculate_transaction_kpis(
        self,
        customer_key: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        aggregation_period: AggregationPeriod = AggregationPeriod.DAILY
    ) -> pd.DataFrame:
        """Calculate transaction KPIs.
        
        Args:
            customer_key: Optional customer key to filter
            start_date: Optional start date
            end_date: Optional end date
            aggregation_period: Time aggregation period
        
        Returns:
            DataFrame with transaction KPIs
        """
        logger.info(f"Calculating transaction KPIs for customer: {customer_key}")
        
        # Set default date range if not provided
        if end_date is None:
            end_date = self.as_of_date
        if start_date is None:
            start_date = end_date - timedelta(days=90)
        
        # Load transactions
        transactions_df = self.data_loader.load_transactions(
            customer_key=customer_key,
            start_date=start_date,
            end_date=end_date
        )
        
        if transactions_df.empty:
            logger.warning("No transactions found for the specified criteria")
            return pd.DataFrame()
        
        # Aggregate by period
        transactions_df['transaction_date'] = pd.to_datetime(transactions_df['transaction_date'])
        
        if aggregation_period == AggregationPeriod.DAILY:
            transactions_df['period'] = transactions_df['transaction_date'].dt.date
        elif aggregation_period == AggregationPeriod.WEEKLY:
            transactions_df['period'] = transactions_df['transaction_date'].dt.to_period('W').dt.start_time.dt.date
        elif aggregation_period == AggregationPeriod.MONTHLY:
            transactions_df['period'] = transactions_df['transaction_date'].dt.to_period('M').dt.start_time.dt.date
        elif aggregation_period == AggregationPeriod.QUARTERLY:
            transactions_df['period'] = transactions_df['transaction_date'].dt.to_period('Q').dt.start_time.dt.date
        else:
            transactions_df['period'] = transactions_df['transaction_date'].dt.to_period('Y').dt.start_time.dt.date
        
        # Calculate KPIs by period
        kpi_df = transactions_df.groupby('period').agg({
            'transaction_id': 'count',
            'amount': ['sum', 'mean', 'median']
        }).reset_index()
        
        kpi_df.columns = ['period', 'transaction_count', 'total_value', 'avg_value', 'median_value']
        
        # Calculate debit/credit breakdown
        debit_df = transactions_df[transactions_df['amount'] < 0].groupby('period').agg({
            'transaction_id': 'count',
            'amount': 'sum'
        }).reset_index()
        debit_df.columns = ['period', 'debit_count', 'debit_value']
        
        credit_df = transactions_df[transactions_df['amount'] > 0].groupby('period').agg({
            'transaction_id': 'count',
            'amount': 'sum'
        }).reset_index()
        credit_df.columns = ['period', 'credit_count', 'credit_value']
        
        # Merge all KPIs
        kpi_df = kpi_df.merge(debit_df, on='period', how='left')
        kpi_df = kpi_df.merge(credit_df, on='period', how='left')
        
        # Fill NaN values
        kpi_df = kpi_df.fillna(0)
        
        # Calculate derived KPIs
        kpi_df['net_flow'] = kpi_df['credit_value'] + kpi_df['debit_value']  # debit is negative
        kpi_df['transaction_frequency'] = kpi_df['transaction_count']  # Simplified
        
        logger.info(f"Calculated transaction KPIs for {len(kpi_df)} periods")
        return kpi_df
    
    def analyze_transaction_patterns(
        self,
        customer_key: str,
        window_days: int = 90
    ) -> Dict[str, Any]:
        """Analyze transaction patterns for a customer.
        
        Args:
            customer_key: Customer key
            window_days: Number of days to analyze
        
        Returns:
            Dictionary with transaction pattern analysis
        """
        logger.info(f"Analyzing transaction patterns for customer: {customer_key}")
        
        start_date = self.as_of_date - timedelta(days=window_days)
        
        transactions_df = self.data_loader.load_transactions(
            customer_key=customer_key,
            start_date=start_date,
            end_date=self.as_of_date
        )
        
        if transactions_df.empty:
            return {"error": "No transactions found"}
        
        transactions_df['transaction_date'] = pd.to_datetime(transactions_df['transaction_date'])
        
        analysis = {}
        
        # Temporal patterns
        transactions_df['day_of_week'] = transactions_df['transaction_date'].dt.dayofweek
        transactions_df['hour'] = transactions_df['transaction_date'].dt.hour
        
        analysis['day_of_week_distribution'] = transactions_df['day_of_week'].value_counts().to_dict()
        analysis['hour_distribution'] = transactions_df['hour'].value_counts().to_dict()
        
        # Merchant category patterns
        analysis['merchant_category_distribution'] = transactions_df['merchant_category'].value_counts().to_dict()
        
        # Transaction type patterns
        analysis['transaction_type_distribution'] = transactions_df['transaction_type'].value_counts().to_dict()
        
        # Amount patterns
        analysis['amount_statistics'] = {
            'mean': float(transactions_df['amount'].mean()),
            'median': float(transactions_df['amount'].median()),
            'std': float(transactions_df['amount'].std()),
            'min': float(transactions_df['amount'].min()),
            'max': float(transactions_df['amount'].max())
        }
        
        # Frequency patterns
        daily_counts = transactions_df.groupby(transactions_df['transaction_date'].dt.date).size()
        analysis['frequency_statistics'] = {
            'avg_daily_transactions': float(daily_counts.mean()),
            'max_daily_transactions': int(daily_counts.max()),
            'min_daily_transactions': int(daily_counts.min())
        }
        
        # Channel patterns
        analysis['channel_distribution'] = transactions_df['channel'].value_counts().to_dict()
        
        logger.info(f"Transaction pattern analysis completed for customer: {customer_key}")
        return analysis
    
    def detect_anomalies(
        self,
        customer_key: str,
        window_days: int = 90,
        std_threshold: float = 3.0
    ) -> pd.DataFrame:
        """Detect anomalous transactions using statistical methods.
        
        Args:
            customer_key: Customer key
            window_days: Number of days to analyze
            std_threshold: Standard deviation threshold for anomaly detection
        
        Returns:
            DataFrame with anomalous transactions
        """
        logger.info(f"Detecting transaction anomalies for customer: {customer_key}")
        
        start_date = self.as_of_date - timedelta(days=window_days)
        
        transactions_df = self.data_loader.load_transactions(
            customer_key=customer_key,
            start_date=start_date,
            end_date=self.as_of_date
        )
        
        if transactions_df.empty or len(transactions_df) < 10:
            logger.warning("Insufficient data for anomaly detection")
            return pd.DataFrame()
        
        # Calculate z-scores for transaction amounts
        mean_amount = transactions_df['amount'].mean()
        std_amount = transactions_df['amount'].std()
        
        transactions_df['z_score'] = np.abs((transactions_df['amount'] - mean_amount) / std_amount)
        
        # Flag anomalies
        anomalies_df = transactions_df[transactions_df['z_score'] > std_threshold].copy()
        anomalies_df['anomaly_reason'] = f"Amount deviates by {std_threshold}+ standard deviations"
        
        logger.info(f"Detected {len(anomalies_df)} anomalous transactions")
        return anomalies_df
    
    def get_customer_transaction_summary(
        self,
        customer_key: str,
        window_days: int = 30
    ) -> Dict[str, Any]:
        """Get transaction summary for a customer.
        
        Args:
            customer_key: Customer key
            window_days: Number of days to summarize
        
        Returns:
            Dictionary with transaction summary
        """
        logger.info(f"Getting transaction summary for customer: {customer_key}")
        
        start_date = self.as_of_date - timedelta(days=window_days)
        
        transactions_df = self.data_loader.load_transactions(
            customer_key=customer_key,
            start_date=start_date,
            end_date=self.as_of_date
        )
        
        if transactions_df.empty:
            return {
                "total_transactions": 0,
                "total_volume": 0,
                "avg_transaction_value": 0
            }
        
        summary = {
            "total_transactions": len(transactions_df),
            "total_volume": float(transactions_df['amount'].abs().sum()),
            "avg_transaction_value": float(transactions_df['amount'].abs().mean()),
            "median_transaction_value": float(transactions_df['amount'].abs().median()),
            "transaction_types": transactions_df['transaction_type'].value_counts().to_dict(),
            "merchant_categories": transactions_df['merchant_category'].value_counts().to_dict(),
            "channels": transactions_df['channel'].value_counts().to_dict()
        }
        
        logger.info(f"Transaction summary generated for customer: {customer_key}")
        return summary
