"""Unit tests for event-time processing."""

import pytest
from datetime import datetime, timedelta

from src.streaming.processor.event_time import EventTimeProcessor, TimedEvent


class TestEventTimeProcessor:
    """Test EventTimeProcessor class."""
    
    @pytest.fixture
    def processor(self):
        """Create an event-time processor."""
        return EventTimeProcessor(allowed_lateness_ms=5000)
    
    def test_extract_event_timestamp(self, processor):
        """Test extracting event timestamp."""
        event = {
            "event_id": "evt_123",
            "event_timestamp": datetime.utcnow().isoformat(),
        }
        
        timestamp = processor.extract_event_timestamp(event)
        assert isinstance(timestamp, datetime)
    
    def test_extract_event_timestamp_datetime(self, processor):
        """Test extracting datetime timestamp."""
        ts = datetime.utcnow()
        event = {
            "event_id": "evt_123",
            "event_timestamp": ts,
        }
        
        timestamp = processor.extract_event_timestamp(event)
        assert timestamp == ts
    
    def test_extract_event_timestamp_missing(self, processor):
        """Test error when timestamp is missing."""
        event = {"event_id": "evt_123"}
        
        with pytest.raises(ValueError, match="missing 'event_timestamp'"):
            processor.extract_event_timestamp(event)
    
    def test_extract_processing_timestamp(self, processor):
        """Test extracting processing timestamp."""
        event = {
            "event_id": "evt_123",
            "event_timestamp": datetime.utcnow().isoformat(),
            "ingestion_timestamp": datetime.utcnow().isoformat(),
        }
        
        timestamp = processor.extract_processing_timestamp(event)
        assert isinstance(timestamp, datetime)
    
    def test_assign_timed_event(self, processor):
        """Test assigning time information to event."""
        event = {
            "event_id": "evt_123",
            "event_timestamp": datetime.utcnow(),
        }
        
        timed_event = processor.assign_timed_event(event)
        
        assert isinstance(timed_event, TimedEvent)
        assert timed_event.event_data == event
        assert timed_event.event_timestamp == event["event_timestamp"]
        assert timed_event.processing_timestamp is not None
        assert timed_event.is_late is False
    
    def test_assign_timed_event_with_watermark(self, processor):
        """Test assigning time information with watermark."""
        event = {
            "event_id": "evt_123",
            "event_timestamp": datetime.utcnow() - timedelta(seconds=10),
        }
        
        watermark = datetime.utcnow()
        timed_event = processor.assign_timed_event(event, watermark)
        
        assert timed_event.is_late is True
        assert timed_event.lateness_ms is not None
        assert timed_event.lateness_ms > processor.allowed_lateness_ms
    
    def test_calculate_watermark(self, processor):
        """Test watermark calculation."""
        timestamps = [
            datetime.utcnow() - timedelta(seconds=5),
            datetime.utcnow() - timedelta(seconds=3),
            datetime.utcnow() - timedelta(seconds=1),
        ]
        
        watermark = processor.calculate_watermark(timestamps, out_of_orderness_ms=1000)
        
        assert isinstance(watermark, datetime)
        assert watermark < max(timestamps)
    
    def test_advance_watermark(self, processor):
        """Test advancing watermark."""
        new_watermark = datetime.utcnow()
        processor.advance_watermark(new_watermark)
        
        assert processor.get_watermark() == new_watermark
    
    def test_get_max_event_timestamp(self, processor):
        """Test getting max event timestamp."""
        event1 = {"event_id": "evt_1", "event_timestamp": datetime.utcnow() - timedelta(seconds=5)}
        event2 = {"event_id": "evt_2", "event_timestamp": datetime.utcnow()}
        
        processor.assign_timed_event(event1)
        processor.assign_timed_event(event2)
        
        max_ts = processor.get_max_event_timestamp()
        assert max_ts == event2["event_timestamp"]
    
    def test_metrics(self, processor):
        """Test metrics tracking."""
        event = {"event_id": "evt_123", "event_timestamp": datetime.utcnow()}
        processor.assign_timed_event(event)
        
        metrics = processor.get_metrics()
        assert metrics['events_processed'] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])