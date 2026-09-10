"""Streaming observability and monitoring module.

This module provides observability capabilities for the banking analytics
platform, including metrics collection, logging, and health monitoring.

Key Components:
- MetricsCollector: Metrics collection and aggregation
- Logging configuration
- Health monitoring
"""

from src.streaming.observability.metrics import MetricsCollector

__all__ = ["MetricsCollector"]
