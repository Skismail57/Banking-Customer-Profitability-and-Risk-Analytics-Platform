# Statistical Analytics Methodology

## Overview

This document defines the methodology for statistical analytics in the banking platform. The approach includes descriptive statistics, hypothesis testing, regression analysis, and business question testing with comprehensive reporting that goes beyond p-values to include effect sizes, confidence intervals, and business interpretations.

---

## Test Result Structure

Every statistical test report includes:

- **Null Hypothesis (H₀)**: The default assumption of no effect or no difference
- **Alternative Hypothesis (H₁)**: The hypothesis being tested (effect or difference exists)
- **Assumptions**: Conditions that must be met for the test to be valid
- **Test Statistic**: Calculated value from the test
- **P-value**: Probability of observing results if H₀ is true
- **Confidence Interval**: Range of plausible values for the parameter (where applicable)
- **Effect Size**: Magnitude of the effect (independent of sample size)
- **Business Interpretation**: Practical significance and business implications

**Important**: Conclusions are not based solely on p-values. Effect sizes, confidence intervals, and business context are always considered.

---

## Descriptive Statistics

### Summary Statistics

**Metrics**:
- Count, mean, median, mode
- Standard deviation, variance
- Min, max, range
- Quartiles (Q1, Q3), IQR
- Skewness, kurtosis
- Coefficient of variation

**Use Case**: Understanding data distribution, identifying outliers, baseline characterization

---

### Normality Testing

**Test**: Shapiro-Wilk test

**Null Hypothesis**: Data is normally distributed

**Alternative Hypothesis**: Data is not normally distributed

**Assumptions**:
- Continuous data
- Random sample
- Sufficient sample size (n ≥ 3)

**Interpretation**:
- p < α: Reject normality assumption
- p ≥ α: Cannot reject normality assumption

**Use Case**: Determining appropriate parametric vs non-parametric tests

---

## Correlation Analysis

### Pearson Correlation

**Purpose**: Measure linear relationship between continuous variables

**Null Hypothesis**: No linear correlation between variables

**Alternative Hypothesis**: Linear correlation exists between variables

**Assumptions**:
- Linear relationship
- Normally distributed variables
- Homoscedasticity
- No significant outliers

**Effect Size**: Correlation coefficient (r)
- 0.0-0.1: Negligible
- 0.1-0.3: Weak
- 0.3-0.5: Moderate
- 0.5-0.7: Strong
- 0.7-1.0: Very strong

**Use Case**: Understanding linear relationships between continuous variables

---

### Spearman Correlation

**Purpose**: Measure monotonic relationship between ordinal or continuous variables

**Null Hypothesis**: No monotonic correlation between variables

**Alternative Hypothesis**: Monotonic correlation exists between variables

**Assumptions**:
- Monotonic relationship
- Ordinal or continuous variables
- No normality assumption

**Effect Size**: Correlation coefficient (ρ)

**Use Case**: Non-linear monotonic relationships, ordinal data

---

### Kendall's Tau

**Purpose**: Measure ordinal association

**Null Hypothesis**: No association between variables

**Alternative Hypothesis**: Association exists between variables

**Assumptions**:
- Ordinal data
- No normality assumption
- Robust to outliers

**Effect Size**: Kendall's tau (τ)

**Use Case**: Small sample sizes, ordinal data, outlier-prone data

---

## Confidence Intervals

### Mean Confidence Interval

**Purpose**: Estimate range of plausible values for population mean

**Formula**: `CI = mean ± t_critical × (std / √n)`

**Assumptions**:
- Random sample
- Normally distributed data or large sample (n ≥ 30)
- Independent observations

**Interpretation**: We are X% confident that the true mean lies within the interval

**Use Case**: Estimating population parameters with uncertainty quantification

---

### Proportion Confidence Interval

**Methods**:
- Normal approximation (large samples)
- Wilson score interval (recommended for most cases)
- Exact binomial (Clopper-Pearson, small samples)

**Assumptions**:
- Random sample
- Independent observations
- Binary outcome

**Interpretation**: We are X% confident that the true proportion lies within the interval

**Use Case**: Estimating proportions with uncertainty quantification

---

## T-Tests

### Independent Samples T-Test

**Purpose**: Compare means between two independent groups

**Null Hypothesis**: Group means are equal

**Alternative Hypothesis**: Group means differ

**Assumptions**:
- Independent observations
- Normally distributed populations
- Homoscedasticity (equal variances) - or use Welch's t-test
- Continuous dependent variable

**Effect Size**: Cohen's d
- 0.2: Small
- 0.5: Medium
- 0.8: Large

**Confidence Interval**: Difference in means

**Use Case**: Comparing profitability between two customer segments

---

### Paired Samples T-Test

**Purpose**: Compare means between two related measurements (same subjects)

**Null Hypothesis**: Mean difference equals zero

**Alternative Hypothesis**: Mean difference differs from zero

**Assumptions**:
- Paired observations (same subjects)
- Normally distributed differences
- Continuous dependent variable
- Independence between pairs

**Effect Size**: Cohen's d (for paired)

**Confidence Interval**: Mean difference

**Use Case**: Before/after comparisons, matched pairs

---

## Chi-Square Tests

### Chi-Square Test of Independence

**Purpose**: Test association between two categorical variables

**Null Hypothesis**: Variables are independent

**Alternative Hypothesis**: Variables are associated

**Assumptions**:
- Independent observations
- Sufficient sample size (expected frequencies ≥ 5)
- Categorical variables
- Random sampling

**Effect Size**:
- Phi coefficient (2×2 tables)
- Cramer's V (larger tables)
  - 0.1: Small
  - 0.3: Medium
  - 0.5: Large

**Use Case**: Testing if churn differs by customer group

---

### Chi-Square Goodness of Fit

**Purpose**: Test if observed distribution matches expected distribution

**Null Hypothesis**: Observed distribution matches expected distribution

**Alternative Hypothesis**: Observed distribution differs from expected distribution

**Assumptions**:
- Independent observations
- Sufficient sample size (expected frequencies ≥ 5)
- Categorical data
- Mutually exclusive categories

**Effect Size**: Phi coefficient

**Use Case**: Testing if segment distribution matches expected proportions

---

## ANOVA

### One-Way ANOVA

**Purpose**: Compare means across three or more groups

**Null Hypothesis**: All group means are equal

**Alternative Hypothesis**: At least one group mean differs

**Assumptions**:
- Independent observations
- Normally distributed populations
- Homoscedasticity (equal variances)
- Continuous dependent variable
- Independent groups

**Effect Size**: Eta-squared (η²)
- 0.01: Small
- 0.06: Medium
- 0.14: Large

**Follow-up**: Post-hoc tests (e.g., Tukey HSD) to identify which groups differ

**Use Case**: Comparing profitability across multiple segments

---

### Two-Way ANOVA

**Purpose**: Test effects of two factors and their interaction

**Null Hypotheses**:
- No main effect of factor 1
- No main effect of factor 2
- No interaction effect

**Alternative Hypotheses**:
- Main effect of factor 1 exists
- Main effect of factor 2 exists
- Interaction effect exists

**Assumptions**:
- Independent observations
- Normally distributed residuals
- Homoscedasticity
- No significant outliers

**Effect Size**: Partial eta-squared

**Use Case**: Testing segment and tenure effects on profitability

---

## Non-Parametric Tests

### Mann-Whitney U Test (Wilcoxon Rank-Sum)

**Purpose**: Compare distributions between two independent groups (non-parametric alternative to t-test)

**Null Hypothesis**: Distributions are equal

**Alternative Hypothesis**: Distributions differ

**Assumptions**:
- Independent observations
- Ordinal or continuous data
- Similar shape distributions (for median comparison)
- No normality assumption

**Effect Size**: r = Z / √N

**Use Case**: When normality assumption violated, comparing two groups

---

### Kruskal-Wallis H-Test

**Purpose**: Compare distributions across three or more groups (non-parametric alternative to ANOVA)

**Null Hypothesis**: All group distributions are equal

**Alternative Hypothesis**: At least one group distribution differs

**Assumptions**:
- Independent observations
- Ordinal or continuous data
- Similar shape distributions
- No normality assumption
- Independent groups

**Effect Size**: Eta-squared based on H statistic

**Follow-up**: Post-hoc pairwise Mann-Whitney tests with Bonferroni correction

**Use Case**: When normality assumption violated, comparing multiple groups

---

## Regression Analysis

### Linear Regression

**Purpose**: Model relationship between continuous dependent variable and independent variables

**Model**: `Y = β₀ + β₁X₁ + β₂X₂ + ... + βₙXₙ + ε`

**Assumptions**:
- Linear relationship between variables
- Independent observations
- Homoscedasticity
- Normally distributed residuals
- No multicollinearity

**Metrics**:
- R²: Proportion of variance explained
- Adjusted R²: R² adjusted for number of predictors
- F-statistic: Overall model significance
- Coefficient p-values: Individual predictor significance
- Confidence intervals: Coefficient uncertainty

**Use Case**: Modeling profitability based on customer characteristics

---

### Logistic Regression

**Purpose**: Model relationship between binary dependent variable and independent variables

**Model**: `log(p/(1-p)) = β₀ + β₁X₁ + β₂X₂ + ... + βₙXₙ`

**Assumptions**:
- Binary dependent variable
- Independent observations
- No perfect multicollinearity
- Large sample size
- Linearity of logit

**Metrics**:
- Pseudo R²: Proportion of variance explained (McFadden, Nagelkerke)
- Likelihood ratio test: Overall model significance
- Coefficient p-values: Individual predictor significance
- Odds ratios: Effect size interpretation
- Confidence intervals: Odds ratio uncertainty

**Use Case**: Modeling churn probability based on customer characteristics

---

## Business Question Tests

### 1. Does Customer Profitability Differ Between Segments?

**Test**: ANOVA (multiple segments) or T-test (two segments)

**Null Hypothesis**: Customer profitability is equal across segments

**Alternative Hypothesis**: Customer profitability differs between segments

**Variables**:
- Dependent: Profitability (continuous)
- Independent: Segment (categorical)

**Business Interpretation**:
- If significant: Segments have different profitability levels. Consider targeted strategies.
- If not significant: Profitability similar across segments. Consider other differentiators.

**Actionable Insights**:
- Identify high-profit segments for retention focus
- Identify low-profit segments for improvement initiatives
- Resource allocation based on segment profitability

---

### 2. Does Churn Differ Significantly Between Customer Groups?

**Test**: Chi-Square Test of Independence

**Null Hypothesis**: Churn rate is independent of customer group

**Alternative Hypothesis**: Churn rate differs by customer group

**Variables**:
- Variable 1: Churn indicator (binary)
- Variable 2: Customer group (categorical)

**Business Interpretation**:
- If significant: Some customer groups have higher churn rates. Investigate causes.
- If not significant: Churn similar across groups. Consider other factors.

**Actionable Insights**:
- Identify high-churn groups for retention focus
- Understand drivers of churn in specific groups
- Target retention interventions appropriately

---

### 3. Does Credit Utilization Relate to Churn?

**Test**: Independent Samples T-Test

**Null Hypothesis**: Credit utilization is equal between churned and non-churned customers

**Alternative Hypothesis**: Credit utilization differs between churned and non-churned customers

**Variables**:
- Dependent: Credit utilization (continuous)
- Independent: Churn status (binary)

**Business Interpretation**:
- If significant: Credit utilization associated with churn. Monitor utilization.
- If not significant: Credit utilization not a churn driver. Consider other factors.

**Actionable Insights**:
- High utilization customers may need retention focus
- Utilization as early warning signal for churn
- Credit management programs for at-risk customers

---

### 4. Does Product Ownership Relate to Profitability?

**Test**: Pearson Correlation

**Null Hypothesis**: No correlation between product ownership and profitability

**Alternative Hypothesis**: Correlation exists between product ownership and profitability

**Variables**:
- Variable 1: Product count (continuous/ordinal)
- Variable 2: Profitability (continuous)

**Business Interpretation**:
- If significant positive: More products associated with higher profitability. Cross-sell opportunities.
- If significant negative: More products associated with lower profitability. Investigate cost structure.
- If not significant: Product count not a profitability driver. Consider product mix.

**Actionable Insights**:
- Cross-sell programs to increase profitability
- Product mix optimization
- Understanding product profitability relationships

---

### 5. Does Payment Behavior Differ Between Risk Groups?

**Test**: ANOVA

**Null Hypothesis**: Payment behavior is equal across risk groups

**Alternative Hypothesis**: Payment behavior differs between risk groups

**Variables**:
- Dependent: Payment behavior metric (e.g., on-time payment rate)
- Independent: Risk group (categorical)

**Business Interpretation**:
- If significant: Payment behavior differs by risk group. Validate risk assessment.
- If not significant: Payment behavior similar across groups. Consider other risk factors.

**Actionable Insights**:
- Validate risk group definitions
- Payment behavior as risk indicator
- Targeted payment support for high-risk groups

---

## P-Value Interpretation Beyond Significance

### Evidence Strength

- **p < 0.001**: Very strong evidence against null hypothesis
- **p < 0.01**: Strong evidence against null hypothesis
- **p < 0.05**: Moderate evidence against null hypothesis
- **p < 0.10**: Weak evidence against null hypothesis
- **p ≥ 0.10**: Insufficient evidence to reject null hypothesis

### Important Considerations

- P-value does not measure effect size or practical significance
- P-value does not measure probability that null hypothesis is true
- P-value depends on sample size (large samples can detect tiny effects)
- Always consider effect size, confidence intervals, and business context
- Statistical significance ≠ practical significance

---

## Effect Size Interpretation

### Cohen's d (T-Tests)

- **0.2**: Small effect
- **0.5**: Medium effect
- **0.8**: Large effect

### Eta-Squared (ANOVA)

- **0.01**: Small effect
- **0.06**: Medium effect
- **0.14**: Large effect

### Phi / Cramer's V (Chi-Square)

- **0.1**: Small effect
- **0.3**: Medium effect
- **0.5**: Large effect

### Correlation Coefficient

- **0.1**: Weak correlation
- **0.3**: Moderate correlation
- **0.5**: Strong correlation

---

## Assumptions and Limitations

### General Assumptions

- Data is representative of population
- Observations are independent
- Sample size is sufficient
- Data quality is adequate (minimal missing values, outliers)

### General Limitations

- Statistical tests do not prove causation
- Results may not generalize to other populations
- Assumptions may not be perfectly met
- Multiple comparisons increase Type I error risk

### Test-Specific Limitations

- **Parametric tests**: Sensitive to assumption violations
- **Non-parametric tests**: Less powerful when assumptions met
- **Correlation**: Does not imply causation
- **Regression**: Assumes correct model specification

---

## Methodology Selection Guide

### When to Use Parametric Tests (T-Tests, ANOVA)

- Data is normally distributed
- Sample size is sufficient (n ≥ 30 per group)
- Homoscedasticity holds
- Continuous dependent variable

### When to Use Non-Parametric Tests (Mann-Whitney, Kruskal-Wallis)

- Normality assumption violated
- Small sample sizes (n < 30 per group)
- Ordinal data
- Significant outliers present

### When to Use Chi-Square Tests

- Categorical variables
- Testing independence or goodness of fit
- Sufficient expected frequencies (≥ 5)

### When to Use Correlation

- Understanding relationship between continuous variables
- Exploratory analysis
- Variable selection for modeling

### When to Use Regression

- Modeling relationships
- Prediction
- Understanding effect of multiple variables
- Controlling for confounders

---

## Usage Examples

### Python Implementation
```python
from src.statistical_analytics.orchestrator import StatisticalOrchestrator

# Initialize orchestrator
orchestrator = StatisticalOrchestrator(alpha=0.05)

# Generate statistical report
report = orchestrator.generate_statistical_report(
    df=customer_data,
    columns=["net_profit", "balance", "transaction_count"]
)

# Run business question analysis
business_results = orchestrator.run_business_question_analysis(
    df=customer_data,
    questions=["profitability_by_segment", "churn_by_customer_group"]
)
```

### Specific Test Example
```python
from src.statistical_analytics.business_tests import BusinessQuestionTests

# Initialize
tester = BusinessQuestionTests(alpha=0.05)

# Test profitability by segment
result = tester.test_profitability_by_segment(
    df=customer_data,
    profitability_col="net_profit",
    segment_col="segment"
)

# View results
print(result.to_dict())
```

---

## Maintenance

### Regular Updates
- Re-run analyses as data updates
- Validate assumptions over time
- Monitor for data drift
- Update business questions as needed

### Documentation
- Keep methodology documentation current
- Document any changes to tests
- Maintain test interpretation guide
- Track business question evolution

---

## Glossary

- **Null Hypothesis (H₀)**: Default assumption of no effect or no difference
- **Alternative Hypothesis (H₁)**: Hypothesis being tested (effect or difference exists)
- **P-value**: Probability of observing results if H₀ is true
- **Effect Size**: Magnitude of the effect, independent of sample size
- **Confidence Interval**: Range of plausible values for a parameter
- **Statistical Significance**: Result unlikely due to chance (p < α)
- **Practical Significance**: Result has meaningful business impact
- **Type I Error**: False positive (reject H₀ when true)
- **Type II Error**: False negative (fail to reject H₀ when false)
- **Power**: Probability of correctly rejecting false H₀
- **Cohen's d**: Effect size for mean differences
- **Eta-squared**: Effect size for ANOVA
- **Phi/Cramer's V**: Effect size for chi-square tests
