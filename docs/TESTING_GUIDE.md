# Testing Guide

## Overview

This guide provides comprehensive documentation for the testing implementation of the Banking Customer Profitability and Risk Analytics Platform. The test suite includes unit tests, integration tests, data quality tests, SQL tests, analytics tests, ML tests, API tests, and regression tests.

---

## Test Structure

```
tests/
├── conftest.py                    # Pytest configuration and fixtures
├── __init__.py
├── unit/                          # Unit tests
│   ├── decision_intelligence/      # Decision intelligence unit tests
│   ├── advanced_risk_analytics/   # Advanced risk analytics unit tests
│   ├── churn_analytics/           # Churn analytics unit tests
│   ├── clv_analytics/             # CLV analytics unit tests
│   ├── credit_risk_analytics/     # Credit risk analytics unit tests
│   ├── customer_intelligence/     # Customer intelligence unit tests
│   ├── customer_segmentation/     # Customer segmentation unit tests
│   ├── data_quality/              # Data quality unit tests
│   ├── decision_intelligence/     # Decision intelligence unit tests
│   ├── ingestion/                 # Data ingestion unit tests
│   ├── predictive_analytics/      # Predictive analytics unit tests
│   ├── profitability_analytics/   # Profitability analytics unit tests
│   ├── statistical_analytics/     # Statistical analytics unit tests
│   └── transaction_analytics/     # Transaction analytics unit tests
├── integration/                   # Integration tests
│   └── test_analytics_orchestrator.py
├── data_quality/                  # Data quality tests
│   ├── test_null_handling.py
│   ├── test_duplicate_handling.py
│   └── test_edge_cases.py
├── sql/                           # SQL tests
│   └── test_view_syntax.py
├── analytics/                     # Analytics tests
│   ├── test_profitability_calculations.py
│   ├── test_risk_calculations.py
│   └── test_churn_features.py
├── ml/                            # ML tests
│   └── test_model_pipeline.py
├── api/                           # API tests
│   └── test_api_endpoints.py
└── regression/                    # Regression tests
    └── test_critical_metrics.py
```

---

## Test Configuration

### pytest.ini

The pytest configuration file includes:

- Test discovery patterns
- Test paths
- Output options (verbose, strict markers, short traceback)
- Coverage configuration (commented out due to missing pytest-cov)
- Markers for different test types

### Markers

- `unit`: Unit tests
- `integration`: Integration tests
- `data_quality`: Data quality tests
- `sql`: SQL tests
- `analytics`: Analytics tests
- `ml`: Machine learning tests
- `api`: API tests
- `regression`: Regression tests
- `slow`: Slow running tests

---

## Test Fixtures

### Sample Data Fixtures

Located in `tests/conftest.py`:

- `sample_customer_data`: Sample customer information
- `sample_customer_metrics`: Sample customer metrics with profitability, risk, churn data
- `sample_transactions`: Sample transaction data
- `sample_recommendations`: Sample recommendation data
- `sample_model_performance`: Sample model performance data
- `sample_null_data`: Data with null values for testing null handling
- `sample_duplicate_data`: Data with duplicates for testing duplicate handling
- `sample_edge_case_data`: Data with edge cases (zero, negative, extreme values)
- `sample_large_dataset`: Large dataset for performance testing

---

## Test Categories

### 1. Unit Tests

**Location**: `tests/unit/`

**Purpose**: Test individual components in isolation.

**Examples**:
- Decision intelligence base classes (Priority, ConfidenceLevel, Recommendation)
- Decision intelligence rules engine
- Advanced risk analytics components
- Churn analytics components
- CLV analytics components
- Credit risk analytics components
- Customer intelligence components
- Customer segmentation components
- Data quality schemas
- Predictive analytics components
- Profitability analytics components
- Statistical analytics components
- Transaction analytics components

**Running**:
```bash
pytest tests/unit/ -v
```

---

### 2. Integration Tests

**Location**: `tests/integration/`

**Purpose**: Test integration between multiple components.

**Tests**:
- Advanced risk orchestrator initialization
- Advanced risk orchestrator report generation
- Decision intelligence orchestrator initialization
- Decision intelligence customer recommendations
- Decision intelligence segment recommendations

**Running**:
```bash
pytest tests/integration/ -v
```

---

### 3. Data Quality Tests

**Location**: `tests/data_quality/`

**Purpose**: Test data quality handling (nulls, duplicates, edge cases).

**Tests**:
- **Null Handling**:
  - Null customer key handling
  - Null profitability handling
  - Null risk level handling
  - Null churn probability handling
  - All null row handling

- **Duplicate Handling**:
  - Duplicate detection
  - Duplicate removal
  - Duplicate removal by subset
  - Duplicate keep first
  - Duplicate keep last

- **Edge Cases**:
  - Zero profitability
  - Negative profitability
  - Extreme profitability
  - Churn probability bounds (0-1)
  - Zero churn probability
  - Max churn probability
  - Zero exposure
  - Negative exposure
  - Utilization bounds (0-1)
  - Invalid utilization handling

**Running**:
```bash
pytest tests/data_quality/ -v
```

---

### 4. SQL Tests

**Location**: `tests/sql/`

**Purpose**: Test SQL view syntax and structure.

**Tests**:
- Executive overview view exists
- Customer 360 view exists
- Profitability view exists
- Risk view exists
- Segment view exists
- Churn view exists
- Product view exists
- Transaction view exists
- Decision intelligence view exists
- Model monitoring view exists
- View has CREATE OR REPLACE VIEW statement
- View has SELECT statement

**Running**:
```bash
pytest tests/sql/ -v
```

---

### 5. Analytics Tests

**Location**: `tests/analytics/`

**Purpose**: Test analytical calculations.

**Tests**:
- **Profitability Calculations**:
  - Net profit calculation (revenue - cost)
  - Profit margin calculation
  - Total profit aggregation
  - Average profit calculation
  - Profit by segment aggregation
  - Profit variance calculation
  - Profit distribution

- **Risk Calculations**:
  - Risk level distribution
  - High risk customer count
  - Exposure aggregation
  - Exposure by risk level
  - Utilization calculation
  - High utilization threshold (>0.85)
  - DPD calculation
  - DPD 30+ count
  - Credit score range (300-850)
  - Risk score mapping

- **Churn Features**:
  - Churn probability bounds (0-1)
  - High churn threshold (>0.7)
  - Churn by segment
  - Churn vs risk correlation
  - Churn vs CLV correlation
  - Retention rate calculation
  - High churn + high CLV count
  - Churn distribution

**Running**:
```bash
pytest tests/analytics/ -v
```

---

### 6. ML Tests

**Location**: `tests/ml/`

**Purpose**: Test machine learning model pipeline.

**Tests**:
- Model initialization
- Model training
- Model prediction
- Model probability prediction
- Model accuracy calculation
- Model precision calculation
- Model recall calculation
- Feature importance extraction
- Model with null features

**Running**:
```bash
pytest tests/ml/ -v
```

---

### 7. API Tests

**Location**: `tests/api/`

**Purpose**: Test FastAPI API endpoints.

**Tests**:
- Root endpoint
- Health check endpoint
- Customers endpoint
- Customers with pagination
- Profitability aggregate endpoint
- Risk aggregate endpoint
- Segments endpoint
- Churn aggregate endpoint
- Portfolio summary endpoint

**Running**:
```bash
pytest tests/api/ -v
```

---

### 8. Regression Tests

**Location**: `tests/regression/`

**Purpose**: Ensure critical metrics remain stable over time.

**Tests**:
- Total profit calculation regression
- Risk level distribution regression
- Churn probability average regression
- Exposure aggregation regression
- Segment profitability regression

**Running**:
```bash
pytest tests/regression/ -v
```

---

## Running Tests

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test Category

```bash
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/data_quality/ -v
pytest tests/sql/ -v
pytest tests/analytics/ -v
pytest tests/ml/ -v
pytest tests/api/ -v
pytest tests/regression/ -v
```

### Run with Markers

```bash
pytest -m unit -v
pytest -m integration -v
pytest -m data_quality -v
pytest -m analytics -v
pytest -m ml -v
pytest -m api -v
pytest -m regression -v
```

### Run Specific Test File

```bash
pytest tests/data_quality/test_null_handling.py -v
```

### Run Specific Test Class

```bash
pytest tests/analytics/test_profitability_calculations.py::TestProfitabilityCalculations -v
```

### Run Specific Test Method

```bash
pytest tests/analytics/test_profitability_calculations.py::TestProfitabilityCalculations::test_net_profit_calculation -v
```

---

## Test Coverage

### Coverage Configuration

Coverage is configured in `pytest.ini` but currently commented out due to missing `pytest-cov` dependency.

To enable coverage:

1. Install pytest-cov:
```bash
pip install pytest-cov
```

2. Uncomment coverage options in `pytest.ini`:
```ini
addopts =
    -v
    --strict-markers
    --tb=short
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
```

3. Run tests with coverage:
```bash
pytest --cov=src --cov-report=html --cov-report=term-missing
```

4. View coverage report:
```bash
# HTML report
open htmlcov/index.html

# Terminal report
pytest --cov=src --cov-report=term-missing
```

---

## Test Results Summary

### New Tests Created

- **Unit Tests**: 12 tests (decision intelligence)
- **Integration Tests**: 5 tests
- **Data Quality Tests**: 20 tests
- **SQL Tests**: 12 tests
- **Analytics Tests**: 25 tests
- **ML Tests**: 9 tests
- **API Tests**: 10 tests
- **Regression Tests**: 5 tests

**Total New Tests**: 98 tests

### Test Status

All newly created tests are passing:
- ✅ Unit tests (decision intelligence): 12 passed
- ✅ Integration tests: 5 passed
- ✅ Data quality tests: 20 passed
- ✅ SQL tests: 12 passed
- ✅ Analytics tests: 25 passed
- ✅ ML tests: 9 passed
- ✅ API tests: 10 passed
- ✅ Regression tests: 5 passed

### Pre-existing Test Issues

Some pre-existing unit tests have import errors due to:
- Pandera version compatibility issues
- API module structure issues

These are outside the scope of this testing implementation task.

---

## Best Practices

### Writing Tests

1. **Use descriptive test names**: Test names should clearly describe what is being tested.
2. **Follow AAA pattern**: Arrange, Act, Assert.
3. **Use fixtures**: Reuse fixtures for common test data.
4. **Test edge cases**: Include tests for null values, duplicates, and edge cases.
5. **Test calculations**: Verify analytical calculations are correct.
6. **Test error handling**: Ensure errors are handled gracefully.
7. **Keep tests independent**: Tests should not depend on each other.
8. **Use markers**: Mark tests with appropriate markers for categorization.

### Test Data

1. **Use realistic data**: Sample data should reflect real-world scenarios.
2. **Include edge cases**: Test with zero, negative, and extreme values.
3. **Include null values**: Test null handling explicitly.
4. **Include duplicates**: Test duplicate handling.
5. **Use consistent data**: Use fixtures to ensure consistency across tests.

### Maintenance

1. **Update regression tests**: When expected values change, update regression tests.
2. **Add new tests**: When adding new features, add corresponding tests.
3. **Fix failing tests**: Address test failures promptly.
4. **Review coverage**: Monitor test coverage and add tests for uncovered code.
5. **Document tests**: Add docstrings to explain complex test logic.

---

## Troubleshooting

### Common Issues

**Import Errors**:
- Ensure all dependencies are installed
- Check Python path configuration
- Verify module structure

**Fixture Not Found**:
- Ensure fixtures are defined in `conftest.py`
- Check fixture names match usage
- Verify fixture scope

**Test Data Issues**:
- Verify fixture data is correct
- Check data types match expectations
- Ensure data is not modified in tests

**Assertion Errors**:
- Review expected vs actual values
- Check calculation logic
- Verify test assumptions

---

## Continuous Integration

### CI Configuration

To integrate tests with CI:

```yaml
# Example GitHub Actions workflow
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: pytest tests/ -v --cov=html
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

---

## Summary

The comprehensive testing implementation includes:

- **98 new tests** across 8 test categories
- **Test fixtures** for sample data and edge cases
- **Pytest configuration** with markers and coverage setup
- **Test documentation** for running and maintaining tests
- **All new tests passing** with proper error handling

The test suite covers:
- Unit tests for individual components
- Integration tests for component interactions
- Data quality tests for null/duplicate/edge case handling
- SQL tests for view validation
- Analytics tests for calculation verification
- ML tests for model pipeline validation
- API tests for endpoint functionality
- Regression tests for metric stability
