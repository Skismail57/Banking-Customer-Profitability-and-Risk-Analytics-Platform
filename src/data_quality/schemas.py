"""Pandera schemas for dimension and fact tables."""

import pandera as pa
from pandera.typing import DataFrame, Series
from datetime import datetime
import logging

from src.data_quality.base import BaseSchema, CustomCheck

logger = logging.getLogger(__name__)


# ============================================================================
# DIMENSION TABLE SCHEMAS
# ============================================================================

class DimCustomerSchema(BaseSchema):
    """Schema for dim_customer table.
    
    Validation Rules:
    - customer_id: Required, unique, non-null string
    - first_name, last_name: Optional strings
    - birth_date: Optional date, must be in past, not in future
    - annual_income: Non-negative integer
    - is_active: Required boolean
    - customer_since: Optional date, not in future
    - churn_date: Optional date, must be >= customer_since if both present
    """
    
    customer_id: Series[str] = pa.Field(
        nullable=False,
        unique=True,
        description="Unique customer identifier"
    )
    
    first_name: Series[str] = pa.Field(
        nullable=True,
        description="Customer first name"
    )
    
    last_name: Series[str] = pa.Field(
        nullable=True,
        description="Customer last name"
    )
    
    birth_date: Series[datetime] = pa.Field(
        nullable=True,
        checks=[
            pa.Check(CustomCheck.not_future_date, error="Birth date cannot be in future"),
            pa.Check(CustomCheck.not_past_date, years=120, error="Birth date cannot be more than 120 years ago")
        ],
        description="Customer date of birth"
    )
    
    annual_income: Series[int] = pa.Field(
        nullable=True,
        checks=[
            pa.Check(CustomCheck.non_negative, error="Annual income must be non-negative")
        ],
        description="Annual income amount"
    )
    
    is_active: Series[bool] = pa.Field(
        nullable=False,
        description="Customer active status"
    )
    
    customer_since: Series[datetime] = pa.Field(
        nullable=True,
        checks=[
            pa.Check(CustomCheck.not_future_date, error="Customer since date cannot be in future")
        ],
        description="Customer onboarding date"
    )
    
    churn_date: Series[datetime] = pa.Field(
        nullable=True,
        description="Customer churn date"
    )
    
    class Config:
        """Schema configuration."""
        strict = True
        coerce = True


class DimAccountSchema(BaseSchema):
    """Schema for dim_account table.
    
    Validation Rules:
    - account_id: Required, unique, non-null string
    - customer_key: Required non-null integer
    - customer_id: Required non-null string
    - product_key: Required non-null integer
    - credit_limit: Non-negative integer
    - overdraft_limit: Non-negative integer
    - opened_date: Optional date, not in future
    - closed_date: Optional date, must be >= opened_date if both present
    - is_active: Required boolean
    """
    
    account_id: Series[str] = pa.Field(
        nullable=False,
        unique=True,
        description="Unique account identifier"
    )
    
    customer_key: Series[int] = pa.Field(
        nullable=False,
        description="Foreign key to dim_customer"
    )
    
    customer_id: Series[str] = pa.Field(
        nullable=False,
        description="Customer identifier"
    )
    
    product_key: Series[int] = pa.Field(
        nullable=False,
        description="Foreign key to dim_product"
    )
    
    credit_limit: Series[int] = pa.Field(
        nullable=True,
        checks=[
            pa.Check(CustomCheck.non_negative, error="Credit limit must be non-negative")
        ],
        description="Account credit limit"
    )
    
    overdraft_limit: Series[int] = pa.Field(
        nullable=True,
        checks=[
            pa.Check(CustomCheck.non_negative, error="Overdraft limit must be non-negative")
        ],
        description="Account overdraft limit"
    )
    
    is_active: Series[bool] = pa.Field(
        nullable=False,
        description="Account active status"
    )
    
    opened_date: Series[datetime] = pa.Field(
        nullable=True,
        checks=[
            pa.Check(CustomCheck.not_future_date, error="Opened date cannot be in future")
        ],
        description="Account opening date"
    )
    
    closed_date: Series[datetime] = pa.Field(
        nullable=True,
        description="Account closing date"
    )
    
    class Config:
        strict = True
        coerce = True


class DimProductSchema(BaseSchema):
    """Schema for dim_product table.
    
    Validation Rules:
    - product_id: Required, unique, non-null string
    - product_category: Required non-null string
    - product_type: Required non-null string
    - product_name: Required non-null string
    - interest_rate: Non-negative float
    - annual_fee: Non-negative integer
    - minimum_balance: Non-negative integer
    - term_months: Non-negative integer
    - is_active: Required boolean
    """
    
    product_id: Series[str] = pa.Field(
        nullable=False,
        unique=True,
        description="Unique product identifier"
    )
    
    product_category: Series[str] = pa.Field(
        nullable=False,
        description="Product category (deposits, loans, cards)"
    )
    
    product_type: Series[str] = pa.Field(
        nullable=False,
        description="Product type"
    )
    
    product_name: Series[str] = pa.Field(
        nullable=False,
        description="Product display name"
    )
    
    interest_rate: Series[float] = pa.Field(
        nullable=True,
        checks=[
            pa.Check(CustomCheck.non_negative, error="Interest rate must be non-negative")
        ],
        description="Annual interest rate"
    )
    
    annual_fee: Series[int] = pa.Field(
        nullable=True,
        checks=[
            pa.Check(CustomCheck.non_negative, error="Annual fee must be non-negative")
        ],
        description="Annual fee amount"
    )
    
    minimum_balance: Series[int] = pa.Field(
        nullable=True,
        checks=[
            pa.Check(CustomCheck.non_negative, error="Minimum balance must be non-negative")
        ],
        description="Minimum balance requirement"
    )
    
    term_months: Series[int] = pa.Field(
        nullable=True,
        checks=[
            pa.Check(CustomCheck.non_negative, error="Term months must be non-negative")
        ],
        description="Loan term in months"
    )
    
    is_active: Series[bool] = pa.Field(
        nullable=False,
        description="Product active status"
    )
    
    class Config:
        strict = True
        coerce = True


class DimBranchSchema(BaseSchema):
    """Schema for dim_branch table.
    
    Validation Rules:
    - branch_id: Required, unique, non-null string
    - branch_name: Required non-null string
    - latitude: Between -90 and 90
    - longitude: Between -180 and 180
    - atm_count: Non-negative integer
    - employee_count: Non-negative integer
    - is_active: Required boolean
    """
    
    branch_id: Series[str] = pa.Field(
        nullable=False,
        unique=True,
        description="Unique branch identifier"
    )
    
    branch_name: Series[str] = pa.Field(
        nullable=False,
        description="Branch display name"
    )
    
    latitude: Series[float] = pa.Field(
        nullable=True,
        checks=[
            pa.Check(CustomCheck.in_range, min_val=-90, max_val=90, 
                   error="Latitude must be between -90 and 90")
        ],
        description="Branch latitude"
    )
    
    longitude: Series[float] = pa.Field(
        nullable=True,
        checks=[
            pa.Check(CustomCheck.in_range, min_val=-180, max_val=180,
                   error="Longitude must be between -180 and 180")
        ],
        description="Branch longitude"
    )
    
    atm_count: Series[int] = pa.Field(
        nullable=True,
        checks=[
            pa.Check(CustomCheck.non_negative, error="ATM count must be non-negative")
        ],
        description="Number of ATMs at branch"
    )
    
    employee_count: Series[int] = pa.Field(
        nullable=True,
        checks=[
            pa.Check(CustomCheck.non_negative, error="Employee count must be non-negative")
        ],
        description="Number of employees at branch"
    )
    
    is_active: Series[bool] = pa.Field(
        nullable=False,
        description="Branch active status"
    )
    
    class Config:
        strict = True
        coerce = True


class DimDateSchema(BaseSchema):
    """Schema for dim_date table.
    
    Validation Rules:
    - date_key: Required, unique, non-null integer
    - full_date: Required, unique, non-null date
    - day_of_month: Between 1 and 31
    - day_of_week: Between 1 and 7
    - month: Between 1 and 12
    - quarter: Between 1 and 4
    - year: Reasonable year range
    """
    
    date_key: Series[int] = pa.Field(
        nullable=False,
        unique=True,
        description="Date key in YYYYMMDD format"
    )
    
    full_date: Series[datetime] = pa.Field(
        nullable=False,
        unique=True,
        description="Full date value"
    )
    
    day_of_month: Series[int] = pa.Field(
        nullable=False,
        checks=[
            pa.Check(CustomCheck.in_range, min_val=1, max_val=31,
                   error="Day of month must be between 1 and 31")
        ],
        description="Day of month (1-31)"
    )
    
    day_of_week: Series[int] = pa.Field(
        nullable=False,
        checks=[
            pa.Check(CustomCheck.in_range, min_val=1, max_val=7,
                   error="Day of week must be between 1 and 7")
        ],
        description="Day of week (1-7, Monday=1)"
    )
    
    month: Series[int] = pa.Field(
        nullable=False,
        checks=[
            pa.Check(CustomCheck.in_range, min_val=1, max_val=12,
                   error="Month must be between 1 and 12")
        ],
        description="Month (1-12)"
    )
    
    quarter: Series[int] = pa.Field(
        nullable=False,
        checks=[
            pa.Check(CustomCheck.in_range, min_val=1, max_val=4,
                   error="Quarter must be between 1 and 4")
        ],
        description="Quarter (1-4)"
    )
    
    year: Series[int] = pa.Field(
        nullable=False,
        checks=[
            pa.Check(CustomCheck.in_range, min_val=1900, max_val=2100,
                   error="Year must be reasonable")
        ],
        description="Year"
    )
    
    class Config:
        strict = True
        coerce = True


class DimCustomerSegmentSchema(BaseSchema):
    """Schema for dim_customer_segment table.
    
    Validation Rules:
    - segment_id: Required, unique, non-null string
    - segment_name: Required non-null string
    - segment_type: Required non-null string
    - min_balance, max_balance: Non-negative integers
    - min_transactions, max_transactions: Non-negative integers
    - credit_score_min, credit_score_max: Between 300 and 850
    - effective_date: Required date
    - expiry_date: Optional date, must be >= effective_date
    - is_current: Required boolean
    """
    
    segment_id: Series[str] = pa.Field(
        nullable=False,
        unique=True,
        description="Unique segment identifier"
    )
    
    segment_name: Series[str] = pa.Field(
        nullable=False,
        description="Segment display name"
    )
    
    segment_type: Series[str] = pa.Field(
        nullable=False,
        description="Segment type (value, behavior, risk, lifecycle)"
    )
    
    min_balance: Series[int] = pa.Field(
        nullable=True,
        checks=[
            pa.Check(CustomCheck.non_negative, error="Min balance must be non-negative")
        ],
        description="Minimum balance for segment"
    )
    
    max_balance: Series[int] = pa.Field(
        nullable=True,
        checks=[
            pa.Check(CustomCheck.non_negative, error="Max balance must be non-negative")
        ],
        description="Maximum balance for segment"
    )
    
    credit_score_min: Series[int] = pa.Field(
        nullable=True,
        checks=[
            pa.Check(CustomCheck.valid_credit_score, error="Credit score min must be 300-850")
        ],
        description="Minimum credit score for segment"
    )
    
    credit_score_max: Series[int] = pa.Field(
        nullable=True,
        checks=[
            pa.Check(CustomCheck.valid_credit_score, error="Credit score max must be 300-850")
        ],
        description="Maximum credit score for segment"
    )
    
    effective_date: Series[datetime] = pa.Field(
        nullable=False,
        description="Segment effective date"
    )
    
    expiry_date: Series[datetime] = pa.Field(
        nullable=True,
        description="Segment expiry date"
    )
    
    is_current: Series[bool] = pa.Field(
        nullable=False,
        description="Current record flag"
    )
    
    class Config:
        strict = True
        coerce = True


# ============================================================================
# FACT TABLE SCHEMAS
# ============================================================================

class FactTransactionSchema(BaseSchema):
    """Schema for fact_transaction table.
    
    Validation Rules:
    - transaction_id: Required, unique, non-null string
    - account_key, customer_key, product_key, date_key: Required non-null integers
    - amount: Non-zero numeric
    - transaction_date: Required datetime
    - fraud_score: Between 0 and 1 if present
    """
    
    transaction_id: Series[str] = pa.Field(
        nullable=False,
        unique=True,
        description="Unique transaction identifier"
    )
    
    account_key: Series[int] = pa.Field(
        nullable=False,
        description="Foreign key to dim_account"
    )
    
    customer_key: Series[int] = pa.Field(
        nullable=False,
        description="Foreign key to dim_customer"
    )
    
    product_key: Series[int] = pa.Field(
        nullable=False,
        description="Foreign key to dim_product"
    )
    
    date_key: Series[int] = pa.Field(
        nullable=False,
        description="Foreign key to dim_date"
    )
    
    amount: Series[float] = pa.Field(
        nullable=False,
        checks=[
            pa.Check(lambda x: x != 0, error="Transaction amount cannot be zero")
        ],
        description="Transaction amount"
    )
    
    transaction_date: Series[datetime] = pa.Field(
        nullable=False,
        description="Transaction timestamp"
    )
    
    fraud_score: Series[float] = pa.Field(
        nullable=True,
        checks=[
            pa.Check(CustomCheck.valid_rate, error="Fraud score must be between 0 and 1")
        ],
        description="Fraud detection score"
    )
    
    class Config:
        strict = True
        coerce = True


class FactLoanSchema(BaseSchema):
    """Schema for fact_loan table.
    
    Validation Rules:
    - loan_id: Required, unique, non-null string
    - customer_key, product_key, origination_date_key, maturity_date_key: Required
    - principal_amount: Positive numeric
    - interest_rate: Non-negative numeric
    - term_months: Positive integer
    - credit_score_at_origination: Between 300 and 850 if present
    - days_past_due: Non-negative integer
    - origination_date: Required date
    - maturity_date: Required date, must be >= origination_date
    """
    
    loan_id: Series[str] = pa.Field(
        nullable=False,
        unique=True,
        description="Unique loan identifier"
    )
    
    customer_key: Series[int] = pa.Field(
        nullable=False,
        description="Foreign key to dim_customer"
    )
    
    product_key: Series[int] = pa.Field(
        nullable=False,
        description="Foreign key to dim_product"
    )
    
    origination_date_key: Series[int] = pa.Field(
        nullable=False,
        description="Foreign key to dim_date for origination"
    )
    
    maturity_date_key: Series[int] = pa.Field(
        nullable=False,
        description="Foreign key to dim_date for maturity"
    )
    
    principal_amount: Series[float] = pa.Field(
        nullable=False,
        checks=[
            pa.Check(CustomCheck.positive, error="Principal amount must be positive")
        ],
        description="Loan principal amount"
    )
    
    interest_rate: Series[float] = pa.Field(
        nullable=False,
        checks=[
            pa.Check(CustomCheck.non_negative, error="Interest rate must be non-negative")
        ],
        description="Loan interest rate"
    )
    
    term_months: Series[int] = pa.Field(
        nullable=False,
        checks=[
            pa.Check(CustomCheck.positive, error="Term months must be positive")
        ],
        description="Loan term in months"
    )
    
    credit_score_at_origination: Series[int] = pa.Field(
        nullable=True,
        checks=[
            pa.Check(CustomCheck.valid_credit_score, error="Credit score must be 300-850")
        ],
        description="Credit score at loan origination"
    )
    
    days_past_due: Series[int] = pa.Field(
        nullable=True,
        checks=[
            pa.Check(CustomCheck.non_negative, error="Days past due must be non-negative")
        ],
        description="Days past due"
    )
    
    origination_date: Series[datetime] = pa.Field(
        nullable=False,
        description="Loan origination date"
    )
    
    maturity_date: Series[datetime] = pa.Field(
        nullable=False,
        description="Loan maturity date"
    )
    
    class Config:
        strict = True
        coerce = True


class FactLoanPaymentSchema(BaseSchema):
    """Schema for fact_loan_payment table.
    
    Validation Rules:
    - payment_id: Required, unique, non-null string
    - loan_key, customer_key, date_key: Required non-null integers
    - payment_amount: Positive numeric
    - principal_component, interest_component: Non-negative numeric
    - days_late: Non-negative integer
    """
    
    payment_id: Series[str] = pa.Field(
        nullable=False,
        unique=True,
        description="Unique payment identifier"
    )
    
    loan_key: Series[int] = pa.Field(
        nullable=False,
        description="Foreign key to fact_loan"
    )
    
    customer_key: Series[int] = pa.Field(
        nullable=False,
        description="Foreign key to dim_customer"
    )
    
    date_key: Series[int] = pa.Field(
        nullable=False,
        description="Foreign key to dim_date"
    )
    
    payment_amount: Series[float] = pa.Field(
        nullable=False,
        checks=[
            pa.Check(CustomCheck.positive, error="Payment amount must be positive")
        ],
        description="Total payment amount"
    )
    
    principal_component: Series[float] = pa.Field(
        nullable=True,
        checks=[
            pa.Check(CustomCheck.non_negative, error="Principal component must be non-negative")
        ],
        description="Principal portion of payment"
    )
    
    interest_component: Series[float] = pa.Field(
        nullable=True,
        checks=[
            pa.Check(CustomCheck.non_negative, error="Interest component must be non-negative")
        ],
        description="Interest portion of payment"
    )
    
    days_late: Series[int] = pa.Field(
        nullable=True,
        checks=[
            pa.Check(CustomCheck.non_negative, error="Days late must be non-negative")
        ],
        description="Days payment is late"
    )
    
    class Config:
        strict = True
        coerce = True


class FactCardTransactionSchema(BaseSchema):
    """Schema for fact_card_transaction table.
    
    Validation Rules:
    - card_transaction_id: Required, unique, non-null string
    - account_key, customer_key, product_key, date_key: Required non-null integers
    - transaction_amount: Non-zero numeric
    - fraud_score: Between 0 and 1 if present
    - rewards_points: Non-negative integer
    """
    
    card_transaction_id: Series[str] = pa.Field(
        nullable=False,
        unique=True,
        description="Unique card transaction identifier"
    )
    
    account_key: Series[int] = pa.Field(
        nullable=False,
        description="Foreign key to dim_account"
    )
    
    customer_key: Series[int] = pa.Field(
        nullable=False,
        description="Foreign key to dim_customer"
    )
    
    product_key: Series[int] = pa.Field(
        nullable=False,
        description="Foreign key to dim_product"
    )
    
    date_key: Series[int] = pa.Field(
        nullable=False,
        description="Foreign key to dim_date"
    )
    
    transaction_amount: Series[float] = pa.Field(
        nullable=False,
        checks=[
            pa.Check(lambda x: x != 0, error="Transaction amount cannot be zero")
        ],
        description="Card transaction amount"
    )
    
    fraud_score: Series[float] = pa.Field(
        nullable=True,
        checks=[
            pa.Check(CustomCheck.valid_rate, error="Fraud score must be between 0 and 1")
        ],
        description="Fraud detection score"
    )
    
    rewards_points: Series[int] = pa.Field(
        nullable=True,
        checks=[
            pa.Check(CustomCheck.non_negative, error="Rewards points must be non-negative")
        ],
        description="Rewards points earned"
    )
    
    class Config:
        strict = True
        coerce = True


class FactCustomerInteractionSchema(BaseSchema):
    """Schema for fact_customer_interaction table.
    
    Validation Rules:
    - interaction_id: Required, unique, non-null string
    - customer_key, date_key: Required non-null integers
    - duration_seconds: Non-negative integer
    - satisfaction_score: Between 1 and 5 if present
    """
    
    interaction_id: Series[str] = pa.Field(
        nullable=False,
        unique=True,
        description="Unique interaction identifier"
    )
    
    customer_key: Series[int] = pa.Field(
        nullable=False,
        description="Foreign key to dim_customer"
    )
    
    date_key: Series[int] = pa.Field(
        nullable=False,
        description="Foreign key to dim_date"
    )
    
    duration_seconds: Series[int] = pa.Field(
        nullable=True,
        checks=[
            pa.Check(CustomCheck.non_negative, error="Duration must be non-negative")
        ],
        description="Interaction duration in seconds"
    )
    
    satisfaction_score: Series[int] = pa.Field(
        nullable=True,
        checks=[
            pa.Check(CustomCheck.in_range, min_val=1, max_val=5,
                   error="Satisfaction score must be between 1 and 5")
        ],
        description="Customer satisfaction score (1-5)"
    )
    
    class Config:
        strict = True
        coerce = True


class FactCustomerProfitabilitySchema(BaseSchema):
    """Schema for fact_customer_profitability table.
    
    Validation Rules:
    - customer_key, date_key: Required non-null integers
    - period_start_date, period_end_date: Required dates
    - Revenue components: Non-negative numeric
    - Cost components: Non-negative numeric
    - number_of_accounts, number_of_transactions: Non-negative integers
    - period_start_date <= period_end_date
    """
    
    customer_key: Series[int] = pa.Field(
        nullable=False,
        description="Foreign key to dim_customer"
    )
    
    date_key: Series[int] = pa.Field(
        nullable=False,
        description="Foreign key to dim_date"
    )
    
    period_start_date: Series[datetime] = pa.Field(
        nullable=False,
        description="Period start date"
    )
    
    period_end_date: Series[datetime] = pa.Field(
        nullable=False,
        description="Period end date"
    )
    
    interest_income: Series[float] = pa.Field(
        nullable=True,
        checks=[
            pa.Check(CustomCheck.non_negative, error="Interest income must be non-negative")
        ],
        description="Interest income"
    )
    
    fee_income: Series[float] = pa.Field(
        nullable=True,
        checks=[
            pa.Check(CustomCheck.non_negative, error="Fee income must be non-negative")
        ],
        description="Fee income"
    )
    
    cost_of_funds: Series[float] = pa.Field(
        nullable=True,
        checks=[
            pa.Check(CustomCheck.non_negative, error="Cost of funds must be non-negative")
        ],
        description="Cost of funds"
    )
    
    operating_costs: Series[float] = pa.Field(
        nullable=True,
        checks=[
            pa.Check(CustomCheck.non_negative, error="Operating costs must be non-negative")
        ],
        description="Operating costs"
    )
    
    number_of_accounts: Series[int] = pa.Field(
        nullable=True,
        checks=[
            pa.Check(CustomCheck.non_negative, error="Number of accounts must be non-negative")
        ],
        description="Number of accounts"
    )
    
    number_of_transactions: Series[int] = pa.Field(
        nullable=True,
        checks=[
            pa.Check(CustomCheck.non_negative, error="Number of transactions must be non-negative")
        ],
        description="Number of transactions"
    )
    
    class Config:
        strict = True
        coerce = True


class FactCustomerRiskSchema(BaseSchema):
    """Schema for fact_customer_risk table.
    
    Validation Rules:
    - customer_key, date_key: Required non-null integers
    - period_start_date, period_end_date: Required dates
    - credit_score: Between 300 and 850 if present
    - Exposure metrics: Non-negative numeric
    - days_past_due, number_of_delinquent_accounts: Non-negative integers
    - probability_of_default, loss_given_default: Between 0 and 1 if present
    """
    
    customer_key: Series[int] = pa.Field(
        nullable=False,
        description="Foreign key to dim_customer"
    )
    
    date_key: Series[int] = pa.Field(
        nullable=False,
        description="Foreign key to dim_date"
    )
    
    period_start_date: Series[datetime] = pa.Field(
        nullable=False,
        description="Period start date"
    )
    
    period_end_date: Series[datetime] = pa.Field(
        nullable=False,
        description="Period end date"
    )
    
    credit_score: Series[int] = pa.Field(
        nullable=True,
        checks=[
            pa.Check(CustomCheck.valid_credit_score, error="Credit score must be 300-850")
        ],
        description="Customer credit score"
    )
    
    total_exposure: Series[float] = pa.Field(
        nullable=True,
        checks=[
            pa.Check(CustomCheck.non_negative, error="Total exposure must be non-negative")
        ],
        description="Total credit exposure"
    )
    
    days_past_due: Series[int] = pa.Field(
        nullable=True,
        checks=[
            pa.Check(CustomCheck.non_negative, error="Days past due must be non-negative")
        ],
        description="Days past due"
    )
    
    number_of_delinquent_accounts: Series[int] = pa.Field(
        nullable=True,
        checks=[
            pa.Check(CustomCheck.non_negative, error="Delinquent accounts must be non-negative")
        ],
        description="Number of delinquent accounts"
    )
    
    probability_of_default: Series[float] = pa.Field(
        nullable=True,
        checks=[
            pa.Check(CustomCheck.valid_rate, error="PD must be between 0 and 1")
        ],
        description="Probability of default"
    )
    
    loss_given_default: Series[float] = pa.Field(
        nullable=True,
        checks=[
            pa.Check(CustomCheck.valid_rate, error="LGD must be between 0 and 1")
        ],
        description="Loss given default"
    )
    
    class Config:
        strict = True
        coerce = True
