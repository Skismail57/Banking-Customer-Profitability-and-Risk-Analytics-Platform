"""Base classes for Customer 360 analytics."""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
import logging

import pandas as pd

logger = logging.getLogger(__name__)


class FeatureCategory(Enum):
    """Categories of customer features."""
    DEMOGRAPHIC = "demographic"
    ACCOUNT = "account"
    TRANSACTION = "transaction"
    LOAN = "loan"
    INTERACTION = "interaction"
    PROFITABILITY = "profitability"
    RISK = "risk"


@dataclass
class FeatureDefinition:
    """Definition of a customer feature."""
    
    name: str
    category: FeatureCategory
    description: str
    data_type: str  # numeric, categorical, datetime, boolean
    is_temporal: bool = False
    requires_historical_data: bool = False
    calculation_window_days: Optional[int] = None
    business_definition: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "category": self.category.value,
            "description": self.description,
            "data_type": self.data_type,
            "is_temporal": self.is_temporal,
            "requires_historical_data": self.requires_historical_data,
            "calculation_window_days": self.calculation_window_days,
            "business_definition": self.business_definition
        }


class Customer360Base:
    """Base class for Customer 360 feature extraction."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize Customer 360 base.
        
        Args:
            as_of_date: As-of date for temporal features (prevents future data leakage)
        """
        self.as_of_date = as_of_date or date.today()
        self.feature_registry: Dict[str, FeatureDefinition] = {}
    
    def register_feature(self, feature: FeatureDefinition) -> None:
        """Register a feature definition.
        
        Args:
            feature: FeatureDefinition to register
        """
        self.feature_registry[feature.name] = feature
        logger.debug(f"Registered feature: {feature.name}")
    
    def get_feature_definition(self, feature_name: str) -> Optional[FeatureDefinition]:
        """Get feature definition by name.
        
        Args:
            feature_name: Name of the feature
        
        Returns:
            FeatureDefinition if found, None otherwise
        """
        return self.feature_registry.get(feature_name)
    
    def get_features_by_category(self, category: FeatureCategory) -> List[FeatureDefinition]:
        """Get all features in a category.
        
        Args:
            category: FeatureCategory to filter by
        
        Returns:
            List of FeatureDefinitions
        """
        return [f for f in self.feature_registry.values() if f.category == category]
    
    def ensure_temporal_safety(self, df: pd.DataFrame, date_column: str) -> pd.DataFrame:
        """Ensure no future data leakage by filtering to as_of_date.
        
        Args:
            df: DataFrame to filter
            date_column: Name of date column
        
        Returns:
            Filtered DataFrame
        """
        if date_column not in df.columns:
            logger.warning(f"Date column {date_column} not found in DataFrame")
            return df
        
        # Convert to datetime if needed
        if not pd.api.types.is_datetime64_any_dtype(df[date_column]):
            df[date_column] = pd.to_datetime(df[date_column])
        
        # Filter to as_of_date
        before_count = len(df)
        df_filtered = df[df[date_column] <= pd.Timestamp(self.as_of_date)].copy()
        after_count = len(df_filtered)
        
        if before_count != after_count:
            logger.info(
                f"Temporal safety: Filtered {before_count - after_count} future records "
                f"from {before_count} total records using as_of_date {self.as_of_date}"
            )
        
        return df_filtered
    
    def validate_required_columns(self, df: pd.DataFrame, required_columns: List[str]) -> bool:
        """Validate that required columns exist in DataFrame.
        
        Args:
            df: DataFrame to validate
            required_columns: List of required column names
        
        Returns:
            True if all columns present, False otherwise
        """
        missing_columns = set(required_columns) - set(df.columns)
        
        if missing_columns:
            logger.warning(f"Missing required columns: {missing_columns}")
            return False
        
        return True


class TemporalWindow:
    """Helper for temporal window calculations."""
    
    @staticmethod
    def get_window_start(as_of_date: date, days: int) -> date:
        """Get start date for a temporal window.
        
        Args:
            as_of_date: As-of date
            days: Number of days in window
        
        Returns:
            Start date
        """
        from datetime import timedelta
        return as_of_date - timedelta(days=days)
    
    @staticmethod
    def partition_windows(as_of_date: date, window_days: int, num_windows: int) -> List[tuple]:
        """Partition time into multiple windows.
        
        Args:
            as_of_date: As-of date
            window_days: Size of each window in days
            num_windows: Number of windows to create
        
        Returns:
            List of (window_start, window_end) tuples
        """
        from datetime import timedelta
        
        windows = []
        for i in range(num_windows):
            window_end = as_of_date - timedelta(days=i * window_days)
            window_start = window_end - timedelta(days=window_days)
            windows.append((window_start, window_end))
        
        return windows
