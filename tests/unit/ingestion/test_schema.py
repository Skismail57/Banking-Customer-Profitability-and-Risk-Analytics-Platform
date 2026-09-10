"""Unit tests for schema detection and validation."""

import pytest
import pandas as pd
import numpy as np

from src.ingestion.schema import SchemaDetector, SchemaValidator, DataQualityChecker


class TestSchemaDetector:
    """Tests for SchemaDetector."""
    
    def test_detect_schema(self):
        """Test schema detection."""
        df = pd.DataFrame({
            "col1": [1, 2, 3],
            "col2": ["a", "b", "c"],
            "col3": [1.1, 2.2, 3.3]
        })
        
        schema = SchemaDetector.detect_schema(df)
        
        assert "col1" in schema["columns"]
        assert "col2" in schema["columns"]
        assert "col3" in schema["columns"]
        assert schema["dtypes"]["col1"] == "int64"
        assert schema["null_counts"]["col1"] == 0
        assert schema["unique_counts"]["col1"] == 3
    
    def test_detect_schema_with_nulls(self):
        """Test schema detection with null values."""
        df = pd.DataFrame({
            "col1": [1, np.nan, 3],
            "col2": ["a", None, "c"]
        })
        
        schema = SchemaDetector.detect_schema(df)
        
        assert schema["null_counts"]["col1"] == 1
        assert schema["null_percentages"]["col1"] == pytest.approx(0.3333, rel=0.01)
    
    def test_infer_column_type_numeric(self):
        """Test inferring numeric column type."""
        col = pd.Series([1, 2, 3, 4, 5])
        inferred_type = SchemaDetector.infer_column_type(col)
        
        assert inferred_type == "numeric"
    
    def test_infer_column_type_datetime(self):
        """Test inferring datetime column type."""
        col = pd.Series(pd.date_range("2024-01-01", periods=5))
        inferred_type = SchemaDetector.infer_column_type(col)
        
        assert inferred_type == "datetime"
    
    def test_infer_column_type_categorical(self):
        """Test inferring categorical column type."""
        col = pd.Series(["A", "B", "A", "B", "C"])
        inferred_type = SchemaDetector.infer_column_type(col)
        
        assert inferred_type == "categorical"
    
    def test_detect_key_candidates(self):
        """Test detection of key candidates."""
        df = pd.DataFrame({
            "id": [1, 2, 3, 4],
            "name": ["Alice", "Bob", "Charlie", "David"],
            "category": ["A", "B", "A", "B"]
        })
        
        candidates = SchemaDetector.detect_key_candidates(df)
        
        assert "id" in candidates["primary_keys"]
        assert "category" in candidates["foreign_keys"]


class TestSchemaValidator:
    """Tests for SchemaValidator."""
    
    def test_validate_success(self):
        """Test successful schema validation."""
        df = pd.DataFrame({
            "col1": [1, 2, 3],
            "col2": ["a", "b", "c"]
        })
        
        schema = {
            "required_columns": ["col1", "col2"],
            "column_types": {
                "col1": "int64"
            },
            "nullable": {
                "col1": False
            }
        }
        
        validator = SchemaValidator(schema)
        is_valid, errors = validator.validate(df)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_missing_columns(self):
        """Test validation with missing required columns."""
        df = pd.DataFrame({
            "col1": [1, 2, 3]
        })
        
        schema = {
            "required_columns": ["col1", "col2"]
        }
        
        validator = SchemaValidator(schema)
        is_valid, errors = validator.validate(df)
        
        assert is_valid is False
        assert "Missing required columns" in errors[0]
    
    def test_validate_nullable_violation(self):
        """Test validation with nullable constraint violation."""
        df = pd.DataFrame({
            "col1": [1, None, 3]
        })
        
        schema = {
            "nullable": {
                "col1": False
            }
        }
        
        validator = SchemaValidator(schema)
        is_valid, errors = validator.validate(df)
        
        assert is_valid is False
        assert "null values but is not nullable" in errors[0]


class TestDataQualityChecker:
    """Tests for DataQualityChecker."""
    
    def test_check_min_row_count_pass(self):
        """Test minimum row count check - pass."""
        df = pd.DataFrame({"col1": range(10)})
        
        config = {"min_row_count": 5}
        checker = DataQualityChecker(config)
        passed, report = checker.check(df)
        
        assert passed is True
        assert report["checks"]["min_row_count"]["passed"] is True
    
    def test_check_min_row_count_fail(self):
        """Test minimum row count check - fail."""
        df = pd.DataFrame({"col1": range(3)})
        
        config = {"min_row_count": 5}
        checker = DataQualityChecker(config)
        passed, report = checker.check(df)
        
        assert passed is False
        assert report["checks"]["min_row_count"]["passed"] is False
    
    def test_check_null_percentage(self):
        """Test null percentage check."""
        df = pd.DataFrame({
            "col1": [1, 2, None, 4, 5]
        })
        
        config = {"max_null_percentage": 0.5}
        checker = DataQualityChecker(config)
        passed, report = checker.check(df)
        
        assert passed is True  # 20% null is less than 50% threshold
        assert report["null_percentages"]["col1"] == 0.2
    
    def test_check_duplicates(self):
        """Test duplicate check."""
        df = pd.DataFrame({
            "col1": [1, 2, 2, 3]
        })
        
        config = {"handle_duplicates": True}
        checker = DataQualityChecker(config)
        passed, report = checker.check(df)
        
        assert passed is False  # Has duplicates
        assert report["duplicate_count"] == 1
