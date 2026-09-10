"""Streaming risk scoring module.

This module provides real-time risk scoring capabilities for the banking analytics
platform, adapting batch risk analytics for streaming event processing.

Key Components:
- RealTimeRiskEngine: Real-time risk scoring engine
- Risk level determination based on streaming features
- Integration with existing RiskBase for consistency
"""

from src.streaming.risk.risk_engine import RealTimeRiskEngine

__all__ = ["RealTimeRiskEngine"]
