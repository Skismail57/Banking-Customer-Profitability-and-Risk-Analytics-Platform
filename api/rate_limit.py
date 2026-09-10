"""Rate limiting implementation using slowapi."""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException, status
from typing import Callable
import logging

from src.api.config import settings

logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.rate_limit_requests_per_minute}/minute"],
    storage_uri="memory://"  # Use in-memory storage for development
    # TODO: Use Redis for distributed rate limiting in production
    # storage_uri=f"redis://:{settings.redis_password}@{settings.redis_host}:{settings.redis_port}/{settings.redis_db}"
)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> HTTPException:
    """Custom handler for rate limit exceeded.
    
    Args:
        request: Incoming request
        exc: Rate limit exceeded exception
        
    Returns:
        HTTPException with rate limit details
    """
    logger.warning(
        f"Rate limit exceeded for {request.client.host if request.client else 'unknown'}, "
        f"path: {request.url.path}"
    )
    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail={
            "error": "Rate limit exceeded",
            "retry_after": exc.retry_after,
            "limit": exc.limit,
        }
    )


# Override default handler
_rate_limit_exceeded_handler = rate_limit_exceeded_handler


def get_rate_limit_enabled() -> bool:
    """Check if rate limiting is enabled.
    
    Returns:
        True if rate limiting is enabled, False otherwise
    """
    return settings.rate_limit_enabled


def conditional_rate_limit(limit: str):
    """Decorator for conditional rate limiting.
    
    Args:
        limit: Rate limit string (e.g., "5/minute")
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable):
        if get_rate_limit_enabled():
            return limiter.limit(limit)(func)
        return func
    return decorator
