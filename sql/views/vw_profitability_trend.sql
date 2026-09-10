-- Customer Profitability Trend View
-- Purpose: Profitability analysis over time
-- Single Source of Truth: Python Profitability Analytics
-- This view aggregates pre-calculated profitability metrics

CREATE OR REPLACE VIEW vw_profitability_trend AS
SELECT 
    d.date_key,
    d.year,
    d.quarter,
    d.month,
    d.week,
    
    -- Profitability Metrics (Source: Python Profitability Analytics)
    SUM(cm.net_profit) AS total_net_profit,
    AVG(cm.net_profit) AS avg_profit_per_customer,
    SUM(cm.risk_adjusted_profit) AS total_risk_adjusted_profit,
    AVG(cm.risk_adjusted_profit) AS avg_risk_adjusted_profit,
    
    -- Profitability by Segment
    SUM(CASE WHEN cm.segment = 'premium' THEN cm.net_profit END) AS premium_profit,
    SUM(CASE WHEN cm.segment = 'standard' THEN cm.net_profit END) AS standard_profit,
    
    -- Profitability Distribution (Source: Python)
    COUNT(DISTINCT CASE WHEN cm.net_profit > 10000 THEN cm.customer_key END) AS high_profit_customers,
    COUNT(DISTINCT CASE WHEN cm.net_profit BETWEEN 1000 AND 10000 THEN cm.customer_key END) AS medium_profit_customers,
    COUNT(DISTINCT CASE WHEN cm.net_profit < 1000 THEN cm.customer_key END) AS low_profit_customers,
    
    -- Customer Count
    COUNT(DISTINCT cm.customer_key) AS customer_count
    
FROM fact_customer_metrics cm
JOIN dim_date d ON cm.as_of_date = d.date
GROUP BY 
    d.date_key, d.year, d.quarter, d.month, d.week;
