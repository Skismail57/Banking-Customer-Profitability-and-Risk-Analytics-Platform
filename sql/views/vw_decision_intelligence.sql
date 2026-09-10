-- Decision Intelligence View
-- Purpose: Recommendations from decision intelligence engine
-- Single Source of Truth: Python Decision Intelligence
-- This view formats pre-generated recommendations

CREATE OR REPLACE VIEW vw_decision_intelligence AS
SELECT 
    r.recommendation_key,
    r.customer_key,
    r.segment,
    r.generated_at,
    d.year,
    d.quarter,
    d.month,
    
    -- Recommendation Details (Source: Python Decision Intelligence)
    r.priority,
    r.confidence,
    r.recommended_action,
    r.reason,
    
    -- Triggering Metrics (Source: Python Decision Intelligence - JSON)
    r.triggering_metrics,
    
    -- Recommendation Type (SQL: Derived from action)
    CASE 
        WHEN r.recommended_action LIKE '%retention%' THEN 'Retention'
        WHEN r.recommended_action LIKE '%risk%' THEN 'Risk Management'
        WHEN r.recommended_action LIKE '%cross-sell%' THEN 'Cross-Sell'
        WHEN r.recommended_action LIKE '%review%' THEN 'Review'
        ELSE 'Other'
    END AS recommendation_type,
    
    -- Customer Context (Source: Python Analytics)
    cm.net_profit,
    cm.clv,
    cm.risk_level,
    cm.churn_probability,
    cm.exposure_amount
    
FROM fact_recommendations r
JOIN dim_date d ON r.generated_at = d.date
LEFT JOIN fact_customer_metrics cm ON r.customer_key = cm.customer_key 
    AND cm.as_of_date = r.generated_at;
