"""Kafka consumer abstraction for streaming pipeline.

This module provides a high-level abstraction for consuming events from Kafka
with automatic deserialization, error handling, and metrics tracking.
"""

import logging
from typing import Optional, Dict, Any, List, Callable, Iterator
from datetime import datetime, timezone
from collections import defaultdict

from confluent_kafka import Consumer, KafkaException, KafkaError, TopicPartition
from confluent_kafka.serialization import StringDeserializer

from src.streaming.config import StreamingConfig
from src.streaming.kafka.serialization import MessageDeserializer

logger = logging.getLogger(__name__)


class KafkaConsumer:
    """High-level Kafka consumer with automatic deserialization and error handling."""
    
    def __init__(
        self,
        config: StreamingConfig,
        deserializer: Optional[MessageDeserializer] = None
    ):
        """Initialize Kafka consumer.
        
        Args:
            config: Streaming configuration
            deserializer: Optional custom deserializer
        """
        self.config = config
        self.deserializer = deserializer or MessageDeserializer()
        
        # Build consumer configuration
        consumer_config = {
            'bootstrap.servers': config.kafka.bootstrap_servers,
            'group.id': config.kafka.group_id,
            'client.id': config.kafka.client_id or 'banking-analytics-consumer',
            'auto.offset.reset': config.kafka.auto_offset_reset,
            'enable.auto.commit': config.kafka.enable_auto_commit,
            'auto.commit.interval.ms': config.kafka.auto_commit_interval_ms,
            'session.timeout.ms': config.kafka.session_timeout_ms,
            'heartbeat.interval.ms': config.kafka.heartbeat_interval_ms,
            'max.poll.interval.ms': config.kafka.max_poll_interval_ms,
            'max.poll.records': config.kafka.max_poll_records,
            'fetch.min.bytes': config.kafka.fetch_min_bytes,
            'fetch.max.wait.ms': config.kafka.fetch_max_wait_ms,
            'enable.partition.eof': False,
        }
        
        # Add authentication if configured
        if config.kafka.security_protocol:
            consumer_config['security.protocol'] = config.kafka.security_protocol
        if config.kafka.sasl_mechanism:
            consumer_config['sasl.mechanism'] = config.kafka.sasl_mechanism
        if config.kafka.sasl_username:
            consumer_config['sasl.username'] = config.kafka.sasl_username
        if config.kafka.sasl_password:
            consumer_config['sasl.password'] = config.kafka.sasl_password
        
        # Create consumer
        self.consumer = Consumer(consumer_config)
        
        # Metrics tracking
        self.metrics = {
            'messages_consumed': 0,
            'messages_failed': 0,
            'bytes_consumed': 0,
            'commits': 0,
            'rebalances': 0,
            'errors': defaultdict(int),
        }
        
        logger.info(f"Kafka consumer initialized with group_id: {config.kafka.group_id}")
    
    def subscribe(
        self,
        topics: List[str],
        on_assign: Optional[Callable] = None,
        on_revoke: Optional[Callable] = None
    ) -> None:
        """Subscribe to a list of topics.
        
        Args:
            topics: List of topic names
            on_assign: Optional callback for partition assignment
            on_revoke: Optional callback for partition revocation
        """
        try:
            self.consumer.subscribe(
                topics,
                on_assign=self._partition_assign_callback(on_assign),
                on_revoke=self._partition_revoke_callback(on_revoke)
            )
            logger.info(f"Subscribed to topics: {topics}")
        except KafkaException as e:
            logger.error(f"Failed to subscribe to topics: {e}")
            raise
    
    def _partition_assign_callback(self, user_callback: Optional[Callable]):
        """Create partition assign callback wrapper.
        
        Args:
            user_callback: Optional user-provided callback
        
        Returns:
            Callback function
        """
        def callback(consumer, partitions):
            logger.info(f"Partitions assigned: {len(partitions)}")
            self.metrics['rebalances'] += 1
            
            for partition in partitions:
                logger.debug(f"Assigned: {partition.topic} [{partition.partition}]")
            
            if user_callback:
                user_callback(consumer, partitions)
        
        return callback
    
    def _partition_revoke_callback(self, user_callback: Optional[Callable]):
        """Create partition revoke callback wrapper.
        
        Args:
            user_callback: Optional user-provided callback
        
        Returns:
            Callback function
        """
        def callback(consumer, partitions):
            logger.info(f"Partitions revoked: {len(partitions)}")
            
            for partition in partitions:
                logger.debug(f"Revoked: {partition.topic} [{partition.partition}]")
            
            if user_callback:
                user_callback(consumer, partitions)
        
        return callback
    
    def poll(
        self,
        timeout: float = 1.0,
        deserialize: bool = True
    ) -> Optional[tuple[Optional[str], Dict[str, Any]]]:
        """Poll for a single message.
        
        Args:
            timeout: Poll timeout in seconds
            deserialize: Whether to deserialize message
        
        Returns:
            Tuple of (partition_key, event_dict) or None if no message
        """
        try:
            msg = self.consumer.poll(timeout=timeout)
            
            if msg is None:
                return None
            
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    logger.debug(f"Reached end of partition: {msg.topic()} [{msg.partition()}]")
                    return None
                else:
                    logger.error(f"Consumer error: {msg.error()}")
                    self.metrics['messages_failed'] += 1
                    self.metrics['errors'][str(msg.error())] += 1
                    raise KafkaException(msg.error())
            
            # Update metrics
            self.metrics['messages_consumed'] += 1
            self.metrics['bytes_consumed'] += len(msg.value())
            
            # Deserialize message
            if deserialize:
                partition_key, event_dict = self.deserializer.deserialize(
                    key=msg.key(),
                    value=msg.value(),
                    topic=msg.topic()
                )
                return partition_key, event_dict
            else:
                partition_key = msg.key().decode('utf-8') if msg.key() else None
                event_dict = {
                    'key': partition_key,
                    'value': msg.value().decode('utf-8'),
                    'topic': msg.topic(),
                    'partition': msg.partition(),
                    'offset': msg.offset(),
                    'timestamp': msg.timestamp()[1] if msg.timestamp()[0] else None,
                }
                return partition_key, event_dict
        
        except Exception as e:
            logger.error(f"Failed to poll message: {e}")
            self.metrics['messages_failed'] += 1
            self.metrics['errors'][str(e)] += 1
            raise
    
    def poll_batch(
        self,
        max_messages: int = 100,
        timeout: float = 1.0,
        deserialize: bool = True
    ) -> List[tuple[Optional[str], Dict[str, Any]]]:
        """Poll for multiple messages.
        
        Args:
            max_messages: Maximum number of messages to poll
            timeout: Poll timeout in seconds
            deserialize: Whether to deserialize messages
        
        Returns:
            List of (partition_key, event_dict) tuples
        """
        messages = []
        
        for _ in range(max_messages):
            msg = self.poll(timeout=timeout, deserialize=deserialize)
            if msg is None:
                break
            messages.append(msg)
        
        return messages
    
    def consume(
        self,
        message_handler: Callable,
        timeout: float = 1.0,
        auto_commit: bool = True
    ) -> None:
        """Consume messages and pass to handler function.
        
        Args:
            message_handler: Function to handle each message
            timeout: Poll timeout in seconds
            auto_commit: Whether to auto-commit offsets
        """
        try:
            while True:
                msg = self.poll(timeout=timeout)
                
                if msg is None:
                    continue
                
                partition_key, event_dict = msg
                
                try:
                    # Call message handler
                    message_handler(partition_key, event_dict)
                    
                    # Commit offset if auto_commit is enabled
                    if auto_commit and not self.config.kafka.enable_auto_commit:
                        self.commit()
                
                except Exception as e:
                    logger.error(f"Message handler failed: {e}")
                    # Continue processing other messages
        
        except KeyboardInterrupt:
            logger.info("Consumer interrupted by user")
        except Exception as e:
            logger.error(f"Consumer error: {e}")
            raise
        finally:
            self.close()
    
    def commit(self, asynchronous: bool = False) -> None:
        """Commit current offsets.
        
        Args:
            asynchronous: Whether to commit asynchronously
        """
        try:
            if asynchronous:
                self.consumer.commit(asynchronous=True)
            else:
                self.consumer.commit()
            self.metrics['commits'] += 1
            logger.debug("Offsets committed")
        except KafkaException as e:
            logger.error(f"Failed to commit offsets: {e}")
            raise
    
    def commit_message(self, message, asynchronous: bool = False) -> None:
        """Commit offset for a specific message.
        
        Args:
            message: Kafka message
            asynchronous: Whether to commit asynchronously
        """
        try:
            if asynchronous:
                self.consumer.commit(message=message, asynchronous=True)
            else:
                self.consumer.commit(message=message)
            self.metrics['commits'] += 1
            logger.debug(f"Offset committed for {message.topic()} [{message.partition()}] offset {message.offset()}")
        except KafkaException as e:
            logger.error(f"Failed to commit message offset: {e}")
            raise
    
    def seek(self, topic: str, partition: int, offset: int) -> None:
        """Seek to a specific offset.
        
        Args:
            topic: Topic name
            partition: Partition number
            offset: Offset to seek to
        """
        try:
            tp = TopicPartition(topic, partition, offset)
            self.consumer.seek(tp)
            logger.info(f"Seeked to {topic} [{partition}] offset {offset}")
        except KafkaException as e:
            logger.error(f"Failed to seek: {e}")
            raise
    
    def get_watermark_offsets(self, topic: str, partition: int) -> tuple[int, int]:
        """Get watermark offsets for a partition.
        
        Args:
            topic: Topic name
            partition: Partition number
        
        Returns:
            Tuple of (low, high) offsets
        """
        try:
            tp = TopicPartition(topic, partition)
            low, high = self.consumer.get_watermark_offsets(tp)
            return low, high
        except KafkaException as e:
            logger.error(f"Failed to get watermark offsets: {e}")
            raise
    
    def get_committed_offsets(self, topic: str, partition: int) -> Optional[int]:
        """Get committed offset for a partition.
        
        Args:
            topic: Topic name
            partition: Partition number
        
        Returns:
            Committed offset or None if not committed
        """
        try:
            tp = TopicPartition(topic, partition)
            committed = self.consumer.committed([tp])
            if committed and committed[0].offset is not None:
                return committed[0].offset
            return None
        except KafkaException as e:
            logger.error(f"Failed to get committed offset: {e}")
            raise
    
    def get_position(self, topic: str, partition: int) -> int:
        """Get current position (next offset to consume).
        
        Args:
            topic: Topic name
            partition: Partition number
        
        Returns:
            Current position offset
        """
        try:
            tp = TopicPartition(topic, partition)
            position = self.consumer.position([tp])
            return position[0].offset
        except KafkaException as e:
            logger.error(f"Failed to get position: {e}")
            raise
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get consumer metrics.
        
        Returns:
            Dictionary of metrics
        """
        return dict(self.metrics)
    
    def reset_metrics(self) -> None:
        """Reset metrics counters."""
        self.metrics = {
            'messages_consumed': 0,
            'messages_failed': 0,
            'bytes_consumed': 0,
            'commits': 0,
            'rebalances': 0,
            'errors': defaultdict(int),
        }
    
    def close(self) -> None:
        """Close the consumer."""
        logger.info("Closing Kafka consumer...")
        self.consumer.close()
        logger.info("Kafka consumer closed")


class BatchKafkaConsumer(KafkaConsumer):
    """Batch-oriented Kafka consumer for processing messages in batches."""
    
    def __init__(
        self,
        config: StreamingConfig,
        deserializer: Optional[MessageDeserializer] = None,
        batch_size: int = 100,
        batch_timeout: float = 5.0
    ):
        """Initialize batch Kafka consumer.
        
        Args:
            config: Streaming configuration
            deserializer: Optional custom deserializer
            batch_size: Number of messages per batch
            batch_timeout: Maximum time to wait for batch
        """
        super().__init__(config, deserializer)
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
    
    def consume_batch(
        self,
        batch_handler: Callable,
        auto_commit: bool = True
    ) -> None:
        """Consume messages in batches and pass to handler.
        
        Args:
            batch_handler: Function to handle each batch
            auto_commit: Whether to auto-commit offsets
        """
        try:
            while True:
                # Collect batch
                batch = []
                start_time = datetime.now(timezone.utc).replace(tzinfo=None)
                
                while len(batch) < self.batch_size:
                    remaining_time = self.batch_timeout - (datetime.now(timezone.utc).replace(tzinfo=None) - start_time).total_seconds()
                    if remaining_time <= 0:
                        break
                    
                    msg = self.poll(timeout=min(remaining_time, 1.0))
                    if msg is not None:
                        batch.append(msg)
                
                if batch:
                    try:
                        # Call batch handler
                        batch_handler(batch)
                        
                        # Commit offsets if auto_commit is enabled
                        if auto_commit and not self.config.kafka.enable_auto_commit:
                            self.commit()
                    
                    except Exception as e:
                        logger.error(f"Batch handler failed: {e}")
                        # Continue processing other batches
                else:
                    logger.debug("No messages in batch, waiting...")
        
        except KeyboardInterrupt:
            logger.info("Batch consumer interrupted by user")
        except Exception as e:
            logger.error(f"Batch consumer error: {e}")
            raise
        finally:
            self.close()