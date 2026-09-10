"""Feature engineering for customer clustering."""

from datetime import date
from typing import Dict, Any, List, Optional
import logging

import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler

from src.customer_segmentation.base import CustomerSegmentationBase

logger = logging.getLogger(__name__)


class FeatureEngineer(CustomerSegmentationBase):
    """Engineer features for customer clustering."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize feature engineer.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
    
    def extract_features(
        self,
        df: pd.DataFrame,
        feature_config: Optional[Dict[str, str]] = None
    ) -> pd.DataFrame:
        """Extract features for clustering.
        
        Args:
            df: DataFrame with customer data
            feature_config: Configuration mapping feature names to column names
        
        Returns:
            DataFrame with extracted features
        """
        if feature_config is None:
            feature_config = {
                "profitability": "net_profit",
                "transaction_frequency": "transaction_frequency",
                "balance": "total_balance",
                "product_count": "product_count",
                "credit_utilization": "credit_utilization",
                "loan_exposure": "total_exposure",
                "tenure_days": "tenure_days",
                "engagement_score": "engagement_score"
            }
        
        features_df = pd.DataFrame()
        
        for feature_name, column_name in feature_config.items():
            if column_name in df.columns:
                features_df[feature_name] = df[column_name]
            else:
                logger.warning(f"Column {column_name} not found for feature {feature_name}")
                features_df[feature_name] = 0
        
        return features_df
    
    def handle_missing_values(
        self,
        df: pd.DataFrame,
        strategy: str = "median"
    ) -> pd.DataFrame:
        """Handle missing values in features.
        
        Args:
            df: DataFrame with features
            strategy: Strategy for handling missing values (median, mean, zero)
        
        Returns:
            DataFrame with missing values handled
        """
        df = df.copy()
        
        if strategy == "median":
            df = df.fillna(df.median())
        elif strategy == "mean":
            df = df.fillna(df.mean())
        elif strategy == "zero":
            df = df.fillna(0)
        
        return df
    
    def scale_features(
        self,
        df: pd.DataFrame,
        method: str = "standard"
    ) -> pd.DataFrame:
        """Scale features for clustering.
        
        Args:
            df: DataFrame with features
            method: Scaling method (standard, minmax)
        
        Returns:
            DataFrame with scaled features
        """
        df = df.copy()
        
        if method == "standard":
            scaler = StandardScaler()
        elif method == "minmax":
            scaler = MinMaxScaler()
        else:
            logger.warning(f"Unknown scaling method {method}, returning unscaled")
            return df
        
        scaled_data = scaler.fit_transform(df)
        scaled_df = pd.DataFrame(scaled_data, columns=df.columns, index=df.index)
        
        return scaled_df
    
    def select_features(
        self,
        df: pd.DataFrame,
        feature_list: List[str]
    ) -> pd.DataFrame:
        """Select specific features.
        
        Args:
            df: DataFrame with features
            feature_list: List of features to select
        
        Returns:
            DataFrame with selected features
        """
        available_features = [f for f in feature_list if f in df.columns]
        
        if len(available_features) < len(feature_list):
            missing = set(feature_list) - set(available_features)
            logger.warning(f"Missing features: {missing}")
        
        return df[available_features]
    
    def create_derived_features(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """Create derived features from existing features.
        
        Args:
            df: DataFrame with base features
        
        Returns:
            DataFrame with derived features
        """
        df = df.copy()
        
        # Profitability per transaction
        if "profitability" in df.columns and "transaction_frequency" in df.columns:
            df["profit_per_transaction"] = df["profitability"] / (df["transaction_frequency"] + 1)
        
        # Balance per product
        if "balance" in df.columns and "product_count" in df.columns:
            df["balance_per_product"] = df["balance"] / (df["product_count"] + 1)
        
        # Exposure per tenure
        if "loan_exposure" in df.columns and "tenure_days" in df.columns:
            df["exposure_per_tenure"] = df["loan_exposure"] / (df["tenure_days"] + 1)
        
        return df
