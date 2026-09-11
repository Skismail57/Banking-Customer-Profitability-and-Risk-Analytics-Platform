"""Quality metrics calculation for data quality assessment."""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import logging

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class QualityMetrics:
    """Data quality metrics for a dataset."""
    
    # Overall score (0-100)
    dq_score: float
    
    # Dimension scores (0-100 each)
    completeness: float
    validity: float
    uniqueness: float
    consistency: float
    referential_integrity: float
    
    # Detailed metrics
    total_rows: int
    total_columns: int
    total_cells: int
    
    # Missing values
    missing_cells: int
    missing_percentage: float
    columns_with_missing: List[str]
    
    # Duplicates
    duplicate_rows: int
    duplicate_percentage: float
    
    # Validation errors
    validation_errors: int
    validation_error_percentage: float
    
    # Additional context
    table_name: str = ""
    timestamp: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "dq_score": self.dq_score,
            "dimensions": {
                "completeness": self.completeness,
                "validity": self.validity,
                "uniqueness": self.uniqueness,
                "consistency": self.consistency,
                "referential_integrity": self.referential_integrity
            },
            "details": {
                "total_rows": self.total_rows,
                "total_columns": self.total_columns,
                "total_cells": self.total_cells,
                "missing_cells": self.missing_cells,
                "missing_percentage": self.missing_percentage,
                "columns_with_missing": self.columns_with_missing,
                "duplicate_rows": self.duplicate_rows,
                "duplicate_percentage": self.duplicate_percentage,
                "validation_errors": self.validation_errors,
                "validation_error_percentage": self.validation_error_percentage
            },
            "table_name": self.table_name,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }


class QualityCalculator:
    """Calculate data quality metrics for DataFrames."""
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """Initialize quality calculator.
        
        Args:
            weights: Weights for each dimension (default: equal weights)
        """
        self.weights = weights or {
            "completeness": 0.25,
            "validity": 0.30,
            "uniqueness": 0.20,
            "consistency": 0.15,
            "referential_integrity": 0.10
        }
        
        # Validate weights sum to 1
        total_weight = sum(self.weights.values())
        if not np.isclose(total_weight, 1.0, atol=0.01):
            logger.warning(f"Weights sum to {total_weight}, normalizing to 1.0")
            for key in self.weights:
                self.weights[key] /= total_weight
    
    def calculate(self, df: pd.DataFrame, validation_result: Optional[Any] = None,
                  table_name: str = "") -> QualityMetrics:
        """Calculate comprehensive quality metrics.
        
        Args:
            df: DataFrame to analyze
            validation_result: Optional validation result from schema validation
            table_name: Name of the table
        
        Returns:
            QualityMetrics object with all metrics
        """
        from datetime import datetime, timezone
        
        total_rows = len(df)
        total_columns = len(df.columns)
        total_cells = total_rows * total_columns
        
        if total_rows == 0:
            return QualityMetrics(
                dq_score=0.0,
                completeness=0.0,
                validity=0.0,
                uniqueness=0.0,
                consistency=0.0,
                referential_integrity=0.0,
                total_rows=0,
                total_columns=total_columns,
                total_cells=0,
                missing_cells=0,
                missing_percentage=0.0,
                columns_with_missing=[],
                duplicate_rows=0,
                duplicate_percentage=0.0,
                validation_errors=0,
                validation_error_percentage=0.0,
                table_name=table_name,
                timestamp=datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
            )
        
        # Calculate individual dimensions
        completeness = self._calculate_completeness(df)
        validity = self._calculate_validity(df, validation_result)
        uniqueness = self._calculate_uniqueness(df)
        consistency = self._calculate_consistency(df)
        referential_integrity = self._calculate_referential_integrity(df)
        
        # Calculate overall DQ score
        dq_score = (
            completeness * self.weights["completeness"] +
            validity * self.weights["validity"] +
            uniqueness * self.weights["uniqueness"] +
            consistency * self.weights["consistency"] +
            referential_integrity * self.weights["referential_integrity"]
        ) * 100
        
        # Detailed metrics
        missing_cells = df.isnull().sum().sum()
        missing_percentage = (missing_cells / total_cells) * 100
        columns_with_missing = df.columns[df.isnull().any()].tolist()
        
        duplicate_rows = df.duplicated().sum()
        duplicate_percentage = (duplicate_rows / total_rows) * 100
        
        validation_errors = validation_result.invalid_rows if validation_result else 0
        validation_error_percentage = (validation_errors / total_rows) * 100
        
        return QualityMetrics(
            dq_score=round(dq_score, 2),
            completeness=round(completeness * 100, 2),
            validity=round(validity * 100, 2),
            uniqueness=round(uniqueness * 100, 2),
            consistency=round(consistency * 100, 2),
            referential_integrity=round(referential_integrity * 100, 2),
            total_rows=total_rows,
            total_columns=total_columns,
            total_cells=total_cells,
            missing_cells=int(missing_cells),
            missing_percentage=round(missing_percentage, 2),
            columns_with_missing=columns_with_missing,
            duplicate_rows=int(duplicate_rows),
            duplicate_percentage=round(duplicate_percentage, 2),
            validation_errors=validation_errors,
            validation_error_percentage=round(validation_error_percentage, 2),
            table_name=table_name,
            timestamp=datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
        )
    
    def _calculate_completeness(self, df: pd.DataFrame) -> float:
        """Calculate completeness score (1 - missing percentage).
        
        Args:
            df: DataFrame to analyze
        
        Returns:
            Completeness score between 0 and 1
        """
        total_cells = len(df) * len(df.columns)
        if total_cells == 0:
            return 0.0
        
        missing_cells = df.isnull().sum().sum()
        return 1.0 - (missing_cells / total_cells)
    
    def _calculate_validity(self, df: pd.DataFrame, validation_result: Optional[Any]) -> float:
        """Calculate validity score based on validation results.
        
        Args:
            df: DataFrame to analyze
            validation_result: Optional validation result
        
        Returns:
            Validity score between 0 and 1
        """
        if validation_result is None:
            # If no validation result, assume valid
            return 1.0
        
        if hasattr(validation_result, 'validity_rate'):
            return validation_result.validity_rate
        
        total_rows = len(df)
        if total_rows == 0:
            return 0.0
        
        invalid_rows = validation_result.invalid_rows if hasattr(validation_result, 'invalid_rows') else 0
        return 1.0 - (invalid_rows / total_rows)
    
    def _calculate_uniqueness(self, df: pd.DataFrame) -> float:
        """Calculate uniqueness score (1 - duplicate percentage).
        
        Args:
            df: DataFrame to analyze
        
        Returns:
            Uniqueness score between 0 and 1
        """
        total_rows = len(df)
        if total_rows == 0:
            return 0.0
        
        duplicate_rows = df.duplicated().sum()
        return 1.0 - (duplicate_rows / total_rows)
    
    def _calculate_consistency(self, df: pd.DataFrame) -> float:
        """Calculate consistency score based on data type consistency.
        
        Args:
            df: DataFrame to analyze
        
        Returns:
            Consistency score between 0 and 1
        """
        if len(df) == 0:
            return 0.0
        
        # Check for mixed types in object columns
        consistency_score = 1.0
        
        for column in df.select_dtypes(include=['object']).columns:
            # Check if column has mixed types
            non_null_values = df[column].dropna()
            if len(non_null_values) > 0:
                types = set(type(v).__name__ for v in non_null_values)
                if len(types) > 1:
                    # Penalize for mixed types
                    consistency_score *= 0.9
        
        return max(0.0, consistency_score)
    
    def _calculate_referential_integrity(self, df: pd.DataFrame) -> float:
        """Calculate referential integrity score.
        
        This is a placeholder - actual implementation would check foreign key
        relationships against dimension tables.
        
        Args:
            df: DataFrame to analyze
        
        Returns:
            Referential integrity score between 0 and 1
        """
        # Placeholder: assume integrity is good if no obvious issues
        # In production, this would check FK relationships
        return 1.0
    
    def calculate_column_metrics(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Calculate metrics for each column.
        
        Args:
            df: DataFrame to analyze
        
        Returns:
            Dictionary mapping column names to their metrics
        """
        column_metrics = {}
        
        for column in df.columns:
            col_data = df[column]
            total_count = len(col_data)
            null_count = col_data.isnull().sum()
            non_null_count = total_count - null_count
            
            unique_count = col_data.nunique()
            
            metrics = {
                "total_count": total_count,
                "null_count": int(null_count),
                "null_percentage": round((null_count / total_count) * 100, 2) if total_count > 0 else 0,
                "non_null_count": int(non_null_count),
                "unique_count": int(unique_count),
                "unique_percentage": round((unique_count / total_count) * 100, 2) if total_count > 0 else 0,
                "dtype": str(col_data.dtype)
            }
            
            # Add numeric statistics if applicable
            if pd.api.types.is_numeric_dtype(col_data):
                metrics["min"] = col_data.min() if non_null_count > 0 else None
                metrics["max"] = col_data.max() if non_null_count > 0 else None
                metrics["mean"] = round(col_data.mean(), 2) if non_null_count > 0 else None
                metrics["std"] = round(col_data.std(), 2) if non_null_count > 0 else None
            
            # Add string statistics if applicable
            if pd.api.types.is_string_dtype(col_data) or col_data.dtype == 'object':
                metrics["avg_length"] = round(col_data.str.len().mean(), 2) if non_null_count > 0 else None
                metrics["max_length"] = col_data.str.len().max() if non_null_count > 0 else None
            
            column_metrics[column] = metrics
        
        return column_metrics
