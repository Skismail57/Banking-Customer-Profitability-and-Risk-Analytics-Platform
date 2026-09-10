"""Redis feature store for real-time feature serving.

This module provides a Redis-based feature store for storing and retrieving
features for real-time analytics and ML predictions with reliability patterns.
"""

import logging
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import redis

from src.streaming.config import StreamingConfig
from src.streaming.reliability import RetryConfig, retry_with_backoff

logger = logging.getLogger(__name__)


@dataclass
class FeatureVersion:
    """Feature version information."""
    version: str
    created_at: datetime
    feature_schema: Dict[str, Any]
    description: Optional[str] = None


@dataclass
class FeatureSnapshot:
    """Feature snapshot for audit and replay."""
    snapshot_id: str
    entity_key: str
    feature_version: str
    features: Dict[str, Any]
    event_timestamp: datetime
    snapshot_timestamp: datetime


class FeatureStore:
    """Redis-based feature store for real-time feature serving."""
    
    def __init__(
        self,
        config: StreamingConfig,
        default_ttl_seconds: int = 3600,  # 1 hour default
        key_prefix: str = "features"
    ):
        """Initialize feature store.
        
        Args:
            config: Streaming configuration
            default_ttl_seconds: Default TTL for features in seconds
            key_prefix: Prefix for Redis keys
        """
        self.config = config
        self.default_ttl_seconds = default_ttl_seconds
        self.key_prefix = key_prefix
        
        # Create Redis client
        self.redis_client = redis.Redis(
            host=config.redis.host,
            port=config.redis.port,
            db=config.redis.db,
            password=config.redis.password,
            decode_responses=True
        )
        
        # Metrics
        self.metrics = {
            'features_stored': 0,
            'features_retrieved': 0,
            'features_deleted': 0,
            'snapshots_created': 0,
            'snapshots_retrieved': 0,
        }
        
        logger.info(f"Feature store initialized with Redis at {config.redis.host}:{config.redis.port}")
    
    def _build_key(self, entity_key: str, feature_name: Optional[str] = None) -> str:
        """Build Redis key for feature.
        
        Args:
            entity_key: Entity key (e.g., customer_key)
            feature_name: Optional feature name
        
        Returns:
            Redis key
        """
        if feature_name:
            return f"{self.key_prefix}:{entity_key}:{feature_name}"
        return f"{self.key_prefix}:{entity_key}"
    
    @retry_with_backoff(RetryConfig(max_attempts=3, base_delay=0.5, max_delay=5.0))
    def store_feature(
        self,
        entity_key: str,
        feature_name: str,
        feature_value: Any,
        ttl_seconds: Optional[int] = None
    ) -> bool:
        """Store a single feature value.
        
        Args:
            entity_key: Entity key (e.g., customer_key)
            feature_name: Feature name
            feature_value: Feature value
            ttl_seconds: TTL in seconds (uses default if None)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            key = self._build_key(entity_key, feature_name)
            ttl = ttl_seconds or self.default_ttl_seconds
            
            # Serialize value if it's not a primitive type
            if isinstance(feature_value, (dict, list)):
                value = json.dumps(feature_value)
            else:
                value = str(feature_value)
            
            self.redis_client.setex(key, ttl, value)
            self.metrics['features_stored'] += 1
            
            logger.debug(f"Stored feature {feature_name} for {entity_key}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to store feature {feature_name} for {entity_key}: {e}")
            return False
    
    @retry_with_backoff(RetryConfig(max_attempts=3, base_delay=0.5, max_delay=5.0))
    def store_features(
        self,
        entity_key: str,
        features: Dict[str, Any],
        ttl_seconds: Optional[int] = None
    ) -> bool:
        """Store multiple features for an entity.
        
        Args:
            entity_key: Entity key (e.g., customer_key)
            features: Dictionary of feature names to values
            ttl_seconds: TTL in seconds (uses default if None)
        
        Returns:
            True if all successful, False otherwise
        """
        try:
            ttl = ttl_seconds or self.default_ttl_seconds
            
            for feature_name, feature_value in features.items():
                key = self._build_key(entity_key, feature_name)
                
                # Serialize value if it's not a primitive type
                if isinstance(feature_value, (dict, list)):
                    value = json.dumps(feature_value)
                else:
                    value = str(feature_value)
                
                self.redis_client.setex(key, ttl, value)
                self.metrics['features_stored'] += 1
            
            logger.debug(f"Stored {len(features)} features for {entity_key}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to store features for {entity_key}: {e}")
            return False
    
    @retry_with_backoff(RetryConfig(max_attempts=3, base_delay=0.3, max_delay=3.0))
    def get_feature(
        self,
        entity_key: str,
        feature_name: str
    ) -> Optional[Any]:
        """Get a single feature value.
        
        Args:
            entity_key: Entity key (e.g., customer_key)
            feature_name: Feature name
        
        Returns:
            Feature value or None if not found
        """
        try:
            key = self._build_key(entity_key, feature_name)
            value = self.redis_client.get(key)
            
            if value is None:
                return None
            
            self.metrics['features_retrieved'] += 1
            
            # Try to deserialize JSON
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                # Return as string if not JSON
                return value
        
        except Exception as e:
            logger.error(f"Failed to get feature {feature_name} for {entity_key}: {e}")
        
        return None
    
    @retry_with_backoff(RetryConfig(max_attempts=3, base_delay=0.3, max_delay=3.0))
    def get_features(
        self,
        entity_key: str,
        feature_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get multiple features for an entity.
        
        Args:
            entity_key: Entity key (e.g., customer_key)
            feature_names: Optional list of feature names (gets all if None)
        
        Returns:
            Dictionary of feature names to values
        """
        try:
            if feature_names:
                # Get specific features
                keys = [self._build_key(entity_key, name) for name in feature_names]
                values = self.redis_client.mget(keys)
                
                features = {}
                for name, value in zip(feature_names, values):
                    if value is not None:
                        try:
                            features[name] = json.loads(value)
                        except json.JSONDecodeError:
                            features[name] = value
                        self.metrics['features_retrieved'] += 1
                
                return features
            else:
                # Get all features for entity
                pattern = self._build_key(entity_key, "*")
                keys = self.redis_client.keys(pattern)
                
                features = {}
                for key in keys:
                    value = self.redis_client.get(key)
                    if value is not None:
                        # Extract feature name from key
                        feature_name = key.split(":")[-1]
                        try:
                            features[feature_name] = json.loads(value)
                        except json.JSONDecodeError:
                            features[feature_name] = value
                        self.metrics['features_retrieved'] += 1
                
                return features
        
        except Exception as e:
            logger.error(f"Failed to get features for {entity_key}: {e}")
            return {}
    
    def delete_feature(
        self,
        entity_key: str,
        feature_name: str
    ) -> bool:
        """Delete a single feature.
        
        Args:
            entity_key: Entity key (e.g., customer_key)
            feature_name: Feature name
        
        Returns:
            True if successful, False otherwise
        """
        try:
            key = self._build_key(entity_key, feature_name)
            result = self.redis_client.delete(key)
            
            if result > 0:
                self.metrics['features_deleted'] += 1
                logger.debug(f"Deleted feature {feature_name} for {entity_key}")
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Failed to delete feature {feature_name} for {entity_key}: {e}")
            return False
    
    def delete_features(
        self,
        entity_key: str
    ) -> int:
        """Delete all features for an entity.
        
        Args:
            entity_key: Entity key (e.g., customer_key)
        
        Returns:
            Number of features deleted
        """
        try:
            pattern = self._build_key(entity_key, "*")
            keys = self.redis_client.keys(pattern)
            
            if keys:
                deleted = self.redis_client.delete(*keys)
                self.metrics['features_deleted'] += deleted
                logger.debug(f"Deleted {deleted} features for {entity_key}")
                return deleted
            
            return 0
        
        except Exception as e:
            logger.error(f"Failed to delete features for {entity_key}: {e}")
            return 0
    
    def create_snapshot(
        self,
        entity_key: str,
        features: Dict[str, Any],
        feature_version: str,
        event_timestamp: datetime
    ) -> str:
        """Create a feature snapshot for audit/replay.
        
        Args:
            entity_key: Entity key
            features: Feature values
            feature_version: Feature version
            event_timestamp: Event timestamp
        
        Returns:
            Snapshot ID
        """
        snapshot_id = f"snapshot_{entity_key}_{datetime.utcnow().isoformat()}"
        
        snapshot = FeatureSnapshot(
            snapshot_id=snapshot_id,
            entity_key=entity_key,
            feature_version=feature_version,
            features=features,
            event_timestamp=event_timestamp,
            snapshot_timestamp=datetime.utcnow()
        )
        
        # Store snapshot in Redis
        snapshot_key = f"{self.key_prefix}:snapshots:{snapshot_id}"
        snapshot_data = json.dumps(asdict(snapshot), default=str)
        
        # Store with longer TTL (e.g., 7 days for audit)
        self.redis_client.setex(snapshot_key, 7 * 24 * 3600, snapshot_data)
        
        self.metrics['snapshots_created'] += 1
        logger.info(f"Created snapshot {snapshot_id} for {entity_key}")
        
        return snapshot_id
    
    def get_snapshot(self, snapshot_id: str) -> Optional[FeatureSnapshot]:
        """Get a feature snapshot.
        
        Args:
            snapshot_id: Snapshot ID
        
        Returns:
            FeatureSnapshot or None if not found
        """
        try:
            snapshot_key = f"{self.key_prefix}:snapshots:{snapshot_id}"
            snapshot_data = self.redis_client.get(snapshot_key)
            
            if snapshot_data is None:
                return None
            
            data = json.loads(snapshot_data)
            snapshot = FeatureSnapshot(
                snapshot_id=data['snapshot_id'],
                entity_key=data['entity_key'],
                feature_version=data['feature_version'],
                features=data['features'],
                event_timestamp=datetime.fromisoformat(data['event_timestamp']),
                snapshot_timestamp=datetime.fromisoformat(data['snapshot_timestamp'])
            )
            
            self.metrics['snapshots_retrieved'] += 1
            return snapshot
        
        except Exception as e:
            logger.error(f"Failed to get snapshot {snapshot_id}: {e}")
            return None
    
    def register_feature_version(
        self,
        version: str,
        feature_schema: Dict[str, Any],
        description: Optional[str] = None
    ) -> bool:
        """Register a feature version.
        
        Args:
            version: Version string
            feature_schema: Feature schema (feature names and types)
            description: Optional description
        
        Returns:
            True if successful, False otherwise
        """
        try:
            feature_version = FeatureVersion(
                version=version,
                created_at=datetime.utcnow(),
                feature_schema=feature_schema,
                description=description
            )
            
            version_key = f"{self.key_prefix}:versions:{version}"
            version_data = json.dumps(asdict(feature_version), default=str)
            
            # Store version with no expiration
            self.redis_client.set(version_key, version_data)
            
            logger.info(f"Registered feature version {version}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to register feature version {version}: {e}")
            return False
    
    def get_feature_version(self, version: str) -> Optional[FeatureVersion]:
        """Get a feature version.
        
        Args:
            version: Version string
        
        Returns:
            FeatureVersion or None if not found
        """
        try:
            version_key = f"{self.key_prefix}:versions:{version}"
            version_data = self.redis_client.get(version_key)
            
            if version_data is None:
                return None
            
            data = json.loads(version_data)
            return FeatureVersion(
                version=data['version'],
                created_at=datetime.fromisoformat(data['created_at']),
                feature_schema=data['feature_schema'],
                description=data.get('description')
            )
        
        except Exception as e:
            logger.error(f"Failed to get feature version {version}: {e}")
            return None
    
    def list_feature_versions(self) -> List[str]:
        """List all registered feature versions.
        
        Returns:
            List of version strings
        """
        try:
            pattern = f"{self.key_prefix}:versions:*"
            keys = self.redis_client.keys(pattern)
            
            versions = [key.split(":")[-1] for key in keys]
            return versions
        
        except Exception as e:
            logger.error(f"Failed to list feature versions: {e}")
            return []
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get feature store metrics.
        
        Returns:
            Dictionary of metrics
        """
        return dict(self.metrics)
    
    @retry_with_backoff(RetryConfig(max_attempts=2, base_delay=0.2, max_delay=1.0))
    def health_check(self) -> bool:
        """Check if Redis is healthy.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            return self.redis_client.ping()
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False
    
    def close(self) -> None:
        """Close Redis connection."""
        self.redis_client.close()
        logger.info("Feature store closed")