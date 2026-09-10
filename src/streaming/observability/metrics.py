"""Metrics collector for streaming pipeline.

This module provides metrics collection and aggregation for the streaming
pipeline, tracking performance, throughput, and business metrics.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable
import logging
import time
import json
import uuid
from collections import defaultdict
from dataclasses import dataclass, asdict
from contextlib import contextmanager

logger = logging.getLogger(__name__)


@dataclass
class MetricValue:
    """Metric value with timestamp."""
    value: float
    timestamp: datetime


class MetricsCollector:
    """Metrics collector for streaming pipeline.
    
    This collector tracks:
    - Performance metrics (latency, throughput)
    - Business metrics (alerts, anomalies, risk events)
    - System metrics (consumer lag, error rates)
    - Custom metrics
    
    Key Features:
    - Incremental metric updates
    - Time-windowed aggregation
    - Metric export (Prometheus format)
    - Metric reset
    """
    
    def __init__(self):
        """Initialize metrics collector."""
        self.counters = defaultdict(int)
        self.gauges = defaultdict(float)
        self.histograms = defaultdict(list)
        self.timers = defaultdict(list)
        self.start_time = datetime.utcnow()
    
    def increment_counter(self, name: str, value: int = 1, labels: Optional[Dict[str, str]] = None):
        """Increment a counter metric.
        
        Args:
            name: Metric name
            value: Value to increment by
            labels: Metric labels (for Prometheus export)
        """
        key = self._make_key(name, labels)
        self.counters[key] += value
        logger.debug(f"Counter {key} incremented by {value}")
    
    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Set a gauge metric.
        
        Args:
            name: Metric name
            value: Value to set
            labels: Metric labels
        """
        key = self._make_key(name, labels)
        self.gauges[key] = value
        logger.debug(f"Gauge {key} set to {value}")
    
    def observe_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Observe a histogram metric.
        
        Args:
            name: Metric name
            value: Value to observe
            labels: Metric labels
        """
        key = self._make_key(name, labels)
        self.histograms[key].append(value)
        
        # Keep only last 1000 values
        if len(self.histograms[key]) > 1000:
            self.histograms[key] = self.histograms[key][-1000:]
        
        logger.debug(f"Histogram {key} observed value {value}")
    
    def observe_timer(self, name: str, duration_ms: float, labels: Optional[Dict[str, str]] = None):
        """Observe a timer metric.
        
        Args:
            name: Metric name
            duration_ms: Duration in milliseconds
            labels: Metric labels
        """
        key = self._make_key(name, labels)
        self.timers[key].append(duration_ms)
        
        # Keep only last 1000 values
        if len(self.timers[key]) > 1000:
            self.timers[key] = self.timers[key][-1000:]
        
        logger.debug(f"Timer {key} observed duration {duration_ms}ms")
    
    def time_function(self, name: str, labels: Optional[Dict[str, str]] = None):
        """Context manager for timing function execution.
        
        Args:
            name: Metric name
            labels: Metric labels
        
        Returns:
            Context manager
        """
        class TimerContext:
            def __init__(self, collector, metric_name, metric_labels):
                self.collector = collector
                self.metric_name = metric_name
                self.metric_labels = metric_labels
                self.start_time = None
            
            def __enter__(self):
                self.start_time = time.time()
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                duration_ms = (time.time() - self.start_time) * 1000
                self.collector.observe_timer(self.metric_name, duration_ms, self.metric_labels)
        
        return TimerContext(self, name, labels)
    
    def get_counter(self, name: str, labels: Optional[Dict[str, str]] = None) -> int:
        """Get counter value.
        
        Args:
            name: Metric name
            labels: Metric labels
        
        Returns:
            Counter value
        """
        key = self._make_key(name, labels)
        return self.counters.get(key, 0)
    
    def get_gauge(self, name: str, labels: Optional[Dict[str, str]] = None) -> float:
        """Get gauge value.
        
        Args:
            name: Metric name
            labels: Metric labels
        
        Returns:
            Gauge value
        """
        key = self._make_key(name, labels)
        return self.gauges.get(key, 0.0)
    
    def get_histogram_stats(self, name: str, labels: Optional[Dict[str, str]] = None) -> Dict[str, float]:
        """Get histogram statistics.
        
        Args:
            name: Metric name
            labels: Metric labels
        
        Returns:
            Statistics dictionary (count, sum, avg, min, max, p50, p95, p99)
        """
        key = self._make_key(name, labels)
        values = self.histograms.get(key, [])
        
        if not values:
            return {
                'count': 0,
                'sum': 0.0,
                'avg': 0.0,
                'min': 0.0,
                'max': 0.0,
                'p50': 0.0,
                'p95': 0.0,
                'p99': 0.0
            }
        
        import numpy as np
        values_array = np.array(values)
        
        return {
            'count': len(values),
            'sum': float(np.sum(values_array)),
            'avg': float(np.mean(values_array)),
            'min': float(np.min(values_array)),
            'max': float(np.max(values_array)),
            'p50': float(np.percentile(values_array, 50)),
            'p95': float(np.percentile(values_array, 95)),
            'p99': float(np.percentile(values_array, 99))
        }
    
    def get_timer_stats(self, name: str, labels: Optional[Dict[str, str]] = None) -> Dict[str, float]:
        """Get timer statistics.
        
        Args:
            name: Metric name
            labels: Metric labels
        
        Returns:
            Statistics dictionary
        """
        return self.get_histogram_stats(name, labels)
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics.
        
        Returns:
            Dictionary of all metrics
        """
        return {
            'counters': dict(self.counters),
            'gauges': dict(self.gauges),
            'histograms': {k: self.get_histogram_stats(k) for k in self.histograms.keys()},
            'timers': {k: self.get_timer_stats(k) for k in self.timers.keys()},
            'start_time': self.start_time.isoformat(),
            'uptime_seconds': (datetime.utcnow() - self.start_time).total_seconds()
        }
    
    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format.
        
        Returns:
            Prometheus-formatted metrics string
        """
        lines = []
        
        # Export counters
        for key, value in self.counters.items():
            name, labels = self._parse_key(key)
            label_str = self._format_labels(labels)
            lines.append(f"# TYPE {name} counter")
            lines.append(f"{name}{label_str} {value}")
        
        # Export gauges
        for key, value in self.gauges.items():
            name, labels = self._parse_key(key)
            label_str = self._format_labels(labels)
            lines.append(f"# TYPE {name} gauge")
            lines.append(f"{name}{label_str} {value}")
        
        # Export histograms
        for key in self.histograms.keys():
            name, labels = self._parse_key(key)
            label_str = self._format_labels(labels)
            stats = self.get_histogram_stats(key)
            
            lines.append(f"# TYPE {name} histogram")
            lines.append(f"{name}_count{label_str} {stats['count']}")
            lines.append(f"{name}_sum{label_str} {stats['sum']}")
            lines.append(f"{name}_avg{label_str} {stats['avg']}")
            lines.append(f"{name}_min{label_str} {stats['min']}")
            lines.append(f"{name}_max{label_str} {stats['max']}")
            lines.append(f"{name}_p50{label_str} {stats['p50']}")
            lines.append(f"{name}_p95{label_str} {stats['p95']}")
            lines.append(f"{name}_p99{label_str} {stats['p99']}")
        
        return '\n'.join(lines)
    
    def reset(self):
        """Reset all metrics."""
        self.counters.clear()
        self.gauges.clear()
        self.histograms.clear()
        self.timers.clear()
        self.start_time = datetime.utcnow()
        logger.info("Metrics reset")
    
    def _make_key(self, name: str, labels: Optional[Dict[str, str]]) -> str:
        """Make metric key from name and labels.
        
        Args:
            name: Metric name
            labels: Metric labels
        
        Returns:
            Metric key
        """
        if labels:
            label_str = ','.join(f"{k}={v}" for k, v in sorted(labels.items()))
            return f"{name}{{{label_str}}}"
        return name
    
    def _parse_key(self, key: str) -> tuple:
        """Parse metric key into name and labels.
        
        Args:
            key: Metric key
        
        Returns:
            Tuple of (name, labels_dict)
        """
        if '{' in key and '}' in key:
            name, label_str = key.split('{', 1)
            label_str = label_str.rstrip('}')
            labels = {}
            for label_pair in label_str.split(','):
                if '=' in label_pair:
                    k, v = label_pair.split('=', 1)
                    labels[k] = v
            return name, labels
        return key, {}
    
    def _format_labels(self, labels: Dict[str, str]) -> str:
        """Format labels for Prometheus export.
        
        Args:
            labels: Labels dictionary
        
        Returns:
            Formatted label string
        """
        if labels:
            return '{' + ','.join(f'{k}="{v}"' for k, v in sorted(labels.items())) + '}'
        return ''


# Global metrics collector instance
metrics = MetricsCollector()


class StructuredLogger:
    """Structured logger for consistent log formatting."""
    
    def __init__(self, service_name: str = "streaming-pipeline"):
        """Initialize structured logger.
        
        Args:
            service_name: Service name for log context
        """
        self.service_name = service_name
        self.logger = logging.getLogger(service_name)
    
    def log(
        self,
        level: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None
    ):
        """Log structured message.
        
        Args:
            level: Log level (debug, info, warning, error, critical)
            message: Log message
            context: Additional context data
            trace_id: Trace ID for distributed tracing
            span_id: Span ID for distributed tracing
        """
        log_data = {
            'service': self.service_name,
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'message': message,
            'trace_id': trace_id,
            'span_id': span_id,
            'context': context or {}
        }
        
        # Log as JSON for structured parsing
        log_message = json.dumps(log_data)
        
        getattr(self.logger, level)(log_message)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.log('debug', message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self.log('info', message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.log('warning', message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self.log('error', message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self.log('critical', message, **kwargs)


class Tracer:
    """Distributed tracing for request tracking."""
    
    def __init__(self, service_name: str = "streaming-pipeline"):
        """Initialize tracer.
        
        Args:
            service_name: Service name
        """
        self.service_name = service_name
        self.active_spans = {}
        self.span_history = []
    
    def start_span(
        self,
        operation_name: str,
        parent_span_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Start a new span.
        
        Args:
            operation_name: Name of the operation
            parent_span_id: Parent span ID
            context: Span context data
        
        Returns:
            Span ID
        """
        span_id = str(uuid.uuid4())
        trace_id = parent_span_id.split(':')[0] if parent_span_id else str(uuid.uuid4())
        
        span = {
            'span_id': span_id,
            'trace_id': trace_id,
            'parent_span_id': parent_span_id,
            'operation_name': operation_name,
            'service_name': self.service_name,
            'start_time': time.time(),
            'context': context or {},
            'tags': {},
            'logs': []
        }
        
        self.active_spans[span_id] = span
        
        return f"{trace_id}:{span_id}"
    
    def end_span(self, span_full_id: str, tags: Optional[Dict[str, str]] = None):
        """End a span.
        
        Args:
            span_full_id: Full span ID (trace_id:span_id)
            tags: Span tags
        """
        trace_id, span_id = span_full_id.split(':', 1)
        
        if span_id in self.active_spans:
            span = self.active_spans[span_id]
            span['end_time'] = time.time()
            span['duration_ms'] = (span['end_time'] - span['start_time']) * 1000
            span['tags'] = tags or {}
            
            # Move to history
            self.span_history.append(span)
            del self.active_spans[span_id]
    
    def add_span_tag(self, span_full_id: str, key: str, value: str):
        """Add tag to span.
        
        Args:
            span_full_id: Full span ID
            key: Tag key
            value: Tag value
        """
        trace_id, span_id = span_full_id.split(':', 1)
        
        if span_id in self.active_spans:
            self.active_spans[span_id]['tags'][key] = value
    
    def add_span_log(self, span_full_id: str, log_data: Dict[str, Any]):
        """Add log to span.
        
        Args:
            span_full_id: Full span ID
            log_data: Log data
        """
        trace_id, span_id = span_full_id.split(':', 1)
        
        if span_id in self.active_spans:
            self.active_spans[span_id]['logs'].append({
                'timestamp': time.time(),
                'data': log_data
            })
    
    @contextmanager
    def trace_operation(
        self,
        operation_name: str,
        parent_span_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """Context manager for tracing operations.
        
        Args:
            operation_name: Operation name
            parent_span_id: Parent span ID
            context: Span context
        
        Yields:
            Span ID
        """
        span_id = self.start_span(operation_name, parent_span_id, context)
        try:
            yield span_id
        finally:
            self.end_span(span_id)
    
    def get_trace(self, trace_id: str) -> List[Dict[str, Any]]:
        """Get all spans for a trace.
        
        Args:
            trace_id: Trace ID
        
        Returns:
            List of spans
        """
        return [
            span for span in self.span_history
            if span['trace_id'] == trace_id
        ]
    
    def export_spans(self) -> List[Dict[str, Any]]:
        """Export all completed spans.
        
        Returns:
            List of spans
        """
        return self.span_history.copy()
    
    def clear_history(self):
        """Clear span history."""
        self.span_history.clear()


class ObservabilityManager:
    """Unified observability manager."""
    
    def __init__(self, service_name: str = "streaming-pipeline"):
        """Initialize observability manager.
        
        Args:
            service_name: Service name
        """
        self.service_name = service_name
        self.metrics = MetricsCollector()
        self.logger = StructuredLogger(service_name)
        self.tracer = Tracer(service_name)
    
    def record_event(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        trace_id: Optional[str] = None
    ):
        """Record an event with full observability.
        
        Args:
            event_type: Type of event
            event_data: Event data
            trace_id: Trace ID
        """
        # Log event
        self.logger.info(
            f"Event: {event_type}",
            context={'event_type': event_type, **event_data},
            trace_id=trace_id
        )
        
        # Record metric
        self.metrics.increment_counter(f"events_{event_type}")
    
    @contextmanager
    def observe_operation(
        self,
        operation_name: str,
        parent_span_id: Optional[str] = None
    ):
        """Observe operation with metrics and tracing.
        
        Args:
            operation_name: Operation name
            parent_span_id: Parent span ID
        
        Yields:
            Span ID
        """
        with self.tracer.trace_operation(operation_name, parent_span_id) as span_id:
            with self.metrics.time_function(f"operation_{operation_name}"):
                yield span_id
    
    def get_observability_snapshot(self) -> Dict[str, Any]:
        """Get snapshot of all observability data.
        
        Returns:
            Observability snapshot
        """
        return {
            'metrics': self.metrics.get_all_metrics(),
            'spans': self.tracer.export_spans(),
            'service': self.service_name,
            'timestamp': datetime.utcnow().isoformat()
        }


# Global observability manager instance
observability = ObservabilityManager()
