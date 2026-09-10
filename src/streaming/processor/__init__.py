"""Stream processing engine for real-time analytics.

This module provides stream processing capabilities including event-time handling,
watermark management, late event handling, window operations, and state management.
"""

from .event_time import EventTimeProcessor, TimedEvent
from .watermark import WatermarkManager, Watermark
from .late_events import LateEventHandler, LateEvent, LateEventStrategy
from .windows import WindowOperator, Window, WindowResult, WindowType
from .state import StateManager, StateSnapshot, StateBackend
from .processor import StreamProcessor

__all__ = [
    "EventTimeProcessor",
    "TimedEvent",
    "WatermarkManager",
    "Watermark",
    "LateEventHandler",
    "LateEvent",
    "LateEventStrategy",
    "WindowOperator",
    "Window",
    "WindowResult",
    "WindowType",
    "StateManager",
    "StateSnapshot",
    "StateBackend",
    "StreamProcessor",
]