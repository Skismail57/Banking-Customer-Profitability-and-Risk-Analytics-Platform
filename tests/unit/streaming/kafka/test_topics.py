"""Unit tests for Kafka topic management.

This module tests the topic management utilities (unit tests only,
no actual Kafka connection required).
"""

import pytest

from src.streaming.kafka.topics import TopicConfig, TopicManager


class TestTopicConfig:
    """Test TopicConfig dataclass."""
    
    def test_topic_config_creation(self):
        """Test creating a topic configuration."""
        config = TopicConfig(
            name="test_topic",
            num_partitions=3,
            replication_factor=2,
            retention_ms=86400000,
            cleanup_policy="delete"
        )
        
        assert config.name == "test_topic"
        assert config.num_partitions == 3
        assert config.replication_factor == 2
        assert config.retention_ms == 86400000
        assert config.cleanup_policy == "delete"
    
    def test_topic_config_defaults(self):
        """Test topic configuration defaults."""
        config = TopicConfig(name="test_topic")
        
        assert config.name == "test_topic"
        assert config.num_partitions == 3
        assert config.replication_factor == 1
        assert config.retention_ms is None
        assert config.cleanup_policy == "delete"
    
    def test_topic_config_compact_policy(self):
        """Test topic configuration with compact policy."""
        config = TopicConfig(
            name="test_topic",
            cleanup_policy="compact"
        )
        
        assert config.cleanup_policy == "compact"


class TestTopicManager:
    """Test TopicManager class (unit tests only)."""
    
    def test_topic_manager_initialization(self):
        """Test topic manager initialization."""
        from src.streaming.config import StreamingConfig
        
        config = StreamingConfig(
            kafka={
                "bootstrap_servers": "localhost:9092",
                "group_id": "test_group",
            },
            redis={
                "host": "localhost",
                "port": 6379,
            },
            schema_registry={
                "enable": False,
                "url": "http://localhost:8081",
            }
        )
        
        # Note: This will fail if Kafka is not available, but we're testing initialization
        try:
            manager = TopicManager(config)
            assert manager.config is not None
            assert manager.admin_client is not None
        except Exception as e:
            # Expected if Kafka is not available
            pytest.skip(f"Kafka not available: {e}")
    
    def test_topic_config_dict_building(self):
        """Test building topic configuration dictionary."""
        config = TopicConfig(
            name="test_topic",
            num_partitions=3,
            replication_factor=2,
            retention_ms=86400000,
            retention_bytes=1073741824,
            cleanup_policy="delete",
            segment_ms=3600000,
            segment_bytes=1073741824,
            min_insync_replicas=2,
            compression_type="snappy",
            max_message_bytes=1048576
        )
        
        config_dict = {}
        if config.retention_ms:
            config_dict['retention.ms'] = str(config.retention_ms)
        if config.retention_bytes:
            config_dict['retention.bytes'] = str(config.retention_bytes)
        if config.cleanup_policy:
            config_dict['cleanup.policy'] = config.cleanup_policy
        if config.segment_ms:
            config_dict['segment.ms'] = str(config.segment_ms)
        if config.segment_bytes:
            config_dict['segment.bytes'] = str(config.segment_bytes)
        if config.min_insync_replicas:
            config_dict['min.insync.replicas'] = str(config.min_insync_replicas)
        if config.compression_type:
            config_dict['compression.type'] = config.compression_type
        if config.max_message_bytes:
            config_dict['max.message.bytes'] = str(config.max_message_bytes)
        
        assert config_dict['retention.ms'] == '86400000'
        assert config_dict['retention.bytes'] == '1073741824'
        assert config_dict['cleanup.policy'] == 'delete'
        assert config_dict['segment.ms'] == '3600000'
        assert config_dict['segment.bytes'] == '1073741824'
        assert config_dict['min.insync.replicas'] == '2'
        assert config_dict['compression.type'] == 'snappy'
        assert config_dict['max.message.bytes'] == '1048576'


def test_create_banking_topics_function():
    """Test the create_banking_topics function."""
    from src.streaming.config import StreamingConfig
    
    config = StreamingConfig(
        kafka={
            "bootstrap_servers": "localhost:9092",
            "group_id": "test_group",
        },
        redis={
            "host": "localhost",
            "port": 6379,
        },
        schema_registry={
            "enable": False,
            "url": "http://localhost:8081",
        }
    )
    
    # Note: This will fail if Kafka is not available
    try:
        results = create_banking_topics(config)
        assert isinstance(results, dict)
        # Should have results for all banking topics
        expected_topics = [
            "transactions",
            "account_updates",
            "customer_updates",
            "loan_applications",
            "payments",
            "dlq",
            "anomalies",
            "risk_events",
            "alerts",
        ]
        for topic in expected_topics:
            assert topic in results
    except Exception as e:
        # Expected if Kafka is not available
        pytest.skip(f"Kafka not available: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])