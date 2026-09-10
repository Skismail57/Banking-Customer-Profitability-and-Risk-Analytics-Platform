"""Data splitting (train/validation/test, time-aware)."""

from typing import Dict, Any, Tuple, Optional
import logging

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

from src.predictive_analytics.base import ModelBase

logger = logging.getLogger(__name__)


class DataSplitter(ModelBase):
    """Split data into train/validation/test sets with time-aware options."""
    
    def split_train_val_test(
        self,
        df: pd.DataFrame,
        target_column: str,
        train_size: float = 0.6,
        val_size: float = 0.2,
        test_size: float = 0.2,
        random_state: Optional[int] = None
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Split data into train/validation/test sets.
        
        Args:
            df: DataFrame with data
            target_column: Name of target column
            train_size: Proportion for training
            val_size: Proportion for validation
            test_size: Proportion for testing
            random_state: Random state for reproducibility
        
        Returns:
            Tuple of (train_df, val_df, test_df)
        """
        if random_state is None:
            random_state = self.random_state
        
        # First split: train + val vs test
        train_val_df, test_df = train_test_split(
            df, test_size=test_size, random_state=random_state, stratify=df[target_column]
        )
        
        # Second split: train vs val
        # Adjust val_size to account for first split
        adjusted_val_size = val_size / (train_size + val_size)
        train_df, val_df = train_test_split(
            train_val_df, test_size=adjusted_val_size, random_state=random_state, stratify=train_val_df[target_column]
        )
        
        logger.info(f"Data split: Train={len(train_df)}, Val={len(val_df)}, Test={len(test_df)}")
        
        return train_df, val_df, test_df
    
    def time_aware_split(
        self,
        df: pd.DataFrame,
        date_column: str,
        target_column: str,
        train_end_date: str,
        val_end_date: str,
        test_end_date: str
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Split data based on time (time-aware splitting).
        
        Args:
            df: DataFrame with data
            date_column: Name of date column
            target_column: Name of target column
            train_end_date: End date for training data
            val_end_date: End date for validation data
            test_end_date: End date for test data
        
        Returns:
            Tuple of (train_df, val_df, test_df)
        """
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])
        
        train_df = df[df[date_column] <= train_end_date]
        val_df = df[(df[date_column] > train_end_date) & (df[date_column] <= val_end_date)]
        test_df = df[(df[date_column] > val_end_date) & (df[date_column] <= test_end_date)]
        
        logger.info(f"Time-aware split: Train={len(train_df)}, Val={len(val_df)}, Test={len(test_df)}")
        
        return train_df, val_df, test_df
    
    def get_features_and_target(
        self,
        df: pd.DataFrame,
        target_column: str,
        feature_columns: Optional[list] = None
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """Separate features and target.
        
        Args:
            df: DataFrame with data
            target_column: Name of target column
            feature_columns: List of feature columns (if None, use all except target)
        
        Returns:
            Tuple of (X, y)
        """
        if feature_columns is None:
            feature_columns = [col for col in df.columns if col != target_column]
        
        X = df[feature_columns]
        y = df[target_column]
        
        return X, y
