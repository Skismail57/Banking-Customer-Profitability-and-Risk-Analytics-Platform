"""Customer schemas."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class CustomerBase(BaseModel):
    """Base customer schema."""
    
    customer_key: str = Field(..., description="Customer unique identifier")
    customer_name: Optional[str] = Field(None, description="Customer name")
    segment: Optional[str] = Field(None, description="Customer segment")
    region: Optional[str] = Field(None, description="Customer region")
    acquisition_date: Optional[date] = Field(None, description="Customer acquisition date")


class Customer(CustomerBase):
    """Customer response schema."""
    
    customer_age: Optional[int] = Field(None, description="Customer age")
    income_level: Optional[str] = Field(None, description="Income level")
    
    class Config:
        from_attributes = True


class CustomerListResponse(BaseModel):
    """Customer list response."""
    
    customers: list[Customer]
    total: int


class CustomerDetail(Customer):
    """Customer detail schema with additional fields."""
    
    net_profit: Optional[float] = Field(None, description="Net profit")
    clv: Optional[float] = Field(None, description="Customer lifetime value")
    risk_level: Optional[str] = Field(None, description="Risk level")
    churn_probability: Optional[float] = Field(None, description="Churn probability")
    exposure_amount: Optional[float] = Field(None, description="Exposure amount")
