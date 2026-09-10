-- Credit Risk Distribution View
-- Purpose: Risk analytics and distribution
-- Single Source of Truth: Python Advanced Risk Analytics
-- This view aggregates pre-calculated risk metrics

CREATE OR REPLACE VIEW vw_risk_distribution AS
SELECT 
    d.date_key,
    d.year,
    d.quarter,
    d.month,
    
    -- Risk Level Distribution (Source: Python Advanced Risk Analytics)
    COUNT(DISTINCT CASE WHEN cm.risk_level = 'critical' THEN cm.customer_key END) AS critical_risk_count,
    COUNT(DISTINCT CASE WHEN cm.risk_level = 'high' THEN cm.customer_key END) AS high_risk_count,
    COUNT(DISTINCT CASE WHEN cm.risk_level = 'medium' THEN cm.customer_key END) AS medium_risk_count,
    COUNT(DISTINCT CASE WHEN cm.risk_level = 'low' THEN cm.customer_key END) AS low_risk_count,
    
    -- Risk Exposure (Source: Python Advanced Risk Analytics)
    SUM(CASE WHEN cm.risk_level = 'critical' THEN cm.exposure_amount END) AS critical_risk_exposure,
    SUM(CASE WHEN cm.risk_level = 'high' THEN cm.exposure_amount END) AS high_risk_exposure,
    SUM(CASE WHEN cm.risk_level = 'medium' THEN cm.exposure_amount END) AS medium_risk_exposure,
    SUM(CASE WHEN cm.risk_level = 'low' THEN cm.exposure_amount END) AS low_risk_exposure,
    
    -- Risk Trend (Source: Python Advanced Risk Analytics)
    COUNT(DISTINCT CASE WHEN cm.risk_trend = 'increasing' THEN cm.customer_key END) AS increasing_risk_count,
    COUNT(DISTINCT CASE WHEN cm.risk_trend = 'decreasing' THEN cm.customer_key END) AS decreasing_risk_count,
    COUNT(DISTINCT CASE WHEN cm.risk_trend = 'stable' THEN cm.customer_key END) AS stable_risk_count,
    
    -- Delinquency Distribution (Source: Python Advanced Risk Analytics)
    COUNT(DISTINCT CASE WHEN cm.days_past_due = 0 THEN cm.customer_key END) AS current_customers,
    COUNT(DISTINCT CASE WHEN cm.days_past_due BETWEEN 1 AND 30 THEN cm.customer_key END) AS dpd_30_customers,
    COUNT(DISTINCT CASE WHEN cm.days_past_due BETWEEN 31 AND 60 THEN cm.customer_key END) AS dpd_60_customers,
    COUNT(DISTINCT CASE WHEN cm.days_past_due BETWEEN 61 AND 90 THEN cm.customer_key END) AS dpd_90_customers,
    COUNT(DISTINCT CASE WHEN cm.days_past_due > 90 THEN cm.customer_key END) AS dpd_120_plus_customers,
    
    -- Utilization Distribution (Source: Python Advanced Risk Analytics)
    AVG(cm.credit_utilization) AS avg_utilization,
    COUNT(DISTINCT CASE WHEN cm.credit_utilization > 0.85 THEN cm.customer_key END) AS high_utilization_customers,
    
    -- Total Customers
    COUNT(DISTINCT cm.customer_key) AS total_customers
    
FROM fact_customer_metrics cm
JOIN dim_date d ON cm.as_of_date = d.date
GROUP BY 
    d.date_key, d.year, d.quarter, d.month;
