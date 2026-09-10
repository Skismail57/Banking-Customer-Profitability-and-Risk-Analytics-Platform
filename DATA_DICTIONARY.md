# Data Dictionary

This document provides a comprehensive dictionary of all data elements in the Banking Customer Profitability and Risk Analytics Platform.

---

## Core Tables

### customers

Customer master data table containing basic customer information.

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| customer_key | VARCHAR(50) | Unique customer identifier | CUST_001 |
| customer_name | VARCHAR(200) | Customer full name | John Doe |
| customer_age | INTEGER | Customer age in years | 45 |
| income_level | VARCHAR(50) | Income category (Low, Medium, High) | High |
| segment | VARCHAR(50) | Customer segment (premium, standard, basic) | premium |
| as_of_date | DATE | Data snapshot date | 2026-09-01 |

### customer_metrics

Customer-level metrics including profitability, risk, and engagement data.

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| customer_key | VARCHAR(50) | Unique customer identifier (FK) | CUST_001 |
| as_of_date | DATE | Data snapshot date | 2026-09-01 |
| net_profit | DECIMAL(15,2) | Net profit (revenue - cost) | 15000.00 |
| revenue | DECIMAL(15,2) | Total revenue from customer | 20000.00 |
| cost | DECIMAL(15,2) | Total cost to serve customer | 5000.00 |
| clv | DECIMAL(15,2) | Customer lifetime value | 50000.00 |
| risk_level | VARCHAR(20) | Risk level (low, medium, high, critical) | low |
| risk_trend | VARCHAR(20) | Risk trend (stable, increasing, decreasing) | stable |
| churn_probability | DECIMAL(5,4) | Probability of churn (0-1) | 0.12 |
| exposure_amount | DECIMAL(15,2) | Total exposure amount | 75000.00 |
| credit_utilization | DECIMAL(5,4) | Credit utilization ratio (0-1) | 0.35 |
| days_past_due | INTEGER | Days past due on payments | 0 |
| credit_score | INTEGER | Credit score (300-850) | 750 |
| balance_to_income_ratio | DECIMAL(5,4) | Balance to income ratio | 0.25 |

### transactions

Transaction-level data for all customer transactions.

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| transaction_id | VARCHAR(50) | Unique transaction identifier | TXN_001 |
| customer_key | VARCHAR(50) | Customer identifier (FK) | CUST_001 |
| transaction_date | DATE | Transaction date | 2026-09-01 |
| transaction_type | VARCHAR(50) | Type of transaction (purchase, payment, transfer) | purchase |
| channel | VARCHAR(50) | Transaction channel (online, branch, ATM, mobile) | online |
| amount | DECIMAL(15,2) | Transaction amount | 150.00 |
| product_id | VARCHAR(50) | Product identifier | PROD_001 |

### products

Product catalog with product-level information.

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| product_id | VARCHAR(50) | Unique product identifier | PROD_001 |
| product_name | VARCHAR(200) | Product name | Credit Card Gold |
| product_category | VARCHAR(50) | Product category (credit_card, loan, savings) | credit_card |
| base_rate | DECIMAL(5,4) | Base interest rate | 0.1599 |

### recommendations

Generated recommendations for customers and segments.

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| recommendation_id | VARCHAR(50) | Unique recommendation identifier | REC_001 |
| customer_key | VARCHAR(50) | Customer identifier (FK, nullable) | CUST_001 |
| segment | VARCHAR(50) | Segment (nullable for customer-level) | premium |
| priority | VARCHAR(20) | Priority level (low, medium, high, critical) | high |
| confidence_level | VARCHAR(20) | Confidence level (low, medium, high) | high |
| recommended_action | TEXT | Recommended action text | Offer premium product |
| reason | TEXT | Reason for recommendation | High profitability |
| generated_at | DATE | Date recommendation generated | 2026-09-01 |

### model_performance

Model performance tracking metrics.

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| model_id | VARCHAR(50) | Model identifier | CHURN_MODEL_V1 |
| model_name | VARCHAR(200) | Model name | Churn Prediction Model |
| model_type | VARCHAR(50) | Model type (classification, regression) | classification |
| accuracy | DECIMAL(5,4) | Model accuracy | 0.85 |
| precision | DECIMAL(5,4) | Model precision | 0.82 |
| recall | DECIMAL(5,4) | Model recall | 0.78 |
| f1_score | DECIMAL(5,4) | F1 score | 0.80 |
| auc_roc | DECIMAL(5,4) | AUC-ROC score | 0.88 |
| as_of_date | DATE | Performance snapshot date | 2026-09-01 |

---

## Calculated Fields

### Profitability Metrics

- **net_profit**: Revenue minus all associated costs
- **profit_margin**: net_profit / revenue
- **average_profit**: Mean net profit across customers
- **total_profit**: Sum of net profit across all customers

### Risk Metrics

- **risk_score**: Composite risk score (0-100) based on multiple factors
- **high_risk_count**: Count of customers with risk_level = 'high' or 'critical'
- **exposure_by_risk**: Total exposure aggregated by risk level
- **credit_utilization**: Ratio of credit used to credit limit
- **dpd_30_plus**: Count of customers with days_past_due >= 30

### Churn Metrics

- **churn_probability**: Predicted probability of customer churn (0-1)
- **high_churn_count**: Count of customers with churn_probability > 0.7
- **retention_rate**: Percentage of customers retained (1 - churn_rate)
- **churn_by_segment**: Average churn probability by segment

### CLV Metrics

- **clv**: Customer lifetime value calculated from historical and projected data
- **clv_by_segment**: Average CLV by customer segment
- **clv_trend**: CLV trend over time

---

## Risk Levels

| Level | Description | Credit Score Range | Utilization Range |
|-------|-------------|-------------------|------------------|
| Low | Minimal risk | 720-850 | 0-0.30 |
| Medium | Moderate risk | 660-719 | 0.31-0.50 |
| High | Elevated risk | 600-659 | 0.51-0.70 |
| Critical | Severe risk | Below 600 | Above 0.70 |

---

## Customer Segments

| Segment | Description | Characteristics |
|---------|-------------|------------------|
| Premium | High-value customers | High profitability, low risk, high CLV |
| Standard | Average-value customers | Moderate profitability, moderate risk |
| Basic | Entry-level customers | Lower profitability, higher risk |

---

## Transaction Types

| Type | Description |
|------|-------------|
| purchase | Point-of-sale purchase |
| payment | Loan or credit payment |
| transfer | Funds transfer |
| withdrawal | Cash withdrawal |
| deposit | Cash deposit |

---

## Transaction Channels

| Channel | Description |
|---------|-------------|
| online | Online banking or web portal |
| mobile | Mobile app |
| branch | Physical branch location |
| ATM | Automated Teller Machine |
| phone | Phone banking |

---

## Recommendation Priorities

| Priority | Description | Response Time |
|----------|-------------|---------------|
| Critical | Immediate action required | Within 24 hours |
| High | Urgent action needed | Within 72 hours |
| Medium | Action recommended | Within 1 week |
| Low | Optional action | Within 1 month |

---

## Confidence Levels

| Level | Description | Probability Range |
|--------|-------------|-------------------|
| High | High confidence in recommendation | > 0.8 |
| Medium | Moderate confidence | 0.5-0.8 |
| Low | Lower confidence | < 0.5 |

---

## Data Quality Rules

### Null Handling
- customer_key: Not nullable (primary key)
- as_of_date: Not nullable
- net_profit: Nullable (defaults to 0)
- churn_probability: Nullable (defaults to 0)
- risk_level: Nullable (defaults to 'medium')

### Duplicate Handling
- customer_key: Unique per record
- transaction_id: Unique per record
- recommendation_id: Unique per record

### Data Validation
- credit_score: Must be between 300 and 850
- credit_utilization: Must be between 0 and 1
- churn_probability: Must be between 0 and 1
- days_past_due: Must be non-negative
- net_profit: Can be negative (loss-making customers)

---

## Relationships

### Foreign Keys
- customer_metrics.customer_key → customers.customer_key
- transactions.customer_key → customers.customer_key
- transactions.product_id → products.product_id
- recommendations.customer_key → customers.customer_key (nullable)

### Indexes
- customers: customer_key (primary)
- customer_metrics: customer_key, as_of_date
- transactions: customer_key, transaction_date
- products: product_id (primary)
- recommendations: recommendation_id (primary), customer_key
- model_performance: model_id (primary)

---

## Data Retention

- Transaction data: 7 years
- Customer metrics: 5 years (monthly snapshots)
- Recommendations: 1 year
- Model performance: 2 years

---

## Data Privacy

- PII (Personally Identifiable Information): customer_name, customer_age
- Access restrictions: Role-based access control
- Data masking: Applied in non-production environments
- Compliance: GDPR, CCPA compliant (where applicable)
