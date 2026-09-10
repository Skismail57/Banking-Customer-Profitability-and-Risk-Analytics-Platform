# Data Quality Rules Documentation

## Overview

This document describes all data quality validation rules implemented using Pandera for the Banking Customer Profitability & Risk Analytics Platform. Each rule is documented with its purpose, validation logic, and error conditions.

---

## Quality Dimensions

### 1. Completeness
**Definition**: Proportion of non-null values in the dataset.

**Calculation**: `(total_cells - missing_cells) / total_cells`

**Thresholds**:
- Excellent: ≥ 90%
- Good: 75% - 89%
- Fair: 50% - 74%
- Poor: < 50%

---

### 2. Validity
**Definition**: Proportion of rows that pass all validation rules.

**Calculation**: `valid_rows / total_rows`

**Thresholds**:
- Excellent: ≥ 95%
- Good: 80% - 94%
- Fair: 50% - 79%
- Poor: < 50%

---

### 3. Uniqueness
**Definition**: Proportion of unique rows (no duplicates).

**Calculation**: `(total_rows - duplicate_rows) / total_rows`

**Thresholds**:
- Excellent: ≥ 98%
- Good: 90% - 97%
- Fair: 75% - 89%
- Poor: < 75%

---

### 4. Consistency
**Definition**: Consistency of data types and formats within columns.

**Calculation**: Based on type consistency checks, penalizes mixed types in object columns.

**Thresholds**:
- Excellent: ≥ 95%
- Good: 80% - 94%
- Fair: 60% - 79%
- Poor: < 60%

---

### 5. Referential Integrity
**Definition**: Validity of foreign key relationships between tables.

**Calculation**: Placeholder for FK validation (currently assumes 100% if no obvious issues).

**Thresholds**:
- Excellent: ≥ 95%
- Good: 80% - 94%
- Fair: 60% - 79%
- Poor: < 60%

---

## Dimension Table Rules

### dim_customer

| Column | Rule | Description | Error Message |
|--------|------|-------------|---------------|
| customer_id | Required, Unique | Must be non-null and unique | customer_id is required and must be unique |
| first_name | Optional | Customer first name | - |
| last_name | Optional | Customer last name | - |
| birth_date | Not in future | Birth date cannot be in the future | Birth date cannot be in future |
| birth_date | Not too old | Birth date cannot be more than 120 years ago | Birth date cannot be more than 120 years ago |
| annual_income | Non-negative | Annual income must be ≥ 0 | Annual income must be non-negative |
| is_active | Required | Customer active status is required | is_active is required |
| customer_since | Not in future | Customer onboarding date cannot be in future | Customer since date cannot be in future |
| churn_date | Optional | Customer churn date | - |

**Business Rules**:
- A customer cannot have a birth date in the future
- A customer cannot be more than 120 years old
- Annual income cannot be negative
- Customer since date cannot be in the future

---

### dim_account

| Column | Rule | Description | Error Message |
|--------|------|-------------|---------------|
| account_id | Required, Unique | Must be non-null and unique | account_id is required and must be unique |
| customer_key | Required | Foreign key to dim_customer | customer_key is required |
| customer_id | Required | Customer identifier | customer_id is required |
| product_key | Required | Foreign key to dim_product | product_key is required |
| credit_limit | Non-negative | Credit limit must be ≥ 0 | Credit limit must be non-negative |
| overdraft_limit | Non-negative | Overdraft limit must be ≥ 0 | Overdraft limit must be non-negative |
| is_active | Required | Account active status is required | is_active is required |
| opened_date | Not in future | Account opening date cannot be in future | Opened date cannot be in future |
| closed_date | Optional | Account closing date | - |

**Business Rules**:
- Credit limits cannot be negative
- Overdraft limits cannot be negative
- Account cannot be opened in the future

---

### dim_product

| Column | Rule | Description | Error Message |
|--------|------|-------------|---------------|
| product_id | Required, Unique | Must be non-null and unique | product_id is required and must be unique |
| product_category | Required | Product category (deposits, loans, cards) | product_category is required |
| product_type | Required | Product type | product_type is required |
| product_name | Required | Product display name | product_name is required |
| interest_rate | Non-negative | Interest rate must be ≥ 0 | Interest rate must be non-negative |
| annual_fee | Non-negative | Annual fee must be ≥ 0 | Annual fee must be non-negative |
| minimum_balance | Non-negative | Minimum balance must be ≥ 0 | Minimum balance must be non-negative |
| term_months | Non-negative | Loan term in months must be ≥ 0 | Term months must be non-negative |
| is_active | Required | Product active status is required | is_active is required |

**Business Rules**:
- Interest rates cannot be negative
- Fees cannot be negative
- Minimum balance requirements cannot be negative
- Loan terms cannot be negative

---

### dim_branch

| Column | Rule | Description | Error Message |
|--------|------|-------------|---------------|
| branch_id | Required, Unique | Must be non-null and unique | branch_id is required and must be unique |
| branch_name | Required | Branch display name | branch_name is required |
| latitude | Range check | Must be between -90 and 90 | Latitude must be between -90 and 90 |
| longitude | Range check | Must be between -180 and 180 | Longitude must be between -180 and 180 |
| atm_count | Non-negative | Number of ATMs must be ≥ 0 | ATM count must be non-negative |
| employee_count | Non-negative | Number of employees must be ≥ 0 | Employee count must be non-negative |
| is_active | Required | Branch active status is required | is_active is required |

**Business Rules**:
- Latitude must be valid (-90 to 90 degrees)
- Longitude must be valid (-180 to 180 degrees)
- ATM and employee counts cannot be negative

---

### dim_date

| Column | Rule | Description | Error Message |
|--------|------|-------------|---------------|
| date_key | Required, Unique | Must be non-null and unique | date_key is required and must be unique |
| full_date | Required, Unique | Full date value must be unique | full_date is required and must be unique |
| day_of_month | Range check | Must be between 1 and 31 | Day of month must be between 1 and 31 |
| day_of_week | Range check | Must be between 1 and 7 | Day of week must be between 1 and 7 |
| month | Range check | Must be between 1 and 12 | Month must be between 1 and 12 |
| quarter | Range check | Must be between 1 and 4 | Quarter must be between 1 and 4 |
| year | Range check | Must be reasonable (1900-2100) | Year must be reasonable |

**Business Rules**:
- Day of month must be valid (1-31)
- Day of week must be valid (1-7, Monday=1)
- Month must be valid (1-12)
- Quarter must be valid (1-4)
- Year must be within reasonable range

---

### dim_customer_segment

| Column | Rule | Description | Error Message |
|--------|------|-------------|---------------|
| segment_id | Required, Unique | Must be non-null and unique | segment_id is required and must be unique |
| segment_name | Required | Segment display name | segment_name is required |
| segment_type | Required | Segment type (value, behavior, risk, lifecycle) | segment_type is required |
| min_balance | Non-negative | Minimum balance must be ≥ 0 | Min balance must be non-negative |
| max_balance | Non-negative | Maximum balance must be ≥ 0 | Max balance must be non-negative |
| credit_score_min | Range check | Must be between 300 and 850 | Credit score min must be 300-850 |
| credit_score_max | Range check | Must be between 300 and 850 | Credit score max must be 300-850 |
| effective_date | Required | Segment effective date | effective_date is required |
| expiry_date | Optional | Segment expiry date | - |
| is_current | Required | Current record flag | is_current is required |

**Business Rules**:
- Balance ranges cannot be negative
- Credit score ranges must be valid (300-850 FICO range)
- Effective date is required for all segments

---

## Fact Table Rules

### fact_transaction

| Column | Rule | Description | Error Message |
|--------|------|-------------|---------------|
| transaction_id | Required, Unique | Must be non-null and unique | transaction_id is required and must be unique |
| account_key | Required | Foreign key to dim_account | account_key is required |
| customer_key | Required | Foreign key to dim_customer | customer_key is required |
| product_key | Required | Foreign key to dim_product | product_key is required |
| date_key | Required | Foreign key to dim_date | date_key is required |
| amount | Non-zero | Transaction amount cannot be zero | Transaction amount cannot be zero |
| transaction_date | Required | Transaction timestamp | transaction_date is required |
| fraud_score | Range check | Must be between 0 and 1 if present | Fraud score must be between 0 and 1 |

**Business Rules**:
- Transaction amounts cannot be zero
- Fraud scores must be valid probabilities (0-1)
- All foreign keys must be present

---

### fact_loan

| Column | Rule | Description | Error Message |
|--------|------|-------------|---------------|
| loan_id | Required, Unique | Must be non-null and unique | loan_id is required and must be unique |
| customer_key | Required | Foreign key to dim_customer | customer_key is required |
| product_key | Required | Foreign key to dim_product | product_key is required |
| origination_date_key | Required | Foreign key to dim_date | origination_date_key is required |
| maturity_date_key | Required | Foreign key to dim_date | maturity_date_key is required |
| principal_amount | Positive | Principal amount must be > 0 | Principal amount must be positive |
| interest_rate | Non-negative | Interest rate must be ≥ 0 | Interest rate must be non-negative |
| term_months | Positive | Loan term must be > 0 | Term months must be positive |
| credit_score_at_origination | Range check | Must be between 300 and 850 if present | Credit score must be 300-850 |
| days_past_due | Non-negative | Days past due must be ≥ 0 | Days past due must be non-negative |
| origination_date | Required | Loan origination date | origination_date is required |
| maturity_date | Required | Loan maturity date | maturity_date is required |

**Business Rules**:
- Loan principal must be positive
- Interest rates cannot be negative
- Loan terms must be positive
- Credit scores must be valid (300-850)
- Days past due cannot be negative
- Origination and maturity dates are required

---

### fact_loan_payment

| Column | Rule | Description | Error Message |
|--------|------|-------------|---------------|
| payment_id | Required, Unique | Must be non-null and unique | payment_id is required and must be unique |
| loan_key | Required | Foreign key to fact_loan | loan_key is required |
| customer_key | Required | Foreign key to dim_customer | customer_key is required |
| date_key | Required | Foreign key to dim_date | date_key is required |
| payment_amount | Positive | Payment amount must be > 0 | Payment amount must be positive |
| principal_component | Non-negative | Principal portion must be ≥ 0 | Principal component must be non-negative |
| interest_component | Non-negative | Interest portion must be ≥ 0 | Interest component must be non-negative |
| days_late | Non-negative | Days late must be ≥ 0 | Days late must be non-negative |

**Business Rules**:
- Payment amounts must be positive
- Payment components cannot be negative
- Days late cannot be negative

---

### fact_card_transaction

| Column | Rule | Description | Error Message |
|--------|------|-------------|---------------|
| card_transaction_id | Required, Unique | Must be non-null and unique | card_transaction_id is required and must be unique |
| account_key | Required | Foreign key to dim_account | account_key is required |
| customer_key | Required | Foreign key to dim_customer | customer_key is required |
| product_key | Required | Foreign key to dim_product | product_key is required |
| date_key | Required | Foreign key to dim_date | date_key is required |
| transaction_amount | Non-zero | Transaction amount cannot be zero | Transaction amount cannot be zero |
| fraud_score | Range check | Must be between 0 and 1 if present | Fraud score must be between 0 and 1 |
| rewards_points | Non-negative | Rewards points must be ≥ 0 | Rewards points must be non-negative |

**Business Rules**:
- Card transaction amounts cannot be zero
- Fraud scores must be valid probabilities (0-1)
- Rewards points cannot be negative

---

### fact_customer_interaction

| Column | Rule | Description | Error Message |
|--------|------|-------------|---------------|
| interaction_id | Required, Unique | Must be non-null and unique | interaction_id is required and must be unique |
| customer_key | Required | Foreign key to dim_customer | customer_key is required |
| date_key | Required | Foreign key to dim_date | date_key is required |
| duration_seconds | Non-negative | Duration must be ≥ 0 | Duration must be non-negative |
| satisfaction_score | Range check | Must be between 1 and 5 if present | Satisfaction score must be between 1 and 5 |

**Business Rules**:
- Interaction duration cannot be negative
- Satisfaction scores must be valid (1-5 scale)

---

### fact_customer_profitability

| Column | Rule | Description | Error Message |
|--------|------|-------------|---------------|
| customer_key | Required | Foreign key to dim_customer | customer_key is required |
| date_key | Required | Foreign key to dim_date | date_key is required |
| period_start_date | Required | Period start date | period_start_date is required |
| period_end_date | Required | Period end date | period_end_date is required |
| interest_income | Non-negative | Interest income must be ≥ 0 | Interest income must be non-negative |
| fee_income | Non-negative | Fee income must be ≥ 0 | Fee income must be non-negative |
| cost_of_funds | Non-negative | Cost of funds must be ≥ 0 | Cost of funds must be non-negative |
| operating_costs | Non-negative | Operating costs must be ≥ 0 | Operating costs must be non-negative |
| number_of_accounts | Non-negative | Account count must be ≥ 0 | Number of accounts must be non-negative |
| number_of_transactions | Non-negative | Transaction count must be ≥ 0 | Number of transactions must be non-negative |

**Business Rules**:
- All revenue components must be non-negative
- All cost components must be non-negative
- Account and transaction counts cannot be negative
- Period start and end dates are required

---

### fact_customer_risk

| Column | Rule | Description | Error Message |
|--------|------|-------------|---------------|
| customer_key | Required | Foreign key to dim_customer | customer_key is required |
| date_key | Required | Foreign key to dim_date | date_key is required |
| period_start_date | Required | Period start date | period_start_date is required |
| period_end_date | Required | Period end date | period_end_date is required |
| credit_score | Range check | Must be between 300 and 850 if present | Credit score must be 300-850 |
| total_exposure | Non-negative | Total exposure must be ≥ 0 | Total exposure must be non-negative |
| days_past_due | Non-negative | Days past due must be ≥ 0 | Days past due must be non-negative |
| number_of_delinquent_accounts | Non-negative | Delinquent account count must be ≥ 0 | Delinquent accounts must be non-negative |
| probability_of_default | Range check | Must be between 0 and 1 if present | PD must be between 0 and 1 |
| loss_given_default | Range check | Must be between 0 and 1 if present | LGD must be between 0 and 1 |

**Business Rules**:
- Credit scores must be valid (300-850)
- Exposure amounts cannot be negative
- Days past due cannot be negative
- Delinquent account counts cannot be negative
- PD must be valid probability (0-1)
- LGD must be valid probability (0-1)

---

## Custom Validators

### Non-Negative Check
**Purpose**: Ensure numeric values are ≥ 0

**Applies to**: All monetary amounts, counts, durations

**Error**: "Value must be non-negative"

---

### Positive Check
**Purpose**: Ensure numeric values are > 0

**Applies to**: Principal amounts, payment amounts, loan terms

**Error**: "Value must be positive"

---

### Range Check
**Purpose**: Ensure values are within specified range

**Applies to**: 
- Latitude: -90 to 90
- Longitude: -180 to 180
- Credit scores: 300 to 850
- Satisfaction scores: 1 to 5
- Probabilities: 0 to 1

**Error**: "Value must be between {min} and {max}"

---

### Valid Percentage Check
**Purpose**: Ensure values are valid percentages (0-100)

**Applies to**: Percentage-based metrics

**Error**: "Value must be between 0 and 100"

---

### Valid Rate Check
**Purpose**: Ensure values are valid rates (0-1)

**Applies to**: Fraud scores, PD, LGD

**Error**: "Value must be between 0 and 1"

---

### Valid Credit Score Check
**Purpose**: Ensure credit scores are in FICO range (300-850)

**Applies to**: Credit scores at origination, segment ranges

**Error**: "Credit score must be between 300 and 850"

---

### Valid Currency Code Check
**Purpose**: Ensure currency codes are valid ISO 4217

**Applies to**: Currency fields

**Error**: "Invalid currency code"

**Supported Currencies**: USD, EUR, GBP, JPY, CAD, AUD, CHF, CNY

---

### Not Future Date Check
**Purpose**: Ensure dates are not in the future

**Applies to**: Birth dates, customer since dates, account opened dates

**Error**: "Date cannot be in future"

---

### Not Past Date Check
**Purpose**: Ensure dates are not too far in the past

**Applies to**: Birth dates (max 120 years ago)

**Error**: "Date cannot be more than {years} years ago"

---

## Temporal Consistency Rules

### Date Order Validation
**Rule**: Start date must be ≤ end date

**Applies to**: 
- Customer segment effective/expiry dates
- Loan origination/maturity dates
- Profitability period dates
- Risk period dates

**Error**: "Start date must be before or equal to end date"

---

### Impossible State Detection

### Account States
**Rule**: Closed account cannot have future transactions
**Detection**: Check transaction dates against account closed date

**Rule**: Inactive account cannot have active status
**Detection**: Check is_active flag against account status

---

### Loan States
**Rule**: Paid-off loan cannot have future payments
**Detection**: Check payment dates against loan paid_off_date

**Rule**: Defaulted loan cannot have positive status
**Detection**: Check loan_status against days_past_due

**Rule**: Maturity date must be after origination date
**Detection**: Compare maturity_date and origination_date

---

## Failed Record Handling

### Quarantine Process
1. **Detection**: Identify records failing validation
2. **Separation**: Separate valid from invalid records
3. **Metadata**: Add quarantine timestamp and reason
4. **Storage**: Save to quarantine directory in Parquet format
5. **Reporting**: Log quarantine summary

### Quarantine File Naming
Format: `quarantine_{table_name}_{timestamp}.parquet`

### Quarantine Metadata
- `_quarantine_timestamp`: When record was quarantined
- `_quarantine_table`: Source table name
- `_quarantine_reason`: Reason for quarantine

### Restoration Process
1. Load quarantined records from file
2. Remove quarantine metadata columns
3. Review and fix issues
4. Re-validate and re-load

---

## Threshold-Based Actions

### Action Determination

| DQ Score Range | Action | Description |
|----------------|--------|-------------|
| ≥ 75 | Accept | Data quality acceptable |
| 50 - 74 | Warn | Accept with warnings |
| < 50 | Reject | Data quality too poor, reject |

### Failure Percentage Thresholds

| Failure Percentage | Action | Description |
|-------------------|--------|-------------|
| ≤ 5% | Accept | Accept all data |
| 5% - 10% | Warn | Accept with warnings |
| > 10% | Quarantine | Quarantine failed records |

---

## Quality Score Calculation

### Formula
```
DQ Score = (
    Completeness × 0.25 +
    Validity × 0.30 +
    Uniqueness × 0.20 +
    Consistency × 0.15 +
    Referential Integrity × 0.10
) × 100
```

### Default Weights
- Completeness: 25%
- Validity: 30%
- Uniqueness: 20%
- Consistency: 15%
- Referential Integrity: 10%

**Note**: Weights can be customized per business requirements.

---

## Report Generation

### Report Contents
1. **Overall Assessment**: Status (excellent/good/fair/poor)
2. **Dimension Scores**: Individual dimension scores with status
3. **Detailed Metrics**: Row/column counts, missing values, duplicates
4. **Column Metrics**: Per-column statistics
5. **Validation Errors**: List of validation failures
6. **Recommendations**: Actionable improvement suggestions

### Report Formats
- **JSON**: Machine-readable format
- **HTML**: Human-readable format with styling

---

## Integration with ETL Pipeline

### Validation Points
1. **Post-Extraction**: Validate after extracting from source
2. **Post-Transformation**: Validate after cleaning and transformation
3. **Pre-Load**: Validate before loading to warehouse

### Pipeline Hooks
- `pre_load_hook`: Validate before warehouse load
- `post_load_hook`: Record quality metrics after load

### Error Handling
- **Reject**: Stop pipeline, return empty DataFrame
- **Quarantine**: Separate failed records, continue with valid
- **Warn**: Log warning, continue with all data

---

## Monitoring and Alerts

### Quality Monitoring
- Track DQ scores over time
- Monitor trends in quality dimensions
- Alert on score degradation
- Track quarantine volume

### Alert Thresholds
- DQ score drops below 75: Warning
- DQ score drops below 50: Critical alert
- Quarantine volume > 1000 records: Review required

---

## Maintenance

### Schema Updates
- Add new validation rules as needed
- Update thresholds based on business requirements
- Document rule changes with version history

### Rule Review
- Quarterly review of all rules
- Adjust thresholds based on data quality trends
- Remove obsolete rules
- Add new rules for identified issues

---

## Glossary

- **DQ Score**: Data Quality Score (0-100)
- **Completeness**: Proportion of non-null values
- **Validity**: Proportion of valid rows
- **Uniqueness**: Proportion of unique rows
- **Consistency**: Data type consistency
- **Referential Integrity**: Foreign key validity
- **Quarantine**: Storage for failed records
- **Threshold**: Boundary for quality actions
