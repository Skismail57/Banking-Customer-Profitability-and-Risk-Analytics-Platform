"""Core Analytics Layer.

This layer integrates Profitability, Risk, and Behavior analytics into a unified
core analytics layer that outputs to fact_customer_metrics.

Architecture Position:
Customer 360/Transaction/Product Analytics → Core Analytics → Statistical Analytics
"""

from src.core_analytics.core_analytics_orchestrator import CoreAnalyticsOrchestrator

__all__ = ['CoreAnalyticsOrchestrator']
