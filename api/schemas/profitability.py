"""Profitability schemas."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date


class CustomerProfitability(BaseModel):
    """Customer profitability schema."""
    
    model_config = ConfigDict(from_attributes=True)
    
    customer_key: str = Field(..., description="Customer unique identifier")
    net_profit: float = Field(..., description="Net profit")
    risk_adjusted_profit: Optional[float] = Field(None, description="Risk-adjusted profit")
    profit_margin: Optional[float] = Field(None, description="Profit margin")
    as_of_date: date = Field(..., description="As of date")


class ProfitabilityAggregate(BaseModel):
    """Aggregate profitability schema."""
    
    total_net_profit: float = Field(..., description="Total net profit")
    avg_profit_per_customer: float = Field(..., description="Average profit per customer")
    total_risk_adjusted_profit: Optional[float] = Field(None, description="Total risk-adjusted profit")
    profit_margin: Optional[float] = Field(None, description="Profit margin")
    customer_count: int = Field(..., description="Number of customers")
    as_of_date: date = Field(..., description="As of date")


class ProfitabilityBySegment(BaseModel):
    """Profitability by segment schema."""
    
    segment: str = Field(..., description="Segment name")
    total_profit: float = Field(..., description="Total profit")
    avg_profit: float = Field(..., description="Average profit")
    customer_count: int = Field(..., description="Customer count")
