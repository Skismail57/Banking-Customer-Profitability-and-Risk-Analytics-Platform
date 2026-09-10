# Churn Analytics Methodology

## Overview

This document defines the methodology for customer churn analytics in the banking platform. The approach includes churn definition, signal detection, feature engineering, and predictive modeling with a focus on interpretability.

---

## Churn Definition

### Precise Churn Definitions

Churn is defined based on available data with multiple definitions to capture different types of customer departure:

#### 1. Account Closure Churn
**Definition**: Customer closes all accounts  
**Criteria**: 
- Account status = "closed"
- Closure reason = "customer_initiated"

**Data Requirements**: account_status, closure_date, closure_reason  
**Lookback Period**: 90 days  
**Observation Window**: 30 days

**Assumptions**:
- Closure is customer-initiated
- All accounts considered
- Closure reasons accurately recorded

**Limitations**:
- May miss partial churn (some accounts closed)
- Closure reasons may be incomplete
- May not capture intent before closure

---

#### 2. Inactivity Churn
**Definition**: Customer shows no activity for extended period  
**Criteria**:
- No transactions for 90 days
- No login for 60 days

**Data Requirements**: last_transaction_date, last_login_date  
**Lookback Period**: 90 days  
**Observation Window**: 30 days

**Assumptions**:
- Inactivity indicates churn intent
- No external factors causing inactivity
- Thresholds appropriate for customer base

**Limitations**:
- May miss active but low-value customers
- Thresholds may vary by segment
- Seasonal variations not considered

---

#### 3. Balance Depletion Churn
**Definition**: Customer depletes all balances  
**Criteria**:
- Balance < $100
- Balance declined by > 90%

**Data Requirements**: current_balance, historical_balances  
**Lookback Period**: 90 days  
**Observation Window**: 30 days

**Assumptions**:
- Balance depletion indicates churn
- Thresholds appropriate
- Not due to balance transfers

**Limitations**:
- May miss balance transfers
- Seasonal variations not considered
- May not reflect actual churn intent

---

#### 4. Composite Churn (Recommended)
**Definition**: Multiple indicators of churn  
**Criteria**:
- Minimum 2 indicators from: account_closure, inactivity, balance_depletion

**Data Requirements**: account_status, activity_data, balance_data  
**Lookback Period**: 90 days  
**Observation Window**: 30 days

**Assumptions**:
- Multiple indicators stronger signal
- Indicators independent
- Composite definition more robust

**Limitations**:
- Complex to implement
- May overfit to historical patterns
- Requires multiple data sources

---

## Churn Rate and Retention Rate

### Churn Rate
**Formula**: `(churned_customers / total_customers) * 100`  
**Interpretation**: Percentage of customers who churned in the period  
**Use**: Monitor overall churn trends, identify problem periods

### Retention Rate
**Formula**: `(retained_customers / total_customers) * 100`  
**Interpretation**: Percentage of customers retained in the period  
**Use**: Monitor retention effectiveness, set retention targets

### Monthly Churn Rates
**Calculation**: Calculate churn rate for each month  
**Use**: Identify seasonal patterns, track trends over time

---

## Cohort Retention Analysis

### Cohort Definition
**Basis**: Customer acquisition month  
**Cohort Period**: Number of months since acquisition

### Retention Matrix
**Calculation**: For each cohort, calculate retention rate at each period  
**Visualization**: Heatmap showing retention over time by cohort

### Use Cases
- Compare retention across acquisition cohorts
- Identify cohorts with poor retention
- Evaluate impact of acquisition changes
- Forecast future retention

---

## Churn Signal Detection

### Activity Decline Detection

#### Customer Activity Decline
**Metric**: Percentage decline in activity count  
**Calculation**: `((baseline_activity - recent_activity) / baseline_activity) * 100`  
**Threshold**: > 50% decline and recent < baseline/2  
**Lookback**: 90 days recent, 30 days baseline

**Interpretation**: Significant reduction in customer activity indicates churn risk

---

#### Product Disengagement
**Metric**: Percentage of products with no recent usage  
**Calculation**: `(disengaged_products / total_products) * 100`  
**Threshold**: Days since last use > 60 days  
**Interpretation**: High disengagement rate indicates reduced product usage

---

### Transaction Decline Detection

#### Transaction Count Decline
**Metric**: Percentage decline in transaction count  
**Calculation**: `((baseline_count - recent_count) / baseline_count) * 100`  
**Threshold**: > 50% decline and recent < baseline/2  
**Lookback**: 90 days recent, 30 days baseline

#### Transaction Amount Decline
**Metric**: Percentage decline in transaction amount  
**Calculation**: `((baseline_sum - recent_sum) / baseline_sum) * 100`  
**Threshold**: Significant decline indicates reduced engagement

---

### Balance Decline Detection

#### Balance Decline
**Metric**: Percentage decline in balance  
**Calculation**: `((historical_balance - current_balance) / historical_balance) * 100`  
**Threshold**: > 50% decline  
**Lookback**: 90 days

**Interpretation**: Significant balance depletion may indicate churn intent

---

### Complaint-Related Signals

#### Complaint Score
**Metric**: Weighted sum of complaints  
**Calculation**: Sum of severity weights (high=3, medium=2, low=1)  
**Lookback**: 90 days  
**Threshold**: Score ≥ 5 indicates high risk

**Interpretation**: High complaint activity indicates dissatisfaction and churn risk

---

## Feature Engineering

### Point-in-Time Correct Features

**Critical Principle**: Features must use only data available at prediction time. No future information is used in feature calculation.

### Base Features

| Feature | Description | Data Type | Source |
|---------|-------------|-----------|--------|
| tenure_days | Customer tenure in days | Numeric | Customer data |
| balance | Current account balance | Currency | Account data |
| transaction_count | Number of transactions | Numeric | Transaction data |
| transaction_amount | Total transaction amount | Currency | Transaction data |
| product_count | Number of products | Numeric | Product data |
| credit_utilization | Credit utilization ratio | Percentage | Credit data |
| days_since_last_transaction | Days since last transaction | Numeric | Transaction data |
| complaint_count | Number of complaints | Numeric | Complaint data |
| profitability | Net profit | Currency | Profitability data |

### Derived Features

| Feature | Formula | Purpose |
|---------|---------|---------|
| transactions_per_day | transaction_count / (tenure_days + 1) | Activity intensity |
| balance_per_product | balance / (product_count + 1) | Product intensity |
| profit_per_transaction | profitability / (transaction_count + 1) | Profit efficiency |
| recency_score | 1 / (days_since_last_transaction + 1) | Recency indicator |

### Temporal Features

**Rolling Aggregates** (point-in-time correct):
- Transaction count last 30/60/90 days
- Transaction amount last 30/60/90 days
- Balance trends over time

**Implementation**: For each customer, calculate aggregates using only data up to the observation date.

---

## Churn Prediction Models

### Model Comparison

| Model | Strengths | Weaknesses | Interpretability |
|-------|----------|------------|-----------------|
| Logistic Regression | Highly interpretable, fast, baseline | Linear assumptions, limited complexity | High (coefficients) |
| Random Forest | Handles non-linear, robust | Less interpretable, slower | Medium (feature importance) |
| Gradient Boosting | High accuracy, handles complex | Less interpretable, prone to overfit | Medium (feature importance) |

### Logistic Regression (Baseline)

**Configuration**:
- Class weight: balanced
- Max iterations: 1000
- Random state: 42

**Interpretability**:
- Coefficients indicate feature direction and magnitude
- Positive coefficient: higher value increases churn risk
- Negative coefficient: higher value decreases churn risk

**Use Case**: Baseline model, interpretability-focused analysis

---

### Random Forest

**Configuration**:
- N estimators: 100
- Max depth: 10
- Class weight: balanced
- Random state: 42

**Interpretability**:
- Feature importance indicates relative importance
- No direction information (positive/negative)
- Can handle non-linear relationships

**Use Case**: Improved accuracy, when non-linear relationships expected

---

### Gradient Boosting

**Configuration**:
- N estimators: 100
- Max depth: 5
- Learning rate: 0.1
- Random state: 42

**Interpretability**:
- Feature importance indicates relative importance
- No direction information
- High accuracy potential

**Use Case**: Maximum accuracy, when interpretability less critical

---

## Model Evaluation

### Classification Metrics

#### Precision
**Formula**: `TP / (TP + FP)`  
**Interpretation**: Of predicted churners, how many actually churned  
**Use**: Minimize false positives (unnecessary retention costs)

#### Recall
**Formula**: `TP / (TP + FN)`  
**Interpretation**: Of actual churners, how many were identified  
**Use**: Minimize false negatives (missed churn opportunities)

#### F1 Score
**Formula**: `2 * (precision * recall) / (precision + recall)`  
**Interpretation**: Harmonic mean of precision and recall  
**Use**: Balance between precision and recall

---

### Ranking Metrics

#### ROC-AUC
**Range**: 0 to 1  
**Interpretation**: Ability to distinguish churners from non-churners  
**Use**: Overall ranking performance, threshold selection

#### PR-AUC
**Range**: 0 to 1  
**Interpretation**: Precision-recall trade-off  
**Use**: More informative for imbalanced data (churn typically rare)

---

### Calibration

**Definition**: Agreement between predicted probabilities and actual outcomes  
**Measurement**: Calibration curve (predicted probability vs observed frequency)  
**Interpretation**: Well-calibrated model has predicted probability = observed frequency  
**Use**: Important for business decisions based on probability thresholds

---

### Business Metrics

#### Intervention Cost
**Formula**: `(TP + FP) * retention_cost`  
**Interpretation**: Cost of retention interventions

#### Missed Churn Cost
**Formula**: `FN * acquisition_cost`  
**Interpretation**: Cost of missed churners

#### Total Cost
**Formula**: `intervention_cost + missed_churn_cost`  
**Interpretation**: Total cost of churn prediction approach

#### Savings
**Formula**: `no_intervention_cost - total_cost`  
**Interpretation**: Savings compared to no intervention

---

## Interpretability Focus

### Feature Importance

#### Logistic Regression
- Coefficients indicate direction and magnitude
- Can explain why a customer is predicted to churn
- Example: "High days_since_last_transaction increases churn risk"

#### Random Forest / Gradient Boosting
- Feature importance indicates relative importance
- No direction information
- Can identify key drivers but not direction

### Model Selection for Interpretability

**Primary**: Logistic Regression for interpretability-focused analysis  
**Secondary**: Random Forest for improved accuracy with moderate interpretability  
**Tertiary**: Gradient Boosting for maximum accuracy when interpretability less critical

---

## Assumptions

### Data Assumptions
- Churn labels are accurate and complete
- Historical data representative of future behavior
- Point-in-time correctness maintained in feature engineering
- No data leakage from future information

### Model Assumptions
- Logistic Regression: Linear relationship between features and log-odds
- Random Forest: No specific assumptions about data distribution
- Gradient Boosting: No specific assumptions about data distribution

### Business Assumptions
- Churn prediction will be used for retention interventions
- Retention cost and acquisition cost estimates are accurate
- Model will be updated regularly to maintain performance
- Interpretability is important for business adoption

---

## Limitations

### Data Limitations
- Churn definition may not capture all types of churn
- Historical data may not reflect future behavior
- Missing data may affect model performance
- Point-in-time correctness requires careful implementation

### Model Limitations
- Logistic Regression: Limited to linear relationships
- Random Forest: Less interpretable, may overfit
- Gradient Boosting: Prone to overfitting, less interpretable
- All models: May not capture causal relationships

### Business Limitations
- Predictive, not causal - may not identify root causes
- Requires regular updating to maintain performance
- Interpretability vs accuracy trade-off
- May not generalize to new customer segments

### General Limitations
- Churn prediction is descriptive, not prescriptive
- Does not recommend specific retention actions
- May not reflect competitive dynamics
- Requires integration with retention strategy

---

## Point-in-Time Correctness

### Principle
**Features must use only data available at prediction time.**

### Implementation
1. Define observation date (point in time for prediction)
2. Filter data to only include records up to observation date
3. Calculate features using only filtered data
4. Calculate churn label using future behavior (for training only)
5. In production, churn label not available (prediction only)

### Common Pitfalls
- Using future balance data
- Using average of entire history (includes future)
- Using churn status in features
- Using future complaint data

### Validation
- Temporal validation (train on past, test on future)
- Check feature distributions over time
- Monitor for data drift

---

## Usage Examples

### Python Implementation
```python
from src.churn_analytics.orchestrator import ChurnAnalyticsOrchestrator
from datetime import date

# Initialize orchestrator
orchestrator = ChurnAnalyticsOrchestrator(as_of_date=date(2024, 1, 15))

# Generate churn report
report = orchestrator.generate_churn_report(customer_data)

# Train churn models
results = orchestrator.train_churn_models(
    X=features,
    y=labels,
    models=["logistic", "random_forest"]
)
```

### Feature Engineering
```python
from src.churn_analytics.features import ChurnFeatureEngineer

# Create point-in-time correct features
feature_engineer = ChurnFeatureEngineer(as_of_date=date(2024, 1, 15))
features_df = feature_engineer.create_feature_dataset(
    df=customer_data,
    lookback_days=90,
    observation_window_days=30
)
```

---

## Maintenance

### Regular Updates
- Re-train models quarterly or as needed
- Update churn definitions based on business feedback
- Monitor model performance over time
- Validate point-in-time correctness

### Model Monitoring
- Track precision, recall, F1 over time
- Monitor calibration
- Check for data drift
- Compare to baseline performance

### Documentation
- Keep methodology documentation current
- Document any changes to churn definitions
- Maintain feature engineering guide
- Track model performance metrics

---

## Glossary

- **Churn**: Customer departure or reduced engagement
- **Churn Rate**: Percentage of customers who churned in a period
- **Retention Rate**: Percentage of customers retained in a period
- **Cohort**: Group of customers acquired in the same period
- **Point-in-Time Correctness**: Using only data available at prediction time
- **ROC-AUC**: Receiver Operating Characteristic Area Under Curve
- **PR-AUC**: Precision-Recall Area Under Curve
- **Calibration**: Agreement between predicted probabilities and actual outcomes
- **Feature Importance**: Relative importance of features in model
- **Data Leakage**: Using future information in feature calculation
