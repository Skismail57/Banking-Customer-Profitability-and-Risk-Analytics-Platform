"""Pytest configuration and fixtures."""

import pytest
import pandas as pd
import numpy as np
from datetime import date, datetime
from typing import Dict, Any


@pytest.fixture
def sample_customer_data() -> pd.DataFrame:
    """Sample customer data for testing."""
    return pd.DataFrame({
        "customer_key": ["CUST_001", "CUST_002", "CUST_003", "CUST_004", "CUST_005"],
        "customer_id": ["1001", "1002", "1003", "1004", "1005"],
        "customer_name": ["John Doe", "Jane Smith", "Bob Johnson", "Alice Brown", "Charlie Davis"],
        "segment": ["premium", "standard", "premium", "standard", "basic"],
        "region": ["North", "South", "East", "West", "North"],
        "acquisition_date": pd.to_datetime(["2020-01-15", "2019-06-20", "2021-03-10", "2018-11-05", "2022-01-01"]),
        "customer_age": [45, 35, 50, 28, 40],
        "income_level": ["High", "Medium", "High", "Low", "Medium"],
    })


@pytest.fixture
def sample_customer_metrics() -> pd.DataFrame:
    """Sample customer metrics data for testing."""
    return pd.DataFrame({
        "customer_key": ["CUST_001", "CUST_002", "CUST_003", "CUST_004", "CUST_005"],
        "segment": ["premium", "standard", "premium", "standard", "basic"],
        "as_of_date": [date(2026, 9, 1)] * 5,
        "net_profit": [15000.0, 3000.0, 20000.0, 500.0, 1000.0],
        "revenue": [20000.0, 5000.0, 25000.0, 1000.0, 2000.0],
        "cost": [5000.0, 2000.0, 5000.0, 500.0, 1000.0],
        "clv": [50000.0, 15000.0, 60000.0, 8000.0, 12000.0],
        "risk_level": ["low", "medium", "low", "high", "medium"],
        "risk_trend": ["stable", "increasing", "stable", "increasing", "stable"],
        "churn_probability": [0.12, 0.25, 0.10, 0.75, 0.20],
        "exposure_amount": [75000.0, 30000.0, 100000.0, 15000.0, 25000.0],
        "credit_utilization": [0.35, 0.65, 0.25, 0.90, 0.45],
        "days_past_due": [0, 15, 0, 45, 0],
        "credit_score": [750, 680, 780, 620, 700],
        "balance_to_income_ratio": [0.25, 0.45, 0.20, 0.65, 0.35],
    })


@pytest.fixture
def sample_transactions() -> pd.DataFrame:
    """Sample transaction data for testing."""
    return pd.DataFrame({
        "transaction_key": [f"TXN_{i:03d}" for i in range(1, 21)],
        "customer_key": ["CUST_001"] * 5 + ["CUST_002"] * 5 + ["CUST_003"] * 5 + ["CUST_004"] * 5,
        "transaction_date": pd.date_range(start="2026-08-01", periods=20, freq="3D"),
        "amount": [100.0, 200.0, 150.0, 300.0, 250.0] * 4,
        "product_type": ["Credit Card"] * 10 + ["Loan"] * 10,
        "transaction_type": ["purchase"] * 15 + ["payment"] * 5,
        "channel": ["online"] * 15 + ["branch"] * 5,
    })


@pytest.fixture
def sample_recommendations() -> pd.DataFrame:
    """Sample recommendation data for testing."""
    return pd.DataFrame({
        "recommendation_key": [f"REC_{i:03d}" for i in range(1, 6)],
        "customer_key": ["CUST_001", "CUST_002", "CUST_003", "CUST_004", "CUST_005"],
        "segment": ["premium", "standard", "premium", "standard", "basic"],
        "priority": ["high", "medium", "high", "critical", "low"],
        "confidence": ["high", "medium", "high", "medium", "high"],
        "recommended_action": [
            "Offer premium product",
            "Review relationship",
            "Cross-sell opportunity",
            "Risk monitoring",
            "Monitor churn"
        ],
        "reason": [
            "High profitability, low risk",
            "Rising risk trend",
            "Low utilization",
            "High risk, high exposure",
            "Moderate churn risk"
        ],
        "generated_at": pd.date_range(start="2026-09-01", periods=5, freq="D"),
    })


@pytest.fixture
def sample_model_performance() -> pd.DataFrame:
    """Sample model performance data for testing."""
    return pd.DataFrame({
        "model_key": ["MODEL_001", "MODEL_002", "MODEL_003"],
        "model_name": ["Churn Model", "Default Risk Model", "Profitability Model"],
        "model_type": ["classification", "classification", "regression"],
        "evaluated_at": pd.date_range(start="2026-09-01", periods=3, freq="D"),
        "accuracy": [0.87, 0.85, 0.82],
        "precision": [0.85, 0.83, 0.80],
        "recall": [0.82, 0.80, 0.78],
        "f1_score": [0.83, 0.81, 0.79],
        "roc_auc": [0.92, 0.88, 0.85],
    })


@pytest.fixture
def sample_null_data() -> pd.DataFrame:
    """Sample data with null values for testing null handling."""
    return pd.DataFrame({
        "customer_key": ["CUST_001", "CUST_002", "CUST_003", None, "CUST_005"],
        "net_profit": [15000.0, None, 20000.0, 500.0, None],
        "risk_level": ["low", None, "low", "high", "medium"],
        "churn_probability": [0.12, 0.25, None, 0.45, 0.20],
    })


@pytest.fixture
def sample_duplicate_data() -> pd.DataFrame:
    """Sample data with duplicates for testing duplicate handling."""
    return pd.DataFrame({
        "customer_key": ["CUST_001", "CUST_001", "CUST_002", "CUST_002", "CUST_003"],
        "as_of_date": [date(2026, 9, 1)] * 5,
        "net_profit": [15000.0, 15000.0, 3000.0, 3000.0, 20000.0],
        "risk_level": ["low", "low", "medium", "medium", "low"],
    })


@pytest.fixture
def sample_edge_case_data() -> pd.DataFrame:
    """Sample data with edge cases for testing."""
    return pd.DataFrame({
        "customer_key": ["CUST_001", "CUST_002", "CUST_003", "CUST_004", "CUST_005"],
        "net_profit": [0.0, -1000.0, 1000000.0, 0.01, -0.01],
        "risk_level": ["low", "critical", "high", "medium", "low"],
        "churn_probability": [0.0, 1.0, 0.5, 0.99, 0.01],
        "exposure_amount": [0.0, 1000000.0, 50000.0, 1.0, -1.0],
        "credit_utilization": [0.0, 1.0, 0.5, 1.5, -0.1],
    })


@pytest.fixture
def sample_large_dataset() -> pd.DataFrame:
    """Sample large dataset for performance testing."""
    np.random.seed(42)
    n = 1000
    return pd.DataFrame({
        "customer_key": [f"CUST_{i:04d}" for i in range(n)],
        "net_profit": np.random.normal(5000, 2000, n),
        "risk_level": np.random.choice(["low", "medium", "high", "critical"], n, p=[0.6, 0.25, 0.1, 0.05]),
        "churn_probability": np.random.beta(2, 5, n),
        "exposure_amount": np.random.lognormal(10, 1, n),
    })
