"""Unit tests for churn analytics base classes."""

import pytest

from src.churn_analytics.base import (
    ChurnType,
    ChurnDefinition,
    ChurnBase,
)


class TestChurnType:
    """Tests for ChurnType enum."""
    
    def test_churn_type_enum_values(self):
        """Test ChurnType enum has expected values."""
        assert ChurnType.ACCOUNT_CLOSURE.value == "account_closure"
        assert ChurnType.INACTIVITY.value == "inactivity"
        assert ChurnType.BALANCE_DEPLETION.value == "balance_depletion"
        assert ChurnType.COMPOSITE.value == "composite"


class TestChurnDefinition:
    """Tests for ChurnDefinition dataclass."""
    
    def test_churn_definition_creation(self):
        """Test creating churn definition."""
        definition = ChurnDefinition(
            name="test_churn",
            churn_type=ChurnType.INACTIVITY,
            definition="Test definition",
            criteria={"threshold": 90},
            lookback_period_days=90,
            observation_window_days=30,
            data_requirements=["activity_data"],
            assumptions=["Assumption 1"],
            limitations=["Limitation 1"]
        )
        
        assert definition.name == "test_churn"
        assert definition.churn_type == ChurnType.INACTIVITY
    
    def test_to_dict(self):
        """Test serialization to dictionary."""
        definition = ChurnDefinition(
            name="test",
            churn_type=ChurnType.ACCOUNT_CLOSURE,
            definition="Test",
            criteria={},
            lookback_period_days=90,
            observation_window_days=30,
            data_requirements=[],
            assumptions=[],
            limitations=[]
        )
        
        data_dict = definition.to_dict()
        
        assert data_dict["name"] == "test"
        assert data_dict["churn_type"] == "account_closure"


class TestChurnBase:
    """Tests for ChurnBase class."""
    
    def test_initialization(self):
        """Test base class initialization."""
        base = ChurnBase()
        
        assert len(base.churn_definitions) > 0
    
    def test_standard_definitions_registered(self):
        """Test standard churn definitions are registered."""
        base = ChurnBase()
        
        assert "account_closure" in base.churn_definitions
        assert "inactivity_churn" in base.churn_definitions
        assert "balance_depletion_churn" in base.churn_definitions
        assert "composite_churn" in base.churn_definitions
    
    def test_get_churn_definition(self):
        """Test getting churn definition."""
        base = ChurnBase()
        
        definition = base.get_churn_definition("inactivity_churn")
        
        assert definition is not None
        assert definition.name == "inactivity_churn"
    
    def test_get_churn_definition_not_found(self):
        """Test getting non-existent churn definition."""
        base = ChurnBase()
        
        definition = base.get_churn_definition("nonexistent")
        
        assert definition is None
    
    def test_get_all_churn_definitions(self):
        """Test getting all churn definitions."""
        base = ChurnBase()
        
        all_definitions = base.get_all_churn_definitions()
        
        assert len(all_definitions) > 0
        assert "account_closure" in all_definitions
