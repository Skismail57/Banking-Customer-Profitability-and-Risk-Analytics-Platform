"""Streaming alert engine module.

This module provides real-time alert generation capabilities for the banking analytics
platform, generating alerts from risk, anomaly, and warning signals.

Key Components:
- AlertEngine: Real-time alert generation engine
- Alert deduplication and aggregation
- Alert severity classification
"""

from src.streaming.alerts.alert_engine import AlertEngine

__all__ = ["AlertEngine"]
