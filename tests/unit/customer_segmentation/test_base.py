"""Unit tests for customer segmentation base classes."""

import pytest

from src.customer_segmentation.base import (
    SegmentationMethod,
    SegmentDefinition,
    SegmentProfile,
    CustomerSegmentationBase,
)


class TestSegmentationMethod:
    """Tests for SegmentationMethod enum."""
    
    def test_method_enum_values(self):
        """Test SegmentationMethod enum has expected values."""
        assert SegmentationMethod.BUSINESS_RULES.value == "business_rules"
        assert SegmentationMethod.KMEANS.value == "kmeans"
        assert SegmentationMethod.HIERARCHICAL.value == "hierarchical"
        assert SegmentationMethod.DBSCAN.value == "dbscan"


class TestSegmentDefinition:
    """Tests for SegmentDefinition dataclass."""
    
    def test_segment_definition_creation(self):
        """Test creating segment definition."""
        segment = SegmentDefinition(
            name="high_value",
            description="High value customers",
            method=SegmentationMethod.BUSINESS_RULES,
            criteria={"profit_min": 50000},
            business_interpretation="High profitability segment",
            recommended_actions=["VIP service", "Retention"]
        )
        
        assert segment.name == "high_value"
        assert segment.method == SegmentationMethod.BUSINESS_RULES
    
    def test_to_dict(self):
        """Test serialization to dictionary."""
        segment = SegmentDefinition(
            name="test_segment",
            description="Test segment",
            method=SegmentationMethod.KMEANS,
            criteria={},
            business_interpretation="Test",
            recommended_actions=[]
        )
        
        data_dict = segment.to_dict()
        
        assert data_dict["name"] == "test_segment"
        assert data_dict["method"] == "kmeans"


class TestSegmentProfile:
    """Tests for SegmentProfile dataclass."""
    
    def test_segment_profile_creation(self):
        """Test creating segment profile."""
        profile = SegmentProfile(
            segment_name="segment_0",
            customer_count=100,
            percentage=25.0,
            characteristics={"profitability": {"mean": 50000}},
            business_metrics={"total_revenue": 1000000}
        )
        
        assert profile.segment_name == "segment_0"
        assert profile.customer_count == 100
        assert profile.percentage == 25.0
    
    def test_to_dict(self):
        """Test serialization to dictionary."""
        profile = SegmentProfile(
            segment_name="segment_1",
            customer_count=50,
            percentage=12.5,
            characteristics={},
            business_metrics={}
        )
        
        data_dict = profile.to_dict()
        
        assert data_dict["segment_name"] == "segment_1"
        assert data_dict["customer_count"] == 50


class TestCustomerSegmentationBase:
    """Tests for CustomerSegmentationBase class."""
    
    def test_initialization(self):
        """Test base class initialization."""
        base = CustomerSegmentationBase()
        
        assert base.segment_registry == {}
    
    def test_register_segment(self):
        """Test segment registration."""
        base = CustomerSegmentationBase()
        
        segment = SegmentDefinition(
            name="test",
            description="Test",
            method=SegmentationMethod.BUSINESS_RULES,
            criteria={},
            business_interpretation="Test",
            recommended_actions=[]
        )
        
        base.register_segment(segment)
        
        assert "test" in base.segment_registry
    
    def test_get_segment_definition(self):
        """Test getting segment definition."""
        base = CustomerSegmentationBase()
        
        segment = SegmentDefinition(
            name="test",
            description="Test",
            method=SegmentationMethod.BUSINESS_RULES,
            criteria={},
            business_interpretation="Test",
            recommended_actions=[]
        )
        
        base.register_segment(segment)
        
        retrieved = base.get_segment_definition("test")
        
        assert retrieved is not None
        assert retrieved.name == "test"
    
    def test_get_segment_definition_not_found(self):
        """Test getting non-existent segment."""
        base = CustomerSegmentationBase()
        
        retrieved = base.get_segment_definition("nonexistent")
        
        assert retrieved is None
