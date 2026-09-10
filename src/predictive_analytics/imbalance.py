"""Class imbalance handling."""

from typing import Dict, Any, Optional
import logging

import pandas as pd
import numpy as np
from imblearn.over_sampling import SMOTE, RandomOverSampler
from imblearn.under_sampling import RandomUnderSampler

from src.predictive_analytics.base import ModelBase

logger = logging.getLogger(__name__)


class ClassImbalanceHandler(ModelBase):
    """Handle class imbalance in classification problems."""
    
    def check_imbalance(
        self,
        y: pd.Series
    ) -> Dict[str, Any]:
        """Check for class imbalance.
        
        Args:
            y: Target variable
        
        Returns:
            Dictionary with imbalance information
        """
        value_counts = y.value_counts()
        total = len(y)
        
        imbalance_info = {
            "class_counts": value_counts.to_dict(),
            "class_proportions": (value_counts / total).to_dict(),
            "is_imbalanced": False,
            "imbalance_ratio": 1.0
        }
        
        if len(value_counts) == 2:
            minority_count = value_counts.min()
            majority_count = value_counts.max()
            imbalance_ratio = majority_count / minority_count
            
            imbalance_info["imbalance_ratio"] = imbalance_ratio
            imbalance_info["is_imbalanced"] = imbalance_ratio > 2.0  # Common threshold
        
        return imbalance_info
    
    def handle_imbalance(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        method: str = "smote",
        sampling_strategy: Optional[str] = "auto"
    ) -> tuple:
        """Handle class imbalance.
        
        Args:
            X: Features
            y: Target
            method: Method to handle imbalance (smote, oversample, undersample)
            sampling_strategy: Sampling strategy
        
        Returns:
            Tuple of (X_resampled, y_resampled)
        """
        imbalance_info = self.check_imbalance(y)
        
        if not imbalance_info["is_imbalanced"]:
            logger.info("No significant class imbalance detected")
            return X, y
        
        if method == "smote":
            sampler = SMOTE(sampling_strategy=sampling_strategy, random_state=self.random_state)
        elif method == "oversample":
            sampler = RandomOverSampler(sampling_strategy=sampling_strategy, random_state=self.random_state)
        elif method == "undersample":
            sampler = RandomUnderSampler(sampling_strategy=sampling_strategy, random_state=self.random_state)
        else:
            logger.warning(f"Unknown imbalance method: {method}")
            return X, y
        
        X_resampled, y_resampled = sampler.fit_resample(X, y)
        
        logger.info(f"Resampled from {len(X)} to {len(X_resampled)} samples using {method}")
        
        return X_resampled, y_resampled
