"""Unit tests for transaction analytics base classes."""

import pytest
from datetime import date

from src.transaction_analytics.base import (
    TransactionKPI,
    AggregationPeriod,
    KPIDefinition,
    TransactionAnalyticsBase,
)


class TestTransactionKPI:
    """Tests for TransactionKPI enum."""
    
    def test_kpi_enum_values(self):
        """Test KPI enum has expected values."""
        assert TransactionKPI.TRANSACTION_COUNT.value == "transaction_count"
        assert TransactionKPI.TRANSACTION_VALUE.value == "transaction_value"
        assert TransactionKPI.AVG_TRANSACTION_VALUE.value == "avg_transaction_value"


class TestAggregationPeriod:
    """Tests for AggregationPeriod enum."""
    
    def test_period_enum_values(self):
        """Test period enum has expected values."""
        assert AggregationPeriod.DAILY.value == "daily"
        assert AggregationPeriod.WEEKLY.value == "weekly"
        assert AggregationPeriod.MONTHLY.value == "monthly"
        assert AggregationPeriod.QUARTERLY.value == "quarterly"
        assert AggregationPeriod.YEARLY.value == "yearly"


class TestKPIDefinition:
    """Tests for KPIDefinition dataclass."""
    
    def test_kpi_definition_creation(self):
        """Test creating KPI definition."""
        kpi = KPIDefinition(
            name=TransactionKPI.TRANSACTION_COUNT,
            description="Total number of transactions",
            data_type="numeric",
            calculation_method="COUNT(transaction_id)",
            business_definition="Count of all transactions"
        )
        
        assert kpi.name == TransactionKPI.TRANSACTION_COUNT
        assert kpi.data_type == "numeric"
    
    def test_to_dict(self):
        """Test serialization to dictionary."""
        kpi = KPIDefinition(
            name=TransactionKPI.TRANSACTION_VALUE,
            description="Total transaction value",
            data_type="currency",
            calculation_method="SUM(amount)",
            business_definition="Sum of transaction amounts"
        )
        
        data_dict = kpi.to_dict()
        
        assert data_dict["name"] == "transaction_value"
        assert data_dict["data_type"] == "currency"
        assert "calculation_method" in data_dict


class TestTransactionAnalyticsBase:
    """Tests for TransactionAnalyticsBase class."""
    
    def test_initialization(self):
        """Test base class initialization."""
        base = TransactionAnalyticsBase(as_of_date=date(2024, 1, 15))
        
        assert base.as_of_date == date(2024, 1, 15)
        assert len(base.kpi_registry) > 0
    
    def test_kpi_registration(self):
        """Test KPI registration."""
        base = TransactionAnalyticsBase()
        
        # Check standard KPIs are registered
        assert "transaction_count" in base.kpi_registry
        assert "transaction_value" in base.kpi_registry
        assert "avg_transaction_value" in base.kpi_registry
    
    def test_get_kpi_definition(self):
        """Test getting KPI definition."""
        base = TransactionAnalyticsBase()
        
        kpi_def = base.get_kpi_definition("transaction_count")
        
        assert kpi_def is not None
        assert kpi_def.name == TransactionKPI.TRANSACTION_COUNT
    
    def test_get_kpi_definition_not_found(self):
        """Test getting non-existent KPI."""
        base = TransactionAnalyticsBase()
        
        kpi_def = base.get_kpi_definition("nonexistent_kpi")
        
        assert kpi_def is None
    
    def test_get_all_kpi_definitions(self):
        """Test getting all KPI definitions."""
        base = TransactionAnalyticsBase()
        
        all_kpis = base.get_all_kpi_definitions()
        
        assert len(all_kpis) > 0
        assert "transaction_count" in all_kpis
        assert "transaction_value" in all_kpis
