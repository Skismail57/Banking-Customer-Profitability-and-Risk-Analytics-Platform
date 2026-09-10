-- Banking Customer Profitability & Risk Analytics Platform
-- Database Schema
-- This schema supports the analytical layer architecture:
-- Banking Data → Data Platform → Customer 360/Transaction/Product Analytics → 
-- Core Analytics → Statistical Analytics → ML → Decision Engine → Power BI/Streamlit/API

-- ============================================================================
-- DIMENSION TABLES
-- ============================================================================

-- Date Dimension
CREATE TABLE IF NOT EXISTS dim_date (
    date_key INTEGER PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    day INTEGER NOT NULL,
    month INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    year INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_of_year INTEGER NOT NULL,
    week_of_year INTEGER NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    is_holiday BOOLEAN NOT NULL DEFAULT FALSE,
    month_name VARCHAR(20) NOT NULL,
    quarter_name VARCHAR(10) NOT NULL,
    fiscal_year INTEGER,
    fiscal_quarter INTEGER
);

-- Customer Dimension
CREATE TABLE IF NOT EXISTS dim_customer (
    customer_key VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL UNIQUE,
    customer_name VARCHAR(200) NOT NULL,
    customer_age INTEGER,
    gender VARCHAR(20),
    income_level VARCHAR(50),
    segment VARCHAR(50),
    region VARCHAR(50),
    branch VARCHAR(100),
    customer_since DATE,
    customer_status VARCHAR(20) NOT NULL DEFAULT 'active',
    marital_status VARCHAR(50),
    education_level VARCHAR(50),
    occupation VARCHAR(100),
    household_size INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Product Dimension
CREATE TABLE IF NOT EXISTS dim_product (
    product_key VARCHAR(50) PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL UNIQUE,
    product_name VARCHAR(200) NOT NULL,
    product_category VARCHAR(50) NOT NULL,
    product_type VARCHAR(50),
    base_rate DECIMAL(10,6),
    term_months INTEGER,
    min_amount DECIMAL(15,2),
    max_amount DECIMAL(15,2),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    launch_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Channel Dimension
CREATE TABLE IF NOT EXISTS dim_channel (
    channel_key VARCHAR(50) PRIMARY KEY,
    channel_id VARCHAR(50) NOT NULL UNIQUE,
    channel_name VARCHAR(100) NOT NULL,
    channel_type VARCHAR(50) NOT NULL,
    channel_category VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- FACT TABLES
-- ============================================================================

-- Customer Metrics Fact (Core Analytics Output)
CREATE TABLE IF NOT EXISTS fact_customer_metrics (
    customer_key VARCHAR(50) NOT NULL,
    as_of_date DATE NOT NULL,
    
    -- Profitability Metrics
    net_profit DECIMAL(15,2),
    revenue DECIMAL(15,2),
    cost DECIMAL(15,2),
    profit_margin DECIMAL(10,6),
    risk_adjusted_profit DECIMAL(15,2),
    
    -- Risk Metrics
    risk_level VARCHAR(20),
    risk_trend VARCHAR(20),
    exposure_amount DECIMAL(15,2),
    credit_utilization DECIMAL(5,4),
    days_past_due INTEGER,
    credit_score INTEGER,
    balance_to_income_ratio DECIMAL(5,4),
    
    -- Churn Metrics
    churn_probability DECIMAL(5,4),
    churn_risk_level VARCHAR(20),
    
    -- CLV Metrics
    clv DECIMAL(15,2),
    clv_trend VARCHAR(20),
    
    -- Segment Information
    segment VARCHAR(50),
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (customer_key, as_of_date),
    FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key)
);

-- Transactions Fact (Transaction Analytics Output)
CREATE TABLE IF NOT EXISTS fact_transactions (
    transaction_id VARCHAR(50) PRIMARY KEY,
    customer_key VARCHAR(50) NOT NULL,
    product_key VARCHAR(50),
    channel_key VARCHAR(50),
    transaction_date DATE NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    channel VARCHAR(50),
    amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    description TEXT,
    merchant_category VARCHAR(100),
    location VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
    FOREIGN KEY (product_key) REFERENCES dim_product(product_key),
    FOREIGN KEY (channel_key) REFERENCES dim_channel(channel_key)
);

-- Loan Fact (Risk Analytics Source)
CREATE TABLE IF NOT EXISTS fact_loan (
    loan_key VARCHAR(50) PRIMARY KEY,
    customer_key VARCHAR(50) NOT NULL,
    product_key VARCHAR(50) NOT NULL,
    loan_id VARCHAR(50) NOT NULL UNIQUE,
    loan_amount DECIMAL(15,2) NOT NULL,
    current_balance DECIMAL(15,2),
    original_balance DECIMAL(15,2),
    interest_rate DECIMAL(10,6),
    term_months INTEGER,
    start_date DATE NOT NULL,
    maturity_date DATE,
    loan_status VARCHAR(50) NOT NULL,
    days_past_due INTEGER DEFAULT 0,
    payment_amount DECIMAL(15,2),
    next_payment_date DATE,
    as_of_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    
    FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
    FOREIGN KEY (product_key) REFERENCES dim_product(product_key)
);

-- Account Fact (Risk Analytics Source)
CREATE TABLE IF NOT EXISTS fact_account (
    account_key VARCHAR(50) PRIMARY KEY,
    customer_key VARCHAR(50) NOT NULL,
    product_key VARCHAR(50) NOT NULL,
    account_id VARCHAR(50) NOT NULL UNIQUE,
    account_type VARCHAR(50) NOT NULL,
    current_balance DECIMAL(15,2),
    credit_limit DECIMAL(15,2),
    available_credit DECIMAL(15,2),
    account_status VARCHAR(50) NOT NULL,
    open_date DATE NOT NULL,
    as_of_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    
    FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
    FOREIGN KEY (product_key) REFERENCES dim_product(product_key)
);

-- Payment Fact (Risk Analytics Source)
CREATE TABLE IF NOT EXISTS fact_payment (
    payment_id VARCHAR(50) PRIMARY KEY,
    customer_key VARCHAR(50) NOT NULL,
    loan_key VARCHAR(50) NOT NULL,
    payment_date DATE NOT NULL,
    due_date DATE NOT NULL,
    payment_amount DECIMAL(15,2) NOT NULL,
    payment_type VARCHAR(50),
    payment_status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
    FOREIGN KEY (loan_key) REFERENCES fact_loan(loan_key)
);

-- Customer Profitability Fact (Profitability Analytics Source)
CREATE TABLE IF NOT EXISTS fact_customer_profitability (
    customer_key VARCHAR(50) NOT NULL,
    product_key VARCHAR(50),
    period DATE NOT NULL,
    period_type VARCHAR(20) NOT NULL,
    
    -- Revenue Components
    interest_income DECIMAL(15,2),
    fee_income DECIMAL(15,2),
    service_charge_income DECIMAL(15,2),
    product_revenue DECIMAL(15,2),
    
    -- Cost Components
    servicing_cost DECIMAL(15,2),
    operational_cost DECIMAL(15,2),
    incentive_cost DECIMAL(15,2),
    expected_credit_loss DECIMAL(15,2),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (customer_key, period, period_type, product_key),
    FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
    FOREIGN KEY (product_key) REFERENCES dim_product(product_key)
);

-- Recommendations Fact (Decision Engine Output)
CREATE TABLE IF NOT EXISTS fact_recommendations (
    recommendation_key VARCHAR(50) PRIMARY KEY,
    customer_key VARCHAR(50),
    segment VARCHAR(50),
    priority VARCHAR(20) NOT NULL,
    confidence_level VARCHAR(20) NOT NULL,
    recommended_action TEXT NOT NULL,
    reason TEXT NOT NULL,
    triggering_metrics JSONB,
    limitations TEXT[],
    generated_at DATE NOT NULL,
    implemented_at DATE,
    implementation_status VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key)
);

-- Model Performance Fact (ML Monitoring)
CREATE TABLE IF NOT EXISTS fact_model_performance (
    model_id VARCHAR(50) PRIMARY KEY,
    model_name VARCHAR(200) NOT NULL,
    model_type VARCHAR(50) NOT NULL,
    accuracy DECIMAL(5,4),
    precision DECIMAL(5,4),
    recall DECIMAL(5,4),
    f1_score DECIMAL(5,4),
    auc_roc DECIMAL(5,4),
    pr_auc DECIMAL(5,4),
    mse DECIMAL(15,6),
    rmse DECIMAL(15,6),
    mae DECIMAL(15,6),
    r2 DECIMAL(5,4),
    training_samples INTEGER,
    test_samples INTEGER,
    as_of_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Data Quality Metrics Fact (Data Quality Monitoring)
CREATE TABLE IF NOT EXISTS fact_data_quality (
    table_name VARCHAR(100) NOT NULL,
    as_of_date DATE NOT NULL,
    total_rows INTEGER,
    valid_rows INTEGER,
    invalid_rows INTEGER,
    completeness DECIMAL(5,4),
    uniqueness DECIMAL(5,4),
    accuracy DECIMAL(5,4),
    consistency DECIMAL(5,4),
    timeliness DECIMAL(5,4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (table_name, as_of_date)
);

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Customer Metrics Indexes
CREATE INDEX idx_customer_metrics_as_of_date ON fact_customer_metrics(as_of_date);
CREATE INDEX idx_customer_metrics_segment ON fact_customer_metrics(segment);
CREATE INDEX idx_customer_metrics_risk_level ON fact_customer_metrics(risk_level);
CREATE INDEX idx_customer_metrics_churn_probability ON fact_customer_metrics(churn_probability);

-- Transactions Indexes
CREATE INDEX idx_transactions_customer_key ON fact_transactions(customer_key);
CREATE INDEX idx_transactions_date ON fact_transactions(transaction_date);
CREATE INDEX idx_transactions_type ON fact_transactions(transaction_type);
CREATE INDEX idx_transactions_product_key ON fact_transactions(product_key);

-- Loan Indexes
CREATE INDEX idx_loan_customer_key ON fact_loan(customer_key);
CREATE INDEX idx_loan_status ON fact_loan(loan_status);
CREATE INDEX idx_loan_as_of_date ON fact_loan(as_of_date);
CREATE INDEX idx_loan_days_past_due ON fact_loan(days_past_due);

-- Account Indexes
CREATE INDEX idx_account_customer_key ON fact_account(customer_key);
CREATE INDEX idx_account_type ON fact_account(account_type);
CREATE INDEX idx_account_as_of_date ON fact_account(as_of_date);

-- Payment Indexes
CREATE INDEX idx_payment_customer_key ON fact_payment(customer_key);
CREATE INDEX idx_payment_loan_key ON fact_payment(loan_key);
CREATE INDEX idx_payment_date ON fact_payment(payment_date);

-- Customer Profitability Indexes
CREATE INDEX idx_profitability_customer_key ON fact_customer_profitability(customer_key);
CREATE INDEX idx_profitability_period ON fact_customer_profitability(period);

-- Recommendations Indexes
CREATE INDEX idx_recommendations_customer_key ON fact_recommendations(customer_key);
CREATE INDEX idx_recommendations_segment ON fact_recommendations(segment);
CREATE INDEX idx_recommendations_priority ON fact_recommendations(priority);
CREATE INDEX idx_recommendations_generated_at ON fact_recommendations(generated_at);

-- Model Performance Indexes
CREATE INDEX idx_model_performance_as_of_date ON fact_model_performance(as_of_date);
CREATE INDEX idx_model_performance_type ON fact_model_performance(model_type);

-- Data Quality Indexes
CREATE INDEX idx_data_quality_table_name ON fact_data_quality(table_name);
CREATE INDEX idx_data_quality_as_of_date ON fact_data_quality(as_of_date);

-- ============================================================================
-- CONSTRAINTS
-- ============================================================================

-- Check constraints for data validation
ALTER TABLE dim_customer ADD CONSTRAINT chk_customer_age_positive CHECK (customer_age IS NULL OR customer_age >= 0);
ALTER TABLE dim_customer ADD CONSTRAINT chk_customer_age_reasonable CHECK (customer_age IS NULL OR customer_age <= 120);

ALTER TABLE fact_customer_metrics ADD CONSTRAINT chk_churn_probability_range CHECK (churn_probability IS NULL OR (churn_probability >= 0 AND churn_probability <= 1));
ALTER TABLE fact_customer_metrics ADD CONSTRAINT chk_credit_utilization_range CHECK (credit_utilization IS NULL OR (credit_utilization >= 0 AND credit_utilization <= 1));
ALTER TABLE fact_customer_metrics ADD CONSTRAINT chk_credit_score_range CHECK (credit_score IS NULL OR (credit_score >= 300 AND credit_score <= 850));
ALTER TABLE fact_customer_metrics ADD CONSTRAINT chk_days_past_due_positive CHECK (days_past_due IS NULL OR days_past_due >= 0);

ALTER TABLE fact_transactions ADD CONSTRAINT chk_transaction_amount_not_zero CHECK (amount != 0);

ALTER TABLE fact_loan ADD CONSTRAINT chk_loan_amount_positive CHECK (loan_amount > 0);
ALTER TABLE fact_loan ADD CONSTRAINT chk_current_balance_positive CHECK (current_balance IS NULL OR current_balance >= 0);
ALTER TABLE fact_loan ADD CONSTRAINT chk_days_past_due_positive CHECK (days_past_due >= 0);

ALTER TABLE fact_account ADD CONSTRAINT chk_current_balance CHECK (current_balance IS NULL OR current_balance >= 0);
ALTER TABLE fact_account ADD CONSTRAINT chk_credit_limit_positive CHECK (credit_limit IS NULL OR credit_limit > 0);

ALTER TABLE fact_payment ADD CONSTRAINT chk_payment_amount_positive CHECK (payment_amount > 0);

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE dim_customer IS 'Customer dimension with demographic and profile information';
COMMENT ON TABLE fact_customer_metrics IS 'Core analytics output: profitability, risk, churn, and CLV metrics per customer';
COMMENT ON TABLE fact_transactions IS 'Transaction fact for transaction analytics';
COMMENT ON TABLE fact_loan IS 'Loan fact for risk analytics';
COMMENT ON TABLE fact_account IS 'Account fact for risk analytics';
COMMENT ON TABLE fact_payment IS 'Payment fact for risk analytics';
COMMENT ON TABLE fact_customer_profitability IS 'Customer profitability fact for profitability analytics';
COMMENT ON TABLE fact_recommendations IS 'Decision engine output: recommendations for customers and segments';
COMMENT ON TABLE fact_model_performance IS 'ML model performance tracking';
COMMENT ON TABLE fact_data_quality IS 'Data quality metrics monitoring';

COMMENT ON COLUMN fact_customer_metrics.net_profit IS 'Net profit (revenue - cost)';
COMMENT ON COLUMN fact_customer_metrics.risk_adjusted_profit IS 'Profit adjusted for risk (net_profit * risk_factor)';
COMMENT ON COLUMN fact_customer_metrics.churn_probability IS 'Predicted probability of churn (0-1)';
COMMENT ON COLUMN fact_customer_metrics.clv IS 'Customer lifetime value';
COMMENT ON COLUMN fact_recommendations.triggering_metrics IS 'JSON object containing metrics that triggered the recommendation';
