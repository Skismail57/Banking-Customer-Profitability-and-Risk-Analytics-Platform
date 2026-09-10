"""Consumer group management utilities for Kafka.

This module provides utilities for managing Kafka consumer groups including
lag monitoring, offset management, and group administration.
"""

import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

from confluent_kafka import AdminClient, KafkaException, ConsumerGroupTopicPartitions

from src.streaming.config import StreamingConfig

logger = logging.getLogger(__name__)


@dataclass
class ConsumerGroupInfo:
    """Information about a consumer group."""
    group_id: str
    state: str
    protocol: str
    protocol_type: str
    members: List[Dict[str, Any]]
    assignments: Dict[str, List[int]]


@dataclass
class PartitionLag:
    """Lag information for a partition."""
    topic: str
    partition: int
    current_offset: int
    log_end_offset: int
    lag: int
    consumer_id: Optional[str] = None
    client_id: Optional[str] = None
    host: Optional[str] = None


@dataclass
class ConsumerGroupLag:
    """Lag information for a consumer group."""
    group_id: str
    total_lag: int
    partition_lags: List[PartitionLag]


class ConsumerGroupManager:
    """Manage Kafka consumer groups."""
    
    def __init__(self, config: StreamingConfig):
        """Initialize consumer group manager.
        
        Args:
            config: Streaming configuration
        """
        self.config = config
        
        # Build admin client configuration
        admin_config = {
            'bootstrap.servers': config.kafka.bootstrap_servers,
            'client.id': config.kafka.client_id or 'banking-analytics-cg-manager',
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
        
        logger.info(f"Consumer group manager initialized with bootstrap servers: {config.kafka.bootstrap_servers}")
    
    def list_consumer_groups(self) -> List[str]:
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
    
    def describe_consumer_group(self, group_id: str) -> Optional[ConsumerGroupInfo]:
        """Describe a consumer group.
        
        Args:
            group_id: Consumer group ID
        
        Returns:
            ConsumerGroupInfo or None if not found
        """
        try:
            future = self.admin_client.describe_consumer_groups([group_id])
            
            for group, future_result in future.items():
                try:
                    group_info = future_result.result()
                    
                    members = []
                    assignments = {}
                    
                    for member in group_info.members:
                        member_info = {
                            'id': member.member_id,
                            'client_id': member.client_id,
                            'host': member.client_host,
                        }
                        members.append(member_info)
                        
                        # Extract assignments
                        for topic, partitions in member.member_assignment.topic_partitions.items():
                            if topic not in assignments:
                                assignments[topic] = []
                            assignments[topic].extend(partitions)
                    
                    return ConsumerGroupInfo(
                        group_id=group_info.group_id,
                        state=group_info.state,
                        protocol=group_info.protocol,
                        protocol_type=group_info.protocol_type,
                        members=members,
                        assignments=assignments
                    )
                
                except KafkaException as e:
                    logger.error(f"Failed to describe consumer group {group}: {e}")
                    return None
        
        except Exception as e:
            logger.error(f"Error describing consumer group {group_id}: {e}")
            return None
    
    def get_consumer_group_lag(
        self,
        group_id: str,
        topics: Optional[List[str]] = None
    ) -> Optional[ConsumerGroupLag]:
        """Get consumer group lag.
        
        Args:
            group_id: Consumer group ID
            topics: Optional list of topics to check (if None, checks all topics)
        
        Returns:
            ConsumerGroupLag or None if error
        """
        try:
            # Get consumer group offsets
            future_offsets = self.admin_client.list_consumer_group_offsets(group_id, timeout=10)
            offsets = future_offsets.result()
            
            # Get cluster metadata for log end offsets
            cluster_metadata = self.admin_client.list_topics(timeout=10)
            
            partition_lags = []
            total_lag = 0
            
            for topic, partitions in offsets.topic_partitions.items():
                if topics and topic not in topics:
                    continue
                
                if topic not in cluster_metadata.topics:
                    logger.warning(f"Topic {topic} not found in cluster metadata")
                    continue
                
                for partition, metadata in partitions.items():
                    try:
                        # Get log end offset
                        topic_metadata = cluster_metadata.topics[topic]
                        if partition not in topic_metadata.partitions:
                            continue
                        
                        partition_metadata = topic_metadata.partitions[partition]
                        log_end_offset = partition_metadata.end_offset if hasattr(partition_metadata, 'end_offset') else 0
                        
                        # Get current offset
                        current_offset = metadata.offset if metadata.offset != -1 else 0
                        
                        # Calculate lag
                        lag = log_end_offset - current_offset
                        total_lag += lag
                        
                        partition_lags.append(PartitionLag(
                            topic=topic,
                            partition=partition,
                            current_offset=current_offset,
                            log_end_offset=log_end_offset,
                            lag=lag,
                            consumer_id=metadata.consumer_id if hasattr(metadata, 'consumer_id') else None,
                            client_id=metadata.client_id if hasattr(metadata, 'client_id') else None,
                            host=metadata.host if hasattr(metadata, 'host') else None,
                        ))
                    
                    except Exception as e:
                        logger.error(f"Error calculating lag for {topic}[{partition}]: {e}")
                        continue
            
            return ConsumerGroupLag(
                group_id=group_id,
                total_lag=total_lag,
                partition_lags=partition_lags
            )
        
        except Exception as e:
            logger.error(f"Error getting consumer group lag for {group_id}: {e}")
            return None
    
    def reset_consumer_group_offset(
        self,
        group_id: str,
        topic: str,
        partition: int,
        offset: int
    ) -> bool:
        """Reset consumer group offset for a specific partition.
        
        Args:
            group_id: Consumer group ID
            topic: Topic name
            partition: Partition number
            offset: New offset
        
        Returns:
            True if successful, False otherwise
        """
        try:
            from confluent_kafka import TopicPartition
            
            tp = TopicPartition(topic, partition, offset)
            future = self.admin_client.alter_consumer_group_offsets(
                group_id,
                {tp: offset}
            )
            
            for _, future_result in future.items():
                try:
                    future_result.result()
                    logger.info(f"Reset offset for {group_id} {topic}[{partition}] to {offset}")
                    return True
                except KafkaException as e:
                    logger.error(f"Failed to reset offset: {e}")
                    return False
        
        except Exception as e:
            logger.error(f"Error resetting consumer group offset: {e}")
            return False
    
    def reset_consumer_group_to_earliest(
        self,
        group_id: str,
        topics: Optional[List[str]] = None
    ) -> bool:
        """Reset consumer group offsets to earliest for topics.
        
        Args:
            group_id: Consumer group ID
            topics: Optional list of topics (if None, resets all topics)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            from confluent_kafka import TopicPartition
            
            # Get current assignments
            future_offsets = self.admin_client.list_consumer_group_offsets(group_id, timeout=10)
            offsets = future_offsets.result()
            
            # Get watermark offsets
            tps_to_reset = []
            for topic, partitions in offsets.topic_partitions.items():
                if topics and topic not in topics:
                    continue
                
                for partition, _ in partitions.items():
                    tp = TopicPartition(topic, partition)
                    low, _ = self.admin_client.get_watermark_offsets(tp)
                    tps_to_reset.append((TopicPartition(topic, partition, low), low))
            
            # Reset offsets
            offsets_dict = {tp: offset for tp, offset in tps_to_reset}
            future = self.admin_client.alter_consumer_group_offsets(group_id, offsets_dict)
            
            for _, future_result in future.items():
                try:
                    future_result.result()
                    logger.info(f"Reset {group_id} to earliest for {len(offsets_dict)} partitions")
                    return True
                except KafkaException as e:
                    logger.error(f"Failed to reset to earliest: {e}")
                    return False
        
        except Exception as e:
            logger.error(f"Error resetting consumer group to earliest: {e}")
            return False
    
    def reset_consumer_group_to_latest(
        self,
        group_id: str,
        topics: Optional[List[str]] = None
    ) -> bool:
        """Reset consumer group offsets to latest for topics.
        
        Args:
            group_id: Consumer group ID
            topics: Optional list of topics (if None, resets all topics)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            from confluent_kafka import TopicPartition
            
            # Get current assignments
            future_offsets = self.admin_client.list_consumer_group_offsets(group_id, timeout=10)
            offsets = future_offsets.result()
            
            # Get watermark offsets
            tps_to_reset = []
            for topic, partitions in offsets.topic_partitions.items():
                if topics and topic not in topics:
                    continue
                
                for partition, _ in partitions.items():
                    tp = TopicPartition(topic, partition)
                    _, high = self.admin_client.get_watermark_offsets(tp)
                    tps_to_reset.append((TopicPartition(topic, partition, high), high))
            
            # Reset offsets
            offsets_dict = {tp: offset for tp, offset in tps_to_reset}
            future = self.admin_client.alter_consumer_group_offsets(group_id, offsets_dict)
            
            for _, future_result in future.items():
                try:
                    future_result.result()
                    logger.info(f"Reset {group_id} to latest for {len(offsets_dict)} partitions")
                    return True
                except KafkaException as e:
                    logger.error(f"Failed to reset to latest: {e}")
                    return False
        
        except Exception as e:
            logger.error(f"Error resetting consumer group to latest: {e}")
            return False
    
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
    
    def get_consumer_group_summary(self, group_id: str) -> Optional[Dict[str, Any]]:
        """Get summary information for a consumer group.
        
        Args:
            group_id: Consumer group ID
        
        Returns:
            Dictionary with summary information or None
        """
        try:
            # Get group info
            group_info = self.describe_consumer_group(group_id)
            if not group_info:
                return None
            
            # Get lag info
            lag_info = self.get_consumer_group_lag(group_id)
            
            return {
                'group_id': group_info.group_id,
                'state': group_info.state,
                'protocol': group_info.protocol,
                'member_count': len(group_info.members),
                'topic_count': len(group_info.assignments),
                'total_lag': lag_info.total_lag if lag_info else 0,
                'assignments': group_info.assignments,
            }
        
        except Exception as e:
            logger.error(f"Error getting consumer group summary for {group_id}: {e}")
            return None


def check_all_consumer_groups_lag(config: StreamingConfig) -> Dict[str, Dict[str, Any]]:
    """Check lag for all consumer groups.
    
    Args:
        config: Streaming configuration
    
    Returns:
        Dictionary mapping group_id to lag information
    """
    manager = ConsumerGroupManager(config)
    group_ids = manager.list_consumer_groups()
    
    results = {}
    for group_id in group_ids:
        lag_info = manager.get_consumer_group_lag(group_id)
        if lag_info:
            results[group_id] = {
                'total_lag': lag_info.total_lag,
                'partition_count': len(lag_info.partition_lags),
                'high_lag_partitions': [p for p in lag_info.partition_lags if p.lag > 10000],
            }
    
    return results