"""Late event handling for stream processing.

This module provides utilities for handling late events that arrive after
the watermark has passed them, including side output, buffering, and
reprocessing strategies.
"""

import logging
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class LateEventStrategy(str, Enum):
    """Strategy for handling late events."""
    DROP = "drop"  # Drop late events
    SIDE_OUTPUT = "side_output"  # Send to side output
    BUFFER = "buffer"  # Buffer for reprocessing
    REPROCESS = "reprocess"  # Reprocess with updated state


@dataclass
class LateEvent:
    """Late event information."""
    event_data: Dict[str, Any]
    event_timestamp: datetime
    watermark_at_arrival: datetime
    lateness_ms: int
    handled: bool = False
    handling_strategy: Optional[str] = None


class LateEventHandler:
    """Handle late events according to configured strategy."""
    
    def __init__(
        self,
        strategy: LateEventStrategy = LateEventStrategy.SIDE_OUTPUT,
        allowed_lateness_ms: int = 5000,  # 5 seconds default
        buffer_size: int = 1000
    ):
        """Initialize late event handler.
        
        Args:
            strategy: Strategy for handling late events
            allowed_lateness_ms: Maximum allowed lateness in milliseconds
            buffer_size: Maximum number of late events to buffer
        """
        self.strategy = strategy
        self.allowed_lateness_ms = allowed_lateness_ms
        self.buffer_size = buffer_size
        
        # Buffer for late events
        self.late_event_buffer: List[LateEvent] = []
        
        # Side output for late events
        self.side_output: List[LateEvent] = []
        
        # Metrics
        self.metrics = {
            'late_events_received': 0,
            'late_events_dropped': 0,
            'late_events_buffered': 0,
            'late_events_side_output': 0,
            'late_events_reprocessed': 0,
        }
    
    def handle_late_event(
        self,
        event: Dict[str, Any],
        event_timestamp: datetime,
        watermark: datetime,
        on_side_output: Optional[Callable] = None,
        on_reprocess: Optional[Callable] = None
    ) -> Optional[LateEvent]:
        """Handle a late event according to configured strategy.
        
        Args:
            event: Event data
            event_timestamp: Event timestamp
            watermark: Current watermark
            on_side_output: Optional callback for side output
            on_reprocess: Optional callback for reprocessing
        
        Returns:
            LateEvent object or None if dropped
        """
        # Calculate lateness
        lateness = watermark - event_timestamp
        lateness_ms = int(lateness.total_seconds() * 1000)
        
        self.metrics['late_events_received'] += 1
        
        # Create late event object
        late_event = LateEvent(
            event_data=event,
            event_timestamp=event_timestamp,
            watermark_at_arrival=watermark,
            lateness_ms=lateness_ms,
            handled=False,
            handling_strategy=None
        )
        
        # Handle according to strategy
        if self.strategy == LateEventStrategy.DROP:
            self._drop_late_event(late_event)
        
        elif self.strategy == LateEventStrategy.SIDE_OUTPUT:
            self._side_output_late_event(late_event, on_side_output)
        
        elif self.strategy == LateEventStrategy.BUFFER:
            self._buffer_late_event(late_event)
        
        elif self.strategy == LateEventStrategy.REPROCESS:
            self._reprocess_late_event(late_event, on_reprocess)
        
        return late_event
    
    def _drop_late_event(self, late_event: LateEvent) -> None:
        """Drop a late event.
        
        Args:
            late_event: Late event to drop
        """
        late_event.handled = True
        late_event.handling_strategy = "dropped"
        self.metrics['late_events_dropped'] += 1
        logger.debug(f"Dropped late event with lateness {late_event.lateness_ms}ms")
    
    def _side_output_late_event(
        self,
        late_event: LateEvent,
        on_side_output: Optional[Callable]
    ) -> None:
        """Send late event to side output.
        
        Args:
            late_event: Late event to side output
            on_side_output: Optional callback
        """
        late_event.handled = True
        late_event.handling_strategy = "side_output"
        self.side_output.append(late_event)
        self.metrics['late_events_side_output'] += 1
        logger.debug(f"Side output late event with lateness {late_event.lateness_ms}ms")
        
        # Call callback if provided
        if on_side_output:
            on_side_output(late_event)
    
    def _buffer_late_event(self, late_event: LateEvent) -> None:
        """Buffer a late event for potential reprocessing.
        
        Args:
            late_event: Late event to buffer
        """
        # Check buffer size
        if len(self.late_event_buffer) >= self.buffer_size:
            # Drop oldest event if buffer is full
            dropped = self.late_event_buffer.pop(0)
            self.metrics['late_events_dropped'] += 1
            logger.warning(f"Late event buffer full, dropped oldest event")
        
        self.late_event_buffer.append(late_event)
        late_event.handled = True
        late_event.handling_strategy = "buffered"
        self.metrics['late_events_buffered'] += 1
        logger.debug(f"Buffered late event with lateness {late_event.lateness_ms}ms")
    
    def _reprocess_late_event(
        self,
        late_event: LateEvent,
        on_reprocess: Optional[Callable]
    ) -> None:
        """Reprocess a late event.
        
        Args:
            late_event: Late event to reprocess
            on_reprocess: Optional callback
        """
        late_event.handled = True
        late_event.handling_strategy = "reprocessed"
        self.metrics['late_events_reprocessed'] += 1
        logger.debug(f"Reprocessed late event with lateness {late_event.lateness_ms}ms")
        
        # Call callback if provided
        if on_reprocess:
            on_reprocess(late_event)
    
    def get_side_output(self) -> List[LateEvent]:
        """Get all events in side output.
        
        Returns:
            List of late events in side output
        """
        return self.side_output.copy()
    
    def clear_side_output(self) -> None:
        """Clear side output."""
        self.side_output.clear()
        logger.debug("Cleared late event side output")
    
    def get_buffered_events(self) -> List[LateEvent]:
        """Get all buffered late events.
        
        Returns:
            List of buffered late events
        """
        return self.late_event_buffer.copy()
    
    def clear_buffer(self) -> None:
        """Clear late event buffer."""
        self.late_event_buffer.clear()
        logger.debug("Cleared late event buffer")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get late event handler metrics.
        
        Returns:
            Dictionary of metrics
        """
        return dict(self.metrics)
    
    def get_status(self) -> Dict[str, Any]:
        """Get late event handler status.
        
        Returns:
            Dictionary with status information
        """
        return {
            'strategy': self.strategy.value,
            'allowed_lateness_ms': self.allowed_lateness_ms,
            'buffer_size': self.buffer_size,
            'buffered_count': len(self.late_event_buffer),
            'side_output_count': len(self.side_output),
            'metrics': self.get_metrics(),
        }
    
    def reset_metrics(self) -> None:
        """Reset metrics counters."""
        self.metrics = {
            'late_events_received': 0,
            'late_events_dropped': 0,
            'late_events_buffered': 0,
            'late_events_side_output': 0,
            'late_events_reprocessed': 0,
        }
    
    def reset(self) -> None:
        """Reset handler state."""
        self.late_event_buffer.clear()
        self.side_output.clear()
        self.reset_metrics()