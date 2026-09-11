"""Base classes and utilities for data quality validation."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple, Callable
import logging

import pandas as pd
import pandera as pa
from pandera.typing import DataFrame, Series

logger = logging.getLogger(__name__)

_FIELD_VALIDATION_REGISTRY: Dict[str, Dict[str, Any]] = {}


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
    def _ensure_nullable_columns_present(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Ensure all declared nullable columns exist in the DataFrame.

        For nullable columns that are declared but missing from the input,
        add them with NaN values. This allows Pandera strict validation to
        pass when legitimately-optional columns (e.g. churn_date, closed_date)
        are absent, while still validating their types/ranges when present.

        Args:
            df: Input DataFrame

        Returns:
            DataFrame with all declared nullable columns present
        """
        df = df.copy()
        if hasattr(cls, "to_schema"):
            try:
                schema_obj = cls.to_schema()
                columns = getattr(schema_obj, "columns", {})
                for col_name, col_schema in columns.items():
                    if col_name not in df.columns:
                        nullable = getattr(col_schema, "nullable", False)
                        if nullable:
                            dtype = getattr(col_schema, "dtype", None)
                            if dtype is not None:
                                try:
                                    import numpy as np
                                    df[col_name] = pd.Series(
                                        [np.nan] * len(df),
                                        dtype="object"
                                    )
                                except Exception:
                                    df[col_name] = pd.NA
                            else:
                                df[col_name] = pd.NA
            except Exception:
                pass
        return df

    @classmethod
    def _run_field_validations(cls, df: pd.DataFrame, errors: List[Dict[str, Any]]) -> int:
        """Run custom field-level validations registered for this schema.

        Args:
            df: DataFrame to validate
            errors: Error list to extend (mutated in-place)

        Returns:
            Number of invalid rows detected
        """
        invalid_rows_mask = pd.Series([False] * len(df), index=df.index)
        validators = getattr(cls, "_field_validators", {})
        for col_name, rules in validators.items():
            if col_name not in df.columns:
                continue
            series = df[col_name]
            null_mask = series.isna()
            for rule_name, rule_fn in rules.items():
                try:
                    check_result = rule_fn(series)
                    fail_mask = (~check_result) & (~null_mask)
                except Exception:
                    fail_mask = pd.Series([False] * len(df), index=df.index)
                fail_count = int(fail_mask.sum())
                if fail_count > 0:
                    invalid_rows_mask |= fail_mask
                    fail_indices = df.index[fail_mask].tolist()[:5]
                    errors.append({
                        "column": col_name,
                        "check": rule_name,
                        "failure_case": (
                            f"{fail_count} row(s) failed {rule_name}; "
                            f"sample indices: {fail_indices}"
                        ),
                        "row_number": ",".join(str(i) for i in fail_indices) or "unknown",
                    })
        return int(invalid_rows_mask.sum())

    @classmethod
    def _run_cross_field_validations(cls, df: pd.DataFrame, errors: List[Dict[str, Any]]) -> int:
        """Run cross-column / multi-field business-rule validations.

        Schemas can define a class-level dict ``_cross_field_validators``
        mapping rule labels to callables (or string method names on the
        schema class). Each callable receives the DataFrame and returns
        a boolean Series where ``True`` indicates an INVALID row.

        Args:
            df: DataFrame to validate
            errors: Error list to extend (mutated in-place)

        Returns:
            Number of invalid rows detected
        """
        invalid_rows_mask = pd.Series([False] * len(df), index=df.index)

        rules = getattr(cls, "_cross_field_validators", {})
        for rule_name, rule_ref in rules.items():
            try:
                if isinstance(rule_ref, str):
                    rule_fn = getattr(cls, rule_ref)
                    check_result = rule_fn(df)
                elif isinstance(rule_ref, classmethod):
                    check_result = rule_ref.__func__(cls, df)
                elif isinstance(rule_ref, staticmethod):
                    check_result = rule_ref.__func__(df)
                else:
                    check_result = rule_ref(df)

                if isinstance(check_result, tuple) and len(check_result) == 2:
                    fail_mask, extra_msg = check_result
                else:
                    fail_mask = check_result
                    extra_msg = ""
                fail_mask = pd.Series(fail_mask).fillna(False).astype(bool)
                if len(fail_mask) != len(df):
                    fail_mask = fail_mask.reindex(df.index, fill_value=False)
                fail_count = int(fail_mask.sum())
                if fail_count > 0:
                    invalid_rows_mask |= fail_mask
                    fail_indices = df.index[fail_mask].tolist()[:5]
                    msg = f"{fail_count} row(s) failed {rule_name}"
                    if extra_msg:
                        msg += f"; {extra_msg}"
                    msg += f"; sample indices: {fail_indices}"
                    errors.append({
                        "column": "multiple",
                        "check": rule_name,
                        "failure_case": msg,
                        "row_number": ",".join(str(i) for i in fail_indices) or "unknown",
                    })
            except Exception:
                pass

        return int(invalid_rows_mask.sum())

    @classmethod
    def validate_with_report(cls, df: pd.DataFrame, table_name: str) -> ValidationResult:
        """Validate DataFrame and generate detailed report.
        
        Args:
            df: DataFrame to validate
            table_name: Name of the table being validated
        
        Returns:
            ValidationResult with detailed information
        """
        validation_time = datetime.now(timezone.utc).replace(tzinfo=None)
        total_rows = len(df)
        errors = []
        warnings = []
        
        try:
            prepared_df = cls._ensure_nullable_columns_present(df)
            validated_df = cls.validate(prepared_df)
            valid_rows = len(validated_df)
            invalid_rows = total_rows - valid_rows

            field_invalid = cls._run_field_validations(prepared_df, errors)
            cross_invalid = cls._run_cross_field_validations(prepared_df, errors)
            custom_invalid = max(field_invalid, cross_invalid)

            if custom_invalid > 0:
                invalid_rows = max(invalid_rows, custom_invalid)
                valid_rows = total_rows - invalid_rows
                overall_is_valid = False
            else:
                overall_is_valid = True
            
            warnings.extend(cls._check_warnings(prepared_df))
            metrics = cls._calculate_metrics(prepared_df)

            if not overall_is_valid:
                result = ValidationResult(
                    table_name=table_name,
                    is_valid=False,
                    validation_time=validation_time,
                    total_rows=total_rows,
                    valid_rows=valid_rows,
                    invalid_rows=invalid_rows,
                    errors=errors,
                    warnings=warnings,
                    metrics=metrics,
                )
            else:
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
            error_dict = []
            if hasattr(e, "failure_cases") and e.failure_cases is not None:
                fc = e.failure_cases
                if hasattr(fc, "to_dict") and callable(getattr(fc, "to_dict")):
                    try:
                        error_dict = fc.to_dict("records")
                    except Exception:
                        error_dict = [{"error": str(fc)}]
                elif isinstance(fc, list):
                    error_dict = [{"failure_case": str(item)} for item in fc]
                else:
                    error_dict = [{"failure_case": str(fc)}]
            
            for err in error_dict:
                if isinstance(err, dict):
                    errors.append({
                        "column": err.get("column", "unknown"),
                        "check": err.get("check", "unknown"),
                        "failure_case": str(err.get("failure_case", "unknown")),
                        "row_number": str(err.get("index", "unknown"))
                    })
                else:
                    errors.append({"failure_case": str(err)})
            
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
        
        total_cells = len(df) * len(df.columns)
        null_cells = df.isnull().sum().sum()
        metrics["completeness"] = 1.0 - (null_cells / total_cells)
        
        duplicate_rows = df.duplicated().sum()
        metrics["uniqueness"] = 1.0 - (duplicate_rows / len(df))
        
        return metrics


class CustomCheck:
    """Custom validation checks for business rules."""

    @staticmethod
    def _to_bool_series(raw) -> Series[bool]:
        """Ensure comparison result is a boolean Series with bool dtype."""
        if isinstance(raw, pd.Series):
            return raw.astype(bool)
        return pd.Series(raw, dtype=bool)

    @staticmethod
    def non_negative(series: Series) -> Series[bool]:
        """Check that all values are non-negative.

        Args:
            series: Series to check

        Returns:
            Boolean series indicating valid rows
        """
        return CustomCheck._to_bool_series(series >= 0)

    @staticmethod
    def positive(series: Series) -> Series[bool]:
        """Check that all values are positive (> 0).

        Args:
            series: Series to check

        Returns:
            Boolean series indicating valid rows
        """
        return CustomCheck._to_bool_series(series > 0)

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
        return CustomCheck._to_bool_series((series >= min_val) & (series <= max_val))

    @staticmethod
    def valid_percentage(series: Series) -> Series[bool]:
        """Check that values are valid percentages (0-100).

        Args:
            series: Series to check

        Returns:
            Boolean series indicating valid rows
        """
        return CustomCheck._to_bool_series((series >= 0) & (series <= 100))

    @staticmethod
    def valid_rate(series: Series) -> Series[bool]:
        """Check that values are valid rates (0-1).

        Args:
            series: Series to check

        Returns:
            Boolean series indicating valid rows
        """
        return CustomCheck._to_bool_series((series >= 0) & (series <= 1))

    @staticmethod
    def valid_credit_score(series: Series) -> Series[bool]:
        """Check that values are valid credit scores (300-850).

        Args:
            series: Series to check

        Returns:
            Boolean series indicating valid rows
        """
        return CustomCheck._to_bool_series((series >= 300) & (series <= 850))

    @staticmethod
    def valid_date_order(start_date: Series, end_date: Series) -> Series[bool]:
        """Check that start date is before or equal to end date.

        Args:
            start_date: Start date series
            end_date: End date series

        Returns:
            Boolean series indicating valid rows
        """
        return CustomCheck._to_bool_series(start_date <= end_date)

    @staticmethod
    def valid_currency_code(series: Series) -> Series[bool]:
        """Check that values are valid ISO 4217 currency codes.

        Args:
            series: Series to check

        Returns:
            Boolean series indicating valid rows
        """
        valid_codes = {"INR", "USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY"}
        return CustomCheck._to_bool_series(series.isin(valid_codes))

    @staticmethod
    def not_future_date(series: Series) -> Series[bool]:
        """Check that dates are not in the future.

        Args:
            series: Series to check

        Returns:
            Boolean series indicating valid rows
        """
        return CustomCheck._to_bool_series(series <= datetime.now(timezone.utc).replace(tzinfo=None))

    @staticmethod
    def not_past_date(series: Series, years: int = 100) -> Series[bool]:
        """Check that dates are not too far in the past.

        Args:
            series: Series to check
            years: Maximum years in the past

        Returns:
            Boolean series indicating valid rows
        """
        cutoff_date = datetime.now(timezone.utc).replace(tzinfo=None).replace(year=datetime.now(timezone.utc).replace(tzinfo=None).year - years)
        return CustomCheck._to_bool_series(series >= cutoff_date)
