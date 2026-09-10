# Customer 360 Metrics Documentation

## Overview

Customer 360 provides a unified, comprehensive view of each customer by aggregating data from across the banking platform. This document defines all metrics calculated for the Customer 360 view, including their business definitions, calculation methods, and temporal considerations.

---

## Temporal Safety

All Customer 360 metrics are calculated with temporal safety to prevent future data leakage. An `as_of_date` parameter is used to ensure only data available as of that date is included in calculations.

**Implementation**:
- Python: `Customer360Base.ensure_temporal_safety()` filters DataFrames to as_of_date
- SQL: Views use `WHERE date_column <= CURRENT_DATE` clauses

---

## Metric Categories

### 1. Demographic Features

Static and slowly-changing customer profile attributes.

| Metric | Data Type | Temporal | Description | Business Definition |
|--------|-----------|----------|-------------|---------------------|
| age | numeric | Yes | Customer age in years | Age calculated from birth_date relative to as_of_date |
| age_group | categorical | Yes | Age category | 18-25, 26-35, 36-45, 46-55, 56-65, 65+, under_18 |
| gender | categorical | No | Customer gender | Gender as recorded in customer profile |
| marital_status | categorical | No | Marital status | single, married, divorced, widowed, etc. |
| education_level | categorical | No | Highest education | high school, bachelor, master, phd, etc. |
| occupation | categorical | No | Occupation | Occupation or industry of employment |
| annual_income | numeric | No | Annual household income | Total annual income in local currency |
| income_bracket | categorical | No | Income category | under_25k, 25k-50k, 50k-75k, 75k-100k, 100k-150k, 150k+ |
| tenure_years | numeric | Yes | Years as customer | Time since customer onboarding in years |
| tenure_group | categorical | Yes | Tenure category | new (<1yr), established (1-3yr), loyal (3-5yr), veteran (5yr+) |
| is_active | boolean | Yes | Active status flag | Whether customer is currently active |

**Calculation Notes**:
- Age: `(as_of_date - birth_date) / 365.25`
- Tenure: `(as_of_date - customer_since) / 365.25`
- Age and tenure groups use fixed bin boundaries

---

### 2. Account Features

Customer account ownership and balance metrics.

| Metric | Data Type | Temporal | Description | Business Definition |
|--------|-----------|----------|-------------|---------------------|
| account_count | numeric | Yes | Total accounts | Count of all accounts (active and inactive) |
| active_account_count | numeric | Yes | Active accounts | Count of accounts with is_active=true |
| total_balance | numeric | Yes | Total balance | Sum of balances from all accounts |
| average_balance | numeric | Yes | Average balance | Mean balance across all accounts |
| total_credit_limit | numeric | Yes | Total credit limit | Sum of credit limits for credit products |
| product_diversity | numeric | Yes | Product diversity | Count of unique product categories |
| products_owned | categorical | Yes | Product list | Comma-separated list of product categories |

**Calculation Notes**:
- Account counts include both active and inactive accounts
- Product diversity counts unique product categories (deposits, loans, cards)
- Products owned is a string concatenation of categories

---

### 3. Transaction Features

Customer transaction behavior metrics over time windows.

| Metric | Data Type | Temporal | Window | Description | Business Definition |
|--------|-----------|----------|--------|-------------|---------------------|
| transaction_count_30d | numeric | Yes | 30 days | Transaction count | Number of transactions in last 30 days |
| transaction_count_90d | numeric | Yes | 90 days | Transaction count | Number of transactions in last 90 days |
| transaction_volume_30d | numeric | Yes | 30 days | Transaction value | Sum of transaction amounts in last 30 days |
| transaction_volume_90d | numeric | Yes | 90 days | Transaction value | Sum of transaction amounts in last 90 days |
| avg_transaction_amount_30d | numeric | Yes | 30 days | Average transaction | Mean transaction amount in 30-day window |
| avg_transaction_amount_90d | numeric | Yes | 90 days | Average transaction | Mean transaction amount in 90-day window |
| transaction_frequency_30d | numeric | Yes | 30 days | Daily rate | Transactions per day in 30-day window |
| transaction_frequency_90d | numeric | Yes | 90 days | Daily rate | Transactions per day in 90-day window |
| days_since_last_transaction | numeric | Yes | N/A | Recency metric | Days since most recent transaction |
| transaction_recency_score | numeric | Yes | N/A | Normalized recency | Score (0-1) based on last transaction |

**Calculation Notes**:
- Transaction count: `COUNT(transaction_id)` within window
- Transaction volume: `SUM(amount)` within window
- Average amount: `AVG(amount)` within window
- Frequency: `COUNT / window_days`
- Days since last: `as_of_date - MAX(transaction_date)`
- Recency score: `MAX(0, 1 - (days_since_last / window_days))`
- Customers with no transactions: count=0, volume=0, days_since_last=999, recency_score=0

---

### 4. Loan Features

Customer loan exposure and credit utilization metrics.

| Metric | Data Type | Temporal | Description | Business Definition |
|--------|-----------|----------|-------------|---------------------|
| loan_count | numeric | Yes | Active loans | Count of active loan accounts |
| total_loan_exposure | numeric | Yes | Outstanding balance | Sum of current balances across all loans |
| total_credit_limit | numeric | Yes | Credit limit | Sum of credit limits for credit products |
| credit_utilization | numeric | Yes | Utilization ratio | Ratio of used credit to total credit limit |
| days_past_due_max | numeric | Yes | Worst delinquency | Maximum days past due across all loans |
| has_delinquent_loans | boolean | Yes | Delinquency flag | Flag for any loans with days_past_due > 0 |

**Calculation Notes**:
- Loan count: `COUNT(loan_id)` for active loans
- Total exposure: `SUM(current_balance)` across loans
- Credit utilization: `total_loan_exposure / total_credit_limit` (capped at 1)
- Days past due max: `MAX(days_past_due)` across loans
- Delinquency flag: `days_past_due_max > 0`
- Customers with no loans: all metrics set to 0

---

### 5. Interaction Features

Customer service interaction and complaint metrics.

| Metric | Data Type | Temporal | Window | Description | Business Definition |
|--------|-----------|----------|--------|-------------|---------------------|
| interaction_count_90d | numeric | Yes | 90 days | Interaction count | Number of customer service interactions |
| avg_satisfaction_score | numeric | Yes | 90 days | Satisfaction | Mean satisfaction score (1-5 scale) |
| has_complaints | boolean | Yes | 90 days | Complaint flag | Whether customer has logged complaints |
| complaint_count_90d | numeric | Yes | 90 days | Complaint count | Number of complaint-type interactions |

**Calculation Notes**:
- Interaction count: `COUNT(interaction_id)` within window
- Satisfaction score: `AVG(satisfaction_score)` within window
- Complaint count: `COUNT(interaction_id)` where category='complaint'
- Complaint flag: `complaint_count > 0`
- Customers with no interactions: count=0, satisfaction=0, complaints=0

---

### 6. Profitability Features

Customer profitability metrics over 12-month periods.

| Metric | Data Type | Temporal | Window | Description | Business Definition |
|--------|-----------|----------|--------|-------------|---------------------|
| net_profit_12m | numeric | Yes | 12 months | Net profit | Total revenue minus total costs |
| profit_margin_12m | numeric | Yes | 12 months | Profit margin | Net profit divided by revenue |
| avg_balance_12m | numeric | Yes | 12 months | Average balance | Mean daily balance over 12 months |

**Calculation Notes**:
- Net profit: `interest_income + fee_income - cost_of_funds - operating_costs`
- Profit margin: `net_profit / (interest_income + fee_income)` (0 if no revenue)
- Average balance: From profitability fact table
- Uses latest 12-month period available as of as_of_date
- Customers with no profitability data: all metrics set to 0

---

### 7. Risk Features

Customer risk assessment metrics.

| Metric | Data Type | Temporal | Description | Business Definition |
|--------|-----------|----------|-------------|---------------------|
| credit_score | numeric | Yes | Credit score | FICO or equivalent credit score (300-850) |
| credit_score_trend | numeric | Yes | Score change | Credit score change over last 12 months |
| total_exposure | numeric | Yes | Total exposure | Total outstanding credit across all products |
| probability_of_default | numeric | Yes | PD | Model-calculated probability of default (0-1) |
| risk_level | categorical | Yes | Risk category | low, medium, high, critical |
| is_on_watchlist | boolean | Yes | Watchlist flag | Flag for customers requiring special monitoring |

**Calculation Notes**:
- Credit score: Latest available score
- Credit score trend: `current_score - score_12_months_ago`
- Total exposure: Sum of outstanding balances
- PD: Model-calculated probability of default
- Risk level: Categorical classification based on PD and other factors
- Watchlist: Manual or automated flag for high-risk customers
- Customers with no risk data: score=0, trend=0, exposure=0, PD=0, level=unknown

---

## Feature Registry

All features are registered with metadata including:

- **Name**: Unique feature identifier
- **Category**: Feature category (demographic, account, transaction, loan, interaction, profitability, risk)
- **Description**: Human-readable description
- **Data Type**: numeric, categorical, datetime, boolean
- **Is Temporal**: Whether feature changes over time
- **Requires Historical Data**: Whether feature needs historical data
- **Calculation Window Days**: Window size for temporal features
- **Business Definition**: Business meaning of the feature

---

## Temporal Window Calculations

### Window Start Calculation
```python
window_start = as_of_date - timedelta(days=window_days)
```

### SQL Equivalent
```sql
WHERE date_column >= CURRENT_DATE - INTERVAL '90 days'
```

### Partitioned Windows
For time-series analysis, time can be partitioned into multiple windows:
- Window 1: [as_of_date - 90 days, as_of_date - 60 days]
- Window 2: [as_of_date - 60 days, as_of_date - 30 days]
- Window 3: [as_of_date - 30 days, as_of_date]

This enables trend analysis and feature engineering for time-series models.

---

## Data Quality Considerations

### Missing Value Handling
- **Numeric features**: Filled with 0
- **Categorical features**: Filled with "unknown"
- **Boolean features**: Filled with False
- **Date features**: Filled with as_of_date or NULL

### Edge Cases
- **No transactions**: Transaction metrics set to 0, recency set to 999 days
- **No accounts**: Account metrics set to 0
- **No loans**: Loan metrics set to 0
- **No interactions**: Interaction metrics set to 0
- **No profitability data**: Profitability metrics set to 0
- **No risk data**: Risk metrics set to default/unknown values

### Negative Values
- Transaction amounts can be negative (withdrawals, debits)
- Balances should be non-negative (validated in data quality)
- Credit limits should be non-negative (validated in data quality)
- Days past due should be non-negative (validated in data quality)

---

## Usage Examples

### Python Implementation
```python
from src.customer_intelligence.orchestrator import Customer360Orchestrator
from datetime import date

# Initialize orchestrator with as_of_date
orchestrator = Customer360Orchestrator(as_of_date=date(2024, 1, 15))

# Generate Customer 360 features
customer_360_df = orchestrator.generate_customer_360(
    customers_df=customers_df,
    accounts_df=accounts_df,
    transactions_df=transactions_df,
    loans_df=loans_df,
    interactions_df=interactions_df,
    profitability_df=profitability_df,
    risk_df=risk_df,
    transaction_window_days=90
)

# Get feature registry
registry = orchestrator.get_feature_registry()

# Get features by category
transaction_features = orchestrator.get_features_by_category(FeatureCategory.TRANSACTION)
```

### SQL Implementation
```sql
-- Query comprehensive Customer 360 view
SELECT 
    customer_id,
    age,
    account_count,
    transaction_count_30d,
    transaction_volume_30d,
    credit_utilization,
    credit_score,
    net_profit_12m
FROM vw_customer_360
WHERE is_active = true
ORDER BY net_profit_12m DESC;
```

---

## Feature Engineering for ML

### RFM Features
- **Recency**: `days_since_last_transaction` or `transaction_recency_score`
- **Frequency**: `transaction_frequency_30d` or `transaction_count_90d`
- **Monetary**: `transaction_volume_90d` or `avg_transaction_amount_30d`

### Behavioral Features
- Tenure-based: `tenure_years`, `tenure_group`
- Product-based: `product_diversity`, `products_owned`
- Engagement-based: `interaction_count_90d`, `complaint_count_90d`

### Risk Features
- Credit-based: `credit_score`, `credit_score_trend`
- Exposure-based: `total_loan_exposure`, `credit_utilization`
- Delinquency-based: `days_past_due_max`, `has_delinquent_loans`

### Profitability Features
- Revenue-based: `net_profit_12m`
- Efficiency-based: `profit_margin_12m`
- Balance-based: `avg_balance_12m`

---

## Performance Considerations

### Python Implementation
- Use vectorized pandas operations for aggregations
- Filter to relevant time windows before aggregation
- Merge DataFrames on indexed columns for performance
- Consider chunking for very large datasets

### SQL Implementation
- Views use LEFT JOINs to include all customers
- Indexes on customer_key and customer_id for performance
- Window functions for latest period selection
- Materialized views for frequently accessed data

---

## Maintenance

### Feature Updates
- Add new features by registering in appropriate extractor
- Update business definitions as needed
- Modify calculation logic in extractor methods
- Update SQL views to match Python logic

### Backward Compatibility
- Maintain existing feature names when possible
- Deprecate old features before removal
- Document breaking changes in version history
- Provide migration paths for dependent systems

---

## Glossary

- **As-of-date**: Reference date for temporal calculations
- **Temporal safety**: Ensuring no future data leaks into historical features
- **Window**: Time period for aggregating temporal features
- **Recency**: How recently a customer performed an action
- **Frequency**: How often a customer performs an action
- **Monetary**: Value of customer transactions
- **Exposure**: Total credit extended to customer
- **Utilization**: Ratio of used credit to available credit
- **Delinquency**: Late payment status
- **PD**: Probability of Default
- **LGD**: Loss Given Default
