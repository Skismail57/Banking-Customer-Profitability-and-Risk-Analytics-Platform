# Predictive Analytics Framework

## Overview

This document defines the reusable ML architecture for predictive analytics in the banking platform. The framework supports multiple model types (churn prediction, default-risk classification, customer profitability prediction, CLV prediction, transaction anomaly detection) with appropriate metrics, class imbalance handling, and reproducibility features.

---

## Architecture Components

### 1. Base Classes

**ModelType Enum**: Types of predictive models
- `CHURN_PREDICTION`: Churn prediction
- `DEFAULT_RISK`: Default risk classification
- `PROFITABILITY_PREDICTION`: Customer profitability prediction
- `CLV_PREDICTION`: CLV prediction
- `ANOMALY_DETECTION`: Transaction anomaly detection

**ProblemType Enum**: Types of ML problems
- `BINARY_CLASSIFICATION`: Binary classification
- `MULTICLASS_CLASSIFICATION`: Multiclass classification
- `REGRESSION`: Regression
- `ANOMALY_DETECTION`: Anomaly detection

**ModelResult Dataclass**: Result of model training/prediction
- `model_name`: Name of the model
- `model_type`: Type of model (ModelType)
- `problem_type`: Type of problem (ProblemType)
- `metrics`: Dictionary of evaluation metrics
- `feature_importance`: Dictionary of feature importance values
- `predictions`: Model predictions
- `training_time`: Training time in seconds
- `model_metadata`: Additional model metadata

**ModelBase Class**: Base class for all models
- `random_state`: Random state for reproducibility
- `get_appropriate_metrics()`: Returns appropriate metrics for problem type

---

### 2. Data Splitting

**DataSplitter**: Split data into train/validation/test sets

**Methods**:
- `split_train_val_test()`: Random split with stratification
  - Default proportions: 60% train, 20% validation, 20% test
  - Stratified split for classification problems
  - Configurable proportions and random state

- `time_aware_split()`: Time-based splitting for temporal data
  - Split based on date ranges
  - Prevents data leakage from future
  - Critical for time-series and forecasting

- `get_features_and_target()`: Separate features and target
  - Automatic feature selection (all except target)
  - Manual feature selection support

**Use Case**: Ensuring proper train/validation/test separation with temporal correctness

---

### 3. Preprocessing Pipelines

**PreprocessingPipeline**: Create preprocessing pipelines for ML models

**Methods**:
- `create_preprocessing_pipeline()`: Create ColumnTransformer
  - Numeric features: Imputation (median) + Scaling (StandardScaler or MinMaxScaler)
  - Categorical features: Imputation (most frequent) + One-Hot Encoding
  - Configurable transformers

- `engineer_features()`: Engineer features based on configuration
  - Ratio features: numerator / denominator
  - Log features: log1p transformation
  - Binning features: Discretize continuous variables
  - Interaction features: Multiply or add features

**Use Case**: Consistent preprocessing across models, feature engineering automation

---

### 4. Baseline Models

**BaselineModels**: Create and evaluate baseline models

**Methods**:
- `get_baseline_model()`: Get baseline model for problem type
  - Dummy models: Random guessing (stratified)
  - Simple models: Logistic Regression, Linear Regression
  - Provides performance baseline

- `train_baseline()`: Train baseline model
  - Returns ModelResult with baseline performance
  - Training time tracking

**Use Case**: Establishing performance baselines before complex modeling

---

### 5. Model Comparison

**ModelComparator**: Compare multiple models

**Methods**:
- `compare_models()`: Compare model results
  - Creates comparison DataFrame
  - Sorts by primary metric
  - Includes all metrics and training time

- `select_best_model()`: Select best model based on primary metric
  - Returns best ModelResult
  - Configurable primary metric

**Use Case**: Model selection and performance comparison

---

### 6. Class Imbalance Handling

**ClassImbalanceHandler**: Handle class imbalance in classification

**Methods**:
- `check_imbalance()`: Check for class imbalance
  - Calculates class counts and proportions
  - Calculates imbalance ratio
  - Determines if imbalance is significant (ratio > 2.0)

- `handle_imbalance()`: Handle class imbalance
  - SMOTE: Synthetic Minority Over-sampling Technique
  - Oversampling: Random oversampling of minority class
  - Undersampling: Random undersampling of majority class
  - Configurable sampling strategy

**Use Case**: Addressing class imbalance in churn and default risk prediction

---

### 7. Cross-Validation and Hyperparameter Tuning

**HyperparameterTuner**: Cross-validation and hyperparameter tuning

**Methods**:
- `cross_validate()`: Perform cross-validation
  - Configurable number of folds (default: 5)
  - Configurable scoring metric
  - Returns mean and std of scores

- `grid_search()`: Grid search hyperparameter tuning
  - Exhaustive search over parameter grid
  - Cross-validation for evaluation
  - Returns best parameters and model

- `randomized_search()`: Randomized search hyperparameter tuning
  - Random sampling from parameter distributions
  - More efficient than grid search for large spaces
  - Configurable number of iterations

**Use Case**: Model optimization and hyperparameter selection

---

### 8. Model Persistence

**ModelPersistence**: Handle model persistence and reproducibility

**Methods**:
- `save_model()`: Save model with metadata
  - Saves model and metadata together
  - Generates unique file path with hash
  - Saves metadata separately as JSON
  - Includes timestamp, version, random state

- `load_model()`: Load model with metadata
  - Returns model and metadata
  - Ensures reproducibility

- `get_model_metadata()`: Get model metadata without loading model
  - Quick metadata inspection
  - Useful for model registry

**Use Case**: Model versioning, reproducibility, model registry

---

### 9. Model Evaluation

**ModelEvaluator**: Evaluate models with appropriate metrics

**Methods**:
- `evaluate_classification()`: Evaluate classification models
  - Metrics: accuracy, precision, recall, F1, confusion matrix
  - Optional: ROC-AUC, PR-AUC (if probabilities available)
  - Handles binary and multiclass

- `evaluate_regression()`: Evaluate regression models
  - Metrics: MSE, RMSE, MAE, R²
  - Appropriate for continuous targets

- `evaluate_model()`: Evaluate model based on problem type
  - Automatically selects appropriate evaluation
  - Supports all problem types

- `get_feature_importance()`: Get feature importance from model
  - Supports tree-based models (feature_importances_)
  - Supports linear models (coef_)
  - Returns dictionary of feature: importance

**Use Case**: Comprehensive model evaluation with appropriate metrics

---

## Predictive Models

### 1. Churn Prediction Model

**Problem Type**: Binary Classification

**Model Types**:
- Logistic Regression (baseline, interpretable)
- Random Forest (non-linear, robust)
- Gradient Boosting (high accuracy)

**Class Imbalance Handling**:
- Default: SMOTE oversampling
- Configurable: oversampling, undersampling, or none
- Class weight: balanced in models

**Metrics**:
- Primary: F1-score (balance precision and recall)
- Secondary: Precision, Recall, ROC-AUC, PR-AUC, Accuracy
- Confusion Matrix

**Use Case**: Predicting customer churn for retention interventions

**Key Features**:
- Point-in-time correct features (no future information)
- Feature importance for interpretability
- Probability predictions for risk scoring

---

### 2. Default Risk Model

**Problem Type**: Binary Classification

**Model Types**:
- Logistic Regression (baseline, interpretable)
- Random Forest (non-linear, robust)
- Gradient Boosting (high accuracy)

**Class Imbalance Handling**:
- Default: SMOTE oversampling
- Configurable: oversampling, undersampling, or none
- Class weight: balanced in models

**Metrics**:
- Primary: F1-score (balance precision and recall)
- Secondary: Precision, Recall, ROC-AUC, PR-AUC, Accuracy
- Confusion Matrix

**Use Case**: Predicting loan default risk for credit decisions

**Key Features**:
- Feature importance for risk factor identification
- Probability predictions for risk scoring
- Interpretable baseline model

---

### 3. Customer Profitability Prediction Model

**Problem Type**: Regression

**Model Types**:
- Linear Regression (baseline, interpretable)
- Ridge Regression (regularized linear)
- Random Forest (non-linear, robust)
- Gradient Boosting (high accuracy)

**Metrics**:
- Primary: R² (explained variance)
- Secondary: RMSE, MAE, MSE

**Use Case**: Predicting customer profitability for resource allocation

**Key Features**:
- Feature importance for profitability drivers
- Continuous value predictions
- Interpretable baseline model

---

### 4. CLV Prediction Model

**Problem Type**: Regression

**Model Types**:
- Linear Regression (baseline, interpretable)
- Ridge Regression (regularized linear)
- Random Forest (non-linear, robust)
- Gradient Boosting (high accuracy)

**Metrics**:
- Primary: R² (explained variance)
- Secondary: RMSE, MAE, MSE

**Use Case**: Predicting Customer Lifetime Value for customer valuation

**Key Features**:
- Feature importance for CLV drivers
- Continuous value predictions
- Aligns with CLV methodology

---

### 5. Transaction Anomaly Detection Model

**Problem Type**: Anomaly Detection

**Model Types**:
- Isolation Forest (unsupervised, efficient)
- One-Class SVM (unsupervised, kernel-based)

**Parameters**:
- Contamination: Expected proportion of anomalies (default: 0.1)

**Metrics**:
- Primary: F1-score (if labels available)
- Secondary: Precision, Recall, AUC-ROC
- Note: Evaluation requires labeled anomalies

**Use Case**: Detecting fraudulent or suspicious transactions

**Key Features**:
- Unsupervised learning (no labels required)
- Anomaly scores for risk ranking
- Configurable contamination parameter

---

## Metrics by Problem Type

### Binary Classification (Churn, Default Risk)

**Primary Metric**: F1-score
- Balances precision and recall
- Appropriate for imbalanced datasets
- Focus on both false positives and false negatives

**Secondary Metrics**:
- **Precision**: Minimize false positives (unnecessary interventions)
- **Recall**: Minimize false negatives (missed risks/churn)
- **ROC-AUC**: Overall ranking performance
- **PR-AUC**: More informative for imbalanced data
- **Accuracy**: Overall correctness (less informative for imbalance)

**Business Interpretation**:
- High precision: Few false alarms, efficient resource use
- High recall: Few missed cases, comprehensive coverage
- High F1: Balanced approach

---

### Regression (Profitability, CLV)

**Primary Metric**: R² (R-squared)
- Proportion of variance explained
- Higher is better (0 to 1)
- Indicates model fit quality

**Secondary Metrics**:
- **RMSE**: Root Mean Squared Error (same units as target)
- **MAE**: Mean Absolute Error (same units as target)
- **MSE**: Mean Squared Error (penalizes large errors)

**Business Interpretation**:
- High R²: Model explains most variance in target
- Low RMSE/MAE: Predictions close to actual values

---

### Anomaly Detection

**Primary Metric**: F1-score (if labels available)
- Balances precision and recall
- Appropriate for imbalanced anomaly detection

**Secondary Metrics**:
- **Precision**: Minimize false alarms
- **Recall**: Minimize missed anomalies
- **AUC-ROC**: Ranking performance

**Business Interpretation**:
- High precision: Few false fraud alerts
- High recall: Few missed fraud cases

---

## Class Imbalance Handling

### When to Handle Imbalance

**Threshold**: Imbalance ratio > 2.0 (majority class > 2x minority class)

**Common in Banking**:
- Churn prediction (typically < 10% churn)
- Default risk prediction (typically < 5% default)
- Anomaly detection (typically < 1% anomalies)

### Methods

**SMOTE (Synthetic Minority Over-sampling Technique)**:
- Creates synthetic samples for minority class
- Default method for most cases
- Works well with decision trees

**Random Oversampling**:
- Duplicates minority class samples
- Simple but may overfit
- Useful when SMOTE not appropriate

**Random Undersampling**:
- Removes majority class samples
- May lose information
- Useful when dataset is very large

**Class Weighting**:
- Weight classes inversely proportional to frequency
- Built into many sklearn models
- Alternative to resampling

### Recommendations

**Churn Prediction**: SMOTE (default)
**Default Risk**: SMOTE (default)
**Anomaly Detection**: Not applicable (unsupervised)

---

## Reproducibility

### Random State

**Default**: 42 (consistent across all components)

**Purpose**:
- Reproducible model training
- Reproducible data splits
- Reproducible hyperparameter tuning

**Implementation**:
- All components accept random_state parameter
- Default to 42 if not specified
- Stored in model metadata

### Model Persistence

**Components Saved**:
- Model object (trained model)
- Metadata (version, timestamp, random state, parameters)
- Feature names (for reproducibility)

**File Naming**:
- Hash-based unique identifier
- Includes model name and version
- Prevents overwriting

**Metadata Storage**:
- Separate JSON file
- Quick inspection without loading model
- Model registry support

---

## Usage Examples

### Churn Prediction
```python
from src.predictive_analytics.orchestrator import PredictiveAnalyticsOrchestrator

# Initialize orchestrator
orchestrator = PredictiveAnalyticsOrchestrator(random_state=42)

# Train churn prediction models
results = orchestrator.train_churn_model(
    df=customer_data,
    target_column="is_churned",
    feature_columns=["balance", "transaction_count", "tenure_days"],
    model_types=["logistic", "random_forest", "gradient_boosting"],
    handle_imbalance=True
)

# View results
print(results["best_model"])
print(results["comparison"])
```

### Default Risk Prediction
```python
# Train default risk models
results = orchestrator.train_default_risk_model(
    df=customer_data,
    target_column="is_default",
    model_types=["logistic", "random_forest"],
    handle_imbalance=True
)
```

### Profitability Prediction
```python
# Train profitability prediction models
results = orchestrator.train_profitability_model(
    df=customer_data,
    target_column="net_profit",
    model_types=["linear", "random_forest"]
)
```

### CLV Prediction
```python
# Train CLV prediction models
results = orchestrator.train_clv_model(
    df=customer_data,
    target_column="clv",
    model_types=["linear", "random_forest"]
)
```

### Anomaly Detection
```python
# Train anomaly detection model
results = orchestrator.train_anomaly_detection_model(
    df=transaction_data,
    feature_columns=["amount", "location", "time"],
    model_types=["isolation_forest"],
    contamination=0.05
)
```

### Custom Pipeline
```python
from src.predictive_analytics.splitting import DataSplitter
from src.predictive_analytics.churn_model import ChurnPredictionModel

# Custom pipeline
splitter = DataSplitter(random_state=42)
churn_model = ChurnPredictionModel(random_state=42)

# Split data
train_df, val_df, test_df = splitter.split_train_val_test(df, "is_churned")

# Train model
result = churn_model.train(
    X_train, y_train, X_val, y_val,
    model_type="random_forest",
    handle_imbalance=True
)
```

---

## Best Practices

### 1. Data Splitting

**Use Time-Aware Splitting**:
- For time-series or forecasting
- Prevents data leakage from future
- Critical for realistic performance estimates

**Use Stratified Splitting**:
- For classification problems
- Maintains class distribution
- Prevents biased splits

### 2. Feature Engineering

**Point-in-Time Correctness**:
- Use only data available at prediction time
- No future information in features
- Critical for realistic performance

**Feature Scaling**:
- Scale numeric features (StandardScaler or MinMaxScaler)
- Required for many models (logistic regression, SVM)
- Tree-based models less sensitive

### 3. Class Imbalance

**Always Check Imbalance**:
- Use `check_imbalance()` before training
- Understand class distribution
- Choose appropriate handling method

**Don't Optimize Only for Accuracy**:
- Accuracy misleading for imbalanced data
- Use F1, precision, recall instead
- Consider business costs of errors

### 4. Model Selection

**Start with Baseline**:
- Train dummy/simple baseline first
- Establish performance floor
- Justify complex models

**Compare Multiple Models**:
- Test different model types
- Use appropriate metrics
- Consider interpretability vs accuracy

### 5. Hyperparameter Tuning

**Justify Tuning**:
- Only tune if baseline insufficient
- Start with randomized search (faster)
- Use grid search for fine-tuning

**Cross-Validation**:
- Use CV for hyperparameter tuning
- Prevents overfitting to validation set
- More robust performance estimates

### 6. Model Persistence

**Save with Metadata**:
- Always save model with metadata
- Include random state and parameters
- Enable reproducibility

**Version Control**:
- Use version numbers
- Track model lineage
- Maintain model registry

---

## Assumptions and Limitations

### General Assumptions

- Data is representative of population
- Features are properly engineered
- Sufficient sample size for training
- Random state ensures reproducibility

### General Limitations

- Models are predictive, not causal
- Performance may degrade over time (concept drift)
- Requires regular retraining
- Feature engineering critical for performance

### Model-Specific Limitations

**Churn Prediction**:
- Churn definition may not capture all types
- Point-in-time correctness requires careful implementation
- Class imbalance challenging

**Default Risk**:
- Limited by historical default data
- Economic conditions may change
- Regulatory constraints on model use

**Profitability Prediction**:
- Profitability may be influenced by external factors
- May not capture future business changes
- Requires accurate cost allocation

**CLV Prediction**:
- Relies on retention rate assumptions
- Future behavior may not match historical
- Discount rate selection subjective

**Anomaly Detection**:
- Unsupervised, requires labeled anomalies for evaluation
- Contamination parameter critical
- May miss new types of anomalies

---

## Maintenance

### Regular Updates

- Retrain models quarterly or as needed
- Monitor model performance over time
- Update feature engineering as needed
- Validate assumptions regularly

### Model Monitoring

- Track primary metrics over time
- Monitor for concept drift
- Compare to baseline performance
- Alert on performance degradation

### Documentation

- Keep framework documentation current
- Document model changes and versions
- Maintain feature engineering guide
- Track model performance metrics

---

## Glossary

- **Train/Validation/Test Split**: Separation of data for training, tuning, and final evaluation
- **Time-Aware Splitting**: Data split based on time to prevent future data leakage
- **Stratified Split**: Data split maintaining class distribution
- **Class Imbalance**: Unequal distribution of classes in classification
- **SMOTE**: Synthetic Minority Over-sampling Technique for imbalanced data
- **Cross-Validation**: Model evaluation using multiple train/test splits
- **Hyperparameter Tuning**: Optimizing model hyperparameters
- **Grid Search**: Exhaustive search over hyperparameter grid
- **Randomized Search**: Random sampling from hyperparameter distributions
- **Feature Importance**: Relative importance of features in model predictions
- **F1-Score**: Harmonic mean of precision and recall
- **ROC-AUC**: Area under ROC curve (ranking performance)
- **PR-AUC**: Area under Precision-Recall curve (informative for imbalance)
- **R²**: Proportion of variance explained (regression)
- **RMSE**: Root Mean Squared Error (regression)
- **MAE**: Mean Absolute Error (regression)
- **Point-in-Time Correctness**: Using only data available at prediction time
- **Concept Drift**: Change in data distribution over time affecting model performance
