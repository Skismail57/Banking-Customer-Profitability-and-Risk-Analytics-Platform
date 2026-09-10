"""Streaming configuration loader and management.

This module provides configuration management for the streaming infrastructure,
loading settings from YAML files and providing a clean interface for accessing
streaming-specific configuration.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class BrokerConfig:
    """Kafka/Redpanda broker configuration."""
    bootstrap_servers: str
    group_id: str
    auto_offset_reset: str = "earliest"
    enable_auto_commit: bool = False
    auto_commit_interval_ms: int = 5000
    session_timeout_ms: int = 30000
    heartbeat_interval_ms: int = 3000
    max_poll_records: int = 500
    max_poll_interval_ms: int = 300000
    fetch_min_bytes: int = 1
    fetch_max_wait_ms: int = 500
    client_id: Optional[str] = None
    security_protocol: Optional[str] = None
    sasl_mechanism: Optional[str] = None
    sasl_username: Optional[str] = None
    sasl_password: Optional[str] = None
    acks: str = "all"
    compression_type: str = "snappy"
    linger_ms: int = 0
    batch_size: int = 16384
    max_in_flight: int = 5
    enable_idempotence: bool = True
    message_timeout_ms: int = 30000
    queue_buffering_max_messages: int = 100000
    queue_buffering_max_kbytes: int = 1048576


@dataclass
class SchemaRegistryConfig:
    """Schema registry configuration."""
    url: str
    enable: bool = True
    api_key: Optional[str] = None
    api_secret: Optional[str] = None


@dataclass
class RedisConfig:
    """Redis configuration."""
    host: str
    port: int
    db: int = 0
    password: Optional[str] = None
    max_connections: int = 50
    socket_timeout: int = 5
    socket_connect_timeout: int = 5
    retry_on_timeout: bool = True
    ssl: bool = False


@dataclass
class FeatureStoreConfig:
    """Feature store configuration."""
    ttl_seconds: int = 86400
    snapshot_ttl_seconds: int = 220752000
    key_prefix: str = "banking"


@dataclass
class EventProcessingConfig:
    """Event processing configuration."""
    max_processing_time_seconds: int = 60
    idempotency_ttl_seconds: int = 86400
    late_event_window_seconds: int = 300
    watermark_delay_seconds: int = 60


@dataclass
class AlertConfig:
    """Alert configuration."""
    enabled: bool = True
    deduplication_window_seconds: int = 3600
    max_alerts_per_customer_per_hour: int = 10


@dataclass
class StreamingConfig:
    """Complete streaming configuration."""
    kafka: BrokerConfig
    schema_registry: SchemaRegistryConfig
    redis: RedisConfig
    feature_store: FeatureStoreConfig
    event_processing: EventProcessingConfig
    alerts: AlertConfig
    topics: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    consumer_groups: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    event_types: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    retry: Dict[str, Any] = field(default_factory=dict)
    dlq: Dict[str, Any] = field(default_factory=dict)
    watermark: Dict[str, Any] = field(default_factory=dict)
    feature_store_patterns: Dict[str, str] = field(default_factory=dict)
    monitoring: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load(cls, environment: str = "development") -> "StreamingConfig":
        """Load streaming configuration from YAML files.
        
        Args:
            environment: Environment name (development, production)
        
        Returns:
            StreamingConfig instance
        """
        # Determine base path
        base_path = Path(__file__).parent.parent.parent
        
        # Load base configuration
        base_config_path = base_path / "config" / "base.yaml"
        with open(base_config_path) as f:
            base_config = yaml.safe_load(f)
        
        # Load environment-specific configuration
        env_config_path = base_path / "config" / "environments" / f"{environment}.yaml"
        with open(env_config_path) as f:
            env_config = yaml.safe_load(f)
        
        # Load streaming-specific configuration
        streaming_config_path = base_path / "config" / "streaming.yaml"
        with open(streaming_config_path) as f:
            streaming_config = yaml.safe_load(f)
        
        # Merge configurations (env overrides base)
        streaming_settings = cls._deep_merge(
            base_config.get("streaming", {}),
            env_config.get("streaming", {})
        )
        
        # Add streaming-specific configurations
        streaming_settings["topics"] = streaming_config.get("topics", {})
        streaming_settings["consumer_groups"] = streaming_config.get("consumer_groups", {})
        streaming_settings["event_types"] = streaming_config.get("event_types", {})
        streaming_settings["retry"] = streaming_config.get("retry", {})
        streaming_settings["dlq"] = streaming_config.get("dlq", {})
        streaming_settings["watermark"] = streaming_config.get("watermark", {})
        streaming_settings["feature_store_patterns"] = streaming_config.get("feature_store", {}).get("key_patterns", {})
        streaming_settings["monitoring"] = streaming_config.get("monitoring", {})
        
        # Create configuration objects
        kafka_config = BrokerConfig(**streaming_settings.get("broker", {}))
        schema_registry_config = SchemaRegistryConfig(**streaming_settings.get("schema_registry", {}))
        redis_config = RedisConfig(**streaming_settings.get("redis", {}))
        feature_store_config = FeatureStoreConfig(**streaming_settings.get("feature_store", {}))
        event_processing_config = EventProcessingConfig(**streaming_settings.get("event_processing", {}))
        alert_config = AlertConfig(**streaming_settings.get("alerts", {}))
        
        return cls(
            kafka=kafka_config,
            schema_registry=schema_registry_config,
            redis=redis_config,
            feature_store=feature_store_config,
            event_processing=event_processing_config,
            alerts=alert_config,
            topics=streaming_settings.get("topics", {}),
            consumer_groups=streaming_settings.get("consumer_groups", {}),
            event_types=streaming_settings.get("event_types", {}),
            retry=streaming_settings.get("retry", {}),
            dlq=streaming_settings.get("dlq", {}),
            watermark=streaming_settings.get("watermark", {}),
            feature_store_patterns=streaming_settings.get("feature_store_patterns", {}),
            monitoring=streaming_settings.get("monitoring", {})
        )
    
    @staticmethod
    def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries.
        
        Args:
            base: Base dictionary
            override: Override dictionary
        
        Returns:
            Merged dictionary
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = StreamingConfig._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get_topic_config(self, topic_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific topic.
        
        Args:
            topic_name: Topic name
        
        Returns:
            Topic configuration or None if not found
        """
        return self.topics.get(topic_name)
    
    def get_consumer_group_config(self, group_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific consumer group.
        
        Args:
            group_name: Consumer group name
        
        Returns:
            Consumer group configuration or None if not found
        """
        return self.consumer_groups.get(group_name)
    
    def get_event_type_config(self, event_type: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific event type.
        
        Args:
            event_type: Event type
        
        Returns:
            Event type configuration or None if not found
        """
        return self.event_types.get(event_type)
    
    def get_feature_store_key(self, pattern_name: str, **kwargs) -> str:
        """Generate a feature store key using a pattern.
        
        Args:
            pattern_name: Name of the key pattern
            **kwargs: Values to substitute into the pattern
        
        Returns:
            Generated key
        """
        pattern = self.feature_store_patterns.get(pattern_name, "")
        return pattern.format(**kwargs)
    
    def validate(self) -> bool:
        """Validate the configuration.
        
        Returns:
            True if configuration is valid
        
        Raises:
            ValueError: If configuration is invalid
        """
        # Validate broker configuration
        if not self.broker.bootstrap_servers:
            raise ValueError("Broker bootstrap_servers is required")
        
        # Validate Redis configuration
        if not self.redis.host:
            raise ValueError("Redis host is required")
        
        # Validate schema registry if enabled
        if self.schema_registry.enable and not self.schema_registry.url:
            raise ValueError("Schema registry URL is required when enabled")
        
        logger.info("Streaming configuration validated successfully")
        return True


def get_streaming_config(environment: Optional[str] = None) -> StreamingConfig:
    """Get streaming configuration for the specified environment.
    
    Args:
        environment: Environment name (defaults to ENVIRONMENT env var or development)
    
    Returns:
        StreamingConfig instance
    """
    if environment is None:
        environment = os.getenv("ENVIRONMENT", "development")
    
    return StreamingConfig.load(environment)