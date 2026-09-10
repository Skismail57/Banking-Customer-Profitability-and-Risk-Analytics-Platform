"""Recommendation schemas."""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


class Recommendation(BaseModel):
    """Recommendation schema."""
    
    recommendation_key: str = Field(..., description="Recommendation unique identifier")
    customer_key: str = Field(..., description="Customer unique identifier")
    segment: Optional[str] = Field(None, description="Customer segment")
    priority: str = Field(..., description="Priority (critical, high, medium, low)")
    confidence: str = Field(..., description="Confidence level (high, medium, low)")
    recommended_action: str = Field(..., description="Recommended action")
    reason: str = Field(..., description="Reason for recommendation")
    limitations: Optional[List[str]] = Field(None, description="Limitations")
    generated_at: date = Field(..., description="Generation date")
    
    class Config:
        from_attributes = True


class RecommendationListResponse(BaseModel):
    """Recommendation list response."""
    
    recommendations: list[Recommendation]
    total: int
