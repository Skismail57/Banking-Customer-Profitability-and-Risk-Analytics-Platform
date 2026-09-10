"""Transaction schemas."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class Transaction(BaseModel):
    """Transaction schema."""
    
    transaction_key: str = Field(..., description="Transaction unique identifier")
    customer_key: str = Field(..., description="Customer unique identifier")
    transaction_date: date = Field(..., description="Transaction date")
    amount: float = Field(..., description="Transaction amount")
    product_type: Optional[str] = Field(None, description="Product type")
    transaction_type: Optional[str] = Field(None, description="Transaction type")
    channel: Optional[str] = Field(None, description="Transaction channel")
    
    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    """Transaction list response."""
    
    transactions: list[Transaction]
    total: int
