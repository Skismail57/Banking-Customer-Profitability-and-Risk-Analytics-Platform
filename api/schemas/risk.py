"""Risk schemas."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date


class CustomerRisk(BaseModel):
    """Customer risk schema."""
    
    model_config = ConfigDict(from_attributes=True)
    
    customer_key: str = Field(..., description="Customer unique identifier")
    risk_level: str = Field(..., description="Risk level (low, medium, high, critical)")
    risk_trend: Optional[str] = Field(None, description="Risk trend (increasing, decreasing, stable)")
    exposure_amount: float = Field(..., description="Exposure amount")
    credit_utilization: Optional[float] = Field(None, description="Credit utilization")
    days_past_due: Optional[int] = Field(None, description="Days past due")
    credit_score: Optional[int] = Field(None, description="Credit score")
    balance_to_income_ratio: Optional[float] = Field(None, description="Balance to income ratio")
    as_of_date: date = Field(..., description="As of date")


class RiskAggregate(BaseModel):
    """Aggregate risk schema."""
    
    total_customers: int = Field(..., description="Total customers")
    low_risk_count: int = Field(..., description="Low risk customers")
    medium_risk_count: int = Field(..., description="Medium risk customers")
    high_risk_count: int = Field(..., description="High risk customers")
    critical_risk_count: int = Field(..., description="Critical risk customers")
    total_exposure: float = Field(..., description="Total exposure")
    delinquency_rate: Optional[float] = Field(None, description="Delinquency rate")
    avg_utilization: Optional[float] = Field(None, description="Average utilization")
    as_of_date: date = Field(..., description="As of date")


class RiskDistribution(BaseModel):
    """Risk distribution schema."""
    
    risk_level: str = Field(..., description="Risk level")
    count: int = Field(..., description="Customer count")
    exposure: float = Field(..., description="Total exposure")
