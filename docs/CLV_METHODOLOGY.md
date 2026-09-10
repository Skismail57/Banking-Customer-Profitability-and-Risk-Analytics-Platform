# Customer Lifetime Value (CLV) Methodology

## Overview

This document defines the transparent methodology for Customer Lifetime Value (CLV) analytics in the banking platform. The approach clearly separates Historical, Predicted, and Estimated CLV, with adjustments for retention and profitability, and comprehensive sensitivity analysis.

---

## CLV Types

### 1. Historical CLV

**Definition**: Sum of actual historical profits for a customer.

**Formula**: `Historical CLV = Σ(Profit_t)` for all historical periods t

**Data Requirements**:
- Historical profit data per customer
- Transaction dates

**Calculation**:
1. Sum all historical profit values for the customer
2. Calculate tenure in years
3. Calculate average annual profit

**Assumptions**:
- Historical CLV is sum of actual profits
- No discounting applied to historical values
- All historical periods included

**Limitations**:
- Does not reflect future value
- May not be representative of future behavior
- Does not account for inflation
- Cannot be used for forward-looking decisions

**Use Case**: Understanding past customer value, benchmarking

---

### 2. Predicted CLV

**Definition**: Projected future value based on historical patterns and models.

**Formula**: 
```
Predicted CLV = Σ(Profit_avg × Retention^t × Discount^t) for t = 1 to T
```

Where:
- Profit_avg = Average annual profit (from historical data or parameter)
- Retention = Annual retention rate
- Discount = 1 / (1 + discount_rate)
- T = Time horizon in years

**Data Requirements**:
- Historical profit data
- Retention rate
- Discount rate
- Time horizon

**Calculation**:
1. Calculate average annual profit from historical data
2. Apply retention adjustment (probability of customer remaining)
3. Apply discount adjustment (time value of money)
4. Sum over projection horizon

**Assumptions**:
- Future profit follows historical patterns
- Retention rate constant over time
- Discount rate appropriate for time value of money
- Average profit representative of future periods

**Limitations**:
- Historical patterns may not continue
- Retention rate may vary over time
- Does not account for market changes
- Requires sufficient historical data

**Use Case**: Forward-looking customer valuation, resource allocation

---

### 3. Estimated CLV

**Definition**: Simplified estimate based on averages and assumptions.

**Formula** (Perpetuity with Retention):
```
Estimated CLV = (Profit_avg × Retention) / (1 + Discount - Retention)
```

**Alternative Formula** (Finite Horizon):
```
Estimated CLV = Σ(Profit_avg × Retention^t × Discount^t) for t = 1 to T
```

**Data Requirements**:
- Average revenue (optional)
- Average cost (optional)
- Average profit (optional)
- Retention rate
- Discount rate
- Time horizon

**Calculation**:
1. Use parameter averages (revenue, cost, profit)
2. Calculate average profit if not provided (revenue - cost)
3. Apply perpetuity formula or finite horizon formula
4. Adjust for retention and discount

**Assumptions**:
- Average profit representative of customer
- Retention rate constant over time
- Discount rate appropriate for time value
- Simple perpetuity formula applicable

**Limitations**:
- Uses averages, not customer-specific data
- Assumes constant retention and discount rates
- Less accurate than Predicted CLV
- Perpetuity formula assumes infinite horizon

**Use Case**: Quick estimation when detailed data unavailable, portfolio-level analysis

---

## CLV Adjustments

### Retention-Adjusted CLV

**Definition**: CLV adjusted for customer retention probability.

**Formula**:
```
Retention-Adjusted CLV = Σ(Base_CLV × Retention^t × Discount^t) for t = 1 to T
```

**Purpose**: Account for probability of customer churn over time.

**Interpretation**:
- Higher retention rate → Higher CLV
- Lower retention rate → Lower CLV
- Retention probability decreases exponentially over time

**Use Case**: Understanding impact of retention on customer value

---

### Profitability-Adjusted CLV

**Definition**: CLV adjusted for profit margin.

**Formula**:
```
Profitability-Adjusted CLV = Σ(Base_CLV × Margin × Retention^t × Discount^t) for t = 1 to T
```

**Alternative** (from revenue and cost):
```
Profit = Revenue - Cost
Margin = Profit / Revenue
Profitability-Adjusted CLV = Σ(Profit × Retention^t × Discount^t) for t = 1 to T
```

**Purpose**: Account for profit margin in revenue-based CLV.

**Interpretation**:
- Higher profit margin → Higher CLV
- Lower profit margin → Lower CLV
- Focus on profitability rather than revenue

**Use Case**: Understanding impact of profitability on customer value

---

## Sensitivity Analysis

### Retention Rate Sensitivity

**Purpose**: Understand how CLV changes with retention rate.

**Method**: Calculate CLV across a range of retention rates (e.g., 50% to 95%).

**Interpretation**:
- Identify retention rate thresholds
- Quantify impact of retention improvements
- Prioritize retention initiatives

**Example**: A 5% improvement in retention rate may increase CLV by 15%.

---

### Revenue Sensitivity

**Purpose**: Understand how CLV changes with revenue.

**Method**: Calculate CLV across a range of revenue values (e.g., ±50% of base).

**Interpretation**:
- Identify revenue growth opportunities
- Quantify impact of cross-sell/up-sell
- Prioritize revenue initiatives

**Example**: A 10% increase in revenue may increase CLV by 8%.

---

### Cost Sensitivity

**Purpose**: Understand how CLV changes with cost.

**Method**: Calculate CLV across a range of cost values (e.g., ±50% of base).

**Interpretation**:
- Identify cost reduction opportunities
- Quantify impact of cost optimization
- Prioritize cost initiatives

**Example**: A 10% decrease in cost may increase CLV by 12%.

---

### Discount Rate Sensitivity

**Purpose**: Understand how CLV changes with discount rate.

**Method**: Calculate CLV across a range of discount rates (e.g., 5% to 20%).

**Interpretation**:
- Understand time value of money impact
- Quantify impact of discount rate changes
- Validate discount rate assumptions

**Example**: A 2% increase in discount rate may decrease CLV by 10%.

---

## CLV Parameters

### Discount Rate

**Definition**: Rate used to discount future cash flows to present value。

**Default**: 10% annually

**Range**: 5% to 20% typically

**Purpose**: Account for time value of money and risk.

**Selection Criteria**:
- Cost of capital
- Risk profile
- Industry benchmarks
- Inflation expectations

---

### Retention Rate

**Definition**: Probability that a customer remains active in a given period.

**Default**: 80% annually

**Range**: 50% to 95% typically

**Purpose**: Account for customer churn probability.

**Selection Criteria**:
- Historical retention data
- Industry benchmarks
- Customer segment characteristics
- Business model

---

### Time Horizon

**Definition**: Number of years to project CLV.

**Default**: 5 years

**Range**: 1 to 10 years typically

**Purpose**: Define projection period for future value.

**Selection Criteria**:
- Business planning horizon
- Customer lifecycle length
- Data availability
- Industry practices

---

### Average Profit

**Definition**: Average profit per period for a customer.

**Default**: Calculated from historical data

**Purpose**: Base value for CLV calculation.

**Selection Criteria**:
- Historical profit data
- Customer segment averages
- Business model
- Industry benchmarks

---

## Assumptions

### General Assumptions

- Historical data is accurate and complete
- Parameters (discount rate, retention rate) are appropriate
- Time horizon is representative of customer lifecycle
- Profit data reflects true economic value

### Historical CLV Assumptions

- Historical profits are accurately recorded
- All relevant periods are included
- No adjustments needed for inflation

### Predicted CLV Assumptions

- Historical patterns continue into the future
- Retention rate is constant over time
- Discount rate is appropriate for time value
- Average profit is representative of future periods

### Estimated CLV Assumptions

- Averages are representative of customer behavior
- Retention rate is constant over time
- Discount rate is appropriate for time value
- Perpetuity formula is applicable (if used)

---

## Limitations

### General Limitations

- CLV is a forward-looking estimate with inherent uncertainty
- Parameters may not reflect future conditions
- Does not capture competitive dynamics
- Requires regular updating

### Historical CLV Limitations

- Does not reflect future value
- May not be representative of future behavior
- Does not account for inflation
- Cannot be used for forward-looking decisions

### Predicted CLV Limitations

- Historical patterns may not continue
- Retention rate may vary over time
- Does not account for market changes
- Requires sufficient historical data
- Sensitive to parameter assumptions

### Estimated CLV Limitations

- Uses averages, not customer-specific data
- Assumes constant retention and discount rates
- Less accurate than Predicted CLV
- Perpetuity formula assumes infinite horizon
- May not capture customer heterogeneity

### Sensitivity Analysis Limitations

- Assumes independent parameter changes
- Does not capture interactions between parameters
- May not reflect real-world constraints
- Requires careful interpretation

---

## Methodology Selection Guide

### When to Use Historical CLV
- Understanding past customer value
- Benchmarking and performance tracking
- Validating predictive models
- Regulatory or compliance requirements

### When to Use Predicted CLV
- Forward-looking customer valuation
- Resource allocation decisions
- Customer acquisition budgeting
- Retention investment prioritization

### When to Use Estimated CLV
- Quick estimation when detailed data unavailable
- Portfolio-level analysis
- Preliminary analysis
- When customer-specific data limited

### When to Use Retention-Adjusted CLV
- Understanding retention impact
- Evaluating retention initiatives
- Customer retention budgeting
- Churn prevention ROI analysis

### When to Use Profitability-Adjusted CLV
- Understanding profitability impact
- Evaluating pricing strategies
- Cost optimization initiatives
- Profit margin analysis

### When to Use Sensitivity Analysis
- Validating parameter assumptions
- Understanding CLV drivers
- Scenario planning
- Risk assessment

---

## Calculation Examples

### Historical CLV Example

**Input**:
- Customer profits: $100, $150, $200 over 3 months

**Calculation**:
- Historical CLV = $100 + $150 + $200 = $450

**Output**:
- Historical CLV = $450
- Tenure = 0.25 years
- Average annual profit = $1,800

---

### Predicted CLV Example

**Input**:
- Average annual profit = $1,000
- Retention rate = 80%
- Discount rate = 10%
- Time horizon = 5 years

**Calculation**:
```
Year 1: $1,000 × 0.80 × 0.909 = $727
Year 2: $1,000 × 0.64 × 0.826 = $529
Year 3: $1,000 × 0.512 × 0.751 = $385
Year 4: $1,000 × 0.410 × 0.683 = $280
Year 5: $1,000 × 0.328 × 0.621 = $204
Total = $2,125
```

**Output**:
- Predicted CLV = $2,125

---

### Estimated CLV Example

**Input**:
- Average revenue = $5,000
- Average cost = $4,000
- Retention rate = 80%
- Discount rate = 10%

**Calculation**:
- Average profit = $5,000 - $4,000 = $1,000
- Profit margin = $1,000 / $5,000 = 20%
- Estimated CLV = ($1,000 × 0.80) / (1 + 0.10 - 0.80) = $2,667

**Output**:
- Estimated CLV = $2,667

---

### Sensitivity Analysis Example

**Input**:
- Base CLV = $2,000
- Base retention rate = 80%
- Retention range = 50% to 95%

**Calculation**:
- Calculate CLV at each retention rate
- Calculate percentage change from base

**Output**:
- 50% retention: CLV = $1,000 (-50%)
- 70% retention: CLV = $1,750 (-12.5%)
- 80% retention: CLV = $2,000 (baseline)
- 90% retention: CLV = $2,250 (+12.5%)
- 95% retention: CLV = $2,375 (+18.75%)

---

## Usage Examples

### Python Implementation
```python
from src.clv_analytics.orchestrator import CLVOrchestrator
from src.clv_analytics.base import CLVParameters
from datetime import date

# Initialize orchestrator
orchestrator = CLVOrchestrator(as_of_date=date(2024, 1, 15))

# Define parameters
params = CLVParameters(
    discount_rate=0.10,
    retention_rate=0.80,
    time_horizon_years=5,
    average_profit=1000
)

# Calculate all CLV types
results = orchestrator.calculate_all_clv_types(
    df=customer_data,
    customer_column="customer_key",
    profit_column="net_profit",
    date_column="as_of_date",
    params=params
)

# Run sensitivity analysis
sensitivity = orchestrator.run_sensitivity_analysis(
    base_clv=2000,
    params=params,
    analysis_types=["retention", "revenue", "cost", "discount"]
)
```

---

## Maintenance

### Regular Updates
- Update parameters quarterly or as needed
- Re-calculate CLV with new data
- Validate assumptions regularly
- Monitor CLV trends over time

### Parameter Monitoring
- Track actual vs predicted retention rates
- Monitor discount rate appropriateness
- Validate average profit estimates
- Review time horizon assumptions

### Documentation
- Keep methodology documentation current
- Document any changes to parameters
- Maintain CLV calculation guide
- Track CLV performance metrics

---

## Glossary

- **CLV**: Customer Lifetime Value - total value a customer provides over their relationship
- **Historical CLV**: Sum of actual historical profits
- **Predicted CLV**: Projected future value based on models
- **Estimated CLV**: Simplified estimate based on averages
- **Retention Rate**: Probability of customer remaining active
- **Discount Rate**: Rate used to discount future cash flows
- **Time Horizon**: Number of years to project CLV
- **Profit Margin**: Profit as a percentage of revenue
- **Sensitivity Analysis**: Analysis of how CLV changes with parameter variations
- **Perpetuity Formula**: Formula assuming infinite cash flows
