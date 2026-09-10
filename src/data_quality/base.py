"""Base classes and utilities for data quality validation."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import logging

import pandas as pd
import pandera as pa
from pandera.typing import DataFrame, Series

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of data quality validation."""
    
    table_name: str
    is_valid: bool
    validation_time: datetime
    total_rows: int
    valid_rows: int
    invalid_rows: int
    errors: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "table_name": self.table_name,
            "is_valid": self.is_valid,
            "validation_time": self.validation_time.isoformat(),
            "total_rows": self.total_rows,
            "valid_rows": self.valid_rows,
            "invalid_rows": self.invalid_rows,
            "errors": self.errors,
            "warnings": self.warnings,
            "metrics": self.metrics
        }
    
    @property
    def validity_rate(self) -> float:
        """Calculate validity rate."""
        if self.total_rows == 0:
            return 0.0
        return self.valid_rows / self.total_rows


class BaseSchema(pa.DataFrameModel):
    """Base schema with common validation logic."""
    
    def __init__(self, *args, **kwargs):
        """Initialize base schema."""
        super().__init__(*args, **kwargs)
    
    @classmethod
    def validate_with_report(cls, df: pd.DataFrame, table_name: str) -> ValidationResult:
        """Validate DataFrame and generate detailed report.
        
        Args:
            df: DataFrame to validate
            table_name: Name of the table being validated
        
        Returns:
            ValidationResult with detailed information
        """
        validation_time = datetime.utcnow()
        total_rows = len(df)
        errors = []
        warnings = []
        
        try:
            # Run Pandera validation
            validated_df = cls.validate(df)
            valid_rows = len(validated_df)
            invalid_rows = total_rows - valid_rows
            
            # Check for common issues
            warnings.extend(cls._check_warnings(df))
            
            # Calculate basic metrics
            metrics = cls._calculate_metrics(df)
            
            result = ValidationResult(
                table_name=table_name,
                is_valid=True,
                validation_time=validation_time,
                total_rows=total_rows,
                valid_rows=valid_rows,
                invalid_rows=invalid_rows,
                errors=errors,
                warnings=warnings,
                metrics=metrics
            )
            
        except pa.errors.SchemaError as e:
            # Parse schema errors
            error_dict = e.failure_cases.to_dict("records") if hasattr(e, "failure_cases") else []
            
            for err in error_dict:
                errors.append({
                    "column": err.get("column", "unknown"),
                    "check": err.get("check", "unknown"),
                    "failure_case": str(err.get("failure_case", "unknown")),
                    "row_number": err.get("failure_case", "unknown")
                })
            
            result = ValidationResult(
                table_name=table_name,
                is_valid=False,
                validation_time=validation_time,
                total_rows=total_rows,
                valid_rows=0,
                invalid_rows=total_rows,
                errors=errors,
                warnings=warnings,
                metrics={}
            )
        
        return result
    
    @classmethod
    def _check_warnings(cls, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Check for warning conditions (non-critical issues).
        
        Args:
            df: DataFrame to check
        
        Returns:
            List of warning dictionaries
        """
        warnings = []
        
        # Check for high null percentages
        for column in df.columns:
            null_count = df[column].isnull().sum()
            null_percentage = null_count / len(df) if len(df) > 0 else 0
            
            if null_percentage > 0.5 and null_percentage < 0.95:
                warnings.append({
                    "type": "high_null_percentage",
                    "column": column,
                    "null_percentage": round(null_percentage, 4),
                    "message": f"Column '{column}' has {round(null_percentage * 100, 2)}% null values"
                })
        
        return warnings
    
    @classmethod
    def _calculate_metrics(cls, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate basic quality metrics.
        
        Args:
            df: DataFrame to analyze
        
        Returns:
            Dictionary of metrics
        """
        metrics = {}
        
        if len(df) == 0:
            return metrics
        
        # Completeness
        total_cells = len(df) * len(df.columns)
        null_cells = df.isnull().sum().sum()
        metrics["completeness"] = 1.0 - (null_cells / total_cells)
        
        # Uniqueness (based on all columns)
        duplicate_rows = df.duplicated().sum()
        metrics["uniqueness"] = 1.0 - (duplicate_rows / len(df))
        
        return metrics


class CustomCheck:
    """Custom validation checks for business rules."""
    
    @staticmethod
    def non_negative(series: Series) -> Series[bool]:
        """Check that all values are non-negative.
        
        Args:
            series: Series to check
        
        Returns:
            Boolean series indicating valid rows
        """
        return series >= 0
    
    @staticmethod
    def positive(series: Series) -> Series[bool]:
        """Check that all values are positive (> 0).
        
        Args:
            series: Series to check
        
        Returns:
            Boolean series indicating valid rows
        """
        return series > 0
    
    @staticmethod
    def in_range(series: Series, min_val: float, max_val: float) -> Series[bool]:
        """Check that values are within specified range.
        
        Args:
            series: Series to check
            min_val: Minimum value (inclusive)
            max_val: Maximum value (inclusive)
        
        Returns:
            Boolean series indicating valid rows
        """
        return (series >= min_val) & (series <= max_val)
    
    @staticmethod
    def valid_percentage(series: Series) -> Series[bool]:
        """Check that values are valid percentages (0-100).
        
        Args:
            series: Series to check
        
        Returns:
            Boolean series indicating valid rows
        """
        return (series >= 0) & (series <= 100)
    
    @staticmethod
    def valid_rate(series: Series) -> Series[bool]:
        """Check that values are valid rates (0-1).
        
        Args:
            series: Series to check
        
        Returns:
            Boolean series indicating valid rows
        """
        return (series >= 0) & (series <= 1)
    
    @staticmethod
    def valid_credit_score(series: Series) -> Series[bool]:
        """Check that values are valid credit scores (300-850).
        
        Args:
            series: Series to check
        
        Returns:
            Boolean series indicating valid rows
        """
        return (series >= 300) & (series <= 850)
    
    @staticmethod
    def valid_date_order(start_date: Series, end_date: Series) -> Series[bool]:
        """Check that start date is before or equal to end date.
        
        Args:
            start_date: Start date series
            end_date: End date series
        
        Returns:
            Boolean series indicating valid rows
        """
        return start_date <= end_date
    
    @staticmethod
    def valid_currency_code(series: Series) -> Series[bool]:
        """Check that values are valid ISO 4217 currency codes.
        
        Args:
            series: Series to check
        
        Returns:
            Boolean series indicating valid rows
        """
        valid_codes = {"INR", "USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY"}
        return series.isin(valid_codes)
    
    @staticmethod
    def not_future_date(series: Series) -> Series[bool]:
        """Check that dates are not in the future.
        
        Args:
            series: Series to check
        
        Returns:
            Boolean series indicating valid rows
        """
        return series <= datetime.utcnow()
    
    @staticmethod
    def not_past_date(series: Series, years: int = 100) -> Series[bool]:
        """Check that dates are not too far in the past.
        
        Args:
            series: Series to check
            years: Maximum years in the past
        
        Returns:
            Boolean series indicating valid rows
        """
        cutoff_date = datetime.utcnow().replace(year=datetime.utcnow().year - years)
        return series >= cutoff_date
