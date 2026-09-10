"""Event schemas for streaming infrastructure.

This module provides event schema definitions for the streaming pipeline,
including validation, serialization, and schema registry integration.
"""

from .event_schemas import (
    TransactionEvent,
    AccountUpdateEvent,
    CustomerUpdateEvent,
    LoanApplicationEvent,
    PaymentEvent,
    BaseEvent,
    EventType,
    create_event,
    get_event_schema_version,
)
from .schema_registry import SchemaRegistryClient, CompatibilityLevel, SchemaReference
from .validation import EventValidator, ValidationResult

__all__ = [
    "TransactionEvent",
    "AccountUpdateEvent",
    "CustomerUpdateEvent",
    "LoanApplicationEvent",
    "PaymentEvent",
    "BaseEvent",
    "EventType",
    "create_event",
    "get_event_schema_version",
    "SchemaRegistryClient",
    "CompatibilityLevel",
    "SchemaReference",
    "EventValidator",
    "ValidationResult",
]