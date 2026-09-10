# Credit Risk Analytics Methodology

## Overview

This document defines the methodology for credit risk analytics in the banking platform. This is a **portfolio analytics tool** for internal risk assessment and monitoring. It is **not** a real-world banking credit decision model and should not be used for making lending decisions.

---

## Important Disclaimer

**This risk analytics module is for portfolio analytics only.**

- It is designed for internal portfolio monitoring and risk assessment
- It is not a substitute for regulatory credit scoring models
- It should not be used for making lending or credit decisions
- The risk score is a simplified analytical tool, not a comprehensive credit risk model
- Results should be interpreted as relative risk indicators within the portfolio, not absolute risk measures

---

## Risk Variables

### Exposure Variables

#### Total Loan Exposure
**Variable**: `total_loan_exposure`  
**Data Type**: Currency  
**Calculation**: `SUM(current_balance)` for active loans  
**Data Requirements**: `current_balance`, `loan_status`  
**Assumptions**:
- Only active loans are included
- Balance is current and accurate as of as_of_date
- Off-balance sheet exposures not included

**Limitations**:
- Does not include contingent liabilities
- May not reflect future commitments
- Subject to accounting policies for balance recognition

**Interpretation**: Higher values indicate greater credit exposure to the customer

---

#### Outstanding Balance
**Variable**: `outstanding_balance`  
**Data Type**: Currency  
**Calculation**: `current_balance`  
**Data Requirements**: `current_balance`  
**Assumptions**:
- Balance is current and accurate
- Includes principal only (accrued interest separate)

**Limitations**:
- May not include accrued interest
- Subject to accounting policies
- May not reflect future interest accruals

**Interpretation**: Higher values indicate larger outstanding obligation

---

#### Average Balance
**Variable**: `average_balance`  
**Data Type**: Currency  
**Calculation**: `AVG(current_balance)`  
**Data Requirements**: `current_balance`  
**Assumptions**:
- Representative of typical balance
- No extreme outliers skewing average

**Limitations**:
- Sensitive to outliers
- May not reflect balance volatility
- Simple average may not be representative

**Interpretation**: Indicates typical outstanding balance level

---

### Payment Behavior Variables

#### Days Past Due (DPD)
**Variable**: `days_past_due`  
**Data Type**: Numeric  
**Calculation**: `MAX(days_past_due)`  
**Data Requirements**: `days_past_due`, `payment_due_date`  
**Assumptions**:
- Days calculated from payment due date
- No grace periods considered
- Partial payments not reflected

**Limitations**:
- May not reflect partial payments
- Grace periods not considered
- May not reflect payment amount

**Interpretation**: Higher values indicate more severe delinquency

---

#### Delinquency Status
**Variable**: `delinquency_status`  
**Data Type**: Categorical  
**Calculation**: `CLASSIFY(days_past_due)`  
**Data Requirements**: `days_past_due`  
**Assumptions**:
- Standard delinquency buckets used
- Bucket definitions consistent across portfolio

**Limitations**:
- Bucket definitions may vary by institution
- May not reflect payment history trends
- Static classification may not capture improvement

**Interpretation**: Higher categories indicate more severe delinquency

**Categories**:
- 0: Current (0 DPD)
- 1: 1-30 Days Past Due
- 2: 31-60 Days Past Due
- 3: 61-90 Days Past Due
- 4: 90+ Days Past Due

---

### Utilization Variables

####_credit Utilization
**Variable**: `credit_utilization`  
**Data Type**: Percentage  
**Calculation**: `(current_balance / credit_limit) * 100`  
**Data Requirements**: `current_balance`, `credit_limit`  
**Assumptions**:
- Credit limit is accurate and current
- Balance reflects total utilization
- No authorized but unused credit considered

**Limitations**:
- Does not consider utilization across multiple products
- May not reflect authorized but unused credit
- Credit limit changes not captured in snapshot

**Interpretation**: Higher values indicate higher credit usage

---

### Repayment History Variables

#### On-Time Payment Rate
**Variable**: `on_time_payment_rate`  
**Data Type**: Percentage  
**Calculation**: `(on_time_payments / total_payments) * 100`  
**Data Requirements**: `payment_history`, `payment_due_date`, `payment_date`  
**Assumptions**:
- Payment history is complete and accurate
- Grace periods not considered (configurable)
- Payment amount not considered

**Limitations**:
- May not reflect payment amount
- Grace periods not considered by default
- Short history may not be representative

**Interpretation**: Higher values indicate better payment history

---

#### Late Payment Count
**Variable**: `late_payment_count`  
**Data Type**: Numeric  
**Calculation**: `COUNT(payment_date > due_date + grace_period)`  
**Data Requirements**: `payment_date`, `due_date`  
**Assumptions**:
- Grace period threshold defined
- All payments captured in history

**Limitations**:
- Does not distinguish severity of lateness
- May not reflect payment amount
- Recent late payments weighted same as old

**Interpretation**: Higher values indicate more late payments

---

#### Missed Payment Count
**Variable**: `missed_payment_count`  
**Data Type**: Numeric  
**Calculation**: `COUNT(payment_date > due_date + missed_threshold)`  
**Data Requirements**: `payment_date`, `due_date`  
**Assumptions**:
- Missed payment threshold defined (default 30 days)
- All payments captured in history

**Limitations**:
- Threshold may vary by institution
- Does not reflect recovery
- May not reflect payment amount

**Interpretation**: Higher values indicate more severely missed payments

---

### Debt Burden Variables (Where Data Available)

#### Loan-to-Income (LTI)
**Variable**: `loan_to_income`  
**Data Type**: Percentage  
**Calculation**: `(loan_amount / annual_income) * 100`  
**Data Requirements**: `loan_amount`, `annual_income`  
**Assumptions**:
- Income is current and accurate
- Income reflects borrower's ability to pay
- Annual income is representative

**Limitations**:
- Does not consider other debt obligations
- Income may not reflect current situation
- Income volatility not considered
- May not be available for all customers

**Interpretation**: Higher values indicate higher debt burden relative to income

---

#### Debt-to-Income (DTI)
**Variable**: `debt_to_income`  
**Data Type**: Percentage  
**Calculation**: `(total_debt_payments / monthly_income) * 100`  
**Data Requirements**: `total_debt_payments`, `monthly_income`  
**Assumptions**:
- All debt obligations included
- Income is current and accurate
- Monthly income representative

**Limitations**:
- May not include all debt types
- Income volatility not considered
- May not be available for all customers
- Debt payments may not reflect actual cash flow

**Interpretation**: Higher values indicate higher debt burden

---

#### Debt Burden
**Variable**: `debt_burden`  
**Data Type**: Percentage  
**Calculation**: `(total_debt / annual_income) * 100`  
**Data Requirements**: `total_debt`, `annual_income`  
**Assumptions**:
- Income is current and accurate
- Total debt includes all obligations
- Annual income representative

**Limitations**:
- May not be available for all customers
- Income volatility not considered
- Debt may not reflect future obligations

**Interpretation**: Higher values indicate higher debt burden

---

### Default Variables

#### Default Flag
**Variable**: `default_flag`  
**Data Type**: Categorical  
**Calculation**: `CLASSIFY(default_status)` or `days_past_due >= 90`  
**Data Requirements**: `default_status`, `days_past_due`  
**Assumptions**:
- Default definition follows institutional policy
- DPD threshold used as fallback (90 days)
- Default status accurately recorded

**Limitations**:
- Default definitions vary by institution
- May not reflect partial recoveries
- Fallback DPD may not match policy

**Interpretation**: True indicates loan is in default

---

#### Default Count
**Variable**: `default_count`  
**Data Type**: Numeric  
**Calculation**: `COUNT(default_status = 'Y')`  
**Data Requirements**: `default_status`  
**Assumptions**:
- Default status accurately recorded
- All defaults captured in history

**Limitations**:
- Does not distinguish severity
- May not reflect recovery
- Historical defaults weighted same as recent

**Interpretation**: Higher values indicate more defaults in history

---

#### Recovery Rate
**Variable**: `recovery_rate`  
**Data Type**: Percentage  
**Calculation**: `(total_recovery / total_default_amount) * 100`  
**Data Requirements**: `recovery_amount`, `default_amount`  
**Assumptions**:
- Recovery amounts accurately recorded
- Default amounts accurately recorded
- Recovery process complete

**Limitations**:
- May not reflect ongoing recoveries
- Recovery timing not considered
- May not reflect recovery costs

**Interpretation**: Higher values indicate better recovery performance

---

## Risk Score Methodology

### Overview
The risk score is a **portfolio analytics tool** that combines multiple risk indicators into a single score (0-100). It is **not** a regulatory credit scoring model.

### Score Components
The risk score uses the following weighted components:

| Component | Weight | Direction | Normalization |
|-----------|--------|-----------|----------------|
| Days Past Due | 25% | Higher is worse | 0 DPD = 0, 90+ DPD = 100 |
| Credit Utilization | 20% | Higher is worse | 0% = 0, 100%+ = 100 |
| On-Time Payment Rate | 20% | Higher is better | 100% = 0, 0% = 100 |
| Delinquency Status | 15% | Higher is worse | Current = 0, 90+ DPD = 100 |
| Debt-to-Income | 10% | Higher is worse | 0% = 0, 50%+ = 100 |
| Default Flag | 10% | Higher is worse | No default = 0, Default = 100 |

### Normalization Logic
Each indicator is normalized to a 0-100 scale:

- **DPD**: `min(DPD / 90 * 100, 100)`
- **Utilization**: `min(utilization, 100)`
- **On-Time Payment Rate**: `100 - on_time_rate`
- **Delinquency Status**: `(status / 4) * 100`
- **DTI**: `min(DTI / 50 * 100, 100)`
- **Default Flag**: `default_flag * 100`

### Score Calculation
```
Risk Score = Σ(normalized_value × weight)
```

### Data Completeness
- Confidence score based on available indicators
- Missing indicators reduce overall confidence
- Minimum confidence for partial data

### Assumptions
- Weights are configurable and may not reflect actual risk relationships
- Normalization thresholds are arbitrary and may not be optimal
- Linear relationships assumed (may not reflect actual risk)
- No interaction effects between indicators considered

### Limitations
- Simplified model not suitable for credit decisions
- Does not consider macroeconomic factors
- Does not consider industry-specific risks
- Does not consider collateral value
- Does not consider guarantor information
- Static weights may not reflect changing risk profiles

---

## Risk Band Classification

### Bands
| Band | Score Range | Description | Recommended Actions |
|------|-------------|-------------|---------------------|
| Low | 0-25 | Low risk profile with strong credit behavior | Monitor regularly, Maintain relationship |
| Medium | 25-50 | Medium risk profile with acceptable credit behavior | Monitor closely, Review periodically, Consider risk mitigation |
| High | 50-75 | High risk profile with concerning credit behavior | Intensive monitoring, Risk mitigation required, Review exposure limits |
| Critical | 75-100 | Critical risk profile with severe credit concerns | Immediate action required, Exposure reduction, Enhanced monitoring, Consider collection |

### Classification Logic
- Score compared against threshold values
- Thresholds are configurable
- Default thresholds: 25, 50, 75

### Assumptions
- Thresholds are arbitrary and may not reflect actual risk
- All customers within band have similar risk (may not be true)
- Band boundaries are discrete (risk is continuous)

### Limitations
- Simplified classification may not capture nuance
- Thresholds may not be optimal for all portfolios
- Does not consider risk trajectory
- Does not consider mitigation actions in place

---

## General Assumptions

### Data Quality
- Data is accurate and complete
- Data is current as of as_of_date
- No data quality issues affecting calculations
- Missing data handled appropriately

### Temporal Consistency
- All data reflects same point in time
- No future data leakage
- Historical data consistent with current definitions

### Customer Behavior
- Past behavior indicative of future behavior
- No significant changes in customer circumstances
- Customer behavior stable over analysis period

### Portfolio Composition
- Portfolio representative of overall risk profile
- No concentration risks not captured
- No systemic risks not captured

---

## General Limitations

### Model Limitations
- Simplified model not suitable for credit decisions
- Does not capture all risk factors
- Linear assumptions may not hold
- No interaction effects considered

### Data Limitations
- May not have complete data for all customers
- Income data may not be available
- Historical data may be limited
- Data quality issues may affect results

### Context Limitations
- Does not consider macroeconomic factors
- Does not consider industry-specific risks
- Does not consider geographic risks
- Does not consider regulatory changes

### Interpretation Limitations
- Risk score is relative, not absolute
- Risk bands are arbitrary classifications
- Results should be interpreted with caution
- Not suitable for regulatory reporting

---

## Interpretation Guidelines

### Risk Score
- **0-25**: Low risk - Strong credit behavior
- **25-50**: Medium risk - Acceptable credit behavior
- **50-75**: High risk - Concerning credit behavior
- **75-100**: Critical risk - Severe credit concerns

### Key Considerations
- Score is relative within portfolio, not absolute
- Compare scores across similar customer segments
- Consider data completeness when interpreting
- Review individual components for context
- Monitor score trends over time

### Red Flags
- Rapid score increase
- Critical band classification
- Multiple high-risk indicators
- Recent defaults
- High utilization with low income

### Positive Indicators
- Stable or improving score
- Low band classification
- Strong payment history
- Low utilization
- No defaults

---

## Usage Examples

### Python Implementation
```python
from src.credit_risk_analytics.orchestrator import CreditRiskOrchestrator
from datetime import date

# Initialize orchestrator
orchestrator = CreditRiskOrchestrator(as_of_date=date(2024, 1, 15))

# Generate comprehensive risk report
report = orchestrator.generate_comprehensive_risk_report(
    loan_df=loan_data,
    payment_df=payment_data,
    account_df=account_data,
    customer_df=customer_data
)

# Access risk score
print(report["risk_score"]["risk_score"])
print(report["risk_band"]["classification"])
```

### SQL Implementation
```sql
-- Customer risk indicators
SELECT 
    customer_id,
    total_exposure,
    max_days_past_due,
    credit_utilization_pct,
    on_time_payment_rate,
    risk_score,
    risk_band
FROM vw_customer_risk_score
WHERE risk_band IN ('high', 'critical')
ORDER BY risk_score DESC;
```

---

## Maintenance

### Methodology Updates
- Review weights quarterly
- Update normalization thresholds as needed
- Document any methodology changes
- Validate against portfolio performance

### Threshold Updates
- Review band thresholds quarterly
- Adjust based on portfolio composition
- Document threshold changes
- Communicate changes to stakeholders

### Model Validation
- Validate score distribution quarterly
- Review band classification accuracy
- Monitor score drift over time
- Compare with external benchmarks

---

## Glossary

- **DPD**: Days Past Due
- **LTI**: Loan-to-Income ratio
- **DTI**: Debt-to-Income ratio
- **Utilization**: Credit utilization ratio
- **Default**: Failure to meet loan obligations
- **Recovery Rate**: Percentage of defaulted amount recovered
- **Risk Score**: Composite risk indicator (0-100)
- **Risk Band**: Categorical risk classification
- **Portfolio Analytics**: Internal risk assessment for portfolio monitoring
