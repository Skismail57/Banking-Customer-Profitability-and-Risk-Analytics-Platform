"""Unit tests for Customer 360 feature extraction."""

import pytest
from datetime import date, datetime
import pandas as pd
import numpy as np

from src.customer_intelligence.features import (
    DemographicFeatures,
    AccountFeatures,
    TransactionFeatures,
    LoanFeatures,
    InteractionFeatures,
)


class TestDemographicFeatures:
    """Tests for DemographicFeatures."""
    
    def test_extract_demographic_features(self):
        """Test demographic feature extraction."""
        customers_df = pd.DataFrame({
            "customer_key": [1, 2, 3],
            "customer_id": ["C001", "C002", "C003"],
            "birth_date": [datetime(1980, 1, 1), datetime(1990, 5, 15), datetime(1975, 10, 30)],
            "gender": ["M", "F", "M"],
            "annual_income": [50000, 75000, 60000],
            "customer_since": [datetime(2020, 1, 1), datetime(2021, 3, 1), datetime(2019, 6, 15)],
            "is_active": [True, True, False]
        })
        
        extractor = DemographicFeatures(as_of_date=date(2024, 1, 15))
        features_df = extractor.extract(customers_df)
        
        assert "age" in features_df.columns
        assert "age_group" in features_df.columns
        assert "tenure_years" in features_df.columns
        assert "tenure_group" in features_df.columns
        assert len(features_df) == 3
    
    def test_calculate_age(self):
        """Test age calculation."""
        extractor = DemographicFeatures(as_of_date=date(2024, 1, 15))
        
        birth_dates = pd.Series([datetime(1980, 1, 1), datetime(1990, 5, 15)])
        ages = extractor._calculate_age(birth_dates)
        
        assert ages.iloc[0] == pytest.approx(44.0, rel=0.1)
        assert ages.iloc[1] == pytest.approx(33.7, rel=0.1)
    
    def test_calculate_age_group(self):
        """Test age group calculation."""
        extractor = DemographicFeatures()
        
        ages = pd.Series([20, 30, 40, 60, 70])
        age_groups = extractor._calculate_age_group(ages)
        
        assert age_groups.iloc[0] == "18-25"
        assert age_groups.iloc[1] == "26-35"
        assert age_groups.iloc[2] == "36-45"
        assert age_groups.iloc[3] == "56-65"
        assert age_groups.iloc[4] == "65+"


class TestAccountFeatures:
    """Tests for AccountFeatures."""
    
    def test_extract_account_features(self):
        """Test account feature extraction."""
        accounts_df = pd.DataFrame({
            "account_id": ["A001", "A002", "A003"],
            "customer_key": [1, 1, 2],
            "product_key": [10, 20, 10],
            "product_type": ["savings", "checking", "savings"],
            "product_category": ["deposits", "deposits", "deposits"],
            "is_active": [True, True, False],
            "credit_limit": [10000, 5000, 0]
        })
        
        customers_df = pd.DataFrame({
            "customer_key": [1, 2],
            "customer_id": ["C001", "C002"]
        })
        
        extractor = AccountFeatures()
        features_df = extractor.extract(accounts_df, customers_df)
        
        assert "account_count" in features_df.columns
        assert "active_account_count" in features_df.columns
        assert features_df[features_df["customer_key"] == 1]["account_count"].iloc[0] == 2
        assert features_df[features_df["customer_key"] == 2]["account_count"].iloc[0] == 1


class TestTransactionFeatures:
    """Tests for TransactionFeatures."""
    
    def test_extract_transaction_features(self):
        """Test transaction feature extraction."""
        transactions_df = pd.DataFrame({
            "transaction_id": ["T001", "T002", "T003", "T004"],
            "customer_key": [1, 1, 2, 1],
            "amount": [100.50, 200.75, 150.00, 50.25],
            "transaction_date": pd.to_datetime([
                "2024-01-10",
                "2024-01-12",
                "2024-01-05",
                "2024-01-14"
            ])
        })
        
        customers_df = pd.DataFrame({
            "customer_key": [1, 2],
            "customer_id": ["C001", "C002"]
        })
        
        extractor = TransactionFeatures(as_of_date=date(2024, 1, 15))
        features_df = extractor.extract(transactions_df, customers_df, window_days=90)
        
        assert "transaction_count" in features_df.columns
        assert "transaction_volume" in features_df.columns
        assert "days_since_last_transaction" in features_df.columns
        assert features_df[features_df["customer_key"] == 1]["transaction_count"].iloc[0] == 3


class TestLoanFeatures:
    """Tests for LoanFeatures."""
    
    def test_extract_loan_features(self):
        """Test loan feature extraction."""
        loans_df = pd.DataFrame({
            "loan_id": ["L001", "L002"],
            "customer_key": [1, 2],
            "current_balance": [50000, 30000],
            "days_past_due": [0, 15],
            "origination_date": pd.to_datetime(["2023-01-01", "2023-06-01"])
        })
        
        accounts_df = pd.DataFrame({
            "customer_key": [1, 2],
            "credit_limit": [100000, 50000]
        })
        
        customers_df = pd.DataFrame({
            "customer_key": [1, 2],
            "customer_id": ["C001", "C002"]
        })
        
        extractor = LoanFeatures()
        features_df = extractor.extract(loans_df, accounts_df, customers_df)
        
        assert "loan_count" in features_df.columns
        assert "total_loan_exposure" in features_df.columns
        assert "credit_utilization" in features_df.columns
        assert "has_delinquent_loans" in features_df.columns


class TestInteractionFeatures:
    """Tests for InteractionFeatures."""
    
    def test_extract_interaction_features(self):
        """Test interaction feature extraction."""
        interactions_df = pd.DataFrame({
            "interaction_id": ["I001", "I002", "I003"],
            "customer_key": [1, 1, 2],
            "satisfaction_score": [5, 4, 3],
            "interaction_category": ["inquiry", "complaint", "inquiry"],
            "interaction_date": pd.to_datetime([
                "2024-01-10",
                "2024-01-12",
                "2024-01-05"
            ])
        })
        
        customers_df = pd.DataFrame({
            "customer_key": [1, 2],
            "customer_id": ["C001", "C002"]
        })
        
        extractor = InteractionFeatures(as_of_date=date(2024, 1, 15))
        features_df = extractor.extract(interactions_df, customers_df, window_days=90)
        
        assert "interaction_count" in features_df.columns
        assert "avg_satisfaction_score" in features_df.columns
        assert "complaint_count" in features_df.columns
        assert "has_complaints" in features_df.columns
        assert features_df[features_df["customer_key"] == 1]["complaint_count"].iloc[0] == 1
