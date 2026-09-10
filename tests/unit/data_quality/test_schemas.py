"""Unit tests for Pandera schemas."""

import pytest
from datetime import datetime, timedelta
import pandas as pd

from src.data_quality.schemas import (
    DimCustomerSchema,
    DimAccountSchema,
    DimProductSchema,
    FactTransactionSchema,
    FactLoanSchema,
)


class TestDimCustomerSchema:
    """Tests for DimCustomerSchema."""
    
    def test_valid_customer_data(self):
        """Test validation with valid customer data."""
        df = pd.DataFrame({
            "customer_id": ["C001", "C002", "C003"],
            "first_name": ["John", "Jane", "Bob"],
            "last_name": ["Doe", "Smith", "Johnson"],
            "birth_date": [datetime(1980, 1, 1), datetime(1990, 5, 15), datetime(1975, 10, 30)],
            "annual_income": [50000, 75000, 60000],
            "is_active": [True, True, False],
            "customer_since": [datetime(2020, 1, 1), datetime(2021, 3, 1), datetime(2019, 6, 15)]
        })
        
        result = DimCustomerSchema.validate_with_report(df, "dim_customer")
        
        assert result.is_valid is True
    
    def test_invalid_birth_date_future(self):
        """Test validation with future birth date."""
        df = pd.DataFrame({
            "customer_id": ["C001"],
            "first_name": ["John"],
            "last_name": ["Doe"],
            "birth_date": [datetime.utcnow() + timedelta(days=365)],
            "annual_income": [50000],
            "is_active": [True]
        })
        
        result = DimCustomerSchema.validate_with_report(df, "dim_customer")
        
        assert result.is_valid is False
        assert len(result.errors) > 0
    
    def test_negative_annual_income(self):
        """Test validation with negative annual income."""
        df = pd.DataFrame({
            "customer_id": ["C001"],
            "first_name": ["John"],
            "last_name": ["Doe"],
            "annual_income": [-50000],
            "is_active": [True]
        })
        
        result = DimCustomerSchema.validate_with_report(df, "dim_customer")
        
        assert result.is_valid is False
    
    def test_duplicate_customer_id(self):
        """Test validation with duplicate customer IDs."""
        df = pd.DataFrame({
            "customer_id": ["C001", "C001"],
            "first_name": ["John", "Jane"],
            "last_name": ["Doe", "Smith"],
            "is_active": [True, True]
        })
        
        result = DimCustomerSchema.validate_with_report(df, "dim_customer")
        
        assert result.is_valid is False


class TestDimAccountSchema:
    """Tests for DimAccountSchema."""
    
    def test_valid_account_data(self):
        """Test validation with valid account data."""
        df = pd.DataFrame({
            "account_id": ["A001", "A002"],
            "customer_key": [1, 2],
            "customer_id": ["C001", "C002"],
            "product_key": [10, 20],
            "credit_limit": [10000, 5000],
            "overdraft_limit": [1000, 500],
            "is_active": [True, True],
            "opened_date": [datetime(2020, 1, 1), datetime(2021, 1, 1)]
        })
        
        result = DimAccountSchema.validate_with_report(df, "dim_account")
        
        assert result.is_valid is True
    
    def test_negative_credit_limit(self):
        """Test validation with negative credit limit."""
        df = pd.DataFrame({
            "account_id": ["A001"],
            "customer_key": [1],
            "customer_id": ["C001"],
            "product_key": [10],
            "credit_limit": [-10000],
            "is_active": [True]
        })
        
        result = DimAccountSchema.validate_with_report(df, "dim_account")
        
        assert result.is_valid is False


class TestDimProductSchema:
    """Tests for DimProductSchema."""
    
    def test_valid_product_data(self):
        """Test validation with valid product data."""
        df = pd.DataFrame({
            "product_id": ["P001", "P002"],
            "product_category": ["deposits", "loans"],
            "product_type": ["savings", "mortgage"],
            "product_name": ["Basic Savings", "Home Loan"],
            "interest_rate": [0.02, 0.045],
            "annual_fee": [0, 100],
            "minimum_balance": [100, 0],
            "term_months": [0, 360],
            "is_active": [True, True]
        })
        
        result = DimProductSchema.validate_with_report(df, "dim_product")
        
        assert result.is_valid is True
    
    def test_negative_interest_rate(self):
        """Test validation with negative interest rate."""
        df = pd.DataFrame({
            "product_id": ["P001"],
            "product_category": ["deposits"],
            "product_type": ["savings"],
            "product_name": ["Basic Savings"],
            "interest_rate": [-0.02],
            "is_active": [True]
        })
        
        result = DimProductSchema.validate_with_report(df, "dim_product")
        
        assert result.is_valid is False


class TestFactTransactionSchema:
    """Tests for FactTransactionSchema."""
    
    def test_valid_transaction_data(self):
        """Test validation with valid transaction data."""
        df = pd.DataFrame({
            "transaction_id": ["T001", "T002"],
            "account_key": [1, 2],
            "customer_key": [10, 20],
            "product_key": [100, 200],
            "date_key": [20240101, 20240102],
            "amount": [100.50, -50.25],
            "transaction_date": [datetime(2024, 1, 1, 10, 30), datetime(2024, 1, 2, 14, 15)],
            "fraud_score": [0.1, 0.05]
        })
        
        result = FactTransactionSchema.validate_with_report(df, "fact_transaction")
        
        assert result.is_valid is True
    
    def test_zero_transaction_amount(self):
        """Test validation with zero transaction amount."""
        df = pd.DataFrame({
            "transaction_id": ["T001"],
            "account_key": [1],
            "customer_key": [10],
            "product_key": [100],
            "date_key": [20240101],
            "amount": [0],
            "transaction_date": [datetime(2024, 1, 1)]
        })
        
        result = FactTransactionSchema.validate_with_report(df, "fact_transaction")
        
        assert result.is_valid is False
    
    def test_invalid_fraud_score(self):
        """Test validation with invalid fraud score."""
        df = pd.DataFrame({
            "transaction_id": ["T001"],
            "account_key": [1],
            "customer_key": [10],
            "product_key": [100],
            "date_key": [20240101],
            "amount": [100.50],
            "transaction_date": [datetime(2024, 1, 1)],
            "fraud_score": [1.5]
        })
        
        result = FactTransactionSchema.validate_with_report(df, "fact_transaction")
        
        assert result.is_valid is False


class TestFactLoanSchema:
    """Tests for FactLoanSchema."""
    
    def test_valid_loan_data(self):
        """Test validation with valid loan data."""
        df = pd.DataFrame({
            "loan_id": ["L001", "L002"],
            "customer_key": [1, 2],
            "product_key": [10, 20],
            "origination_date_key": [20240101, 20240201],
            "maturity_date_key": [20250101, 20250201],
            "principal_amount": [100000, 50000],
            "interest_rate": [0.045, 0.05],
            "term_months": [360, 180],
            "credit_score_at_origination": [720, 680],
            "days_past_due": [0, 15],
            "origination_date": [datetime(2024, 1, 1), datetime(2024, 2, 1)],
            "maturity_date": [datetime(2025, 1, 1), datetime(2025, 8, 1)]
        })
        
        result = FactLoanSchema.validate_with_report(df, "fact_loan")
        
        assert result.is_valid is True
    
    def test_negative_principal_amount(self):
        """Test validation with negative principal amount."""
        df = pd.DataFrame({
            "loan_id": ["L001"],
            "customer_key": [1],
            "product_key": [10],
            "origination_date_key": [20240101],
            "maturity_date_key": [20250101],
            "principal_amount": [-100000],
            "interest_rate": [0.045],
            "term_months": [360],
            "origination_date": [datetime(2024, 1, 1)],
            "maturity_date": [datetime(2025, 1, 1)]
        })
        
        result = FactLoanSchema.validate_with_report(df, "fact_loan")
        
        assert result.is_valid is False
    
    def test_invalid_credit_score(self):
        """Test validation with invalid credit score."""
        df = pd.DataFrame({
            "loan_id": ["L001"],
            "customer_key": [1],
            "product_key": [10],
            "origination_date_key": [20240101],
            "maturity_date_key": [20250101],
            "principal_amount": [100000],
            "interest_rate": [0.045],
            "term_months": [360],
            "credit_score_at_origination": [200],
            "origination_date": [datetime(2024, 1, 1)],
            "maturity_date": [datetime(2025, 1, 1)]
        })
        
        result = FactLoanSchema.validate_with_report(df, "fact_loan")
        
        assert result.is_valid is False
