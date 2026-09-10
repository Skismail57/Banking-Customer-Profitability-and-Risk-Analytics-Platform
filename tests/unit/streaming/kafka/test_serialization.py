"""Unit tests for Kafka serialization and deserialization.

This module tests the message serialization and deserialization logic.
"""

import pytest
import json
from datetime import datetime
from decimal import Decimal

from src.streaming.kafka.serialization import (
    MessageSerializer,
    MessageDeserializer,
    ErrorMessage,
    DeadLetterQueueHandler,
)
from src.streaming.schemas import TransactionEvent, EventType


class TestMessageSerializer:
    """Test MessageSerializer class."""
    
    @pytest.fixture
    def serializer(self):
        """Create a message serializer."""
        return MessageSerializer(include_metadata=True)
    
    def test_serialize_event_dict(self, serializer):
        """Test serializing an event dictionary."""
        event_dict = {
            "event_id": "evt_123",
            "event_type": "transaction",
            "event_timestamp": datetime.utcnow().isoformat(),
            "source_system": "core_banking",
            "customer_key": "cust_123",
        }
        
        key, value = serializer.serialize(event_dict, "transactions")
        
        assert value is not None
        assert isinstance(value, bytes)
        
        # Deserialize and check
        deserialized = json.loads(value.decode('utf-8'))
        assert deserialized["event_id"] == "evt_123"
        assert "_metadata" in deserialized
        assert deserialized["_metadata"]["topic"] == "transactions"
    
    def test_serialize_pydantic_event(self, serializer):
        """Test serializing a Pydantic event object."""
        event = TransactionEvent(
            event_id="evt_txn_123",
            event_timestamp=datetime.utcnow(),
            source_system="core_banking",
            customer_key="cust_123",
            transaction_id="txn_456",
            transaction_type="purchase",
            channel="online",
            amount=Decimal("100.50")
        )
        
        key, value = serializer.serialize(event, "transactions")
        
        assert value is not None
        assert isinstance(value, bytes)
        
        # Deserialize and check
        deserialized = json.loads(value.decode('utf-8'))
        assert deserialized["event_id"] == "evt_txn_123"
        assert deserialized["transaction_id"] == "txn_456"
        assert deserialized["amount"] == 100.50  # Decimal converted to float
    
    def test_serialize_with_partition_key(self, serializer):
        """Test serializing with partition key."""
        event_dict = {
            "event_id": "evt_123",
            "event_type": "transaction",
            "event_timestamp": datetime.utcnow().isoformat(),
            "source_system": "core_banking",
            "customer_key": "cust_123",
        }
        
        key, value = serializer.serialize(event_dict, "transactions", partition_key="cust_123")
        
        assert key is not None
        assert isinstance(key, bytes)
        assert key.decode('utf-8') == "cust_123"
    
    def test_serialize_batch(self, serializer):
        """Test serializing a batch of events."""
        events = [
            {
                "event_id": "evt_1",
                "event_type": "transaction",
                "event_timestamp": datetime.utcnow().isoformat(),
                "source_system": "core_banking",
                "customer_key": "cust_1",
            },
            {
                "event_id": "evt_2",
                "event_type": "transaction",
                "event_timestamp": datetime.utcnow().isoformat(),
                "source_system": "core_banking",
                "customer_key": "cust_2",
            },
        ]
        
        messages = serializer.serialize_batch(events, "transactions")
        
        assert len(messages) == 2
        for key, value in messages:
            assert value is not None
            assert isinstance(value, bytes)
    
    def test_json_encoder_datetime(self, serializer):
        """Test JSON encoder for datetime."""
        event_dict = {
            "event_id": "evt_123",
            "event_type": "transaction",
            "event_timestamp": datetime.utcnow(),
            "source_system": "core_banking",
        }
        
        key, value = serializer.serialize(event_dict, "transactions")
        deserialized = json.loads(value.decode('utf-8'))
        
        # Should be ISO format string
        assert isinstance(deserialized["event_timestamp"], str)
    
    def test_json_encoder_decimal(self, serializer):
        """Test JSON encoder for Decimal."""
        event_dict = {
            "event_id": "evt_123",
            "event_type": "transaction",
            "event_timestamp": datetime.utcnow().isoformat(),
            "source_system": "core_banking",
            "amount": Decimal("100.50"),
        }
        
        key, value = serializer.serialize(event_dict, "transactions")
        deserialized = json.loads(value.decode('utf-8'))
        
        # Should be float
        assert isinstance(deserialized["amount"], float)
        assert deserialized["amount"] == 100.50


class TestMessageDeserializer:
    """Test MessageDeserializer class."""
    
    @pytest.fixture
    def deserializer(self):
        """Create a message deserializer."""
        return MessageDeserializer(validate=False)
    
    def test_deserialize_message(self, deserializer):
        """Test deserializing a message."""
        event_dict = {
            "event_id": "evt_123",
            "event_type": "transaction",
            "event_timestamp": datetime.utcnow().isoformat(),
            "source_system": "core_banking",
            "_metadata": {"topic": "transactions"},
        }
        
        value = json.dumps(event_dict).encode('utf-8')
        key = b"cust_123"
        
        partition_key, result = deserializer.deserialize(key, value, "transactions")
        
        assert partition_key == "cust_123"
        assert result["event_id"] == "evt_123"
        assert "_metadata" not in result  # Metadata should be removed
    
    def test_deserialize_without_key(self, deserializer):
        """Test deserializing without partition key."""
        event_dict = {
            "event_id": "evt_123",
            "event_type": "transaction",
            "event_timestamp": datetime.utcnow().isoformat(),
            "source_system": "core_banking",
        }
        
        value = json.dumps(event_dict).encode('utf-8')
        
        partition_key, result = deserializer.deserialize(None, value, "transactions")
        
        assert partition_key is None
        assert result["event_id"] == "evt_123"
    
    def test_deserialize_batch(self, deserializer):
        """Test deserializing a batch of messages."""
        messages = [
            (b"cust_1", json.dumps({"event_id": "evt_1"}).encode('utf-8')),
            (b"cust_2", json.dumps({"event_id": "evt_2"}).encode('utf-8')),
        ]
        
        events = deserializer.deserialize_batch(messages, "transactions")
        
        assert len(events) == 2
        assert events[0][0] == "cust_1"
        assert events[0][1]["event_id"] == "evt_1"
        assert events[1][0] == "cust_2"
        assert events[1][1]["event_id"] == "evt_2"


class TestErrorMessage:
    """Test ErrorMessage class."""
    
    def test_error_message_creation(self):
        """Test creating an error message."""
        original_event = {"event_id": "evt_123"}
        error_msg = ErrorMessage(
            original_event=original_event,
            error_message="Validation failed",
            error_type="validation",
            topic="transactions"
        )
        
        assert error_msg.original_event == original_event
        assert error_msg.error_message == "Validation failed"
        assert error_msg.error_type == "validation"
        assert error_msg.topic == "transactions"
        assert error_msg.timestamp is not None
    
    def test_error_message_to_dict(self):
        """Test converting error message to dictionary."""
        original_event = {"event_id": "evt_123"}
        error_msg = ErrorMessage(
            original_event=original_event,
            error_message="Validation failed",
            error_type="validation",
            topic="transactions"
        )
        
        result = error_msg.to_dict()
        
        assert result["original_event"] == original_event
        assert result["error_message"] == "Validation failed"
        assert result["error_type"] == "validation"
        assert result["topic"] == "transactions"
        assert "timestamp" in result
    
    def test_error_message_to_json(self):
        """Test converting error message to JSON."""
        original_event = {"event_id": "evt_123"}
        error_msg = ErrorMessage(
            original_event=original_event,
            error_message="Validation failed",
            error_type="validation",
            topic="transactions"
        )
        
        json_bytes = error_msg.to_json()
        
        assert isinstance(json_bytes, bytes)
        parsed = json.loads(json_bytes.decode('utf-8'))
        assert parsed["event_id"] == "evt_123"


class TestDeadLetterQueueHandler:
    """Test DeadLetterQueueHandler class."""
    
    @pytest.fixture
    def dlq_handler(self):
        """Create a DLQ handler."""
        serializer = MessageSerializer()
        return DeadLetterQueueHandler(serializer)
    
    def test_create_error_message(self, dlq_handler):
        """Test creating an error message for DLQ."""
        original_event = {"event_id": "evt_123"}
        
        key, value = dlq_handler.create_error_message(
            original_event=original_event,
            error_message="Validation failed",
            error_type="validation",
            topic="transactions"
        )
        
        assert key is not None
        assert isinstance(key, bytes)
        assert key.decode('utf-8') == "evt_123"
        assert isinstance(value, bytes)
    
    def test_create_error_message_without_event_id(self, dlq_handler):
        """Test creating error message without event_id."""
        original_event = {"event_type": "transaction"}
        
        key, value = dlq_handler.create_error_message(
            original_event=original_event,
            error_message="Validation failed",
            error_type="validation",
            topic="transactions"
        )
        
        assert key is None  # No event_id
        assert isinstance(value, bytes)
    
    def test_parse_error_message(self, dlq_handler):
        """Test parsing an error message from DLQ."""
        original_event = {"event_id": "evt_123"}
        
        key, value = dlq_handler.create_error_message(
            original_event=original_event,
            error_message="Validation failed",
            error_type="validation",
            topic="transactions"
        )
        
        parsed = dlq_handler.parse_error_message(value)
        
        assert isinstance(parsed, ErrorMessage)
        assert parsed.original_event == original_event
        assert parsed.error_message == "Validation failed"
        assert parsed.error_type == "validation"
        assert parsed.topic == "transactions"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])