"""Unit tests for main stream processor."""

import pytest
from datetime import datetime, timedelta

from src.streaming.processor.processor import StreamProcessor
from src.streaming.processor.windows import WindowType
from src.streaming.processor.late_events import LateEventStrategy
from src.streaming.processor.state import StateBackend


class TestStreamProcessor:
    """Test StreamProcessor class."""
    
    @pytest.fixture
    def processor(self):
        """Create a stream processor."""
        return StreamProcessor(
            allowed_lateness_ms=5000,
            out_of_orderness_ms=1000,
            late_event_strategy=LateEventStrategy.SIDE_OUTPUT,
            state_backend=StateBackend.MEMORY
        )
    
    def test_processor_initialization(self, processor):
        """Test processor initialization."""
        assert processor.event_time_processor is not None
        assert processor.watermark_manager is not None
        assert processor.late_event_handler is not None
        assert processor.state_manager is not None
        assert len(processor.window_operators) == 0
    
    def test_register_processing_function(self, processor):
        """Test registering processing function."""
        def process_fn(timed_event, state_manager):
            return {"processed": True}
        
        processor.register_processing_function(process_fn)
        assert processor.processing_fn is not None
    
    def test_register_window_function(self, processor):
        """Test registering window function."""
        def window_fn(window):
            return {"result": "test"}
        
        processor.register_window_function(window_fn)
        assert processor.window_fn is not None
    
    def test_add_window_operator(self, processor):
        """Test adding window operator."""
        window_operator = processor.add_window_operator(
            window_type=WindowType.TUMBLING,
            window_size_ms=60000
        )
        
        assert len(processor.window_operators) == 1
        assert window_operator.window_type == WindowType.TUMBLING
    
    def test_process_event(self, processor):
        """Test processing an event."""
        def process_fn(timed_event, state_manager):
            return {"processed": True, "event_id": timed_event.event_data["event_id"]}
        
        processor.register_processing_function(process_fn)
        
        event = {
            "event_id": "evt_123",
            "event_timestamp": datetime.utcnow(),
        }
        
        result = processor.process_event(event)
        
        assert result is not None
        assert result["processed"] is True
        assert result["event_id"] == "evt_123"
    
    def test_process_event_with_key(self, processor):
        """Test processing an event with a key."""
        def process_fn(timed_event, state_manager):
            state_manager.set_keyed("customer", timed_event.event_data["event_id"], {"count": 1})
            return {"processed": True}
        
        processor.register_processing_function(process_fn)
        
        event = {
            "event_id": "evt_123",
            "event_timestamp": datetime.utcnow(),
        }
        
        processor.process_event(event, key="cust_123")
        
        # Check state
        customer_state = processor.state_manager.get_keyed("customer", "cust_123")
        assert customer_state is not None
        assert customer_state["count"] == 1
    
    def test_process_late_event(self, processor):
        """Test processing a late event."""
        processor.late_event_handler.strategy = LateEventStrategy.SIDE_OUTPUT
        
        # First, process some events to advance watermark
        for i in range(5):
            event = {
                "event_id": f"evt_{i}",
                "event_timestamp": datetime.utcnow(),
            }
            processor.process_event(event)
        
        # Now process a late event
        late_event = {
            "event_id": "evt_late",
            "event_timestamp": datetime.utcnow() - timedelta(seconds=10),
        }
        
        result = processor.process_event(late_event)
        
        # Late event should be dropped (result is None)
        assert result is None
        
        # Check late events
        late_events = processor.get_late_events()
        assert len(late_events) > 0
    
    def test_checkpoint(self, processor):
        """Test creating a checkpoint."""
        event = {
            "event_id": "evt_123",
            "event_timestamp": datetime.utcnow(),
        }
        processor.process_event(event)
        
        processor.checkpoint()
        
        snapshots = processor.state_manager.get_snapshots()
        assert len(snapshots) == 1
    
    def test_restore(self, processor):
        """Test restoring from snapshot."""
        # Process event and create checkpoint
        event = {
            "event_id": "evt_123",
            "event_timestamp": datetime.utcnow(),
        }
        processor.process_event(event)
        processor.checkpoint()
        
        # Get snapshot ID
        snapshot_id = processor.state_manager.get_snapshots()[0].snapshot_id
        
        # Reset and restore
        processor.reset()
        processor.restore(snapshot_id)
        
        # Check state is restored
        assert len(processor.state_manager.get_snapshots()) == 1
    
    def test_get_watermark(self, processor):
        """Test getting watermark."""
        event = {
            "event_id": "evt_123",
            "event_timestamp": datetime.utcnow(),
        }
        processor.process_event(event)
        
        watermark = processor.get_watermark()
        assert watermark is not None
        assert isinstance(watermark, datetime)
    
    def test_get_metrics(self, processor):
        """Test getting metrics."""
        event = {
            "event_id": "evt_123",
            "event_timestamp": datetime.utcnow(),
        }
        processor.process_event(event)
        
        metrics = processor.get_metrics()
        
        assert 'processor' in metrics
        assert 'event_time' in metrics
        assert 'watermark' in metrics
        assert 'late_events' in metrics
        assert 'state' in metrics
        assert 'windows' in metrics
    
    def test_get_status(self, processor):
        """Test getting status."""
        status = processor.get_status()
        
        assert 'watermark' in status
        assert 'max_event_timestamp' in status
        assert 'window_operator_count' in status
        assert 'late_event_strategy' in status
        assert 'state_backend' in status
        assert 'snapshot_count' in status
        assert 'status' in status
    
    def test_reset_metrics(self, processor):
        """Test resetting metrics."""
        event = {
            "event_id": "evt_123",
            "event_timestamp": datetime.utcnow(),
        }
        processor.process_event(event)
        
        processor.reset_metrics()
        
        metrics = processor.get_metrics()
        assert metrics['processor']['events_processed'] == 0
    
    def test_reset(self, processor):
        """Test resetting processor."""
        event = {
            "event_id": "evt_123",
            "event_timestamp": datetime.utcnow(),
        }
        processor.process_event(event)
        processor.checkpoint()
        
        processor.reset()
        
        # Check everything is reset
        assert processor.get_watermark() is None
        assert processor.event_time_processor.get_max_event_timestamp() is None
        assert len(processor.state_manager.get_snapshots()) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])