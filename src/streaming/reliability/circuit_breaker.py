"""Circuit breaker pattern for fault tolerance in streaming operations.

This module implements the circuit breaker pattern to prevent cascading
failures by temporarily disabling failing operations.
"""

import time
import logging
from typing import Optional, Callable
from dataclasses import dataclass
from enum import Enum
from functools import wraps

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Circuit is open, calls fail immediately
    HALF_OPEN = "half_open"  # Testing if service has recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5
    success_threshold: int = 2
    timeout: float = 60.0  # Time in seconds before attempting recovery
    half_open_timeout: float = 30.0  # Time in seconds for half-open state
    expected_exception: Optional[type] = None


class CircuitBreaker:
    """Circuit breaker for protecting against cascading failures."""
    
    def __init__(self, config: Optional[CircuitBreakerConfig] = None):
        """Initialize circuit breaker.
        
        Args:
            config: Circuit breaker configuration
        """
        self.config = config or CircuitBreakerConfig()
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = 0.0
        self._state_change_time = time.time()
        self._lock = type('Lock', (), {'acquire': lambda self: None, 'release': lambda self: None})()
    
    def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection.
        
        Args:
            func: Function to call
            *args: Function arguments
            **kwargs: Function keyword arguments
        
        Returns:
            Function result
        
        Raises:
            CircuitOpenError: If circuit is open
        """
        if not self.allow_request():
            raise CircuitOpenError(f"Circuit breaker is {self._state.value}")
        
        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        
        except Exception as e:
            if self.config.expected_exception is None or isinstance(e, self.config.expected_exception):
                self.on_failure()
            raise
    
    def allow_request(self) -> bool:
        """Check if request is allowed based on circuit state.
        
        Returns:
            True if request allowed, False otherwise
        """
        current_time = time.time()
        
        if self._state == CircuitState.CLOSED:
            return True
        
        elif self._state == CircuitState.OPEN:
            # Check if timeout has elapsed
            if current_time - self._state_change_time >= self.config.timeout:
                self._transition_to(CircuitState.HALF_OPEN)
                logger.info("Circuit breaker transitioning to HALF_OPEN")
                return True
            return False
        
        elif self._state == CircuitState.HALF_OPEN:
            # Allow limited requests in half-open state
            return True
        
        return False
    
    def on_success(self):
        """Record successful operation."""
        if self._state == CircuitState.HALF_OPEN:
            self._success_count += 1
            
            if self._success_count >= self.config.success_threshold:
                self._transition_to(CircuitState.CLOSED)
                self._success_count = 0
                logger.info("Circuit breaker transitioning to CLOSED")
        
        elif self._state == CircuitState.CLOSED:
            self._failure_count = 0
    
    def on_failure(self):
        """Record failed operation."""
        self._failure_count += 1
        self._last_failure_time = time.time()
        
        if self._state == CircuitState.HALF_OPEN:
            self._transition_to(CircuitState.OPEN)
            self._success_count = 0
            logger.warning("Circuit breaker transitioning to OPEN (half-open failed)")
        
        elif self._state == CircuitState.CLOSED:
            if self._failure_count >= self.config.failure_threshold:
                self._transition_to(CircuitState.OPEN)
                logger.warning(f"Circuit breaker transitioning to OPEN (failures: {self._failure_count})")
    
    def _transition_to(self, new_state: CircuitState):
        """Transition to new state.
        
        Args:
            new_state: New circuit state
        """
        self._state = new_state
        self._state_change_time = time.time()
    
    def get_state(self) -> CircuitState:
        """Get current circuit state.
        
        Returns:
            Current circuit state
        """
        return self._state
    
    def get_stats(self) -> dict:
        """Get circuit breaker statistics.
        
        Returns:
            Dictionary of statistics
        """
        return {
            'state': self._state.value,
            'failure_count': self._failure_count,
            'success_count': self._success_count,
            'last_failure_time': self._last_failure_time,
            'state_change_time': self._state_change_time,
            'time_in_state': time.time() - self._state_change_time,
        }
    
    def reset(self):
        """Reset circuit breaker to closed state."""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = 0.0
        self._state_change_time = time.time()
        logger.info("Circuit breaker reset to CLOSED")


class CircuitOpenError(Exception):
    """Exception raised when circuit is open."""
    pass


def circuit_breaker(
    config: Optional[CircuitBreakerConfig] = None,
    on_open: Optional[Callable] = None,
    on_close: Optional[Callable] = None
):
    """Decorator for circuit breaker protection.
    
    Args:
        config: Circuit breaker configuration
        on_open: Callback when circuit opens
        on_close: Callback when circuit closes
    
    Returns:
        Decorated function
    """
    breaker = CircuitBreaker(config)
    previous_state = breaker.get_state()
    
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal previous_state
            
            try:
                result = breaker.call(func, *args, **kwargs)
                
                # Check for state change to closed
                current_state = breaker.get_state()
                if previous_state != CircuitState.CLOSED and current_state == CircuitState.CLOSED:
                    if on_close:
                        on_close()
                previous_state = current_state
                
                return result
            
            except CircuitOpenError as e:
                # Check for state change to open
                current_state = breaker.get_state()
                if previous_state != CircuitState.OPEN and current_state == CircuitState.OPEN:
                    if on_open:
                        on_open()
                previous_state = current_state
                raise
        
        # Attach circuit breaker to function for inspection
        wrapper._circuit_breaker = breaker
        
        return wrapper
    
    return decorator


class CircuitBreakerRegistry:
    """Registry for managing multiple circuit breakers."""
    
    def __init__(self):
        """Initialize circuit breaker registry."""
        self._breakers = {}
    
    def register(self, name: str, breaker: CircuitBreaker):
        """Register a circuit breaker.
        
        Args:
            name: Circuit breaker name
            breaker: Circuit breaker instance
        """
        self._breakers[name] = breaker
        logger.info(f"Registered circuit breaker: {name}")
    
    def get(self, name: str) -> Optional[CircuitBreaker]:
        """Get circuit breaker by name.
        
        Args:
            name: Circuit breaker name
        
        Returns:
            Circuit breaker instance or None if not found
        """
        return self._breakers.get(name)
    
    def remove(self, name: str) -> bool:
        """Remove circuit breaker by name.
        
        Args:
            name: Circuit breaker name
        
        Returns:
            True if removed, False if not found
        """
        if name in self._breakers:
            del self._breakers[name]
            logger.info(f"Removed circuit breaker: {name}")
            return True
        return False
    
    def get_all_stats(self) -> dict:
        """Get statistics for all circuit breakers.
        
        Returns:
            Dictionary mapping name to statistics
        """
        return {name: breaker.get_stats() for name, breaker in self._breakers.items()}
    
    def reset_all(self):
        """Reset all circuit breakers."""
        for name, breaker in self._breakers.items():
            breaker.reset()
        logger.info("Reset all circuit breakers")
    
    def get_open_breakers(self) -> list:
        """Get list of currently open circuit breakers.
        
        Returns:
            List of circuit breaker names
        """
        return [name for name, breaker in self._breakers.items() 
                if breaker.get_state() == CircuitState.OPEN]
