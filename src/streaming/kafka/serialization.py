"""Message serialization and deserialization for Kafka.

This module provides utilities for serializing and deserializing messages
to/from Kafka using JSON format with schema validation support.
"""

import json
import logging
from typing import Any, Dict, Optional, Union
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from src.streaming.schemas import BaseEvent, create_event, EventType

logger = logging.getLogger(__name__)


class MessageSerializer:
    """Serializes events to Kafka messages."""
    
    def __init__(self, include_metadata: bool = True):
        """Initialize message serializer.
        
        Args:
            include_metadata: Whether to include metadata in serialized messages
        """
        self.include_metadata = include_metadata
    
    def serialize(
        self,
        event: Union[BaseEvent, Dict[str, Any]],
        topic: str,
        partition_key: Optional[str] = None
    ) -> tuple[bytes, Optional[bytes]]:
        """Serialize an event to Kafka message format.
        
        Args:
            event: Event object or dictionary
            topic: Topic name
            partition_key: Optional partition key for message routing
        
        Returns:
            Tuple of (key, value) as bytes
        """
        # Convert event to dict if it's a Pydantic model
        if isinstance(event, BaseModel):
            event_dict = event.model_dump(mode='json')
        else:
            event_dict = event
        
        # Add metadata if enabled
        if self.include_metadata:
            event_dict["_metadata"] = {
                "topic": topic,
                "serialized_at": datetime.utcnow().isoformat(),
            }
        
        # Serialize to JSON
        value = json.dumps(event_dict, default=self._json_encoder).encode('utf-8')
        
        # Encode partition key
        key = partition_key.encode('utf-8') if partition_key else None
        
        return key, value
    
    def serialize_batch(
        self,
        events: list[Union[BaseEvent, Dict[str, Any]]],
        topic: str
    ) -> list[tuple[Optional[bytes], bytes]]:
        """Serialize a batch of events to Kafka message format.
        
        Args:
            events: List of events
            topic: Topic name
        
        Returns:
            List of (key, value) tuples
        """
        messages = []
        for event in events:
            # Use customer_key as partition key if available
            partition_key = None
            if isinstance(event, BaseModel):
                partition_key = getattr(event, 'customer_key', None)
            elif isinstance(event, dict):
                partition_key = event.get('customer_key')
            
            key, value = self.serialize(event, topic, partition_key)
            messages.append((key, value))
        
        return messages
    
    def _json_encoder(self, obj: Any) -> Any:
        """Custom JSON encoder for special types.
        
        Args:
            obj: Object to encode
        
        Returns:
            JSON-serializable representation
        """
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif hasattr(obj, 'model_dump'):
            return obj.model_dump(mode='json')
        else:
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


class MessageDeserializer:
    """Deserializes Kafka messages to events."""
    
    def __init__(self, validate: bool = True):
        """Initialize message deserializer.
        
        Args:
            validate: Whether to validate events against schemas
        """
        self.validate = validate
    
    def deserialize(
        self,
        key: Optional[bytes],
        value: bytes,
        topic: str
    ) -> tuple[Optional[str], Dict[str, Any]]:
        """Deserialize a Kafka message to event dictionary.
        
        Args:
            key: Message key (partition key)
            value: Message value
            topic: Topic name
        
        Returns:
            Tuple of (partition_key, event_dict)
        """
        # Decode value
        event_dict = json.loads(value.decode('utf-8'))
        
        # Remove metadata if present
        if "_metadata" in event_dict:
            del event_dict["_metadata"]
        
        # Decode key
        partition_key = key.decode('utf-8') if key else None
        
        return partition_key, event_dict
    
    def deserialize_to_event(
        self,
        key: Optional[bytes],
        value: bytes,
        topic: str
    ) -> tuple[Optional[str], BaseEvent]:
        """Deserialize a Kafka message to event object.
        
        Args:
            key: Message key (partition key)
            value: Message value
            topic: Topic name
        
        Returns:
            Tuple of (partition_key, event_object)
        
        Raises:
            ValueError: If event validation fails
        """
        partition_key, event_dict = self.deserialize(key, value, topic)
        
        if self.validate:
            try:
                event = create_event(event_dict)
            except Exception as e:
                logger.error(f"Failed to create event from message: {e}")
                raise ValueError(f"Event validation failed: {e}")
        else:
            # Create event without validation (not recommended)
            event = event_dict
        
        return partition_key, event
    
    def deserialize_batch(
        self,
        messages: list[tuple[Optional[bytes], bytes]],
        topic: str
    ) -> list[tuple[Optional[str], Dict[str, Any]]]:
        """Deserialize a batch of Kafka messages.
        
        Args:
            messages: List of (key, value) tuples
            topic: Topic name
        
        Returns:
            List of (partition_key, event_dict) tuples
        """
        events = []
        for key, value in messages:
            partition_key, event_dict = self.deserialize(key, value, topic)
            events.append((partition_key, event_dict))
        
        return events
    
    def deserialize_batch_to_events(
        self,
        messages: list[tuple[Optional[bytes], bytes]],
        topic: str
    ) -> list[tuple[Optional[str], BaseEvent]]:
        """Deserialize a batch of Kafka messages to event objects.
        
        Args:
            messages: List of (key, value) tuples
            topic: Topic name
        
        Returns:
            List of (partition_key, event_object) tuples
        """
        events = []
        for key, value in messages:
            try:
                partition_key, event = self.deserialize_to_event(key, value, topic)
                events.append((partition_key, event))
            except Exception as e:
                logger.error(f"Failed to deserialize message in batch: {e}")
                # Skip invalid messages instead of failing entire batch
                continue
        
        return events


class ErrorMessage:
    """Error message format for failed events."""
    
    def __init__(
        self,
        original_event: Dict[str, Any],
        error_message: str,
        error_type: str,
        topic: str,
        timestamp: Optional[datetime] = None
    ):
        """Initialize error message.
        
        Args:
            original_event: Original event data
            error_message: Error message
            error_type: Type of error (validation, deserialization, etc.)
            topic: Topic where error occurred
            timestamp: Error timestamp
        """
        self.original_event = original_event
        self.error_message = error_message
        self.error_type = error_type
        self.topic = topic
        self.timestamp = timestamp or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error message to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            "original_event": self.original_event,
            "error_message": self.error_message,
            "error_type": self.error_type,
            "topic": self.topic,
            "timestamp": self.timestamp.isoformat(),
        }
    
    def to_json(self) -> bytes:
        """Convert error message to JSON bytes.
        
        Returns:
            JSON bytes
        """
        return json.dumps(self.to_dict(), default=str).encode('utf-8')


class DeadLetterQueueHandler:
    """Handles messages that failed processing by sending to DLQ."""
    
    def __init__(self, serializer: MessageSerializer):
        """Initialize DLQ handler.
        
        Args:
            serializer: Message serializer
        """
        self.serializer = serializer
    
    def create_error_message(
        self,
        original_event: Dict[str, Any],
        error_message: str,
        error_type: str,
        topic: str
    ) -> tuple[Optional[bytes], bytes]:
        """Create an error message for DLQ.
        
        Args:
            original_event: Original event data
            error_message: Error message
            error_type: Type of error
            topic: Original topic
        
        Returns:
            Tuple of (key, value) for DLQ message
        """
        error_msg = ErrorMessage(
            original_event=original_event,
            error_message=error_message,
            error_type=error_type,
            topic=topic
        )
        
        # Use event_id as partition key if available
        partition_key = original_event.get("event_id")
        value = error_msg.to_json()
        
        return (partition_key.encode('utf-8') if partition_key else None, value)
    
    def parse_error_message(self, value: bytes) -> ErrorMessage:
        """Parse an error message from DLQ.
        
        Args:
            value: Error message value
        
        Returns:
            ErrorMessage object
        """
        error_dict = json.loads(value.decode('utf-8'))
        return ErrorMessage(
            original_event=error_dict["original_event"],
            error_message=error_dict["error_message"],
            error_type=error_dict["error_type"],
            topic=error_dict["topic"],
            timestamp=datetime.fromisoformat(error_dict["timestamp"])
        )