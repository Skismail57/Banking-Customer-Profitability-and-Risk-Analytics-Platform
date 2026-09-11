"""Event-time handling for stream processing.

This module provides utilities for handling event-time semantics in streaming,
including timestamp extraction, event-time vs processing-time tracking, and
time-based event ordering.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TimedEvent:
    """Event with time information."""
    event_data: Dict[str, Any]
    event_timestamp: datetime
    processing_timestamp: datetime
    watermark: Optional[datetime] = None
    is_late: bool = False
    lateness_ms: Optional[int] = None


class EventTimeProcessor:
    """Process events with event-time semantics."""
    
    def __init__(
        self,
        allowed_lateness_ms: int = 5000,  # 5 seconds default
        clock_source: str = "system"  # system or event
    ):
        """Initialize event-time processor.
        
        Args:
            allowed_lateness_ms: Maximum allowed lateness in milliseconds
            clock_source: Clock source for watermark advancement (system or event)
        """
        self.allowed_lateness_ms = allowed_lateness_ms
        self.clock_source = clock_source
        
        # Track max event timestamp seen
        self.max_event_timestamp: Optional[datetime] = None
        
        # Track current watermark
        self.current_watermark: Optional[datetime] = None
        
        # Metrics
        self.metrics = {
            'events_processed': 0,
            'late_events': 0,
            'out_of_order_events': 0,
        }
    
    def extract_event_timestamp(self, event: Dict[str, Any]) -> datetime:
        """Extract event timestamp from event data.
        
        Args:
            event: Event data dictionary
        
        Returns:
            Event timestamp as datetime
        
        Raises:
            ValueError: If event timestamp is missing or invalid
        """
        if 'event_timestamp' not in event:
            raise ValueError("Event missing 'event_timestamp' field")
        
        timestamp_value = event['event_timestamp']
        
        # Handle string timestamps
        if isinstance(timestamp_value, str):
            try:
                return datetime.fromisoformat(timestamp_value)
            except ValueError:
                raise ValueError(f"Invalid event timestamp format: {timestamp_value}")
        
        # Handle datetime objects
        elif isinstance(timestamp_value, datetime):
            return timestamp_value
        
        else:
            raise ValueError(f"Unsupported timestamp type: {type(timestamp_value)}")
    
    def extract_processing_timestamp(self, event: Dict[str, Any]) -> datetime:
        """Extract processing timestamp from event data.
        
        Args:
            event: Event data dictionary
        
        Returns:
            Processing timestamp as datetime
        """
        if 'ingestion_timestamp' in event:
            timestamp_value = event['ingestion_timestamp']
        elif 'processing_timestamp' in event:
            timestamp_value = event['processing_timestamp']
        else:
            # Use current time if not present
            return datetime.now(timezone.utc).replace(tzinfo=None)
        
        # Handle string timestamps
        if isinstance(timestamp_value, str):
            try:
                return datetime.fromisoformat(timestamp_value)
            except ValueError:
                return datetime.now(timezone.utc).replace(tzinfo=None)
        
        # Handle datetime objects
        elif isinstance(timestamp_value, datetime):
            return timestamp_value
        
        else:
            return datetime.now(timezone.utc).replace(tzinfo=None)
    
    def assign_timed_event(
        self,
        event: Dict[str, Any],
        watermark: Optional[datetime] = None
    ) -> TimedEvent:
        """Assign time information to an event.
        
        Args:
            event: Event data dictionary
            watermark: Current watermark
        
        Returns:
            TimedEvent with time information
        """
        # Extract timestamps
        event_timestamp = self.extract_event_timestamp(event)
        processing_timestamp = self.extract_processing_timestamp(event)
        
        # Update max event timestamp
        if self.max_event_timestamp is None or event_timestamp > self.max_event_timestamp:
            self.max_event_timestamp = event_timestamp
        
        # Determine if event is late
        is_late = False
        lateness_ms = None
        
        if watermark is not None:
            lateness = watermark - event_timestamp
            lateness_ms = int(lateness.total_seconds() * 1000)
            
            if lateness_ms > self.allowed_lateness_ms:
                is_late = True
                self.metrics['late_events'] += 1
                logger.debug(f"Late event detected: {lateness_ms}ms late")
        
        # Check if out of order
        if self.max_event_timestamp is not None and event_timestamp < self.max_event_timestamp:
            self.metrics['out_of_order_events'] += 1
            logger.debug(f"Out-of-order event detected")
        
        self.metrics['events_processed'] += 1
        
        return TimedEvent(
            event_data=event,
            event_timestamp=event_timestamp,
            processing_timestamp=processing_timestamp,
            watermark=watermark,
            is_late=is_late,
            lateness_ms=lateness_ms
        )
    
    def advance_watermark(self, new_watermark: datetime) -> None:
        """Advance the watermark to a new value.
        
        Args:
            new_watermark: New watermark value
        """
        if self.current_watermark is None or new_watermark > self.current_watermark:
            self.current_watermark = new_watermark
            logger.debug(f"Watermark advanced to {new_watermark}")
    
    def calculate_watermark(
        self,
        event_timestamps: list[datetime],
        out_of_orderness_ms: int = 1000
    ) -> datetime:
        """Calculate watermark from event timestamps.
        
        Args:
            event_timestamps: List of event timestamps
            out_of_orderness_ms: Out-of-orderness bound in milliseconds
        
        Returns:
            Calculated watermark
        """
        if not event_timestamps:
            return datetime.now(timezone.utc).replace(tzinfo=None)
        
        # Watermark = max timestamp - out-of-orderness bound
        max_timestamp = max(event_timestamps)
        watermark = max_timestamp - timedelta(milliseconds=out_of_orderness_ms)
        
        return watermark
    
    def get_watermark(self) -> Optional[datetime]:
        """Get current watermark.
        
        Returns:
            Current watermark or None if not set
        """
        return self.current_watermark
    
    def get_max_event_timestamp(self) -> Optional[datetime]:
        """Get maximum event timestamp seen.
        
        Returns:
            Maximum event timestamp or None if no events processed
        """
        return self.max_event_timestamp
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get processor metrics.
        
        Returns:
            Dictionary of metrics
        """
        return dict(self.metrics)
    
    def reset_metrics(self) -> None:
        """Reset metrics counters."""
        self.metrics = {
            'events_processed': 0,
            'late_events': 0,
            'out_of_order_events': 0,
        }
    
    def reset(self) -> None:
        """Reset processor state."""
        self.max_event_timestamp = None
        self.current_watermark = None
        self.reset_metrics()