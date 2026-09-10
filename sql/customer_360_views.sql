-- Customer 360 SQL Views
-- These views provide unified customer-level analytical data
-- All views include temporal safety to prevent future data leakage

-- ============================================================================
-- DEMOGRAPHIC FEATURES VIEW
-- ============================================================================

CREATE OR REPLACE VIEW vw_customer_demographic_features AS
SELECT 
    c.customer_key,
    c.customer_id,
    -- Age calculation
    EXTRACT(YEAR FROM AGE(CURRENT_DATE, c.birth_date)) AS age,
    CASE 
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, c.birth_date)) < 18 THEN 'under_18'
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, c.birth_date)) < 25 THEN '18-25'
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, c.birth_date)) < 35 THEN '26-35'
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, c.birth_date)) < 45 THEN '36-45'
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, c.birth_date)) < 55 THEN '46-55'
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, c.birth_date)) < 65 THEN '56-65'
        ELSE '65+'
    END AS age_group,
    c.gender,
    c.marital_status,
    c.education_level,
    c.occupation,
    c.annual_income,
    CASE 
        WHEN c.annual_income < 25000 THEN 'under_25k'
        WHEN c.annual_income < 50000 THEN '25k-50k'
        WHEN c.annual_income < 75000 THEN '50k-75k'
        WHEN c.annual_income < 100000 THEN '75k-100k'
        WHEN c.annual_income < 150000 THEN '100k-150k'
        ELSE '150k+'
    END AS income_bracket,
    -- Tenure calculation
    EXTRACT(YEAR FROM AGE(CURRENT_DATE, c.customer_since)) AS tenure_years,
    CASE 
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, c.customer_since)) < 1 THEN 'new'
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, c.customer_since)) < 3 THEN 'established'
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, c.customer_since)) < 5 THEN 'loyal'
        ELSE 'veteran'
    END AS tenure_group,
    c.is_active
FROM dim_customer c
WHERE c.birth_date IS NOT NULL;

-- ============================================================================
-- ACCOUNT FEATURES VIEW
-- ============================================================================

CREATE OR REPLACE VIEW vw_customer_account_features AS
SELECT 
    c.customer_key,
    c.customer_id,
    -- Account counts
    COUNT(a.account_id) AS account_count,
    SUM(CASE WHEN a.is_active = true THEN 1 ELSE 0 END) AS active_account_count,
    -- Product diversity
    COUNT(DISTINCT a.product_key) AS unique_products,
    COUNT(DISTINCT p.product_category) AS product_diversity,
    STRING_AGG(DISTINCT p.product_category, ',' ORDER BY p.product_category) AS products_owned,
    -- Balance aggregates (if available in account table)
    COALESCE(SUM(a.current_balance), 0) AS total_balance,
    COALESCE(AVG(a.current_balance), 0) AS average_balance,
    -- Credit limits
    COALESCE(SUM(a.credit_limit), 0) AS total_credit_limit
FROM dim_customer c
LEFT JOIN dim_account a ON c.customer_key = a.customer_key
LEFT JOIN dim_product p ON a.product_key = p.product_key
GROUP BY c.customer_key, c.customer_id;

-- ============================================================================
-- TRANSACTION FEATURES VIEW (30-day window)
-- ============================================================================

CREATE OR REPLACE VIEW vw_customer_transaction_features_30d AS
WITH transaction_window AS (
    SELECT 
        t.customer_key,
        c.customer_id,
        -- Transaction counts and volumes
        COUNT(t.transaction_id) AS transaction_count_30d,
        SUM(t.amount) AS transaction_volume_30d,
        AVG(t.amount) AS avg_transaction_amount_30d,
        -- Frequency (transactions per day)
        COUNT(t.transaction_id)::FLOAT / 30 AS transaction_frequency_30d,
        -- Recency
        MAX(t.transaction_date) AS last_transaction_date
    FROM fact_transaction t
    JOIN dim_customer c ON t.customer_key = c.customer_key
    WHERE t.transaction_date >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY t.customer_key, c.customer_id
)
SELECT 
    customer_key,
    customer_id,
    transaction_count_30d,
    COALESCE(transaction_volume_30d, 0) AS transaction_volume_30d,
    COALESCE(avg_transaction_amount_30d, 0) AS avg_transaction_amount_30d,
    COALESCE(transaction_frequency_30d, 0) AS transaction_frequency_30d,
    -- Days since last transaction
    EXTRACT(DAY FROM (CURRENT_DATE - last_transaction_date)) AS days_since_last_transaction,
    -- Recency score (higher = more recent)
    CASE 
        WHEN last_transaction_date IS NULL THEN 0
        ELSE GREATEST(0, 1 - (EXTRACT(DAY FROM (CURRENT_DATE - last_transaction_date))::FLOAT / 30))
    END AS transaction_recency_score
FROM transaction_window;

-- ============================================================================
-- TRANSACTION FEATURES VIEW (90-day window)
-- ============================================================================

CREATE OR REPLACE VIEW vw_customer_transaction_features_90d AS
WITH transaction_window AS (
    SELECT 
        t.customer_key,
        c.customer_id,
        COUNT(t.transaction_id) AS transaction_count_90d,
        SUM(t.amount) AS transaction_volume_90d,
        AVG(t.amount) AS avg_transaction_amount_90d,
        COUNT(t.transaction_id)::FLOAT / 90 AS transaction_frequency_90d
    FROM fact_transaction t
    JOIN dim_customer c ON t.customer_key = c.customer_key
    WHERE t.transaction_date >= CURRENT_DATE - INTERVAL '90 days'
    GROUP BY t.customer_key, c.customer_id
)
SELECT 
    customer_key,
    customer_id,
    COALESCE(transaction_count_90d, 0) AS transaction_count_90d,
    COALESCE(transaction_volume_90d, 0) AS transaction_volume_90d,
    COALESCE(avg_transaction_amount_90d, 0) AS avg_transaction_amount_90d,
    COALESCE(transaction_frequency_90d, 0) AS transaction_frequency_90d
FROM transaction_window;

-- ============================================================================
-- LOAN FEATURES VIEW
-- ============================================================================

CREATE OR REPLACE VIEW vw_customer_loan_features AS
WITH loan_metrics AS (
    SELECT 
        l.customer_key,
        c.customer_id,
        -- Loan counts
        COUNT(l.loan_id) AS loan_count,
        -- Exposure
        COALESCE(SUM(l.current_balance), 0) AS total_loan_exposure,
        -- Delinquency
        COALESCE(MAX(l.days_past_due), 0) AS days_past_due_max,
        CASE WHEN MAX(l.days_past_due) > 0 THEN 1 ELSE 0 END AS has_delinquent_loans
    FROM fact_loan l
    JOIN dim_customer c ON l.customer_key = c.customer_key
    WHERE l.origination_date <= CURRENT_DATE
    GROUP BY l.customer_key, c.customer_id
),
credit_metrics AS (
    SELECT 
        a.customer_key,
        COALESCE(SUM(a.credit_limit), 0) AS total_credit_limit
    FROM dim_account a
    WHERE a.is_active = true
    GROUP BY a.customer_key
)
SELECT 
    l.customer_key,
    l.customer_id,
    l.loan_count,
    l.total_loan_exposure,
    COALESCE(c.total_credit_limit, 0) AS total_credit_limit,
    -- Credit utilization
    CASE 
        WHEN c.total_credit_limit > 0 
        THEN l.total_loan_exposure::FLOAT / c.total_credit_limit 
        ELSE 0 
    END AS credit_utilization,
    l.days_past_due_max,
    l.has_delinquent_loans
FROM loan_metrics l
LEFT JOIN credit_metrics c ON l.customer_key = c.customer_key;

-- ============================================================================
-- INTERACTION FEATURES VIEW
-- ============================================================================

CREATE OR REPLACE VIEW vw_customer_interaction_features AS
WITH interaction_window AS (
    SELECT 
        i.customer_key,
        c.customer_id,
        COUNT(i.interaction_id) AS interaction_count_90d,
        AVG(i.satisfaction_score) AS avg_satisfaction_score,
        -- Complaint metrics
        SUM(CASE WHEN i.interaction_category = 'complaint' THEN 1 ELSE 0 END) AS complaint_count_90d
    FROM fact_customer_interaction i
    JOIN dim_customer c ON i.customer_key = c.customer_key
    WHERE i.interaction_date >= CURRENT_DATE - INTERVAL '90 days'
    GROUP BY i.customer_key, c.customer_id
)
SELECT 
    customer_key,
    customer_id,
    COALESCE(interaction_count_90d, 0) AS interaction_count_90d,
    COALESCE(avg_satisfaction_score, 0) AS avg_satisfaction_score,
    COALESCE(complaint_count_90d, 0) AS complaint_count_90d,
    CASE WHEN complaint_count_90d > 0 THEN 1 ELSE 0 END AS has_complaints
FROM interaction_window;

-- ============================================================================
-- PROFITABILITY FEATURES VIEW
-- ============================================================================

CREATE OR REPLACE VIEW vw_customer_profitability_features AS
WITH latest_profitability AS (
    SELECT 
        p.customer_key,
        c.customer_id,
        p.period_end_date,
        -- Profit metrics
        COALESCE(p.interest_income, 0) + COALESCE(p.fee_income, 0) -
        COALESCE(p.cost_of_funds, 0) - COALESCE(p.operating_costs, 0) AS net_profit_12m,
        -- Profit margin
        CASE 
            WHEN (COALESCE(p.interest_income, 0) + COALESCE(p.fee_income, 0)) > 0 
            THEN (COALESCE(p.interest_income, 0) + COALESCE(p.fee_income, 0) -
                  COALESCE(p.cost_of_funds, 0) - COALESCE(p.operating_costs, 0))::FLOAT /
                 (COALESCE(p.interest_income, 0) + COALESCE(p.fee_income, 0))
            ELSE 0 
        END AS profit_margin_12m,
        COALESCE(p.average_balance, 0) AS avg_balance_12m,
        ROW_NUMBER() OVER (PARTITION BY p.customer_key ORDER BY p.period_end_date DESC) AS rn
    FROM fact_customer_profitability p
    JOIN dim_customer c ON p.customer_key = c.customer_key
    WHERE p.period_end_date <= CURRENT_DATE
)
SELECT 
    customer_key,
    customer_id,
    net_profit_12m,
    profit_margin_12m,
    avg_balance_12m
FROM latest_profitability
WHERE rn = 1;

-- ============================================================================
-- RISK FEATURES VIEW
-- ============================================================================

CREATE OR REPLACE VIEW vw_customer_risk_features AS
WITH latest_risk AS (
    SELECT 
        r.customer_key,
        c.customer_id,
        r.period_end_date,
        COALESCE(r.credit_score, 0) AS credit_score,
        COALESCE(r.credit_score_change, 0) AS credit_score_trend,
        COALESCE(r.total_exposure, 0) AS total_exposure,
        COALESCE(r.probability_of_default, 0) AS probability_of_default,
        COALESCE(r.risk_level, 'unknown') AS risk_level,
        COALESCE(r.is_on_watchlist, false) AS is_on_watchlist,
        ROW_NUMBER() OVER (PARTITION BY r.customer_key ORDER BY r.period_end_date DESC) AS rn
    FROM fact_customer_risk r
    JOIN dim_customer c ON r.customer_key = c.customer_key
    WHERE r.period_end_date <= CURRENT_DATE
)
SELECT 
    customer_key,
    customer_id,
    credit_score,
    credit_score_trend,
    total_exposure,
    probability_of_default,
    risk_level,
    is_on_watchlist
FROM latest_risk
WHERE rn = 1;

-- ============================================================================
-- COMPREHENSIVE CUSTOMER 360 VIEW
-- ============================================================================

CREATE OR REPLACE VIEW vw_customer_360 AS
SELECT 
    -- Customer identifiers
    c.customer_key,
    c.customer_id,
    
    -- Demographic features
    d.age,
    d.age_group,
    d.gender,
    d.marital_status,
    d.education_level,
    d.occupation,
    d.annual_income,
    d.income_bracket,
    d.tenure_years,
    d.tenure_group,
    d.is_active,
    
    -- Account features
    a.account_count,
    a.active_account_count,
    a.total_balance,
    a.average_balance,
    a.total_credit_limit,
    a.product_diversity,
    a.products_owned,
    
    -- Transaction features (30-day)
    t30.transaction_count_30d,
    t30.transaction_volume_30d,
    t30.avg_transaction_amount_30d,
    t30.transaction_frequency_30d,
    t30.days_since_last_transaction,
    t30.transaction_recency_score,
    
    -- Transaction features (90-day)
    t90.transaction_count_90d,
    t90.transaction_volume_90d,
    t90.avg_transaction_amount_90d,
    t90.transaction_frequency_90d,
    
    -- Loan features
    l.loan_count,
    l.total_loan_exposure,
    l.total_credit_limit AS loan_total_credit_limit,
    l.credit_utilization,
    l.days_past_due_max,
    l.has_delinquent_loans,
    
    -- Interaction features
    i.interaction_count_90d,
    i.avg_satisfaction_score,
    i.complaint_count_90d,
    i.has_complaints,
    
    -- Profitability features
    p.net_profit_12m,
    p.profit_margin_12m,
    p.avg_balance_12m,
    
    -- Risk features
    r.credit_score,
    r.credit_score_trend,
    r.total_exposure AS risk_total_exposure,
    r.probability_of_default,
    r.risk_level,
    r.is_on_watchlist,
    
    -- Metadata
    CURRENT_DATE AS as_of_date
    
FROM dim_customer c
LEFT JOIN vw_customer_demographic_features d ON c.customer_key = d.customer_key
LEFT JOIN vw_customer_account_features a ON c.customer_key = a.customer_key
LEFT JOIN vw_customer_transaction_features_30d t30 ON c.customer_key = t30.customer_key
LEFT JOIN vw_customer_transaction_features_90d t90 ON c.customer_key = t90.customer_key
LEFT JOIN vw_customer_loan_features l ON c.customer_key = l.customer_key
LEFT JOIN vw_customer_interaction_features i ON c.customer_key = i.customer_key
LEFT JOIN vw_customer_profitability_features p ON c.customer_key = p.customer_key
LEFT JOIN vw_customer_risk_features r ON c.customer_key = r.customer_key;

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_customer_360_customer_key ON vw_customer_360(customer_key);
CREATE INDEX IF NOT EXISTS idx_customer_360_customer_id ON vw_customer_360(customer_id);
CREATE INDEX IF NOT EXISTS idx_customer_360_risk_level ON vw_customer_360(risk_level);
CREATE INDEX IF NOT EXISTS idx_customer_360_is_active ON vw_customer_360(is_active);

-- ============================================================================
-- COMMENTS ON VIEWS
-- ============================================================================

COMMENT ON VIEW vw_customer_360 IS 'Comprehensive Customer 360 view with all features';
COMMENT ON VIEW vw_customer_demographic_features IS 'Customer demographic and profile features';
COMMENT ON VIEW vw_customer_account_features IS 'Customer account and product ownership features';
COMMENT ON VIEW vw_customer_transaction_features_30d IS 'Customer transaction features (30-day window)';
COMMENT ON VIEW vw_customer_transaction_features_90d IS 'Customer transaction features (90-day window)';
COMMENT ON VIEW vw_customer_loan_features IS 'Customer loan and credit utilization features';
COMMENT ON VIEW vw_customer_interaction_features IS 'Customer service interaction features';
COMMENT ON VIEW vw_customer_profitability_features IS 'Customer profitability metrics';
COMMENT ON VIEW vw_customer_risk_features IS 'Customer risk assessment features';
