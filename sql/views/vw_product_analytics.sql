-- Product Analytics View
-- Purpose: Product performance analysis
-- Single Source of Truth: Transaction data + Python Profitability/Risk Analytics
-- This view joins transaction data with customer metrics

CREATE OR REPLACE VIEW vw_product_analytics AS
SELECT 
    d.date_key,
    d.year,
    d.quarter,
    d.month,
    p.product_type,
    p.product_category,
    
    -- Transaction Metrics (SQL: Aggregation)
    COUNT(t.transaction_key) AS transaction_count,
    SUM(t.amount) AS total_revenue,
    AVG(t.amount) AS avg_transaction_amount,
    COUNT(DISTINCT t.customer_key) AS unique_customers,
    
    -- Product Adoption (SQL: Calculation)
    COUNT(DISTINCT t.customer_key) * 1.0 / (
        SELECT COUNT(DISTINCT customer_key) FROM dim_customer
    ) AS product_adoption_rate,
    
    -- Product Profitability (Source: Python Profitability Analytics)
    AVG(cm.net_profit) AS avg_customer_profit,
    SUM(cm.net_profit) AS total_customer_profit,
    
    -- Product Risk (Source: Python Advanced Risk Analytics)
    AVG(CASE WHEN cm.risk_level = 'critical' THEN 4 
             WHEN cm.risk_level = 'high' THEN 3 
             WHEN cm.risk_level = 'medium' THEN 2 
             WHEN cm.risk_level = 'low' THEN 1 END) AS avg_risk_score,
    COUNT(DISTINCT CASE WHEN cm.risk_level IN ('high', 'critical') THEN cm.customer_key END) AS high_risk_customer_count
    
FROM fact_transactions t
JOIN dim_date d ON t.transaction_date = d.date
JOIN dim_product p ON t.product_type = p.product_type
LEFT JOIN fact_customer_metrics cm ON t.customer_key = cm.customer_key 
    AND cm.as_of_date = (
        SELECT MAX(as_of_date) FROM fact_customer_metrics
    )
GROUP BY 
    d.date_key, d.year, d.quarter, d.month, p.product_type, p.product_category;
