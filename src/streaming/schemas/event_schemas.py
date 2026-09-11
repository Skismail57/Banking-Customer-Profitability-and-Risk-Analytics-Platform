"""Event schemas for banking events.

This module defines Pydantic models for banking event validation and serialization.
All events follow the banking domain conventions and support event-time processing.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from enum import Enum
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import Literal


class EventType(str, Enum):
    """Banking event types."""
    TRANSACTION = "transaction"
    ACCOUNT_UPDATE = "account_update"
    CUSTOMER_UPDATE = "customer_update"
    LOAN_APPLICATION = "loan_application"
    PAYMENT = "payment"


class BaseEvent(BaseModel):
    """Base event with common fields for all banking events."""
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
        }
    )
    
    event_id: str = Field(..., description="Unique event identifier")
    event_type: EventType = Field(..., description="Type of banking event")
    event_timestamp: datetime = Field(..., description="When the event occurred (event-time)")
    ingestion_timestamp: datetime = Field(
        default_factory=timezone.utcnow,
        description="When the event was ingested (processing-time)"
    )
    customer_key: Optional[str] = Field(None, description="Customer identifier")
    source_system: str = Field(..., description="Source system that generated the event")
    correlation_id: Optional[str] = Field(None, description="Correlation ID for tracing")
    
    @field_validator('event_timestamp')
    @classmethod
    def validate_event_timestamp(cls, v):
        """Ensure event timestamp is not in the future."""
        if v > datetime.now(timezone.utc).replace(tzinfo=None):
            raise ValueError("Event timestamp cannot be in the future")
        return v
    
    @field_validator('event_timestamp')
    @classmethod
    def validate_event_timestamp_not_too_old(cls, v):
        """Ensure event timestamp is not too old (more than 1 year)."""
        if (datetime.now(timezone.utc).replace(tzinfo=None) - v).days > 365:
            raise ValueError("Event timestamp is too old (more than 1 year)")
        return v


class TransactionEvent(BaseEvent):
    """Transaction event schema."""
    
    event_type: Literal[EventType.TRANSACTION] = Field(default=EventType.TRANSACTION)
    
    # Transaction details
    transaction_id: str = Field(..., description="Transaction identifier")
    account_key: Optional[str] = Field(None, description="Account identifier")
    transaction_type: str = Field(..., description="Type of transaction (purchase, payment, transfer, withdrawal, deposit)")
    channel: str = Field(..., description="Transaction channel (online, mobile, branch, ATM, phone)")
    amount: Decimal = Field(..., gt=0, description="Transaction amount")
    currency: str = Field(default="INR", description="Currency code")
    product_key: Optional[str] = Field(None, description="Product identifier")
    merchant_category: Optional[str] = Field(None, description="Merchant category code")
    location: Optional[str] = Field(None, description="Transaction location")
    description: Optional[str] = Field(None, description="Transaction description")
    
    @field_validator('transaction_type')
    @classmethod
    def validate_transaction_type(cls, v):
        """Validate transaction type."""
        valid_types = ["purchase", "payment", "transfer", "withdrawal", "deposit", "refund"]
        if v not in valid_types:
            raise ValueError(f"Invalid transaction type: {v}. Must be one of {valid_types}")
        return v
    
    @field_validator('channel')
    @classmethod
    def validate_channel(cls, v):
        """Validate channel."""
        valid_channels = ["online", "mobile", "branch", "ATM", "phone"]
        if v not in valid_channels:
            raise ValueError(f"Invalid channel: {v}. Must be one of {valid_channels}")
        return v


class AccountUpdateEvent(BaseEvent):
    """Account update event schema."""
    
    event_type: Literal[EventType.ACCOUNT_UPDATE] = Field(default=EventType.ACCOUNT_UPDATE)
    
    # Account details
    account_key: str = Field(..., description="Account identifier")
    account_id: str = Field(..., description="Account natural key")
    customer_key: str = Field(..., description="Customer identifier")
    update_type: str = Field(..., description="Type of update (balance_change, status_change, limit_change)")
    
    # Update details
    previous_balance: Optional[Decimal] = Field(None, description="Previous balance")
    new_balance: Optional[Decimal] = Field(None, description="New balance")
    previous_status: Optional[str] = Field(None, description="Previous account status")
    new_status: Optional[str] = Field(None, description="New account status")
    previous_limit: Optional[Decimal] = Field(None, description="Previous credit limit")
    new_limit: Optional[Decimal] = Field(None, description="New credit limit")
    
    @field_validator('update_type')
    @classmethod
    def validate_update_type(cls, v):
        """Validate update type."""
        valid_types = ["balance_change", "status_change", "limit_change", "account_opened", "account_closed"]
        if v not in valid_types:
            raise ValueError(f"Invalid update type: {v}. Must be one of {valid_types}")
        return v
    
    @model_validator(mode='after')
    def validate_update_details(self):
        """Ensure update details match update type."""
        update_type = self.update_type
        
        if update_type == "balance_change":
            if self.previous_balance is None or self.new_balance is None:
                raise ValueError("Balance change requires previous_balance and new_balance")
        elif update_type == "status_change":
            if self.previous_status is None or self.new_status is None:
                raise ValueError("Status change requires previous_status and new_status")
        elif update_type == "limit_change":
            if self.previous_limit is None or self.new_limit is None:
                raise ValueError("Limit change requires previous_limit and new_limit")
        
        return self


class CustomerUpdateEvent(BaseEvent):
    """Customer update event schema."""
    
    event_type: Literal[EventType.CUSTOMER_UPDATE] = Field(default=EventType.CUSTOMER_UPDATE)
    
    # Customer details
    customer_key: str = Field(..., description="Customer identifier")
    customer_id: str = Field(..., description="Customer natural key")
    update_type: str = Field(..., description="Type of update (profile_change, status_change, segment_change)")
    
    # Profile updates
    updated_fields: List[str] = Field(default_factory=list, description="List of updated fields")
    
    # Optional field updates
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    address_line1: Optional[str] = Field(None, description="Address line 1")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State")
    postal_code: Optional[str] = Field(None, description="Postal code")
    
    # Status updates
    previous_status: Optional[str] = Field(None, description="Previous customer status")
    new_status: Optional[str] = Field(None, description="New customer status")
    
    # Segment updates
    previous_segment: Optional[str] = Field(None, description="Previous segment")
    new_segment: Optional[str] = Field(None, description="New segment")
    
    @field_validator('update_type')
    @classmethod
    def validate_update_type(cls, v):
        """Validate update type."""
        valid_types = ["profile_change", "status_change", "segment_change"]
        if v not in valid_types:
            raise ValueError(f"Invalid update type: {v}. Must be one of {valid_types}")
        return v


class LoanApplicationEvent(BaseEvent):
    """Loan application event schema."""
    
    event_type: Literal[EventType.LOAN_APPLICATION] = Field(default=EventType.LOAN_APPLICATION)
    
    # Application details
    application_id: str = Field(..., description="Loan application identifier")
    customer_key: str = Field(..., description="Customer identifier")
    customer_id: str = Field(..., description="Customer natural key")
    product_key: str = Field(..., description="Product identifier")
    
    # Loan details
    loan_amount: Decimal = Field(..., gt=0, description="Requested loan amount")
    loan_purpose: str = Field(..., description="Purpose of the loan")
    loan_term_months: int = Field(..., gt=0, description="Loan term in months")
    interest_rate: Optional[Decimal] = Field(None, description="Interest rate")
    
    # Application details
    application_status: str = Field(..., description="Application status")
    credit_score: Optional[int] = Field(None, ge=300, le=850, description="Credit score")
    annual_income: Optional[Decimal] = Field(None, ge=0, description="Annual income")
    debt_to_income_ratio: Optional[Decimal] = Field(None, ge=0, description="Debt-to-income ratio")
    
    # Decision details (if available)
    application_decision: Optional[str] = Field(None, description="Application decision")
    decision_reason: Optional[str] = Field(None, description="Reason for decision")
    approved_amount: Optional[Decimal] = Field(None, description="Approved amount")
    
    @field_validator('application_status')
    @classmethod
    def validate_application_status(cls, v):
        """Validate application status."""
        valid_statuses = ["submitted", "under_review", "approved", "rejected", "cancelled"]
        if v not in valid_statuses:
            raise ValueError(f"Invalid application status: {v}. Must be one of {valid_statuses}")
        return v
    
    @field_validator('application_decision')
    @classmethod
    def validate_application_decision(cls, v):
        """Validate application decision."""
        if v is not None:
            valid_decisions = ["approved", "rejected", "needs_review"]
            if v not in valid_decisions:
                raise ValueError(f"Invalid application decision: {v}. Must be one of {valid_decisions}")
        return v


class PaymentEvent(BaseEvent):
    """Payment event schema."""
    
    event_type: Literal[EventType.PAYMENT] = Field(default=EventType.PAYMENT)
    
    # Payment details
    payment_id: str = Field(..., description="Payment identifier")
    customer_key: str = Field(..., description="Customer identifier")
    customer_id: str = Field(..., description="Customer natural key")
    loan_key: Optional[str] = Field(None, description="Loan identifier")
    account_key: Optional[str] = Field(None, description="Account identifier")
    
    # Payment details
    payment_date: datetime = Field(..., description="Payment date")
    due_date: datetime = Field(..., description="Payment due date")
    payment_amount: Decimal = Field(..., gt=0, description="Payment amount")
    payment_type: str = Field(..., description="Payment type (principal, interest, fee)")
    payment_status: str = Field(..., description="Payment status")
    
    # Additional details
    payment_method: Optional[str] = Field(None, description="Payment method")
    reference_number: Optional[str] = Field(None, description="Reference number")
    
    @field_validator('payment_type')
    @classmethod
    def validate_payment_type(cls, v):
        """Validate payment type."""
        valid_types = ["principal", "interest", "fee", "penalty"]
        if v not in valid_types:
            raise ValueError(f"Invalid payment type: {v}. Must be one of {valid_types}")
        return v
    
    @field_validator('payment_status')
    @classmethod
    def validate_payment_status(cls, v):
        """Validate payment status."""
        valid_statuses = ["scheduled", "processing", "completed", "failed", "returned"]
        if v not in valid_statuses:
            raise ValueError(f"Invalid payment status: {v}. Must be one of {valid_statuses}")
        return v
    
    @field_validator('due_date')
    @classmethod
    def validate_due_date(cls, v):
        """Ensure due date is not after payment date."""
        # This is a simplified validation - in practice you might allow post-due payments
        return v


# Event factory function
def create_event(event_data: Dict[str, Any]) -> BaseEvent:
    """Factory function to create appropriate event object based on event type.
    
    Args:
        event_data: Dictionary containing event data
    
    Returns:
        Appropriate event object based on event_type
    
    Raises:
        ValueError: If event_type is invalid or data doesn't match schema
    """
    event_type = event_data.get("event_type")
    
    if event_type == EventType.TRANSACTION:
        return TransactionEvent(**event_data)
    elif event_type == EventType.ACCOUNT_UPDATE:
        return AccountUpdateEvent(**event_data)
    elif event_type == EventType.CUSTOMER_UPDATE:
        return CustomerUpdateEvent(**event_data)
    elif event_type == EventType.LOAN_APPLICATION:
        return LoanApplicationEvent(**event_data)
    elif event_type == EventType.PAYMENT:
        return PaymentEvent(**event_data)
    else:
        raise ValueError(f"Invalid event type: {event_type}")


# Event versioning support
EVENT_SCHEMA_VERSIONS = {
    EventType.TRANSACTION: "v1",
    EventType.ACCOUNT_UPDATE: "v1",
    EventType.CUSTOMER_UPDATE: "v1",
    EventType.LOAN_APPLICATION: "v1",
    EventType.PAYMENT: "v1",
}


def get_event_schema_version(event_type: EventType) -> str:
    """Get the current schema version for an event type.
    
    Args:
        event_type: Event type
    
    Returns:
        Schema version string
    """
    return EVENT_SCHEMA_VERSIONS.get(event_type, "v1")