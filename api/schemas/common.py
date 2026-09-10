"""Common schemas."""

from pydantic import BaseModel, Field
from typing import Optional, Generic, TypeVar, List
from datetime import datetime


T = TypeVar("T")


class PaginationParams(BaseModel):
    """Pagination parameters."""
    
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(50, ge=1, le=500, description="Number of items per page")
    
    @property
    def offset(self) -> int:
        """Calculate offset."""
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response."""
    
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    class Config:
        arbitrary_types_allowed = True


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str
    version: str
    timestamp: datetime
    database: str


class ErrorResponse(BaseModel):
    """Error response."""
    
    error: str
    message: str
    detail: Optional[str] = None
