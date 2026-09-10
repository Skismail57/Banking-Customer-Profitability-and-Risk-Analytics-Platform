"""Dimension tables for banking analytics warehouse."""

from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    String,
    Integer,
    Numeric,
    Date,
    DateTime,
    Boolean,
    Text,
    Index,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin


class DimCustomer(Base, TimestampMixin):
    """Customer dimension table.
    
    Contains customer demographic and profile information.
    Type 1 SCD (slowly changing dimension) - overwrite on change.
    """
    
    __tablename__ = "dim_customer"
    
    # Surrogate key
    customer_key: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Natural key
    customer_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    
    # Customer demographics
    first_name: Mapped[Optional[str]] = mapped_column(String(100))
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    birth_date: Mapped[Optional[date]] = mapped_column(Date)
    gender: Mapped[Optional[str]] = mapped_column(String(10))
    marital_status: Mapped[Optional[str]] = mapped_column(String(20))
    education_level: Mapped[Optional[str]] = mapped_column(String(50))
    occupation: Mapped[Optional[str]] = mapped_column(String(100))
    annual_income: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Contact information
    email: Mapped[Optional[str]] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    address_line1: Mapped[Optional[str]] = mapped_column(String(255))
    address_line2: Mapped[Optional[str]] = mapped_column(String(255))
    city: Mapped[Optional[str]] = mapped_column(String(100))
    state: Mapped[Optional[str]] = mapped_column(String(50))
    postal_code: Mapped[Optional[str]] = mapped_column(String(20))
    country: Mapped[Optional[str]] = mapped_column(String(50), default="USA")
    
    # Customer status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    customer_since: Mapped[Optional[date]] = mapped_column(Date, index=True)
    churn_date: Mapped[Optional[date]] = mapped_column(Date)
    
    # Segment assignment
    segment_key: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    
    # Real-time analytics fields
    last_realtime_event_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), index=True)
    realtime_risk_level: Mapped[Optional[str]] = mapped_column(String(20), index=True)
    realtime_risk_score: Mapped[Optional[float]] = mapped_column(Numeric(10, 6))
    on_watchlist: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True, server_default='false')
    
    # Metadata
    source_system: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Relationships
    accounts: Mapped[list["DimAccount"]] = relationship(
        "DimAccount", back_populates="customer", cascade="all, delete-orphan"
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint("annual_income >= 0", name="ck_customer_annual_income_non_negative"),
        CheckConstraint("birth_date <= current_date", name="ck_customer_birth_date_valid"),
        CheckConstraint("realtime_risk_level IN ('low', 'medium', 'high', 'critical') OR realtime_risk_level IS NULL", 
                       name="ck_customer_realtime_risk_level"),
        CheckConstraint("realtime_risk_score BETWEEN 0 AND 1 OR realtime_risk_score IS NULL", 
                       name="ck_customer_realtime_risk_score"),
        Index("ix_customer_name", "last_name", "first_name"),
        Index("ix_customer_location", "city", "state"),
        Index("ix_customer_realtime_risk_level", "realtime_risk_level"),
        Index("ix_customer_on_watchlist", "on_watchlist"),
        Index("ix_customer_last_realtime_event_time", "last_realtime_event_time"),
    )


class DimAccount(Base, TimestampMixin):
    """Account dimension table.
    
    Contains account-level information and relationships to customers and products.
    Type 1 SCD - overwrite on change.
    """
    
    __tablename__ = "dim_account"
    
    # Surrogate key
    account_key: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Natural key
    account_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    
    # Foreign keys
    customer_key: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    customer_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    product_key: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    branch_key: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    
    # Account details
    account_type: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    account_subtype: Mapped[Optional[str]] = mapped_column(String(50))
    currency: Mapped[Optional[str]] = mapped_column(String(3), default="INR")
    
    # Account status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    opened_date: Mapped[Optional[date]] = mapped_column(Date, index=True)
    closed_date: Mapped[Optional[date]] = mapped_column(Date)
    closure_reason: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Account limits
    credit_limit: Mapped[Optional[int]] = mapped_column(Integer)
    overdraft_limit: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Metadata
    source_system: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Relationships
    customer: Mapped["DimCustomer"] = relationship("DimCustomer", back_populates="accounts")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("credit_limit >= 0", name="ck_account_credit_limit_non_negative"),
        CheckConstraint("overdraft_limit >= 0", name="ck_account_overdraft_limit_non_negative"),
        Index("ix_account_customer_product", "customer_key", "product_key"),
    )


class DimProduct(Base, TimestampMixin):
    """Product dimension table.
    
    Contains banking product information (savings, checking, loans, credit cards, etc.).
    Type 1 SCD - overwrite on change.
    """
    
    __tablename__ = "dim_product"
    
    # Surrogate key
    product_key: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Natural key
    product_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    
    # Product classification
    product_category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    product_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    product_name: Mapped[str] = mapped_column(String(100), nullable=False)
    product_code: Mapped[Optional[str]] = mapped_column(String(20), unique=True)
    
    # Product attributes
    interest_rate: Mapped[Optional[float]] = mapped_column(Numeric(5, 4))
    annual_fee: Mapped[Optional[int]] = mapped_column(Integer)
    minimum_balance: Mapped[Optional[int]] = mapped_column(Integer)
    term_months: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Product status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    effective_date: Mapped[Optional[date]] = mapped_column(Date)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date)
    
    # Metadata
    description: Mapped[Optional[str]] = mapped_column(Text)
    source_system: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Constraints
    __table_args__ = (
        CheckConstraint("interest_rate >= 0", name="ck_product_interest_rate_non_negative"),
        CheckConstraint("annual_fee >= 0", name="ck_product_annual_fee_non_negative"),
        CheckConstraint("minimum_balance >= 0", name="ck_product_minimum_balance_non_negative"),
        CheckConstraint("term_months >= 0", name="ck_product_term_months_non_negative"),
        Index("ix_product_category_type", "product_category", "product_type"),
    )


class DimBranch(Base, TimestampMixin):
    """Branch dimension table.
    
    Contains physical branch location information.
    Type 1 SCD - overwrite on change.
    """
    
    __tablename__ = "dim_branch"
    
    # Surrogate key
    branch_key: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Natural key
    branch_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    
    # Branch identification
    branch_name: Mapped[str] = mapped_column(String(100), nullable=False)
    branch_code: Mapped[Optional[str]] = mapped_column(String(20), unique=True)
    
    # Location information
    address_line1: Mapped[Optional[str]] = mapped_column(String(255))
    address_line2: Mapped[Optional[str]] = mapped_column(String(255))
    city: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    state: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(20))
    country: Mapped[Optional[str]] = mapped_column(String(50), default="USA")
    
    # Geographic coordinates
    latitude: Mapped[Optional[float]] = mapped_column(Numeric(10, 8))
    longitude: Mapped[Optional[float]] = mapped_column(Numeric(11, 8))
    
    # Branch status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    opened_date: Mapped[Optional[date]] = mapped_column(Date)
    closed_date: Mapped[Optional[date]] = mapped_column(Date)
    
    # Branch attributes
    branch_type: Mapped[Optional[str]] = mapped_column(String(50))
    atm_count: Mapped[Optional[int]] = mapped_column(Integer)
    employee_count: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Region classification
    region: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    district: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Metadata
    source_system: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Constraints
    __table_args__ = (
        CheckConstraint("latitude >= -90 AND latitude <= 90", name="ck_branch_latitude_valid"),
        CheckConstraint("longitude >= -180 AND longitude <= 180", name="ck_branch_longitude_valid"),
        CheckConstraint("atm_count >= 0", name="ck_branch_atm_count_non_negative"),
        CheckConstraint("employee_count >= 0", name="ck_branch_employee_count_non_negative"),
        Index("ix_branch_location", "city", "state", "country"),
    )


class DimDate(Base):
    """Date dimension table.
    
    Pre-populated calendar dimension for time-based analysis.
    Contains one row per day.
    """
    
    __tablename__ = "dim_date"
    
    # Primary key
    date_key: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    
    # Date attributes
    full_date: Mapped[date] = mapped_column(Date, unique=True, nullable=False, index=True)
    
    # Date components
    day_of_month: Mapped[int] = mapped_column(Integer, nullable=False)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-7 (Monday=1)
    day_of_year: Mapped[int] = mapped_column(Integer, nullable=False)
    week_of_year: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    quarter: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    
    # Date names
    day_name: Mapped[str] = mapped_column(String(10), nullable=False)
    month_name: Mapped[str] = mapped_column(String(15), nullable=False)
    quarter_name: Mapped[str] = mapped_column(String(10), nullable=False)
    
    # Weekend and holiday flags
    is_weekend: Mapped[bool] = mapped_column(Boolean, nullable=False, index=True)
    is_holiday: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    holiday_name: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Fiscal calendar
    fiscal_year: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    fiscal_quarter: Mapped[Optional[int]] = mapped_column(Integer)
    fiscal_month: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Season classification
    season: Mapped[Optional[str]] = mapped_column(String(15))
    
    # Constraints
    __table_args__ = (
        CheckConstraint("day_of_month BETWEEN 1 AND 31", name="ck_date_day_of_month_valid"),
        CheckConstraint("day_of_week BETWEEN 1 AND 7", name="ck_date_day_of_week_valid"),
        CheckConstraint("month BETWEEN 1 AND 12", name="ck_date_month_valid"),
        CheckConstraint("quarter BETWEEN 1 AND 4", name="ck_date_quarter_valid"),
        Index("ix_date_year_quarter", "year", "quarter"),
        Index("ix_date_year_month", "year", "month"),
    )


class DimCustomerSegment(Base, TimestampMixin):
    """Customer segment dimension table.
    
    Contains customer segment definitions and attributes.
    Type 2 SCD (slowly changing dimension) - track history with effective dates.
    """
    
    __tablename__ = "dim_customer_segment"
    
    # Surrogate key
    segment_key: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Natural key
    segment_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    
    # Segment identification
    segment_name: Mapped[str] = mapped_column(String(100), nullable=False)
    segment_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # value, behavior, risk, lifecycle
    
    # Segment classification
    segment_category: Mapped[Optional[str]] = mapped_column(String(50))
    segment_tier: Mapped[Optional[str]] = mapped_column(String(20))  # platinum, gold, silver, bronze
    
    # Segment attributes
    min_balance: Mapped[Optional[int]] = mapped_column(Integer)
    max_balance: Mapped[Optional[int]] = mapped_column(Integer)
    min_transactions: Mapped[Optional[int]] = mapped_column(Integer)
    max_transactions: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Risk profile
    risk_level: Mapped[Optional[str]] = mapped_column(String(20))  # low, medium, high
    credit_score_min: Mapped[Optional[int]] = mapped_column(Integer)
    credit_score_max: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Profitability profile
    profitability_tier: Mapped[Optional[str]] = mapped_column(String(20))
    avg_profitability: Mapped[Optional[int]] = mapped_column(Integer)
    
    # SCD Type 2 attributes
    effective_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date, index=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    
    # Segment description
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Metadata
    source_system: Mapped[Optional[str]] = mapped_column(String(50))
    created_by: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Constraints
    __table_args__ = (
        CheckConstraint("min_balance >= 0", name="ck_segment_min_balance_non_negative"),
        CheckConstraint("max_balance >= 0", name="ck_segment_max_balance_non_negative"),
        CheckConstraint("min_transactions >= 0", name="ck_segment_min_transactions_non_negative"),
        CheckConstraint("max_transactions >= 0", name="ck_segment_max_transactions_non_negative"),
        CheckConstraint("credit_score_min BETWEEN 300 AND 850", name="ck_segment_credit_score_min_valid"),
        CheckConstraint("credit_score_max BETWEEN 300 AND 850", name="ck_segment_credit_score_max_valid"),
        CheckConstraint("effective_date <= COALESCE(expiry_date, '9999-12-31'::date)", 
                       name="ck_segment_effective_before_expiry"),
        Index("ix_segment_type_current", "segment_type", "is_current"),
    )
