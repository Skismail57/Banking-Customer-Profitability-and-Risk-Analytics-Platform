"""Kafka producer and consumer abstractions for streaming pipeline.

This module provides high-level abstractions for Kafka operations including
producer, consumer, topic management, and message serialization.
"""

from .producer import KafkaProducer, AsyncKafkaProducer
from .consumer import KafkaConsumer, BatchKafkaConsumer
from .topics import TopicManager, TopicConfig, create_banking_topics
from .serialization import (
    MessageSerializer,
    MessageDeserializer,
    ErrorMessage,
    DeadLetterQueueHandler,
)
from .consumer_groups import (
    ConsumerGroupManager,
    ConsumerGroupInfo,
    PartitionLag,
    ConsumerGroupLag,
    check_all_consumer_groups_lag,
)

__all__ = [
    "KafkaProducer",
    "AsyncKafkaProducer",
    "KafkaConsumer",
    "BatchKafkaConsumer",
    "TopicManager",
    "TopicConfig",
    "create_banking_topics",
    "MessageSerializer",
    "MessageDeserializer",
    "ErrorMessage",
    "DeadLetterQueueHandler",
    "ConsumerGroupManager",
    "ConsumerGroupInfo",
    "PartitionLag",
    "ConsumerGroupLag",
    "check_all_consumer_groups_lag",
]