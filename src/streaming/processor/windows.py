"""Window operations for stream processing.

This module provides window operations including tumbling, sliding, and session
windows with event-time semantics.
"""

import logging
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict

logger = logging.getLogger(__name__)


class WindowType(str, Enum):
    """Window types."""
    TUMBLING = "tumbling"
    SLIDING = "sliding"
    SESSION = "session"


@dataclass
class Window:
    """Window information."""
    window_id: str
    start: datetime
    end: datetime
    key: Optional[str] = None
    events: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.events is None:
            self.events = []


@dataclass
class WindowResult:
    """Result of window computation."""
    window_id: str
    start: datetime
    end: datetime
    key: Optional[str]
    result: Any
    event_count: int


class WindowOperator:
    """Perform window operations on streaming events."""
    
    def __init__(
        self,
        window_type: WindowType,
        window_size_ms: int,
        slide_ms: Optional[int] = None,
        session_gap_ms: Optional[int] = None,
        allowed_lateness_ms: int = 5000
    ):
        """Initialize window operator.
        
        Args:
            window_type: Type of window
            window_size_ms: Window size in milliseconds
            slide_ms: Slide interval in milliseconds (for sliding windows)
            session_gap_ms: Session gap in milliseconds (for session windows)
            allowed_lateness_ms: Allowed lateness in milliseconds
        """
        self.window_type = window_type
        self.window_size_ms = window_size_ms
        self.slide_ms = slide_ms or window_size_ms
        self.session_gap_ms = session_gap_ms
        self.allowed_lateness_ms = allowed_lateness_ms
        
        # Track active windows per key
        self.active_windows: Dict[str, List[Window]] = defaultdict(list)
        
        # Track completed windows
        self.completed_windows: List[WindowResult] = []
        
        # Window counter for IDs
        self.window_counter = 0
        
        # Metrics
        self.metrics = {
            'windows_created': 0,
            'windows_completed': 0,
            'events_processed': 0,
            'late_events_in_window': 0,
        }
    
    def assign_window(
        self,
        event: Dict[str, Any],
        event_timestamp: datetime,
        key: Optional[str] = None
    ) -> Optional[Window]:
        """Assign event to appropriate window(s).
        
        Args:
            event: Event data
            event_timestamp: Event timestamp
            key: Optional key for keyed windows
        
        Returns:
            Window that event was assigned to (or None if no window)
        """
        self.metrics['events_processed'] += 1
        
        if self.window_type == WindowType.TUMBLING:
            return self._assign_tumbling_window(event, event_timestamp, key)
        elif self.window_type == WindowType.SLIDING:
            return self._assign_sliding_window(event, event_timestamp, key)
        elif self.window_type == WindowType.SESSION:
            return self._assign_session_window(event, event_timestamp, key)
        else:
            logger.error(f"Unknown window type: {self.window_type}")
            return None
    
    def _assign_tumbling_window(
        self,
        event: Dict[str, Any],
        event_timestamp: datetime,
        key: Optional[str]
    ) -> Optional[Window]:
        """Assign event to tumbling window.
        
        Args:
            event: Event data
            event_timestamp: Event timestamp
            key: Optional key
        
        Returns:
            Window that event was assigned to
        """
        # Calculate window start
        window_size = timedelta(milliseconds=self.window_size_ms)
        window_start = self._align_to_window(event_timestamp, window_size)
        window_end = window_start + window_size
        
        # Generate window ID
        window_id = self._generate_window_id(key, window_start, window_end)
        
        # Get or create window
        window = self._get_or_create_window(key, window_id, window_start, window_end)
        
        # Add event to window
        window.events.append(event)
        
        return window
    
    def _assign_sliding_window(
        self,
        event: Dict[str, Any],
        event_timestamp: datetime,
        key: Optional[str]
    ) -> Optional[Window]:
        """Assign event to sliding window(s).
        
        Args:
            event: Event data
            event_timestamp: Event timestamp
            key: Optional key
        
        Returns:
            Window that event was assigned to (first window)
        """
        # Calculate all windows this event belongs to
        window_size = timedelta(milliseconds=self.window_size_ms)
        slide = timedelta(milliseconds=self.slide_ms)
        
        # Find the first window that could contain this event
        # Start from event_timestamp and go backwards
        current_start = self._align_to_window(event_timestamp, slide)
        
        # Find all windows that contain this event
        windows_assigned = []
        while current_start > event_timestamp - window_size:
            window_end = current_start + window_size
            
            if current_start <= event_timestamp < window_end:
                window_id = self._generate_window_id(key, current_start, window_end)
                window = self._get_or_create_window(key, window_id, current_start, window_end)
                window.events.append(event)
                windows_assigned.append(window)
            
            current_start -= slide
        
        return windows_assigned[0] if windows_assigned else None
    
    def _assign_session_window(
        self,
        event: Dict[str, Any],
        event_timestamp: datetime,
        key: Optional[str]
    ) -> Optional[Window]:
        """Assign event to session window.
        
        Args:
            event: Event data
            event_timestamp: Event timestamp
            key: Optional key
        
        Returns:
            Window that event was assigned to
        """
        session_gap = timedelta(milliseconds=self.session_gap_ms)
        
        # Get existing windows for this key
        key_windows = self.active_windows[key]
        
        # Find window that can merge with this event
        merged_window = None
        for window in key_windows:
            # Check if event is within session gap of window
            if window.end + session_gap >= event_timestamp >= window.start - session_gap:
                # Merge with this window
                window.start = min(window.start, event_timestamp)
                window.end = max(window.end, event_timestamp)
                window.events.append(event)
                merged_window = window
                break
        
        # If no mergeable window, create new one
        if merged_window is None:
            window_start = event_timestamp
            window_end = event_timestamp
            window_id = self._generate_window_id(key, window_start, window_end)
            window = self._get_or_create_window(key, window_id, window_start, window_end)
            window.events.append(event)
            merged_window = window
        
        return merged_window
    
    def _align_to_window(self, timestamp: datetime, window_size: timedelta) -> datetime:
        """Align timestamp to window boundary.
        
        Args:
            timestamp: Timestamp to align
            window_size: Window size
        
        Returns:
            Aligned timestamp
        """
        # Calculate epoch milliseconds
        epoch = datetime(1970, 1, 1)
        delta = timestamp - epoch
        window_size_ms = int(window_size.total_seconds() * 1000)
        aligned_ms = (int(delta.total_seconds() * 1000) // window_size_ms) * window_size_ms
        return epoch + timedelta(milliseconds=aligned_ms)
    
    def _generate_window_id(
        self,
        key: Optional[str],
        start: datetime,
        end: datetime
    ) -> str:
        """Generate unique window ID.
        
        Args:
            key: Optional key
            start: Window start
            end: Window end
        
        Returns:
            Window ID
        """
        key_part = key or "global"
        start_part = start.isoformat()
        end_part = end.isoformat()
        return f"{key_part}_{start_part}_{end_part}"
    
    def _get_or_create_window(
        self,
        key: Optional[str],
        window_id: str,
        start: datetime,
        end: datetime
    ) -> Window:
        """Get existing window or create new one.
        
        Args:
            key: Optional key
            window_id: Window ID
            start: Window start
            end: Window end
        
        Returns:
            Window object
        """
        key_part = key or "global"
        windows = self.active_windows[key_part]
        
        # Check if window exists
        for window in windows:
            if window.window_id == window_id:
                return window
        
        # Create new window
        window = Window(
            window_id=window_id,
            start=start,
            end=end,
            key=key
        )
        windows.append(window)
        self.metrics['windows_created'] += 1
        
        return window
    
    def trigger_windows(
        self,
        watermark: datetime,
        compute_fn: Callable[[Window], Any]
    ) -> List[WindowResult]:
        """Trigger window computation for windows that have passed watermark.
        
        Args:
            watermark: Current watermark
            compute_fn: Function to compute window result
        
        Returns:
            List of window results
        """
        results = []
        
        for key, windows in list(self.active_windows.items()):
            remaining_windows = []
            
            for window in windows:
                # Check if window end is before watermark - allowed lateness
                window_end_threshold = window.end - timedelta(milliseconds=self.allowed_lateness_ms)
                
                if watermark >= window_end_threshold:
                    # Trigger window computation
                    result = compute_fn(window)
                    
                    window_result = WindowResult(
                        window_id=window.window_id,
                        start=window.start,
                        end=window.end,
                        key=window.key,
                        result=result,
                        event_count=len(window.events)
                    )
                    
                    results.append(window_result)
                    self.completed_windows.append(window_result)
                    self.metrics['windows_completed'] += 1
                else:
                    # Keep window active
                    remaining_windows.append(window)
            
            # Update active windows
            self.active_windows[key] = remaining_windows
        
        return results
    
    def get_active_windows(self, key: Optional[str] = None) -> List[Window]:
        """Get active windows.
        
        Args:
            key: Optional key to filter by
        
        Returns:
            List of active windows
        """
        if key:
            return self.active_windows.get(key, []).copy()
        else:
            all_windows = []
            for windows in self.active_windows.values():
                all_windows.extend(windows)
            return all_windows
    
    def get_completed_windows(self) -> List[WindowResult]:
        """Get completed window results.
        
        Returns:
            List of completed window results
        """
        return self.completed_windows.copy()
    
    def clear_completed_windows(self) -> None:
        """Clear completed windows."""
        self.completed_windows.clear()
        logger.debug("Cleared completed windows")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get window operator metrics.
        
        Returns:
            Dictionary of metrics
        """
        return dict(self.metrics)
    
    def get_status(self) -> Dict[str, Any]:
        """Get window operator status.
        
        Returns:
            Dictionary with status information
        """
        return {
            'window_type': self.window_type.value,
            'window_size_ms': self.window_size_ms,
            'slide_ms': self.slide_ms,
            'session_gap_ms': self.session_gap_ms,
            'allowed_lateness_ms': self.allowed_lateness_ms,
            'active_window_count': sum(len(windows) for windows in self.active_windows.values()),
            'completed_window_count': len(self.completed_windows),
            'metrics': self.get_metrics(),
        }
    
    def reset_metrics(self) -> None:
        """Reset metrics counters."""
        self.metrics = {
            'windows_created': 0,
            'windows_completed': 0,
            'events_processed': 0,
            'late_events_in_window': 0,
        }
    
    def reset(self) -> None:
        """Reset window operator state."""
        self.active_windows.clear()
        self.completed_windows.clear()
        self.window_counter = 0
        self.reset_metrics()