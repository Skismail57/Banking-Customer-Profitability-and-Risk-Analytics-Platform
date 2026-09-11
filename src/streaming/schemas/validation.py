"""Event validation logic for streaming pipeline.

This module provides validation functions for streaming events, including
schema validation, data quality checks, and business rule validation.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
from decimal import Decimal

from pydantic import ValidationError

from src.streaming.schemas import (
    BaseEvent,
    create_event,
    EventType,
    SchemaRegistryClient,
)
from src.streaming.config import StreamingConfig

logger = logging.getLogger(__name__)


class ValidationResult:
    """Result of event validation."""
    
    def __init__(
        self,
        is_valid: bool,
        errors: Optional[List[str]] = None,
        warnings: Optional[List[str]] = None
    ):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
    
    def add_error(self, error: str) -> None:
        """Add an error to the validation result."""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str) -> None:
        """Add a warning to the validation result."""
        self.warnings.append(warning)
    
    def merge(self, other: 'ValidationResult') -> None:
        """Merge another validation result into this one."""
        self.is_valid = self.is_valid and other.is_valid
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)


class EventValidator:
    """Validates streaming events against schemas and business rules."""
    
    def __init__(self, config: StreamingConfig):
        """Initialize event validator.
        
        Args:
            config: Streaming configuration
        """
        self.config = config
        self.schema_registry = SchemaRegistryClient(config) if config.schema_registry.enable else None
    
    def validate_event(
        self,
        event_data: Dict[str, Any],
        subject: str
    ) -> ValidationResult:
        """Validate an event against schema and business rules.
        
        Args:
            event_data: Raw event data
            subject: Subject name (typically topic name)
        
        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult(is_valid=True)
        
        # Step 1: Schema validation
        schema_result = self._validate_schema(event_data, subject)
        result.merge(schema_result)
        
        # Step 2: Pydantic model validation
        model_result = self._validate_pydantic_model(event_data)
        result.merge(model_result)
        
        # Step 3: Business rule validation
        business_result = self._validate_business_rules(event_data)
        result.merge(business_result)
        
        # Step 4: Data quality validation
        quality_result = self._validate_data_quality(event_data)
        result.merge(quality_result)
        
        return result
    
    def _validate_schema(
        self,
        event_data: Dict[str, Any],
        subject: str
    ) -> ValidationResult:
        """Validate event against schema registry schema.
        
        Args:
            event_data: Event data
            subject: Subject name
        
        Returns:
            ValidationResult
        """
        result = ValidationResult(is_valid=True)
        
        if self.schema_registry is None:
            result.add_warning("Schema registry is disabled, skipping schema validation")
            return result
        
        try:
            is_valid = self.schema_registry.validate_event(event_data, subject)
            if not is_valid:
                result.add_error("Event failed schema validation")
        except Exception as e:
            result.add_error(f"Schema validation failed: {e}")
        
        return result
    
    def _validate_pydantic_model(
        self,
        event_data: Dict[str, Any]
    ) -> ValidationResult:
        """Validate event data against Pydantic model.
        
        Args:
            event_data: Event data
        
        Returns:
            ValidationResult
        """
        result = ValidationResult(is_valid=True)
        
        try:
            # Create event object to validate against Pydantic model
            event = create_event(event_data)
            # If we get here, validation passed
            logger.debug(f"Event {event.event_id} passed Pydantic validation")
        except ValidationError as e:
            result.add_error(f"Pydantic validation failed: {e}")
        except ValueError as e:
            result.add_error(f"Event creation failed: {e}")
        except Exception as e:
            result.add_error(f"Unexpected validation error: {e}")
        
        return result
    
    def _validate_business_rules(
        self,
        event_data: Dict[str, Any]
    ) -> ValidationResult:
        """Validate event against business rules.
        
        Args:
            event_data: Event data
        
        Returns:
            ValidationResult
        """
        result = ValidationResult(is_valid=True)
        event_type = event_data.get("event_type")
        
        # Business rule validation based on event type
        if event_type == EventType.TRANSACTION:
            result.merge(self._validate_transaction_event(event_data))
        elif event_type == EventType.ACCOUNT_UPDATE:
            result.merge(self._validate_account_update_event(event_data))
        elif event_type == EventType.CUSTOMER_UPDATE:
            result.merge(self._validate_customer_update_event(event_data))
        elif event_type == EventType.LOAN_APPLICATION:
            result.merge(self._validate_loan_application_event(event_data))
        elif event_type == EventType.PAYMENT:
            result.merge(self._validate_payment_event(event_data))
        
        return result
    
    def _validate_transaction_event(
        self,
        event_data: Dict[str, Any]
    ) -> ValidationResult:
        """Validate transaction event business rules.
        
        Args:
            event_data: Event data
        
        Returns:
            ValidationResult
        """
        result = ValidationResult(is_valid=True)
        
        # Check transaction amount is reasonable
        amount = event_data.get("amount")
        if amount is not None:
            try:
                amount_decimal = Decimal(str(amount))
                if amount_decimal <= 0:
                    result.add_error("Transaction amount must be positive")
                elif amount_decimal > 10000000:  # $10M threshold
                    result.add_warning("Transaction amount is unusually high")
            except (ValueError, TypeError):
                result.add_error("Invalid transaction amount format")
        
        # Check currency is valid
        currency = event_data.get("currency")
        if currency is not None and currency not in ["INR", "USD", "EUR", "GBP", "CAD", "AUD"]:
            result.add_warning(f"Unusual currency: {currency}")
        
        return result
    
    def _validate_account_update_event(
        self,
        event_data: Dict[str, Any]
    ) -> ValidationResult:
        """Validate account update event business rules.
        
        Args:
            event_data: Event data
        
        Returns:
            ValidationResult
        """
        result = ValidationResult(is_valid=True)
        
        # Check that customer_key and account_key are provided
        if not event_data.get("customer_key"):
            result.add_error("Account update requires customer_key")
        
        if not event_data.get("account_key"):
            result.add_error("Account update requires account_key")
        
        # Validate balance changes
        if event_data.get("update_type") == "balance_change":
            prev_balance = event_data.get("previous_balance")
            new_balance = event_data.get("new_balance")
            
            if prev_balance is not None and new_balance is not None:
                try:
                    prev_decimal = Decimal(str(prev_balance))
                    new_decimal = Decimal(str(new_balance))
                    
                    if new_decimal < 0:
                        result.add_error("New balance cannot be negative")
                    
                    # Check for unusual balance changes
                    change = abs(new_decimal - prev_decimal)
                    if change > Decimal("1000000"):  # $1M threshold
                        result.add_warning("Balance change is unusually large")
                
                except (ValueError, TypeError):
                    result.add_error("Invalid balance format")
        
        return result
    
    def _validate_customer_update_event(
        self,
        event_data: Dict[str, Any]
    ) -> ValidationResult:
        """Validate customer update event business rules.
        
        Args:
            event_data: Event data
        
        Returns:
            ValidationResult
        """
        result = ValidationResult(is_valid=True)
        
        # Check that customer_key is provided
        if not event_data.get("customer_key"):
            result.add_error("Customer update requires customer_key")
        
        # Validate email format if provided
        email = event_data.get("email")
        if email and "@" not in email:
            result.add_error("Invalid email format")
        
        # Validate postal code format if provided
        postal_code = event_data.get("postal_code")
        if postal_code and len(postal_code) > 10:
            result.add_warning("Postal code is unusually long")
        
        return result
    
    def _validate_loan_application_event(
        self,
        event_data: Dict[str, Any]
    ) -> ValidationResult:
        """Validate loan application event business rules.
        
        Args:
            event_data: Event data
        
        Returns:
            ValidationResult
        """
        result = ValidationResult(is_valid=True)
        
        # Check loan amount is reasonable
        loan_amount = event_data.get("loan_amount")
        if loan_amount is not None:
            try:
                amount_decimal = Decimal(str(loan_amount))
                if amount_decimal <= 0:
                    result.add_error("Loan amount must be positive")
                elif amount_decimal > 10000000:  # $10M threshold
                    result.add_warning("Loan amount is unusually high")
            except (ValueError, TypeError):
                result.add_error("Invalid loan amount format")
        
        # Check loan term is reasonable
        loan_term = event_data.get("loan_term_months")
        if loan_term is not None:
            if loan_term <= 0:
                result.add_error("Loan term must be positive")
            elif loan_term > 360:  # 30 years
                result.add_warning("Loan term is unusually long")
        
        # Check credit score if provided
        credit_score = event_data.get("credit_score")
        if credit_score is not None:
            if credit_score < 300 or credit_score > 850:
                result.add_error("Credit score must be between 300 and 850")
        
        # Check debt-to-income ratio if provided
        dti = event_data.get("debt_to_income_ratio")
        if dti is not None:
            try:
                dti_decimal = Decimal(str(dti))
                if dti_decimal < 0:
                    result.add_error("Debt-to-income ratio cannot be negative")
                elif dti_decimal > 1:
                    result.add_warning("Debt-to-income ratio is very high")
            except (ValueError, TypeError):
                result.add_error("Invalid debt-to-income ratio format")
        
        return result
    
    def _validate_payment_event(
        self,
        event_data: Dict[str, Any]
    ) -> ValidationResult:
        """Validate payment event business rules.
        
        Args:
            event_data: Event data
        
        Returns:
            ValidationResult
        """
        result = ValidationResult(is_valid=True)
        
        # Check payment amount is positive
        payment_amount = event_data.get("payment_amount")
        if payment_amount is not None:
            try:
                amount_decimal = Decimal(str(payment_amount))
                if amount_decimal <= 0:
                    result.add_error("Payment amount must be positive")
            except (ValueError, TypeError):
                result.add_error("Invalid payment amount format")
        
        # Check that due_date is not in the future (too far)
        due_date = event_data.get("due_date")
        if due_date:
            if isinstance(due_date, str):
                try:
                    due_date = datetime.fromisoformat(due_date)
                except ValueError:
                    result.add_error("Invalid due_date format")
            
            if isinstance(due_date, datetime):
                if (due_date - datetime.now(timezone.utc).replace(tzinfo=None)).days > 365:
                    result.add_warning("Due date is more than 1 year in the future")
        
        # Check that payment_date is not before due_date (simplified check)
        payment_date = event_data.get("payment_date")
        if payment_date and due_date:
            if isinstance(payment_date, str):
                try:
                    payment_date = datetime.fromisoformat(payment_date)
                except ValueError:
                    result.add_error("Invalid payment_date format")
            
            if isinstance(payment_date, datetime) and isinstance(due_date, datetime):
                if payment_date < due_date:
                    result.add_warning("Payment date is before due date (possible early payment)")
        
        return result
    
    def _validate_data_quality(
        self,
        event_data: Dict[str, Any]
    ) -> ValidationResult:
        """Validate data quality of event.
        
        Args:
            event_data: Event data
        
        Returns:
            ValidationResult
        """
        result = ValidationResult(is_valid=True)
        
        # Check for null required fields
        required_fields = ["event_id", "event_type", "event_timestamp", "source_system"]
        for field in required_fields:
            if field not in event_data or event_data[field] is None:
                result.add_error(f"Required field '{field}' is missing or null")
        
        # Check for empty strings
        for key, value in event_data.items():
            if isinstance(value, str) and value.strip() == "":
                result.add_warning(f"Field '{key}' is an empty string")
        
        # Check for reasonable timestamps
        event_timestamp = event_data.get("event_timestamp")
        if event_timestamp:
            if isinstance(event_timestamp, str):
                try:
                    event_timestamp = datetime.fromisoformat(event_timestamp)
                except ValueError:
                    result.add_error("Invalid event_timestamp format")
            
            if isinstance(event_timestamp, datetime):
                # Check for events too far in the future
                if (event_timestamp - datetime.now(timezone.utc).replace(tzinfo=None)).days > 1:
                    result.add_error("Event timestamp is too far in the future")
                # Check for events too far in the past
                if (datetime.now(timezone.utc).replace(tzinfo=None) - event_timestamp).days > 365:
                    result.add_warning("Event timestamp is very old (more than 1 year)")
        
        return result
    
    def validate_batch(
        self,
        events: List[Dict[str, Any]],
        subject: str
    ) -> Dict[str, ValidationResult]:
        """Validate a batch of events.
        
        Args:
            events: List of event data
            subject: Subject name
        
        Returns:
            Dictionary mapping event_id to ValidationResult
        """
        results = {}
        
        for event_data in events:
            event_id = event_data.get("event_id", "unknown")
            results[event_id] = self.validate_event(event_data, subject)
        
        return results
    
    def get_validation_summary(
        self,
        validation_results: Dict[str, ValidationResult]
    ) -> Dict[str, Any]:
        """Get summary of validation results.
        
        Args:
            validation_results: Dictionary of validation results
        
        Returns:
            Summary dictionary
        """
        total = len(validation_results)
        valid = sum(1 for r in validation_results.values() if r.is_valid)
        invalid = total - valid
        total_errors = sum(len(r.errors) for r in validation_results.values())
        total_warnings = sum(len(r.warnings) for r in validation_results.values())
        
        return {
            "total_events": total,
            "valid_events": valid,
            "invalid_events": invalid,
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "success_rate": valid / total if total > 0 else 0,
        }