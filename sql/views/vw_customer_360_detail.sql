-- Customer 360 Detail View
-- Purpose: Comprehensive customer view for drill-through
-- Single Source of Truth: Python analytics modules
-- This view joins customer master with metrics

CREATE OR REPLACE VIEW vw_customer_360_detail AS
SELECT 
    c.customer_key,
    c.customer_id,
    c.customer_name,
    c.segment,
    c.region,
    c.acquisition_date,
    c.customer_age,
    c.income_level,
    
    -- Current Metrics (Source: Python Analytics)
    cm.as_of_date,
    cm.net_profit,
    cm.risk_adjusted_profit,
    cm.clv,
    cm.risk_level,
    cm.risk_trend,
    cm.churn_probability,
    cm.exposure_amount,
    cm.credit_utilization,
    cm.days_past_due,
    cm.credit_score,
    cm.balance_to_income_ratio,
    
    -- Tenure Calculation (SQL: Date difference)
    DATEDIFF(DAY, c.acquisition_date, GETDATE()) AS customer_tenure_days,
    FLOOR(DATEDIFF(DAY, c.acquisition_date, GETDATE()) / 365) AS customer_tenure_years,
    
    -- Tenure Band (SQL: Categorization)
    CASE 
        WHEN DATEDIFF(DAY, c.acquisition_date, GETDATE()) < 365 THEN '0-1 Years'
        WHEN DATEDIFF(DAY, c.acquisition_date, GETDATE()) < 1825 THEN '1-5 Years'
        WHEN DATEDIFF(DAY, c.acquisition_date, GETDATE()) < 3650 THEN '5-10 Years'
        ELSE '10+ Years'
    END AS tenure_band
    
FROM dim_customer c
LEFT JOIN fact_customer_metrics cm ON c.customer_key = cm.customer_key 
    AND cm.as_of_date = (
        SELECT MAX(as_of_date) FROM fact_customer_metrics
    );
