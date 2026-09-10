-- Transaction Analytics View
-- Purpose: Transaction-level analysis
-- Single Source of Truth: Transaction data
-- This view aggregates transaction data with time and product dimensions

CREATE OR REPLACE VIEW vw_transaction_analytics AS
SELECT 
    d.date_key,
    d.year,
    d.quarter,
    d.month,
    d.week,
    d.day_of_week,
    
    -- Transaction Metrics (SQL: Aggregation)
    COUNT(t.transaction_key) AS transaction_count,
    SUM(t.amount) AS total_transaction_value,
    AVG(t.amount) AS avg_transaction_amount,
    MIN(t.amount) AS min_transaction_amount,
    MAX(t.amount) AS max_transaction_amount,
    
    -- Transaction by Type (SQL: Aggregation)
    COUNT(CASE WHEN t.transaction_type = 'purchase' THEN t.transaction_key END) AS purchase_count,
    COUNT(CASE WHEN t.transaction_type = 'payment' THEN t.transaction_key END) AS payment_count,
    COUNT(CASE WHEN t.transaction_type = 'withdrawal' THEN t.transaction_key END) AS withdrawal_count,
    
    -- Transaction by Channel (SQL: Aggregation)
    COUNT(CASE WHEN t.channel = 'online' THEN t.transaction_key END) AS online_count,
    COUNT(CASE WHEN t.channel = 'branch' THEN t.transaction_key END) AS branch_count,
    COUNT(CASE WHEN t.channel = 'atm' THEN t.transaction_key END) AS atm_count,
    COUNT(CASE WHEN t.channel = 'mobile' THEN t.transaction_key END) AS mobile_count,
    
    -- Unique Customers (SQL: Count)
    COUNT(DISTINCT t.customer_key) AS unique_customers,
    
    -- Transaction Trend (SQL: YoY calculation)
    SUM(t.amount) AS current_period_value,
    LAG(SUM(t.amount), 12) OVER (ORDER BY d.date_key) AS same_period_last_year_value,
    
    -- Transaction Value Bands (SQL: Categorization)
    COUNT(CASE WHEN t.amount < 100 THEN t.transaction_key END) AS low_value_transactions,
    COUNT(CASE WHEN t.amount BETWEEN 100 AND 1000 THEN t.transaction_key END) AS medium_value_transactions,
    COUNT(CASE WHEN t.amount > 1000 THEN t.transaction_key END) AS high_value_transactions
    
FROM fact_transactions t
JOIN dim_date d ON t.transaction_date = d.date
GROUP BY 
    d.date_key, d.year, d.quarter, d.month, d.week, d.day_of_week;
