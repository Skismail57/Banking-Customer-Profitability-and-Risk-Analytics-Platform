-- Model Monitoring View
-- Purpose: Model performance tracking
-- Single Source of Truth: Python Predictive Analytics (Model Evaluation)
-- This view formats pre-calculated model performance metrics

CREATE OR REPLACE VIEW vw_model_monitoring AS
SELECT 
    mp.model_key,
    mp.model_name,
    mp.model_type,
    mp.evaluated_at,
    d.year,
    d.quarter,
    d.month,
    
    -- Model Performance Metrics (Source: Python Predictive Analytics)
    mp.accuracy,
    mp.precision,
    mp.recall,
    mp.f1_score,
    mp.roc_auc,
    
    -- Model Trend (SQL: Comparison with previous evaluation)
    LAG(mp.accuracy) OVER (PARTITION BY mp.model_name ORDER BY mp.evaluated_at) AS previous_accuracy,
    mp.accuracy - LAG(mp.accuracy) OVER (PARTITION BY mp.model_name ORDER BY mp.evaluated_at) AS accuracy_change,
    
    -- Model Drift Indicator (SQL: Threshold check)
    CASE 
        WHEN ABS(mp.accuracy - LAG(mp.accuracy) OVER (PARTITION BY mp.model_name ORDER BY mp.evaluated_at)) > 0.05 
        THEN 'Drift Detected'
        ELSE 'Stable'
    END AS drift_status,
    
    -- Performance Thresholds (SQL: Derived)
    CASE 
        WHEN mp.accuracy >= 0.85 THEN 'Excellent'
        WHEN mp.accuracy >= 0.75 THEN 'Good'
        WHEN mp.accuracy >= 0.65 THEN 'Fair'
        ELSE 'Poor'
    END AS performance_rating
    
FROM fact_model_performance mp
JOIN dim_date d ON mp.evaluated_at = d.date;
