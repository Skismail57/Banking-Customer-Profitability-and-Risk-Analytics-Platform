"""Data profiler for streaming pipeline.

This module provides data profiling capabilities to understand data
characteristics and detect quality issues.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class ProfileResult:
    """Data profiling result."""
    profile_id: str
    field: str
    data_type: str
    null_count: int
    null_percentage: float
    unique_count: int
    unique_percentage: float
    min_value: Optional[Any]
    max_value: Optional[Any]
    mean_value: Optional[float]
    std_value: Optional[float]
    sample_values: List[Any]
    profiled_at: datetime


class DataProfiler:
    """Data profiler for quality analysis."""
    
    def __init__(self):
        """Initialize data profiler."""
        self.profile_history = []
    
    def profile_data(self, data: pd.DataFrame) -> Dict[str, ProfileResult]:
        """Profile entire dataset.
        
        Args:
            data: Data to profile
        
        Returns:
            Dictionary of field profiles
        """
        profiles = {}
        
        for column in data.columns:
            profile = self._profile_column(data, column)
            profiles[column] = profile
        
        return profiles
    
    def _profile_column(self, data: pd.DataFrame, column: str) -> ProfileResult:
        """Profile a single column.
        
        Args:
            data: Data to profile
            column: Column name
        
        Returns:
            Column profile
        """
        profile_id = f"profile_{column}_{int(datetime.now(timezone.utc).replace(tzinfo=None).timestamp())}"
        series = data[column]
        
        # Basic statistics
        null_count = series.isna().sum()
        null_percentage = (null_count / len(series)) * 100
        unique_count = series.nunique()
        unique_percentage = (unique_count / len(series)) * 100
        
        # Type detection
        data_type = str(series.dtype)
        
        # Numeric statistics
        min_value = None
        max_value = None
        mean_value = None
        std_value = None
        
        if pd.api.types.is_numeric_dtype(series):
            min_value = series.min()
            max_value = series.max()
            mean_value = series.mean()
            std_value = series.std()
        
        # Sample values
        sample_values = series.dropna().head(5).tolist()
        
        profile = ProfileResult(
            profile_id=profile_id,
            field=column,
            data_type=data_type,
            null_count=null_count,
            null_percentage=null_percentage,
            unique_count=unique_count,
            unique_percentage=unique_percentage,
            min_value=min_value,
            max_value=max_value,
            mean_value=mean_value,
            std_value=std_value,
            sample_values=sample_values,
            profiled_at=datetime.now(timezone.utc).replace(tzinfo=None)
        )
        
        self.profile_history.append(profile)
        
        return profile
    
    def detect_outliers(
        self,
        data: pd.DataFrame,
        column: str,
        method: str = "iqr"
    ) -> Dict[str, Any]:
        """Detect outliers in a column.
        
        Args:
            data: Data to analyze
            column: Column to analyze
            method: Outlier detection method (iqr, zscore)
        
        Returns:
            Outlier detection results
        """
        series = data[column].dropna()
        
        if not pd.api.types.is_numeric_dtype(series):
            return {'error': 'Column is not numeric'}
        
        outliers = []
        
        if method == "iqr":
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = series[(series < lower_bound) | (series > upper_bound)]
        
        elif method == "zscore":
            mean = series.mean()
            std = series.std()
            z_scores = (series - mean) / std
            outliers = series[abs(z_scores) > 3]
        
        return {
            'column': column,
            'method': method,
            'outlier_count': len(outliers),
            'outlier_percentage': (len(outliers) / len(series)) * 100,
            'outlier_values': outliers.tolist()[:10]  # Limit to 10
        }
    
    def compare_profiles(
        self,
        profile_id_1: str,
        profile_id_2: str
    ) -> Dict[str, Any]:
        """Compare two profiles.
        
        Args:
            profile_id_1: First profile ID
            profile_id_2: Second profile ID
        
        Returns:
            Comparison results
        """
        profile1 = next((p for p in self.profile_history if p.profile_id == profile_id_1), None)
        profile2 = next((p for p in self.profile_history if p.profile_id == profile_id_2), None)
        
        if not profile1 or not profile2:
            return {'error': 'One or both profiles not found'}
        
        return {
            'field': profile1.field,
            'null_count_change': profile2.null_count - profile1.null_count,
            'unique_count_change': profile2.unique_count - profile1.unique_count,
            'min_value_change': (
                profile2.min_value - profile1.min_value 
                if profile1.min_value is not None and profile2.min_value is not None 
                else None
            ),
            'max_value_change': (
                profile2.max_value - profile1.max_value 
                if profile1.max_value is not None and profile2.max_value is not None 
                else None
            ),
            'mean_value_change': (
                profile2.mean_value - profile1.mean_value 
                if profile1.mean_value is not None and profile2.mean_value is not None 
                else None
            )
        }
    
    def get_profile_summary(self, field: Optional[str] = None) -> Dict[str, Any]:
        """Get profile summary.
        
        Args:
            field: Filter by field (optional)
        
        Returns:
            Profile summary
        """
        profiles = self.profile_history
        
        if field:
            profiles = [p for p in profiles if p.field == field]
        
        if not profiles:
            return {'message': 'No profiles found'}
        
        # Aggregate statistics
        total_nulls = sum(p.null_count for p in profiles)
        avg_null_percentage = sum(p.null_percentage for p in profiles) / len(profiles)
        
        return {
            'total_profiles': len(profiles),
            'total_nulls': total_nulls,
            'average_null_percentage': avg_null_percentage,
            'fields_profiled': list(set(p.field for p in profiles))
        }
