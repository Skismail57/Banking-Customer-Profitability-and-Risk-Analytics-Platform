"""Streaming module for Banking Analytics Platform.

This module provides real-time event processing capabilities for the banking analytics
platform, extending the existing batch analytics with streaming infrastructure.

Key Components:
- Event ingestion and validation
- Stream processing and transformation
- Real-time feature engineering
- Streaming anomaly detection
- Risk scoring and alerting
- Decision audit trail

Architecture:
The streaming layer extends the existing batch architecture while maintaining
separation of concerns. Batch and streaming pipelines can run independently
or be reconciled for consistency.

Usage:
    from src.streaming import StreamingConfig
    
    config = StreamingConfig.load()
    # Use config for streaming operations
"""

__version__ = "0.1.0"
__author__ = "Banking Analytics Platform Team"

from .config import StreamingConfig, get_streaming_config

__all__ = [
    "StreamingConfig",
    "get_streaming_config",
    "__version__",
]