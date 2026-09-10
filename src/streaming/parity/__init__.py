"""Streaming feature parity module.

This module provides feature parity validation capabilities for the banking analytics
platform, validating consistency between batch and streaming features.

Key Components:
- FeatureParityChecker: Batch vs stream feature validation
- Statistical tests for feature comparison
- Parity report generation
"""

from src.streaming.parity.feature_parity import FeatureParityChecker

__all__ = ["FeatureParityChecker"]
