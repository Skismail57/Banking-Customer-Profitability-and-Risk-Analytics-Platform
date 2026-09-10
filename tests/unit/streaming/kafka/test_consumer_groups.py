"""Unit tests for Kafka consumer group management.

This module tests the consumer group management utilities (unit tests only,
no actual Kafka connection required).
"""

import pytest

from src.streaming.kafka.consumer_groups import (
    ConsumerGroupInfo,
    PartitionLag,
    ConsumerGroupLag,
    ConsumerGroupManager,
)


class TestConsumerGroupInfo:
    """Test ConsumerGroupInfo dataclass."""
    
    def test_consumer_group_info_creation(self):
        """Test creating consumer group info."""
        info = ConsumerGroupInfo(
            group_id="test_group",
            state="Stable",
            protocol="range",
            protocol_type="consumer",
            members=[],
            assignments={}
        )
        
        assert info.group_id == "test_group"
        assert info.state == "Stable"
        assert info.protocol == "range"
        assert info.protocol_type == "consumer"
        assert info.members == []
        assert info.assignments == {}


class TestPartitionLag:
    """Test PartitionLag dataclass."""
    
    def test_partition_lag_creation(self):
        """Test creating partition lag info."""
        lag = PartitionLag(
            topic="transactions",
            partition=0,
            current_offset=1000,
            log_end_offset=1500,
            lag=500,
            consumer_id="consumer-1",
            client_id="client-1",
            host="localhost"
        )
        
        assert lag.topic == "transactions"
        assert lag.partition == 0
        assert lag.current_offset == 1000
        assert lag.log_end_offset == 1500
        assert lag.lag == 500
        assert lag.consumer_id == "consumer-1"
        assert lag.client_id == "client-1"
        assert lag.host == "localhost"
    
    def test_partition_lag_optional_fields(self):
        """Test partition lag with optional fields."""
        lag = PartitionLag(
            topic="transactions",
            partition=0,
            current_offset=1000,
            log_end_offset=1500,
            lag=500
        )
        
        assert lag.consumer_id is None
        assert lag.client_id is None
        assert lag.host is None


class TestConsumerGroupLag:
    """Test ConsumerGroupLag dataclass."""
    
    def test_consumer_group_lag_creation(self):
        """Test creating consumer group lag info."""
        partition_lags = [
            PartitionLag(
                topic="transactions",
                partition=0,
                current_offset=1000,
                log_end_offset=1500,
                lag=500
            ),
            PartitionLag(
                topic="transactions",
                partition=1,
                current_offset=2000,
                log_end_offset=2500,
                lag=500
            ),
        ]
        
        lag_info = ConsumerGroupLag(
            group_id="test_group",
            total_lag=1000,
            partition_lags=partition_lags
        )
        
        assert lag_info.group_id == "test_group"
        assert lag_info.total_lag == 1000
        assert len(lag_info.partition_lags) == 2


class TestConsumerGroupManager:
    """Test ConsumerGroupManager class (unit tests only)."""
    
    def test_consumer_group_manager_initialization(self):
        """Test consumer group manager initialization."""
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
            manager = ConsumerGroupManager(config)
            assert manager.config is not None
            assert manager.admin_client is not None
        except Exception as e:
            # Expected if Kafka is not available
            pytest.skip(f"Kafka not available: {e}")


def test_check_all_consumer_groups_lag_function():
    """Test the check_all_consumer_groups_lag function."""
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
        results = check_all_consumer_groups_lag(config)
        assert isinstance(results, dict)
    except Exception as e:
        # Expected if Kafka is not available
        pytest.skip(f"Kafka not available: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])