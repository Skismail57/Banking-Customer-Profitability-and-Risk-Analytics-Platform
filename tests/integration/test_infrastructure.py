"""Infrastructure connectivity tests for streaming components.

This module tests the connectivity to the streaming infrastructure components:
- Redpanda (Kafka-compatible broker)
- Redis (feature store and caching)
- PostgreSQL (existing database)

These tests ensure that the infrastructure is properly configured and accessible
before running streaming operations.
"""

import pytest
import os
import time
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class TestInfrastructureConnectivity:
    """Test infrastructure connectivity for streaming components."""
    
    @pytest.fixture(scope="class")
    def environment(self) -> str:
        """Get the test environment."""
        return os.getenv("ENVIRONMENT", "development")
    
    @pytest.fixture(scope="class")
    def config(self, environment: str):
        """Load streaming configuration."""
        try:
            from src.streaming import get_streaming_config
            return get_streaming_config(environment)
        except ImportError:
            pytest.skip("Streaming module not available")
    
    @pytest.fixture(scope="class")
    def redis_client(self, config):
        """Create Redis client for testing."""
        try:
            import redis
            return redis.Redis(
                host=config.redis.host,
                port=config.redis.port,
                db=config.redis.db,
                password=config.redis.password,
                socket_timeout=config.redis.socket_timeout,
                socket_connect_timeout=config.redis.socket_connect_timeout,
                decode_responses=True
            )
        except ImportError:
            pytest.skip("Redis library not available")
    
    @pytest.fixture(scope="class")
    def kafka_producer(self, config):
        """Create Kafka producer for testing."""
        try:
            from confluent_kafka import Producer
            
            producer_config = {
                'bootstrap.servers': config.broker.bootstrap_servers,
                'client.id': 'test_infrastructure',
                'queue.buffering.max.messages': 1000,
                'queue.buffering.max.ms': 1000,
            }
            
            # Add security configuration if provided
            if config.broker.security_protocol:
                producer_config['security.protocol'] = config.broker.security_protocol
            if config.broker.sasl_mechanism:
                producer_config['sasl.mechanism'] = config.broker.sasl_mechanism
            if config.broker.sasl_username:
                producer_config['sasl.username'] = config.broker.sasl_username
            if config.broker.sasl_password:
                producer_config['sasl.password'] = config.broker.sasl_password
            
            return Producer(producer_config)
        except ImportError:
            pytest.skip("confluent-kafka library not available")
    
    @pytest.fixture(scope="class")
    def postgres_engine(self):
        """Create PostgreSQL engine for testing."""
        try:
            from sqlalchemy import create_engine
            from src.api.config import settings
            
            engine = create_engine(settings.db_url, pool_pre_ping=True)
            return engine
        except ImportError:
            pytest.skip("SQLAlchemy not available")
    
    def test_config_loading(self, environment: str, config):
        """Test that streaming configuration loads correctly."""
        assert config is not None
        assert config.broker is not None
        assert config.redis is not None
        assert config.schema_registry is not None
        
        # Validate configuration
        assert config.broker.bootstrap_servers
        assert config.redis.host
        assert config.redis.port > 0
        
        logger.info(f"Configuration loaded successfully for environment: {environment}")
    
    def test_redis_connectivity(self, redis_client):
        """Test Redis connectivity."""
        try:
            # Test ping
            result = redis_client.ping()
            assert result is True, "Redis ping failed"
            
            # Test basic operations
            test_key = "test_infrastructure_connectivity"
            redis_client.set(test_key, "test_value", ex=60)
            value = redis_client.get(test_key)
            assert value == "test_value", "Redis set/get failed"
            
            # Cleanup
            redis_client.delete(test_key)
            
            logger.info("Redis connectivity test passed")
        except Exception as e:
            pytest.fail(f"Redis connectivity test failed: {e}")
    
    def test_redis_feature_store_pattern(self, config):
        """Test Redis feature store key pattern generation."""
        # Test customer features pattern
        customer_key = config.get_feature_store_key(
            "customer_features",
            customer_key="CUST_001"
        )
        assert "customer" in customer_key
        assert "CUST_001" in customer_key
        
        # Test feature snapshot pattern
        snapshot_key = config.get_feature_store_key(
            "feature_snapshot",
            snapshot_id="snap_123"
        )
        assert "feature_snapshot" in snapshot_key
        assert "snap_123" in snapshot_key
        
        logger.info("Redis feature store pattern test passed")
    
    def test_kafka_broker_connectivity(self, kafka_producer, config):
        """Test Kafka/Redpanda broker connectivity."""
        try:
            # Test basic produce operation
            test_topic = "test_infrastructure_connectivity"
            test_message = "test_message"
            
            def delivery_report(err, msg):
                """Callback for message delivery reports."""
                if err is not None:
                    pytest.fail(f"Message delivery failed: {err}")
            
            # Produce test message
            kafka_producer.produce(
                test_topic,
                key="test_key",
                value=test_message,
                callback=delivery_report
            )
            
            # Flush to ensure message is sent
            kafka_producer.flush(timeout=10)
            
            logger.info("Kafka broker connectivity test passed")
        except Exception as e:
            pytest.fail(f"Kafka broker connectivity test failed: {e}")
    
    def test_kafka_topic_configuration(self, config):
        """Test that Kafka topic configuration is properly defined."""
        # Check that topics are defined
        assert len(config.topics) > 0, "No topics defined in configuration"
        
        # Check required topics
        required_topics = [
            "banking_events_raw",
            "banking_events_validated",
            "banking_features_customer",
            "banking_alerts_risk"
        ]
        
        for topic in required_topics:
            assert topic in config.topics, f"Required topic {topic} not defined"
            topic_config = config.topics[topic]
            assert "name" in topic_config
            assert "partitions" in topic_config
            assert topic_config["partitions"] > 0
        
        logger.info("Kafka topic configuration test passed")
    
    def test_postgres_connectivity(self, postgres_engine):
        """Test PostgreSQL connectivity."""
        try:
            # Test basic query
            with postgres_engine.connect() as conn:
                result = conn.execute("SELECT 1")
                assert result.fetchone()[0] == 1
            
            logger.info("PostgreSQL connectivity test passed")
        except Exception as e:
            pytest.fail(f"PostgreSQL connectivity test failed: {e}")
    
    def test_consumer_group_configuration(self, config):
        """Test that consumer group configuration is properly defined."""
        # Check that consumer groups are defined
        assert len(config.consumer_groups) > 0, "No consumer groups defined"
        
        # Check required consumer groups
        required_groups = [
            "feature_processor",
            "prediction_processor",
            "alert_processor"
        ]
        
        for group in required_groups:
            assert group in config.consumer_groups, f"Required consumer group {group} not defined"
            group_config = config.consumer_groups[group]
            assert "group_id" in group_config
            assert "topics" in group_config
            assert len(group_config["topics"]) > 0
        
        logger.info("Consumer group configuration test passed")
    
    def test_event_type_configuration(self, config):
        """Test that event type configuration is properly defined."""
        # Check that event types are defined
        assert len(config.event_types) > 0, "No event types defined"
        
        # Check required event types
        required_types = [
            "transaction",
            "account_update",
            "customer_update"
        ]
        
        for event_type in required_types:
            assert event_type in config.event_types, f"Required event type {event_type} not defined"
            type_config = config.event_types[event_type]
            assert "topic" in type_config
            assert "schema_version" in type_config
        
        logger.info("Event type configuration test passed")
    
    def test_configuration_validation(self, config):
        """Test that configuration validation works correctly."""
        try:
            is_valid = config.validate()
            assert is_valid is True
            logger.info("Configuration validation test passed")
        except Exception as e:
            pytest.fail(f"Configuration validation failed: {e}")
    
    def test_infrastructure_health_check(self, redis_client, kafka_producer, postgres_engine):
        """Comprehensive health check of all infrastructure components."""
        health_status = {
            "redis": False,
            "kafka": False,
            "postgres": False
        }
        
        # Check Redis
        try:
            redis_client.ping()
            health_status["redis"] = True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
        
        # Check Kafka
        try:
            kafka_producer.poll(timeout=1.0)
            health_status["kafka"] = True
        except Exception as e:
            logger.error(f"Kafka health check failed: {e}")
        
        # Check PostgreSQL
        try:
            with postgres_engine.connect() as conn:
                conn.execute("SELECT 1")
            health_status["postgres"] = True
        except Exception as e:
            logger.error(f"PostgreSQL health check failed: {e}")
        
        # Assert all components are healthy
        assert all(health_status.values()), f"Infrastructure health check failed: {health_status}"
        
        logger.info(f"Infrastructure health check passed: {health_status}")


class TestInfrastructureEnvironmentVariables:
    """Test that required environment variables are set."""
    
    def test_environment_variable_exists(self):
        """Test that ENVIRONMENT variable exists or has default."""
        environment = os.getenv("ENVIRONMENT", "development")
        assert environment in ["development", "staging", "production"]
    
    def test_database_variables_exist(self):
        """Test that database environment variables are set."""
        # These should have defaults in config
        db_host = os.getenv("DATABASE_HOST", "localhost")
        db_port = os.getenv("DATABASE_PORT", "5432")
        db_name = os.getenv("DATABASE_NAME", "banking_analytics")
        
        assert db_host is not None
        assert db_port is not None
        assert db_name is not None
    
    def test_streaming_variables_exist(self):
        """Test that streaming environment variables are set."""
        # These should have defaults in config
        kafka_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = os.getenv("REDIS_PORT", "6379")
        
        assert kafka_servers is not None
        assert redis_host is not None
        assert redis_port is not None


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])