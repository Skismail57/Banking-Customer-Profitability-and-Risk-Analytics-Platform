"""Unit tests for credit risk analytics base classes."""

import pytest

from src.credit_risk_analytics.base import (
    RiskIndicator,
    RiskBand,
    IndicatorDefinition,
    CreditRiskBase,
)


class TestRiskIndicator:
    """Tests for RiskIndicator enum."""
    
    def test_indicator_enum_values(self):
        """Test RiskIndicator enum has expected values."""
        assert RiskIndicator.TOTAL_LOAN_EXPOSURE.value == "total_loan_exposure"
        assert RiskIndicator.DAYS_PAST_DUE.value == "days_past_due"
        assert RiskIndicator.CREDIT_UTILIZATION.value == "credit_utilization"


class TestRiskBand:
    """Tests for RiskBand enum."""
    
    def test_band_enum_values(self):
        """Test RiskBand enum has expected values."""
        assert RiskBand.LOW.value == "low"
        assert RiskBand.MEDIUM.value == "medium"
        assert RiskBand.HIGH.value == "high"
        assert RiskBand.CRITICAL.value == "critical"


class TestIndicatorDefinition:
    """Tests for IndicatorDefinition dataclass."""
    
    def test_indicator_definition_creation(self):
        """Test creating indicator definition."""
        indicator = IndicatorDefinition(
            name=RiskIndicator.DAYS_PAST_DUE,
            description="Days past due on loan payments",
            data_type="numeric",
            calculation_method="MAX(days_past_due)",
            business_definition="Number of days payments are past due",
            data_requirements=["days_past_due", "payment_due_date"],
            assumptions=["Days calculated from payment due date"],
            limitations=["May not reflect partial payments"],
            interpretation="Higher values indicate more severe delinquency"
        )
        
        assert indicator.name == RiskIndicator.DAYS_PAST_DUE
        assert indicator.data_type == "numeric"
    
    def test_to_dict(self):
        """Test serialization to dictionary."""
        indicator = IndicatorDefinition(
            name=RiskIndicator.CREDIT_UTILIZATION,
            description="Credit utilization ratio",
            data_type="percentage",
            calculation_method="(current_balance / credit_limit) * 100",
            business_definition="Percentage of available credit being used",
            data_requirements=["current_balance", "credit_limit"],
            assumptions=["Credit limit is accurate"],
            limitations=["Does not consider cross-product utilization"],
            interpretation="Higher values indicate higher credit usage"
        )
        
        data_dict = indicator.to_dict()
        
        assert data_dict["name"] == "credit_utilization"
        assert data_dict["data_type"] == "percentage"
        assert "assumptions" in data_dict
        assert "limitations" in data_dict


class TestCreditRiskBase:
    """Tests for CreditRiskBase class."""
    
    def test_initialization(self):
        """Test base class initialization."""
        base = CreditRiskBase()
        
        assert len(base.indicator_registry) > 0
    
    def test_indicator_registration(self):
        """Test indicator registration."""
        base = CreditRiskBase()
        
        # Check standard indicators are registered
        assert "total_loan_exposure" in base.indicator_registry
        assert "days_past_due" in base.indicator_registry
        assert "credit_utilization" in base.indicator_registry
    
    def test_get_indicator_definition(self):
        """Test getting indicator definition."""
        base = CreditRiskBase()
        
        indicator_def = base.get_indicator_definition("days_past_due")
        
        assert indicator_def is not None
        assert indicator_def.name == RiskIndicator.DAYS_PAST_DUE
    
    def test_get_indicator_definition_not_found(self):
        """Test getting non-existent indicator."""
        base = CreditRiskBase()
        
        indicator_def = base.get_indicator_definition("nonexistent_indicator")
        
        assert indicator_def is None
    
    def test_get_all_indicator_definitions(self):
        """Test getting all indicator definitions."""
        base = CreditRiskBase()
        
        all_indicators = base.get_all_indicator_definitions()
        
        assert len(all_indicators) > 0
        assert "total_loan_exposure" in all_indicators
        assert "days_past_due" in all_indicators
