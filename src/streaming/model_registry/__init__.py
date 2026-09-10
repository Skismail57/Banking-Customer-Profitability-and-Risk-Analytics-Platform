"""Streaming model registry module.

This module provides model registry capabilities for the banking analytics
platform, tracking model versions and deployments for production ML.

Key Components:
- ModelRegistry: Model version tracking and lifecycle management
- OnlineModel: Real-time model inference
- Integration with existing ModelPersistence
"""

from src.streaming.model_registry.registry import ModelRegistry
from src.streaming.model_registry.online_model import OnlineModel

__all__ = ["ModelRegistry", "OnlineModel"]
