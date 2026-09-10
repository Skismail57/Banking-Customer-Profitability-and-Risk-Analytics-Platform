"""Unit tests for data quality base classes."""

import pytest
from datetime import datetime
import pandas as pd
import numpy as np

from src.data_quality.base import BaseSchema, ValidationResult, CustomCheck


class TestValidationResult:
    """Tests for ValidationResult dataclass."""
    
    def test_validation_result_creation(self):
        """Test creating validation result."""
        result = ValidationResult(
            table_name="test_table",
            is_valid=True,
            validation_time=datetime.utcnow(),
            total_rows=100,
            valid_rows=95,
            invalid_rows=5
        )
        
        assert result.table_name == "test_table"
        assert result.is_valid is True
        assert result.validity_rate == 0.95
    
    def test_validity_rate_calculation(self):
        """Test validity rate calculation."""
        result = ValidationResult(
            table_name="test",
            is_valid=True,
            validation_time=datetime.utcnow(),
            total_rows=200,
            valid_rows=180,
            invalid_rows=20
        )
        
        assert result.validity_rate == 0.9
    
    def test_validity_rate_zero_rows(self):
        """Test validity rate with zero rows."""
        result = ValidationResult(
            table_name="test",
            is_valid=True,
            validation_time=datetime.utcnow(),
            total_rows=0,
            valid_rows=0,
            invalid_rows=0
        )
        
        assert result.validity_rate == 0.0
    
    def test_to_dict(self):
        """Test serialization to dictionary."""
        result = ValidationResult(
            table_name="test",
            is_valid=True,
            validation_time=datetime.utcnow(),
            total_rows=100,
            valid_rows=100,
            invalid_rows=0
        )
        
        data_dict = result.to_dict()
        
        assert data_dict["table_name"] == "test"
        assert data_dict["is_valid"] is True
        assert "validation_time" in data_dict


class TestCustomCheck:
    """Tests for custom validation checks."""
    
    def test_non_negative(self):
        """Test non-negative check."""
        series = pd.Series([0, 1, 2, 3])
        result = CustomCheck.non_negative(series)
        
        assert result.all()
    
    def test_non_negative_with_negative(self):
        """Test non-negative check with negative values."""
        series = pd.Series([0, 1, -1, 3])
        result = CustomCheck.non_negative(series)
        
        assert not result.all()
        assert result.iloc[2] is False
    
    def test_positive(self):
        """Test positive check."""
        series = pd.Series([1, 2, 3, 4])
        result = CustomCheck.positive(series)
        
        assert result.all()
    
    def test_positive_with_zero(self):
        """Test positive check with zero."""
        series = pd.Series([0, 1, 2, 3])
        result = CustomCheck.positive(series)
        
        assert not result.iloc[0]
    
    def test_in_range(self):
        """Test range check."""
        series = pd.Series([5, 10, 15, 20])
        result = CustomCheck.in_range(series, min_val=0, max_val=25)
        
        assert result.all()
    
    def test_in_range_out_of_bounds(self):
        """Test range check with out-of-bounds values."""
        series = pd.Series([5, 10, 30, 20])
        result = CustomCheck.in_range(series, min_val=0, max_val=25)
        
        assert not result.iloc[2]
    
    def test_valid_percentage(self):
        """Test valid percentage check."""
        series = pd.Series([0, 50, 100, 75])
        result = CustomCheck.valid_percentage(series)
        
        assert result.all()
    
    def test_valid_percentage_invalid(self):
        """Test valid percentage check with invalid values."""
        series = pd.Series([0, 50, 150, 75])
        result = CustomCheck.valid_percentage(series)
        
        assert not result.iloc[2]
    
    def test_valid_rate(self):
        """Test valid rate check."""
        series = pd.Series([0.0, 0.5, 1.0, 0.75])
        result = CustomCheck.valid_rate(series)
        
        assert result.all()
    
    def test_valid_credit_score(self):
        """Test valid credit score check."""
        series = pd.Series([300, 500, 700, 850])
        result = CustomCheck.valid_credit_score(series)
        
        assert result.all()
    
    def test_valid_credit_score_invalid(self):
        """Test valid credit score check with invalid values."""
        series = pd.Series([200, 500, 700, 900])
        result = CustomCheck.valid_credit_score(series)
        
        assert not result.iloc[0]
        assert not result.iloc[3]
    
    def test_valid_currency_code(self):
        """Test valid currency code check."""
        series = pd.Series(["USD", "EUR", "GBP", "JPY"])
        result = CustomCheck.valid_currency_code(series)
        
        assert result.all()
    
    def test_valid_currency_code_invalid(self):
        """Test valid currency code check with invalid codes."""
        series = pd.Series(["USD", "XXX", "GBP", "JPY"])
        result = CustomCheck.valid_currency_code(series)
        
        assert not result.iloc[1]
