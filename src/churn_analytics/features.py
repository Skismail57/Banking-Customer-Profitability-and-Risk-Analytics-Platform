"""Point-in-time correct churn feature engineering."""

from datetime import date, timedelta
from typing import Dict, Any, List, Optional
import logging

import pandas as pd
import numpy as np

from src.churn_analytics.base import ChurnBase

logger = logging.getLogger(__name__)


class ChurnFeatureEngineer(ChurnBase):
    """Engineer point-in-time correct features for churn modeling."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize churn feature engineer.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
    
    def create_feature_dataset(
        self,
        df: pd.DataFrame,
        feature_config: Optional[Dict[str, str]] = None,
        lookback_days: int = 90,
        observation_window_days: int = 30
    ) -> pd.DataFrame:
        """Create point-in-time correct feature dataset.
        
        Args:
            df: DataFrame with customer data
            feature_config: Configuration mapping feature names to column names
            lookback_days: Lookback period for feature calculation
            observation_window_days: Observation window for churn label
        
        Returns:
            DataFrame with features and churn label
        
        Note:
            Features are calculated using only data available at prediction time.
            No future information is used in feature calculation.
        """
        if feature_config is None:
            feature_config = {
                "tenure_days": "tenure_days",
                "balance": "current_balance",
                "transaction_count": "transaction_count",
                "transaction_amount": "total_amount",
                "product_count": "product_count",
                "credit_utilization": "credit_utilization",
                "days_since_last_transaction": "days_since_last_transaction",
                "complaint_count": "complaint_count",
                "profitability": "net_profit"
            }
        
        df = df.copy()
        
        # Calculate observation date (point-in-time)
        observation_date = self.as_of_date - timedelta(days=observation_window_days)
        
        # Filter to data available at observation date
        if "as_of_date" in df.columns:
            df["as_of_date"] = pd.to_datetime(df["as_of_date"])
            df = df[df["as_of_date"] <= observation_date]
        
        # Extract features
        features_df = pd.DataFrame()
        
        for feature_name, column_name in feature_config.items():
            if column_name in df.columns:
                features_df[feature_name] = df[column_name]
            else:
                logger.warning(f"Column {column_name} not found for feature {feature_name}")
                features_df[feature_name] = 0
        
        # Add derived features
        features_df = self._add_derived_features(features_df)
        
        # Add churn label (based on future behavior)
        features_df["churn_label"] = self._calculate_churn_label(
            df, observation_window_days
        )
        
        # Add observation date
        features_df["observation_date"] = observation_date
        
        return features_df
    
    def _add_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add derived features.
        
        Args:
            df: DataFrame with base features
        
        Returns:
            DataFrame with derived features
        """
        df = df.copy()
        
        # Transaction per day
        if "tenure_days" in df.columns and "transaction_count" in df.columns:
            df["transactions_per_day"] = df["transaction_count"] / (df["tenure_days"] + 1)
        
        # Balance per product
        if "balance" in df.columns and "product_count" in df.columns:
            df["balance_per_product"] = df["balance"] / (df["product_count"] + 1)
        
        # Profit per transaction
        if "profitability" in df.columns and "transaction_count" in df.columns:
            df["profit_per_transaction"] = df["profitability"] / (df["transaction_count"] + 1)
        
        # Recency score (inverse of days since last transaction)
        if "days_since_last_transaction" in df.columns:
            df["recency_score"] = 1 / (df["days_since_last_transaction"] + 1)
        
        return df
    
    def _calculate_churn_label(
        self,
        df: pd.DataFrame,
        observation_window_days: int
    ) -> pd.Series:
        """Calculate churn label based on future behavior.
        
        Args:
            df: DataFrame with customer data
            observation_window_days: Observation window for churn determination
        
        Returns:
            Series with churn labels (1 = churned, 0 = retained)
        
        Note:
            This uses future behavior to create labels for training.
            In production, this would not be available.
        """
        # This is a placeholder - actual implementation depends on churn definition
        # For now, use a simple rule: churn if no activity in observation window
        if "is_churned" in df.columns:
            return df["is_churned"]
        else:
            # Default: assume no churn (placeholder)
            return pd.Series(0, index=df.index)
    
    def create_temporal_features(
        self,
        df: pd.DataFrame,
        customer_column: str = "customer_key",
        date_column: str = "transaction_date",
        feature_columns: List[str] = None,
        periods: List[int] = None
    ) -> pd.DataFrame:
        """Create temporal features (rolling averages, trends).
        
        Args:
            df: DataFrame with transaction data
            customer_column: Name of customer column
            date_column: Name of date column
            feature_columns: List of feature columns to aggregate
            periods: List of periods for rolling calculations (days)
        
        Returns:
            DataFrame with temporal features
        
        Note:
            Only uses data available at each point in time.
        """
        if feature_columns is None:
            feature_columns = ["amount"]
        
        if periods is None:
            periods = [30, 60, 90]
        
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])
        df = df.sort_values([customer_column, date_column])
        
        results = []
        
        for customer in df[customer_column].unique():
            customer_df = df[df[customer_column] == customer].copy()
            
            customer_features = {customer_column: customer}
            
            for period in periods:
                cutoff_date = self.as_of_date - timedelta(days=period)
                period_df = customer_df[customer_df[date_column] <= cutoff_date]
                
                for col in feature_columns:
                    if col in period_df.columns:
                        customer_features[f"{col}_last_{period}d_sum"] = period_df[col].sum()
                        customer_features[f"{col}_last_{period}d_mean"] = period_df[col].mean()
                        customer_features[f"{col}_last_{period}d_count"] = len(period_df)
            
            results.append(customer_features)
        
        return pd.DataFrame(results)
