"""Fact tables for banking analytics warehouse."""

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
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, TimestampMixin


class FactTransaction(Base, TimestampMixin):
    """Transaction fact table.
    
    Records all banking transactions (deposits, withdrawals, transfers).
    Transactional grain - one row per transaction.
    """
    
    __tablename__ = "fact_transaction"
    
    # Surrogate key
    transaction_key: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Natural key
    transaction_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    
    # Foreign keys to dimensions
    account_key: Mapped[int] = mapped_column(Integer, ForeignKey("dim_account.account_key"), nullable=False, index=True)
    customer_key: Mapped[int] = mapped_column(Integer, ForeignKey("dim_customer.customer_key"), nullable=False, index=True)
    product_key: Mapped[int] = mapped_column(Integer, ForeignKey("dim_product.product_key"), nullable=False, index=True)
    branch_key: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("dim_branch.branch_key"), index=True)
    date_key: Mapped[int] = mapped_column(Integer, ForeignKey("dim_date.date_key"), nullable=False, index=True)
    
    # Transaction details
    transaction_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    transaction_subtype: Mapped[Optional[str]] = mapped_column(String(50))
    transaction_status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # completed, pending, failed, cancelled
    
    # Transaction amounts
    amount: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    balance_after: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    balance_before: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    
    # Transaction timing
    transaction_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    posted_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    value_date: Mapped[Optional[date]] = mapped_column(Date)
    
    # Real-time event tracking
    event_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), index=True)
    processing_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), index=True)
    
    # Counterparty information
    counterparty_account: Mapped[Optional[str]] = mapped_column(String(50))
    counterparty_name: Mapped[Optional[str]] = mapped_column(String(100))
    counterparty_bank: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Transaction metadata
    reference_number: Mapped[Optional[str]] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(Text)
    channel: Mapped[Optional[str]] = mapped_column(String(50), index=True)  # ATM, branch, online, mobile
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    
    # Fraud detection
    is_flagged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    fraud_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 4))
    
    # Reversal information
    is_reversal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    original_transaction_id: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Source system
    source_system: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Constraints
    __table_args__ = (
        CheckConstraint("amount != 0", name="ck_transaction_amount_non_zero"),
        CheckConstraint("fraud_score BETWEEN 0 AND 1 OR fraud_score IS NULL", name="ck_transaction_fraud_score_valid"),
        Index("ix_transaction_account_date", "account_key", "date_key"),
        Index("ix_transaction_customer_date", "customer_key", "date_key"),
        Index("ix_transaction_type_date", "transaction_type", "date_key"),
        Index("ix_transaction_event_time", "event_time"),
        Index("ix_transaction_processing_time", "processing_time"),
    )


class FactLoan(Base, TimestampMixin):
    """Loan fact table.
    
    Records loan origination and terms.
    Loan grain - one row per loan.
    """
    
    __tablename__ = "fact_loan"
    
    # Surrogate key
    loan_key: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Natural key
    loan_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    
    # Foreign keys to dimensions
    customer_key: Mapped[int] = mapped_column(Integer, ForeignKey("dim_customer.customer_key"), nullable=False, index=True)
    account_key: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("dim_account.account_key"), index=True)
    product_key: Mapped[int] = mapped_column(Integer, ForeignKey("dim_product.product_key"), nullable=False, index=True)
    branch_key: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("dim_branch.branch_key"), index=True)
    origination_date_key: Mapped[int] = mapped_column(Integer, ForeignKey("dim_date.date_key"), nullable=False, index=True)
    maturity_date_key: Mapped[int] = mapped_column(Integer, ForeignKey("dim_date.date_key"), nullable=False, index=True)
    
    # Loan details
    loan_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    loan_purpose: Mapped[Optional[str]] = mapped_column(String(100))
    loan_status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # active, paid_off, defaulted, in_restructuring
    
    # Loan amounts
    principal_amount: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    
    # Interest and terms
    interest_rate: Mapped[float] = mapped_column(Numeric(8, 4), nullable=False)
    interest_type: Mapped[str] = mapped_column(String(20), nullable=False)  # fixed, variable
    term_months: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Payment details
    monthly_payment: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    payment_frequency: Mapped[str] = mapped_column(String(20), nullable=False)  # monthly, bi_weekly, weekly
    
    # Collateral information
    collateral_type: Mapped[Optional[str]] = mapped_column(String(50))
    collateral_value: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    loan_to_value_ratio: Mapped[Optional[float]] = mapped_column(Numeric(5, 4))
    
    # Credit information
    credit_score_at_origination: Mapped[Optional[int]] = mapped_column(Integer)
    debt_to_income_ratio: Mapped[Optional[float]] = mapped_column(Numeric(5, 4))
    
    # Dates
    origination_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    maturity_date: Mapped[date] = mapped_column(Date, nullable=False)
    first_payment_date: Mapped[Optional[date]] = mapped_column(Date)
    last_payment_date: Mapped[Optional[date]] = mapped_column(Date)
    paid_off_date: Mapped[Optional[date]] = mapped_column(Date)
    
    # Current status
    current_balance: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    days_past_due: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    days_in_arrears: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Risk classification
    risk_grade: Mapped[Optional[str]] = mapped_column(String(10))
    provision_amount: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    
    # Source system
    source_system: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Constraints
    __table_args__ = (
        CheckConstraint("principal_amount > 0", name="ck_loan_principal_positive"),
        CheckConstraint("interest_rate >= 0", name="ck_loan_interest_rate_non_negative"),
        CheckConstraint("term_months > 0", name="ck_loan_term_positive"),
        CheckConstraint("credit_score_at_origination BETWEEN 300 AND 850 OR credit_score_at_origination IS NULL", 
                       name="ck_loan_credit_score_valid"),
        CheckConstraint("days_past_due >= 0", name="ck_loan_days_past_due_non_negative"),
        CheckConstraint("origination_date <= maturity_date", name="ck_loan_origination_before_maturity"),
        Index("ix_loan_customer_status", "customer_key", "loan_status"),
        Index("ix_loan_type_date", "loan_type", "origination_date_key"),
    )


class FactLoanPayment(Base, TimestampMixin):
    """Loan payment fact table.
    
    Records loan payments.
    Payment grain - one row per payment.
    """
    
    __tablename__ = "fact_loan_payment"
    
    # Surrogate key
    payment_key: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Natural key
    payment_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    
    # Foreign keys to dimensions
    loan_key: Mapped[int] = mapped_column(Integer, ForeignKey("fact_loan.loan_key"), nullable=False, index=True)
    customer_key: Mapped[int] = mapped_column(Integer, ForeignKey("dim_customer.customer_key"), nullable=False, index=True)
    date_key: Mapped[int] = mapped_column(Integer, ForeignKey("dim_date.date_key"), nullable=False, index=True)
    
    # Payment details
    payment_type: Mapped[str] = mapped_column(String(20), nullable=False)  # scheduled, partial, extra, late
    payment_status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # completed, pending, failed, cancelled
    
    # Payment amounts
    payment_amount: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    principal_component: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    interest_component: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    fee_component: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    penalty_component: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    
    # Payment timing
    payment_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    days_late: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Payment method
    payment_method: Mapped[Optional[str]] = mapped_column(String(50))  # ACH, check, wire, cash
    channel: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Balance after payment
    principal_balance_after: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    
    # Source system
    source_system: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Constraints
    __table_args__ = (
        CheckConstraint("payment_amount > 0", name="ck_loan_payment_amount_positive"),
        CheckConstraint("principal_component >= 0", name="ck_loan_payment_principal_non_negative"),
        CheckConstraint("interest_component >= 0", name="ck_loan_payment_interest_non_negative"),
        CheckConstraint("fee_component >= 0", name="ck_loan_payment_fee_non_negative"),
        CheckConstraint("penalty_component >= 0", name="ck_loan_payment_penalty_non_negative"),
        CheckConstraint("days_late >= 0", name="ck_loan_payment_days_late_non_negative"),
        Index("ix_payment_loan_date", "loan_key", "date_key"),
        Index("ix_payment_customer_date", "customer_key", "date_key"),
    )


class FactCardTransaction(Base, TimestampMixin):
    """Card transaction fact table.
    
    Records credit/debit card transactions.
    Transaction grain - one row per card transaction.
    """
    
    __tablename__ = "fact_card_transaction"
    
    # Surrogate key
    card_transaction_key: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Natural key
    card_transaction_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    
    # Foreign keys to dimensions
    account_key: Mapped[int] = mapped_column(Integer, ForeignKey("dim_account.account_key"), nullable=False, index=True)
    customer_key: Mapped[int] = mapped_column(Integer, ForeignKey("dim_customer.customer_key"), nullable=False, index=True)
    product_key: Mapped[int] = mapped_column(Integer, ForeignKey("dim_product.product_key"), nullable=False, index=True)
    merchant_key: Mapped[Optional[int]] = mapped_column(Integer, index=True)  # Could link to dim_merchant if created
    date_key: Mapped[int] = mapped_column(Integer, ForeignKey("dim_date.date_key"), nullable=False, index=True)
    
    # Card details
    card_id: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    card_type: Mapped[Optional[str]] = mapped_column(String(20))  # credit, debit
    card_network: Mapped[Optional[str]] = mapped_column(String(20))  # visa, mastercard, amex
    
    # Transaction details
    transaction_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # purchase, cash_advance, refund
    transaction_status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    
    # Transaction amounts
    transaction_amount: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    billing_amount: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    billing_currency: Mapped[Optional[str]] = mapped_column(String(3))
    exchange_rate: Mapped[Optional[float]] = mapped_column(Numeric(10, 6))
    
    # Transaction timing
    transaction_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    posting_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Merchant information
    merchant_name: Mapped[Optional[str]] = mapped_column(String(100))
    merchant_category: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    merchant_city: Mapped[Optional[str]] = mapped_column(String(100))
    merchant_state: Mapped[Optional[str]] = mapped_column(String(50))
    merchant_country: Mapped[Optional[str]] = mapped_column(String(50))
    merchant_id: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Location information
    terminal_id: Mapped[Optional[str]] = mapped_column(String(50))
    authorization_code: Mapped[Optional[str]] = mapped_column(String(20))
    
    # E-commerce flag
    is_ecommerce: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Fraud detection
    is_flagged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    fraud_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 4))
    
    # Rewards
    rewards_points: Mapped[Optional[int]] = mapped_column(Integer)
    cashback_amount: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    
    # Source system
    source_system: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Constraints
    __table_args__ = (
        CheckConstraint("transaction_amount != 0", name="ck_card_transaction_amount_non_zero"),
        CheckConstraint("fraud_score BETWEEN 0 AND 1 OR fraud_score IS NULL", name="ck_card_transaction_fraud_score_valid"),
        CheckConstraint("rewards_points >= 0", name="ck_card_transaction_rewards_non_negative"),
        Index("ix_card_account_date", "account_key", "date_key"),
        Index("ix_card_customer_date", "customer_key", "date_key"),
        Index("ix_card_merchant_category", "merchant_category", "date_key"),
    )


class FactCustomerInteraction(Base, TimestampMixin):
    """Customer interaction fact table.
    
    Records customer interactions with the bank (calls, visits, emails, chats).
    Interaction grain - one row per interaction.
    """
    
    __tablename__ = "fact_customer_interaction"
    
    # Surrogate key
    interaction_key: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Natural key
    interaction_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    
    # Foreign keys to dimensions
    customer_key: Mapped[int] = mapped_column(Integer, ForeignKey("dim_customer.customer_key"), nullable=False, index=True)
    account_key: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("dim_account.account_key"), index=True)
    branch_key: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("dim_branch.branch_key"), index=True)
    date_key: Mapped[int] = mapped_column(Integer, ForeignKey("dim_date.date_key"), nullable=False, index=True)
    
    # Interaction details
    interaction_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # call, visit, email, chat, sms
    interaction_channel: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # phone, branch, web, mobile
    interaction_direction: Mapped[str] = mapped_column(String(20), nullable=False)  # inbound, outbound
    
    # Interaction purpose
    interaction_purpose: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    interaction_category: Mapped[Optional[str]] = mapped_column(String(50))  # service, sales, support, complaint
    
    # Interaction timing
    interaction_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Interaction outcome
    outcome: Mapped[Optional[str]] = mapped_column(String(50))
    resolution_status: Mapped[Optional[str]] = mapped_column(String(50))  # resolved, escalated, pending
    satisfaction_score: Mapped[Optional[int]] = mapped_column(Integer)  # 1-5 scale
    
    # Agent information
    agent_id: Mapped[Optional[str]] = mapped_column(String(50))
    agent_name: Mapped[Optional[str]] = mapped_column(String(100))
    team: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Follow-up
    requires_followup: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    followup_date: Mapped[Optional[date]] = mapped_column(Date)
    
    # Source system
    source_system: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Constraints
    __table_args__ = (
        CheckConstraint("duration_seconds >= 0", name="ck_interaction_duration_non_negative"),
        CheckConstraint("satisfaction_score BETWEEN 1 AND 5 OR satisfaction_score IS NULL", 
                       name="ck_interaction_satisfaction_valid"),
        Index("ix_interaction_customer_date", "customer_key", "date_key"),
        Index("ix_interaction_type_date", "interaction_type", "date_key"),
    )


class FactCustomerProfitability(Base, TimestampMixin):
    """Customer profitability fact table.
    
    Records customer profitability metrics over time.
    Monthly grain - one row per customer per month.
    """
    
    __tablename__ = "fact_customer_profitability"
    
    # Surrogate key
    profitability_key: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys to dimensions
    customer_key: Mapped[int] = mapped_column(Integer, ForeignKey("dim_customer.customer_key"), nullable=False, index=True)
    segment_key: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("dim_customer_segment.segment_key"), index=True)
    date_key: Mapped[int] = mapped_column(Integer, ForeignKey("dim_date.date_key"), nullable=False, index=True)
    
    # Period information
    period_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    period_end_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Revenue components
    interest_income: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    fee_income: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    trading_income: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    other_income: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    total_revenue: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    
    # Cost components
    cost_of_funds: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    operating_costs: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    credit_loss_provision: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    capital_charge: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    total_costs: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    
    # Profitability metrics
    net_profit: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    profit_margin: Mapped[Optional[float]] = mapped_column(Numeric(5, 4))
    return_on_equity: Mapped[Optional[float]] = mapped_column(Numeric(5, 4))
    return_on_assets: Mapped[Optional[float]] = mapped_column(Numeric(5, 4))
    
    # Customer metrics
    average_balance: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    number_of_accounts: Mapped[Optional[int]] = mapped_column(Integer)
    number_of_transactions: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Currency
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    
    # Source system
    source_system: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Constraints
    __table_args__ = (
        CheckConstraint("interest_income >= 0", name="ck_profitability_interest_income_non_negative"),
        CheckConstraint("fee_income >= 0", name="ck_profitability_fee_income_non_negative"),
        CheckConstraint("cost_of_funds >= 0", name="ck_profitability_cost_of_funds_non_negative"),
        CheckConstraint("operating_costs >= 0", name="ck_profitability_operating_costs_non_negative"),
        CheckConstraint("number_of_accounts >= 0", name="ck_profitability_accounts_non_negative"),
        CheckConstraint("number_of_transactions >= 0", name="ck_profitability_transactions_non_negative"),
        CheckConstraint("period_start_date <= period_end_date", name="ck_profitability_period_valid"),
        UniqueConstraint("customer_key", "date_key", name="uq_customer_profitability_period"),
        Index("ix_profitability_segment_date", "segment_key", "date_key"),
    )


class FactCustomerRisk(Base, TimestampMixin):
    """Customer risk fact table.
    
    Records customer risk metrics over time.
    Monthly grain - one row per customer per month.
    """
    
    __tablename__ = "fact_customer_risk"
    
    # Surrogate key
    risk_key: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys to dimensions
    customer_key: Mapped[int] = mapped_column(Integer, ForeignKey("dim_customer.customer_key"), nullable=False, index=True)
    segment_key: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("dim_customer_segment.segment_key"), index=True)
    date_key: Mapped[int] = mapped_column(Integer, ForeignKey("dim_date.date_key"), nullable=False, index=True)
    
    # Period information
    period_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    period_end_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Credit risk metrics
    credit_score: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    credit_score_change: Mapped[Optional[int]] = mapped_column(Integer)
    credit_rating: Mapped[Optional[str]] = mapped_column(String(10), index=True)
    
    # Exposure metrics
    total_exposure: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    secured_exposure: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    unsecured_exposure: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    utilization_rate: Mapped[Optional[float]] = mapped_column(Numeric(5, 4))
    
    # Delinquency metrics
    days_past_due: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    number_of_delinquent_accounts: Mapped[Optional[int]] = mapped_column(Integer)
    delinquency_amount: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    
    # Default risk
    probability_of_default: Mapped[Optional[float]] = mapped_column(Numeric(5, 4))
    loss_given_default: Mapped[Optional[float]] = mapped_column(Numeric(5, 4))
    expected_loss: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    
    # Behavioral risk
    number_of_late_payments: Mapped[Optional[int]] = mapped_column(Integer)
    payment_behavior_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 4))
    
    # Risk classification
    risk_level: Mapped[Optional[str]] = mapped_column(String(20), index=True)  # low, medium, high, critical
    risk_category: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Watchlist and flags
    is_on_watchlist: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    watchlist_reason: Mapped[Optional[str]] = mapped_column(String(100))
    is_fraud_suspect: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Currency
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    
    # Source system
    source_system: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Constraints
    __table_args__ = (
        CheckConstraint("credit_score BETWEEN 300 AND 850 OR credit_score IS NULL", 
                       name="ck_risk_credit_score_valid"),
        CheckConstraint("total_exposure >= 0", name="ck_risk_exposure_non_negative"),
        CheckConstraint("days_past_due >= 0", name="ck_risk_days_past_due_non_negative"),
        CheckConstraint("number_of_delinquent_accounts >= 0", name="ck_risk_delinquent_accounts_non_negative"),
        CheckConstraint("probability_of_default BETWEEN 0 AND 1 OR probability_of_default IS NULL", 
                       name="ck_risk_pd_valid"),
        CheckConstraint("loss_given_default BETWEEN 0 AND 1 OR loss_given_default IS NULL", 
                       name="ck_risk_lgd_valid"),
        CheckConstraint("expected_loss >= 0", name="ck_risk_expected_loss_non_negative"),
        CheckConstraint("period_start_date <= period_end_date", name="ck_risk_period_valid"),
        UniqueConstraint("customer_key", "date_key", name="uq_customer_risk_period"),
        Index("ix_risk_segment_date", "segment_key", "date_key"),
        Index("ix_risk_level_date", "risk_level", "date_key"),
    )
