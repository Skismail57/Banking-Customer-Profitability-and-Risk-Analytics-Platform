"""Backpressure mechanism for controlling flow rate in streaming pipelines.

This module provides backpressure control to prevent overwhelming
downstream consumers when processing rates exceed capacity.
"""

import time
import logging
from typing import Optional, Callable
from dataclasses import dataclass
from collections import deque
from threading import Lock
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class BackpressureConfig:
    """Configuration for backpressure control."""
    max_queue_size: int = 1000
    target_latency_ms: float = 100.0
    max_latency_ms: float = 1000.0
    throttle_factor: float = 0.5
    recovery_factor: float = 1.2
    check_interval_ms: float = 100.0


class BackpressureController:
    """Control backpressure based on system metrics."""
    
    def __init__(self, config: Optional[BackpressureConfig] = None):
        """Initialize backpressure controller.
        
        Args:
            config: Backpressure configuration
        """
        self.config = config or BackpressureConfig()
        self._lock = Lock()
        self._current_throttle = 1.0  # 1.0 = full speed, 0.0 = stopped
        self._latency_samples = deque(maxlen=100)
        self._queue_size = 0
        self._is_throttled = False
    
    def record_latency(self, latency_ms: float):
        """Record processing latency sample.
        
        Args:
            latency_ms: Processing latency in milliseconds
        """
        with self._lock:
            self._latency_samples.append(latency_ms)
            self._adjust_throttle()
    
    def set_queue_size(self, size: int):
        """Set current queue size.
        
        Args:
            size: Current queue size
        """
        with self._lock:
            self._queue_size = size
            self._adjust_throttle()
    
    def _adjust_throttle(self):
        """Adjust throttle based on latency and queue size."""
        if not self._latency_samples:
            return
        
        avg_latency = sum(self._latency_samples) / len(self._latency_samples)
        
        # Check if we need to throttle
        if avg_latency > self.config.max_latency_ms or self._queue_size > self.config.max_queue_size:
            # Reduce throttle
            new_throttle = self._current_throttle * self.config.throttle_factor
            self._current_throttle = max(new_throttle, 0.1)  # Minimum 10%
            
            if not self._is_throttled:
                self._is_throttled = True
                logger.warning(
                    f"Backpressure activated: latency={avg_latency:.2f}ms, "
                    f"queue={self._queue_size}, throttle={self._current_throttle:.2f}"
                )
        
        elif avg_latency < self.config.target_latency_ms and self._queue_size < self.config.max_queue_size * 0.5:
            # Increase throttle (recovery)
            new_throttle = self._current_throttle * self.config.recovery_factor
            self._current_throttle = min(new_throttle, 1.0)  # Maximum 100%
            
            if self._is_throttled and self._current_throttle >= 1.0:
                self._is_throttled = False
                logger.info("Backpressure deactivated: system recovered")
    
    def get_throttle(self) -> float:
        """Get current throttle level.
        
        Returns:
            Throttle level (0.0 to 1.0)
        """
        with self._lock:
            return self._current_throttle
    
    def is_throttled(self) -> bool:
        """Check if currently throttled.
        
        Returns:
            True if throttled, False otherwise
        """
        with self._lock:
            return self._is_throttled
    
    def get_stats(self) -> dict:
        """Get backpressure statistics.
        
        Returns:
            Dictionary of statistics
        """
        with self._lock:
            avg_latency = sum(self._latency_samples) / len(self._latency_samples) if self._latency_samples else 0.0
            return {
                'current_throttle': self._current_throttle,
                'is_throttled': self._is_throttled,
                'queue_size': self._queue_size,
                'avg_latency_ms': avg_latency,
                'latency_samples': len(self._latency_samples),
            }
    
    def reset(self):
        """Reset backpressure controller state."""
        with self._lock:
            self._current_throttle = 1.0
            self._latency_samples.clear()
            self._queue_size = 0
            self._is_throttled = False


class RateLimiter:
    """Rate limiter for controlling message throughput."""
    
    def __init__(self, max_rate: float):
        """Initialize rate limiter.
        
        Args:
            max_rate: Maximum messages per second
        """
        self.max_rate = max_rate
        self.min_interval = 1.0 / max_rate if max_rate > 0 else 0
        self._last_time = 0.0
        self._lock = Lock()
    
    def acquire(self) -> float:
        """Acquire permission to process a message.
        
        Returns:
            Time to wait before processing (in seconds)
        """
        with self._lock:
            current_time = time.time()
            elapsed = current_time - self._last_time
            
            if elapsed >= self.min_interval:
                self._last_time = current_time
                return 0.0
            else:
                wait_time = self.min_interval - elapsed
                return wait_time
    
    async def acquire_async(self) -> float:
        """Acquire permission to process a message (async).
        
        Returns:
            Time to wait before processing (in seconds)
        """
        with self._lock:
            current_time = time.time()
            elapsed = current_time - self._last_time
            
            if elapsed >= self.min_interval:
                self._last_time = current_time
                return 0.0
            else:
                wait_time = self.min_interval - elapsed
                return wait_time
    
    def set_rate(self, new_rate: float):
        """Set new maximum rate.
        
        Args:
            new_rate: New maximum messages per second
        """
        with self._lock:
            self.max_rate = new_rate
            self.min_interval = 1.0 / new_rate if new_rate > 0 else 0
    
    def get_rate(self) -> float:
        """Get current maximum rate.
        
        Returns:
            Current maximum messages per second
        """
        return self.max_rate


class AdaptiveRateLimiter(RateLimiter):
    """Rate limiter that adapts based on backpressure signals."""
    
    def __init__(self, initial_rate: float, min_rate: float = 1.0, max_rate: float = 10000.0):
        """Initialize adaptive rate limiter.
        
        Args:
            initial_rate: Initial messages per second
            min_rate: Minimum messages per second
            max_rate: Maximum messages per second
        """
        super().__init__(initial_rate)
        self.min_rate = min_rate
        self.max_rate = max_rate
        self._backpressure_controller = BackpressureController()
    
    def adjust_for_backpressure(self, throttle: float):
        """Adjust rate based on backpressure throttle.
        
        Args:
            throttle: Throttle level (0.0 to 1.0)
        """
        new_rate = self.max_rate * throttle
        new_rate = max(self.min_rate, min(self.max_rate, new_rate))
        self.set_rate(new_rate)
    
    def record_latency(self, latency_ms: float):
        """Record latency for adaptive adjustment.
        
        Args:
            latency_ms: Processing latency in milliseconds
        """
        self._backpressure_controller.record_latency(latency_ms)
        self.adjust_for_backpressure(self._backpressure_controller.get_throttle())
    
    def get_stats(self) -> dict:
        """Get rate limiter statistics.
        
        Returns:
            Dictionary of statistics
        """
        return {
            'current_rate': self.get_rate(),
            'min_rate': self.min_rate,
            'max_rate': self.max_rate,
            'backpressure': self._backpressure_controller.get_stats(),
        }


class TokenBucket:
    """Token bucket algorithm for rate limiting."""
    
    def __init__(self, capacity: float, refill_rate: float):
        """Initialize token bucket.
        
        Args:
            capacity: Maximum number of tokens
            refill_rate: Tokens per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self._tokens = capacity
        self._last_refill = time.time()
        self._lock = Lock()
    
    def _refill(self):
        """Refill tokens based on elapsed time."""
        current_time = time.time()
        elapsed = current_time - self._last_refill
        tokens_to_add = elapsed * self.refill_rate
        
        with self._lock:
            self._tokens = min(self.capacity, self._tokens + tokens_to_add)
            self._last_refill = current_time
    
    def consume(self, tokens: float = 1.0) -> bool:
        """Consume tokens from bucket.
        
        Args:
            tokens: Number of tokens to consume
        
        Returns:
            True if tokens were available, False otherwise
        """
        self._refill()
        
        with self._lock:
            if self._tokens >= tokens:
                self._tokens -= tokens
                return True
            return False
    
    def wait_for_tokens(self, tokens: float = 1.0, timeout: Optional[float] = None) -> bool:
        """Wait for tokens to become available.
        
        Args:
            tokens: Number of tokens needed
            timeout: Maximum time to wait in seconds
        
        Returns:
            True if tokens were available, False if timeout
        """
        start_time = time.time()
        
        while True:
            if self.consume(tokens):
                return True
            
            if timeout and (time.time() - start_time) >= timeout:
                return False
            
            time.sleep(0.01)
    
    def get_available_tokens(self) -> float:
        """Get number of available tokens.
        
        Returns:
            Number of available tokens
        """
        self._refill()
        with self._lock:
            return self._tokens
