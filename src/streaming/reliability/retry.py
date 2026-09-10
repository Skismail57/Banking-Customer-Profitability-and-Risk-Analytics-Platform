"""Retry logic with exponential backoff for streaming operations.

This module provides retry mechanisms for handling transient failures
in streaming operations with configurable backoff strategies.
"""

import time
import asyncio
import logging
from typing import Callable, Optional, Type, Tuple, Any
from functools import wraps
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 30.0
    exponential_base: float = 2.0
    jitter: bool = True
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,)


class RetryPolicy:
    """Retry policy with exponential backoff."""
    
    def __init__(self, config: RetryConfig):
        """Initialize retry policy.
        
        Args:
            config: Retry configuration
        """
        self.config = config
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for a given attempt using exponential backoff.
        
        Args:
            attempt: Current attempt number (1-indexed)
        
        Returns:
            Delay in seconds
        """
        # Exponential backoff: base_delay * (exponential_base ^ (attempt - 1))
        delay = self.config.base_delay * (self.config.exponential_base ** (attempt - 1))
        
        # Cap at max delay
        delay = min(delay, self.config.max_delay)
        
        # Add jitter if enabled
        if self.config.jitter:
            import random
            delay = delay * (0.5 + random.random())
        
        return delay
    
    def should_retry(self, exception: Exception, attempt: int) -> bool:
        """Determine if operation should be retried.
        
        Args:
            exception: Exception that occurred
            attempt: Current attempt number
        
        Returns:
            True if should retry, False otherwise
        """
        if attempt >= self.config.max_attempts:
            return False
        
        # Check if exception is retryable
        for retryable_type in self.config.retryable_exceptions:
            if isinstance(exception, retryable_type):
                return True
        
        return False


def retry_with_backoff(
    config: Optional[RetryConfig] = None,
    on_retry: Optional[Callable[[Exception, int], None]] = None
):
    """Decorator for retrying functions with exponential backoff.
    
    Args:
        config: Retry configuration (uses default if None)
        on_retry: Optional callback called before each retry
    
    Returns:
        Decorated function
    """
    if config is None:
        config = RetryConfig()
    
    policy = RetryPolicy(config)
    
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(1, config.max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                
                except Exception as e:
                    last_exception = e
                    
                    if not policy.should_retry(e, attempt):
                        logger.error(f"Operation failed after {attempt} attempts: {e}")
                        raise
                    
                    delay = policy.calculate_delay(attempt)
                    logger.warning(
                        f"Attempt {attempt}/{config.max_attempts} failed: {e}. "
                        f"Retrying in {delay:.2f} seconds..."
                    )
                    
                    # Call on_retry callback if provided
                    if on_retry:
                        on_retry(e, attempt)
                    
                    time.sleep(delay)
            
            # If we get here, all retries failed
            logger.error(f"Operation failed after {config.max_attempts} attempts")
            raise last_exception
        
        return wrapper
    
    return decorator


async def async_retry_with_backoff(
    config: Optional[RetryConfig] = None,
    on_retry: Optional[Callable[[Exception, int], None]] = None
):
    """Decorator for retrying async functions with exponential backoff.
    
    Args:
        config: Retry configuration (uses default if None)
        on_retry: Optional callback called before each retry
    
    Returns:
        Decorated async function
    """
    if config is None:
        config = RetryConfig()
    
    policy = RetryPolicy(config)
    
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(1, config.max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                
                except Exception as e:
                    last_exception = e
                    
                    if not policy.should_retry(e, attempt):
                        logger.error(f"Async operation failed after {attempt} attempts: {e}")
                        raise
                    
                    delay = policy.calculate_delay(attempt)
                    logger.warning(
                        f"Async attempt {attempt}/{config.max_attempts} failed: {e}. "
                        f"Retrying in {delay:.2f} seconds..."
                    )
                    
                    # Call on_retry callback if provided
                    if on_retry:
                        on_retry(e, attempt)
                    
                    await asyncio.sleep(delay)
            
            # If we get here, all retries failed
            logger.error(f"Async operation failed after {config.max_attempts} attempts")
            raise last_exception
        
        return wrapper
    
    return decorator


class RetryTracker:
    """Track retry statistics for monitoring."""
    
    def __init__(self):
        """Initialize retry tracker."""
        self.attempts = 0
        self.successes = 0
        self.failures = 0
        self.total_delay = 0.0
        self.exceptions = {}
    
    def record_attempt(self, delay: float):
        """Record a retry attempt.
        
        Args:
            delay: Delay before this attempt
        """
        self.attempts += 1
        self.total_delay += delay
    
    def record_success(self):
        """Record a successful operation."""
        self.successes += 1
    
    def record_failure(self, exception: Exception):
        """Record a failed operation.
        
        Args:
            exception: Exception that caused failure
        """
        self.failures += 1
        exc_type = type(exception).__name__
        self.exceptions[exc_type] = self.exceptions.get(exc_type, 0) + 1
    
    def get_stats(self) -> dict:
        """Get retry statistics.
        
        Returns:
            Dictionary of statistics
        """
        return {
            'attempts': self.attempts,
            'successes': self.successes,
            'failures': self.failures,
            'success_rate': self.successes / max(self.attempts, 1),
            'total_delay': self.total_delay,
            'average_delay': self.total_delay / max(self.attempts, 1),
            'exceptions': dict(self.exceptions),
        }
    
    def reset(self):
        """Reset tracker statistics."""
        self.attempts = 0
        self.successes = 0
        self.failures = 0
        self.total_delay = 0.0
        self.exceptions = {}
