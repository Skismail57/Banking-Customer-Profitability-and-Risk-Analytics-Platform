"""Churn schemas."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class CustomerChurn(BaseModel):
    """Customer churn schema."""
    
    customer_key: str = Field(..., description="Customer unique identifier")
    churn_probability: float = Field(..., ge=0, le=1, description="Churn probability")
    clv: Optional[float] = Field(None, description="Customer lifetime value")
    as_of_date: date = Field(..., description="As of date")
    
    class Config:
        from_attributes = True


class ChurnAggregate(BaseModel):
    """Aggregate churn schema."""
    
    avg_churn_probability: float = Field(..., ge=0, le=1, description="Average churn probability")
    high_churn_risk_customers: int = Field(..., description="High churn risk customers (prob > 0.7)")
    retention_rate: float = Field(..., ge=0, le=1, description="Retention rate")
    high_churn_high_clv_count: int = Field(..., description="High churn + high CLV customers")
    customer_count: int = Field(..., description="Total customers")
    as_of_date: date = Field(..., description="As of date")


class ChurnBySegment(BaseModel):
    """Churn by segment schema."""
    
    segment: str = Field(..., description="Segment name")
    avg_churn_probability: float = Field(..., ge=0, le=1, description="Average churn probability")
    high_churn_count: int = Field(..., description="High churn risk customers")
