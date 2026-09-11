"""Pandera schemas for dimension and fact tables."""

import pandera as pa
from pandera.typing import DataFrame, Series
from datetime import datetime
import logging
import pandas as pd

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
        description="Customer date of birth"
    )
    
    annual_income: Series[int] = pa.Field(
        nullable=True,
        description="Annual income amount"
    )
    
    is_active: Series[bool] = pa.Field(
        nullable=False,
        description="Customer active status"
    )
    
    customer_since: Series[datetime] = pa.Field(
        nullable=True,
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

    _field_validators = {
        "birth_date": {
            "not_future_date": CustomCheck.not_future_date,
            "not_too_old": lambda s: CustomCheck.not_past_date(s, years=120),
        },
        "annual_income": {
            "non_negative": CustomCheck.non_negative,
        },
        "customer_since": {
            "not_future_date": CustomCheck.not_future_date,
        },
        "churn_date": {
            "not_future_date": CustomCheck.not_future_date,
        },
    }

    @classmethod
    def _churn_after_customer_since(cls, df):
        if "customer_since" not in df.columns or "churn_date" not in df.columns:
            return pd.Series([False] * len(df), index=df.index)
        cs = df["customer_since"]
        cd = df["churn_date"]
        both_present = cs.notna() & cd.notna()
        invalid = both_present & (cd < cs)
        return invalid

    _cross_field_validators = {
        "churn_date >= customer_since": _churn_after_customer_since,
    }


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
        description="Account credit limit"
    )
    
    overdraft_limit: Series[int] = pa.Field(
        nullable=True,
        description="Account overdraft limit"
    )
    
    is_active: Series[bool] = pa.Field(
        nullable=False,
        description="Account active status"
    )
    
    opened_date: Series[datetime] = pa.Field(
        nullable=True,
        description="Account opening date"
    )
    
    closed_date: Series[datetime] = pa.Field(
        nullable=True,
        description="Account closing date"
    )
    
    class Config:
        strict = True
        coerce = True

    _field_validators = {
        "credit_limit": {
            "non_negative": CustomCheck.non_negative,
        },
        "overdraft_limit": {
            "non_negative": CustomCheck.non_negative,
        },
        "opened_date": {
            "not_future_date": CustomCheck.not_future_date,
        },
        "closed_date": {
            "not_future_date": CustomCheck.not_future_date,
        },
    }

    @classmethod
    def _closed_after_opened(cls, df):
        if "opened_date" not in df.columns or "closed_date" not in df.columns:
            return pd.Series([False] * len(df), index=df.index)
        od = df["opened_date"]
        cd = df["closed_date"]
        both_present = od.notna() & cd.notna()
        invalid = both_present & (cd < od)
        return invalid

    _cross_field_validators = {
        "closed_date >= opened_date": _closed_after_opened,
    }


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
        description="Annual interest rate"
    )
    
    annual_fee: Series[int] = pa.Field(
        nullable=True,
        description="Annual fee amount"
    )
    
    minimum_balance: Series[int] = pa.Field(
        nullable=True,
        description="Minimum balance requirement"
    )
    
    term_months: Series[int] = pa.Field(
        nullable=True,
        description="Loan term in months"
    )
    
    is_active: Series[bool] = pa.Field(
        nullable=False,
        description="Product active status"
    )
    
    class Config:
        strict = True
        coerce = True

    _field_validators = {
        "interest_rate": {
            "non_negative": CustomCheck.non_negative,
        },
        "annual_fee": {
            "non_negative": CustomCheck.non_negative,
        },
        "minimum_balance": {
            "non_negative": CustomCheck.non_negative,
        },
        "term_months": {
            "non_negative": CustomCheck.non_negative,
        },
    }


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
        description="Branch latitude"
    )
    
    longitude: Series[float] = pa.Field(
        nullable=True,
        description="Branch longitude"
    )
    
    atm_count: Series[int] = pa.Field(
        nullable=True,
        description="Number of ATMs at branch"
    )
    
    employee_count: Series[int] = pa.Field(
        nullable=True,
        description="Number of employees at branch"
    )
    
    is_active: Series[bool] = pa.Field(
        nullable=False,
        description="Branch active status"
    )
    
    class Config:
        strict = True
        coerce = True

    _field_validators = {
        "latitude": {
            "valid_latitude": lambda s: CustomCheck.in_range(s, -90.0, 90.0),
        },
        "longitude": {
            "valid_longitude": lambda s: CustomCheck.in_range(s, -180.0, 180.0),
        },
        "atm_count": {
            "non_negative": CustomCheck.non_negative,
        },
        "employee_count": {
            "non_negative": CustomCheck.non_negative,
        },
    }


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
        description="Day of month (1-31)"
    )
    
    day_of_week: Series[int] = pa.Field(
        nullable=False,
        description="Day of week (1-7, Monday=1)"
    )
    
    month: Series[int] = pa.Field(
        nullable=False,
        description="Month (1-12)"
    )
    
    quarter: Series[int] = pa.Field(
        nullable=False,
        description="Quarter (1-4)"
    )
    
    year: Series[int] = pa.Field(
        nullable=False,
        description="Year"
    )
    
    class Config:
        strict = True
        coerce = True

    _field_validators = {
        "day_of_month": {
            "valid_day_of_month": lambda s: CustomCheck.in_range(s, 1, 31),
        },
        "day_of_week": {
            "valid_day_of_week": lambda s: CustomCheck.in_range(s, 1, 7),
        },
        "month": {
            "valid_month": lambda s: CustomCheck.in_range(s, 1, 12),
        },
        "quarter": {
            "valid_quarter": lambda s: CustomCheck.in_range(s, 1, 4),
        },
        "year": {
            "reasonable_year": lambda s: CustomCheck.in_range(s, 1900, 2200),
        },
    }


class DimCustomerSegmentSchema(BaseSchema):
    """Schema for dim_customer_segment table.
    
    Validation Rules:
    - segment_id: Required, unique, non-null string
    - segment_name: Required non-null string
    - segment_type: Required non-null string
    - min_balance, max_balance: Non-negative integers
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
        description="Minimum balance for segment"
    )
    
    max_balance: Series[int] = pa.Field(
        nullable=True,
        description="Maximum balance for segment"
    )
    
    credit_score_min: Series[int] = pa.Field(
        nullable=True,
        description="Minimum credit score for segment"
    )
    
    credit_score_max: Series[int] = pa.Field(
        nullable=True,
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

    _field_validators = {
        "min_balance": {
            "non_negative": CustomCheck.non_negative,
        },
        "max_balance": {
            "non_negative": CustomCheck.non_negative,
        },
        "credit_score_min": {
            "valid_credit_score": CustomCheck.valid_credit_score,
        },
        "credit_score_max": {
            "valid_credit_score": CustomCheck.valid_credit_score,
        },
    }

    @classmethod
    def _expiry_after_effective(cls, df):
        if "effective_date" not in df.columns or "expiry_date" not in df.columns:
            return pd.Series([False] * len(df), index=df.index)
        ed = df["effective_date"]
        xd = df["expiry_date"]
        both_present = ed.notna() & xd.notna()
        invalid = both_present & (xd < ed)
        return invalid

    @classmethod
    def _min_lte_max_balance(cls, df):
        if "min_balance" not in df.columns or "max_balance" not in df.columns:
            return pd.Series([False] * len(df), index=df.index)
        mn = df["min_balance"]
        mx = df["max_balance"]
        both_present = mn.notna() & mx.notna()
        invalid = both_present & (mn > mx)
        return invalid

    @classmethod
    def _min_lte_max_credit(cls, df):
        if "credit_score_min" not in df.columns or "credit_score_max" not in df.columns:
            return pd.Series([False] * len(df), index=df.index)
        mn = df["credit_score_min"]
        mx = df["credit_score_max"]
        both_present = mn.notna() & mx.notna()
        invalid = both_present & (mn > mx)
        return invalid

    _cross_field_validators = {
        "expiry_date >= effective_date": _expiry_after_effective,
        "min_balance <= max_balance": _min_lte_max_balance,
        "credit_score_min <= credit_score_max": _min_lte_max_credit,
    }


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
        description="Transaction amount"
    )
    
    transaction_date: Series[datetime] = pa.Field(
        nullable=False,
        description="Transaction timestamp"
    )
    
    fraud_score: Series[float] = pa.Field(
        nullable=True,
        description="Fraud detection score"
    )
    
    class Config:
        strict = True
        coerce = True

    _field_validators = {
        "fraud_score": {
            "valid_rate": CustomCheck.valid_rate,
        },
    }

    @classmethod
    def _amount_not_zero(cls, df):
        if "amount" not in df.columns:
            return pd.Series([False] * len(df), index=df.index)
        amt = df["amount"]
        return amt.notna() & (amt == 0)

    _cross_field_validators = {
        "amount != 0": _amount_not_zero,
    }


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
        description="Loan principal amount"
    )
    
    interest_rate: Series[float] = pa.Field(
        nullable=False,
        description="Loan interest rate"
    )
    
    term_months: Series[int] = pa.Field(
        nullable=False,
        description="Loan term in months"
    )
    
    credit_score_at_origination: Series[int] = pa.Field(
        nullable=True,
        description="Credit score at loan origination"
    )
    
    days_past_due: Series[int] = pa.Field(
        nullable=True,
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

    _field_validators = {
        "principal_amount": {
            "positive": CustomCheck.positive,
        },
        "interest_rate": {
            "non_negative": CustomCheck.non_negative,
        },
        "term_months": {
            "positive": CustomCheck.positive,
        },
        "credit_score_at_origination": {
            "valid_credit_score": CustomCheck.valid_credit_score,
        },
        "days_past_due": {
            "non_negative": CustomCheck.non_negative,
        },
    }

    @classmethod
    def _maturity_after_origination(cls, df):
        if "origination_date" not in df.columns or "maturity_date" not in df.columns:
            return pd.Series([False] * len(df), index=df.index)
        od = df["origination_date"]
        md = df["maturity_date"]
        both_present = od.notna() & md.notna()
        invalid = both_present & (md < od)
        return invalid

    _cross_field_validators = {
        "maturity_date >= origination_date": _maturity_after_origination,
    }


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
        description="Total payment amount"
    )
    
    principal_component: Series[float] = pa.Field(
        nullable=True,
        description="Principal portion of payment"
    )
    
    interest_component: Series[float] = pa.Field(
        nullable=True,
        description="Interest portion of payment"
    )
    
    days_late: Series[int] = pa.Field(
        nullable=True,
        description="Days payment is late"
    )
    
    class Config:
        strict = True
        coerce = True

    _field_validators = {
        "payment_amount": {
            "positive": CustomCheck.positive,
        },
        "principal_component": {
            "non_negative": CustomCheck.non_negative,
        },
        "interest_component": {
            "non_negative": CustomCheck.non_negative,
        },
        "days_late": {
            "non_negative": CustomCheck.non_negative,
        },
    }


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
        description="Card transaction amount"
    )
    
    fraud_score: Series[float] = pa.Field(
        nullable=True,
        description="Fraud detection score"
    )
    
    rewards_points: Series[int] = pa.Field(
        nullable=True,
        description="Rewards points earned"
    )
    
    class Config:
        strict = True
        coerce = True

    _field_validators = {
        "fraud_score": {
            "valid_rate": CustomCheck.valid_rate,
        },
        "rewards_points": {
            "non_negative": CustomCheck.non_negative,
        },
    }

    @classmethod
    def _transaction_amount_not_zero(cls, df):
        if "transaction_amount" not in df.columns:
            return pd.Series([False] * len(df), index=df.index)
        amt = df["transaction_amount"]
        return amt.notna() & (amt == 0)

    _cross_field_validators = {
        "transaction_amount != 0": _transaction_amount_not_zero,
    }


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
        description="Interaction duration in seconds"
    )
    
    satisfaction_score: Series[int] = pa.Field(
        nullable=True,
        description="Customer satisfaction score (1-5)"
    )
    
    class Config:
        strict = True
        coerce = True

    _field_validators = {
        "duration_seconds": {
            "non_negative": CustomCheck.non_negative,
        },
        "satisfaction_score": {
            "valid_satisfaction": lambda s: CustomCheck.in_range(s, 1, 5),
        },
    }


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
        description="Interest income"
    )
    
    fee_income: Series[float] = pa.Field(
        nullable=True,
        description="Fee income"
    )
    
    cost_of_funds: Series[float] = pa.Field(
        nullable=True,
        description="Cost of funds"
    )
    
    operating_costs: Series[float] = pa.Field(
        nullable=True,
        description="Operating costs"
    )
    
    number_of_accounts: Series[int] = pa.Field(
        nullable=True,
        description="Number of accounts"
    )
    
    number_of_transactions: Series[int] = pa.Field(
        nullable=True,
        description="Number of transactions"
    )
    
    class Config:
        strict = True
        coerce = True

    _field_validators = {
        "interest_income": {
            "non_negative": CustomCheck.non_negative,
        },
        "fee_income": {
            "non_negative": CustomCheck.non_negative,
        },
        "cost_of_funds": {
            "non_negative": CustomCheck.non_negative,
        },
        "operating_costs": {
            "non_negative": CustomCheck.non_negative,
        },
        "number_of_accounts": {
            "non_negative": CustomCheck.non_negative,
        },
        "number_of_transactions": {
            "non_negative": CustomCheck.non_negative,
        },
    }

    @classmethod
    def _period_end_after_start(cls, df):
        if "period_start_date" not in df.columns or "period_end_date" not in df.columns:
            return pd.Series([False] * len(df), index=df.index)
        sd = df["period_start_date"]
        ed = df["period_end_date"]
        both_present = sd.notna() & ed.notna()
        invalid = both_present & (ed < sd)
        return invalid

    _cross_field_validators = {
        "period_end_date >= period_start_date": _period_end_after_start,
    }


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
        description="Customer credit score"
    )
    
    total_exposure: Series[float] = pa.Field(
        nullable=True,
        description="Total credit exposure"
    )
    
    days_past_due: Series[int] = pa.Field(
        nullable=True,
        description="Days past due"
    )
    
    number_of_delinquent_accounts: Series[int] = pa.Field(
        nullable=True,
        description="Number of delinquent accounts"
    )
    
    probability_of_default: Series[float] = pa.Field(
        nullable=True,
        description="Probability of default"
    )
    
    loss_given_default: Series[float] = pa.Field(
        nullable=True,
        description="Loss given default"
    )
    
    class Config:
        strict = True
        coerce = True

    _field_validators = {
        "credit_score": {
            "valid_credit_score": CustomCheck.valid_credit_score,
        },
        "total_exposure": {
            "non_negative": CustomCheck.non_negative,
        },
        "days_past_due": {
            "non_negative": CustomCheck.non_negative,
        },
        "number_of_delinquent_accounts": {
            "non_negative": CustomCheck.non_negative,
        },
        "probability_of_default": {
            "valid_rate": CustomCheck.valid_rate,
        },
        "loss_given_default": {
            "valid_rate": CustomCheck.valid_rate,
        },
    }

    @classmethod
    def _period_end_after_start_risk(cls, df):
        if "period_start_date" not in df.columns or "period_end_date" not in df.columns:
            return pd.Series([False] * len(df), index=df.index)
        sd = df["period_start_date"]
        ed = df["period_end_date"]
        both_present = sd.notna() & ed.notna()
        invalid = both_present & (ed < sd)
        return invalid

    _cross_field_validators = {
        "period_end_date >= period_start_date": _period_end_after_start_risk,
    }
