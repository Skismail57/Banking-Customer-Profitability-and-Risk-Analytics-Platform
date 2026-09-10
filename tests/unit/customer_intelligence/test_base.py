"""Unit tests for Customer 360 base classes."""

import pytest
from datetime import date, datetime, timedelta
import pandas as pd

from src.customer_intelligence.base import (
    Customer360Base,
    FeatureDefinition,
    FeatureCategory,
    TemporalWindow,
)


class TestFeatureDefinition:
    """Tests for FeatureDefinition dataclass."""
    
    def test_feature_definition_creation(self):
        """Test creating feature definition."""
        feature = FeatureDefinition(
            name="test_feature",
            category=FeatureCategory.DEMOGRAPHIC,
            description="Test feature description",
            data_type="numeric"
        )
        
        assert feature.name == "test_feature"
        assert feature.category == FeatureCategory.DEMOGRAPHIC
        assert feature.is_temporal is False
    
    def test_to_dict(self):
        """Test serialization to dictionary."""
        feature = FeatureDefinition(
            name="age",
            category=FeatureCategory.DEMOGRAPHIC,
            description="Customer age",
            data_type="numeric",
            is_temporal=True,
            calculation_window_days=30
        )
        
        data_dict = feature.to_dict()
        
        assert data_dict["name"] == "age"
        assert data_dict["category"] == "demographic"
        assert data_dict["is_temporal"] is True
        assert data_dict["calculation_window_days"] == 30


class TestCustomer360Base:
    """Tests for Customer360Base class."""
    
    def test_register_feature(self):
        """Test feature registration."""
        base = Customer360Base()
        
        feature = FeatureDefinition(
            name="test_feature",
            category=FeatureCategory.DEMOGRAPHIC,
            description="Test",
            data_type="numeric"
        )
        
        base.register_feature(feature)
        
        assert "test_feature" in base.feature_registry
        assert base.get_feature_definition("test_feature") == feature
    
    def test_get_feature_definition_not_found(self):
        """Test getting non-existent feature."""
        base = Customer360Base()
        
        result = base.get_feature_definition("nonexistent")
        
        assert result is None
    
    def test_get_features_by_category(self):
        """Test filtering features by category."""
        base = Customer360Base()
        
        base.register_feature(FeatureDefinition(
            name="age", category=FeatureCategory.DEMOGRAPHIC,
            description="Age", data_type="numeric"
        ))
        base.register_feature(FeatureDefinition(
            name="income", category=FeatureCategory.DEMOGRAPHIC,
            description="Income", data_type="numeric"
        ))
        base.register_feature(FeatureDefinition(
            name="transaction_count", category=FeatureCategory.TRANSACTION,
            description="Transaction count", data_type="numeric"
        ))
        
        demographic_features = base.get_features_by_category(FeatureCategory.DEMOGRAPHIC)
        
        assert len(demographic_features) == 2
        assert all(f.category == FeatureCategory.DEMOGRAPHIC for f in demographic_features)
    
    def test_ensure_temporal_safety(self):
        """Test temporal safety filtering."""
        base = Customer360Base(as_of_date=date(2024, 1, 15))
        
        df = pd.DataFrame({
            "date_col": pd.to_datetime([
                "2024-01-10",
                "2024-01-15",
                "2024-01-20",  # Future - should be filtered
                "2024-01-01"
            ]),
            "value": [1, 2, 3, 4]
        })
        
        filtered_df = base.ensure_temporal_safety(df, "date_col")
        
        assert len(filtered_df) == 3  # Future date filtered out
        assert all(filtered_df["date_col"] <= pd.Timestamp("2024-01-15"))
    
    def test_validate_required_columns_success(self):
        """Test column validation with all required columns present."""
        base = Customer360Base()
        
        df = pd.DataFrame({
            "col1": [1, 2, 3],
            "col2": ["a", "b", "c"],
            "col3": [4.5, 5.5, 6.5]
        })
        
        result = base.validate_required_columns(df, ["col1", "col2"])
        
        assert result is True
    
    def test_validate_required_columns_failure(self):
        """Test column validation with missing columns."""
        base = Customer360Base()
        
        df = pd.DataFrame({
            "col1": [1, 2, 3],
            "col2": ["a", "b", "c"]
        })
        
        result = base.validate_required_columns(df, ["col1", "col3"])
        
        assert result is False


class TestTemporalWindow:
    """Tests for TemporalWindow helper."""
    
    def test_get_window_start(self):
        """Test calculating window start date."""
        as_of_date = date(2024, 1, 15)
        window_start = TemporalWindow.get_window_start(as_of_date, days=30)
        
        expected = date(2023, 12, 16)
        assert window_start == expected
    
    def test_partition_windows(self):
        """Test partitioning time into windows."""
        as_of_date = date(2024, 1, 15)
        windows = TemporalWindow.partition_windows(as_of_date, window_days=30, num_windows=3)
        
        assert len(windows) == 3
        assert windows[0][0] < windows[0][1]
        assert windows[1][0] < windows[1][1]
