"""Unit tests for CLV analytics base classes."""

import pytest

from src.clv_analytics.base import (
    CLVType,
    CLVParameters,
    CLVBase,
)


class TestCLVType:
    """Tests for CLVType enum."""
    
    def test_clv_type_enum_values(self):
        """Test CLVType enum has expected values."""
        assert CLVType.HISTORICAL.value == "historical"
        assert CLVType.PREDICTED.value == "predicted"
        assert CLVType.ESTIMATED.value == "estimated"


class TestCLVParameters:
    """Tests for CLVParameters dataclass."""
    
    def test_clv_parameters_creation(self):
        """Test creating CLV parameters."""
        params = CLVParameters(
            discount_rate=0.10,
            retention_rate=0.80,
            time_horizon_years=5,
            average_revenue=1000,
            average_cost=800,
            average_profit=200
        )
        
        assert params.discount_rate == 0.10
        assert params.retention_rate == 0.80
        assert params.time_horizon_years == 5
    
    def test_to_dict(self):
        """Test serialization to dictionary."""
        params = CLVParameters(
            discount_rate=0.10,
            retention_rate=0.80,
            time_horizon_years=5
        )
        
        data_dict = params.to_dict()
        
        assert data_dict["discount_rate"] == 0.10
        assert data_dict["retention_rate"] == 0.80
        assert data_dict["time_horizon_years"] == 5


class TestCLVBase:
    """Tests for CLVBase class."""
    
    def test_initialization(self):
        """Test base class initialization."""
        base = CLVBase()
        
        assert base.as_of_date is not None
    
    def test_validate_parameters_valid(self):
        """Test parameter validation with valid parameters."""
        base = CLVBase()
        params = CLVParameters(
            discount_rate=0.10,
            retention_rate=0.80,
            time_horizon_years=5
        )
        
        assert base.validate_parameters(params) is True
    
    def test_validate_parameters_invalid_discount(self):
        """Test parameter validation with invalid discount rate."""
        base = CLVBase()
        params = CLVParameters(
            discount_rate=1.5,  # Invalid (> 1)
            retention_rate=0.80,
            time_horizon_years=5
        )
        
        assert base.validate_parameters(params) is False
    
    def test_validate_parameters_invalid_retention(self):
        """Test parameter validation with invalid retention rate."""
        base = CLVBase()
        params = CLVParameters(
            discount_rate=0.10,
            retention_rate=1.5,  # Invalid (> 1)
            time_horizon_years=5
        )
        
        assert base.validate_parameters(params) is False
    
    def test_validate_parameters_invalid_horizon(self):
        """Test parameter validation with invalid time horizon."""
        base = CLVBase()
        params = CLVParameters(
            discount_rate=0.10,
            retention_rate=0.80,
            time_horizon_years=0  # Invalid (<= 0)
        )
        
        assert base.validate_parameters(params) is False
    
    def test_get_default_parameters(self):
        """Test getting default parameters."""
        base = CLVBase()
        params = base.get_default_parameters()
        
        assert params.discount_rate == 0.10
        assert params.retention_rate == 0.80
        assert params.time_horizon_years == 5
