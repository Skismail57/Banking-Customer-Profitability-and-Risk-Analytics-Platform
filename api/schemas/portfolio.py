"""Portfolio schemas."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class PortfolioSummary(BaseModel):
    """Portfolio summary schema."""
    
    total_customers: int = Field(..., description="Total customers")
    total_exposure: float = Field(..., description="Total exposure")
    total_profit: float = Field(..., description="Total profit")
    avg_risk_score: float = Field(..., description="Average risk score")
    high_risk_exposure: float = Field(..., description="High risk exposure")
    concentration_hhi: Optional[float] = Field(None, description="Concentration HHI")
    as_of_date: date = Field(..., description="As of date")
