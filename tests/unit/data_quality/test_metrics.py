"""Unit tests for quality metrics calculation."""

import pytest
import pandas as pd
import numpy as np

from src.data_quality.metrics import QualityMetrics, QualityCalculator


class TestQualityMetrics:
    """Tests for QualityMetrics dataclass."""
    
    def test_quality_metrics_creation(self):
        """Test creating quality metrics."""
        metrics = QualityMetrics(
            dq_score=85.5,
            completeness=90.0,
            validity=95.0,
            uniqueness=80.0,
            consistency=85.0,
            referential_integrity=90.0,
            total_rows=1000,
            total_columns=10,
            total_cells=10000,
            missing_cells=100,
            missing_percentage=1.0,
            columns_with_missing=["col1", "col2"],
            duplicate_rows=5,
            duplicate_percentage=0.5,
            validation_errors=10,
            validation_error_percentage=1.0
        )
        
        assert metrics.dq_score == 85.5
        assert metrics.completeness == 90.0
        assert metrics.total_rows == 1000
    
    def test_to_dict(self):
        """Test serialization to dictionary."""
        metrics = QualityMetrics(
            dq_score=85.5,
            completeness=90.0,
            validity=95.0,
            uniqueness=80.0,
            consistency=85.0,
            referential_integrity=90.0,
            total_rows=100,
            total_columns=5,
            total_cells=500,
            missing_cells=10,
            missing_percentage=2.0,
            columns_with_missing=["col1"],
            duplicate_rows=0,
            duplicate_percentage=0.0,
            validation_errors=0,
            validation_error_percentage=0.0
        )
        
        data_dict = metrics.to_dict()
        
        assert data_dict["dq_score"] == 85.5
        assert "dimensions" in data_dict
        assert "details" in data_dict


class TestQualityCalculator:
    """Tests for QualityCalculator."""
    
    def test_calculate_perfect_quality(self):
        """Test calculation with perfect quality data."""
        df = pd.DataFrame({
            "col1": [1, 2, 3, 4, 5],
            "col2": ["a", "b", "c", "d", "e"],
            "col3": [1.1, 2.2, 3.3, 4.4, 5.5]
        })
        
        calculator = QualityCalculator()
        metrics = calculator.calculate(df, table_name="test_table")
        
        assert metrics.dq_score == 100.0
        assert metrics.completeness == 100.0
        assert metrics.uniqueness == 100.0
        assert metrics.missing_cells == 0
    
    def test_calculate_with_missing_values(self):
        """Test calculation with missing values."""
        df = pd.DataFrame({
            "col1": [1, 2, None, 4, 5],
            "col2": ["a", None, "c", "d", "e"],
            "col3": [1.1, 2.2, 3.3, None, 5.5]
        })
        
        calculator = QualityCalculator()
        metrics = calculator.calculate(df, table_name="test_table")
        
        assert metrics.completeness < 100.0
        assert metrics.missing_cells == 3
        assert "col1" in metrics.columns_with_missing
        assert "col2" in metrics.columns_with_missing
    
    def test_calculate_with_duplicates(self):
        """Test calculation with duplicate rows."""
        df = pd.DataFrame({
            "col1": [1, 2, 2, 3, 4],
            "col2": ["a", "b", "b", "c", "d"]
        })
        
        calculator = QualityCalculator()
        metrics = calculator.calculate(df, table_name="test_table")
        
        assert metrics.uniqueness < 100.0
        assert metrics.duplicate_rows == 1
    
    def test_calculate_empty_dataframe(self):
        """Test calculation with empty DataFrame."""
        df = pd.DataFrame()
        
        calculator = QualityCalculator()
        metrics = calculator.calculate(df, table_name="test_table")
        
        assert metrics.dq_score == 0.0
        assert metrics.total_rows == 0
    
    def test_calculate_column_metrics(self):
        """Test column-level metrics calculation."""
        df = pd.DataFrame({
            "col1": [1, 2, 3, 4, 5],
            "col2": [10, 20, 30, 40, 50],
            "col3": ["a", "b", "c", "d", "e"]
        })
        
        calculator = QualityCalculator()
        column_metrics = calculator.calculate_column_metrics(df)
        
        assert "col1" in column_metrics
        assert "col2" in column_metrics
        assert "col3" in column_metrics
        
        # Check numeric column metrics
        assert column_metrics["col1"]["min"] == 1
        assert column_metrics["col1"]["max"] == 5
        assert column_metrics["col1"]["mean"] == 3.0
        
        # Check string column metrics
        assert "avg_length" in column_metrics["col3"]
    
    def test_custom_weights(self):
        """Test calculation with custom weights."""
        df = pd.DataFrame({
            "col1": [1, 2, 3, 4, 5],
            "col2": ["a", "b", "c", "d", "e"]
        })
        
        custom_weights = {
            "completeness": 0.5,
            "validity": 0.3,
            "uniqueness": 0.1,
            "consistency": 0.05,
            "referential_integrity": 0.05
        }
        
        calculator = QualityCalculator(weights=custom_weights)
        metrics = calculator.calculate(df, table_name="test_table")
        
        assert metrics.dq_score == 100.0
    
    def test_weight_normalization(self):
        """Test weight normalization when weights don't sum to 1."""
        df = pd.DataFrame({
            "col1": [1, 2, 3],
            "col2": ["a", "b", "c"]
        })
        
        invalid_weights = {
            "completeness": 0.5,
            "validity": 0.5,
            "uniqueness": 0.5,
            "consistency": 0.5,
            "referential_integrity": 0.5
        }
        
        calculator = QualityCalculator(weights=invalid_weights)
        metrics = calculator.calculate(df, table_name="test_table")
        
        # Should still work despite invalid weights
        assert metrics.dq_score >= 0
        assert metrics.dq_score <= 100
