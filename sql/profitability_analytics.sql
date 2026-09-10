-- Profitability Analytics SQL Queries
-- Reusable analytical queries for profitability metrics with value type distinctions

-- ============================================================================
-- CUSTOMER-LEVEL PROFITABILITY VIEW
-- ============================================================================

CREATE OR REPLACE VIEW vw_customer_profitability AS
SELECT 
    cp.customer_key,
    c.customer_id,
    -- Revenue components (observed)
    COALESCE(cp.interest_income, 0) AS interest_income,
    'observed' AS interest_income_type,
    COALESCE(cp.fee_income, 0) AS fee_income,
    'observed' AS fee_income_type,
    COALESCE(cp.service_charge_income, 0) AS service_charge_income,
    'observed' AS service_charge_income_type,
    COALESCE(cp.product_revenue, 0) AS product_revenue,
    'observed' AS product_revenue_type,
    -- Gross revenue
    COALESCE(cp.interest_income, 0) + 
    COALESCE(cp.fee_income, 0) + 
    COALESCE(cp.service_charge_income, 0) + 
    COALESCE(cp.product_revenue, 0) AS gross_revenue,
    CASE 
        WHEN cp.interest_income IS NOT NULL OR cp.fee_income IS NOT NULL 
             OR cp.service_charge_income IS NOT NULL OR cp.product_revenue IS NOT NULL
        THEN 'observed'
        ELSE 'missing'
    END AS gross_revenue_type,
    -- Cost components
    COALESCE(cp.servicing_cost, 0) AS servicing_cost,
    'observed' AS servicing_cost_type,
    COALESCE(cp.operational_cost, 0) AS operational_cost,
    'estimated' AS operational_cost_type,
    COALESCE(cp.incentive_cost, 0) AS incentive_cost,
    'observed' AS incentive_cost_type,
    COALESCE(cp.expected_credit_loss, 0) AS expected_credit_loss,
    'modeled' AS expected_credit_loss_type,
    -- Total cost
    COALESCE(cp.servicing_cost, 0) + 
    COALESCE(cp.operational_cost, 0) + 
    COALESCE(cp.incentive_cost, 0) + 
    COALESCE(cp.expected_credit_loss, 0) AS total_cost,
    'estimated' AS total_cost_type,
    -- Profitability metrics
    (COALESCE(cp.interest_income, 0) + COALESCE(cp.fee_income, 0) + 
     COALESCE(cp.service_charge_income, 0) + COALESCE(cp.product_revenue, 0) -
     (COALESCE(cp.servicing_cost, 0) + COALESCE(cp.operational_cost, 0) + 
      COALESCE(cp.incentive_cost, 0) + COALESCE(cp.expected_credit_loss, 0))) AS net_profit,
    'estimated' AS net_profit_type,
    CASE 
        WHEN (COALESCE(cp.interest_income, 0) + COALESCE(cp.fee_income, 0) + 
              COALESCE(cp.service_charge_income, 0) + COALESCE(cp.product_revenue, 0)) != 0
        THEN ((COALESCE(cp.interest_income, 0) + COALESCE(cp.fee_income, 0) + 
               COALESCE(cp.service_charge_income, 0) + COALESCE(cp.product_revenue, 0) -
               (COALESCE(cp.servicing_cost, 0) + COALESCE(cp.operational_cost, 0) + 
                COALESCE(cp.incentive_cost, 0) + COALESCE(cp.expected_credit_loss, 0)))::numeric /
              (COALESCE(cp.interest_income, 0) + COALESCE(cp.fee_income, 0) + 
               COALESCE(cp.service_charge_income, 0) + COALESCE(cp.product_revenue, 0)) * 100)
        ELSE NULL
    END AS profit_margin,
    'estimated' AS profit_margin_type,
    -- Period metadata
    cp.period,
    cp.period_type
FROM fact_customer_profitability cp
LEFT JOIN dim_customer c ON cp.customer_key = c.customer_key
WHERE cp.period <= CURRENT_DATE;

-- ============================================================================
-- PRODUCT-LEVEL PROFITABILITY VIEW
-- ============================================================================

CREATE OR REPLACE VIEW vw_product_profitability AS
SELECT 
    p.product_key,
    p.product_name,
    p.product_category,
    -- Revenue components
    COALESCE(SUM(COALESCE(cp.interest_income, 0)), 0) AS interest_income,
    COALESCE(SUM(COALESCE(cp.fee_income, 0)), 0) AS fee_income,
    COALESCE(SUM(COALESCE(cp.service_charge_income, 0)), 0) AS service_charge_income,
    COALESCE(SUM(COALESCE(cp.product_revenue, 0)), 0) AS product_revenue,
    -- Gross revenue
    COALESCE(SUM(COALESCE(cp.interest_income, 0) + COALESCE(cp.fee_income, 0) + 
                COALESCE(cp.service_charge_income, 0) + COALESCE(cp.product_revenue, 0)), 0) AS gross_revenue,
    -- Cost components
    COALESCE(SUM(COALESCE(cp.servicing_cost, 0)), 0) AS servicing_cost,
    COALESCE(SUM(COALESCE(cp.operational_cost, 0)), 0) AS operational_cost,
    COALESCE(SUM(COALESCE(cp.incentive_cost, 0)), 0) AS incentive_cost,
    COALESCE(SUM(COALESCE(cp.expected_credit_loss, 0)), 0) AS expected_credit_loss,
    -- Total cost
    COALESCE(SUM(COALESCE(cp.servicing_cost, 0) + COALESCE(cp.operational_cost, 0) + 
                COALESCE(cp.incentive_cost, 0) + COALESCE(cp.expected_credit_loss, 0)), 0) AS total_cost,
    -- Profitability metrics
    COALESCE(SUM(COALESCE(cp.interest_income, 0) + COALESCE(cp.fee_income, 0) + 
                COALESCE(cp.service_charge_income, 0) + COALESCE(cp.product_revenue, 0) -
                (COALESCE(cp.servicing_cost, 0) + COALESCE(cp.operational_cost, 0) + 
                 COALESCE(cp.incentive_cost, 0) + COALESCE(cp.expected_credit_loss, 0)), 0) AS net_profit,
    CASE 
        WHEN COALESCE(SUM(COALESCE(cp.interest_income, 0) + COALESCE(cp.fee_income, 0) + 
                       COALESCE(cp.service_charge_income, 0) + COALESCE(cp.product_revenue, 0)), 0) != 0
        THEN (COALESCE(SUM(COALESCE(cp.interest_income, 0) + COALESCE(cp.fee_income, 0) + 
                          COALESCE(cp.service_charge_income, 0) + COALESCE(cp.product_revenue, 0) -
                          (COALESCE(cp.servicing_cost, 0) + COALESCE(cp.operational_cost, 0) + 
                           COALESCE(cp.incentive_cost, 0) + COALESCE(cp.expected_credit_loss, 0)), 0)::numeric /
              COALESCE(SUM(COALESCE(cp.interest_income, 0) + COALESCE(cp.fee_income, 0) + 
                          COALESCE(cp.service_charge_income, 0) + COALESCE(cp.product_revenue, 0)), 0)) * 100
        ELSE NULL
    END AS profit_margin
FROM fact_customer_profitability cp
JOIN dim_account a ON cp.account_key = a.account_key
JOIN dim_product p ON a.product_key = p.product_key
WHERE cp.period <= CURRENT_DATE
GROUP BY p.product_key, p.product_name, p.product_category;

-- ============================================================================
-- MONTHLY PROFITABILITY TRENDS VIEW
-- ============================================================================

CREATE OR REPLACE VIEW vw_monthly_profitability_trends AS
WITH monthly_profitability AS (
    SELECT 
        DATE_TRUNC('month', period)::date AS month,
        SUM(COALESCE(interest_income, 0) + COALESCE(fee_income, 0) + 
            COALESCE(service_charge_income, 0) + COALESCE(product_revenue, 0)) AS gross_revenue,
        SUM(COALESCE(servicing_cost, 0) + COALESCE(operational_cost, 0) + 
            COALESCE(incentive_cost, 0) + COALESCE(expected_credit_loss, 0)) AS total_cost,
        SUM(COALESCE(interest_income, 0) + COALESCE(fee_income, 0) + 
            COALESCE(service_charge_income, 0) + COALESCE(product_revenue, 0) -
            (COALESCE(servicing_cost, 0) + COALESCE(operational_cost, 0) + 
             COALESCE(incentive_cost, 0) + COALESCE(expected_credit_loss, 0))) AS net_profit
    FROM fact_customer_profitability
    WHERE period <= CURRENT_DATE
    GROUP BY DATE_TRUNC('month', period)
),
lagged_profitability AS (
    SELECT 
        month,
        gross_revenue,
        total_cost,
        net_profit,
        LAG(gross_revenue) OVER (ORDER BY month) AS prev_gross_revenue,
        LAG(total_cost) OVER (ORDER BY month) AS prev_total_cost,
        LAG(net_profit) OVER (ORDER BY month) AS prev_net_profit
    FROM monthly_profitability
)
SELECT 
    month,
    gross_revenue,
    total_cost,
    net_profit,
    prev_gross_revenue,
    prev_total_cost,
    prev_net_profit,
    CASE 
        WHEN prev_gross_revenue > 0 
        THEN ROUND((gross_revenue - prev_gross_revenue)::numeric / prev_gross_revenue * 100, 2)
        ELSE NULL 
    END AS revenue_growth_pct,
    CASE 
        WHEN prev_total_cost > 0 
        THEN ROUND((total_cost - prev_total_cost)::numeric / prev_total_cost * 100, 2)
        ELSE NULL 
    END AS cost_growth_pct,
    CASE 
        WHEN prev_net_profit > 0 
        THEN ROUND((net_profit - prev_net_profit)::numeric / prev_net_profit * 100, 2)
        ELSE NULL 
    END AS profit_growth_pct,
    CASE 
        WHEN gross_revenue > 0 
        THEN ROUND((net_profit::numeric / gross_revenue) * 100, 2)
        ELSE NULL 
    END AS profit_margin
FROM lagged_profitability
ORDER BY month;

-- ============================================================================
-- ANNUALIZED PROFITABILITY VIEW
-- ============================================================================

CREATE OR REPLACE VIEW vw_annualized_profitability AS
WITH monthly_stats AS (
    SELECT 
        DATE_TRUNC('month', period)::date AS month,
        SUM(COALESCE(interest_income, 0) + COALESCE(fee_income, 0) + 
            COALESCE(service_charge_income, 0) + COALESCE(product_revenue, 0)) AS gross_revenue,
        SUM(COALESCE(servicing_cost, 0) + COALESCE(operational_cost, 0) + 
            COALESCE(incentive_cost, 0) + COALESCE(expected_credit_loss, 0)) AS total_cost,
        SUM(COALESCE(interest_income, 0) + COALESCE(fee_income, 0) + 
            COALESCE(service_charge_income, 0) + COALESCE(product_revenue, 0) -
            (COALESCE(servicing_cost, 0) + COALESCE(operational_cost, 0) + 
             COALESCE(incentive_cost, 0) + COALESCE(expected_credit_loss, 0))) AS net_profit
    FROM fact_customer_profitability
    WHERE period <= CURRENT_DATE
    GROUP BY DATE_TRUNC('month', period)
)
SELECT 
    COUNT(*) AS months_available,
    ROUND(SUM(gross_revenue) * 12.0 / NULLIF(COUNT(*), 0), 2) AS annualized_gross_revenue,
    ROUND(SUM(total_cost) * 12.0 / NULLIF(COUNT(*), 0), 2) AS annualized_total_cost,
    ROUND(SUM(net_profit) * 12.0 / NULLIF(COUNT(*), 0), 2) AS annualized_net_profit,
    CASE 
        WHEN COUNT(*) >= 12 THEN 'observed'
        ELSE 'estimated'
    END AS value_type,
    ROUND(COUNT(*)::numeric / 12, 2) AS confidence,
    ROUND(STDDEV(net_profit), 2) AS monthly_net_profit_std,
    ROUND(AVG(net_profit), 2) AS monthly_net_profit_mean,
    CASE 
        WHEN AVG(net_profit) != 0 
        THEN ROUND(STDDEV(net_profit) / ABS(AVG(net_profit)), 2)
        ELSE NULL 
    END AS profit_cv
FROM monthly_stats;

-- ============================================================================
-- PROFITABILITY TIER CLASSIFICATION VIEW
-- ============================================================================

CREATE OR REPLACE VIEW vw_customer_profitability_tiers AS
SELECT 
    customer_key,
    customer_id,
    net_profit,
    profit_margin,
    CASE 
        WHEN net_profit >= 100000 AND profit_margin >= 25 THEN 'platinum'
        WHEN net_profit >= 50000 AND net_profit < 100000 AND profit_margin >= 15 THEN 'gold'
        WHEN net_profit >= 10000 AND net_profit < 50000 AND profit_margin >= 10 THEN 'silver'
        WHEN net_profit >= 0 AND net_profit < 10000 AND profit_margin >= 5 THEN 'bronze'
        WHEN net_profit < 0 THEN 'unprofitable'
        ELSE 'unknown'
    END AS profitability_tier,
    CASE 
        WHEN net_profit >= 100000 AND profit_margin >= 25 THEN 'Top-tier profitable customers'
        WHEN net_profit >= 50000 AND net_profit < 100000 AND profit_margin >= 15 THEN 'High-value profitable customers'
        WHEN net_profit >= 10000 AND net_profit < 50000 AND profit_margin >= 10 THEN 'Moderately profitable customers'
        WHEN net_profit >= 0 AND net_profit < 10000 AND profit_margin >= 5 THEN 'Low-margin profitable customers'
        WHEN net_profit < 0 THEN 'Unprofitable customers'
        ELSE 'Unknown tier'
    END AS tier_description
FROM vw_customer_profitability;

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_fact_customer_profitability_customer ON fact_customer_profitability(customer_key);
CREATE INDEX IF NOT EXISTS idx_fact_customer_profitability_period ON fact_customer_profitability(period);
CREATE INDEX IF NOT EXISTS idx_fact_customer_profitability_account ON fact_customer_profitability(account_key);

-- ============================================================================
-- COMMENTS ON VIEWS
-- ============================================================================

COMMENT ON VIEW vw_customer_profitability IS 'Customer-level profitability with revenue, cost, and profit metrics with value type distinctions';
COMMENT ON VIEW vw_product_profitability IS 'Product-level profitability aggregated from customer data';
COMMENT ON VIEW vw_monthly_profitability_trends IS 'Monthly profitability trends with period-over-period growth rates';
COMMENT ON VIEW vw_annualized_profitability IS 'Annualized profitability with variance statistics';
COMMENT ON VIEW vw_customer_profitability_tiers IS 'Customer profitability tier classification based on profit and margin thresholds';
