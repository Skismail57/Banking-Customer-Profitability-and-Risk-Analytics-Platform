# Decision Intelligence Methodology

## Overview

This document defines the methodology for the Decision Intelligence layer, which translates analytics into recommended business actions. The system uses a transparent rules-based recommendation engine that combines multiple analytics outputs (profitability, risk, churn, CLV, exposure) to generate actionable recommendations.

**Important Disclaimer**: All recommendations are analytical decision-support recommendations, not actual banking decisions. Human review and approval are required before any action is taken.

---

## Recommendation Structure

Every recommendation contains:

- **Customer/Segment**: Target of the recommendation (customer-level or segment-level)
- **Triggering Metrics**: The analytics values that triggered the recommendation
- **Reason**: Explanation of why the recommendation was generated
- **Recommended Action**: Suggested business action
- **Priority**: Urgency level (critical, high, medium, low)
- **Confidence/Evidence Level**: Confidence in the recommendation (high, medium, low)
- **Limitations**: Caveats and assumptions of the recommendation
- **Disclaimer**: Explicit statement that this is not a banking decision

---

## Priority Levels

### Critical

**Definition**: Immediate attention required

**Triggers**:
- High risk + high exposure
- High churn probability + high CLV
- Critical risk level

**Action Timeline**: Within 24-48 hours

### High

**Definition**: Urgent attention required

**Triggers**:
- High profitability + rising risk
- High risk + medium exposure
- High churn probability + medium CLV

**Action Timeline**: Within 1 week

### Medium

**Definition**: Attention required in near term

**Triggers**:
- Low profitability + low risk
- Medium risk + medium exposure
- Segment-level analysis

**Action Timeline**: Within 1 month

### Low

**Definition**: Monitor or consider

**Triggers**:
- High churn probability + low CLV
- Low risk + low exposure
- Informational updates

**Action Timeline**: As resources allow

---

## Confidence Levels

### High

**Definition**: Strong evidence supporting recommendation

**Criteria**:
- High data quality
- High model accuracy (>85%)
- Simple, well-understood rules
- Multiple confirming metrics

### Medium

**Definition**: Moderate evidence supporting recommendation

**Criteria**:
- Medium data quality
- Medium model accuracy (75-85%)
- Complex rules
- Limited historical data

### Low

**Definition**: Limited evidence supporting recommendation

**Criteria**:
- Low data quality
- Low model accuracy (<75%)
- Uncertain assumptions
- Limited validation

---

## Recommendation Rules

### Profitability + Risk Rules

#### Rule 1: High Profitability + Low Risk

**Triggering Metrics**:
- Net profit > $5,000
- Risk level = low

**Reason**: Customer has high profitability and low risk profile

**Recommended Action**: Prioritize retention and offer premium product opportunities

**Priority**: High

**Confidence**: High

**Limitations**:
- Based on current snapshot, may not capture future behavior
- Risk level may change over time
- Profitability may be influenced by one-time events

---

#### Rule 2: High Profitability + Rising Risk

**Triggering Metrics**:
- Net profit > $5,000
- Risk trend = increasing

**Reason**: Customer has high profitability but risk is increasing

**Recommended Action**: Initiate enhanced risk monitoring and relationship review

**Priority**: High

**Confidence**: Medium

**Limitations**:
- Risk trend based on limited historical data
- May not capture sudden risk events
- Profitability may mask underlying risk

---

#### Rule 3: Low Profitability + Low Risk

**Triggering Metrics**:
- Net profit < $1,000
- Risk level = low

**Reason**: Customer has low profitability but low risk profile

**Recommended Action**: Provide cost-efficient servicing and targeted cross-sell opportunities

**Priority**: Medium

**Confidence**: High

**Limitations**:
- Low profitability may be temporary
- Cross-sell success depends on customer needs
- Cost-efficient servicing may affect customer experience

---

### Churn + CLV Rules

#### Rule 4: High Churn Probability + High CLV

**Triggering Metrics**:
- Churn probability > 70%
- CLV > $10,000

**Reason**: Customer has high churn probability and high lifetime value

**Recommended Action**: Initiate immediate retention intervention with personalized offers

**Priority**: Critical

**Confidence**: Medium

**Limitations**:
- Churn prediction model accuracy may vary
- CLV estimates based on assumptions
- Retention intervention success not guaranteed
- Customer may have already decided to leave

---

#### Rule 5: High Churn Probability + Low CLV

**Triggering Metrics**:
- Churn probability > 70%
- CLV < $2,000

**Reason**: Customer has high churn probability but low lifetime value

**Recommended Action**: Monitor churn or consider allowing natural attrition

**Priority**: Low

**Confidence**: High

**Limitations**:
- May miss opportunities for profitable retention
- Low CLV may be temporary
- Customer may become more valuable over time

---

### Risk + Exposure Rules

#### Rule 6: High Risk + High Exposure

**Triggering Metrics**:
- Risk level = high or critical
- Exposure > $50,000

**Reason**: Customer has high risk level and high exposure

**Recommended Action**: Initiate early-warning review and risk mitigation measures

**Priority**: Critical

**Confidence**: High

**Limitations**:
- Exposure may not reflect actual loss given default
- Risk level based on current snapshot
- May require additional credit review

---

#### Rule 7: High Risk + Low Exposure

**Triggering Metrics**:
- Risk level = high or critical
- Exposure ≤ $50,000

**Reason**: Customer has high risk level but low exposure

**Recommended Action**: Monitor risk and limit additional exposure

**Priority**: Medium

**Confidence**: High

**Limitations**:
- Low exposure may increase over time
- Risk may improve with intervention

---

### Segment-Level Rules

#### Rule 8: Segment Profitability Analysis

**Triggering Metrics**:
- Segment average profitability
- Segment customer count

**Reason**: Segment profitability analysis

**Recommended Action**: Review segment strategy based on profitability and customer base

**Priority**: Medium

**Confidence**: Medium

**Limitations**:
- Segment averages may mask individual variation
- Segment definitions may change over time
- Recommendations may not apply to all customers in segment

---

#### Rule 9: Segment Risk Concentration

**Triggering Metrics**:
- Segment average risk level
- Segment exposure concentration > 15%

**Reason**: Segment has elevated risk and exposure concentration

**Recommended Action**: Review risk management and exposure limits for segment

**Priority**: High (if concentration > 20%), Medium (if 15-20%)

**Confidence**: Medium

**Limitations**:
- Risk concentration may be acceptable with proper mitigation
- Segment-level analysis may not capture individual risks
- Exposure concentration thresholds are configurable

---

## Priority Calculation

### Scoring System

Priority is calculated based on a weighted scoring system:

**Risk Contribution**:
- Critical: +4 points
- High: +3 points
- Medium: +2 points
- Low: +1 point

**Exposure Contribution**:
- > $100,000: +3 points
- > $50,000: +2 points
- > $10,000: +1 point

**Profitability Contribution** (inverse):
- Negative: +3 points
- < $1,000: +2 points
- < $5,000: +1 point

**Churn Contribution**:
- > 70%: +3 points
- > 50%: +2 points
- > 30%: +1 point

**Priority Mapping**:
- Score ≥ 8: Critical
- Score ≥ 6: High
- Score ≥ 4: Medium
- Score < 4: Low

---

## Confidence Calculation

### Scoring System

Confidence is calculated based on:

**Data Quality Contribution**:
- High: +2 points
- Medium: +1 point
- Low: 0 points

**Model Accuracy Contribution**:
- > 85%: +2 points
- > 75%: +1 point
- ≤ 75%: 0 points

**Rule Complexity Contribution**:
- Simple: +1 point
- Complex: 0 points

**Confidence Mapping**:
- Score ≥ 4: High
- Score ≥ 2: Medium
- Score < 2: Low

---

## Rules Engine

### Architecture

The rules engine provides a flexible framework for registering and evaluating rules:

**Components**:
1. **Rule Registration**: Register rules with condition and action generator
2. **Rule Evaluation**: Evaluate conditions against customer data
3. **Recommendation Generation**: Generate recommendations when conditions met

**Benefits**:
- Transparent rule-based approach
- Easy to add new rules
- Clear audit trail
- Configurable thresholds

---

## Assumptions

### General Assumptions

- Analytics outputs are accurate and up-to-date
- Metrics are calculated consistently
- Risk thresholds are appropriate for the business
- Customer data is representative

### Rule-Specific Assumptions

**Profitability + Risk Rules**:
- Profitability is measured accurately
- Risk level reflects actual risk
- Risk trends are meaningful over time
- Cross-sell opportunities exist

**Churn + CLV Rules**:
- Churn predictions are accurate
- CLV estimates are reasonable
- Retention interventions can be effective
- CLV is appropriate measure of value

**Risk + Exposure Rules**:
- Exposure reflects actual risk
- Risk level is current
- Risk mitigation measures are available
- Exposure limits are appropriate

**Segment-Level Rules**:
- Segment definitions are meaningful
- Segment averages are representative
- Segment-level actions are appropriate
- Concentration thresholds are appropriate

---

## Limitations

### General Limitations

- Recommendations are not banking decisions
- Human review required
- May not capture all relevant factors
- Subject to model accuracy and data quality

### Rule-Specific Limitations

**Profitability + Risk Rules**:
- Snapshot-based, may not capture dynamics
- Profitability may be volatile
- Risk may change suddenly
- Cross-sell may not be appropriate

**Churn + CLV Rules**:
- Churn predictions may be inaccurate
- CLV estimates based on assumptions
- Retention may not be possible
- Customer may have already decided

**Risk + Exposure Rules**:
- Exposure may not reflect LGD
- Risk may be over/underestimated
- Mitigation may not be effective
- Exposure may be concentrated elsewhere

**Segment-Level Rules**:
- Averages mask individual variation
- Segment definitions may change
- Actions may not apply to all customers
- Concentration may be acceptable

---

## Usage Examples

### Python Implementation
```python
from src.decision_intelligence.orchestrator import DecisionIntelligenceOrchestrator

# Initialize orchestrator
orchestrator = DecisionIntelligenceOrchestrator()

# Generate customer recommendations
customer_data = {
    "customer_key": "cust_001",
    "net_profit": 6000,
    "risk_level": "low",
    "risk_trend": "stable",
    "churn_probability": 0.2,
    "clv": 15000,
    "exposure_amount": 30000,
    "segment": "premium"
}

recommendations = orchestrator.generate_customer_recommendations(customer_data)

for rec in recommendations:
    print(f"Action: {rec.recommended_action}")
    print(f"Priority: {rec.priority}")
    print(f"Reason: {rec.reason}")
```

### Segment Recommendations
```python
segment_data = {
    "segment": "premium",
    "avg_profitability": 8000,
    "customer_count": 150,
    "avg_risk_level": "low",
    "exposure_concentration": 0.25
}

recommendations = orchestrator.generate_segment_recommendations(segment_data)
```

---

## Best Practices

### Rule Development

1. **Keep rules simple**: Complex rules are harder to understand and maintain
2. **Document assumptions**: Clearly state what the rule assumes
3. **Include limitations**: Be transparent about what the rule doesn't capture
4. **Test thoroughly**: Validate rules against historical data
5. **Review regularly**: Update rules as business needs change

### Recommendation Review

1. **Human review required**: All recommendations require human approval
2. **Consider context**: Recommendations don't capture all context
3. **Validate assumptions**: Check if assumptions hold for specific case
4. **Monitor outcomes**: Track recommendation effectiveness
5. **Adjust thresholds**: Calibrate based on business feedback

### Priority Management

1. **Focus on critical**: Address critical recommendations first
2. **Balance resources**: Don't ignore medium/low priority items
3. **Track trends**: Monitor if priorities are changing over time
4. **Escalate appropriately**: Know when to escalate to management

---

## Maintenance

### Regular Updates

- Review rule effectiveness quarterly
- Update thresholds based on business changes
- Validate model accuracy regularly
- Monitor recommendation adoption rates

### Rule Governance

- Maintain rule registry
- Document rule changes
- Approve new rules through governance process
- Retire obsolete rules

### Documentation

- Keep methodology current
- Document rule rationale
- Track recommendation outcomes
- Maintain audit trail

---

## Glossary

- **Decision Intelligence**: Layer that translates analytics into business actions
- **Recommendation**: Suggested business action based on analytics
- **Priority**: Urgency level of recommendation (critical, high, medium, low)
- **Confidence**: Evidence level supporting recommendation (high, medium, low)
- **Triggering Metrics**: Analytics values that triggered the recommendation
- **Rules Engine**: Framework for registering and evaluating rules
- **Risk Trend**: Direction of risk change over time (increasing, decreasing, stable)
- **Exposure**: Total amount at risk for a customer
- **CLV**: Customer Lifetime Value
- **Churn Probability**: Predicted probability of customer churn
- **Segment**: Group of customers with similar characteristics
- **Limitations**: Caveats and assumptions of the recommendation
- **Disclaimer**: Statement that recommendations are not banking decisions
