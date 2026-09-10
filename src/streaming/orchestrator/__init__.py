"""Streaming pipeline orchestrator module.

This module provides pipeline orchestration capabilities for the banking analytics
platform, coordinating all streaming components into a unified processing pipeline.

Key Components:
- StreamingOrchestrator: Main pipeline coordinator
- Event processing workflow
- Component integration
"""

from src.streaming.orchestrator.pipeline_orchestrator import StreamingOrchestrator

__all__ = ["StreamingOrchestrator"]
