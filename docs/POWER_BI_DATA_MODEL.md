# Power BI Data Model Architecture

## Overview

This document defines the Power BI data model architecture, including the single source of truth for each metric, relationships between tables, and the philosophy for avoiding business logic duplication between Python, SQL, and Power BI.

---

## Single Source of Truth Philosophy

### Principle

**Business logic resides in Python analytics modules. SQL views are for data transformation and aggregation only. Power BI is for visualization.**

### Metric Ownership

| Metric Category | Single Source of Truth | Location | Power BI Role |
|----------------|----------------------|-----------|---------------|
| Customer Profitability | Python: `src/profitability_analytics/` | Database tables | Display only |
| Customer Lifetime Value | Python: `src/clv_analytics/` | Database tables | Display only |
| Credit Risk Level | Python: `src/advanced_risk_analytics/` | Database tables | Display only |
| Churn Probability | Python: `src/predictive_analytics/` | Database tables | Display only |
| Customer Segment | Python: `src/customer_segmentation/` | Database tables | Display only |
| Risk-Adjusted Profitability | Python: `src/advanced_risk_analytics/` | Database tables | Display only |
| Decision Intelligence | Python: `src/decision_intelligence/` | Database tables | Display only |
| Model Performance | Python: `src/predictive_analytics/` | Database tables | Display only |

### Business Logic Distribution

**Python Analytics Modules**:
- Calculate all metrics (profitability, CLV, risk, churn, segments)
- Apply business rules and thresholds
- Generate predictions and recommendations
- Write results to database tables

**SQL Views**:
- Join related tables
- Filter data for specific use cases
- Aggregate data for performance
- Create time-based snapshots
- Format data for Power BI consumption

**Power BI**:
- Display pre-calculated metrics
- Create visualizations
- Enable filtering and slicing
- Provide drill-down capabilities
- No business logic calculations

---

## Data Model Schema

### Core Tables

#### Fact Tables

1. **fact_customer_metrics** - Daily customer metrics snapshot
   - customer_key
   - as_of_date
   - net_profit
   - clv
   - risk_level
   - churn_probability
   - segment
   - exposure_amount
   - credit_utilization
   - days_past_due
   - credit_score
   - balance_to_income_ratio

2. **fact_transactions** - Transaction-level data
   - transaction_key
   - customer_key
   - transaction_date
   - amount
   - product_type
   - transaction_type
   - channel

3. **fact_recommendations** - Decision intelligence recommendations
   - recommendation_key
   - customer_key
   - segment
   - generated_at
   - priority
   - confidence
   - recommended_action
   - reason
   - triggering_metrics (JSON)

4. **fact_model_performance** - Model performance metrics
   - model_key
   - model_name
   - model_type
   - evaluated_at
   - accuracy
   - precision
   - recall
   - f1_score
   - roc_auc

#### Dimension Tables

1. **dim_customer** - Customer master
   - customer_key
   - customer_id
   - customer_name
   - segment
   - region
   - acquisition_date
   - customer_age
   - income_level

2. **dim_date** - Date dimension
   - date_key
   - date
   - year
   - quarter
   - month
   - week
   - day_of_week
   - is_holiday

3. **dim_product** - Product dimension
   - product_key
   - product_type
   - product_category
   - product_name
   - interest_rate

4. **dim_segment** - Segment dimension
   - segment_key
   - segment_name
   - segment_description
   - avg_profitability
   - avg_risk_level

### Relationships

```
fact_customer_metrics
  ├── dim_customer (customer_key)
  ├── dim_date (as_of_date)
  └── dim_segment (segment)

fact_transactions
  ├── dim_customer (customer_key)
  ├── dim_date (transaction_date)
  └── dim_product (product_type)

fact_recommendations
  ├── dim_customer (customer_key)
  └── dim_date (generated_at)

fact_model_performance
  └── dim_date (evaluated_at)
```

---

## Analytical Views

### View Naming Convention

**Format**: `vw_<area>_<purpose>`

**Examples**:
- `vw_executive_overview_kpi`
- `vw_customer_360_detail`
- `vw_profitability_trend`
- `vw_risk_distribution`

### View Categories

1. **Executive Overview** - High-level KPIs for executives
2. **Customer 360** - Comprehensive customer view
3. **Customer Profitability** - Profitability analysis
4. **Credit Risk** - Risk analytics
5. **Customer Segmentation** - Segment analysis
6. **Churn & Retention** - Churn analysis
7. **Product Analytics** - Product performance
8. **Transaction Analytics** - Transaction analysis
9. **Decision Intelligence** - Recommendations
10. **Model Monitoring** - Model performance

---

## KPI Measures

### Executive Overview KPIs

| KPI | Source | Calculation Location | Power BI Measure |
|-----|--------|---------------------|------------------|
| Total Customers | Python: Customer count | Python | SUM(fact_customer_metrics.customer_count) |
| Total Profitability | Python: Profitability | Python | SUM(fact_customer_metrics.net_profit) |
| Average Risk Level | Python: Risk level | Python | AVERAGE(fact_customer_metrics.risk_score) |
| Churn Rate | Python: Churn probability | Python | AVERAGE(fact_customer_metrics.churn_probability) |
| Total Exposure | Python: Exposure | Python | SUM(fact_customer_metrics.exposure_amount) |

### Customer 360 KPIs

| KPI | Source | Calculation Location | Power BI Measure |
|-----|--------|---------------------|------------------|
| Customer Profitability | Python: Profitability | Python | SELECTEDVALUE(fact_customer_metrics.net_profit) |
| Customer CLV | Python: CLV | Python | SELECTEDVALUE(fact_customer_metrics.clv) |
| Customer Risk Level | Python: Risk level | Python | SELECTEDVALUE(fact_customer_metrics.risk_level) |
| Customer Segment | Python: Segment | Python | SELECTEDVALUE(fact_customer_metrics.segment) |
| Customer Tenure | SQL: Date diff | SQL | DATEDIFF(dim_customer.acquisition_date, TODAY()) |

### Customer Profitability KPIs

| KPI | Source | Calculation Location | Power BI Measure |
|-----|--------|---------------------|------------------|
| Net Profit | Python: Profitability | Python | SUM(fact_customer_metrics.net_profit) |
| Risk-Adjusted Profit | Python: Risk-adjusted | Python | SUM(fact_customer_metrics.risk_adjusted_profit) |
| Profit Margin | SQL: Calculation | SQL | SUM(net_profit) / SUM(revenue) |
| Profit Trend | SQL: YoY change | SQL | (Current - Previous) / Previous |

### Credit Risk KPIs

| KPI | Source | Calculation Location | Power BI Measure |
|-----|--------|---------------------|------------------|
| Risk Level Distribution | Python: Risk level | Python | COUNT(fact_customer_metrics) BY risk_level |
| High Risk Customers | Python: Risk level | Python | COUNT(fact_customer_metrics) WHERE risk_level IN ('high', 'critical') |
| Exposure Concentration | Python: HHI | Python | SELECTEDVALUE(fact_customer_metrics.hhi) |
| Delinquency Rate | Python: DPD | Python | COUNT(fact_customer_metrics) WHERE dpd > 30 / COUNT(all) |

### Customer Segmentation KPIs

| KPI | Source | Calculation Location | Power BI Measure |
|-----|--------|---------------------|------------------|
| Segment Size | Python: Segment | Python | COUNT(fact_customer_metrics) BY segment |
| Segment Profitability | Python: Profitability | Python | AVG(fact_customer_metrics.net_profit) BY segment |
| Segment Risk Profile | Python: Risk level | Python | AVG(fact_customer_metrics.risk_score) BY segment |
| Segment Churn Rate | Python: Churn | Python | AVG(fact_customer_metrics.churn_probability) BY segment |

### Churn & Retention KPIs

| KPI | Source | Calculation Location | Power BI Measure |
|-----|--------|---------------------|------------------|
| Churn Probability | Python: Churn model | Python | AVG(fact_customer_metrics.churn_probability) |
| High Churn Customers | Python: Churn model | Python | COUNT(fact_customer_metrics) WHERE churn_probability > 0.7 |
| Retention Rate | SQL: Calculation | SQL | 1 - AVG(churn_probability) |
| Churn by Segment | Python: Churn model | Python | AVG(fact_customer_metrics.churn_probability) BY segment |

### Product Analytics KPIs

| KPI | Source | Calculation Location | Power BI Measure |
|-----|--------|---------------------|------------------|
| Product Revenue | SQL: Aggregation | SQL | SUM(fact_transactions.amount) BY product_type |
| Product Adoption | SQL: Count | SQL | COUNT(DISTINCT customer_key) BY product_type |
| Product Profitability | Python: Profitability | Python | AVG(fact_customer_metrics.net_profit) BY product_type |
| Product Risk | Python: Risk level | Python | AVG(fact_customer_metrics.risk_score) BY product_type |

### Transaction Analytics KPIs

| KPI | Source | Calculation Location | Power BI Measure |
|-----|--------|---------------------|------------------|
| Transaction Volume | SQL: Count | SQL | COUNT(fact_transactions) |
| Transaction Value | SQL: Sum | SQL | SUM(fact_transactions.amount) |
| Average Transaction | SQL: Avg | SQL | AVG(fact_transactions.amount) |
| Transaction Trend | SQL: YoY change | SQL | (Current - Previous) / Previous |

### Decision Intelligence KPIs

| KPI | Source | Calculation Location | Power BI Measure |
|-----|--------|---------------------|------------------|
| Critical Recommendations | Python: Decision Intel | Python | COUNT(fact_recommendations) WHERE priority = 'critical' |
| High Confidence Recommendations | Python: Decision Intel | Python | COUNT(fact_recommendations) WHERE confidence = 'high' |
| Recommendation Adoption | SQL: Tracking | SQL | COUNT(adopted) / COUNT(total) |
| Action Completion Rate | SQL: Tracking | SQL | COUNT(completed) / COUNT(total) |

### Model Monitoring KPIs

| KPI | Source | Calculation Location | Power BI Measure |
|-----|--------|---------------------|------------------|
| Model Accuracy | Python: Evaluation | Python | AVG(fact_model_performance.accuracy) |
| Model Precision | Python: Evaluation | Python | AVG(fact_model_performance.precision) |
| Model Recall | Python: Evaluation | Python | AVG(fact_model_performance.recall) |
| Model Drift | SQL: Comparison | SQL | Current accuracy - Previous accuracy |

---

## Dimensions

### Customer Dimensions

- **Customer Key** - Unique identifier
- **Customer Name** - Display name
- **Segment** - Customer segment
- **Region** - Geographic region
- **Tenure** - Customer tenure bucket
- **Income Level** - Income category
- **Age Band** - Age group

### Time Dimensions

- **Date** - Full date
- **Year** - Calendar year
- **Quarter** - Calendar quarter
- **Month** - Calendar month
- **Week** - Calendar week
- **Day of Week** - Day name

### Product Dimensions

- **Product Type** - Product category
- **Product Name** - Product name
- **Interest Rate Band** - Interest rate range

### Risk Dimensions

- **Risk Level** - Low/Medium/High/Critical
- **Risk Trend** - Increasing/Decreasing/Stable
- **Delinquency Bucket** - Current/30/60/90/120+
- **Utilization Band** - Utilization range

---

## Drill-Down Hierarchies

### Customer Hierarchy

```
Segment
  └── Region
      └── Customer
```

### Time Hierarchy

```
Year
  └── Quarter
      └── Month
          └── Day
```

### Product Hierarchy

```
Product Category
  └── Product Type
      └── Product Name
```

### Risk Hierarchy

```
Risk Level
  └── Risk Trend
      └── Delinquency Bucket
```

---

## Filters and Slicers

### Executive Overview

**Slicers**:
- Date Range
- Segment
- Region

**Filters**:
- Risk Level
- Product Type

### Customer 360

**Slicers**:
- Customer Selector
- Date Range

**Filters**:
- Segment
- Risk Level

### Customer Profitability

**Slicers**:
- Date Range
- Segment
- Region
- Product Type

**Filters**:
- Profitability Band
- Risk Level

### Credit Risk

**Slicers**:
- Date Range
- Segment
- Region

**Filters**:
- Risk Level
- Delinquency Bucket
- Utilization Band

### Customer Segmentation

**Slicers**:
- Date Range
- Segment
- Region

**Filters**:
- Profitability Band
- Risk Level

### Churn & Retention

**Slicers**:
- Date Range
- Segment
- Region

**Filters**:
- Churn Probability Band
- CLV Band

### Product Analytics

**Slicers**:
- Date Range
- Product Type
- Product Category

**Filters**:
- Segment
- Region

### Transaction Analytics

**Slicers**:
- Date Range
- Product Type
- Channel

**Filters**:
- Transaction Type
- Amount Band

### Decision Intelligence

**Slicers**:
- Date Range
- Segment
- Priority
- Confidence

**Filters**:
- Recommendation Type
- Risk Level

### Model Monitoring

**Slicers**:
- Date Range
- Model Name
- Model Type

**Filters**:
- Performance Threshold
- Drift Threshold

---

## Tooltips

### Standard Tooltips

- **Customer Key**
- **Customer Name**
- **Segment**
- **Risk Level**
- **Profitability**
- **CLV**
- **Churn Probability**

### Context-Specific Tooltips

**Profitability Tooltip**:
- Net Profit
- Risk-Adjusted Profit
- Profit Margin
- Profit Trend

**Risk Tooltip**:
- Risk Level
- Risk Trend
- Utilization
- DPD
- Credit Score

**Churn Tooltip**:
- Churn Probability
- CLV
- Tenure
- Segment

---

## Drill-Through Pages

### Customer 360 Drill-Through

**From**: Executive Overview, Customer Segmentation

**To**: Customer 360 Detail Page

**Fields**:
- Customer Key
- Customer Name
- Segment
- Region

**Content**:
- Customer profile
- Profitability trend
- Risk trajectory
- Transaction history
- Recommendations

### Transaction Detail Drill-Through

**From**: Transaction Analytics, Product Analytics

**To**: Transaction Detail Page

**Fields**:
- Transaction Key
- Customer Key
- Transaction Date

**Content**:
- Transaction details
- Customer context
- Product information
- Channel information

### Recommendation Detail Drill-Through

**From**: Decision Intelligence

**To**: Recommendation Detail Page

**Fields**:
- Recommendation Key
- Customer Key
- Priority

**Content**:
- Recommendation details
- Triggering metrics
- Limitations
- Action history

### Model Performance Drill-Through

**From**: Model Monitoring

**To**: Model Detail Page

**Fields**:
- Model Key
- Model Name
- Evaluated At

**Content**:
- Model metrics
- Feature importance
- Confusion matrix
- ROC curve

---

## Performance Optimization

### View Optimization

1. **Materialized Views** - For heavy aggregations
2. **Indexed Views** - For frequently accessed data
3. **Partitioned Views** - For time-series data
4. **Incremental Refresh** - For large datasets

### Power BI Optimization

1. **Import Mode** - For static data
2. **DirectQuery** - For real-time data
3. **Composite Models** - Mix of import and DirectQuery
4. **Aggregations** - Pre-aggregated data for performance

---

## Security

### Row-Level Security

- **Segment-based** - Users see only their segment
- **Region-based** - Users see only their region
- **Role-based** - Different access levels

### Data Protection

- **PII Masking** - Sensitive customer data
- **Profitability Data** - Restricted access
- **Risk Data** - Restricted access
