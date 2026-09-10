# Power BI Setup Guide

This guide explains how to connect Power BI to the Banking Analytics Platform and create reports based on the Decision Engine outputs.

## Architecture Connection

Power BI connects to the Decision Engine outputs stored in the database:

```
ML (Churn/CLV, Risk Models) → Decision Engine → fact_recommendations → Power BI
```

## Database Connection

### Connection String

```
Server=localhost;Database=banking_analytics;Port=5432;User Id=postgres;Password=your_password;
```

### Connection Steps

1. Open Power BI Desktop
2. Click "Get Data" → "Database" → "PostgreSQL database"
3. Enter server details:
   - Server: `localhost`
   - Database: `banking_analytics`
   - User: `postgres`
   - Password: (from .env file)
4. Click "Connect"

## Data Model

### Key Tables for Power BI

1. **fact_recommendations** - Decision Engine outputs
   - `customer_key` - Customer identifier
   - `segment` - Customer segment
   - `priority` - Recommendation priority (high, medium, low)
   - `confidence_level` - Confidence in recommendation
   - `recommended_action` - Action to take
   - `reason` - Why this recommendation
   - `triggering_metrics` - Metrics that triggered recommendation
   - `generated_at` - When recommendation was generated

2. **fact_customer_metrics** - Core Analytics outputs
   - `customer_key` - Customer identifier
   - `as_of_date` - Date of metrics
   - `net_profit` - Net profit
   - `risk_level` - Risk level (low, medium, high, critical)
   - `churn_probability` - Churn probability
   - `clv` - Customer lifetime value
   - `segment` - Customer segment

3. **dim_customer** - Customer dimension
   - `customer_key` - Customer identifier
   - `customer_id` - Customer ID
   - `customer_name` - Customer name
   - `segment` - Segment
   - `region` - Region

4. **fact_transactions** - Transaction data
   - `transaction_id` - Transaction ID
   - `customer_key` - Customer identifier
   - `transaction_date` - Transaction date
   - `amount` - Transaction amount
   - `transaction_type` - Transaction type

## Recommended Power BI Reports

### 1. Executive Overview Dashboard

**Purpose**: High-level view of bank performance and recommendations

**Visuals**:
- Total Customers (Card)
- Total Net Profit (Card)
- Total Recommendations (Card)
- High Priority Recommendations (Card)
- Risk Level Distribution (Pie Chart)
- Segment Performance (Bar Chart)
- Profit Trend (Line Chart)
- Top Recommendations by Priority (Table)

**Measures**:
- Total Customers = `DISTINCTCOUNT(fact_customer_metrics[customer_key])`
- Total Net Profit = `SUM(fact_customer_metrics[net_profit])`
- Total Recommendations = `COUNTROWS(fact_recommendations)`
- High Priority Recommendations = `CALCULATE(COUNTROWS(fact_recommendations), fact_recommendations[priority] = "high")`

### 2. Customer 360 Dashboard

**Purpose**: Detailed view of individual customers

**Visuals**:
- Customer Profile (Card)
- Profitability Metrics (Cards)
- Risk Metrics (Cards)
- Churn Probability (Gauge)
- CLV (Card)
- Transaction History (Line Chart)
- Recommendations (Table)

**Slicers**:
- Customer Selection

### 3. Recommendations Dashboard

**Purpose**: View and track recommendations from Decision Engine

**Visuals**:
- Recommendations by Priority (Donut Chart)
- Recommendations by Segment (Bar Chart)
- Recommendations by Confidence (Bar Chart)
- Top 10 Recommendations (Table)
- Recommendation Trends (Line Chart)

**Slicers**:
- Date Range
- Segment
- Priority
- Confidence Level

### 4. Risk Analytics Dashboard

**Purpose**: Monitor risk across the portfolio

**Visuals**:
- Risk Level Distribution (Pie Chart)
- High Risk Customers (Table)
- Risk by Segment (Stacked Bar Chart)
- Exposure by Risk Level (Treemap)
- Credit Utilization Distribution (Histogram)

### 5. Profitability Dashboard

**Purpose**: Track profitability across customers and segments

**Visuals**:
- Total Profit by Segment (Bar Chart)
- Profit Trend (Line Chart)
- Top Profitable Customers (Table)
- Profit Margin by Segment (Bar Chart)
- Risk-Adjusted Profit (Card)

## DAX Measures

### Customer Metrics

```
Total Customers = DISTINCTCOUNT(fact_customer_metrics[customer_key])

Total Net Profit = SUM(fact_customer_metrics[net_profit])

Avg Profit Per Customer = 
DIVIDE([Total Net Profit], [Total Customers])

Total CLV = SUM(fact_customer_metrics[clv])

Avg CLV = 
DIVIDE([Total CLV], [Total Customers])
```

### Risk Metrics

```
Critical Risk Customers = 
CALCULATE(
    DISTINCTCOUNT(fact_customer_metrics[customer_key]),
    fact_customer_metrics[risk_level] = "critical"
)

High Risk Customers = 
CALCULATE(
    DISTINCTCOUNT(fact_customer_metrics[customer_key]),
    fact_customer_metrics[risk_level] = "high"
)

Total Exposure = SUM(fact_customer_metrics[exposure_amount])

Avg Churn Probability = 
AVERAGE(fact_customer_metrics[churn_probability])
```

### Recommendation Metrics

```
Total Recommendations = COUNTROWS(fact_recommendations)

High Priority Recommendations = 
CALCULATE(
    COUNTROWS(fact_recommendations),
    fact_recommendations[priority] = "high"
)

Recommendations by Segment = 
COUNTROWS(fact_recommendations)

High Confidence Recommendations = 
CALCULATE(
    COUNTROWS(fact_recommendations),
    fact_recommendations[confidence_level] = "high"
)
```

## Relationships

```
dim_customer (customer_key) 1:* fact_customer_metrics (customer_key)
dim_customer (customer_key) 1:* fact_transactions (customer_key)
dim_customer (customer_key) 1:* fact_recommendations (customer_key)
fact_customer_metrics (customer_key) 1:* fact_recommendations (customer_key)
```

## Refresh Schedule

- **Data Refresh**: Daily (after pipeline run)
- **Incremental Refresh**: Enable for large tables
- **Gateway**: Configure Power BI Gateway for on-premises database

## Deployment

1. Publish to Power BI Service
2. Configure scheduled refresh
3. Set up workspace
4. Share with stakeholders
5. Set up alerts for key metrics

## Security

- Row-level security based on region/segment
- Role-based access control
- Data masking for sensitive fields

## Troubleshooting

### Connection Issues
- Verify database is running
- Check firewall settings
- Verify credentials

### Data Not Refreshing
- Check gateway status
- Verify refresh schedule
- Check data source credentials

### Performance Issues
- Use DirectQuery for large datasets
- Optimize DAX measures
- Use incremental refresh
