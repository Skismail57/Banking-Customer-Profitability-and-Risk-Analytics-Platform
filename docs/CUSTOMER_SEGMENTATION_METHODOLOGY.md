# Customer Segmentation Methodology

## Overview

This document defines the methodology for customer segmentation in the banking platform. The approach combines business-rule based segmentation with data-driven clustering to create meaningful customer segments for portfolio management and targeted marketing.

---

## Segmentation Approaches

### 1. Business-Rule Segmentation

**Description**: Segmentation based on predefined business rules and thresholds.

**Advantages**:
- Transparent and interpretable
- Easy to implement and maintain
- Aligns with business intuition
- Stable over time

**Disadvantages**:
- May not capture complex patterns
- Thresholds may be arbitrary
- Limited flexibility

**Implemented Segments**:

#### Profitability-Based Segments
- **High Value**: Net profit ≥ $50,000, margin ≥ 15%
- **Medium Value**: Net profit $10,000-$50,000, margin ≥ 10%
- **Low Value**: Net profit $0-$10,000, margin ≥ 5%
- **Unprofitable**: Net profit < $0

#### Behavior-Based Segments
- **Highly Engaged**: Transaction frequency ≥ 10, products ≥ 3
- **Moderately Engaged**: Transaction frequency 5-10, products ≥ 2
- **Lowly Engaged**: Transaction frequency < 5 or products < 2

#### Lifecycle-Based Segments
- **New Customer**: Tenure ≤ 90 days
- **Established Customer**: Tenure 90-365 days
- **Long-Term Customer**: Tenure > 365 days

---

### 2. Data-Driven Clustering

**Description**: Segmentation using unsupervised machine learning algorithms.

**Advantages**:
- Discovers natural groupings in data
- Captures complex patterns
- Data-driven approach
- Can reveal unexpected segments

**Disadvantages**:
- Less interpretable
- May produce unstable segments
- Requires feature engineering
- Number of clusters not predetermined

**Implemented Algorithms**:

#### K-Means Clustering
- **Description**: Partitions customers into K clusters based on feature similarity
- **Optimal Cluster Selection**: Uses silhouette score or elbow method
- **Strengths**: Fast, scalable, works well with spherical clusters
- **Weaknesses**: Assumes spherical clusters, sensitive to outliers, requires K specification
- **Use Case**: General-purpose segmentation when clusters expected to be spherical

#### Hierarchical Clustering
- **Description**: Builds hierarchy of clusters using agglomerative approach
- **Linkage Methods**: Ward, complete, average, single
- **Strengths**: No need to specify K, provides dendrogram, captures nested structure
- **Weaknesses**: Computationally expensive, sensitive to noise, not scalable
- **Use Case**: When hierarchical relationships are important or cluster count uncertain

#### DBSCAN Clustering
- **Description**: Density-based clustering that identifies arbitrary-shaped clusters
- **Parameters**: eps (neighborhood radius), min_samples (minimum points in neighborhood)
- **Strengths**: Handles arbitrary shapes, identifies noise/outliers, no need to specify K
- **Weaknesses**: Sensitive to parameter selection, struggles with varying density
- **Use Case**: When clusters expected to be non-spherical or outlier detection needed

---

## Feature Engineering

### Base Features

| Feature | Description | Data Type | Source |
|---------|-------------|-----------|--------|
| profitability | Net profit | Currency | Profitability analytics |
| transaction_frequency | Number of transactions | Numeric | Transaction analytics |
| balance | Total account balance | Currency | Account data |
| product_count | Number of products | Numeric | Product data |
| credit_utilization | Credit utilization ratio | Percentage | Credit data |
| loan_exposure | Total loan exposure | Currency | Loan data |
| tenure_days | Customer tenure in days | Numeric | Customer data |
| engagement_score | Composite engagement score | Numeric | Derived |

### Derived Features

| Feature | Formula | Purpose |
|---------|---------|---------|
| profit_per_transaction | profitability / (transaction_frequency + 1) | Profit efficiency |
| balance_per_product | balance / (product_count + 1) | Product intensity |
| exposure_per_tenure | loan_exposure / (tenure_days + 1) | Exposure growth rate |

### Feature Preprocessing

1. **Missing Value Handling**: Median imputation (default), mean, or zero
2. **Scaling**: Standard scaling (z-score) or min-max scaling
3. **Feature Selection**: Select relevant features for clustering

---

## Cluster Evaluation

### Evaluation Metrics

#### Silhouette Score
- **Range**: -1 to 1
- **Interpretation**:
  - > 0.7: Strong structure
  - 0.5-0.7: Reasonable structure
  - 0.25-0.5: Weak structure
  - < 0.25: No substantial structure
- **Use**: Measures how similar an object is to its own cluster compared to other clusters

#### Calinski-Harabasz Score
- **Range**: 0 to ∞
- **Interpretation**: Higher values indicate better defined clusters
- **Use**: Ratio of between-cluster dispersion to within-cluster dispersion

#### Davies-Bouldin Score
- **Range**: 0 to ∞
- **Interpretation**:
  - < 0.5: Well-separated clusters
  - 0.5-1.0: Reasonably separated clusters
  - > 1.0: Poorly separated clusters
- **Use**: Average similarity between each cluster and its most similar cluster

#### Cluster Size Balance
- **Metrics**: Coefficient of variation, Gini coefficient
- **Interpretation**:
  - CV < 0.3: Well-balanced
  - CV 0.3-0.5: Moderately balanced
  - CV > 0.5: Poorly balanced
- **Use**: Measures how evenly customers are distributed across clusters

---

## Segment Profiling

### Profile Components

#### Characteristics
- Mean, median, standard deviation for each feature
- Min and max values
- Deviation from overall population

#### Business Metrics
- Customer count
- Percentage of total customers
- Key characteristics comparison

#### Business Interpretation
- Key characteristics identification
- Business implications
- Recommended actions

### Interpretation Guidelines

#### Profitability Characteristics
- **Higher than average**: Prioritize retention, cross-sell opportunities
- **Lower than average**: Review relationship, cost optimization

#### Engagement Characteristics
- **Higher than average**: Loyalty programs, rewards, advocacy
- **Lower than average**: Re-engagement campaigns, product education

#### Exposure Characteristics
- **Higher than average**: Risk monitoring, regular review
- **Lower than average**: Growth opportunity, relationship building

---

## Stability Analysis

### Methods

#### Bootstrap Stability
- **Description**: Resample data and recluster to assess stability
- **Metric**: Adjusted Rand Index (ARI) between original and bootstrap clusterings
- **Interpretation**:
  - ARI > 0.8: Very stable
  - ARI 0.6-0.8: Stable
  - ARI 0.4-0.6: Moderately stable
  - ARI < 0.4: Unstable

#### Temporal Stability
- **Description**: Compare segmentations across different time periods
- **Metric**: Adjusted Rand Index between periods
- **Use**: Assess how segments change over time

#### Cross-Method Comparison
- **Description**: Compare different clustering methods
- **Metric**: Adjusted Rand Index or Adjusted Mutual Information
- **Use**: Assess consistency across algorithms

---

## Methodology Selection Guide

### When to Use Business-Rule Segmentation
- Clear business criteria exist
- Interpretability is critical
- Stability over time required
- Regulatory or compliance needs
- Simple, actionable segments needed

### When to Use K-Means
- Large datasets (scalability)
- Spherical clusters expected
- Number of clusters approximately known
- Fast computation needed
- General-purpose segmentation

### When to Use Hierarchical Clustering
- Hierarchical relationships important
- Cluster count uncertain
- Dendrogram visualization needed
- Small to medium datasets
- Nested segments desired

### When to Use DBSCAN
- Arbitrary-shaped clusters expected
- Outlier detection needed
- Cluster count unknown
- Varying cluster density
- Noise in data

---

## Optimal Cluster Selection

### Silhouette Method
- **Process**: Calculate silhouette score for different K values
- **Selection**: Choose K with maximum silhouette score
- **Advantages**: Direct measure of cluster quality
- **Disadvantages**: May prefer fewer clusters, computationally expensive

### Elbow Method
- **Process**: Plot inertia vs K, find "elbow" point
- **Selection**: Choose K at point of maximum curvature
- **Advantages**: Simple, visual
- **Disadvantages**: Elbow may be ambiguous, subjective

### Recommendation
- Use silhouette method for primary selection
- Validate with elbow method
- Consider business interpretability
- Start with 3-6 clusters for interpretability

---

## Assumptions

### Data Assumptions
- Data is clean and complete (after preprocessing)
- Features are relevant to customer behavior
- Customer behavior is relatively stable
- No significant temporal drift in data

### Algorithm Assumptions
- K-Means: Clusters are spherical, similar size
- Hierarchical: Hierarchical structure exists
- DBSCAN: Clusters have similar density

### Business Assumptions
- Segments will be used for portfolio management
- Actionable insights can be derived from segments
- Segment stability is desirable
- Business rules reflect actual customer behavior

---

## Limitations

### Data Limitations
- Missing data may affect clustering
- Feature selection bias
- Temporal changes not captured in snapshot
- Outliers may skew results

### Algorithm Limitations
- K-Means: Sensitive to initialization, assumes spherical clusters
- Hierarchical: Not scalable, sensitive to noise
- DBSCAN: Parameter sensitivity, struggles with varying density

### Business Limitations
- Segments may not align with business needs
- Interpretation may be subjective
- Actionability not guaranteed
- Stability not assured

### General Limitations
- Segmentation is descriptive, not predictive
- Does not capture causal relationships
- May not reflect future behavior
- Requires regular updating

---

## Interpretation Guidelines

### Segment Size Considerations
- **Large segments (> 30%)**: May be too broad, consider sub-segmentation
- **Small segments (< 5%)**: May be outliers, consider consolidation
- **Balanced segments**: Generally more actionable

### Feature Importance
- Identify features that most distinguish segments
- Focus on business-relevant features
- Consider feature correlations

### Business Actionability
- Ensure segments have clear business implications
- Define specific actions for each segment
- Consider resource constraints

### Stability Considerations
- Prefer stable segments for long-term strategy
- Monitor segment changes over time
- Update segments periodically

---

## Usage Examples

### Python Implementation
```python
from src.customer_segmentation.orchestrator import SegmentationOrchestrator
from datetime import date

# Initialize orchestrator
orchestrator = SegmentationOrchestrator(as_of_date=date(2024, 1, 15))

# Business-rule segmentation
business_result = orchestrator.run_business_rule_segmentation(
    df=customer_data,
    segment_type="combined"
)

# K-Means clustering
clustering_result = orchestrator.run_clustering_segmentation(
    df=customer_data,
    feature_columns=["profitability", "transaction_frequency", "balance"],
    method="kmeans"
)

# Generate segment profiles
profiles = orchestrator.generate_segment_profiles(
    df=clustering_result["segmented_df"],
    feature_columns=["profitability", "transaction_frequency", "balance"]
)
```

### Method Comparison
```python
# Compare multiple methods
comparison = orchestrator.compare_segmentation_methods(
    df=customer_data,
    feature_columns=["profitability", "transaction_frequency", "balance"],
    methods=["kmeans", "hierarchical"]
)
```

---

## Maintenance

### Regular Updates
- Re-run segmentation quarterly or as needed
- Update feature set as business evolves
- Review segment definitions periodically
- Validate segment stability over time

### Parameter Tuning
- Review clustering parameters regularly
- Adjust based on business feedback
- Monitor segment quality metrics
- Update business rules as needed

### Documentation
- Keep methodology documentation current
- Document any changes to segments
- Maintain segment interpretation guide
- Track segment performance metrics

---

## Glossary

- **ARI**: Adjusted Rand Index - measure of clustering similarity
- **AMI**: Adjusted Mutual Information - measure of clustering similarity
- **Silhouette Score**: Measure of cluster cohesion and separation
- **Inertia**: Sum of squared distances to cluster centers (K-Means)
- **Bootstrap**: Resampling technique for stability assessment
- **Dendrogram**: Tree diagram showing hierarchical clustering
- **Eps**: Maximum distance between samples in DBSCAN
- **Min Samples**: Minimum points in neighborhood for DBSCAN
- **CV**: Coefficient of Variation - measure of dispersion
- **Gini Coefficient**: Measure of inequality
