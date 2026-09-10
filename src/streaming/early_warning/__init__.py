"""Streaming early warning module.

This module provides real-time early warning capabilities for the banking analytics
platform, adapting batch early warning indicators for streaming event processing.

Key Components:
- StreamingWarningAdapter: Adapts batch early warning detection for streaming
- Real-time warning score calculation
- Watchlist management
"""

from src.streaming.early_warning.warning_adapter import StreamingWarningAdapter

__all__ = ["StreamingWarningAdapter"]
