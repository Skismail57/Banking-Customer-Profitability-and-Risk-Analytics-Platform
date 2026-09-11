"""Segment schemas."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date


class Segment(BaseModel):
    """Segment schema."""
    
    model_config = ConfigDict(from_attributes=True)
    
    segment: str = Field(..., description="Segment name")
    customer_count: int = Field(..., description="Customer count")
    avg_profit: Optional[float] = Field(None, description="Average profit")
    avg_risk_score: Optional[float] = Field(None, description="Average risk score")
    avg_churn_probability: Optional[float] = Field(None, description="Average churn probability")


class SegmentListResponse(BaseModel):
    """Segment list response."""
    
    segments: list[Segment]
    total: int
