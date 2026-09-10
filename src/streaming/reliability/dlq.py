"""Dead Letter Queue (DLQ) handler for failed messages.

This module provides functionality for handling failed messages by sending
them to a dead letter queue for later inspection and reprocessing.
"""

import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class DeadLetterMessage:
    """Dead letter message structure."""
    original_topic: str
    original_partition: Optional[int]
    original_offset: Optional[int]
    original_key: Optional[str]
    original_value: Optional[str]
    error_type: str
    error_message: str
    error_timestamp: str
    retry_count: int = 0
    headers: Optional[Dict[str, str]] = None
    context: Optional[Dict[str, Any]] = None


class DeadLetterQueueHandler:
    """Handle dead letter queue operations."""
    
    def __init__(self, producer, dlq_topic: str = "dlq"):
        """Initialize DLQ handler.
        
        Args:
            producer: Kafka producer instance
            dlq_topic: Dead letter queue topic name
        """
        self.producer = producer
        self.dlq_topic = dlq_topic
    
    def create_error_message(
        self,
        original_event: Dict[str, Any],
        error_message: str,
        error_type: str,
        topic: str,
        partition: Optional[int] = None,
        offset: Optional[int] = None,
        key: Optional[str] = None,
        retry_count: int = 0,
        headers: Optional[Dict[str, str]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> tuple[Optional[str], str]:
        """Create a dead letter message.
        
        Args:
            original_event: Original event data
            error_message: Error message
            error_type: Type of error
            topic: Original topic
            partition: Original partition
            offset: Original offset
            key: Original message key
            retry_count: Number of retries attempted
            headers: Original message headers
            context: Additional context information
        
        Returns:
            Tuple of (key, value) for DLQ message
        """
        dlq_message = DeadLetterMessage(
            original_topic=topic,
            original_partition=partition,
            original_offset=offset,
            original_key=key,
            original_value=json.dumps(original_event) if original_event else None,
            error_type=error_type,
            error_message=error_message,
            error_timestamp=datetime.utcnow().isoformat(),
            retry_count=retry_count,
            headers=headers,
            context=context
        )
        
        # Use original key or generate one from error type
        dlq_key = key or f"{error_type}_{topic}"
        dlq_value = json.dumps(asdict(dlq_message))
        
        return dlq_key, dlq_value
    
    def send_to_dlq(
        self,
        original_event: Dict[str, Any],
        error: Exception,
        topic: str,
        partition: Optional[int] = None,
        offset: Optional[int] = None,
        key: Optional[str] = None,
        retry_count: int = 0,
        headers: Optional[Dict[str, str]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send failed message to dead letter queue.
        
        Args:
            original_event: Original event data
            error: Exception that occurred
            topic: Original topic
            partition: Original partition
            offset: Original offset
            key: Original message key
            retry_count: Number of retries attempted
            headers: Original message headers
            context: Additional context information
        
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            dlq_key, dlq_value = self.create_error_message(
                original_event=original_event,
                error_message=str(error),
                error_type=type(error).__name__,
                topic=topic,
                partition=partition,
                offset=offset,
                key=key,
                retry_count=retry_count,
                headers=headers,
                context=context
            )
            
            # Produce to DLQ topic
            self.producer.produce(
                topic=self.dlq_topic,
                key=dlq_key.encode('utf-8') if dlq_key else None,
                value=dlq_value.encode('utf-8'),
                on_delivery=self._dlq_delivery_callback(topic, offset)
            )
            
            # Poll to handle delivery report
            self.producer.poll(0)
            
            logger.info(f"Sent message to DLQ: topic={topic}, offset={offset}, error={type(error).__name__}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to send message to DLQ: {e}")
            return False
    
    def _dlq_delivery_callback(self, original_topic: str, original_offset: Optional[int]):
        """Create DLQ delivery callback.
        
        Args:
            original_topic: Original topic for logging
            original_offset: Original offset for logging
        
        Returns:
            Callback function
        """
        def callback(err, msg):
            if err is not None:
                logger.error(f"Failed to deliver to DLQ for {original_topic} offset {original_offset}: {err}")
            else:
                logger.debug(f"Delivered to DLQ: {msg.topic()} [{msg.partition()}] offset {msg.offset()}")
        return callback
    
    def flush(self, timeout: Optional[float] = None) -> int:
        """Flush pending DLQ messages.
        
        Args:
            timeout: Optional timeout in seconds
        
        Returns:
            Number of messages remaining in queue
        """
        try:
            remaining = self.producer.flush(timeout=timeout)
            if remaining > 0:
                logger.warning(f"{remaining} DLQ messages remaining after flush")
            return remaining
        except Exception as e:
            logger.error(f"Failed to flush DLQ messages: {e}")
            return -1


class DLQReprocessor:
    """Reprocess messages from dead letter queue."""
    
    def __init__(self, consumer, dlq_topic: str = "dlq"):
        """Initialize DLQ reprocessor.
        
        Args:
            consumer: Kafka consumer instance
            dlq_topic: Dead letter queue topic name
        """
        self.consumer = consumer
        self.dlq_topic = dlq_topic
    
    def consume_dlq(
        self,
        reprocess_handler: Callable,
        max_messages: int = 100,
        timeout: float = 1.0
    ) -> int:
        """Consume and reprocess messages from DLQ.
        
        Args:
            reprocess_handler: Function to handle reprocessing
            max_messages: Maximum messages to reprocess
            timeout: Poll timeout in seconds
        
        Returns:
            Number of messages reprocessed
        """
        # Subscribe to DLQ topic
        self.consumer.subscribe([self.dlq_topic])
        
        reprocessed = 0
        
        for _ in range(max_messages):
            msg = self.consumer.poll(timeout=timeout)
            
            if msg is None:
                break
            
            if msg.error():
                logger.error(f"DLQ consumer error: {msg.error()}")
                continue
            
            try:
                # Parse DLQ message
                dlq_data = json.loads(msg.value().decode('utf-8'))
                
                # Extract original event
                original_event = json.loads(dlq_data['original_value']) if dlq_data.get('original_value') else None
                
                if original_event:
                    # Call reprocess handler
                    success = reprocess_handler(
                        original_event=original_event,
                        error_type=dlq_data.get('error_type'),
                        error_message=dlq_data.get('error_message'),
                        retry_count=dlq_data.get('retry_count', 0),
                        original_topic=dlq_data.get('original_topic')
                    )
                    
                    if success:
                        reprocessed += 1
                        # Commit offset on successful reprocessing
                        self.consumer.commit(message=msg, asynchronous=False)
                    else:
                        logger.warning(f"Reprocessing failed for message from {dlq_data.get('original_topic')}")
            
            except Exception as e:
                logger.error(f"Failed to reprocess DLQ message: {e}")
                continue
        
        logger.info(f"Reprocessed {reprocessed} messages from DLQ")
        return reprocessed
