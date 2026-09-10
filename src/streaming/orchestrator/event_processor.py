"""Event processor integration with StreamProcessor.

This module integrates the existing StreamProcessor with the streaming
orchestrator to provide event-time processing capabilities.
"""

from datetime import datetime
from typing import Dict, Any, Optional, Callable
import logging

from src.streaming.config import StreamingConfig
from src.streaming.processor.processor import StreamProcessor
from src.streaming.orchestrator.pipeline_orchestrator import StreamingOrchestrator

logger = logging.getLogger(__name__)


class EventProcessor:
    """Event processor that integrates StreamProcessor with orchestrator.
    
    This processor wraps the existing StreamProcessor and integrates it
    with the streaming orchestrator for end-to-end event processing.
    
    Key Features:
    - Uses existing StreamProcessor for event-time processing
    - Integrates with orchestrator for business logic
    - Handles late events and watermarks
    - Supports windowed operations
    """
    
    def __init__(
        self,
        config: StreamingConfig,
        orchestrator: StreamingOrchestrator
    ):
        """Initialize event processor.
        
        Args:
            config: Streaming configuration
            orchestrator: Streaming orchestrator
        """
        self.config = config
        self.orchestrator = orchestrator
        
        # Initialize StreamProcessor
        self.stream_processor = StreamProcessor(config)
        
        # Register processing function
        self.stream_processor.register_processing_function(
            self._process_event_with_orchestrator
        )
    
    def _process_event_with_orchestrator(
        self,
        event: Dict[str, Any],
        watermark: datetime
    ) -> Dict[str, Any]:
        """Process event using orchestrator.
        
        Args:
            event: Event data
            watermark: Current watermark
        
        Returns:
            Processing result
        """
        event_id = event.get('event_id')
        event_time = event.get('event_timestamp')
        
        logger.debug(f"Processing event {event_id} with watermark {watermark}")
        
        # Check if event is late
        if event_time < watermark:
            logger.warning(f"Late event detected: {event_id} at {event_time}, watermark {watermark}")
            # Handle late event (could send to DLQ or process with warning)
        
        # Process through orchestrator
        result = self.orchestrator.process_event(event)
        
        # Add watermark info
        result['watermark'] = watermark.isoformat()
        result['is_late'] = event_time < watermark
        
        return result
    
    def process_batch(self, events: list) -> list:
        """Process a batch of events.
        
        Args:
            events: List of events
        
        Returns:
            List of processing results
        """
        logger.info(f"Processing batch of {len(events)} events")
        
        results = []
        for event in events:
            try:
                result = self.orchestrator.process_event(event)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing event: {e}")
                results.append({
                    'event_id': event.get('event_id'),
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def get_watermark(self) -> datetime:
        """Get current watermark.
        
        Returns:
            Current watermark
        """
        return self.stream_processor.get_watermark()
    
    def get_processing_metrics(self) -> Dict[str, Any]:
        """Get processing metrics.
        
        Returns:
            Processing metrics
        """
        return {
            'stream_processor_metrics': self.stream_processor.get_metrics(),
            'orchestrator_metrics': self.orchestrator.get_pipeline_metrics()
        }
