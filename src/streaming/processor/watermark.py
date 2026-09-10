"""Watermark management for stream processing.

This module provides watermark management for event-time processing,
including watermark calculation, advancement, and tracking per-key/partition.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class Watermark:
    """Watermark information."""
    timestamp: datetime
    source: str  # e.g., "partition_0", "customer_key_123"
    updated_at: datetime


class WatermarkManager:
    """Manage watermarks for event-time processing."""
    
    def __init__(
        self,
        out_of_orderness_ms: int = 1000,  # 1 second default
        watermark_strategy: str = "max_minus_delay"  # max_minus_delay or min_timestamp
    ):
        """Initialize watermark manager.
        
        Args:
            out_of_orderness_ms: Out-of-orderness bound in milliseconds
            watermark_strategy: Strategy for watermark calculation
        """
        self.out_of_orderness_ms = out_of_orderness_ms
        self.watermark_strategy = watermark_strategy
        
        # Track watermarks per source (partition, key, etc.)
        self.watermarks: Dict[str, Watermark] = {}
        
        # Track global watermark
        self.global_watermark: Optional[datetime] = None
        
        # Track event timestamps per source
        self.event_timestamps: Dict[str, List[datetime]] = defaultdict(list)
        
        # Metrics
        self.metrics = {
            'watermark_advancements': 0,
            'events_tracked': 0,
            'sources_tracked': 0,
        }
    
    def track_event(
        self,
        event_timestamp: datetime,
        source: str = "global"
    ) -> None:
        """Track an event timestamp for watermark calculation.
        
        Args:
            event_timestamp: Event timestamp
            source: Source identifier (partition, key, etc.)
        """
        # Add timestamp to source's list
        self.event_timestamps[source].append(event_timestamp)
        
        # Keep only recent timestamps (last 1000 per source to avoid memory issues)
        if len(self.event_timestamps[source]) > 1000:
            self.event_timestamps[source] = self.event_timestamps[source][-1000:]
        
        self.metrics['events_tracked'] += 1
        
        # Update sources tracked count
        if source not in self.watermarks:
            self.metrics['sources_tracked'] += 1
    
    def calculate_source_watermark(self, source: str) -> Optional[datetime]:
        """Calculate watermark for a specific source.
        
        Args:
            source: Source identifier
        
        Returns:
            Calculated watermark or None if no events for source
        """
        if source not in self.event_timestamps or not self.event_timestamps[source]:
            return None
        
        timestamps = self.event_timestamps[source]
        
        if self.watermark_strategy == "max_minus_delay":
            # Watermark = max timestamp - out-of-orderness bound
            max_timestamp = max(timestamps)
            watermark = max_timestamp - timedelta(milliseconds=self.out_of_orderness_ms)
        elif self.watermark_strategy == "min_timestamp":
            # Watermark = min timestamp (more conservative)
            watermark = min(timestamps)
        else:
            # Default to max_minus_delay
            max_timestamp = max(timestamps)
            watermark = max_timestamp - timedelta(milliseconds=self.out_of_orderness_ms)
        
        return watermark
    
    def calculate_global_watermark(self) -> Optional[datetime]:
        """Calculate global watermark across all sources.
        
        Returns:
            Global watermark or None if no events tracked
        """
        if not self.event_timestamps:
            return None
        
        # Calculate watermark for each source
        source_watermarks = []
        for source in self.event_timestamps:
            watermark = self.calculate_source_watermark(source)
            if watermark:
                source_watermarks.append(watermark)
        
        if not source_watermarks:
            return None
        
        # Global watermark = minimum of all source watermarks
        global_watermark = min(source_watermarks)
        
        # Update global watermark if it advanced
        if self.global_watermark is None or global_watermark > self.global_watermark:
            self.global_watermark = global_watermark
            self.metrics['watermark_advancements'] += 1
            logger.debug(f"Global watermark advanced to {global_watermark}")
        
        return global_watermark
    
    def get_global_watermark(self) -> Optional[datetime]:
        """Get current global watermark.
        
        Returns:
            Global watermark or None if not set
        """
        # Recalculate to ensure it's up to date
        return self.calculate_global_watermark()
    
    def get_source_watermark(self, source: str) -> Optional[datetime]:
        """Get watermark for a specific source.
        
        Args:
            source: Source identifier
        
        Returns:
            Source watermark or None if not available
        """
        return self.calculate_source_watermark(source)
    
    def is_event_late(
        self,
        event_timestamp: datetime,
        watermark: Optional[datetime] = None
    ) -> bool:
        """Check if an event is late relative to watermark.
        
        Args:
            event_timestamp: Event timestamp
            watermark: Watermark to compare against (uses global if None)
        
        Returns:
            True if event is late, False otherwise
        """
        if watermark is None:
            watermark = self.get_global_watermark()
        
        if watermark is None:
            return False  # No watermark yet, assume not late
        
        # Event is late if its timestamp is before watermark
        return event_timestamp < watermark
    
    def get_event_lateness_ms(
        self,
        event_timestamp: datetime,
        watermark: Optional[datetime] = None
    ) -> Optional[int]:
        """Get how late an event is in milliseconds.
        
        Args:
            event_timestamp: Event timestamp
            watermark: Watermark to compare against (uses global if None)
        
        Returns:
            Lateness in milliseconds or None if not late
        """
        if watermark is None:
            watermark = self.get_global_watermark()
        
        if watermark is None:
            return None
        
        if event_timestamp >= watermark:
            return None  # Not late
        
        lateness = watermark - event_timestamp
        return int(lateness.total_seconds() * 1000)
    
    def advance_watermark(self, new_watermark: datetime) -> None:
        """Manually advance the global watermark.
        
        Args:
            new_watermark: New watermark value
        """
        if self.global_watermark is None or new_watermark > self.global_watermark:
            self.global_watermark = new_watermark
            self.metrics['watermark_advancements'] += 1
            logger.info(f"Watermark manually advanced to {new_watermark}")
    
    def clear_source(self, source: str) -> None:
        """Clear tracking data for a source.
        
        Args:
            source: Source identifier
        """
        if source in self.event_timestamps:
            del self.event_timestamps[source]
        if source in self.watermarks:
            del self.watermarks[source]
        
        logger.debug(f"Cleared watermark tracking for source: {source}")
    
    def clear_all(self) -> None:
        """Clear all tracking data."""
        self.event_timestamps.clear()
        self.watermarks.clear()
        self.global_watermark = None
        logger.debug("Cleared all watermark tracking data")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get watermark manager metrics.
        
        Returns:
            Dictionary of metrics
        """
        return dict(self.metrics)
    
    def get_status(self) -> Dict[str, Any]:
        """Get watermark manager status.
        
        Returns:
            Dictionary with status information
        """
        return {
            'global_watermark': self.global_watermark.isoformat() if self.global_watermark else None,
            'sources_tracked': len(self.event_timestamps),
            'out_of_orderness_ms': self.out_of_orderness_ms,
            'watermark_strategy': self.watermark_strategy,
            'metrics': self.get_metrics(),
        }
    
    def reset_metrics(self) -> None:
        """Reset metrics counters."""
        self.metrics = {
            'watermark_advancements': 0,
            'events_tracked': 0,
            'sources_tracked': len(self.event_timestamps),
        }