# Power BI Implementation Guide

## Overview

This guide provides step-by-step instructions for implementing the Power BI dashboard for the Banking Customer Profitability and Risk Analytics Platform. The guide covers data model setup, report creation, visualization best practices, and maintenance procedures.

---

## Prerequisites

### Required Tools

- Power BI Desktop (latest version)
- Power BI Service (for publishing)
- SQL Server or compatible database
- Python analytics pipeline (to populate fact tables)

### Required Access

- Database read access for fact and dimension tables
- Access to SQL views
- Power BI Service workspace access

---

## Step 1: Data Model Setup

### 1.1 Connect to Data Source

1. Open Power BI Desktop
2. Click **Get Data** → **SQL Server**
3. Enter server name and database name
4. Select **Import** mode (recommended for performance)
5. Click **Connect**

### 1.2 Import Tables

Import the following tables in order:

**Dimension Tables**:
1. `dim_customer`
2. `dim_date`
3. `dim_product`
4. `dim_segment`

**Fact Tables**:
1. `fact_customer_metrics`
2. `fact_transactions`
3. `fact_recommendations`
4. `fact_model_performance`

**Views** (for optimized queries):
1. `vw_executive_overview_kpi`
2. `vw_customer_360_detail`
3. `vw_profitability_trend`
4. `vw_risk_distribution`
5. `vw_segment_analysis`
6. `vw_churn_retention`
7. `vw_product_analytics`
8. `vw_transaction_analytics`
9. `vw_decision_intelligence`
10. `vw_model_monitoring`

### 1.3 Define Relationships

In Power BI Desktop, go to **Model View** and create the following relationships:

**fact_customer_metrics Relationships**:
- `customer_key` → `dim_customer.customer_key` (Many-to-One, Active)
- `as_of_date` → `dim_date.date` (Many-to-One, Active)
- `segment` → `dim_segment.segment_name` (Many-to-One, Active)

**fact_transactions Relationships**:
- `customer_key` → `dim_customer.customer_key` (Many-to-One, Active)
- `transaction_date` → `dim_date.date` (Many-to-One, Active)
- `product_type` → `dim_product.product_type` (Many-to-One, Active)

**fact_recommendations Relationships**:
- `customer_key` → `dim_customer.customer_key` (Many-to-One, Active)
- `generated_at` → `dim_date.date` (Many-to-One, Active)

**fact_model_performance Relationships**:
- `evaluated_at` → `dim_date.date` (Many-to-One, Active)

### 1.4 Set Data Types

Ensure correct data types for key columns:

**Date Columns**: Date
**Numeric Columns**: Decimal Number
**Text Columns**: Text
**Boolean Columns**: True/False

---

## Step 2: Create Measures

### 2.1 Executive Overview Measures

```dax
-- Total Customers
Total Customers = DISTINCTCOUNT(fact_customer_metrics[customer_key])

-- Total Net Profit
Total Net Profit = SUM(fact_customer_metrics[net_profit])

-- Average Profit Per Customer
Avg Profit Per Customer = DIVIDE([Total Net Profit], [Total Customers])

-- Total Risk-Adjusted Profit
Total Risk Adjusted Profit = SUM(fact_customer_metrics[risk_adjusted_profit])

-- Critical Risk Customers
Critical Risk Customers = CALCULATE(
    [Total Customers],
    fact_customer_metrics[risk_level] = "critical"
)

-- High Churn Risk Customers
High Churn Risk Customers = CALCULATE(
    [Total Customers],
    fact_customer_metrics[churn_probability] > 0.7
)

-- Total Exposure
Total Exposure = SUM(fact_customer_metrics[exposure_amount])

-- Average Churn Probability
Avg Churn Probability = AVERAGE(fact_customer_metrics[churn_probability])

-- Total CLV
Total CLV = SUM(fact_customer_metrics[clv])
```

### 2.2 Customer 360 Measures

```dax
-- Selected Customer Profit
Selected Customer Profit = SELECTEDVALUE(fact_customer_metrics[net_profit])

-- Selected Customer CLV
Selected Customer CLV = SELECTEDVALUE(fact_customer_metrics[clv])

-- Selected Customer Risk Level
Selected Customer Risk Level = SELECTEDVALUE(fact_customer_metrics[risk_level])

-- Customer Tenure (Days)
Customer Tenure Days = DATEDIFF(
    SELECTEDVALUE(dim_customer[acquisition_date]),
    TODAY(),
    DAY
)

-- Customer Tenure (Years)
Customer Tenure Years = DIVIDE([Customer Tenure Days], 365)
```

### 2.3 Profitability Measures

```dax
-- Profit Margin
Profit Margin = DIVIDE(
    [Total Net Profit],
    SUM(fact_customer_metrics[revenue])
)

-- Profit Trend (YoY)
Profit Trend YoY = DIVIDE(
    [Total Net Profit] - CALCULATE([Total Net Profit], SAMEPERIODLASTYEAR(dim_date[date])),
    CALCULATE([Total Net Profit], SAMEPERIODLASTYEAR(dim_date[date]))
)

-- High Profit Customers
High Profit Customers = CALCULATE(
    [Total Customers],
    fact_customer_metrics[net_profit] > 10000
)
```

### 2.4 Risk Measures

```dax
-- High Risk Customers
High Risk Customers = CALCULATE(
    [Total Customers],
    fact_customer_metrics[risk_level] IN {"high", "critical"}
)

-- Delinquency Rate
Delinquency Rate = DIVIDE(
    CALCULATE([Total Customers], fact_customer_metrics[days_past_due] > 30),
    [Total Customers]
)

-- Risk Concentration (HHI)
Risk Concentration HHI = SELECTEDVALUE(fact_customer_metrics[hhi])

-- High Utilization Customers
High Utilization Customers = CALCULATE(
    [Total Customers],
    fact_customer_metrics[credit_utilization] > 0.85
)
```

### 2.5 Churn Measures

```dax
-- Retention Rate
Retention Rate = 1 - [Avg Churn Probability]

-- Churn by Segment
Churn by Segment = AVERAGE(fact_customer_metrics[churn_probability])

-- High Churn High CLV Customers
High Churn High CLV = CALCULATE(
    [Total Customers],
    fact_customer_metrics[churn_probability] > 0.7 && fact_customer_metrics[clv] > 10000
)
```

### 2.6 Product Measures

```dax
-- Total Product Revenue
Total Product Revenue = SUM(fact_transactions[amount])

-- Product Adoption Rate
Product Adoption Rate = DIVIDE(
    DISTINCTCOUNT(fact_transactions[customer_key]),
    [Total Customers]
)

-- Avg Transaction Amount
Avg Transaction Amount = AVERAGE(fact_transactions[amount])

-- Transaction Volume
Transaction Volume = COUNT(fact_transactions[transaction_key])
```

### 2.7 Decision Intelligence Measures

```dax
-- Critical Recommendations
Critical Recommendations = CALCULATE(
    COUNT(fact_recommendations[recommendation_key]),
    fact_recommendations[priority] = "critical"
)

-- High Confidence Recommendations
High Confidence Recommendations = CALCULATE(
    COUNT(fact_recommendations[recommendation_key]),
    fact_recommendations[confidence] = "high"
)

-- Total Recommendations
Total Recommendations = COUNT(fact_recommendations[recommendation_key])
```

### 2.8 Model Monitoring Measures

```dax
-- Model Accuracy
Model Accuracy = AVERAGE(fact_model_performance[accuracy])

-- Model Drift
Model Drift = [Model Accuracy] - CALCULATE(
    [Model Accuracy],
    SAMEPERIODLASTYEAR(dim_date[date])
)

-- Performance Rating
Performance Rating = SWITCH(
    TRUE(),
    [Model Accuracy] >= 0.85, "Excellent",
    [Model Accuracy] >= 0.75, "Good",
    [Model Accuracy] >= 0.65, "Fair",
    "Poor"
)
```

---

## Step 3: Create Report Pages

### 3.1 Executive Overview Page

**Purpose**: High-level KPIs for executives

**Visualizations**:
1. **KPI Cards** (Top row):
   - Total Customers
   - Total Net Profit
   - Total Exposure
   - Avg Churn Probability

2. **Risk Level Distribution** (Donut chart):
   - Field: `fact_customer_metrics[risk_level]`
   - Measure: `Total Customers`

3. **Profit Trend** (Line chart):
   - Axis: `dim_date[month]`
   - Value: `Total Net Profit`

4. **Segment Performance** (Clustered bar chart):
   - Axis: `dim_segment[segment_name]`
   - Value: `Total Net Profit`
   - Value: `Total Customers`

5. **High Risk Customers** (Table):
   - Columns: Customer Name, Segment, Risk Level, Exposure, Profit

**Slicers**:
- Date Range (using `dim_date[date]`)
- Segment (using `dim_segment[segment_name]`)
- Region (using `dim_customer[region]`)

---

### 3.2 Customer 360 Page

**Purpose**: Comprehensive customer view

**Visualizations**:
1. **Customer Selector** (Slicer):
   - Field: `dim_customer[customer_name]`

2. **Customer Profile Card**:
   - Customer Name
   - Segment
   - Region
   - Tenure
   - Risk Level

3. **Profitability Trend** (Line chart):
   - Axis: `dim_date[month]`
   - Value: `Selected Customer Profit`

4. **Risk Trajectory** (Line chart):
   - Axis: `dim_date[month]`
   - Value: Risk Level (categorical)

5. **Transaction History** (Table):
   - Columns: Date, Amount, Product Type, Channel

6. **Recommendations** (Table):
   - Columns: Priority, Action, Reason, Date

**Drill-through**:
- From Executive Overview → Customer 360
- From Customer Segmentation → Customer 360

---

### 3.3 Customer Profitability Page

**Purpose**: Profitability analysis

**Visualizations**:
1. **Profitability KPIs** (Cards):
   - Total Net Profit
   - Avg Profit Per Customer
   - Profit Margin
   - Profit Trend YoY

2. **Profitability by Segment** (Stacked bar chart):
   - Axis: `dim_segment[segment_name]`
   - Value: `Total Net Profit`

3. **Profitability Distribution** (Histogram):
   - Field: `fact_customer_metrics[net_profit]`

4. **Profitability Trend** (Area chart):
   - Axis: `dim_date[month]`
   - Value: `Total Net Profit`

5. **Risk-Adjusted Profit** (Scatter plot):
   - X-axis: Risk Level
   - Y-axis: Net Profit
   - Size: Exposure

**Slicers**:
- Date Range
- Segment
- Region
- Product Type

---

### 3.4 Credit Risk Page

**Purpose**: Risk analytics

**Visualizations**:
1. **Risk KPIs** (Cards):
   - High Risk Customers
   - Critical Risk Customers
   - Total Exposure
   - Delinquency Rate

2. **Risk Level Distribution** (Donut chart):
   - Field: `fact_customer_metrics[risk_level]`

3. **Risk Trend** (Line chart):
   - Axis: `dim_date[month]`
   - Value: High Risk Customers

4. **Delinquency Distribution** (Funnel chart):
   - Field: Delinquency Bucket

5. **Exposure by Risk Level** (Treemap):
   - Group: Risk Level
   - Values: Exposure

6. **Risk Concentration** (Gauge):
   - Value: Risk Concentration HHI

**Slicers**:
- Date Range
- Segment
- Region
- Risk Level

---

### 3.5 Customer Segmentation Page

**Purpose**: Segment analysis

**Visualizations**:
1. **Segment KPIs** (Cards):
   - Total Segments
   - Largest Segment
   - Segment Profitability
   - Segment Churn Rate

2. **Segment Size** (Pie chart):
   - Field: `dim_segment[segment_name]`
   - Value: `Total Customers`

3. **Segment Profitability** (Ribbon chart):
   - Axis: `dim_segment[segment_name]`
   - Value: `Total Net Profit`

4. **Segment Risk Profile** (Stacked bar chart):
   - Axis: `dim_segment[segment_name]`
   - Legend: Risk Level
   - Value: `Total Customers`

5. **Segment Churn** (Line chart):
   - Axis: `dim_segment[segment_name]`
   - Value: `Avg Churn Probability`

**Slicers**:
- Date Range
- Segment
- Region

---

### 3.6 Churn & Retention Page

**Purpose**: Churn analysis

**Visualizations**:
1. **Churn KPIs** (Cards):
   - Avg Churn Probability
   - High Churn Risk Customers
   - Retention Rate
   - High Churn High CLV

2. **Churn Distribution** (Histogram):
   - Field: `fact_customer_metrics[churn_probability]`

3. **Churn by Segment** (Clustered bar chart):
   - Axis: `dim_segment[segment_name]`
   - Value: `Avg Churn Probability`

4. **Churn vs Risk** (Scatter plot):
   - X-axis: Risk Level
   - Y-axis: Churn Probability
   - Size: CLV

5. **Retention Trend** (Line chart):
   - Axis: `dim_date[month]`
   - Value: `Retention Rate`

**Slicers**:
- Date Range
- Segment
- Region
- Churn Probability Band

---

### 3.7 Product Analytics Page

**Purpose**: Product performance

**Visualizations**:
1. **Product KPIs** (Cards):
   - Total Product Revenue
   - Product Adoption Rate
   - Avg Transaction Amount
   - Transaction Volume

2. **Product Revenue** (Column chart):
   - Axis: `dim_product[product_type]`
   - Value: `Total Product Revenue`

3. **Product Adoption** (Funnel chart):
   - Field: `dim_product[product_type]`
   - Value: `Product Adoption Rate`

4. **Product Risk** (Scatter plot):
   - X-axis: Product Type
   - Y-axis: Avg Risk Score
   - Size: Revenue

5. **Transaction Trend** (Line chart):
   - Axis: `dim_date[month]`
   - Value: `Transaction Volume`

**Slicers**:
- Date Range
- Product Type
- Product Category

---

### 3.8 Transaction Analytics Page

**Purpose**: Transaction analysis

**Visualizations**:
1. **Transaction KPIs** (Cards):
   - Transaction Volume
   - Total Transaction Value
   - Avg Transaction Amount
   - Unique Customers

2. **Transaction Trend** (Line chart):
   - Axis: `dim_date[month]`
   - Value: `Total Transaction Value`

3. **Transaction by Type** (Donut chart):
   - Field: `fact_transactions[transaction_type]`

4. **Transaction by Channel** (Stacked bar chart):
   - Axis: `dim_date[month]`
   - Legend: Channel
   - Value: `Transaction Volume`

5. **Transaction Value Distribution** (Histogram):
   - Field: `fact_transactions[amount]`

**Slicers**:
- Date Range
- Product Type
- Channel
- Transaction Type

---

### 3.9 Decision Intelligence Page

**Purpose**: Recommendations

**Visualizations**:
1. **Recommendation KPIs** (Cards):
   - Critical Recommendations
   - High Confidence Recommendations
   - Total Recommendations
   - Action Completion Rate

2. **Recommendations by Priority** (Donut chart):
   - Field: `fact_recommendations[priority]`

3. **Recommendations by Type** (Clustered bar chart):
   - Axis: Recommendation Type
   - Value: `Total Recommendations`

4. **Recommendation Trend** (Line chart):
   - Axis: `dim_date[month]`
   - Value: `Total Recommendations`

5. **Recommendation List** (Table):
   - Columns: Customer, Priority, Action, Reason, Confidence, Date

**Slicers**:
- Date Range
- Segment
- Priority
- Confidence
- Recommendation Type

---

### 3.10 Model Monitoring Page

**Purpose**: Model performance tracking

**Visualizations**:
1. **Model KPIs** (Cards):
   - Model Accuracy
   - Model Precision
   - Model Recall
   - Model Drift

2. **Model Performance Trend** (Line chart):
   - Axis: `dim_date[month]`
   - Values: Accuracy, Precision, Recall

3. **Model Comparison** (Ribbon chart):
   - Axis: Model Name
   - Value: Accuracy

4. **Drift Status** (Gauge):
   - Value: Model Drift

5. **Performance Rating** (Card):
   - Value: `Performance Rating`

**Slicers**:
- Date Range
- Model Name
- Model Type

---

## Step 4: Configure Drill-Through

### 4.1 Customer 360 Drill-Through

1. Go to Customer 360 page
2. Click **Drill-through** in the Visualizations pane
3. Add fields:
   - `dim_customer[customer_key]`
   - `dim_customer[customer_name]`
   - `dim_segment[segment_name]`

4. Enable drill-through from:
   - Executive Overview
   - Customer Segmentation

### 4.2 Transaction Detail Drill-Through

1. Create Transaction Detail page
2. Add drill-through fields:
   - `fact_transactions[transaction_key]`
   - `fact_transactions[customer_key]`
   - `dim_date[date]`

3. Enable drill-through from:
   - Transaction Analytics
   - Product Analytics

### 4.3 Recommendation Detail Drill-Through

1. Create Recommendation Detail page
2. Add drill-through fields:
   - `fact_recommendations[recommendation_key]`
   - `fact_recommendations[customer_key]`
   - `fact_recommendations[priority]`

3. Enable drill-through from:
   - Decision Intelligence

### 4.4 Model Detail Drill-Through

1. Create Model Detail page
2. Add drill-through fields:
   - `fact_model_performance[model_key]`
   - `fact_model_performance[model_name]`
   - `dim_date[date]`

3. Enable drill-through from:
   - Model Monitoring

---

## Step 5: Configure Tooltips

### 5.1 Standard Tooltip Page

Create a tooltip page with the following fields:

- Customer Key
- Customer Name
- Segment
- Risk Level
- Profitability
- CLV
- Churn Probability

### 5.2 Context-Specific Tooltips

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

## Step 6: Configure Row-Level Security

### 6.1 Create Roles

1. Go to **Modeling** → **Manage Roles**
2. Create roles:
   - **Segment Manager**: Filter by segment
   - **Regional Manager**: Filter by region
   - **Executive**: Full access

### 6.2 Define Role Filters

**Segment Manager Role**:
```dax
[segment] = USERPRINCIPALNAME()
```

**Regional Manager Role**:
```dax
[region] = USERPRINCIPALNAME()
```

### 6.3 Test Roles

1. Click **View as Roles**
2. Select role to test
3. Verify data is filtered correctly

---

## Step 7: Publish to Power BI Service

### 7.1 Publish Report

1. Click **Publish** in Power BI Desktop
2. Select workspace
3. Click **Publish**

### 7.2 Configure Dataset

1. Go to Power BI Service
2. Select dataset
3. Configure refresh schedule
4. Set credentials for data source

### 7.3 Create App

1. Go to workspace
2. Click **Create app**
3. Configure app settings
4. Add users/groups
5. Publish app

---

## Step 8: Maintenance

### 8.1 Regular Updates

**Daily**:
- Data refresh (automated)
- Monitor refresh failures

**Weekly**:
- Review model performance
- Check for data quality issues

**Monthly**:
- Review recommendation effectiveness
- Update thresholds if needed
- Review user feedback

**Quarterly**:
- Full model retraining
- Threshold recalibration
- Report optimization

### 8.2 Performance Optimization

**Data Model**:
- Use Import mode for large datasets
- Create aggregations for DirectQuery
- Optimize relationships
- Remove unused columns

**Report**:
- Limit visual count per page
- Use appropriate visual types
- Optimize DAX measures
- Use incremental refresh

### 8.3 Monitoring

**Refresh Monitoring**:
- Monitor refresh history
- Set up refresh failure alerts
- Track refresh duration

**Usage Monitoring**:
- Track report usage
- Monitor performance
- Identify popular pages

**Data Quality**:
- Monitor null values
- Check for outliers
- Validate data ranges

---

## Best Practices

### Data Model

1. **Star Schema**: Use star schema for optimal performance
2. **Single Source of Truth**: All business logic in Python, not in Power BI
3. **Relationships**: Use single-direction relationships
4. **Data Types**: Ensure correct data types for all columns

### DAX Measures

1. **Naming**: Use descriptive measure names
2. **Variables**: Use variables for complex calculations
3. **Error Handling**: Handle division by zero
4. **Performance**: Use CALCULATE efficiently

### Visualizations

1. **Clarity**: Keep visualizations simple and clear
2. **Consistency**: Use consistent formatting
3. **Color**: Use color meaningfully
4. **Labels**: Label axes and legends clearly

### Security

1. **RLS**: Implement row-level security
2. **PII**: Mask sensitive customer data
3. **Access**: Grant minimum necessary access
4. **Audit**: Track user activity

---

## Troubleshooting

### Common Issues

**Refresh Failures**:
- Check data source credentials
- Verify network connectivity
- Review error messages
- Check for schema changes

**Performance Issues**:
- Reduce data volume
- Optimize DAX measures
- Use aggregations
- Check visual complexity

**Data Quality Issues**:
- Validate source data
- Check for null values
- Review data transformations
- Monitor data ranges

**Security Issues**:
- Verify RLS roles
- Check user permissions
- Review data masking
- Test with different users

---

## Appendix

### DAX Measure Reference

See Section 2 for complete DAX measure definitions.

### SQL View Reference

See `docs/POWER_BI_DATA_MODEL.md` for SQL view definitions.

### Single Source of Truth

See `docs/POWER_BI_DATA_MODEL.md` for metric ownership and business logic distribution.

---

## Support

For issues or questions:
1. Check this guide
2. Review data model documentation
3. Consult Python analytics documentation
4. Contact Power BI administrator
