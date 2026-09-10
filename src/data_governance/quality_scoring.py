"""Data Quality Scoring.

This module implements comprehensive data quality scoring to assess the
quality of data across multiple dimensions.

Key Quality Dimensions:
- Completeness (missing values)
- Accuracy (data validation)
- Consistency (format and range)
- Uniqueness (duplicates)
- Timeliness (data freshness)
- Validity (business rules)

NOTE: This is an analytical/educational model for decision support.
It does not make actual lending decisions.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import date, timedelta
from enum import Enum
import logging

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class QualityDimension(Enum):
    """Data quality dimensions."""
    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    CONSISTENCY = "consistency"
    UNIQUENESS = "uniqueness"
    TIMELINESS = "timeliness"
    VALIDITY = "validity"


class QualityLevel(Enum):
    """Quality levels."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


class DataQualityScorer:
    """Score data quality across multiple dimensions.
    
    This class assesses data quality and provides actionable insights
    for improvement.
    
    Assumptions:
    - Quality thresholds are based on industry best practices
    - Data validation rules are defined per column
    - Freshness requirements are known for each dataset
    
    Limitations:
    - Thresholds may need calibration for specific use cases
    - Does not detect all types of data quality issues
    - May not capture semantic quality issues
    - Validation rules must be manually defined
    
    Fairness Considerations:
    - Ensure quality scoring is consistent across data sources
    - Check for disparate impact in quality assessments
    - Ensure quality metrics are not biased
    - Regular audit for bias in quality scoring
    """
    
    def __init__(self):
        """Initialize Data Quality Scorer."""
        # Quality thresholds (configurable)
        self.thresholds = {
            QualityDimension.COMPLETENESS: {'excellent': 0.95, 'good': 0.90, 'fair': 0.80, 'poor': 0.70},
            QualityDimension.ACCURACY: {'excellent': 0.98, 'good': 0.95, 'fair': 0.90, 'poor': 0.85},
            QualityDimension.CONSISTENCY: {'excellent': 0.95, 'good': 0.90, 'fair': 0.85, 'poor': 0.75},
            QualityDimension.UNIQUENESS: {'excellent': 0.99, 'good': 0.95, 'fair': 0.90, 'poor': 0.85},
            QualityDimension.TIMELINESS: {'excellent': 1, 'good': 7, 'fair': 14, 'poor': 30},  # days
            QualityDimension.VALIDITY: {'excellent': 0.98, 'good': 0.95, 'fair': 0.90, 'poor': 0.85}
        }
    
    def score_completeness(self, df: pd.DataFrame, critical_columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """Score data completeness (missing values).
        
        Args:
            df: DataFrame to score
            critical_columns: List of critical columns (weighted higher)
        
        Returns:
            Dictionary with completeness score
        """
        total_cells = len(df) * len(df.columns)
        missing_cells = df.isnull().sum().sum()
        
        completeness_score = 1 - (missing_cells / total_cells) if total_cells > 0 else 0
        
        # Critical column completeness
        critical_completeness = 1.0
        if critical_columns:
            critical_cols_present = [col for col in critical_columns if col in df.columns]
            if critical_cols_present:
                critical_missing = df[critical_cols_present].isnull().sum().sum()
                critical_total = len(df) * len(critical_cols_present)
                critical_completeness = 1 - (critical_missing / critical_total) if critical_total > 0 else 0
        
        # Column-level completeness
        column_completeness = {}
        for col in df.columns:
            col_completeness = 1 - (df[col].isnull().sum() / len(df))
            column_completeness[col] = float(col_completeness)
        
        quality_level = self._determine_quality_level(
            completeness_score,
            self.thresholds[QualityDimension.COMPLETENESS]
        )
        
        return {
            'dimension': QualityDimension.COMPLETENESS.value,
            'overall_score': float(completeness_score),
            'critical_completeness': float(critical_completeness),
            'column_completeness': column_completeness,
            'quality_level': quality_level.value,
            'missing_cells': int(missing_cells),
            'total_cells': int(total_cells)
        }
    
    def score_accuracy(self, df: pd.DataFrame, validation_rules: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Score data accuracy (validation rules).
        
        Args:
            df: DataFrame to score
            validation_rules: Dictionary of column validation rules
        
        Returns:
            Dictionary with accuracy score
        """
        if validation_rules is None:
            validation_rules = {}
        
        total_validations = 0
        passed_validations = 0
        validation_results = {}
        
        for col, rules in validation_rules.items():
            if col not in df.columns:
                continue
            
            col_data = df[col].dropna()
            
            for rule_name, rule_func in rules.items():
                total_validations += len(col_data)
                
                try:
                    passed = col_data.apply(rule_func).sum()
                    passed_validations += passed
                    validation_results[f"{col}.{rule_name}"] = {
                        'passed': int(passed),
                        'total': len(col_data),
                        'pass_rate': float(passed / len(col_data)) if len(col_data) > 0 else 0
                    }
                except Exception as e:
                    logger.warning(f"Validation error for {col}.{rule_name}: {e}")
        
        accuracy_score = passed_validations / total_validations if total_validations > 0 else 1.0
        
        quality_level = self._determine_quality_level(
            accuracy_score,
            self.thresholds[QualityDimension.ACCURACY]
        )
        
        return {
            'dimension': QualityDimension.ACCURACY.value,
            'overall_score': float(accuracy_score),
            'quality_level': quality_level.value,
            'validation_results': validation_results,
            'total_validations': int(total_validations),
            'passed_validations': int(passed_validations)
        }
    
    def score_consistency(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Score data consistency (format and range).
        
        Args:
            df: DataFrame to score
        
        Returns:
            Dictionary with consistency score
        """
        consistency_issues = 0
        total_checks = 0
        consistency_details = {}
        
        # Check for consistent data types
        for col in df.columns:
            total_checks += 1
            
            # Check if numeric column has non-numeric values
            if df[col].dtype in ['int64', 'float64']:
                # All values should be numeric
                if df[col].isnull().sum() < len(df):
                    try:
                        pd.to_numeric(df[col], errors='raise')
                    except:
                        consistency_issues += 1
                        consistency_details[col] = "Non-numeric values in numeric column"
            
            # Check for consistent date formats
            elif df[col].dtype == 'object':
                # Try to parse as date
                sample = df[col].dropna().head(100)
                if not sample.empty:
                    try:
                        pd.to_datetime(sample, errors='raise')
                    except:
                        # Not all are dates, that's okay
                        pass
        
        consistency_score = 1 - (consistency_issues / total_checks) if total_checks > 0 else 1.0
        
        quality_level = self._determine_quality_level(
            consistency_score,
            self.thresholds[QualityDimension.CONSISTENCY]
        )
        
        return {
            'dimension': QualityDimension.CONSISTENCY.value,
            'overall_score': float(consistency_score),
            'quality_level': quality_level.value,
            'consistency_issues': consistency_issues,
            'total_checks': total_checks,
            'consistency_details': consistency_details
        }
    
    def score_uniqueness(self, df: pd.DataFrame, key_columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """Score data uniqueness (duplicates).
        
        Args:
            df: DataFrame to score
            key_columns: List of columns that should be unique
        
        Returns:
            Dictionary with uniqueness score
        """
        total_rows = len(df)
        duplicate_rows = df.duplicated().sum()
        
        uniqueness_score = 1 - (duplicate_rows / total_rows) if total_rows > 0 else 1.0
        
        # Check key column uniqueness
        key_uniqueness = {}
        if key_columns:
            for col in key_columns:
                if col in df.columns:
                    col_duplicates = df[col].duplicated().sum()
                    col_uniqueness = 1 - (col_duplicates / len(df)) if len(df) > 0 else 1.0
                    key_uniqueness[col] = float(col_uniqueness)
        
        quality_level = self._determine_quality_level(
            uniqueness_score,
            self.thresholds[QualityDimension.UNIQUENESS]
        )
        
        return {
            'dimension': QualityDimension.UNIQUENESS.value,
            'overall_score': float(uniqueness_score),
            'quality_level': quality_level.value,
            'duplicate_rows': int(duplicate_rows),
            'total_rows': int(total_rows),
            'key_uniqueness': key_uniqueness
        }
    
    def score_timeliness(self, df: pd.DataFrame, date_column: str, max_age_days: int = 30) -> Dict[str, Any]:
        """Score data timeliness (freshness).
        
        Args:
            df: DataFrame to score
            date_column: Column with date information
            max_age_days: Maximum acceptable age in days
        
        Returns:
            Dictionary with timeliness score
        """
        if date_column not in df.columns:
            return {
                'dimension': QualityDimension.TIMELINESS.value,
                'overall_score': 0.0,
                'quality_level': QualityLevel.CRITICAL.value,
                'error': f"Date column {date_column} not found"
            }
        
        df[date_column] = pd.to_datetime(df[date_column])
        current_date = pd.Timestamp.now()
        
        # Calculate age of data
        max_date = df[date_column].max()
        age_days = (current_date - max_date).days
        
        # Score based on age
        if age_days <= self.thresholds[QualityDimension.TIMELINESS]['excellent']:
            timeliness_score = 1.0
        elif age_days <= self.thresholds[QualityDimension.TIMELINESS]['good']:
            timeliness_score = 0.8
        elif age_days <= self.thresholds[QualityDimension.TIMELINESS]['fair']:
            timeliness_score = 0.6
        elif age_days <= self.thresholds[QualityDimension.TIMELINESS]['poor']:
            timeliness_score = 0.4
        else:
            timeliness_score = 0.2
        
        quality_level = self._determine_quality_level(
            timeliness_score,
            self.thresholds[QualityDimension.TIMELINESS],
            is_timeliness=True
        )
        
        return {
            'dimension': QualityDimension.TIMELINESS.value,
            'overall_score': float(timeliness_score),
            'quality_level': quality_level.value,
            'max_date': max_date.isoformat(),
            'age_days': age_days,
            'max_age_days': max_age_days
        }
    
    def score_validity(self, df: pd.DataFrame, business_rules: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Score data validity (business rules).
        
        Args:
            df: DataFrame to score
            business_rules: Dictionary of business rules
        
        Returns:
            Dictionary with validity score
        """
        if business_rules is None:
            business_rules = {}
        
        total_rules = len(business_rules)
        passed_rules = 0
        rule_results = {}
        
        for rule_name, rule_func in business_rules.items():
            try:
                is_valid = rule_func(df)
                if is_valid:
                    passed_rules += 1
                rule_results[rule_name] = {
                    'passed': is_valid,
                    'description': 'Business rule validation'
                }
            except Exception as e:
                logger.warning(f"Business rule error for {rule_name}: {e}")
                rule_results[rule_name] = {
                    'passed': False,
                    'error': str(e)
                }
        
        validity_score = passed_rules / total_rules if total_rules > 0 else 1.0
        
        quality_level = self._determine_quality_level(
            validity_score,
            self.thresholds[QualityDimension.VALIDITY]
        )
        
        return {
            'dimension': QualityDimension.VALIDITY.value,
            'overall_score': float(validity_score),
            'quality_level': quality_level.value,
            'rule_results': rule_results,
            'total_rules': total_rules,
            'passed_rules': passed_rules
        }
    
    def generate_quality_report(
        self,
        df: pd.DataFrame,
        date_column: Optional[str] = None,
        critical_columns: Optional[List[str]] = None,
        key_columns: Optional[List[str]] = None,
        validation_rules: Optional[Dict[str, Any]] = None,
        business_rules: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive data quality report.
        
        Args:
            df: DataFrame to score
            date_column: Column with date information
            critical_columns: List of critical columns
            key_columns: List of key columns
            validation_rules: Dictionary of validation rules
            business_rules: Dictionary of business rules
        
        Returns:
            Dictionary with quality report
        """
        logger.info("Generating data quality report")
        
        report = {
            'completeness': self.score_completeness(df, critical_columns),
            'consistency': self.score_consistency(df),
            'uniqueness': self.score_uniqueness(df, key_columns),
            'accuracy': self.score_accuracy(df, validation_rules),
            'validity': self.score_validity(df, business_rules)
        }
        
        # Add timeliness if date column provided
        if date_column:
            report['timeliness'] = self.score_timeliness(df, date_column)
        
        # Calculate overall quality score
        dimension_scores = [
            v['overall_score'] for v in report.values()
            if isinstance(v, dict) and 'overall_score' in v
        ]
        overall_quality = np.mean(dimension_scores) if dimension_scores else 0
        
        # Determine overall quality level
        overall_level = self._determine_quality_level(
            overall_quality,
            {'excellent': 0.90, 'good': 0.80, 'fair': 0.70, 'poor': 0.60}
        )
        
        report['overall_quality'] = {
            'score': float(overall_quality),
            'level': overall_level.value
        }
        
        report['assumptions'] = [
            'Quality thresholds based on industry best practices',
            'Validation rules are defined per column',
            'Freshness requirements are known'
        ]
        
        report['limitations'] = [
            'Thresholds may need calibration',
            'Does not detect all quality issues',
            'May not capture semantic quality',
            'Validation rules must be manually defined'
        ]
        
        report['fairness_considerations'] = [
            'Ensure quality scoring is consistent',
            'Check for disparate impact in assessments',
            'Ensure quality metrics are not biased',
            'Regular audit for bias in quality scoring'
        ]
        
        logger.info("Data quality report generated")
        return report
    
    def _determine_quality_level(
        self,
        score: float,
        thresholds: Dict[str, float],
        is_timeliness: bool = False
    ) -> QualityLevel:
        """Determine quality level from score.
        
        Args:
            score: Quality score
            thresholds: Threshold values
            is_timeliness: Whether this is a timeliness score (lower is better)
        
        Returns:
            QualityLevel enum
        """
        if is_timeliness:
            # For timeliness, lower score (fewer days) is better
            if score <= thresholds['excellent']:
                return QualityLevel.EXCELLENT
            elif score <= thresholds['good']:
                return QualityLevel.GOOD
            elif score <= thresholds['fair']:
                return QualityLevel.FAIR
            elif score <= thresholds['poor']:
                return QualityLevel.POOR
            else:
                return QualityLevel.CRITICAL
        else:
            # For other dimensions, higher score is better
            if score >= thresholds['excellent']:
                return QualityLevel.EXCELLENT
            elif score >= thresholds['good']:
                return QualityLevel.GOOD
            elif score >= thresholds['fair']:
                return QualityLevel.FAIR
            elif score >= thresholds['poor']:
                return QualityLevel.POOR
            else:
                return QualityLevel.CRITICAL
