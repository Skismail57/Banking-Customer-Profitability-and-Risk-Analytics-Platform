"""Unit tests for event validation logic.

This module tests the EventValidator and ValidationResult classes.
"""

import pytest
from datetime import datetime, timezone, timedelta
from decimal import Decimal

from src.streaming.schemas import (
    EventValidator,
    ValidationResult,
    EventType,
)
from src.streaming.config import StreamingConfig


class TestValidationResult:
    """Test ValidationResult class."""
    
    def test_validation_result_creation(self):
        """Test creating a validation result."""
        result = ValidationResult(is_valid=True)
        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == []
    
    def test_validation_result_with_errors(self):
        """Test creating a validation result with errors."""
        result = ValidationResult(is_valid=False, errors=["Error 1", "Error 2"])
        assert result.is_valid is False
        assert len(result.errors) == 2
        assert result.warnings == []
    
    def test_validation_result_with_warnings(self):
        """Test creating a validation result with warnings."""
        result = ValidationResult(is_valid=True, warnings=["Warning 1"])
        assert result.is_valid is True
        assert result.errors == []
        assert len(result.warnings) == 1
    
    def test_add_error(self):
        """Test adding an error."""
        result = ValidationResult(is_valid=True)
        result.add_error("New error")
        assert result.is_valid is False
        assert "New error" in result.errors
    
    def test_add_warning(self):
        """Test adding a warning."""
        result = ValidationResult(is_valid=True)
        result.add_warning("New warning")
        assert result.is_valid is True
        assert "New warning" in result.warnings
    
    def test_merge(self):
        """Test merging validation results."""
        result1 = ValidationResult(is_valid=True, warnings=["Warning 1"])
        result2 = ValidationResult(is_valid=False, errors=["Error 1"])
        
        result1.merge(result2)
        
        assert result1.is_valid is False
        assert "Error 1" in result1.errors
        assert "Warning 1" in result1.warnings


class TestEventValidator:
    """Test EventValidator class."""
    
    @pytest.fixture
    def config(self):
        """Create a streaming config for testing."""
        return StreamingConfig(
            kafka={
                "bootstrap_servers": "localhost:9092",
                "group_id": "test_group",
            },
            redis={
                "host": "localhost",
                "port": 6379,
            },
            schema_registry={
                "enable": False,  # Disable for unit tests
                "url": "http://localhost:8081",
            }
        )
    
    @pytest.fixture
    def validator(self, config):
        """Create an event validator for testing."""
        return EventValidator(config)
    
    def test_validator_initialization(self, validator):
        """Test validator initialization."""
        assert validator.config is not None
        assert validator.schema_registry is None  # Disabled in config
    
    def test_validate_valid_transaction_event(self, validator):
        """Test validating a valid transaction event."""
        event_data = {
            "event_id": "evt_txn_123",
            "event_type": EventType.TRANSACTION,
            "event_timestamp": datetime.now(timezone.utc).replace(tzinfo=None),
            "source_system": "core_banking",
            "customer_key": "cust_123",
            "transaction_id": "txn_456",
            "transaction_type": "purchase",
            "channel": "online",
            "amount": "100.50",
            "currency": "USD"
        }
        
        result = validator.validate_event(event_data, "transactions")
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_transaction_invalid_amount(self, validator):
        """Test validating transaction with invalid amount."""
        event_data = {
            "event_id": "evt_txn_123",
            "event_type": EventType.TRANSACTION,
            "event_timestamp": datetime.now(timezone.utc).replace(tzinfo=None),
            "source_system": "core_banking",
            "transaction_id": "txn_456",
            "transaction_type": "purchase",
            "channel": "online",
            "amount": "-100.50",  # Negative amount
            "currency": "USD"
        }
        
        result = validator.validate_event(event_data, "transactions")
        assert result.is_valid is False
        assert any("amount" in error.lower() for error in result.errors)
    
    def test_validate_transaction_high_amount_warning(self, validator):
        """Test validating transaction with unusually high amount."""
        event_data = {
            "event_id": "evt_txn_123",
            "event_type": EventType.TRANSACTION,
            "event_timestamp": datetime.now(timezone.utc).replace(tzinfo=None),
            "source_system": "core_banking",
            "customer_key": "cust_123",
            "transaction_id": "txn_456",
            "transaction_type": "purchase",
            "channel": "online",
            "amount": "15000000.00",  # $15M - triggers warning
            "currency": "USD"
        }
        
        result = validator.validate_event(event_data, "transactions")
        # Should be valid but with warning
        assert result.is_valid is True
        assert any("unusually high" in warning.lower() for warning in result.warnings)
    
    def test_validate_valid_account_update(self, validator):
        """Test validating a valid account update event."""
        event_data = {
            "event_id": "evt_acc_123",
            "event_type": EventType.ACCOUNT_UPDATE,
            "event_timestamp": datetime.now(timezone.utc).replace(tzinfo=None),
            "source_system": "core_banking",
            "account_key": "acc_456",
            "account_id": "ACC123",
            "customer_key": "cust_789",
            "update_type": "balance_change",
            "previous_balance": "1000.00",
            "new_balance": "900.00"
        }
        
        result = validator.validate_event(event_data, "account_updates")
        assert result.is_valid is True
    
    def test_validate_account_update_missing_customer(self, validator):
        """Test validating account update without customer key."""
        event_data = {
            "event_id": "evt_acc_123",
            "event_type": EventType.ACCOUNT_UPDATE,
            "event_timestamp": datetime.now(timezone.utc).replace(tzinfo=None),
            "source_system": "core_banking",
            "account_key": "acc_456",
            "account_id": "ACC123",
            # Missing customer_key
            "update_type": "balance_change",
            "previous_balance": "1000.00",
            "new_balance": "900.00"
        }
        
        result = validator.validate_event(event_data, "account_updates")
        assert result.is_valid is False
        assert any("customer_key" in error.lower() for error in result.errors)
    
    def test_validate_account_update_negative_balance(self, validator):
        """Test validating account update with negative balance."""
        event_data = {
            "event_id": "evt_acc_123",
            "event_type": EventType.ACCOUNT_UPDATE,
            "event_timestamp": datetime.now(timezone.utc).replace(tzinfo=None),
            "source_system": "core_banking",
            "account_key": "acc_456",
            "account_id": "ACC123",
            "customer_key": "cust_789",
            "update_type": "balance_change",
            "previous_balance": "1000.00",
            "new_balance": "-100.00"  # Negative balance
        }
        
        result = validator.validate_event(event_data, "account_updates")
        assert result.is_valid is False
        assert any("negative" in error.lower() for error in result.errors)
    
    def test_validate_valid_customer_update(self, validator):
        """Test validating a valid customer update event."""
        event_data = {
            "event_id": "evt_cust_123",
            "event_type": EventType.CUSTOMER_UPDATE,
            "event_timestamp": datetime.now(timezone.utc).replace(tzinfo=None),
            "source_system": "crm",
            "customer_key": "cust_456",
            "customer_id": "CUST123",
            "update_type": "profile_change",
            "updated_fields": ["email"],
            "email": "new.email@example.com"
        }
        
        result = validator.validate_event(event_data, "customer_updates")
        assert result.is_valid is True
    
    def test_validate_customer_update_invalid_email(self, validator):
        """Test validating customer update with invalid email."""
        event_data = {
            "event_id": "evt_cust_123",
            "event_type": EventType.CUSTOMER_UPDATE,
            "event_timestamp": datetime.now(timezone.utc).replace(tzinfo=None),
            "source_system": "crm",
            "customer_key": "cust_456",
            "customer_id": "CUST123",
            "update_type": "profile_change",
            "updated_fields": ["email"],
            "email": "invalid-email"  # Missing @
        }
        
        result = validator.validate_event(event_data, "customer_updates")
        assert result.is_valid is False
        assert any("email" in error.lower() for error in result.errors)
    
    def test_validate_valid_loan_application(self, validator):
        """Test validating a valid loan application event."""
        event_data = {
            "event_id": "evt_loan_123",
            "event_type": EventType.LOAN_APPLICATION,
            "event_timestamp": datetime.now(timezone.utc).replace(tzinfo=None),
            "source_system": "lending",
            "application_id": "APP123",
            "customer_key": "cust_456",
            "customer_id": "CUST123",
            "product_key": "prod_789",
            "loan_amount": "50000.00",
            "loan_purpose": "home_improvement",
            "loan_term_months": 60,
            "application_status": "submitted",
            "credit_score": 720,
            "annual_income": "75000.00"
        }
        
        result = validator.validate_event(event_data, "loan_applications")
        assert result.is_valid is True
    
    def test_validate_loan_application_invalid_credit_score(self, validator):
        """Test validating loan application with invalid credit score."""
        event_data = {
            "event_id": "evt_loan_123",
            "event_type": EventType.LOAN_APPLICATION,
            "event_timestamp": datetime.now(timezone.utc).replace(tzinfo=None),
            "source_system": "lending",
            "application_id": "APP123",
            "customer_key": "cust_456",
            "customer_id": "CUST123",
            "product_key": "prod_789",
            "loan_amount": "50000.00",
            "loan_purpose": "home_improvement",
            "loan_term_months": 60,
            "application_status": "submitted",
            "credit_score": 200  # Below minimum
        }
        
        result = validator.validate_event(event_data, "loan_applications")
        assert result.is_valid is False
        assert any("credit score" in error.lower() for error in result.errors)
    
    def test_validate_loan_application_high_dti_warning(self, validator):
        """Test validating loan application with high DTI."""
        event_data = {
            "event_id": "evt_loan_123",
            "event_type": EventType.LOAN_APPLICATION,
            "event_timestamp": datetime.now(timezone.utc).replace(tzinfo=None),
            "source_system": "lending",
            "application_id": "APP123",
            "customer_key": "cust_456",
            "customer_id": "CUST123",
            "product_key": "prod_789",
            "loan_amount": "50000.00",
            "loan_purpose": "home_improvement",
            "loan_term_months": 60,
            "application_status": "submitted",
            "debt_to_income_ratio": "1.5"  # High DTI
        }
        
        result = validator.validate_event(event_data, "loan_applications")
        assert result.is_valid is True
        assert any("debt-to-income" in warning.lower() for warning in result.warnings)
    
    def test_validate_valid_payment_event(self, validator):
        """Test validating a valid payment event."""
        payment_date = datetime.now(timezone.utc).replace(tzinfo=None)
        due_date = payment_date - timedelta(days=5)
        
        event_data = {
            "event_id": "evt_pay_123",
            "event_type": EventType.PAYMENT,
            "event_timestamp": datetime.now(timezone.utc).replace(tzinfo=None),
            "source_system": "lending",
            "payment_id": "PAY123",
            "customer_key": "cust_456",
            "customer_id": "CUST123",
            "loan_key": "loan_789",
            "payment_date": payment_date.isoformat(),
            "due_date": due_date.isoformat(),
            "payment_amount": "500.00",
            "payment_type": "principal",
            "payment_status": "completed"
        }
        
        result = validator.validate_event(event_data, "payments")
        assert result.is_valid is True
    
    def test_validate_payment_negative_amount(self, validator):
        """Test validating payment with negative amount."""
        event_data = {
            "event_id": "evt_pay_123",
            "event_type": EventType.PAYMENT,
            "event_timestamp": datetime.now(timezone.utc).replace(tzinfo=None),
            "source_system": "lending",
            "payment_id": "PAY123",
            "customer_key": "cust_456",
            "customer_id": "CUST123",
            "payment_date": datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
            "due_date": datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
            "payment_amount": "-500.00",  # Negative
            "payment_type": "principal",
            "payment_status": "completed"
        }
        
        result = validator.validate_event(event_data, "payments")
        assert result.is_valid is False
        assert any("amount" in error.lower() for error in result.errors)
    
    def test_validate_event_missing_required_field(self, validator):
        """Test validating event with missing required field."""
        event_data = {
            "event_id": "evt_123",
            "event_type": EventType.TRANSACTION,
            # Missing event_timestamp
            "source_system": "core_banking"
        }
        
        result = validator.validate_event(event_data, "transactions")
        assert result.is_valid is False
        assert any("required" in error.lower() for error in result.errors)
    
    def test_validate_event_future_timestamp(self, validator):
        """Test validating event with future timestamp."""
        event_data = {
            "event_id": "evt_123",
            "event_type": EventType.TRANSACTION,
            "event_timestamp": (datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=2)).isoformat(),
            "source_system": "core_banking"
        }
        
        result = validator.validate_event(event_data, "transactions")
        assert result.is_valid is False
        assert any("future" in error.lower() for error in result.errors)
    
    def test_validate_event_old_timestamp_warning(self, validator):
        """Test validating event with very old timestamp."""
        event_data = {
            "event_id": "evt_123",
            "event_type": EventType.TRANSACTION,
            "event_timestamp": (datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=400)).isoformat(),
            "source_system": "core_banking",
            "transaction_id": "txn_456",
            "transaction_type": "purchase",
            "channel": "online",
            "amount": "100.50"
        }
        
        result = validator.validate_event(event_data, "transactions")
        assert result.is_valid is True
        assert any("old" in warning.lower() for warning in result.warnings)
    
    def test_validate_batch(self, validator):
        """Test validating a batch of events."""
        events = [
            {
                "event_id": "evt_1",
                "event_type": EventType.TRANSACTION,
                "event_timestamp": datetime.now(timezone.utc).replace(tzinfo=None),
                "source_system": "core_banking",
                "transaction_id": "txn_1",
                "transaction_type": "purchase",
                "channel": "online",
                "amount": "100.50"
            },
            {
                "event_id": "evt_2",
                "event_type": EventType.TRANSACTION,
                "event_timestamp": datetime.now(timezone.utc).replace(tzinfo=None),
                "source_system": "core_banking",
                "transaction_id": "txn_2",
                "transaction_type": "purchase",
                "channel": "online",
                "amount": "200.50"
            }
        ]
        
        results = validator.validate_batch(events, "transactions")
        assert len(results) == 2
        assert "evt_1" in results
        assert "evt_2" in results
        assert results["evt_1"].is_valid is True
        assert results["evt_2"].is_valid is True
    
    def test_get_validation_summary(self, validator):
        """Test getting validation summary."""
        events = [
            {
                "event_id": "evt_1",
                "event_type": EventType.TRANSACTION,
                "event_timestamp": datetime.now(timezone.utc).replace(tzinfo=None),
                "source_system": "core_banking",
                "transaction_id": "txn_1",
                "transaction_type": "purchase",
                "channel": "online",
                "amount": "100.50"
            },
            {
                "event_id": "evt_2",
                "event_type": EventType.TRANSACTION,
                "event_timestamp": datetime.now(timezone.utc).replace(tzinfo=None),
                "source_system": "core_banking",
                "transaction_id": "txn_2",
                "transaction_type": "purchase",
                "channel": "online",
                "amount": "-100.50"  # Invalid
            }
        ]
        
        results = validator.validate_batch(events, "transactions")
        summary = validator.get_validation_summary(results)
        
        assert summary["total_events"] == 2
        assert summary["valid_events"] == 1
        assert summary["invalid_events"] == 1
        assert summary["success_rate"] == 0.5
        assert summary["total_errors"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])