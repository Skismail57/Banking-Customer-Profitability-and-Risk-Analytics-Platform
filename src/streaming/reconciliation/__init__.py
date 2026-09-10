"""Streaming reconciliation module.

This module provides reconciliation capabilities for the banking analytics
platform, validating consistency between batch and live data.

Key Components:
- ReconciliationEngine: Batch vs live reconciliation
- Reconciliation report generation
- Discrepancy tracking
"""

from src.streaming.reconciliation.reconciliation import ReconciliationEngine

__all__ = ["ReconciliationEngine"]
