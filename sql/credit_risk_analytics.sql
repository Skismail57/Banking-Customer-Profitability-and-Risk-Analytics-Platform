-- Credit Risk Analytics SQL Queries
-- Reusable analytical queries for credit risk indicators with transparency metadata

-- ============================================================================
-- CUSTOMER EXPOSURE VIEW
-- ============================================================================

CREATE OR REPLACE VIEW vw_customer_exposure AS
SELECT 
    fl.customer_key,
    c.customer_id,
    SUM(COALESCE(fl.current_balance, 0)) AS total_exposure,
    AVG(COALESCE(fl.current_balance, 0)) AS average_balance,
    COUNT(*) AS loan_count,
    MAX(COALESCE(fl.current_balance, 0)) AS max_balance,
    MIN(COALESCE(fl.current_balance, 0)) AS min_balance
FROM fact_loan fl
LEFT JOIN dim_customer c ON fl.customer_key = c.customer_key
WHERE fl.loan_status IN ('active', 'current')
  AND fl.as_of_date <= CURRENT_DATE
GROUP BY fl.customer_key, c.customer_id
ORDER BY total_exposure DESC;

-- ============================================================================
-- PAYMENT BEHAVIOR VIEW
-- ============================================================================

CREATE OR REPLACE VIEW vw_customer_payment_behavior AS
SELECT 
    fl.customer_key,
    c.customer_id,
    MAX(COALESCE(fl.days_past_due, 0)) AS max_days_past_due,
    AVG(COALESCE(fl.days_past_due, 0)) AS avg_days_past_due,
    CASE 
        WHEN MAX(COALESCE(fl.days_past_due, 0)) = 0 THEN 'Current'
        WHEN MAX(COALESCE(fl.days_past_due, 0)) <= 30 THEN '1-30 Days Past Due'
        WHEN MAX(COALESCE(fl.days_past_due, 0)) <= 60 THEN '31-60 Days Past Due'
        WHEN MAX(COALESCE(fl.days_past_due, 0)) <= 90 THEN '61-90 Days Past Due'
        ELSE '90+ Days Past Due'
    END AS delinquency_status,
    COUNT(CASE WHEN fl.days_past_due > 0 THEN 1 END) AS delinquent_loan_count
FROM fact_loan fl
LEFT JOIN dim_customer c ON fl.customer_key = c.customer_key
WHERE fl.as_of_date <= CURRENT_DATE
GROUP BY fl.customer_key, c.customer_id
ORDER BY max_days_past_due DESC;

-- ============================================================================
-- CREDIT UTILIZATION VIEW
-- ============================================================================

CREATE OR REPLACE VIEW vw_customer_utilization AS
SELECT 
    fa.customer_key,
    c.customer_id,
    SUM(COALESCE(fa.current_balance, 0)) AS total_balance,
    SUM(COALESCE(fa.credit_limit, 0)) AS total_credit_limit,
    CASE 
        WHEN SUM(COALESCE(fa.credit_limit, 0)) > 0 
        THEN ROUND((SUM(COALESCE(fa.current_balance, 0))::numeric / 
                   SUM(COALESCE(fa.credit_limit, 0))) * 100, 2)
        ELSE NULL 
    END AS credit_utilization_pct,
    COUNT(*) AS account_count
FROM fact_account fa
LEFT JOIN dim_customer c ON fa.customer_key = c.customer_key
WHERE fa.account_type IN ('credit_card', 'line_of_credit')
  AND fa.as_of_date <= CURRENT_DATE
GROUP BY fa.customer_key, c.customer_id
ORDER BY credit_utilization_pct DESC;

-- ============================================================================
-- REPAYMENT HISTORY VIEW
-- ============================================================================

CREATE OR REPLACE VIEW vw_customer_repayment_history AS
SELECT 
    fp.customer_key,
    c.customer_id,
    COUNT(*) AS total_payments,
    COUNT(CASE 
        WHEN fp.payment_date <= fp.due_date THEN 1 
    END) AS on_time_payments,
    COUNT(CASE 
        WHEN fp.payment_date > fp.due_date THEN 1 
    END) AS late_payments,
    COUNT(CASE 
        WHEN (fp.payment_date - fp.due_date) > INTERVAL '30 days' THEN 1 
    END) AS missed_payments,
    CASE 
        WHEN COUNT(*) > 0 
        THEN ROUND((COUNT(CASE WHEN fp.payment_date <= fp.due_date THEN 1 END)::numeric / 
                   COUNT(*)) * 100, 2)
        ELSE NULL 
    END AS on_time_payment_rate
FROM fact_payment fp
LEFT JOIN dim_customer c ON fp.customer_key = c.customer_key
WHERE fp.payment_date <= CURRENT_DATE
GROUP BY fp.customer_key, c.customer_id
ORDER BY on_time_payment_rate ASC;

-- ============================================================================
-- DEBT BURDEN VIEW (where data available)
-- ============================================================================

CREATE OR REPLACE VIEW vw_customer_debt_burden AS
SELECT 
    fl.customer_key,
    c.customer_id,
    SUM(COALESCE(fl.current_balance, 0)) AS total_debt,
    c.annual_income,
    CASE 
        WHEN c.annual_income > 0 
        THEN ROUND((SUM(COALESCE(fl.current_balance, 0))::numeric / 
                   c.annual_income) * 100, 2)
        ELSE NULL 
    END AS debt_to_income_pct,
    SUM(COALESCE(fl.monthly_payment, 0)) AS total_monthly_payment,
    CASE 
        WHEN c.monthly_income > 0 
        THEN ROUND((SUM(COALESCE(fl.monthly_payment, 0))::numeric / 
                   c.monthly_income) * 100, 2)
        ELSE NULL 
    END AS payment_to_income_pct
FROM fact_loan fl
LEFT JOIN dim_customer c ON fl.customer_key = c.customer_key
WHERE fl.loan_status IN ('active', 'current')
  AND fl.as_of_date <= CURRENT_DATE
GROUP BY fl.customer_key, c.customer_id, c.annual_income, c.monthly_income
ORDER BY debt_to_income_pct DESC NULLS LAST;

-- ============================================================================
-- DEFAULT INDICATORS VIEW
-- ============================================================================

CREATE OR REPLACE VIEW vw_customer_default_indicators AS
SELECT 
    fl.customer_key,
    c.customer_id,
    COUNT(CASE WHEN fl.default_status = 'Y' THEN 1 END) AS default_count,
    MAX(CASE WHEN fl.default_status = 'Y' THEN fl.default_date END) AS most_recent_default_date,
    SUM(COALESCE(fl.recovery_amount, 0)) AS total_recovery,
    SUM(COALESCE(fl.default_amount, 0)) AS total_default_amount,
    CASE 
        WHEN SUM(COALESCE(fl.default_amount, 0)) > 0 
        THEN ROUND((SUM(COALESCE(fl.recovery_amount, 0))::numeric / 
                   SUM(COALESCE(fl.default_amount, 0))) * 100, 2)
        ELSE NULL 
    END AS recovery_rate_pct
FROM fact_loan fl
LEFT JOIN dim_customer c ON fl.customer_key = c.customer_key
WHERE fl.as_of_date <= CURRENT_DATE
GROUP BY fl.customer_key, c.customer_id
ORDER BY default_count DESC;

-- ============================================================================
-- COMPREHENSIVE RISK INDICATORS VIEW
-- ============================================================================

CREATE OR REPLACE VIEW vw_customer_risk_indicators AS
SELECT 
    c.customer_key,
    c.customer_id,
    -- Exposure
    COALESCE(exp.total_exposure, 0) AS total_exposure,
    COALESCE(exp.loan_count, 0) AS loan_count,
    -- Payment behavior
    COALESCE(pb.max_days_past_due, 0) AS max_days_past_due,
    pb.delinquency_status,
    COALESCE(pb.delinquent_loan_count, 0) AS delinquent_loan_count,
    -- Utilization
    COALESCE(u.credit_utilization_pct, 0) AS credit_utilization_pct,
    -- Repayment history
    COALESCE(rh.on_time_payment_rate, 100) AS on_time_payment_rate,
    COALESCE(rh.late_payments, 0) AS late_payments,
    COALESCE(rh.missed_payments, 0) AS missed_payments,
    -- Debt burden (where available)
    db.debt_to_income_pct,
    db.payment_to_income_pct,
    -- Default indicators
    COALESCE(di.default_count, 0) AS default_count,
    di.recovery_rate_pct
FROM dim_customer c
LEFT JOIN vw_customer_exposure exp ON c.customer_key = exp.customer_key
LEFT JOIN vw_customer_payment_behavior pb ON c.customer_key = pb.customer_key
LEFT JOIN vw_customer_utilization u ON c.customer_key = u.customer_key
LEFT JOIN vw_customer_repayment_history rh ON c.customer_key = rh.customer_key
LEFT JOIN vw_customer_debt_burden db ON c.customer_key = db.customer_key
LEFT JOIN vw_customer_default_indicators di ON c.customer_key = di.customer_key;

-- ============================================================================
-- RISK SCORE CALCULATION VIEW (Portfolio Analytics Only)
-- ============================================================================

CREATE OR REPLACE VIEW vw_customer_risk_score AS
WITH normalized_indicators AS (
    SELECT 
        customer_key,
        customer_id,
        -- Normalize each indicator to 0-100 scale
        -- Higher values indicate higher risk
        LEAST(max_days_past_due / 90.0 * 100, 100) AS dpd_score,
        LEAST(credit_utilization_pct, 100) AS utilization_score,
        (100 - on_time_payment_rate) AS payment_score,
        CASE delinquency_status
            WHEN 'Current' THEN 0
            WHEN '1-30 Days Past Due' THEN 25
            WHEN '31-60 Days Past Due' THEN 50
            WHEN '61-90 Days Past Due' THEN 75
            ELSE 100
        END AS delinquency_score,
        LEAST(COALESCE(debt_to_income_pct, 0) / 50.0 * 100, 100) AS dti_score,
        CASE WHEN default_count > 0 THEN 100 ELSE 0 END AS default_score
    FROM vw_customer_risk_indicators
)
SELECT 
    customer_key,
    customer_id,
    -- Weighted risk score (portfolio analytics only)
    ROUND(
        (dpd_score * 0.25 +
         utilization_score * 0.20 +
         payment_score * 0.20 +
         delinquency_score * 0.15 +
         dti_score * 0.10 +
         default_score * 0.10)
    , 2) AS risk_score,
    -- Risk band classification
    CASE 
        WHEN (dpd_score * 0.25 +
              utilization_score * 0.20 +
              payment_score * 0.20 +
              delinquency_score * 0.15 +
              dti_score * 0.10 +
              default_score * 0.10) >= 75 THEN 'critical'
        WHEN (dpd_score * 0.25 +
              utilization_score * 0.20 +
              payment_score * 0.20 +
              delinquency_score * 0.15 +
              dti_score * 0.10 +
              default_score * 0.10) >= 50 THEN 'high'
        WHEN (dpd_score * 0.25 +
              utilization_score * 0.20 +
              payment_score * 0.20 +
              delinquency_score * 0.15 +
              dti_score * 0.10 +
              default_score * 0.10) >= 25 THEN 'medium'
        ELSE 'low'
    END AS risk_band,
    -- Component scores for transparency
    dpd_score,
    utilization_score,
    payment_score,
    delinquency_score,
    dti_score,
    default_score
FROM normalized_indicators
ORDER BY risk_score DESC;

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_fact_loan_customer ON fact_loan(customer_key);
CREATE INDEX IF NOT EXISTS idx_fact_loan_status ON fact_loan(loan_status);
CREATE INDEX IF NOT EXISTS idx_fact_loan_date ON fact_loan(as_of_date);
CREATE INDEX IF NOT EXISTS idx_fact_account_customer ON fact_account(customer_key);
CREATE INDEX IF NOT EXISTS idx_fact_payment_customer ON fact_payment(customer_key);

-- ============================================================================
-- COMMENTS ON VIEWS
-- ============================================================================

COMMENT ON VIEW vw_customer_exposure IS 'Customer loan exposure with total and average balances';
COMMENT ON VIEW vw_customer_payment_behavior IS 'Customer payment behavior with DPD and delinquency status';
COMMENT ON VIEW vw_customer_utilization IS 'Customer credit utilization across revolving accounts';
COMMENT ON VIEW vw_customer_repayment_history IS 'Customer repayment history with on-time payment rate';
COMMENT ON VIEW vw_customer_debt_burden IS 'Customer debt burden ratios (where income data available)';
COMMENT ON VIEW vw_customer_default_indicators IS 'Customer default indicators and recovery rates';
COMMENT ON VIEW vw_customer_risk_indicators IS 'Comprehensive risk indicators for portfolio analytics';
COMMENT ON VIEW vw_customer_risk_score IS 'Risk score and band classification for portfolio analytics only - NOT for credit decisions';
