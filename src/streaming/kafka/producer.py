"""Kafka producer abstraction for streaming pipeline.

This module provides a high-level abstraction for producing events to Kafka
with automatic serialization, error handling, and metrics tracking.
"""

import logging
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime
from collections import defaultdict

from confluent_kafka import Producer, KafkaException, KafkaError
from confluent_kafka.serialization import StringSerializer

from src.streaming.config import StreamingConfig
from src.streaming.kafka.serialization import MessageSerializer

logger = logging.getLogger(__name__)


class KafkaProducer:
    """High-level Kafka producer with automatic serialization and error handling."""
    
    def __init__(
        self,
        config: StreamingConfig,
        serializer: Optional[MessageSerializer] = None
    ):
        """Initialize Kafka producer.
        
        Args:
            config: Streaming configuration
            serializer: Optional custom serializer
        """
        self.config = config
        self.serializer = serializer or MessageSerializer()
        
        # Build producer configuration
        producer_config = {
            'bootstrap.servers': config.kafka.bootstrap_servers,
            'client.id': config.kafka.client_id or 'banking-analytics-producer',
            'acks': config.kafka.acks,
            'compression.type': config.kafka.compression_type,
            'linger.ms': config.kafka.linger_ms,
            'batch.size': config.kafka.batch_size,
            'max.in.flight.requests.per.connection': config.kafka.max_in_flight,
            'enable.idempotence': config.kafka.enable_idempotence,
            'message.timeout.ms': config.kafka.message_timeout_ms,
            'queue.buffering.max.messages': config.kafka.queue_buffering_max_messages,
            'queue.buffering.max.kbytes': config.kafka.queue_buffering_max_kbytes,
        }
        
        # Add authentication if configured
        if config.kafka.security_protocol:
            producer_config['security.protocol'] = config.kafka.security_protocol
        if config.kafka.sasl_mechanism:
            producer_config['sasl.mechanism'] = config.kafka.sasl_mechanism
        if config.kafka.sasl_username:
            producer_config['sasl.username'] = config.kafka.sasl_username
        if config.kafka.sasl_password:
            producer_config['sasl.password'] = config.kafka.sasl_password
        
        # Create producer
        self.producer = Producer(producer_config)
        
        # Metrics tracking
        self.metrics = {
            'messages_produced': 0,
            'messages_failed': 0,
            'bytes_produced': 0,
            'errors': defaultdict(int),
        }
        
        logger.info(f"Kafka producer initialized with bootstrap servers: {config.kafka.bootstrap_servers}")
    
    def produce(
        self,
        topic: str,
        event: Dict[str, Any],
        partition_key: Optional[str] = None,
        on_delivery: Optional[Callable] = None
    ) -> None:
        """Produce a single event to Kafka.
        
        Args:
            topic: Topic name
            event: Event data dictionary
            partition_key: Optional partition key
            on_delivery: Optional callback function for delivery reports
        """
        try:
            # Serialize event
            key, value = self.serializer.serialize(event, topic, partition_key)
            
            # Produce message
            self.producer.produce(
                topic=topic,
                key=key,
                value=value,
                on_delivery=self._delivery_callback(on_delivery)
            )
            
            # Update metrics
            self.metrics['messages_produced'] += 1
            self.metrics['bytes_produced'] += len(value)
            
            # Poll to handle delivery reports
            self.producer.poll(0)
            
        except Exception as e:
            logger.error(f"Failed to produce message to topic {topic}: {e}")
            self.metrics['messages_failed'] += 1
            self.metrics['errors'][str(e)] += 1
            raise
    
    def produce_batch(
        self,
        topic: str,
        events: List[Dict[str, Any]],
        on_delivery: Optional[Callable] = None
    ) -> int:
        """Produce a batch of events to Kafka.
        
        Args:
            topic: Topic name
            events: List of event data dictionaries
            on_delivery: Optional callback function for delivery reports
        
        Returns:
            Number of messages produced
        """
        count = 0
        for event in events:
            try:
                self.produce(topic, event, on_delivery=on_delivery)
                count += 1
            except Exception as e:
                logger.error(f"Failed to produce message in batch: {e}")
                continue
        
        # Flush to ensure all messages are sent
        self.flush()
        
        return count
    
    def flush(self, timeout: Optional[float] = None) -> int:
        """Flush all buffered messages.
        
        Args:
            timeout: Optional timeout in seconds
        
        Returns:
            Number of messages remaining in queue
        """
        try:
            remaining = self.producer.flush(timeout=timeout)
            if remaining > 0:
                logger.warning(f"{remaining} messages remaining in queue after flush")
            return remaining
        except Exception as e:
            logger.error(f"Failed to flush producer: {e}")
            return -1
    
    def _delivery_callback(self, user_callback: Optional[Callable] = None):
        """Create delivery callback wrapper.
        
        Args:
            user_callback: Optional user-provided callback
        
        Returns:
            Callback function
        """
        def callback(err, msg):
            if err is not None:
                logger.error(f"Message delivery failed: {err}")
                self.metrics['messages_failed'] += 1
                self.metrics['errors'][str(err)] += 1
            else:
                logger.debug(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")
            
            # Call user callback if provided
            if user_callback:
                user_callback(err, msg)
        
        return callback
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get producer metrics.
        
        Returns:
            Dictionary of metrics
        """
        return dict(self.metrics)
    
    def reset_metrics(self) -> None:
        """Reset metrics counters."""
        self.metrics = {
            'messages_produced': 0,
            'messages_failed': 0,
            'bytes_produced': 0,
            'errors': defaultdict(int),
        }
    
    def close(self) -> None:
        """Close the producer and flush all messages."""
        logger.info("Closing Kafka producer...")
        self.flush(timeout=30)
        logger.info("Kafka producer closed")


class AsyncKafkaProducer(KafkaProducer):
    """Asynchronous Kafka producer with callback-based error handling."""
    
    def __init__(
        self,
        config: StreamingConfig,
        serializer: Optional[MessageSerializer] = None,
        dlq_topic: Optional[str] = None
    ):
        """Initialize async Kafka producer.
        
        Args:
            config: Streaming configuration
            serializer: Optional custom serializer
            dlq_topic: Optional dead letter queue topic
        """
        super().__init__(config, serializer)
        self.dlq_topic = dlq_topic
        self._pending_messages = 0
    
    def produce_async(
        self,
        topic: str,
        event: Dict[str, Any],
        partition_key: Optional[str] = None,
        on_success: Optional[Callable] = None,
        on_error: Optional[Callable] = None
    ) -> None:
        """Produce event asynchronously with success/error callbacks.
        
        Args:
            topic: Topic name
            event: Event data dictionary
            partition_key: Optional partition key
            on_success: Callback for successful delivery
            on_error: Callback for failed delivery
        """
        try:
            # Serialize event
            key, value = self.serializer.serialize(event, topic, partition_key)
            
            # Increment pending count
            self._pending_messages += 1
            
            # Produce with custom callback
            self.producer.produce(
                topic=topic,
                key=key,
                value=value,
                on_delivery=self._async_delivery_callback(on_success, on_error, topic, event)
            )
            
            # Update metrics
            self.metrics['messages_produced'] += 1
            self.metrics['bytes_produced'] += len(value)
            
            # Poll to handle delivery reports
            self.producer.poll(0)
            
        except Exception as e:
            logger.error(f"Failed to produce async message to topic {topic}: {e}")
            self.metrics['messages_failed'] += 1
            self.metrics['errors'][str(e)] += 1
            self._pending_messages -= 1
            
            # Call error callback
            if on_error:
                on_error(e, event)
    
    def _async_delivery_callback(
        self,
        on_success: Optional[Callable],
        on_error: Optional[Callable],
        topic: str,
        event: Dict[str, Any]
    ):
        """Create async delivery callback.
        
        Args:
            on_success: Success callback
            on_error: Error callback
            topic: Topic name
            event: Original event data
        
        Returns:
            Callback function
        """
        def callback(err, msg):
            self._pending_messages -= 1
            
            if err is not None:
                logger.error(f"Async message delivery failed: {err}")
                self.metrics['messages_failed'] += 1
                self.metrics['errors'][str(err)] += 1
                
                # Send to DLQ if configured
                if self.dlq_topic:
                    self._send_to_dlq(event, str(err))
                
                # Call error callback
                if on_error:
                    on_error(err, event)
            else:
                logger.debug(f"Async message delivered to {msg.topic()} [{msg.partition()}]")
                
                # Call success callback
                if on_success:
                    on_success(msg)
        
        return callback
    
    def _send_to_dlq(self, event: Dict[str, Any], error_message: str) -> None:
        """Send failed event to dead letter queue.
        
        Args:
            event: Failed event data
            error_message: Error message
        """
        try:
            from src.streaming.kafka.serialization import DeadLetterQueueHandler
            dlq_handler = DeadLetterQueueHandler(self.serializer)
            key, value = dlq_handler.create_error_message(
                original_event=event,
                error_message=error_message,
                error_type="delivery_failure",
                topic="unknown"
            )
            
            self.producer.produce(
                topic=self.dlq_topic,
                key=key,
                value=value,
                on_delivery=self._dlq_delivery_callback()
            )
            
            logger.info(f"Sent failed event to DLQ topic: {self.dlq_topic}")
            
        except Exception as e:
            logger.error(f"Failed to send event to DLQ: {e}")
    
    def _dlq_delivery_callback(self):
        """Create DLQ delivery callback."""
        def callback(err, msg):
            if err is not None:
                logger.error(f"Failed to deliver to DLQ: {err}")
            else:
                logger.debug(f"Delivered to DLQ: {msg.topic()}")
        return callback
    
    def get_pending_count(self) -> int:
        """Get number of pending messages.
        
        Returns:
            Number of pending messages
        """
        return self._pending_messages
    
    def wait_for_pending(self, timeout: Optional[float] = None) -> bool:
        """Wait for all pending messages to be delivered.
        
        Args:
            timeout: Optional timeout in seconds
        
        Returns:
            True if all messages delivered, False if timeout
        """
        import time
        start_time = time.time()
        
        while self._pending_messages > 0:
            if timeout and (time.time() - start_time) > timeout:
                logger.warning(f"Timeout waiting for {self._pending_messages} pending messages")
                return False
            
            self.producer.poll(0.1)
            time.sleep(0.01)
        
        return True