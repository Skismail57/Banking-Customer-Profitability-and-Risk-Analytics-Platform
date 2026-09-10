-- Executive Overview KPI View
-- Purpose: High-level KPIs for executive dashboard
-- Single Source of Truth: Python analytics modules
-- This view only aggregates and formats pre-calculated metrics

CREATE OR REPLACE VIEW vw_executive_overview_kpi AS
SELECT 
    d.date_key,
    d.year,
    d.quarter,
    d.month,
    
    -- Customer Metrics (Source: Python Customer Analytics)
    COUNT(DISTINCT cm.customer_key) AS total_customers,
    COUNT(DISTINCT CASE WHEN cm.segment = 'premium' THEN cm.customer_key END) AS premium_customers,
    COUNT(DISTINCT CASE WHEN cm.segment = 'standard' THEN cm.customer_key END) AS standard_customers,
    
    -- Profitability Metrics (Source: Python Profitability Analytics)
    SUM(cm.net_profit) AS total_net_profit,
    AVG(cm.net_profit) AS avg_profit_per_customer,
    SUM(cm.risk_adjusted_profit) AS total_risk_adjusted_profit,
    
    -- Risk Metrics (Source: Python Advanced Risk Analytics)
    COUNT(DISTINCT CASE WHEN cm.risk_level = 'critical' THEN cm.customer_key END) AS critical_risk_customers,
    COUNT(DISTINCT CASE WHEN cm.risk_level = 'high' THEN cm.customer_key END) AS high_risk_customers,
    COUNT(DISTINCT CASE WHEN cm.risk_level = 'medium' THEN cm.customer_key END) AS medium_risk_customers,
    COUNT(DISTINCT CASE WHEN cm.risk_level = 'low' THEN cm.customer_key END) AS low_risk_customers,
    
    -- Churn Metrics (Source: Python Predictive Analytics)
    AVG(cm.churn_probability) AS avg_churn_probability,
    COUNT(DISTINCT CASE WHEN cm.churn_probability > 0.7 THEN cm.customer_key END) AS high_churn_risk_customers,
    
    -- Exposure Metrics (Source: Python Advanced Risk Analytics)
    SUM(cm.exposure_amount) AS total_exposure,
    AVG(cm.exposure_amount) AS avg_exposure_per_customer,
    
    -- CLV Metrics (Source: Python CLV Analytics)
    SUM(cm.clv) AS total_clv,
    AVG(cm.clv) AS avg_clv_per_customer
    
FROM fact_customer_metrics cm
JOIN dim_date d ON cm.as_of_date = d.date
WHERE cm.as_of_date = (
    SELECT MAX(as_of_date) FROM fact_customer_metrics
)
GROUP BY 
    d.date_key, d.year, d.quarter, d.month;
