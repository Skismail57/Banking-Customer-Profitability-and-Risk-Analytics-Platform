# Advanced Risk Analytics Methodology

## Overview

This document defines the methodology for advanced risk analytics in the banking platform. The approach includes risk trend monitoring, exposure concentration analysis, risk-adjusted profitability, early-warning indicators, customer risk migration, portfolio risk distribution, risk transition matrices, delinquency buckets, and concentration analysis. All thresholds are configurable.

---

## Risk Trajectory

### Risk Levels

The customer risk trajectory follows four levels:

**Low → Medium → High → Critical**

Each level represents increasing risk based on multiple factors:
- Credit utilization
- Days past due (DPD)
- Credit score
- Balance-to-income ratio (BTI)

### Risk Level Determination

Risk level is determined by a scoring system that aggregates contributions from multiple risk factors:

**Score Calculation**:
- Utilization contribution: 0-3 points
- DPD contribution: 0-4 points
- Credit score contribution: 0-3 points (if available)
- BTI contribution: 0-3 points (if available)

**Risk Level Mapping**:
- Score ≥ 7: Critical
- Score ≥ 5: High
- Score ≥ 3: Medium
- Score < 3: Low

---

## Configurable Thresholds

All thresholds are configurable via the `RiskThresholds` dataclass:

### Credit Utilization Thresholds

- **Low threshold**: 0.30 (30%)
- **Medium threshold**: 0.60 (60%)
- **High threshold**: 0.85 (85%)

**Assumptions**:
- Utilization above 30% indicates increased risk
- Utilization above 60% indicates significant risk
- Utilization above 85% indicates critical risk

### Days Past Due (DPD) Thresholds

- **Low threshold**: 0 days
- **Medium threshold**: 30 days
- **High threshold**: 60 days
- **Critical threshold**: 90 days

**Assumptions**:
- DPD of 0 indicates no delinquency
- DPD of 30+ indicates early delinquency
- DPD of 60+ indicates serious delinquency
- DPD of 90+ indicates critical delinquency

### Credit Score Thresholds

- **Low threshold**: 700 (good credit)
- **Medium threshold**: 600 (fair credit)
- **High threshold**: 500 (poor credit)

**Assumptions**:
- Credit score below 700 indicates some risk
- Credit score below 600 indicates significant risk
- Credit score below 500 indicates critical risk

### Balance-to-Income (BTI) Thresholds

- **Low threshold**: 0.20 (20%)
- **Medium threshold**: 0.40 (40%)
- **High threshold**: 0.60 (60%)

**Assumptions**:
- BTI above 20% indicates moderate debt burden
- BTI above 40% indicates high debt burden
- BTI above 60% indicates critical debt burden

### Delinquency Buckets

- **Current**: 0 days
- **30 days**: 1-30 days
- **60 days**: 31-60 days
- **90 days**: 61-90 days
- **120+ days**: 91+ days

**Assumptions**:
- Standard banking delinquency buckets
- Aligns with regulatory reporting requirements

### Concentration Thresholds

- **Warning threshold**: 0.20 (20% of exposure)
- **Critical threshold**: 0.30 (30% of exposure)

**Assumptions**:
- Single entity with >20% exposure requires monitoring
- Single entity with >30% exposure requires immediate action

### Early Warning Thresholds

- **Utilization increase**: 0.15 (15% increase)
- **Payment decline**: 0.20 (20% decline in on-time payment rate)
- **Balance increase**: 0.25 (25% increase in balance)

**Assumptions**:
- 15% utilization increase indicates potential stress
- 20% payment decline indicates payment difficulty
- 25% balance increase indicates potential over-leveraging

---

## Risk Trend Monitoring

### Purpose

Monitor risk trends for individual customers over time to identify deteriorating or improving risk profiles.

### Methodology

**Steps**:
1. Calculate risk level for each time period
2. Determine trend direction (increasing, decreasing, stable)
3. Identify risk level transitions
4. Track transition history

**Trend Direction**:
- **Increasing**: Risk level worsened over time
- **Decreasing**: Risk level improved over time
- **Stable**: Risk level unchanged
- **Insufficient data**: Fewer than 2 periods

### Assumptions

- Risk levels calculated consistently over time
- Time periods are comparable
- Trend direction based on first and last periods only

### Limitations

- Does not capture intermediate fluctuations
- Sensitive to outliers in first/last periods
- Requires sufficient historical data

---

## Exposure Concentration Analysis

### Purpose

Analyze concentration of exposure across customers to identify concentration risk.

### Methodology

**Metrics**:
- **Warning customers**: Customers with ≥20% of total exposure
- **Critical customers**: Customers with ≥30% of total exposure
- **Herfindahl-Hirschman Index (HHI)**: Sum of squared exposure percentages
- **Gini coefficient**: Measure of inequality in exposure distribution
- **Top 10/20 exposure**: Exposure concentration in top customers

**HHI Interpretation**:
- HHI < 0.01: Low concentration
- HHI 0.01-0.05: Moderate concentration
- HHI > 0.05: High concentration

**Gini Interpretation**:
- Gini < 0.3: Low inequality
- Gini 0.3-0.5: Moderate inequality
- Gini > 0.5: High inequality

### Assumptions

- Exposure represents total outstanding balance
- Concentration risk increases with single-customer exposure
- HHI and Gini provide complementary views

### Limitations

- Does not consider correlation between customers
- Static measure, does not capture temporal changes
- Assumes exposure is the only risk factor

---

## Risk-Adjusted Profitability

### Purpose

Calculate profitability adjusted for risk to provide a more accurate view of economic value.

### Methodology

**Risk Adjustment Factors** (default):
- Low risk: 1.0 (no adjustment)
- Medium risk: 0.9 (10% reduction)
- High risk: 0.7 (30% reduction)
- Critical risk: 0.5 (50% reduction)

**Calculation**:
```
Risk-Adjusted Profit = Profit × Risk Adjustment Factor
```

**Metrics**:
- Total profit (unadjusted)
- Total risk-adjusted profit
- Risk adjustment factor (portfolio level)
- Profitability by risk level

### Assumptions

- Risk adjustment factors reflect expected losses
- Linear relationship between risk and expected loss
- Risk adjustment factors are configurable per business needs

### Limitations

- Risk adjustment factors are subjective
- Does not consider correlation between customers
- Static adjustment, does not capture dynamic risk

---

## Early Warning Indicators

### Purpose

Identify early warning signals before a customer enters a high-risk state.

### Methodology

**Signal Types**:
1. **Utilization increase**: Credit utilization increases by ≥15%
2. **Payment decline**: On-time payment rate declines by ≥20%
3. **Balance increase**: Balance increases by ≥25%

**Detection**:
- Compare current values to historical values
- Flag customers exceeding thresholds
- Track warning signals over time

### Assumptions

- Early warning signals precede risk escalation
- Thresholds are appropriate for the customer base
- Historical data is representative

### Limitations

- May generate false positives
- May miss risk escalation without warning signals
- Requires sufficient historical data

---

## Customer Risk Migration

### Purpose

Analyze how customers migrate between risk levels over time.

### Methodology

**Steps**:
1. Calculate risk level for each period
2. Identify transitions between risk levels
3. Count transitions by type (e.g., "low → medium")
4. Analyze migration patterns

**Transition Types**:
- Upward migration: Low → Medium → High → Critical
- Downward migration: Critical → High → Medium → Low
- Stable: No change in risk level

### Assumptions

- Risk levels calculated consistently
- Transitions represent genuine risk changes
- Sufficient time periods for analysis

### Limitations

- Does not capture speed of migration
- Sensitive to risk level calculation method
- Requires longitudinal data

---

## Portfolio Risk Distribution

### Purpose

Analyze distribution of customers and exposure across risk levels.

### Methodology

**Metrics**:
- Customer count by risk level
- Exposure amount by risk level
- Customer percentage by risk level
- Exposure percentage by risk level

**Distribution Analysis**:
- Identify concentration in high-risk segments
- Compare customer vs exposure distribution
- Track changes over time

### Assumptions

- Risk levels accurately represent risk
- Exposure is appropriate measure of risk
- Portfolio is representative

### Limitations

- Static snapshot, does not capture dynamics
- Risk levels may not capture all risk dimensions
- Exposure may not reflect actual loss given default

---

## Risk Transition Matrices

### Purpose

Calculate probability of transitioning between risk levels across periods.

### Methodology

**Transition Matrix**:
- Rows: From risk level
- Columns: To risk level
- Values: Transition counts or probabilities

**Calculation**:
1. Count transitions between risk levels
2. Normalize to probabilities (row-wise)
3. Analyze transition patterns

**Interpretation**:
- Diagonal: Probability of staying in same risk level
- Off-diagonal: Probability of migrating to different risk level
- Upward transitions: Risk worsening
- Downward transitions: Risk improving

### Assumptions

- Markov property (future depends only on current state)
- Stationary transition probabilities over time
- Sufficient data for reliable estimates

### Limitations

- Markov assumption may not hold
- Transition probabilities may change over time
- Requires large sample size for reliable estimates

---

## Delinquency Buckets

### Purpose

Categorize customers into delinquency buckets based on days past due.

### Methodology

**Buckets**:
- Current: 0 days past due
- 30 days: 1-30 days past due
- 60 days: 31-60 days past due
- 90 days: 61-90 days past due
- 120+ days: 91+ days past due

**Distribution Analysis**:
- Customer count by bucket
- Exposure amount by bucket
- Customer percentage by bucket
- Exposure percentage by bucket

### Assumptions

- DPD accurately reflects delinquency status
- Buckets align with regulatory requirements
- DPD is measured consistently

### Limitations

- Static snapshot, does not capture migration
- Does not consider payment arrangements
- May not capture all types of delinquency

---

## Concentration Analysis

### Purpose

Analyze concentration across segments (e.g., industry, geography, product).

### Methodology

**Metrics**:
- Segment exposure
- Segment exposure percentage
- Warning segments (≥20% of exposure)
- Critical segments (≥30% of exposure)
- HHI by segment

**Analysis**:
- Identify concentrated segments
- Compare segment concentration to thresholds
- Track changes over time

### Assumptions

- Segments are mutually exclusive
- Exposure is appropriate measure of concentration
- Segment definitions are stable

### Limitations

- Does not consider correlation between segments
- Static measure, does not capture dynamics
- Segment definitions may change over time

---

## Usage Examples

### Python Implementation
```python
from src.advanced_risk_analytics.orchestrator import AdvancedRiskOrchestrator
from src.advanced_risk_analytics.base import RiskThresholds

# Initialize with custom thresholds
custom_thresholds = RiskThresholds(
    utilization_low_threshold=0.25,
    concentration_warning_threshold=0.15
)
orchestrator = AdvancedRiskOrchestrator(thresholds=custom_thresholds)

# Generate risk report
report = orchestrator.generate_risk_report(
    df=customer_data,
    customer_column="customer_key",
    exposure_column="exposure_amount"
)
```

### Risk Trend Monitoring
```python
from src.advanced_risk_analytics.trend_monitoring import RiskTrendMonitor

monitor = RiskTrendMonitor()
trend = monitor.calculate_risk_trend(
    df=customer_history,
    customer_column="customer_key",
    date_column="as_of_date",
    utilization_column="credit_utilization",
    dpd_column="days_past_due"
)
```

### Early Warning Detection
```python
from src.advanced_risk_analytics.early_warning import EarlyWarningIndicators

ewi = EarlyWarningIndicators()
warnings = ewi.detect_early_warning_signals(
    df=customer_data,
    customer_column="customer_key",
    date_column="as_of_date",
    utilization_column="credit_utilization",
    payment_rate_column="on_time_payment_rate",
    balance_column="balance"
)
```

---

## Assumptions Summary

### General Assumptions

- Data is accurate and complete
- Risk thresholds are appropriate for the customer base
- Risk factors are independent (unless specified)
- Historical data is representative of future behavior

### Method-Specific Assumptions

**Risk Level Determination**:
- Weighted scoring system accurately reflects risk
- Risk factors are additive
- Thresholds are appropriate for the business

**Exposure Concentration**:
- Exposure is the primary risk factor
- HHI and Gini are appropriate concentration measures
- Concentration risk increases with single-entity exposure

**Risk-Adjusted Profitability**:
- Risk adjustment factors reflect expected losses
- Linear relationship between risk and expected loss
- Profit is measured accurately

**Early Warning Indicators**:
- Warning signals precede risk escalation
- Thresholds are appropriate
- Historical data is representative

**Risk Migration**:
- Risk levels calculated consistently
- Transitions represent genuine risk changes
- Sufficient longitudinal data

**Transition Matrices**:
- Markov property holds
- Transition probabilities are stationary
- Sufficient data for reliable estimates

---

## Limitations Summary

### General Limitations

- Models are predictive, not causal
- Performance may degrade over time (concept drift)
- Requires regular updates and validation
- Thresholds may need adjustment over time

### Method-Specific Limitations

**Risk Trend Monitoring**:
- Does not capture intermediate fluctuations
- Sensitive to outliers
- Requires sufficient historical data

**Exposure Concentration**:
- Does not consider correlation
- Static measure
- Assumes exposure is only risk factor

**Risk-Adjusted Profitability**:
- Risk adjustment factors are subjective
- Does not consider correlation
- Static adjustment

**Early Warning Indicators**:
- May generate false positives
- May miss risk escalation
- Requires historical data

**Risk Migration**:
- Does not capture speed of migration
- Sensitive to risk calculation method
- Requires longitudinal data

**Transition Matrices**:
- Markov assumption may not hold
- Transition probabilities may change
- Requires large sample size

---

## Maintenance

### Regular Updates

- Review and update thresholds quarterly
- Validate risk level determination methodology
- Update risk adjustment factors based on loss experience
- Monitor early warning signal performance

### Model Monitoring

- Track risk level distribution over time
- Monitor concentration metrics
- Validate early warning signal accuracy
- Review transition matrices for changes

### Documentation

- Keep methodology documentation current
- Document threshold changes and rationale
- Track model performance metrics
- Maintain audit trail of risk assessments

---

## Glossary

- **Risk Trajectory**: Customer risk level progression (Low → Medium → High → Critical)
- **Credit Utilization**: Ratio of credit used to credit available
- **Days Past Due (DPD)**: Number of days payment is overdue
- **Balance-to-Income (BTI)**: Ratio of outstanding balance to income
- **Exposure**: Total outstanding balance or amount at risk
- **Concentration Risk**: Risk from large exposure to single entity or segment
- **HHI**: Herfindahl-Hirschman Index, measure of concentration
- **Gini Coefficient**: Measure of inequality in distribution
- **Risk-Adjusted Profitability**: Profit adjusted for expected losses
- **Early Warning Indicators**: Signals preceding risk escalation
- **Risk Migration**: Movement of customers between risk levels
- **Transition Matrix**: Probability of transitioning between risk levels
- **Delinquency Bucket**: Category based on days past due
- **Markov Property**: Future state depends only on current state
