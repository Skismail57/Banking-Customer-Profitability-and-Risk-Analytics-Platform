"""Topic management utilities for Kafka.

This module provides utilities for managing Kafka topics including
creation, deletion, listing, and configuration.
"""

import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from confluent_kafka import AdminClient, KafkaException, NewTopic, NewPartitions

from src.streaming.config import StreamingConfig

logger = logging.getLogger(__name__)


@dataclass
class TopicConfig:
    """Topic configuration."""
    name: str
    num_partitions: int = 3
    replication_factor: int = 1
    retention_ms: Optional[int] = None
    retention_bytes: Optional[int] = None
    cleanup_policy: Optional[str] = "delete"  # delete or compact
    segment_ms: Optional[int] = None
    segment_bytes: Optional[int] = None
    min_insync_replicas: Optional[int] = None
    compression_type: Optional[str] = None
    max_message_bytes: Optional[int] = None


class TopicManager:
    """Manage Kafka topics."""
    
    def __init__(self, config: StreamingConfig):
        """Initialize topic manager.
        
        Args:
            config: Streaming configuration
        """
        self.config = config
        
        # Build admin client configuration
        admin_config = {
            'bootstrap.servers': config.kafka.bootstrap_servers,
            'client.id': config.kafka.client_id or 'banking-analytics-topic-manager',
        }
        
        # Add authentication if configured
        if config.kafka.security_protocol:
            admin_config['security.protocol'] = config.kafka.security_protocol
        if config.kafka.sasl_mechanism:
            admin_config['sasl.mechanism'] = config.kafka.sasl_mechanism
        if config.kafka.sasl_username:
            admin_config['sasl.username'] = config.kafka.sasl_username
        if config.kafka.sasl_password:
            admin_config['sasl.password'] = config.kafka.sasl_password
        
        # Create admin client
        self.admin_client = AdminClient(admin_config)
        
        logger.info(f"Topic manager initialized with bootstrap servers: {config.kafka.bootstrap_servers}")
    
    def create_topic(
        self,
        topic_config: TopicConfig,
        validate_only: bool = False
    ) -> bool:
        """Create a new topic.
        
        Args:
            topic_config: Topic configuration
            validate_only: If True, only validate without creating
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if topic already exists
            if self.topic_exists(topic_config.name):
                logger.warning(f"Topic {topic_config.name} already exists")
                return False
            
            # Build topic configuration
            config_dict = {}
            if topic_config.retention_ms:
                config_dict['retention.ms'] = str(topic_config.retention_ms)
            if topic_config.retention_bytes:
                config_dict['retention.bytes'] = str(topic_config.retention_bytes)
            if topic_config.cleanup_policy:
                config_dict['cleanup.policy'] = topic_config.cleanup_policy
            if topic_config.segment_ms:
                config_dict['segment.ms'] = str(topic_config.segment_ms)
            if topic_config.segment_bytes:
                config_dict['segment.bytes'] = str(topic_config.segment_bytes)
            if topic_config.min_insync_replicas:
                config_dict['min.insync.replicas'] = str(topic_config.min_insync_replicas)
            if topic_config.compression_type:
                config_dict['compression.type'] = topic_config.compression_type
            if topic_config.max_message_bytes:
                config_dict['max.message.bytes'] = str(topic_config.max_message_bytes)
            
            # Create new topic
            new_topic = NewTopic(
                topic=topic_config.name,
                num_partitions=topic_config.num_partitions,
                replication_factor=topic_config.replication_factor,
                config=config_dict
            )
            
            if validate_only:
                logger.info(f"Validating topic creation for {topic_config.name}")
                return True
            
            # Create topic
            future = self.admin_client.create_topics([new_topic])
            
            # Wait for result
            for topic, future_result in future.items():
                try:
                    future_result.result()
                    logger.info(f"Topic {topic} created successfully")
                    return True
                except KafkaException as e:
                    logger.error(f"Failed to create topic {topic}: {e}")
                    return False
        
        except Exception as e:
            logger.error(f"Error creating topic {topic_config.name}: {e}")
            return False
    
    def create_topics(
        self,
        topic_configs: List[TopicConfig],
        validate_only: bool = False
    ) -> Dict[str, bool]:
        """Create multiple topics.
        
        Args:
            topic_configs: List of topic configurations
            validate_only: If True, only validate without creating
        
        Returns:
            Dictionary mapping topic name to success status
        """
        results = {}
        for topic_config in topic_configs:
            results[topic_config.name] = self.create_topic(topic_config, validate_only)
        return results
    
    def delete_topic(self, topic_name: str) -> bool:
        """Delete a topic.
        
        Args:
            topic_name: Name of topic to delete
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.topic_exists(topic_name):
                logger.warning(f"Topic {topic_name} does not exist")
                return False
            
            future = self.admin_client.delete_topics([topic_name])
            
            for topic, future_result in future.items():
                try:
                    future_result.result()
                    logger.info(f"Topic {topic} deleted successfully")
                    return True
                except KafkaException as e:
                    logger.error(f"Failed to delete topic {topic}: {e}")
                    return False
        
        except Exception as e:
            logger.error(f"Error deleting topic {topic_name}: {e}")
            return False
    
    def list_topics(self) -> List[str]:
        """List all topics.
        
        Returns:
            List of topic names
        """
        try:
            cluster_metadata = self.admin_client.list_topics(timeout=10)
            topics = list(cluster_metadata.topics.keys())
            logger.info(f"Found {len(topics)} topics")
            return topics
        except Exception as e:
            logger.error(f"Error listing topics: {e}")
            return []
    
    def topic_exists(self, topic_name: str) -> bool:
        """Check if a topic exists.
        
        Args:
            topic_name: Name of topic to check
        
        Returns:
            True if topic exists, False otherwise
        """
        try:
            cluster_metadata = self.admin_client.list_topics(timeout=10)
            return topic_name in cluster_metadata.topics
        except Exception as e:
            logger.error(f"Error checking topic existence: {e}")
            return False
    
    def get_topic_metadata(self, topic_name: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a topic.
        
        Args:
            topic_name: Name of topic
        
        Returns:
            Dictionary with topic metadata or None if not found
        """
        try:
            cluster_metadata = self.admin_client.list_topics(topic=topic_name, timeout=10)
            
            if topic_name not in cluster_metadata.topics:
                return None
            
            topic_metadata = cluster_metadata.topics[topic_name]
            
            partitions = {}
            for partition_id, partition_metadata in topic_metadata.partitions.items():
                partitions[partition_id] = {
                    'leader': partition_metadata.leader,
                    'replicas': partition_metadata.replicas,
                    'isrs': partition_metadata.isrs,
                }
            
            return {
                'name': topic_name,
                'partitions': partitions,
                'partition_count': len(partitions),
            }
        
        except Exception as e:
            logger.error(f"Error getting topic metadata for {topic_name}: {e}")
            return None
    
    def alter_topic_config(
        self,
        topic_name: str,
        config_updates: Dict[str, str]
    ) -> bool:
        """Alter topic configuration.
        
        Args:
            topic_name: Name of topic
            config_updates: Dictionary of config updates
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.topic_exists(topic_name):
                logger.warning(f"Topic {topic_name} does not exist")
                return False
            
            # Alter configuration
            future = self.admin_client.alter_configs({topic_name: config_updates})
            
            for resource, future_result in future.items():
                try:
                    future_result.result()
                    logger.info(f"Topic {resource} configuration updated successfully")
                    return True
                except KafkaException as e:
                    logger.error(f"Failed to alter topic config for {resource}: {e}")
                    return False
        
        except Exception as e:
            logger.error(f"Error altering topic config for {topic_name}: {e}")
            return False
    
    def add_partitions(
        self,
        topic_name: str,
        new_total_partition_count: int
    ) -> bool:
        """Add partitions to a topic.
        
        Args:
            topic_name: Name of topic
            new_total_partition_count: New total number of partitions
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.topic_exists(topic_name):
                logger.warning(f"Topic {topic_name} does not exist")
                return False
            
            # Get current partition count
            metadata = self.get_topic_metadata(topic_name)
            if not metadata:
                return False
            
            current_count = metadata['partition_count']
            if new_total_partition_count <= current_count:
                logger.warning(f"New partition count ({new_total_partition_count}) must be greater than current ({current_count})")
                return False
            
            # Add partitions
            new_partitions = NewPartitions(topic_name, new_total_partition_count)
            future = self.admin_client.create_partitions([new_partitions])
            
            for topic, future_result in future.items():
                try:
                    future_result.result()
                    logger.info(f"Partitions added to {topic} successfully")
                    return True
                except KafkaException as e:
                    logger.error(f"Failed to add partitions to {topic}: {e}")
                    return False
        
        except Exception as e:
            logger.error(f"Error adding partitions to {topic_name}: {e}")
            return False
    
    def get_consumer_groups(self) -> List[str]:
        """List all consumer groups.
        
        Returns:
            List of consumer group IDs
        """
        try:
            groups = self.admin_client.list_consumer_groups(timeout=10)
            group_ids = [group.group_id for group in groups.valid]
            logger.info(f"Found {len(group_ids)} consumer groups")
            return group_ids
        except Exception as e:
            logger.error(f"Error listing consumer groups: {e}")
            return []
    
    def delete_consumer_group(self, group_id: str) -> bool:
        """Delete a consumer group.
        
        Args:
            group_id: Consumer group ID
        
        Returns:
            True if successful, False otherwise
        """
        try:
            future = self.admin_client.delete_consumer_groups([group_id])
            
            for group, future_result in future.items():
                try:
                    future_result.result()
                    logger.info(f"Consumer group {group} deleted successfully")
                    return True
                except KafkaException as e:
                    logger.error(f"Failed to delete consumer group {group}: {e}")
                    return False
        
        except Exception as e:
            logger.error(f"Error deleting consumer group {group_id}: {e}")
            return False


def create_banking_topics(config: StreamingConfig) -> Dict[str, bool]:
    """Create standard banking analytics topics.
    
    Args:
        config: Streaming configuration
    
    Returns:
        Dictionary mapping topic name to success status
    """
    manager = TopicManager(config)
    
    # Define banking-specific topics with appropriate configurations
    topic_configs = [
        # Transaction events - high throughput, short retention
        TopicConfig(
            name="transactions",
            num_partitions=6,
            replication_factor=2,
            retention_ms=7 * 24 * 60 * 60 * 1000,  # 7 days
            cleanup_policy="delete",
            compression_type="snappy"
        ),
        # Account updates - moderate throughput
        TopicConfig(
            name="account_updates",
            num_partitions=3,
            replication_factor=2,
            retention_ms=30 * 24 * 60 * 60 * 1000,  # 30 days
            cleanup_policy="delete",
            compression_type="snappy"
        ),
        # Customer updates - lower throughput
        TopicConfig(
            name="customer_updates",
            num_partitions=3,
            replication_factor=2,
            retention_ms=90 * 24 * 60 * 60 * 1000,  # 90 days
            cleanup_policy="delete",
            compression_type="snappy"
        ),
        # Loan applications - moderate throughput
        TopicConfig(
            name="loan_applications",
            num_partitions=3,
            replication_factor=2,
            retention_ms=365 * 24 * 60 * 60 * 1000,  # 1 year
            cleanup_policy="delete",
            compression_type="snappy"
        ),
        # Payments - moderate throughput
        TopicConfig(
            name="payments",
            num_partitions=3,
            replication_factor=2,
            retention_ms=365 * 24 * 60 * 60 * 1000,  # 1 year
            cleanup_policy="delete",
            compression_type="snappy"
        ),
        # Dead letter queue - longer retention
        TopicConfig(
            name="dlq",
            num_partitions=3,
            replication_factor=2,
            retention_ms=30 * 24 * 60 * 60 * 1000,  # 30 days
            cleanup_policy="delete",
            compression_type="snappy"
        ),
        # Anomaly events - for downstream processing
        TopicConfig(
            name="anomalies",
            num_partitions=3,
            replication_factor=2,
            retention_ms=90 * 24 * 60 * 60 * 1000,  # 90 days
            cleanup_policy="delete",
            compression_type="snappy"
        ),
        # Risk events - for downstream processing
        TopicConfig(
            name="risk_events",
            num_partitions=3,
            replication_factor=2,
            retention_ms=365 * 24 * 60 * 60 * 1000,  # 1 year
            cleanup_policy="delete",
            compression_type="snappy"
        ),
        # Alerts - for downstream processing
        TopicConfig(
            name="alerts",
            num_partitions=3,
            replication_factor=2,
            retention_ms=30 * 24 * 60 * 60 * 1000,  # 30 days
            cleanup_policy="delete",
            compression_type="snappy"
        ),
    ]
    
    return manager.create_topics(topic_configs)