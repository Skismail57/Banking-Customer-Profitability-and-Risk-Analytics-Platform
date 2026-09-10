# Assumptions and Limitations

This document outlines the key assumptions and limitations of the Banking Customer Profitability & Risk Analytics — Decision Support Platform.

## Important Disclaimer

**This platform is an analytical and educational model for decision support only.** It does not make actual lending decisions, approve or reject loan applications, or replace human judgment in credit decisions. All risk scores, churn predictions, and recommendations are analytical outputs intended to support decision-making, not replace it.

---

## Platform-Wide Assumptions

### Data Assumptions
- Historical data is available and representative of future patterns
- Data quality is sufficient for reliable analysis
- Customer data is accurate and up-to-date
- Transaction data is complete and properly categorized
- Customer identifiers are consistent across all data sources

### Analytical Assumptions
- Historical patterns will continue to hold (stationarity assumption)
- Customer behavior is relatively stable under normal conditions
- Risk factors are independent unless explicitly modeled
- Model performance on training data will generalize to new data
- Statistical significance tests are appropriate for the data

### Business Assumptions
- Profitability calculations follow standard banking practices
- Risk levels are defined based on industry guidelines
- Customer segments are meaningful and stable
- Product categories are well-defined and consistent
- Time horizons for projections are appropriate

---

## Platform-Wide Limitations

### Data Limitations
- **Historical Bias**: Models may learn and perpetuate historical biases in the data
- **Data Quality**: Results depend on input data quality; poor data leads to poor insights
- **Missing Data**: Gaps in historical data may affect model accuracy
- **Sample Size**: Small sample sizes may lead to unreliable estimates
- **Temporal Changes**: Historical patterns may not predict future behavior

### Analytical Limitations
- **Model Accuracy**: Predictions are estimates, not guarantees
- **Correlation vs Causation**: Analytics identify correlations, not causation
- **Black Swan Events**: Cannot predict unprecedented events
- **External Factors**: Does not account for economic, regulatory, or market changes
- **Approximation**: Many models use approximations that may have error

### Business Limitations
- **Context Specific**: Models may not generalize to different contexts
- **Regulatory Compliance**: May require customization for specific regulatory environments
- **Scalability**: Designed for mid-sized institutions (up to 1M customers)
- **Real-time Processing**: Current implementation uses batch processing
- **Human Judgment**: Does not replace human judgment in decision-making

---

## Module-Specific Assumptions and Limitations

### Risk Migration Matrix

**Assumptions:**
- Risk levels are calculated based on credit utilization and days past due
- Historical data is available for multiple periods
- Risk definitions are consistent over time
- Migration probabilities are stable over time

**Limitations:**
- Does not account for external economic factors
- Assumes risk level transitions are independent
- May not capture sudden risk events (job loss, medical emergency)
- Based on historical patterns which may not predict future migrations

**Fairness Considerations:**
- Risk scoring should be regularly audited for bias
- Consider demographic parity in risk level distributions
- Ensure equal access to credit improvement opportunities

---

### Early-Warning System

**Assumptions:**
- Historical data is available for trend analysis
- Warning thresholds are based on historical patterns
- Early indicators correlate with future risk events

**Limitations:**
- May generate false positives (customers flagged but don't deteriorate)
- May miss false negatives (customers not flagged but deteriorate)
- Thresholds may need calibration for different portfolios
- Does not account for external economic factors

**Fairness Considerations:**
- Warning thresholds should be validated across demographic groups
- Ensure equal false positive rates across segments
- Regular audit for bias in warning signals
- Provide context for warnings to avoid stereotyping

---

### Behavioral Change Detection

**Assumptions:**
- Sufficient historical data is available for comparison
- Behavioral patterns are relatively stable under normal conditions
- Changes are statistically significant when they exceed thresholds

**Limitations:**
- May flag seasonal changes as anomalies
- Requires sufficient data for statistical significance
- Does not account for external events (holidays, promotions)
- May miss gradual long-term changes

**Fairness Considerations:**
- Behavioral baselines should be established per segment
- Avoid penalizing legitimate lifestyle changes
- Consider cultural differences in spending patterns
- Regular audit for bias in change detection

---

### Explainable ML (SHAP)

**Assumptions:**
- Model is trained and available
- Feature names are available
- SHAP values can be computed for the model

**Limitations:**
- SHAP computation can be expensive for large datasets
- Approximate SHAP values may have some error
- Does not explain feature interactions by default
- May not work well with all model types

**Fairness Considerations:**
- Analyze feature importance across demographic groups
- Check for disparate impact in feature contributions
- Ensure explanations are understandable to all stakeholders
- Regular audit for bias in feature importance

---

### Model Monitoring

**Assumptions:**
- Historical performance data is available for comparison
- Feature distributions are relatively stable under normal conditions
- Performance degradation indicates potential model drift

**Limitations:**
- May flag seasonal changes as drift
- Requires sufficient historical data for comparison
- Does not account for external economic factors
- Thresholds may need calibration for different models

**Fairness Considerations:**
- Monitor performance across demographic groups
- Check for disparate impact in model degradation
- Ensure alerts are not biased against any segment
- Regular audit for bias in drift detection

---

### Scenario Analysis

**Assumptions:**
- Scenario parameters are based on historical stress events
- Customer behavior follows historical patterns under stress
- Correlations between risk factors are stable
- Stress events are independent

**Limitations:**
- Cannot predict unprecedented events (black swans)
- Assumes historical patterns will repeat
- Does not account for policy interventions
- May overestimate or underestimate actual impact

**Fairness Considerations:**
- Analyze scenario impact across demographic groups
- Check for disparate impact under stress scenarios
- Ensure stress testing considers vulnerable populations
- Regular audit for bias in scenario assumptions

---

### Portfolio Concentration Analysis

**Assumptions:**
- Concentration thresholds based on regulatory guidelines
- HHI interpretation follows standard banking practices
- Concentration ratios are calculated on exposure amounts

**Limitations:**
- Does not account for correlation between exposures
- Assumes independence of concentration risks
- May not capture all dimensions of concentration
- Thresholds may need calibration for different portfolios

**Fairness Considerations:**
- Analyze concentration across demographic groups
- Check for disparate impact in concentration limits
- Ensure diversification benefits are accessible to all segments
- Regular audit for bias in concentration assessment

---

### Customer Profitability Decomposition

**Assumptions:**
- Profitability data is available at the customer and product level
- Cost allocation rules are consistent across customers
- Expected credit loss calculations are based on risk models

**Limitations:**
- Cost allocation may not be perfectly accurate
- Does not account for indirect costs
- Expected credit loss is a model estimate
- May not capture all revenue and cost components

**Fairness Considerations:**
- Analyze profitability decomposition across demographic groups
- Check for disparate impact in cost allocation
- Ensure profitability metrics are not biased
- Regular audit for bias in profitability assessment

---

### CLV Sensitivity Analysis

**Assumptions:**
- CLV follows a discounted cash flow model
- Retention rate is constant over time
- Revenue and costs are stable over time horizon
- Discount rate reflects time value of money

**Limitations:**
- Assumes constant parameters (may not reflect reality)
- Does not account for customer lifecycle changes
- Sensitivity ranges are arbitrary
- May not capture non-linear relationships

**Fairness Considerations:**
- Analyze CLV sensitivity across demographic groups
- Check for disparate impact in CLV assumptions
- Ensure CLV estimates are not biased
- Regular audit for bias in CLV calculations

---

### Point-in-Time Feature Engineering

**Assumptions:**
- Historical data is available with timestamps
- Feature windows are defined relative to prediction date
- Data is chronologically ordered
- No future information is used

**Limitations:**
- Requires sufficient historical data for all windows
- May not capture all relevant temporal patterns
- Window sizes are fixed (may not be optimal)
- Does not account for seasonality automatically

**Fairness Considerations:**
- Ensure feature windows are consistent across customers
- Check for temporal bias in feature availability
- Ensure feature engineering does not introduce bias
- Regular audit for bias in feature distributions

---

### Data Lineage

**Assumptions:**
- All data transformations are logged
- Source and destination tables are known
- Transformation metadata is captured

**Limitations:**
- Requires manual registration of transformations
- Does not automatically detect lineage
- May not capture all implicit dependencies
- Lineage is only as good as the logging

**Fairness Considerations:**
- Ensure lineage tracking is consistent across all data
- Check for disparate impact in data transformations
- Ensure audit trail is complete and unbiased
- Regular audit for bias in lineage tracking

---

### Data Quality Scoring

**Assumptions:**
- Quality thresholds are based on industry best practices
- Data validation rules are defined per column
- Freshness requirements are known for each dataset

**Limitations:**
- Thresholds may need calibration for specific use cases
- Does not detect all types of data quality issues
- May not capture semantic quality issues
- Validation rules must be manually defined

**Fairness Considerations:**
- Ensure quality scoring is consistent across data sources
- Check for disparate impact in quality assessments
- Ensure quality metrics are not biased
- Regular audit for bias in quality scoring

---

## Fairness and Ethics Considerations

### General Principles
- **Transparency**: All models and assumptions should be documented
- **Accountability**: Human judgment should always override model outputs
- **Fairness**: Regular audits for bias across demographic groups
- **Privacy**: Customer data should be protected and used responsibly
- **Explainability**: Model decisions should be explainable to stakeholders

### Bias Mitigation
- Regularly audit models for disparate impact
- Use fairness-aware machine learning techniques
- Ensure representative training data
- Monitor model performance across segments
- Provide recourse for affected customers

### Regulatory Considerations
- Ensure compliance with relevant regulations (e.g., ECOA, FCRA)
- Document model governance processes
- Maintain audit trails for all decisions
- Regular model validation and review
- Stakeholder communication and transparency

---

## Conclusion

This platform is designed to support decision-making, not replace it. Users should:
1. Understand the assumptions and limitations of each module
2. Validate results against business knowledge
3. Use outputs as one input among many in decision-making
4. Regularly review and update models
5. Maintain human oversight of all automated processes

For questions or concerns about assumptions and limitations, please refer to the module-specific documentation or contact the development team.
