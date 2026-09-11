"""Adapter for integrating streaming feature store with existing feature engineering.

This module provides an adapter that bridges the Redis feature store with the
existing batch feature engineering components, enabling feature parity between
batch and streaming pipelines.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone, timedelta

from src.streaming.features.feature_store import FeatureStore
from src.streaming.config import StreamingConfig

logger = logging.getLogger(__name__)


class FeatureStoreAdapter:
    """Adapter for integrating feature store with existing feature engineering.
    
    This adapter provides:
    - Storage of streaming features in Redis
    - Retrieval of features for real-time predictions
    - Feature versioning for batch-stream parity
    - Integration with existing feature engineering patterns
    """
    
    def __init__(
        self,
        config: StreamingConfig,
        feature_version: str = "v1",
        default_ttl_seconds: int = 3600
    ):
        """Initialize feature store adapter.
        
        Args:
            config: Streaming configuration
            feature_version: Current feature version
            default_ttl_seconds: Default TTL for features
        """
        self.config = config
        self.feature_version = feature_version
        self.default_ttl_seconds = default_ttl_seconds
        
        # Initialize feature store
        self.feature_store = FeatureStore(
            config=config,
            default_ttl_seconds=default_ttl_seconds
        )
        
        # Register feature version
        self._register_default_feature_version()
        
        logger.info(f"Feature store adapter initialized with version {feature_version}")
    
    def _register_default_feature_version(self) -> None:
        """Register default feature version schema."""
        # Define common banking feature schema
        feature_schema = {
            "transaction_features": {
                "transaction_count": "int",
                "total_amount": "float",
                "avg_amount": "float",
                "median_amount": "float",
                "std_amount": "float",
                "max_amount": "float",
                "min_amount": "float",
                "debit_count": "int",
                "credit_count": "int",
                "debit_total": "float",
                "credit_total": "float",
                "net_flow": "float",
                "daily_frequency": "float",
            },
            "account_features": {
                "current_balance": "float",
                "available_balance": "float",
                "credit_utilization": "float",
                "days_overdue": "int",
                "payment_history_score": "float",
            },
            "customer_features": {
                "account_age_days": "int",
                "total_accounts": "int",
                "customer_tenure_days": "int",
                "segment": "str",
                "risk_score": "float",
            },
        }
        
        self.feature_store.register_feature_version(
            version=self.feature_version,
            feature_schema=feature_schema,
            description="Default banking feature schema for streaming"
        )
    
    def store_transaction_features(
        self,
        customer_key: str,
        features: Dict[str, float],
        event_timestamp: Optional[datetime] = None,
        create_snapshot: bool = True
    ) -> Optional[str]:
        """Store transaction features for a customer.
        
        Args:
            customer_key: Customer key
            features: Transaction feature dictionary
            event_timestamp: Event timestamp
            create_snapshot: Whether to create a snapshot
        
        Returns:
            Snapshot ID if created, None otherwise
        """
        # Store features
        self.feature_store.store_features(
            entity_key=customer_key,
            features=features,
            ttl_seconds=self.default_ttl_seconds
        )
        
        # Create snapshot if requested
        snapshot_id = None
        if create_snapshot:
            snapshot_id = self.feature_store.create_snapshot(
                entity_key=customer_key,
                features=features,
                feature_version=self.feature_version,
                event_timestamp=event_timestamp or datetime.now(timezone.utc).replace(tzinfo=None)
            )
        
        return snapshot_id
    
    def store_account_features(
        self,
        customer_key: str,
        account_key: str,
        features: Dict[str, float],
        event_timestamp: Optional[datetime] = None,
        create_snapshot: bool = True
    ) -> Optional[str]:
        """Store account features for a customer.
        
        Args:
            customer_key: Customer key
            account_key: Account key
            features: Account feature dictionary
            event_timestamp: Event timestamp
            create_snapshot: Whether to create a snapshot
        
        Returns:
            Snapshot ID if created, None otherwise
        """
        # Store features with account-specific key
        entity_key = f"{customer_key}:{account_key}"
        
        self.feature_store.store_features(
            entity_key=entity_key,
            features=features,
            ttl_seconds=self.default_ttl_seconds
        )
        
        # Create snapshot if requested
        snapshot_id = None
        if create_snapshot:
            snapshot_id = self.feature_store.create_snapshot(
                entity_key=entity_key,
                features=features,
                feature_version=self.feature_version,
                event_timestamp=event_timestamp or datetime.now(timezone.utc).replace(tzinfo=None)
            )
        
        return snapshot_id
    
    def store_customer_features(
        self,
        customer_key: str,
        features: Dict[str, Any],
        event_timestamp: Optional[datetime] = None,
        create_snapshot: bool = True
    ) -> Optional[str]:
        """Store customer-level features.
        
        Args:
            customer_key: Customer key
            features: Customer feature dictionary
            event_timestamp: Event timestamp
            create_snapshot: Whether to create a snapshot
        
        Returns:
            Snapshot ID if created, None otherwise
        """
        # Store features
        self.feature_store.store_features(
            entity_key=customer_key,
            features=features,
            ttl_seconds=self.default_ttl_seconds
        )
        
        # Create snapshot if requested
        snapshot_id = None
        if create_snapshot:
            snapshot_id = self.feature_store.create_snapshot(
                entity_key=customer_key,
                features=features,
                feature_version=self.feature_version,
                event_timestamp=event_timestamp or datetime.now(timezone.utc).replace(tzinfo=None)
            )
        
        return snapshot_id
    
    def get_transaction_features(
        self,
        customer_key: str,
        feature_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get transaction features for a customer.
        
        Args:
            customer_key: Customer key
            feature_names: Optional list of specific feature names
        
        Returns:
            Dictionary of features
        """
        return self.feature_store.get_features(
            entity_key=customer_key,
            feature_names=feature_names
        )
    
    def get_account_features(
        self,
        customer_key: str,
        account_key: str,
        feature_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get account features for a customer.
        
        Args:
            customer_key: Customer key
            account_key: Account key
            feature_names: Optional list of specific feature names
        
        Returns:
            Dictionary of features
        """
        entity_key = f"{customer_key}:{account_key}"
        return self.feature_store.get_features(
            entity_key=entity_key,
            feature_names=feature_names
        )
    
    def get_customer_features(
        self,
        customer_key: str,
        feature_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get customer-level features.
        
        Args:
            customer_key: Customer key
            feature_names: Optional list of specific feature names
        
        Returns:
            Dictionary of features
        """
        return self.feature_store.get_features(
            entity_key=customer_key,
            feature_names=feature_names
        )
    
    def get_all_features_for_prediction(
        self,
        customer_key: str,
        account_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get all features needed for prediction.
        
        Args:
            customer_key: Customer key
            account_key: Optional account key
        
        Returns:
            Combined feature dictionary
        """
        all_features = {}
        
        # Get customer features
        customer_features = self.get_customer_features(customer_key)
        all_features.update({f"customer_{k}": v for k, v in customer_features.items()})
        
        # Get transaction features
        transaction_features = self.get_transaction_features(customer_key)
        all_features.update({f"transaction_{k}": v for k, v in transaction_features.items()})
        
        # Get account features if account key provided
        if account_key:
            account_features = self.get_account_features(customer_key, account_key)
            all_features.update({f"account_{k}": v for k, v in account_features.items()})
        
        return all_features
    
    def update_feature_version(self, new_version: str) -> None:
        """Update the feature version.
        
        Args:
            new_version: New feature version
        """
        self.feature_version = new_version
        logger.info(f"Feature version updated to {new_version}")
    
    def get_feature_version(self) -> str:
        """Get current feature version.
        
        Returns:
            Current feature version
        """
        return self.feature_version
    
    def delete_customer_features(self, customer_key: str) -> int:
        """Delete all features for a customer.
        
        Args:
            customer_key: Customer key
        
        Returns:
            Number of features deleted
        """
        return self.feature_store.delete_features(customer_key)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get adapter metrics.
        
        Returns:
            Dictionary of metrics
        """
        return {
            'feature_version': self.feature_version,
            'feature_store_metrics': self.feature_store.get_metrics(),
        }
    
    def health_check(self) -> bool:
        """Check if feature store is healthy.
        
        Returns:
            True if healthy, False otherwise
        """
        return self.feature_store.health_check()
    
    def close(self) -> None:
        """Close feature store adapter."""
        self.feature_store.close()
        logger.info("Feature store adapter closed")