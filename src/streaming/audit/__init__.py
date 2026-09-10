"""Streaming decision audit module.

This module provides decision audit trail capabilities for the banking analytics
platform, tracking all decisions for regulatory compliance.

Key Components:
- DecisionAuditor: Decision audit trail tracking
- Feature snapshot management
- Full decision context capture
"""

from src.streaming.audit.decision_auditor import DecisionAuditor

__all__ = ["DecisionAuditor"]
