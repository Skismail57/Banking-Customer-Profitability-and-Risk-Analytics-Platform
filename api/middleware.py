"""Security middleware for FastAPI application."""

from fastapi import Request, Response
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.gzip import GZipMiddleware
import logging
import uuid
from typing import Callable

from api.config import settings

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response.
        
        Args:
            request: Incoming request
            call_next: Next middleware or route handler
            
        Returns:
            Response with security headers
        """
        response = await call_next(request)
        
        # HSTS (HTTP Strict Transport Security)
        if settings.environment == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # X-Content-Type-Options
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # X-Frame-Options
        response.headers["X-Frame-Options"] = "DENY"
        
        # Content-Security-Policy (skip in development for Swagger UI)
        if settings.environment == "production":
            # Strict CSP for production
            csp = "default-src 'self'; script-src 'self'; style-src 'self'; object-src 'none';"
            response.headers["Content-Security-Policy"] = csp
        
        # Referrer-Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions-Policy
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # X-XSS-Protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        return response


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Middleware to add correlation ID to requests for tracing."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add correlation ID to request and response.
        
        Args:
            request: Incoming request
            call_next: Next middleware or route handler
            
        Returns:
            Response with correlation ID header
        """
        # Get correlation ID from header or generate new one
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        
        # Add to request state
        request.state.correlation_id = correlation_id
        
        # Process request
        response = await call_next(request)
        
        # Add correlation ID to response header
        response.headers["X-Correlation-ID"] = correlation_id
        
        return response


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to limit request body size."""
    
    def __init__(self, app, max_size: int = 10 * 1024 * 1024):  # 10MB default
        """Initialize middleware.
        
        Args:
            app: ASGI application
            max_size: Maximum request body size in bytes
        """
        super().__init__(app)
        self.max_size = max_size
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check request body size before processing.
        
        Args:
            request: Incoming request
            call_next: Next middleware or route handler
            
        Returns:
            Response or error if request too large
        """
        content_length = request.headers.get("content-length")
        
        if content_length:
            try:
                size = int(content_length)
                if size > self.max_size:
                    logger.warning(
                        f"Request too large: {size} bytes (max: {self.max_size}), "
                        f"correlation_id: {request.state.correlation_id if hasattr(request.state, 'correlation_id') else 'unknown'}"
                    )
                    from fastapi import HTTPException, status
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"Request body too large (max {self.max_size} bytes)"
                    )
            except ValueError:
                pass  # Invalid content-length, let the request proceed
        
        return await call_next(request)


def get_security_middleware() -> list[Middleware]:
    """Get list of security middleware for FastAPI application.
    
    Returns:
        List of middleware
    """
    middleware = []
    
    # Security headers
    middleware.append(Middleware(SecurityHeadersMiddleware))
    
    # Correlation ID
    middleware.append(Middleware(CorrelationIdMiddleware))
    
    # Request size limit (10MB)
    middleware.append(Middleware(RequestSizeLimitMiddleware, max_size=10 * 1024 * 1024))
    
    # GZip compression
    middleware.append(Middleware(GZipMiddleware, minimum_size=1000))
    
    # Trusted hosts (in production)
    if settings.environment == "production":
        # TODO: Add actual trusted hosts from configuration
        # middleware.append(Middleware(TrustedHostMiddleware, allowed_hosts=["*.banking.local"]))
        pass
    
    return middleware
