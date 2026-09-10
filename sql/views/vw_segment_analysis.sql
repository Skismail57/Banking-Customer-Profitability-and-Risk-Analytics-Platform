-- Customer Segmentation Analysis View
-- Purpose: Segment-level analysis
-- Single Source of Truth: Python Customer Segmentation
-- This view aggregates pre-calculated segment metrics

CREATE OR REPLACE VIEW vw_segment_analysis AS
SELECT 
    d.date_key,
    d.year,
    d.quarter,
    d.month,
    cm.segment,
    
    -- Segment Size (Source: Python Customer Segmentation)
    COUNT(DISTINCT cm.customer_key) AS segment_customer_count,
    
    -- Segment Profitability (Source: Python Profitability Analytics)
    SUM(cm.net_profit) AS segment_total_profit,
    AVG(cm.net_profit) AS segment_avg_profit,
    SUM(cm.risk_adjusted_profit) AS segment_risk_adjusted_profit,
    
    -- Segment Risk Profile (Source: Python Advanced Risk Analytics)
    AVG(CASE WHEN cm.risk_level = 'critical' THEN 4 
             WHEN cm.risk_level = 'high' THEN 3 
             WHEN cm.risk_level = 'medium' THEN 2 
             WHEN cm.risk_level = 'low' THEN 1 END) AS segment_avg_risk_score,
    COUNT(DISTINCT CASE WHEN cm.risk_level IN ('high', 'critical') THEN cm.customer_key END) AS segment_high_risk_count,
    
    -- Segment Churn Profile (Source: Python Predictive Analytics)
    AVG(cm.churn_probability) AS segment_avg_churn_probability,
    COUNT(DISTINCT CASE WHEN cm.churn_probability > 0.7 THEN cm.customer_key END) AS segment_high_churn_count,
    
    -- Segment CLV (Source: Python CLV Analytics)
    SUM(cm.clv) AS segment_total_clv,
    AVG(cm.clv) AS segment_avg_clv,
    
    -- Segment Exposure (Source: Python Advanced Risk Analytics)
    SUM(cm.exposure_amount) AS segment_total_exposure,
    AVG(cm.exposure_amount) AS segment_avg_exposure
    
FROM fact_customer_metrics cm
JOIN dim_date d ON cm.as_of_date = d.date
GROUP BY 
    d.date_key, d.year, d.quarter, d.month, cm.segment;
