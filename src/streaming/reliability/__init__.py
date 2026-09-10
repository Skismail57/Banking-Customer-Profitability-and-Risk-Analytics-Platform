"""Streaming reliability utilities.

This module provides reliability patterns for streaming operations including
retry logic, dead letter queues, backpressure control, and circuit breakers.
"""

from .retry import RetryConfig, RetryPolicy, retry_with_backoff, RetryTracker
from .dlq import DeadLetterMessage, DeadLetterQueueHandler, DLQReprocessor
from .backpressure import (
    BackpressureConfig,
    BackpressureController,
    RateLimiter,
    AdaptiveRateLimiter,
    TokenBucket,
)
from .circuit_breaker import (
    CircuitState,
    CircuitBreakerConfig,
    CircuitBreaker,
    CircuitOpenError,
    circuit_breaker,
    CircuitBreakerRegistry,
)

__all__ = [
    # Retry
    'RetryConfig',
    'RetryPolicy',
    'retry_with_backoff',
    'RetryTracker',
    # Dead Letter Queue
    'DeadLetterMessage',
    'DeadLetterQueueHandler',
    'DLQReprocessor',
    # Backpressure
    'BackpressureConfig',
    'BackpressureController',
    'RateLimiter',
    'AdaptiveRateLimiter',
    'TokenBucket',
    # Circuit Breaker
    'CircuitState',
    'CircuitBreakerConfig',
    'CircuitBreaker',
    'CircuitOpenError',
    'circuit_breaker',
    'CircuitBreakerRegistry',
]
