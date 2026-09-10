"""Redis feature store for streaming analytics.

This module provides a Redis-based feature store for real-time feature serving,
including feature storage, retrieval, versioning, and snapshot management.
"""

from .feature_store import FeatureStore, FeatureVersion, FeatureSnapshot
from .adapter import FeatureStoreAdapter

__all__ = [
    "FeatureStore",
    "FeatureVersion",
    "FeatureSnapshot",
    "FeatureStoreAdapter",
]