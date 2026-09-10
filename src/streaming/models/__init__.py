"""Model registry for ML model management.

This module provides model registry capabilities for the banking analytics
platform, managing model versions, deployments, and rollbacks.
"""

from src.streaming.models.model_registry import ModelRegistry, ModelVersion, ModelDeployment

__all__ = ['ModelRegistry', 'ModelVersion', 'ModelDeployment']
