"""Main stream processor integrating all components.

This module provides the main StreamProcessor class that integrates event-time
handling, watermark management, late event handling, window operations, and
state management into a cohesive stream processing engine.
"""

import logging
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime

from src.streaming.processor.event_time import EventTimeProcessor, TimedEvent
from src.streaming.processor.watermark import WatermarkManager
from src.streaming.processor.late_events import LateEventHandler, LateEventStrategy
from src.streaming.processor.windows import WindowOperator, WindowType
from src.streaming.processor.state import StateManager, StateBackend

logger = logging.getLogger(__name__)


class StreamProcessor:
    """Main stream processor for real-time analytics."""
    
    def __init__(
        self,
        allowed_lateness_ms: int = 5000,
        out_of_orderness_ms: int = 1000,
        late_event_strategy: LateEventStrategy = LateEventStrategy.SIDE_OUTPUT,
        state_backend: StateBackend = StateBackend.MEMORY,
        checkpoint_interval_ms: int = 60000
    ):
        """Initialize stream processor.
        
        Args:
            allowed_lateness_ms: Maximum allowed lateness in milliseconds
            out_of_orderness_ms: Out-of-orderness bound in milliseconds
            late_event_strategy: Strategy for handling late events
            state_backend: State backend type
            checkpoint_interval_ms: Checkpoint interval in milliseconds
        """
        # Initialize components
        self.event_time_processor = EventTimeProcessor(
            allowed_lateness_ms=allowed_lateness_ms
        )
        self.watermark_manager = WatermarkManager(
            out_of_orderness_ms=out_of_orderness_ms
        )
        self.late_event_handler = LateEventHandler(
            strategy=late_event_strategy,
            allowed_lateness_ms=allowed_lateness_ms
        )
        self.state_manager = StateManager(
            backend=state_backend,
            checkpoint_interval_ms=checkpoint_interval_ms
        )
        
        # Window operators (can be multiple)
        self.window_operators: List[WindowOperator] = []
        
        # Processing functions
        self.processing_fn: Optional[Callable] = None
        self.window_fn: Optional[Callable] = None
        
        # Metrics
        self.metrics = {
            'events_processed': 0,
            'events_dropped': 0,
            'windows_triggered': 0,
        }
        
        logger.info("Stream processor initialized")
    
    def register_processing_function(self, fn: Callable) -> None:
        """Register event processing function.
        
        Args:
            fn: Function to process each event
        """
        self.processing_fn = fn
        logger.info("Processing function registered")
    
    def register_window_function(self, fn: Callable) -> None:
        """Register window computation function.
        
        Args:
            fn: Function to compute window results
        """
        self.window_fn = fn
        logger.info("Window function registered")
    
    def add_window_operator(
        self,
        window_type: WindowType,
        window_size_ms: int,
        slide_ms: Optional[int] = None,
        session_gap_ms: Optional[int] = None
    ) -> WindowOperator:
        """Add a window operator.
        
        Args:
            window_type: Type of window
            window_size_ms: Window size in milliseconds
            slide_ms: Slide interval for sliding windows
            session_gap_ms: Session gap for session windows
        
        Returns:
            WindowOperator instance
        """
        window_operator = WindowOperator(
            window_type=window_type,
            window_size_ms=window_size_ms,
            slide_ms=slide_ms,
            session_gap_ms=session_gap_ms,
            allowed_lateness_ms=self.event_time_processor.allowed_lateness_ms
        )
        self.window_operators.append(window_operator)
        logger.info(f"Added {window_type.value} window operator")
        return window_operator
    
    def process_event(
        self,
        event: Dict[str, Any],
        key: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Process a single event through the stream processor.
        
        Args:
            event: Event data
            key: Optional key for keyed operations
        
        Returns:
            Processed event or None if dropped
        """
        # Get current watermark
        watermark = self.watermark_manager.get_global_watermark()
        
        # Assign time information
        timed_event = self.event_time_processor.assign_timed_event(event, watermark)
        
        # Track event for watermark calculation
        event_timestamp = timed_event.event_timestamp
        source = key or "global"
        self.watermark_manager.track_event(event_timestamp, source)
        
        # Update watermark
        self.watermark_manager.calculate_global_watermark()
        watermark = self.watermark_manager.get_global_watermark()
        
        # Check if event is late
        if timed_event.is_late:
            # Handle late event
            self.late_event_handler.handle_late_event(
                event=timed_event.event_data,
                event_timestamp=timed_event.event_timestamp,
                watermark=watermark
            )
            self.metrics['events_dropped'] += 1
            return None
        
        # Assign to windows
        for window_operator in self.window_operators:
            window_operator.assign_window(
                event=timed_event.event_data,
                event_timestamp=timed_event.event_timestamp,
                key=key
            )
        
        # Process event with processing function
        if self.processing_fn:
            try:
                result = self.processing_fn(timed_event, self.state_manager)
                self.metrics['events_processed'] += 1
                return result
            except Exception as e:
                logger.error(f"Processing function failed: {e}")
                return None
        
        self.metrics['events_processed'] += 1
        return timed_event.event_data
    
    def trigger_windows(self) -> List[Dict[str, Any]]:
        """Trigger window computation for all window operators.
        
        Returns:
            List of window results
        """
        watermark = self.watermark_manager.get_global_watermark()
        if watermark is None:
            return []
        
        all_results = []
        
        for window_operator in self.window_operators:
            if self.window_fn:
                results = window_operator.trigger_windows(watermark, self.window_fn)
                all_results.extend(results)
                self.metrics['windows_triggered'] += len(results)
        
        return all_results
    
    def checkpoint(self) -> None:
        """Create a state checkpoint."""
        watermark = self.watermark_manager.get_global_watermark()
        self.state_manager.checkpoint(watermark)
    
    def restore(self, snapshot_id: Optional[str] = None) -> bool:
        """Restore state from snapshot.
        
        Args:
            snapshot_id: Snapshot ID to restore (uses latest if None)
        
        Returns:
            True if successful, False otherwise
        """
        if snapshot_id:
            return self.state_manager.restore(snapshot_id)
        else:
            return self.state_manager.restore_latest()
    
    def get_watermark(self) -> Optional[datetime]:
        """Get current watermark.
        
        Returns:
            Current watermark or None
        """
        return self.watermark_manager.get_global_watermark()
    
    def get_late_events(self) -> List[Any]:
        """Get late events from handler.
        
        Returns:
            List of late events
        """
        if self.late_event_handler.strategy == LateEventStrategy.SIDE_OUTPUT:
            return self.late_event_handler.get_side_output()
        elif self.late_event_handler.strategy == LateEventStrategy.BUFFER:
            return self.late_event_handler.get_buffered_events()
        else:
            return []
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get processor metrics.
        
        Returns:
            Dictionary of metrics
        """
        return {
            'processor': dict(self.metrics),
            'event_time': self.event_time_processor.get_metrics(),
            'watermark': self.watermark_manager.get_metrics(),
            'late_events': self.late_event_handler.get_metrics(),
            'state': self.state_manager.get_metrics(),
            'windows': [
                window_operator.get_metrics() for window_operator in self.window_operators
            ],
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get processor status.
        
        Returns:
            Dictionary with status information
        """
        return {
            'watermark': self.watermark_manager.get_global_watermark().isoformat() if self.watermark_manager.get_global_watermark() else None,
            'max_event_timestamp': self.event_time_processor.get_max_event_timestamp().isoformat() if self.event_time_processor.get_max_event_timestamp() else None,
            'window_operator_count': len(self.window_operators),
            'late_event_strategy': self.late_event_handler.strategy.value,
            'state_backend': self.state_manager.backend.value,
            'snapshot_count': len(self.state_manager.get_snapshots()),
            'status': {
                'event_time': self.event_time_processor.get_metrics(),
                'watermark': self.watermark_manager.get_status(),
                'late_events': self.late_event_handler.get_status(),
                'state': self.state_manager.get_status(),
                'windows': [
                    window_operator.get_status() for window_operator in self.window_operators
                ],
            },
        }
    
    def reset_metrics(self) -> None:
        """Reset all metrics."""
        self.metrics = {
            'events_processed': 0,
            'events_dropped': 0,
            'windows_triggered': 0,
        }
        self.event_time_processor.reset_metrics()
        self.watermark_manager.reset_metrics()
        self.late_event_handler.reset_metrics()
        self.state_manager.reset_metrics()
        for window_operator in self.window_operators:
            window_operator.reset_metrics()
    
    def reset(self) -> None:
        """Reset processor state."""
        self.event_time_processor.reset()
        self.watermark_manager.clear_all()
        self.late_event_handler.reset()
        self.state_manager.clear()
        for window_operator in self.window_operators:
            window_operator.reset()
        self.reset_metrics()
        logger.info("Stream processor reset")