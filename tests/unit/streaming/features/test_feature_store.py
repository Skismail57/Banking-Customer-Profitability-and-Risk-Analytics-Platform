"""Unit tests for Redis feature store.

This module tests the feature store functionality (requires Redis to be available).
"""

import pytest
from datetime import datetime

from src.streaming.features.feature_store import FeatureStore, FeatureVersion, FeatureSnapshot


class TestFeatureStore:
    """Test FeatureStore class."""
    
    @pytest.fixture
    def config(self):
        """Create streaming config for testing."""
        from src.streaming.config import StreamingConfig
        return StreamingConfig(
            kafka={
                "bootstrap_servers": "localhost:9092",
                "group_id": "test_group",
            },
            redis={
                "host": "localhost",
                "port": 6379,
                "db": 0,
            },
            schema_registry={
                "enable": False,
                "url": "http://localhost:8081",
            }
        )
    
    @pytest.fixture
    def feature_store(self, config):
        """Create a feature store for testing."""
        try:
            store = FeatureStore(config, default_ttl_seconds=3600)
            return store
        except Exception as e:
            pytest.skip(f"Redis not available: {e}")
    
    def test_store_and_get_feature(self, feature_store):
        """Test storing and retrieving a single feature."""
        entity_key = "cust_123"
        feature_name = "transaction_count"
        feature_value = 100
        
        # Store feature
        result = feature_store.store_feature(entity_key, feature_name, feature_value)
        assert result is True
        
        # Get feature
        retrieved = feature_store.get_feature(entity_key, feature_name)
        assert retrieved == "100"  # Stored as string
    
    def test_store_and_get_features(self, feature_store):
        """Test storing and retrieving multiple features."""
        entity_key = "cust_456"
        features = {
            "transaction_count": 50,
            "total_amount": 5000.50,
            "avg_amount": 100.01,
        }
        
        # Store features
        result = feature_store.store_features(entity_key, features)
        assert result is True
        
        # Get features
        retrieved = feature_store.get_features(entity_key)
        assert len(retrieved) == 3
        assert retrieved["transaction_count"] == "50"
        assert retrieved["total_amount"] == "5000.5"
    
    def test_store_complex_feature(self, feature_store):
        """Test storing a complex (dict/list) feature."""
        entity_key = "cust_789"
        feature_name = "transaction_history"
        feature_value = {
            "last_5_transactions": [100, 200, 150, 300, 50],
            "merchants": ["amazon", "walmart", "target"],
        }
        
        # Store feature
        result = feature_store.store_feature(entity_key, feature_name, feature_value)
        assert result is True
        
        # Get feature
        retrieved = feature_store.get_feature(entity_key, feature_name)
        assert isinstance(retrieved, dict)
        assert "last_5_transactions" in retrieved
        assert "merchants" in retrieved
    
    def test_delete_feature(self, feature_store):
        """Test deleting a feature."""
        entity_key = "cust_999"
        feature_name = "temp_feature"
        
        # Store feature
        feature_store.store_feature(entity_key, feature_name, 100)
        
        # Delete feature
        result = feature_store.delete_feature(entity_key, feature_name)
        assert result is True
        
        # Verify deletion
        retrieved = feature_store.get_feature(entity_key, feature_name)
        assert retrieved is None
    
    def test_delete_features(self, feature_store):
        """Test deleting all features for an entity."""
        entity_key = "cust_888"
        features = {"f1": 1, "f2": 2, "f3": 3}
        
        # Store features
        feature_store.store_features(entity_key, features)
        
        # Delete all features
        deleted_count = feature_store.delete_features(entity_key)
        assert deleted_count == 3
        
        # Verify deletion
        retrieved = feature_store.get_features(entity_key)
        assert len(retrieved) == 0
    
    def test_create_and_get_snapshot(self, feature_store):
        """Test creating and retrieving a snapshot."""
        entity_key = "cust_777"
        features = {"score": 0.85, "risk": "low"}
        feature_version = "v1"
        event_timestamp = datetime.utcnow()
        
        # Create snapshot
        snapshot_id = feature_store.create_snapshot(
            entity_key=entity_key,
            features=features,
            feature_version=feature_version,
            event_timestamp=event_timestamp
        )
        
        assert snapshot_id is not None
        assert "snapshot_" in snapshot_id
        
        # Get snapshot
        snapshot = feature_store.get_snapshot(snapshot_id)
        assert snapshot is not None
        assert snapshot.entity_key == entity_key
        assert snapshot.feature_version == feature_version
        assert snapshot.features == features
    
    def test_register_and_get_feature_version(self, feature_store):
        """Test registering and retrieving a feature version."""
        version = "v2"
        feature_schema = {
            "feature1": "float",
            "feature2": "int",
            "feature3": "str",
        }
        description = "Test feature version"
        
        # Register version
        result = feature_store.register_feature_version(
            version=version,
            feature_schema=feature_schema,
            description=description
        )
        assert result is True
        
        # Get version
        feature_version = feature_store.get_feature_version(version)
        assert feature_version is not None
        assert feature_version.version == version
        assert feature_version.feature_schema == feature_schema
        assert feature_version.description == description
    
    def test_list_feature_versions(self, feature_store):
        """Test listing feature versions."""
        # Register multiple versions
        feature_store.register_feature_version("v1", {"f1": "float"})
        feature_store.register_feature_version("v2", {"f2": "int"})
        feature_store.register_feature_version("v3", {"f3": "str"})
        
        # List versions
        versions = feature_store.list_feature_versions()
        assert len(versions) >= 3
        assert "v1" in versions
        assert "v2" in versions
        assert "v3" in versions
    
    def test_get_metrics(self, feature_store):
        """Test getting metrics."""
        # Perform some operations
        feature_store.store_feature("cust_1", "f1", 100)
        feature_store.get_feature("cust_1", "f1")
        
        metrics = feature_store.get_metrics()
        assert "features_stored" in metrics
        assert "features_retrieved" in metrics
        assert metrics["features_stored"] >= 1
        assert metrics["features_retrieved"] >= 1
    
    def test_health_check(self, feature_store):
        """Test health check."""
        is_healthy = feature_store.health_check()
        assert isinstance(is_healthy, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])