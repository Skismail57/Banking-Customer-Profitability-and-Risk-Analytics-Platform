# Profitability Analytics Methodology

## Overview

This document defines the transparent methodology for customer profitability analytics in the banking platform. The methodology distinguishes between observed, estimated, and modeled values to ensure clarity about data sources and reliability.

---

## Value Type System

### Observed Values
**Definition**: Directly measured from transaction or system data without estimation or modeling.

**Characteristics**:
- 100% confidence score
- Sourced from actual transaction records
- No assumptions or allocations required

**Examples**:
- Interest income from loan interest accruals
- Fee income from transaction fees
- Service charges from service fee records
- Incentive costs from reward program payouts
- Servicing costs from direct cost allocations

---

### Estimated Values
**Definition**: Calculated from available data using allocation methods or assumptions.

**Characteristics**:
- Confidence score < 100% (typically 0.5-0.9)
- Requires allocation or estimation logic
- Based on reasonable business assumptions

**Examples**:
- Operational cost allocation (proportional to revenue or activity)
- Total cost when some components are missing
- Gross revenue when not all revenue components are available

**Allocation Methods**:
- Proportional to revenue
- Proportional to transaction count
- Proportional to account balance
- Fixed per-account allocation

---

### Modeled Values
**Definition**: Generated from statistical or machine learning models.

**Characteristics**:
- Confidence score typically 0.6-0.8
- Based on model predictions
- Subject to model accuracy and calibration

**Examples**:
- Expected Credit Loss (ECL) from risk models
- Probability of Default (PD)
- Loss Given Default (LGD)
- Exposure at Default (EAD)

**Model Inputs**:
- Customer risk scores
- Historical default rates
- Economic indicators
- Portfolio characteristics

---

### Missing Values
**Definition**: Data not available for calculation.

**Characteristics**:
- 0% confidence score
- Value set to 0 for calculations
- Clearly marked as missing in output

**Handling**:
- Returns 0 for numeric calculations
- Marks value_type as "missing"
- Logs warning for missing data

---

## Revenue Components

### Interest Income
**Metric ID**: `interest_income`  
**Value Type**: Observed  
**Calculation**: `SUM(interest_accrued)`  
**Business Definition**: Interest earned on loan portfolios and paid on deposits

**Data Sources**:
- Loan interest accruals
- Deposit interest payments
- Investment income

**Calculation Notes**:
- Net interest income (interest received - interest paid)
- Includes accrued but not yet received interest
- Excludes interest from non-performing assets (per accounting policy)

---

### Fee Income
**Metric ID**: `fee_income`  
**Value Type**: Observed  
**Calculation**: `SUM(fee_amount)`  
**Business Definition**: Fees charged for various banking services

**Data Sources**:
- Account maintenance fees
- Overdraft fees
- Transaction fees
- Late payment fees
- Wire transfer fees

**Calculation Notes**:
- Includes all fee types
- Excludes waived fees
- Includes fee reversals as negative values

---

### Service Charge Income
**Metric ID**: `service_charge_income`  
**Value Type**: Observed  
**Calculation**: `SUM(service_charge)`  
**Business Definition**: Service charges for specific transactions or services

**Data Sources**:
- ATM service charges
- Branch service charges
- Special service requests
- Premium service fees

**Calculation Notes**:
- Separate from general fee income
- Often customer-initiated
- May vary by service type

---

### Product Revenue
**Metric ID**: `product_revenue`  
**Value Type**: Observed  
**Calculation**: `SUM(product_revenue)`  
**Business Definition**: Revenue attributed to specific banking products

**Data Sources**:
- Credit card interchange revenue
- Insurance product commissions
- Investment product fees
- Cross-sell product revenue

**Calculation Notes**:
- Product-specific attribution
- May include revenue sharing
- Excludes core banking revenue

---

### Gross Revenue
**Metric ID**: `gross_revenue`  
**Value Type**: Observed/Estimated/Missing  
**Calculation**: `SUM(interest_income + fee_income + service_charge_income + product_revenue)`  
**Business Definition**: Sum of all revenue components before costs

**Value Type Logic**:
- **Observed**: All revenue components available and observed
- **Estimated**: Some components missing or estimated
- **Missing**: No revenue components available

**Confidence Calculation**:
- Confidence = count of available components / total components
- Minimum confidence based on component availability

---

## Cost Components

### Servicing Cost
**Metric ID**: `servicing_cost`  
**Value Type**: Observed  
**Calculation**: `SUM(servicing_cost)`  
**Business Definition**: Direct costs associated with account servicing

**Data Sources**:
- Staff costs for account management
- System costs for account maintenance
- Communication costs (mail, email, SMS)
- Customer service costs

**Calculation Notes**:
- Direct allocation to accounts
- May be activity-based
- Excludes general overhead

---

### Operational Cost
**Metric ID**: `operational_cost`  
**Value Type**: Estimated  
**Calculation**: `ALLOCATED(operational_overhead)`  
**Business Definition**: Allocated portion of operational overhead

**Data Sources**:
- Building costs
- Utilities
- General administration
- IT infrastructure
- Compliance costs

**Allocation Methods**:
- Proportional to revenue (default)
- Proportional to transaction count
- Proportional to account balance
- Fixed per-account allocation

**Confidence**: 0.6 (lower due to allocation assumptions)

---

### Incentive Cost
**Metric ID**: `incentive_cost`  
**Value Type**: Observed  
**Calculation**: `SUM(incentive_amount)`  
**Business Definition**: Cost of customer incentives, rewards, and promotions

**Data Sources**:
- Cash back rewards
- Points redemption costs
- Sign-up bonuses
- Referral bonuses
- Loyalty program costs

**Calculation Notes**:
- Actual cost incurred
- Includes accrued but not yet paid
- Excludes expired unredeemed rewards

---

### Expected Credit Loss (ECL)
**Metric ID**: `expected_credit_loss`  
**Value Type**: Modeled  
**Calculation**: `PD * LGD * EAD`  
**Business Definition**: Expected loss from credit defaults based on risk models

**Model Components**:
- **PD (Probability of Default)**: Likelihood of borrower default
- **LGD (Loss Given Default)**: Percentage of exposure lost if default occurs
- **EAD (Exposure at Default)**: Outstanding balance at time of default

**Calculation Notes**:
- Per-loan ECL calculation
- Summed across portfolio
- Uses latest model outputs
- Falls back to balance if EAD not available

**Confidence**: 0.7 (model-based, moderate confidence)

**Fallback Logic**:
- If PD, LGD, or EAD missing: returns MISSING
- If EAD missing: uses current balance as proxy

---

### Total Cost
**Metric ID**: `total_cost`  
**Value Type**: Observed/Estimated/Missing  
**Calculation**: `SUM(servicing_cost + operational_cost + incentive_cost + expected_credit_loss)`  
**Business Definition**: Sum of all cost components

**Value Type Logic**:
- **Observed**: All cost components observed
- **Estimated**: Some components estimated or missing
- **Missing**: No cost components available

**Confidence Calculation**:
- Confidence = minimum of component confidences
- Reflects least reliable component

---

## Profitability Metrics

### Net Profit
**Metric ID**: `net_profit`  
**Value Type**: Observed/Estimated/Missing  
**Calculation**: `gross_revenue - total_cost`  
**Business Definition**: Revenue minus all costs including expected credit loss

**Value Type Logic**:
- **Observed**: Both revenue and costs observed
- **Estimated**: Either revenue or costs estimated
- **Missing**: Either revenue or costs missing

**Confidence Calculation**:
- Confidence = minimum of revenue and cost confidences

**Business Notes**:
- Includes expected credit loss (risk-adjusted profit)
- May be negative for unprofitable customers
- Used for tier classification

---

### Profit Margin
**Metric ID**: `profit_margin`  
**Value Type**: Observed/Estimated/Missing  
**Calculation**: `(net_profit / gross_revenue) * 100`  
**Business Definition**: Net profit as percentage of gross revenue

**Value Type Logic**:
- Follows net_profit value type
- Returns MISSING if gross_revenue is 0 or missing

**Confidence Calculation**:
- Same as net_profit confidence

**Business Notes**:
- Expressed as percentage
- Can be negative for unprofitable customers
- Used for tier classification alongside net profit

---

### Return on Assets (ROA)
**Metric ID**: `return_on_assets`  
**Value Type**: Estimated  
**Calculation**: `(net_profit / average_assets) * 100`  
**Business Definition**: Net profit as percentage of average assets deployed

**Data Requirements**:
- Net profit (from above)
- Average assets (external input)

**Value Type Logic**:
- Follows net_profit value type
- Returns MISSING if average_assets is 0

**Business Notes**:
- Measures efficiency of asset utilization
- Higher values indicate better asset efficiency
- Used for product-level analysis

---

### Return on Equity (ROE)
**Metric ID**: `return_on_equity`  
**Value Type**: Estimated  
**Calculation**: `(net_profit / average_equity) * 100`  
**Business Definition**: Net profit as percentage of equity capital

**Data Requirements**:
- Net profit (from above)
- Average equity (external input)

**Value Type Logic**:
- Follows net_profit value type
- Returns MISSING if average_equity is 0

**Business Notes**:
- Measures return on shareholder capital
- Higher values indicate better equity efficiency
- Used for overall business performance

---

## Level-Based Analysis

### Product-Level Profitability
**Aggregation**: Group by product_key  
**Metrics**: All profitability metrics per product  
**Usage**: Product performance comparison, product mix optimization

**Calculation Notes**:
- Aggregates customer-level profitability to product level
- Includes all revenue and cost components
- Useful for product portfolio management

---

### Account-Level Profitability
**Aggregation**: Group by account_id  
**Metrics**: All profitability metrics per account  
**Usage**: Account profitability analysis, account closure decisions

**Calculation Notes**:
- Aggregates transaction-level data to account level
- Includes account-specific costs
- Useful for account-level decision making

---

### Customer-Level Profitability
**Aggregation**: Group by customer_key  
**Metrics**: All profitability metrics per customer  
**Usage**: Customer segmentation, tier classification, relationship management

**Calculation Notes**:
- Aggregates across all customer accounts
- Includes operational cost allocation
- Primary level for customer profitability analysis

---

## Temporal Analysis

### Monthly Profitability
**Aggregation**: Group by month  
**Metrics**: All profitability metrics per month  
**Usage**: Trend analysis, seasonal patterns, performance tracking

**Calculation Notes**:
- Aggregates transactions by calendar month
- Enables month-over-month comparison
- Basis for annualization

---

### Annualized Profitability
**Calculation**: Monthly values × (12 / months_available)  
**Metrics**: Annualized gross revenue, cost, net profit, margin  
**Usage**: Annual performance comparison, forecasting

**Value Type Logic**:
- **Observed**: 12 months of data available
- **Estimated**: Less than 12 months of data available

**Confidence Calculation**:
- Confidence = months_available / 12
- Reflects data completeness

**Variance Statistics**:
- Monthly standard deviation
- Monthly mean
- Coefficient of variation (stability measure)

**Business Notes**:
- Only annualized when statistically appropriate
- Lower confidence for partial year data
- Includes variance to assess stability

---

## Profitability Tiers

### Tier Classification
**Method**: Configurable thresholds based on net profit and profit margin  
**Default Tiers**:

| Tier | Min Profit | Max Profit | Min Margin | Description |
|------|------------|------------|------------|-------------|
| Platinum | $100,000 | None | 25% | Top-tier profitable customers |
| Gold | $50,000 | $100,000 | 15% | High-value profitable customers |
| Silver | $10,000 | $50,000 | 10% | Moderately profitable customers |
| Bronze | $0 | $10,000 | 5% | Low-margin profitable customers |
| Unprofitable | -∞ | $0 | None | Unprofitable customers |

**Classification Logic**:
- Both profit AND margin thresholds must be met
- Profit range checked first
- Margin checked if profit in range
- Falls to "unknown" if no tier matches

**Configurability**:
- Thresholds can be updated via `ProfitabilityTierEngine.update_thresholds()`
- Custom tiers can be defined
- Number of tiers is configurable

**Usage**:
- Customer segmentation
- Service level differentiation
- Marketing targeting
- Resource allocation

---

## Data Quality Considerations

### Missing Data Handling
- **Observed components missing**: Returns MISSING value type
- **Estimated components missing**: Uses available components, marks as ESTIMATED
- **Modeled components missing**: Returns MISSING if model outputs unavailable

### Zero Values
- **Zero revenue**: Profit margin returns MISSING (division by zero)
- **Zero costs**: Net profit equals gross revenue
- **Zero assets/equity**: ROA/ROE returns MISSING

### Negative Values
- **Negative profit**: Classified as unprofitable
- **Negative margin**: Indicates loss-making customer
- **Negative costs**: Not expected (data quality issue)

### Outlier Detection
- Extreme profit values should be reviewed
- Margin outliers may indicate data issues
- Cost outliers may indicate allocation errors

---

## Usage Examples

### Python Implementation
```python
from src.profitability_analytics.orchestrator import ProfitabilityOrchestrator
from datetime import date

# Initialize orchestrator
orchestrator = ProfitabilityOrchestrator(as_of_date=date(2024, 1, 15))

# Generate comprehensive report
report = orchestrator.generate_comprehensive_profitability_report(
    revenue_df=revenue_data,
    cost_df=cost_data,
    revenue_columns={
        "interest_income": "interest_accrued",
        "fee_income": "fee_amount"
    },
    cost_columns={
        "servicing_cost": "servicing_cost",
        "incentive_cost": "incentive_amount"
    },
    total_operational_overhead=1000000
)

# Access profitability metrics
print(report["overall_profitability"]["net_profit"])
print(report["overall_profitability"]["profit_margin"])
```

### SQL Implementation
```sql
-- Customer profitability with value types
SELECT 
    customer_id,
    gross_revenue,
    gross_revenue_type,
    total_cost,
    total_cost_type,
    net_profit,
    net_profit_type,
    profit_margin,
    profitability_tier
FROM vw_customer_profitability_tiers
WHERE net_profit > 0
ORDER BY net_profit DESC;
```

---

## Performance Considerations

### Python Implementation
- Use vectorized pandas operations
- Filter to relevant time periods before aggregation
- Index DataFrames on grouping columns
- Consider chunking for very large datasets

### SQL Implementation
- Views use LEFT JOINs for comprehensive coverage
- Indexes on customer_key, period, account_key
- Window functions for trend calculations
- Materialized views for frequently accessed data

---

## Maintenance

### Methodology Updates
- Update value type classifications as data sources change
- Refine allocation methods based on business needs
- Update model confidence scores as models improve
- Document any methodology changes

### Threshold Updates
- Review tier thresholds quarterly
- Adjust based on business strategy
- Document threshold changes
- Communicate changes to stakeholders

### Model Updates
- Update ECL models as risk models improve
- Recalibrate confidence scores
- Document model version changes
- Validate model outputs regularly

---

## Glossary

- **Observed**: Directly measured from transaction/system data
- **Estimated**: Calculated with allocation methods or assumptions
- **Modeled**: Generated from statistical/ML models
- **Missing**: Data not available
- **ECL**: Expected Credit Loss
- **PD**: Probability of Default
- **LGD**: Loss Given Default
- **EAD**: Exposure at Default
- **ROA**: Return on Assets
- **ROE**: Return on Equity
- **Net Profit**: Revenue minus all costs
- **Profit Margin**: Net profit as percentage of revenue
- **Confidence Score**: 0-1 score indicating value reliability
- **Allocation**: Distributing shared costs to specific entities
