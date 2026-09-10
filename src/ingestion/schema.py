"""Schema detection and validation utilities."""

from typing import Dict, List, Any, Optional, Tuple
import logging

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class SchemaDetector:
    """Detect and analyze DataFrame schema."""
    
    @staticmethod
    def detect_schema(df: pd.DataFrame) -> Dict[str, Any]:
        """Detect schema from DataFrame.
        
        Args:
            df: DataFrame to analyze
        
        Returns:
            Dictionary containing schema information
        """
        schema = {
            "columns": [],
            "dtypes": {},
            "null_counts": {},
            "null_percentages": {},
            "unique_counts": {},
            "sample_values": {}
        }
        
        for column in df.columns:
            col_data = df[column]
            
            # Data type
            dtype = str(col_data.dtype)
            schema["dtypes"][column] = dtype
            schema["columns"].append(column)
            
            # Null information
            null_count = col_data.isnull().sum()
            null_percentage = null_count / len(df) if len(df) > 0 else 0
            schema["null_counts"][column] = int(null_count)
            schema["null_percentages"][column] = round(float(null_percentage), 4)
            
            # Unique count
            unique_count = col_data.nunique()
            schema["unique_counts"][column] = int(unique_count)
            
            # Sample values (first non-null values)
            non_null_values = col_data.dropna()
            if len(non_null_values) > 0:
                sample_size = min(5, len(non_null_values))
                sample_values = non_null_values.head(sample_size).tolist()
                schema["sample_values"][column] = sample_values
        
        return schema
    
    @staticmethod
    def infer_column_type(column: pd.Series) -> str:
        """Infer semantic type of a column.
        
        Args:
            column: pandas Series
        
        Returns:
            Inferred type: numeric, datetime, categorical, boolean, text
        """
        dtype = column.dtype
        
        # Check for datetime
        if pd.api.types.is_datetime64_any_dtype(dtype):
            return "datetime"
        
        # Check for numeric
        if pd.api.types.is_numeric_dtype(dtype):
            # Check if it's actually an integer identifier
            if dtype == "int64" or dtype == "int32":
                unique_ratio = column.nunique() / len(column)
                if unique_ratio > 0.95:  # High cardinality integers likely IDs
                    return "id"
                return "numeric"
            return "numeric"
        
        # Check for boolean
        if dtype == "bool":
            return "boolean"
        
        # Check for categorical (low cardinality strings)
        if dtype == "object" or dtype == "string":
            unique_count = column.nunique()
            total_count = len(column)
            
            if unique_count <= 10:  # Low cardinality
                return "categorical"
            elif unique_count / total_count > 0.9:  # High cardinality
                return "id"
            else:
                return "text"
        
        return "unknown"
    
    @staticmethod
    def detect_key_candidates(df: pd.DataFrame) -> Dict[str, List[str]]:
        """Detect potential primary and foreign key candidates.
        
        Args:
            df: DataFrame to analyze
        
        Returns:
            Dictionary with 'primary_keys' and 'foreign_keys' lists
        """
        candidates = {
            "primary_keys": [],
            "foreign_keys": []
        }
        
        for column in df.columns:
            col_data = df[column]
            unique_count = col_data.nunique()
            total_count = len(col_data)
            null_count = col_data.isnull().sum()
            
            # Primary key candidates: unique, no nulls, high cardinality
            if unique_count == total_count and null_count == 0:
                candidates["primary_keys"].append(column)
            
            # Foreign key candidates: some nulls allowed, not unique
            elif unique_count < total_count and (unique_count / total_count) > 0.5:
                candidates["foreign_keys"].append(column)
        
        return candidates


class SchemaValidator:
    """Validate DataFrame against expected schema."""
    
    def __init__(self, expected_schema: Dict[str, Any]):
        """Initialize validator.
        
        Args:
            expected_schema: Expected schema dictionary with:
                - required_columns: List of required column names
                - column_types: Dict mapping column names to expected types
                - nullable: Dict mapping column names to boolean (whether nulls allowed)
        """
        self.expected_schema = expected_schema
    
    def validate(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Validate DataFrame against expected schema.
        
        Args:
            df: DataFrame to validate
        
        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []
        
        # Check required columns
        required_columns = self.expected_schema.get("required_columns", [])
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            errors.append(f"Missing required columns: {missing_columns}")
        
        # Check column types
        column_types = self.expected_schema.get("column_types", {})
        for column, expected_type in column_types.items():
            if column in df.columns:
                actual_type = str(df[column].dtype)
                if not self._types_compatible(actual_type, expected_type):
                    errors.append(
                        f"Column '{column}' has type '{actual_type}', expected '{expected_type}'"
                    )
        
        # Check nullable constraints
        nullable = self.expected_schema.get("nullable", {})
        for column, is_nullable in nullable.items():
            if column in df.columns:
                null_count = df[column].isnull().sum()
                if not is_nullable and null_count > 0:
                    errors.append(f"Column '{column}' has {null_count} null values but is not nullable")
        
        return len(errors) == 0, errors
    
    def _types_compatible(self, actual: str, expected: str) -> bool:
        """Check if actual type is compatible with expected type.
        
        Args:
            actual: Actual dtype string
            expected: Expected dtype string
        
        Returns:
            True if types are compatible
        """
        # Normalize type strings
        actual_lower = actual.lower()
        expected_lower = expected.lower()
        
        # Exact match
        if actual_lower == expected_lower:
            return True
        
        # Numeric compatibility
        numeric_types = ["int64", "int32", "int16", "int8", "float64", "float32"]
        if actual_lower in numeric_types and expected_lower in numeric_types:
            return True
        
        # String/object compatibility
        if actual_lower in ["object", "string"] and expected_lower in ["object", "string"]:
            return True
        
        return False


class DataQualityChecker:
    """Check data quality metrics."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize quality checker.
        
        Args:
            config: Configuration dictionary with:
                - min_row_count: Minimum acceptable row count
                - max_null_percentage: Maximum acceptable null percentage (0-1)
                - handle_duplicates: Whether to check for duplicates
        """
        self.config = config
    
    def check(self, df: pd.DataFrame) -> Tuple[bool, Dict[str, Any]]:
        """Perform data quality checks.
        
        Args:
            df: DataFrame to check
        
        Returns:
            Tuple of (passed, quality_report)
        """
        report = {
            "row_count": len(df),
            "column_count": len(df.columns),
            "null_counts": {},
            "null_percentages": {},
            "duplicate_count": df.duplicated().sum(),
            "checks": {}
        }
        
        passed = True
        
        # Check minimum row count
        min_row_count = self.config.get("min_row_count", 1)
        row_count_check = len(df) >= min_row_count
        report["checks"]["min_row_count"] = {
            "passed": row_count_check,
            "expected": min_row_count,
            "actual": len(df)
        }
        if not row_count_check:
            passed = False
        
        # Check null percentages
        max_null_percentage = self.config.get("max_null_percentage", 0.95)
        for column in df.columns:
            null_count = df[column].isnull().sum()
            null_percentage = null_count / len(df) if len(df) > 0 else 0
            
            report["null_counts"][column] = int(null_count)
            report["null_percentages"][column] = round(float(null_percentage), 4)
            
            column_passed = null_percentage <= max_null_percentage
            report["checks"][f"null_percentage_{column}"] = {
                "passed": column_passed,
                "expected": max_null_percentage,
                "actual": null_percentage
            }
            if not column_passed:
                passed = False
        
        # Check for duplicates
        if self.config.get("handle_duplicates", True):
            duplicate_count = df.duplicated().sum()
            report["duplicate_count"] = int(duplicate_count)
            duplicate_passed = duplicate_count == 0
            report["checks"]["no_duplicates"] = {
                "passed": duplicate_passed,
                "actual": duplicate_count
            }
            if not duplicate_passed:
                passed = False
        
        return passed, report
