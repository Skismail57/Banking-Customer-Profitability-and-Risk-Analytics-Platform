"""Secure error handling for API."""

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import logging
import traceback

logger = logging.getLogger(__name__)


class SecurityHTTPException(HTTPException):
    """HTTP exception with secure error handling."""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        correlation_id: Optional[str] = None
    ):
        """Initialize secure HTTP exception.
        
        Args:
            status_code: HTTP status code
            detail: Error detail (safe to expose)
            correlation_id: Correlation ID for tracing
        """
        super().__init__(status_code=status_code, detail=detail)
        self.correlation_id = correlation_id


async def security_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions securely.
    
    Args:
        request: FastAPI request
        exc: HTTP exception
        
    Returns:
        JSON response with secure error details
    """
    correlation_id = request.state.correlation_id if hasattr(request.state, 'correlation_id') else None
    
    # Log the full error for debugging
    logger.error(
        f"HTTP Exception: {exc.status_code} | "
        f"Detail: {exc.detail} | "
        f"Path: {request.url.path} | "
        f"Correlation ID: {correlation_id}"
    )
    
    # Return safe error details to client
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "correlation_id": correlation_id
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle generic exceptions securely.
    
    Args:
        request: FastAPI request
        exc: Generic exception
        
    Returns:
        JSON response with generic error details
    """
    correlation_id = request.state.correlation_id if hasattr(request.state, 'correlation_id') else None
    
    # Log the full error with traceback for debugging
    logger.error(
        f"Unhandled Exception: {type(exc).__name__} | "
        f"Path: {request.url.path} | "
        f"Correlation ID: {correlation_id}",
        exc_info=True
    )
    
    # Return generic error to client (no stack traces or internal details)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "correlation_id": correlation_id
        }
    )


def get_safe_error_response(
    status_code: int,
    detail: str,
    correlation_id: Optional[str] = None
) -> Dict[str, Any]:
    """Get safe error response.
    
    Args:
        status_code: HTTP status code
        detail: Error detail
        correlation_id: Correlation ID
        
    Returns:
        Safe error response dictionary
    """
    return {
        "detail": detail,
        "correlation_id": correlation_id
    }
