"""Unit tests for profitability analytics base classes."""

import pytest

from src.profitability_analytics.base import (
    ValueType,
    ProfitabilityValue,
    ProfitabilityMetric,
    MetricDefinition,
    ProfitabilityBase,
)


class TestValueType:
    """Tests for ValueType enum."""
    
    def test_value_type_enum_values(self):
        """Test ValueType enum has expected values."""
        assert ValueType.OBSERVED.value == "observed"
        assert ValueType.ESTIMATED.value == "estimated"
        assert ValueType.MODELED.value == "modeled"
        assert ValueType.MISSING.value == "missing"


class TestProfitabilityValue:
    """Tests for ProfitabilityValue dataclass."""
    
    def test_profitability_value_creation_observed(self):
        """Test creating observed profitability value."""
        value = ProfitabilityValue(
            value=1000.0,
            value_type=ValueType.OBSERVED,
            source="transaction_data"
        )
        
        assert value.value == 1000.0
        assert value.value_type == ValueType.OBSERVED
        assert value.confidence == 1.0  # Observed values have 100% confidence
    
    def test_profitability_value_creation_estimated(self):
        """Test creating estimated profitability value."""
        value = ProfitabilityValue(
            value=500.0,
            value_type=ValueType.ESTIMATED,
            source="allocated",
            confidence=0.7
        )
        
        assert value.value == 500.0
        assert value.value_type == ValueType.ESTIMATED
        assert value.confidence == 0.7
    
    def test_profitability_value_default_confidence(self):
        """Test default confidence for estimated/modeled values."""
        value = ProfitabilityValue(
            value=200.0,
            value_type=ValueType.ESTIMATED,
            source="calculated"
        )
        
        assert value.confidence == 0.5  # Default confidence
    
    def test_to_dict(self):
        """Test serialization to dictionary."""
        value = ProfitabilityValue(
            value=1000.0,
            value_type=ValueType.OBSERVED,
            source="transaction_data",
            metadata={"row_count": 100}
        )
        
        data_dict = value.to_dict()
        
        assert data_dict["value"] == 1000.0
        assert data_dict["value_type"] == "observed"
        assert data_dict["confidence"] == 1.0
        assert data_dict["metadata"]["row_count"] == 100


class TestProfitabilityMetric:
    """Tests for ProfitabilityMetric enum."""
    
    def test_metric_enum_values(self):
        """Test ProfitabilityMetric enum has expected values."""
        assert ProfitabilityMetric.INTEREST_INCOME.value == "interest_income"
        assert ProfitabilityMetric.NET_PROFIT.value == "net_profit"
        assert ProfitabilityMetric.PROFIT_MARGIN.value == "profit_margin"


class TestMetricDefinition:
    """Tests for MetricDefinition dataclass."""
    
    def test_metric_definition_creation(self):
        """Test creating metric definition."""
        metric = MetricDefinition(
            name=ProfitabilityMetric.NET_PROFIT,
            description="Net profit after all costs",
            data_type="currency",
            calculation_method="gross_revenue - total_cost",
            business_definition="Revenue minus all costs",
            default_value_type=ValueType.ESTIMATED
        )
        
        assert metric.name == ProfitabilityMetric.NET_PROFIT
        assert metric.data_type == "currency"
        assert metric.default_value_type == ValueType.ESTIMATED
    
    def test_to_dict(self):
        """Test serialization to dictionary."""
        metric = MetricDefinition(
            name=ProfitabilityMetric.GROSS_REVENUE,
            description="Total gross revenue",
            data_type="currency",
            calculation_method="SUM(all_revenue_components)",
            business_definition="Sum of all revenue components",
            default_value_type=ValueType.OBSERVED
        )
        
        data_dict = metric.to_dict()
        
        assert data_dict["name"] == "gross_revenue"
        assert data_dict["data_type"] == "currency"
        assert data_dict["default_value_type"] == "observed"


class TestProfitabilityBase:
    """Tests for ProfitabilityBase class."""
    
    def test_initialization(self):
        """Test base class initialization."""
        base = ProfitabilityBase()
        
        assert len(base.metric_registry) > 0
    
    def test_metric_registration(self):
        """Test metric registration."""
        base = ProfitabilityBase()
        
        # Check standard metrics are registered
        assert "interest_income" in base.metric_registry
        assert "net_profit" in base.metric_registry
        assert "profit_margin" in base.metric_registry
    
    def test_get_metric_definition(self):
        """Test getting metric definition."""
        base = ProfitabilityBase()
        
        metric_def = base.get_metric_definition("net_profit")
        
        assert metric_def is not None
        assert metric_def.name == ProfitabilityMetric.NET_PROFIT
    
    def test_get_metric_definition_not_found(self):
        """Test getting non-existent metric."""
        base = ProfitabilityBase()
        
        metric_def = base.get_metric_definition("nonexistent_metric")
        
        assert metric_def is None
    
    def test_get_all_metric_definitions(self):
        """Test getting all metric definitions."""
        base = ProfitabilityBase()
        
        all_metrics = base.get_all_metric_definitions()
        
        assert len(all_metrics) > 0
        assert "interest_income" in all_metrics
        assert "net_profit" in all_metrics
    
    def test_get_metrics_by_value_type(self):
        """Test filtering metrics by value type."""
        base = ProfitabilityBase()
        
        observed_metrics = base.get_metrics_by_value_type(ValueType.OBSERVED)
        estimated_metrics = base.get_metrics_by_value_type(ValueType.ESTIMATED)
        modeled_metrics = base.get_metrics_by_value_type(ValueType.MODELED)
        
        assert len(observed_metrics) > 0
        assert len(estimated_metrics) > 0
        assert len(modeled_metrics) > 0
