-- Churn & Retention Analysis View
-- Purpose: Churn and retention analytics
-- Single Source of Truth: Python Predictive Analytics (Churn Model)
-- This view aggregates pre-calculated churn metrics

CREATE OR REPLACE VIEW vw_churn_retention AS
SELECT 
    d.date_key,
    d.year,
    d.quarter,
    d.month,
    
    -- Churn Metrics (Source: Python Predictive Analytics)
    AVG(cm.churn_probability) AS avg_churn_probability,
    COUNT(DISTINCT CASE WHEN cm.churn_probability > 0.7 THEN cm.customer_key END) AS high_churn_risk_count,
    COUNT(DISTINCT CASE WHEN cm.churn_probability BETWEEN 0.5 AND 0.7 THEN cm.customer_key END) AS medium_churn_risk_count,
    COUNT(DISTINCT CASE WHEN cm.churn_probability < 0.5 THEN cm.customer_key END) AS low_churn_risk_count,
    
    -- Churn by Segment (Source: Python Predictive Analytics)
    AVG(CASE WHEN cm.segment = 'premium' THEN cm.churn_probability END) AS premium_churn_prob,
    AVG(CASE WHEN cm.segment = 'standard' THEN cm.churn_probability END) AS standard_churn_prob,
    
    -- High Churn + High CLV (Source: Python Predictive Analytics + CLV Analytics)
    COUNT(DISTINCT CASE WHEN cm.churn_probability > 0.7 AND cm.clv > 10000 THEN cm.customer_key END) AS high_churn_high_clv_count,
    
    -- Retention Rate (SQL: Derived from churn probability)
    1 - AVG(cm.churn_probability) AS estimated_retention_rate,
    
    -- Churn by Risk Level (Source: Python Advanced Risk Analytics + Predictive Analytics)
    AVG(CASE WHEN cm.risk_level = 'critical' THEN cm.churn_probability END) AS critical_risk_churn_prob,
    AVG(CASE WHEN cm.risk_level = 'high' THEN cm.churn_probability END) AS high_risk_churn_prob,
    AVG(CASE WHEN cm.risk_level = 'medium' THEN cm.churn_probability END) AS medium_risk_churn_prob,
    AVG(CASE WHEN cm.risk_level = 'low' THEN cm.churn_probability END) AS low_risk_churn_prob,
    
    -- Total Customers
    COUNT(DISTINCT cm.customer_key) AS total_customers
    
FROM fact_customer_metrics cm
JOIN dim_date d ON cm.as_of_date = d.date
GROUP BY 
    d.date_key, d.year, d.quarter, d.month;
