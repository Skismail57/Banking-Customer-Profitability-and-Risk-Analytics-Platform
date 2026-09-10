# Transaction KPIs Documentation

## Overview

This document defines all transaction Key Performance Indicators (KPIs) used in the banking analytics platform. These KPIs are designed to be reusable across different contexts (dashboards, reports, ML features) and avoid hardcoded dashboard-only calculations.

---

## Core Transaction KPIs

### 1. Transaction Count
**KPI ID**: `transaction_count`  
**Data Type**: numeric  
**Calculation**: `COUNT(transaction_id)`  
**Business Definition**: Total number of transactions in the analysis period

**Usage**:
- Overall transaction volume
- Customer activity level
- Channel performance comparison

**Temporal**: Yes - varies by time period

---

### 2. Transaction Value
**KPI ID**: `transaction_value`  
**Data Type**: currency  
**Calculation**: `SUM(amount)`  
**Business Definition**: Total monetary value of all transactions in the period

**Usage**:
- Revenue tracking
- Cash flow analysis
- Period-over-period comparison

**Temporal**: Yes - varies by time period

---

### 3. Average Transaction Value
**KPI ID**: `avg_transaction_value`  
**Data Type**: currency  
**Calculation**: `AVG(amount)`  
**Business Definition**: Mean transaction amount in the period

**Usage**:
- Customer spending patterns
- Transaction size analysis
- Benchmarking

**Temporal**: Yes - varies by time period

---

### 4. Median Transaction Value
**KPI ID**: `median_transaction_value`  
**Data Type**: currency  
**Calculation**: `MEDIAN(amount)`  
**Business Definition**: Median transaction amount (50th percentile)

**Usage**:
- Robust central tendency measure
- Less sensitive to outliers than mean
- Transaction size distribution analysis

**Temporal**: Yes - varies by time period

---

### 5. Transaction Frequency
**KPI ID**: `transaction_frequency`  
**Data Type**: numeric  
**Calculation**: `COUNT(transaction_id) / period_days`  
**Business Definition**: Average number of transactions per day

**Usage**:
- Customer engagement rate
- Activity level normalization
- Trend analysis

**Temporal**: Yes - varies by time period

---

## Flow Analysis KPIs

### 6. Total Inflow
**KPI ID**: `total_inflow`  
**Data Type**: currency  
**Calculation**: `SUM(amount WHERE amount > 0)`  
**Business Definition**: Sum of all positive transaction amounts (credits)

**Usage**:
- Income tracking
- Deposit analysis
- Cash inflow monitoring

**Temporal**: Yes - varies by time period

---

### 7. Outflow
**KPI ID**: `outflow`  
**Data Type**: currency  
**Calculation**: `SUM(ABS(amount) WHERE amount < 0)`  
**Business Definition**: Sum of absolute values of negative transactions (debits)

**Usage**:
- Spending analysis
- Withdrawal tracking
- Cash outflow monitoring

**Temporal**: Yes - varies by time period

---

### 8. Net Flow
**KPI ID**: `net_flow`  
**Data Type**: currency  
**Calculation**: `SUM(amount)` or `total_inflow - outflow`  
**Business Definition**: Net transaction amount (credits minus debits)

**Usage**:
- Balance change tracking
- Cash flow position
- Liquidity analysis

**Temporal**: Yes - varies by time period

---

## Debit/Credit KPIs

### 9. Debit Count
**KPI ID**: `debit_count`  
**Data Type**: numeric  
**Calculation**: `COUNT(amount < 0)`  
**Business Definition**: Number of debit transactions (negative amounts)

**Usage**:
- Spending frequency
- Withdrawal activity
- Channel usage patterns

**Temporal**: Yes - varies by time period

---

### 10. Credit Count
**KPI ID**: `credit_count`  
**Data Type**: numeric  
**Calculation**: `COUNT(amount > 0)`  
**Business Definition**: Number of credit transactions (positive amounts)

**Usage**:
- Deposit frequency
- Income activity
- Channel usage patterns

**Temporal**: Yes - varies by time period

---

### 11. Debit Value
**KPI ID**: `debit_value`  
**Data Type**: currency  
**Calculation**: `SUM(ABS(amount) WHERE amount < 0)`  
**Business Definition**: Total value of debit transactions

**Usage**:
- Total spending
- Withdrawal value
- Outflow analysis

**Temporal**: Yes - varies by time period

---

### 12. Credit Value
**KPI ID**: `credit_value`  
**Data Type**: currency  
**Calculation**: `SUM(amount WHERE amount > 0)`  
**Business Definition**: Total value of credit transactions

**Usage**:
- Total deposits
- Income value
- Inflow analysis

**Temporal**: Yes - varies by time period

---

## Derived KPIs

### 13. Debit to Credit Ratio
**KPI ID**: `debit_to_credit_ratio`  
**Data Type**: numeric  
**Calculation**: `debit_count / credit_count`  
**Business Definition**: Ratio of debit transactions to credit transactions

**Usage**:
- Spending vs saving behavior
- Transaction type balance
- Customer profile classification

**Temporal**: Yes - varies by time period

---

### 14. Credit to Debit Value Ratio
**KPI ID**: `credit_to_debit_value_ratio`  
**Data Type**: numeric  
**Calculation**: `credit_value / debit_value`  
**Business Definition**: Ratio of credit value to debit value

**Usage**:
- Cash flow balance
- Liquidity assessment
- Financial health indicator

**Temporal**: Yes - varies by time period

---

## Time-Based Aggregations

### Aggregation Periods

All transaction KPIs support aggregation at the following levels:

| Period | Description | Typical Use Case |
|--------|-------------|------------------|
| Daily | Day-level aggregation | Operational monitoring, daily dashboards |
| Weekly | Week-level aggregation | Short-term trend analysis |
| Monthly | Month-level aggregation | Monthly reporting, seasonality analysis |
| Quarterly | Quarter-level aggregation | Quarterly business reviews |
| Yearly | Year-level aggregation | Annual reporting, long-term trends |

### Temporal Safety

All KPI calculations include temporal safety:
- **Python**: `as_of_date` parameter filters data to prevent future data leakage
- **SQL**: `WHERE transaction_date <= CURRENT_DATE` clauses in all views

### Growth Metrics

#### Period-over-Period Growth
**Calculation**: `(current_value - previous_value) / previous_value * 100`

**Usage**:
- Trend analysis
- Performance tracking
- Anomaly detection

#### Moving Average
**Calculation**: `AVG(value OVER window ROWS BETWEEN n PRECEDING AND CURRENT ROW)`

**Usage**:
- Smoothing volatility
- Trend identification
- Forecasting

---

## Behavior Analysis KPIs

### Category Behavior

**Metrics per Transaction Category**:
- Transaction count
- Transaction value
- Average transaction value
- Median transaction value
- Standard deviation
- Inflow/outflow split
- Debit/credit count
- Value percentage of total

**Usage**:
- Category performance ranking
- Customer preference analysis
- Product mix optimization

---

### Channel Behavior

**Metrics per Channel**:
- Transaction count
- Transaction value
- Average transaction value
- Median transaction value
- Value percentage of total

**Usage**:
- Channel performance
- Digital adoption tracking
- Cost optimization

---

### Geographic Behavior

**Metrics per Location**:
- Transaction count
- Transaction value
- Average transaction value

**Usage**:
- Regional performance
- Market analysis
- Branch performance

---

## Anomaly Detection KPIs

### Amount Anomalies

**Detection Methods**:
- **IQR Method**: Values outside `Q1 - 3*IQR` or `Q3 + 3*IQR`
- **Z-Score Method**: Values with `|z-score| > 3`

**Metrics**:
- Anomaly count
- Anomaly percentage
- Anomaly type

**Usage**:
- Fraud detection
- Error identification
- Data quality monitoring

---

### Frequency Anomalies

**Detection Method**: Transactions per period exceeding `mean + 2*std`

**Metrics**:
- Anomaly count
- Affected customers
- Anomaly periods

**Usage**:
- Unusual activity detection
- Fraud monitoring
- System error detection

---

### Pattern Anomalies

**Detection Method**: High coefficient of variation (`std/mean > 2`) with sufficient transaction count

**Metrics**:
- Customers with unusual patterns
- Pattern severity

**Usage**:
- Behavioral profiling
- Risk assessment
- Customer segmentation

---

### Velocity Anomalies

**Detection Method**: Transactions within short time window (e.g., 60 minutes)

**Metrics**:
- Rapid transaction count
- Affected customers
- Time window violations

**Usage**:
- Fraud detection
- Anti-money laundering
- System abuse prevention

---

## Trend Analysis KPIs

### Trend Direction
**Values**: `increasing`, `decreasing`, `stable`

**Calculation**: Linear regression slope on time series

**Usage**:
- Trend classification
- Strategic planning
- Performance monitoring

---

### Growth Rate
**Calculation**: `(final_value / initial_value) - 1`

**Usage**:
- Compound growth tracking
- Performance comparison
- Forecasting

---

### Volatility
**Calculation**: `std(value) / mean(value)`

**Usage**:
- Risk assessment
- Stability analysis
- Forecasting accuracy

---

### Momentum
**Calculation**: `(recent_value - start_value) / start_value` over recent window

**Usage**:
- Short-term trend detection
- Momentum trading
- Performance acceleration

---

### Seasonality

**Detection Method**: Variance of seasonal means vs total variance

**Metrics**:
- Seasonal pattern by period
- Peak/trough periods
- Seasonality strength (0-1)

**Usage**:
- Seasonal planning
- Resource allocation
- Forecasting

---

## Usage Examples

### Python Implementation
```python
from src.transaction_analytics.orchestrator import TransactionAnalyticsOrchestrator
from datetime import date

# Initialize orchestrator
orchestrator = TransactionAnalyticsOrchestrator(as_of_date=date(2024, 1, 15))

# Generate comprehensive report
report = orchestrator.generate_comprehensive_report(
    df=transactions_df,
    date_column="transaction_date",
    amount_column="amount",
    customer_column="customer_key"
)

# Access KPIs
print(report["overall_kpis"]["transaction_count"])
print(report["overall_kpis"]["transaction_value"])
```

### SQL Implementation
```sql
-- Daily transaction KPIs
SELECT 
    period,
    transaction_count,
    transaction_value,
    avg_transaction_value,
    median_transaction_value,
    total_inflow,
    outflow,
    net_flow
FROM vw_transaction_kpis_daily
ORDER BY period DESC;
```

---

## Performance Considerations

### Python Implementation
- Use vectorized pandas operations
- Filter to relevant time windows before aggregation
- Index DataFrames on grouping columns
- Consider chunking for very large datasets

### SQL Implementation
- Views use LEFT JOINs for comprehensive coverage
- Indexes on date, customer, category, channel columns
- Window functions for trend calculations
- Materialized views for frequently accessed data

---

## Maintenance

### KPI Updates
- Add new KPIs by registering in `TransactionAnalyticsBase`
- Update business definitions as needed
- Modify calculation logic in appropriate modules
- Update SQL views to match Python logic

### Backward Compatibility
- Maintain existing KPI names when possible
- Deprecate old KPIs before removal
- Document breaking changes in version history
- Provide migration paths for dependent systems

---

## Glossary

- **KPI**: Key Performance Indicator
- **Inflow**: Positive transaction amounts (credits)
- **Outflow**: Negative transaction amounts (debits)
- **Net Flow**: Inflow minus outflow
- **Debit**: Negative transaction (withdrawal/spending)
- **Credit**: Positive transaction (deposit/income)
- **Temporal Safety**: Ensuring no future data leaks into historical calculations
- **IQR**: Interquartile Range (Q3 - Q1)
- **Z-Score**: Standard score indicating how many standard deviations from mean
- **Moving Average**: Average over sliding window of periods
- **Seasonality**: Regular pattern that repeats at fixed intervals
- **Volatility**: Degree of variation in time series
- **Momentum**: Rate of change in recent periods
