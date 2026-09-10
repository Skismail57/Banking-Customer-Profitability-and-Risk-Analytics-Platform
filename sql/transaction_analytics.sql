-- Transaction Analytics SQL Queries
-- Reusable analytical queries for transaction KPIs, trends, and behavior analysis

-- ============================================================================
-- DAILY TRANSACTION KPIs
-- ============================================================================

CREATE OR REPLACE VIEW vw_transaction_kpis_daily AS
SELECT 
    DATE(transaction_date) AS period,
    COUNT(transaction_id) AS transaction_count,
    SUM(amount) AS transaction_value,
    AVG(amount) AS avg_transaction_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amount) AS median_transaction_value,
    COUNT(transaction_id)::FLOAT / 1 AS transaction_frequency,
    SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS total_inflow,
    SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) AS outflow,
    SUM(amount) AS net_flow,
    COUNT(CASE WHEN amount < 0 THEN 1 END) AS debit_count,
    COUNT(CASE WHEN amount > 0 THEN 1 END) AS credit_count,
    SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) AS debit_value,
    SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS credit_value
FROM fact_transaction
WHERE transaction_date <= CURRENT_DATE
GROUP BY DATE(transaction_date)
ORDER BY period;

-- ============================================================================
-- WEEKLY TRANSACTION KPIs
-- ============================================================================

CREATE OR REPLACE VIEW vw_transaction_kpis_weekly AS
SELECT 
    date_trunc('week', transaction_date)::date AS period,
    COUNT(transaction_id) AS transaction_count,
    SUM(amount) AS transaction_value,
    AVG(amount) AS avg_transaction_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amount) AS median_transaction_value,
    COUNT(transaction_id)::FLOAT / 7 AS transaction_frequency,
    SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS total_inflow,
    SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) AS outflow,
    SUM(amount) AS net_flow,
    COUNT(CASE WHEN amount < 0 THEN 1 END) AS debit_count,
    COUNT(CASE WHEN amount > 0 THEN 1 END) AS credit_count,
    SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) AS debit_value,
    SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS credit_value
FROM fact_transaction
WHERE transaction_date <= CURRENT_DATE
GROUP BY date_trunc('week', transaction_date)
ORDER BY period;

-- ============================================================================
-- MONTHLY TRANSACTION KPIs
-- ============================================================================

CREATE OR REPLACE VIEW vw_transaction_kpis_monthly AS
SELECT 
    date_trunc('month', transaction_date)::date AS period,
    COUNT(transaction_id) AS transaction_count,
    SUM(amount) AS transaction_value,
    AVG(amount) AS avg_transaction_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amount) AS median_transaction_value,
    COUNT(transaction_id)::FLOAT / 
        EXTRACT(DAY FROM (date_trunc('month', transaction_date) + INTERVAL '1 month' - INTERVAL '1 day')) 
        AS transaction_frequency,
    SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS total_inflow,
    SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) AS outflow,
    SUM(amount) AS net_flow,
    COUNT(CASE WHEN amount < 0 THEN 1 END) AS debit_count,
    COUNT(CASE WHEN amount > 0 THEN 1 END) AS credit_count,
    SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) AS debit_value,
    SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS credit_value
FROM fact_transaction
WHERE transaction_date <= CURRENT_DATE
GROUP BY date_trunc('month', transaction_date)
ORDER BY period;

-- ============================================================================
-- QUARTERLY TRANSACTION KPIs
-- ============================================================================

CREATE OR REPLACE VIEW vw_transaction_kpis_quarterly AS
SELECT 
    date_trunc('quarter', transaction_date)::date AS period,
    COUNT(transaction_id) AS transaction_count,
    SUM(amount) AS transaction_value,
    AVG(amount) AS avg_transaction_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amount) AS median_transaction_value,
    COUNT(transaction_id)::FLOAT / 90 AS transaction_frequency,
    SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS total_inflow,
    SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) AS outflow,
    SUM(amount) AS net_flow,
    COUNT(CASE WHEN amount < 0 THEN 1 END) AS debit_count,
    COUNT(CASE WHEN amount > 0 THEN 1 END) AS credit_count,
    SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) AS debit_value,
    SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS credit_value
FROM fact_transaction
WHERE transaction_date <= CURRENT_DATE
GROUP BY date_trunc('quarter', transaction_date)
ORDER BY period;

-- ============================================================================
-- YEARLY TRANSACTION KPIs
-- ============================================================================

CREATE OR REPLACE VIEW vw_transaction_kpis_yearly AS
SELECT 
    date_trunc('year', transaction_date)::date AS period,
    COUNT(transaction_id) AS transaction_count,
    SUM(amount) AS transaction_value,
    AVG(amount) AS avg_transaction_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amount) AS median_transaction_value,
    COUNT(transaction_id)::FLOAT / 365 AS transaction_frequency,
    SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS total_inflow,
    SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) AS outflow,
    SUM(amount) AS net_flow,
    COUNT(CASE WHEN amount < 0 THEN 1 END) AS debit_count,
    COUNT(CASE WHEN amount > 0 THEN 1 END) AS credit_count,
    SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) AS debit_value,
    SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS credit_value
FROM fact_transaction
WHERE transaction_date <= CURRENT_DATE
GROUP BY date_trunc('year', transaction_date)
ORDER BY period;

-- ============================================================================
-- CUSTOMER-LEVEL TRANSACTION KPIs
-- ============================================================================

CREATE OR REPLACE VIEW vw_customer_transaction_kpis AS
SELECT 
    customer_key,
    COUNT(transaction_id) AS transaction_count,
    SUM(amount) AS transaction_value,
    AVG(amount) AS avg_transaction_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amount) AS median_transaction_value,
    SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS total_inflow,
    SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) AS outflow,
    SUM(amount) AS net_flow,
    COUNT(CASE WHEN amount < 0 THEN 1 END) AS debit_count,
    COUNT(CASE WHEN amount > 0 THEN 1 END) AS credit_count,
    SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) AS debit_value,
    SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS credit_value
FROM fact_transaction
WHERE transaction_date <= CURRENT_DATE
GROUP BY customer_key;

-- ============================================================================
-- CATEGORY BEHAVIOR ANALYSIS
-- ============================================================================

CREATE OR REPLACE VIEW vw_transaction_category_behavior AS
SELECT 
    transaction_category,
    COUNT(transaction_id) AS transaction_count,
    SUM(amount) AS transaction_value,
    AVG(amount) AS avg_transaction_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amount) AS median_transaction_value,
    STDDEV(amount) AS std_transaction_value,
    SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS inflow,
    SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) AS outflow,
    COUNT(CASE WHEN amount < 0 THEN 1 END) AS debit_count,
    COUNT(CASE WHEN amount > 0 THEN 1 END) AS credit_count,
    ROUND(SUM(amount) * 100.0 / SUM(SUM(amount)) OVER (), 2) AS value_percentage
FROM fact_transaction
WHERE transaction_date <= CURRENT_DATE
GROUP BY transaction_category
ORDER BY transaction_value DESC;

-- ============================================================================
-- CHANNEL BEHAVIOR ANALYSIS
-- ============================================================================

CREATE OR REPLACE VIEW vw_transaction_channel_behavior AS
SELECT 
    channel,
    COUNT(transaction_id) AS transaction_count,
    SUM(amount) AS transaction_value,
    AVG(amount) AS avg_transaction_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amount) AS median_transaction_value,
    ROUND(SUM(amount) * 100.0 / SUM(SUM(amount)) OVER (), 2) AS value_percentage
FROM fact_transaction
WHERE transaction_date <= CURRENT_DATE
GROUP BY channel
ORDER BY transaction_value DESC;

-- ============================================================================
-- CUSTOMER x PERIOD TRANSACTION KPIs
-- ============================================================================

CREATE OR REPLACE VIEW vw_customer_monthly_transaction_kpis AS
SELECT 
    customer_key,
    date_trunc('month', transaction_date)::date AS period,
    COUNT(transaction_id) AS transaction_count,
    SUM(amount) AS transaction_value,
    AVG(amount) AS avg_transaction_value,
    SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS total_inflow,
    SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) AS outflow,
    SUM(amount) AS net_flow
FROM fact_transaction
WHERE transaction_date <= CURRENT_DATE
GROUP BY customer_key, date_trunc('month', transaction_date)
ORDER BY customer_key, period;

-- ============================================================================
-- TREND ANALYSIS WITH GROWTH RATES
-- ============================================================================

CREATE OR REPLACE VIEW vw_transaction_trends_monthly AS
WITH monthly_kpis AS (
    SELECT 
        date_trunc('month', transaction_date)::date AS period,
        COUNT(transaction_id) AS transaction_count,
        SUM(amount) AS transaction_value
    FROM fact_transaction
    WHERE transaction_date <= CURRENT_DATE
    GROUP BY date_trunc('month', transaction_date)
),
lagged_kpis AS (
    SELECT 
        period,
        transaction_count,
        transaction_value,
        LAG(transaction_value) OVER (ORDER BY period) AS prev_value,
        LAG(transaction_count) OVER (ORDER BY period) AS prev_count
    FROM monthly_kpis
)
SELECT 
    period,
    transaction_count,
    transaction_value,
    prev_value,
    prev_count,
    CASE 
        WHEN prev_value > 0 
        THEN ROUND((transaction_value - prev_value)::numeric / prev_value * 100, 2)
        ELSE NULL 
    END AS value_growth_pct,
    CASE 
        WHEN prev_count > 0 
        THEN ROUND((transaction_count - prev_count)::numeric / prev_count * 100, 2)
        ELSE NULL 
    END AS count_growth_pct
FROM lagged_kpis
ORDER BY period;

-- ============================================================================
-- MOVING AVERAGES
-- ============================================================================

CREATE OR REPLACE VIEW vw_transaction_moving_averages AS
WITH monthly_kpis AS (
    SELECT 
        date_trunc('month', transaction_date)::date AS period,
        SUM(amount) AS transaction_value
    FROM fact_transaction
    WHERE transaction_date <= CURRENT_DATE
    GROUP BY date_trunc('month', transaction_date)
),
moving_avg AS (
    SELECT 
        period,
        transaction_value,
        AVG(transaction_value) OVER (
            ORDER BY period 
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS ma_3_month,
        AVG(transaction_value) OVER (
            ORDER BY period 
            ROWS BETWEEN 5 PRECEDING AND CURRENT ROW
        ) AS ma_6_month
    FROM monthly_kpis
)
SELECT * FROM moving_avg
ORDER BY period;

-- ============================================================================
-- SEASONALITY ANALYSIS
-- ============================================================================

CREATE OR REPLACE VIEW vw_transaction_seasonality_monthly AS
SELECT 
    EXTRACT(MONTH FROM transaction_date) AS month,
    COUNT(transaction_id) AS transaction_count,
    SUM(amount) AS transaction_value,
    AVG(amount) AS avg_transaction_value
FROM fact_transaction
WHERE transaction_date <= CURRENT_DATE
GROUP BY EXTRACT(MONTH FROM transaction_date)
ORDER BY month;

-- ============================================================================
-- ANOMALY DETECTION (IQR METHOD)
-- ============================================================================

CREATE OR REPLACE VIEW vw_transaction_amount_anomalies AS
WITH transaction_stats AS (
    SELECT 
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY amount) AS q1,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY amount) AS q3,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY amount) - 
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY amount) AS iqr
    FROM fact_transaction
    WHERE transaction_date <= CURRENT_DATE
),
anomalies AS (
    SELECT 
        t.transaction_id,
        t.customer_key,
        t.amount,
        ts.q1,
        ts.q3,
        ts.iqr,
        ts.q1 - 3 * ts.iqr AS lower_bound,
        ts.q3 + 3 * ts.iqr AS upper_bound,
        CASE 
            WHEN t.amount < (ts.q1 - 3 * ts.iqr) OR t.amount > (ts.q3 + 3 * ts.iqr) 
            THEN true 
            ELSE false 
        END AS is_anomaly
    FROM fact_transaction t
    CROSS JOIN transaction_stats ts
    WHERE t.transaction_date <= CURRENT_DATE
)
SELECT * FROM anomalies
WHERE is_anomaly = true;

-- ============================================================================
-- DEBIT VS CREDIT ANALYSIS
-- ============================================================================

CREATE OR REPLACE VIEW vw_debit_credit_analysis AS
SELECT 
    'debit' AS transaction_type,
    COUNT(CASE WHEN amount < 0 THEN 1 END) AS transaction_count,
    ABS(SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END)) AS total_value,
    AVG(ABS(CASE WHEN amount < 0 THEN amount ELSE 0 END)) AS avg_value
FROM fact_transaction
WHERE transaction_date <= CURRENT_DATE
UNION ALL
SELECT 
    'credit' AS transaction_type,
    COUNT(CASE WHEN amount > 0 THEN 1 END) AS transaction_count,
    SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS total_value,
    AVG(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS avg_value
FROM fact_transaction
WHERE transaction_date <= CURRENT_DATE;

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_fact_transaction_date ON fact_transaction(transaction_date);
CREATE INDEX IF NOT EXISTS idx_fact_transaction_customer ON fact_transaction(customer_key);
CREATE INDEX IF NOT EXISTS idx_fact_transaction_category ON fact_transaction(transaction_category);
CREATE INDEX IF NOT EXISTS idx_fact_transaction_channel ON fact_transaction(channel);

-- ============================================================================
-- COMMENTS ON VIEWS
-- ============================================================================

COMMENT ON VIEW vw_transaction_kpis_daily IS 'Daily transaction KPIs with count, value, avg, median, inflow/outflow';
COMMENT ON VIEW vw_transaction_kpis_weekly IS 'Weekly transaction KPIs';
COMMENT ON VIEW vw_transaction_kpis_monthly IS 'Monthly transaction KPIs';
COMMENT ON VIEW vw_transaction_kpis_quarterly IS 'Quarterly transaction KPIs';
COMMENT ON VIEW vw_transaction_kpis_yearly IS 'Yearly transaction KPIs';
COMMENT ON VIEW vw_customer_transaction_kpis IS 'Customer-level transaction KPIs';
COMMENT ON VIEW vw_transaction_category_behavior IS 'Transaction behavior by category';
COMMENT ON VIEW vw_transaction_channel_behavior IS 'Transaction behavior by channel';
COMMENT ON VIEW vw_customer_monthly_transaction_kpis IS 'Customer x monthly transaction KPIs';
COMMENT ON VIEW vw_transaction_trends_monthly IS 'Monthly transaction trends with growth rates';
COMMENT ON VIEW vw_transaction_moving_averages IS 'Transaction moving averages (3 and 6 month)';
COMMENT ON VIEW vw_transaction_seasonality_monthly IS 'Monthly seasonality analysis';
COMMENT ON VIEW vw_transaction_amount_anomalies IS 'Amount anomalies detected using IQR method';
COMMENT ON VIEW vw_debit_credit_analysis IS 'Debit vs credit transaction analysis';
