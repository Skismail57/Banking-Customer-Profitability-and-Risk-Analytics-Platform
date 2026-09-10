"""Streaming anomaly detection module.

This module provides real-time anomaly detection capabilities for the banking analytics
platform, adapting batch anomaly detection algorithms for streaming event processing.

Key Components:
- StreamingAnomalyAdapter: Adapts batch anomaly detection for streaming
- State management for streaming statistics
- Real-time anomaly scoring
"""

from src.streaming.anomaly.anomaly_adapter import StreamingAnomalyAdapter

__all__ = ["StreamingAnomalyAdapter"]
