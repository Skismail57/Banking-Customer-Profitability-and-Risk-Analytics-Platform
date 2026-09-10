"""Customer 360 feature extraction modules."""

from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional, List
import logging

import pandas as pd
import numpy as np

from src.customer_intelligence.base import (
    Customer360Base,
    FeatureDefinition,
    FeatureCategory,
    TemporalWindow,
)

logger = logging.getLogger(__name__)


class DemographicFeatures(Customer360Base):
    """Extract demographic features from customer dimension."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize demographic features.
        
        Args:
            as_of_date: As-of date for temporal features
        """
        super().__init__(as_of_date)
        
        # Register feature definitions
        self._register_features()
    
    def _register_features(self) -> None:
        """Register demographic feature definitions."""
        features = [
            FeatureDefinition(
                name="age",
                category=FeatureCategory.DEMOGRAPHIC,
                description="Customer age in years as of as_of_date",
                data_type="numeric",
                is_temporal=True,
                business_definition="Age calculated from birth_date relative to as_of_date"
            ),
            FeatureDefinition(
                name="age_group",
                category=FeatureCategory.DEMOGRAPHIC,
                description="Customer age group (18-25, 26-35, 36-45, 46-55, 56-65, 65+)",
                data_type="categorical",
                is_temporal=True,
                business_definition="Categorical age grouping for segmentation"
            ),
            FeatureDefinition(
                name="gender",
                category=FeatureCategory.DEMOGRAPHIC,
                description="Customer gender",
                data_type="categorical",
                business_definition="Gender as recorded in customer profile"
            ),
            FeatureDefinition(
                name="marital_status",
                category=FeatureCategory.DEMOGRAPHIC,
                description="Customer marital status",
                data_type="categorical",
                business_definition="Marital status (single, married, divorced, widowed, etc.)"
            ),
            FeatureDefinition(
                name="education_level",
                category=FeatureCategory.DEMOGRAPHIC,
                description="Highest education level achieved",
                data_type="categorical",
                business_definition="Education level (high school, bachelor, master, phd, etc.)"
            ),
            FeatureDefinition(
                name="occupation",
                category=FeatureCategory.DEMOGRAPHIC,
                description="Customer occupation",
                data_type="categorical",
                business_definition="Occupation or industry of employment"
            ),
            FeatureDefinition(
                name="annual_income",
                category=FeatureCategory.DEMOGRAPHIC,
                description="Annual household income",
                data_type="numeric",
                business_definition="Total annual income in local currency"
            ),
            FeatureDefinition(
                name="income_bracket",
                category=FeatureCategory.DEMOGRAPHIC,
                description="Income bracket category",
                data_type="categorical",
                business_definition="Categorical income grouping for segmentation"
            ),
            FeatureDefinition(
                name="tenure_years",
                category=FeatureCategory.DEMOGRAPHIC,
                description="Years as customer (tenure)",
                data_type="numeric",
                is_temporal=True,
                business_definition="Time since customer onboarding in years"
            ),
            FeatureDefinition(
                name="tenure_group",
                category=FeatureCategory.DEMOGRAPHIC,
                description="Customer tenure group",
                data_type="categorical",
                is_temporal=True,
                business_definition="Categorical tenure grouping (new, established, loyal)"
            ),
            FeatureDefinition(
                name="is_active",
                category=FeatureCategory.DEMOGRAPHIC,
                description="Customer active status",
                data_type="boolean",
                is_temporal=True,
                business_definition="Whether customer is currently active"
            ),
        ]
        
        for feature in features:
            self.register_feature(feature)
    
    def extract(self, customers_df: pd.DataFrame) -> pd.DataFrame:
        """Extract demographic features from customer data.
        
        Args:
            customers_df: DataFrame from dim_customer
        
        Returns:
            DataFrame with demographic features
        """
        logger.info(f"Extracting demographic features for {len(customers_df)} customers")
        
        features_df = customers_df.copy()
        
        # Calculate age
        if "birth_date" in features_df.columns:
            features_df["birth_date"] = pd.to_datetime(features_df["birth_date"])
            features_df["age"] = self._calculate_age(features_df["birth_date"])
            features_df["age_group"] = self._calculate_age_group(features_df["age"])
        
        # Calculate income bracket
        if "annual_income" in features_df.columns:
            features_df["income_bracket"] = self._calculate_income_bracket(features_df["annual_income"])
        
        # Calculate tenure
        if "customer_since" in features_df.columns:
            features_df["customer_since"] = pd.to_datetime(features_df["customer_since"])
            features_df["tenure_years"] = self._calculate_tenure(features_df["customer_since"])
            features_df["tenure_group"] = self._calculate_tenure_group(features_df["tenure_years"])
        
        # Select relevant columns
        feature_columns = [
            "customer_id", "customer_key",
            "age", "age_group", "gender", "marital_status",
            "education_level", "occupation", "annual_income", "income_bracket",
            "tenure_years", "tenure_group", "is_active"
        ]
        
        available_columns = [col for col in feature_columns if col in features_df.columns]
        
        return features_df[available_columns]
    
    def _calculate_age(self, birth_dates: pd.Series) -> pd.Series:
        """Calculate age from birth dates.
        
        Args:
            birth_dates: Series of birth dates
        
        Returns:
            Series of ages in years
        """
        as_of_timestamp = pd.Timestamp(self.as_of_date)
        ages = (as_of_timestamp - birth_dates).dt.days / 365.25
        return ages.round(1)
    
    def _calculate_age_group(self, ages: pd.Series) -> pd.Series:
        """Calculate age group from age.
        
        Args:
            ages: Series of ages
        
        Returns:
            Series of age groups
        """
        bins = [0, 18, 25, 35, 45, 55, 65, 120]
        labels = ["under_18", "18-25", "26-35", "36-45", "46-55", "56-65", "65+"]
        return pd.cut(ages, bins=bins, labels=labels, right=False).astype(str)
    
    def _calculate_income_bracket(self, incomes: pd.Series) -> pd.Series:
        """Calculate income bracket from annual income.
        
        Args:
            incomes: Series of annual incomes
        
        Returns:
            Series of income brackets
        """
        bins = [0, 25000, 50000, 75000, 100000, 150000, float("inf")]
        labels = ["under_25k", "25k-50k", "50k-75k", "75k-100k", "100k-150k", "150k+"]
        return pd.cut(incomes, bins=bins, labels=labels, right=False).astype(str)
    
    def _calculate_tenure(self, customer_since: pd.Series) -> pd.Series:
        """Calculate tenure in years.
        
        Args:
            customer_since: Series of customer since dates
        
        Returns:
            Series of tenure in years
        """
        as_of_timestamp = pd.Timestamp(self.as_of_date)
        tenures = (as_of_timestamp - customer_since).dt.days / 365.25
        return tenures.round(1)
    
    def _calculate_tenure_group(self, tenures: pd.Series) -> pd.Series:
        """Calculate tenure group from tenure.
        
        Args:
            tenures: Series of tenures in years
        
        Returns:
            Series of tenure groups
        """
        bins = [0, 1, 3, 5, float("inf")]
        labels = ["new", "established", "loyal", "veteran"]
        return pd.cut(tenures, bins=bins, labels=labels, right=False).astype(str)


class AccountFeatures(Customer360Base):
    """Extract account-level features."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize account features.
        
        Args:
            as_of_date: As-of date for temporal features
        """
        super().__init__(as_of_date)
        self._register_features()
    
    def _register_features(self) -> None:
        """Register account feature definitions."""
        features = [
            FeatureDefinition(
                name="account_count",
                category=FeatureCategory.ACCOUNT,
                description="Total number of accounts owned by customer",
                data_type="numeric",
                is_temporal=True,
                business_definition="Count of active and inactive accounts"
            ),
            FeatureDefinition(
                name="active_account_count",
                category=FeatureCategory.ACCOUNT,
                description="Number of currently active accounts",
                data_type="numeric",
                is_temporal=True,
                business_definition="Count of accounts with is_active=true"
            ),
            FeatureDefinition(
                name="total_balance",
                category=FeatureCategory.ACCOUNT,
                description="Total balance across all accounts",
                data_type="numeric",
                is_temporal=True,
                business_definition="Sum of balances from all accounts"
            ),
            FeatureDefinition(
                name="average_balance",
                category=FeatureCategory.ACCOUNT,
                description="Average balance across accounts",
                data_type="numeric",
                is_temporal=True,
                business_definition="Mean balance across all accounts"
            ),
            FeatureDefinition(
                name="total_credit_limit",
                category=FeatureCategory.ACCOUNT,
                description="Total credit limit across all credit accounts",
                data_type="numeric",
                is_temporal=True,
                business_definition="Sum of credit limits for credit products"
            ),
            FeatureDefinition(
                name="product_diversity",
                category=FeatureCategory.ACCOUNT,
                description="Number of different product types owned",
                data_type="numeric",
                is_temporal=True,
                business_definition="Count of unique product categories"
            ),
            FeatureDefinition(
                name="products_owned",
                category=FeatureCategory.ACCOUNT,
                description="List of product types owned",
                data_type="categorical",
                is_temporal=True,
                business_definition="Comma-separated list of product categories"
            ),
        ]
        
        for feature in features:
            self.register_feature(feature)
    
    def extract(self, accounts_df: pd.DataFrame, customers_df: pd.DataFrame) -> pd.DataFrame:
        """Extract account-level features aggregated to customer level.
        
        Args:
            accounts_df: DataFrame from dim_account
            customers_df: DataFrame from dim_customer
        
        Returns:
            DataFrame with account features per customer
        """
        logger.info(f"Extracting account features for {len(customers_df)} customers")
        
        # Merge accounts with customers
        merged_df = accounts_df.merge(
            customers_df[["customer_key", "customer_id"]],
            on="customer_key",
            how="left"
        )
        
        # Apply temporal safety
        if "opened_date" in merged_df.columns:
            merged_df = self.ensure_temporal_safety(merged_df, "opened_date")
        
        # Aggregate to customer level
        features_df = merged_df.groupby("customer_key").agg({
            "account_id": "count",
            "is_active": "sum",
            "product_key": "nunique",
            "product_type": lambda x: ",".join(x.unique()) if len(x.unique()) > 0 else ""
        }).reset_index()
        
        features_df.columns = [
            "customer_key",
            "account_count",
            "active_account_count",
            "unique_products",
            "products_owned"
        ]
        
        # Calculate product diversity (unique product categories)
        if "product_category" in merged_df.columns:
            product_diversity = merged_df.groupby("customer_key")["product_category"].nunique()
            features_df = features_df.merge(
                product_diversity.rename("product_diversity"),
                on="customer_key",
                how="left"
            )
        
        # Merge back customer_id
        features_df = features_df.merge(
            customers_df[["customer_key", "customer_id"]],
            on="customer_key",
            how="left"
        )
        
        # Fill NaN values
        features_df = features_df.fillna({
            "active_account_count": 0,
            "product_diversity": 0,
            "products_owned": ""
        })
        
        return features_df


class TransactionFeatures(Customer360Base):
    """Extract transaction-level features."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize transaction features.
        
        Args:
            as_of_date: As-of date for temporal features
        """
        super().__init__(as_of_date)
        self._register_features()
    
    def _register_features(self) -> None:
        """Register transaction feature definitions."""
        features = [
            FeatureDefinition(
                name="transaction_count_30d",
                category=FeatureCategory.TRANSACTION,
                description="Number of transactions in last 30 days",
                data_type="numeric",
                is_temporal=True,
                requires_historical_data=True,
                calculation_window_days=30,
                business_definition="Count of transactions in 30-day window"
            ),
            FeatureDefinition(
                name="transaction_count_90d",
                category=FeatureCategory.TRANSACTION,
                description="Number of transactions in last 90 days",
                data_type="numeric",
                is_temporal=True,
                requires_historical_data=True,
                calculation_window_days=90,
                business_definition="Count of transactions in 90-day window"
            ),
            FeatureDefinition(
                name="transaction_volume_30d",
                category=FeatureCategory.TRANSACTION,
                description="Total transaction value in last 30 days",
                data_type="numeric",
                is_temporal=True,
                requires_historical_data=True,
                calculation_window_days=30,
                business_definition="Sum of transaction amounts in 30-day window"
            ),
            FeatureDefinition(
                name="transaction_volume_90d",
                category=FeatureCategory.TRANSACTION,
                description="Total transaction value in last 90 days",
                data_type="numeric",
                is_temporal=True,
                requires_historical_data=True,
                calculation_window_days=90,
                business_definition="Sum of transaction amounts in 90-day window"
            ),
            FeatureDefinition(
                name="avg_transaction_amount_30d",
                category=FeatureCategory.TRANSACTION,
                description="Average transaction amount in last 30 days",
                data_type="numeric",
                is_temporal=True,
                requires_historical_data=True,
                calculation_window_days=30,
                business_definition="Mean transaction amount in 30-day window"
            ),
            FeatureDefinition(
                name="transaction_frequency_30d",
                category=FeatureCategory.TRANSACTION,
                description="Transactions per day in last 30 days",
                data_type="numeric",
                is_temporal=True,
                requires_historical_data=True,
                calculation_window_days=30,
                business_definition="Daily transaction rate in 30-day window"
            ),
            FeatureDefinition(
                name="days_since_last_transaction",
                category=FeatureCategory.TRANSACTION,
                description="Days since most recent transaction",
                data_type="numeric",
                is_temporal=True,
                business_definition="Recency metric: days since last transaction"
            ),
            FeatureDefinition(
                name="transaction_recency_score",
                category=FeatureCategory.TRANSACTION,
                description="Recency score (higher = more recent activity)",
                data_type="numeric",
                is_temporal=True,
                business_definition="Normalized recency score based on last transaction"
            ),
        ]
        
        for feature in features:
            self.register_feature(feature)
    
    def extract(self, transactions_df: pd.DataFrame, customers_df: pd.DataFrame,
                window_days: int = 90) -> pd.DataFrame:
        """Extract transaction features aggregated to customer level.
        
        Args:
            transactions_df: DataFrame from fact_transaction
            customers_df: DataFrame from dim_customer
            window_days: Analysis window in days
        
        Returns:
            DataFrame with transaction features per customer
        """
        logger.info(f"Extracting transaction features for {len(customers_df)} customers")
        
        # Apply temporal safety
        if "transaction_date" in transactions_df.columns:
            transactions_df = self.ensure_temporal_safety(transactions_df, "transaction_date")
        
        # Merge with customers
        merged_df = transactions_df.merge(
            customers_df[["customer_key", "customer_id"]],
            on="customer_key",
            how="left"
        )
        
        # Calculate window start
        window_start = TemporalWindow.get_window_start(self.as_of_date, window_days)
        
        # Filter to window
        merged_df["transaction_date"] = pd.to_datetime(merged_df["transaction_date"])
        window_df = merged_df[merged_df["transaction_date"] >= pd.Timestamp(window_start)].copy()
        
        # Aggregate to customer level
        features_df = window_df.groupby("customer_key").agg({
            "transaction_id": "count",
            "amount": ["sum", "mean"]
        }).reset_index()
        
        features_df.columns = ["customer_key", "transaction_count", "transaction_volume", "avg_transaction_amount"]
        
        # Calculate frequency (transactions per day)
        features_df["transaction_frequency"] = features_df["transaction_count"] / window_days
        
        # Calculate recency metrics
        last_transaction = merged_df.groupby("customer_key")["transaction_date"].max().reset_index()
        last_transaction.columns = ["customer_key", "last_transaction_date"]
        
        as_of_timestamp = pd.Timestamp(self.as_of_date)
        last_transaction["days_since_last_transaction"] = (
            as_of_timestamp - last_transaction["last_transaction_date"]
        ).dt.days
        
        # Calculate recency score (higher = more recent)
        # Score = 1 - (days_since_last / 90), capped at 0
        last_transaction["transaction_recency_score"] = (
            1 - (last_transaction["days_since_last_transaction"] / 90)
        ).clip(lower=0)
        
        # Merge recency metrics
        features_df = features_df.merge(
            last_transaction[["customer_key", "days_since_last_transaction", "transaction_recency_score"]],
            on="customer_key",
            how="left"
        )
        
        # Merge customer_id
        features_df = features_df.merge(
            customers_df[["customer_key", "customer_id"]],
            on="customer_key",
            how="left"
        )
        
        # Fill NaN for customers with no transactions
        features_df = features_df.fillna({
            "transaction_count": 0,
            "transaction_volume": 0,
            "avg_transaction_amount": 0,
            "transaction_frequency": 0,
            "days_since_last_transaction": 999,  # Large value for inactive
            "transaction_recency_score": 0
        })
        
        return features_df


class LoanFeatures(Customer360Base):
    """Extract loan-related features."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize loan features.
        
        Args:
            as_of_date: As-of date for temporal features
        """
        super().__init__(as_of_date)
        self._register_features()
    
    def _register_features(self) -> None:
        """Register loan feature definitions."""
        features = [
            FeatureDefinition(
                name="loan_count",
                category=FeatureCategory.LOAN,
                description="Total number of active loans",
                data_type="numeric",
                is_temporal=True,
                business_definition="Count of active loan accounts"
            ),
            FeatureDefinition(
                name="total_loan_exposure",
                category=FeatureCategory.LOAN,
                description="Total outstanding loan balance",
                data_type="numeric",
                is_temporal=True,
                business_definition="Sum of current balances across all loans"
            ),
            FeatureDefinition(
                name="total_credit_limit",
                category=FeatureCategory.LOAN,
                description="Total credit limit across all credit products",
                data_type="numeric",
                is_temporal=True,
                business_definition="Sum of credit limits for credit cards and lines of credit"
            ),
            FeatureDefinition(
                name="credit_utilization",
                category=FeatureCategory.LOAN,
                description="Credit utilization ratio (used / limit)",
                data_type="numeric",
                is_temporal=True,
                business_definition="Ratio of used credit to total credit limit"
            ),
            FeatureDefinition(
                name="days_past_due_max",
                category=FeatureCategory.LOAN,
                description="Maximum days past due across all loans",
                data_type="numeric",
                is_temporal=True,
                business_definition="Worst delinquency status across loan portfolio"
            ),
            FeatureDefinition(
                name="has_delinquent_loans",
                category=FeatureCategory.LOAN,
                description="Whether customer has any delinquent loans",
                data_type="boolean",
                is_temporal=True,
                business_definition="Flag for any loans with days_past_due > 0"
            ),
        ]
        
        for feature in features:
            self.register_feature(feature)
    
    def extract(self, loans_df: pd.DataFrame, accounts_df: pd.DataFrame,
                customers_df: pd.DataFrame) -> pd.DataFrame:
        """Extract loan features aggregated to customer level.
        
        Args:
            loans_df: DataFrame from fact_loan
            accounts_df: DataFrame from dim_account
            customers_df: DataFrame from dim_customer
        
        Returns:
            DataFrame with loan features per customer
        """
        logger.info(f"Extracting loan features for {len(customers_df)} customers")
        
        # Apply temporal safety
        if "origination_date" in loans_df.columns:
            loans_df = self.ensure_temporal_safety(loans_df, "origination_date")
        
        # Merge with customers
        merged_df = loans_df.merge(
            customers_df[["customer_key", "customer_id"]],
            on="customer_key",
            how="left"
        )
        
        # Aggregate loan metrics
        loan_metrics = merged_df.groupby("customer_key").agg({
            "loan_id": "count",
            "current_balance": "sum",
            "days_past_due": "max"
        }).reset_index()
        
        loan_metrics.columns = ["customer_key", "loan_count", "total_loan_exposure", "days_past_due_max"]
        
        # Calculate credit utilization from accounts
        if "credit_limit" in accounts_df.columns:
            account_metrics = accounts_df.merge(
                customers_df[["customer_key", "customer_id"]],
                on="customer_key",
                how="left"
            )
            
            credit_metrics = account_metrics.groupby("customer_key").agg({
                "credit_limit": "sum"
            }).reset_index()
            
            # Merge with loan metrics
            loan_metrics = loan_metrics.merge(
                credit_metrics.rename(columns={"credit_limit": "total_credit_limit"}),
                on="customer_key",
                how="left"
            )
            
            # Calculate utilization
            loan_metrics["credit_utilization"] = (
                loan_metrics["total_loan_exposure"] / loan_metrics["total_credit_limit"]
            ).fillna(0).clip(upper=1)
        else:
            loan_metrics["total_credit_limit"] = 0
            loan_metrics["credit_utilization"] = 0
        
        # Calculate delinquency flag
        loan_metrics["has_delinquent_loans"] = (loan_metrics["days_past_due_max"] > 0).astype(int)
        
        # Fill NaN
        loan_metrics = loan_metrics.fillna({
            "loan_count": 0,
            "total_loan_exposure": 0,
            "days_past_due_max": 0,
            "has_delinquent_loans": 0
        })
        
        # Merge customer_id
        loan_metrics = loan_metrics.merge(
            customers_df[["customer_key", "customer_id"]],
            on="customer_key",
            how="left"
        )
        
        return loan_metrics


class InteractionFeatures(Customer360Base):
    """Extract customer interaction features."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize interaction features.
        
        Args:
            as_of_date: As-of date for temporal features
        """
        super().__init__(as_of_date)
        self._register_features()
    
    def _register_features(self) -> None:
        """Register interaction feature definitions."""
        features = [
            FeatureDefinition(
                name="interaction_count_90d",
                category=FeatureCategory.INTERACTION,
                description="Number of interactions in last 90 days",
                data_type="numeric",
                is_temporal=True,
                requires_historical_data=True,
                calculation_window_days=90,
                business_definition="Count of customer service interactions"
            ),
            FeatureDefinition(
                name="avg_satisfaction_score",
                category=FeatureCategory.INTERACTION,
                description="Average satisfaction score (1-5)",
                data_type="numeric",
                is_temporal=True,
                business_definition="Mean satisfaction score from interactions"
            ),
            FeatureDefinition(
                name="has_complaints",
                category=FeatureCategory.INTERACTION,
                description="Whether customer has logged complaints",
                data_type="boolean",
                is_temporal=True,
                business_definition="Flag for interactions categorized as complaints"
            ),
            FeatureDefinition(
                name="complaint_count_90d",
                category=FeatureCategory.INTERACTION,
                description="Number of complaints in last 90 days",
                data_type="numeric",
                is_temporal=True,
                requires_historical_data=True,
                calculation_window_days=90,
                business_definition="Count of complaint-type interactions"
            ),
        ]
        
        for feature in features:
            self.register_feature(feature)
    
    def extract(self, interactions_df: pd.DataFrame, customers_df: pd.DataFrame,
                window_days: int = 90) -> pd.DataFrame:
        """Extract interaction features aggregated to customer level.
        
        Args:
            interactions_df: DataFrame from fact_customer_interaction
            customers_df: DataFrame from dim_customer
            window_days: Analysis window in days
        
        Returns:
            DataFrame with interaction features per customer
        """
        logger.info(f"Extracting interaction features for {len(customers_df)} customers")
        
        # Apply temporal safety
        if "interaction_date" in interactions_df.columns:
            interactions_df = self.ensure_temporal_safety(interactions_df, "interaction_date")
        
        # Merge with customers
        merged_df = interactions_df.merge(
            customers_df[["customer_key", "customer_id"]],
            on="customer_key",
            how="left"
        )
        
        # Calculate window start
        window_start = TemporalWindow.get_window_start(self.as_of_date, window_days)
        
        # Filter to window
        merged_df["interaction_date"] = pd.to_datetime(merged_df["interaction_date"])
        window_df = merged_df[merged_df["interaction_date"] >= pd.Timestamp(window_start)].copy()
        
        # Aggregate to customer level
        features_df = window_df.groupby("customer_key").agg({
            "interaction_id": "count",
            "satisfaction_score": "mean"
        }).reset_index()
        
        features_df.columns = ["customer_key", "interaction_count", "avg_satisfaction_score"]
        
        # Calculate complaint metrics
        if "interaction_category" in window_df.columns:
            complaints_df = window_df[window_df["interaction_category"] == "complaint"]
            complaint_counts = complaints_df.groupby("customer_key").size().reset_index()
            complaint_counts.columns = ["customer_key", "complaint_count"]
            
            features_df = features_df.merge(
                complaint_counts,
                on="customer_key",
                how="left"
            )
        else:
            features_df["complaint_count"] = 0
        
        # Calculate complaint flag
        features_df["has_complaints"] = (features_df["complaint_count"] > 0).astype(int)
        
        # Merge customer_id
        features_df = features_df.merge(
            customers_df[["customer_key", "customer_id"]],
            on="customer_key",
            how="left"
        )
        
        # Fill NaN
        features_df = features_df.fillna({
            "interaction_count": 0,
            "avg_satisfaction_score": 0,
            "complaint_count": 0,
            "has_complaints": 0
        })
        
        return features_df


class ProfitabilityFeatures(Customer360Base):
    """Extract profitability features."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize profitability features.
        
        Args:
            as_of_date: As-of date for temporal features
        """
        super().__init__(as_of_date)
        self._register_features()
    
    def _register_features(self) -> None:
        """Register profitability feature definitions."""
        features = [
            FeatureDefinition(
                name="net_profit_12m",
                category=FeatureCategory.PROFITABILITY,
                description="Net profit in last 12 months",
                data_type="numeric",
                is_temporal=True,
                requires_historical_data=True,
                calculation_window_days=365,
                business_definition="Total revenue minus total costs over 12 months"
            ),
            FeatureDefinition(
                name="profit_margin_12m",
                category=FeatureCategory.PROFITABILITY,
                description="Profit margin percentage in last 12 months",
                data_type="numeric",
                is_temporal=True,
                requires_historical_data=True,
                calculation_window_days=365,
                business_definition="Net profit divided by revenue"
            ),
            FeatureDefinition(
                name="avg_balance_12m",
                category=FeatureCategory.PROFITABILITY,
                description="Average account balance in last 12 months",
                data_type="numeric",
                is_temporal=True,
                requires_historical_data=True,
                calculation_window_days=365,
                business_definition="Mean daily balance over 12 months"
            ),
        ]
        
        for feature in features:
            self.register_feature(feature)
    
    def extract(self, profitability_df: pd.DataFrame, customers_df: pd.DataFrame) -> pd.DataFrame:
        """Extract profitability features.
        
        Args:
            profitability_df: DataFrame from fact_customer_profitability
            customers_df: DataFrame from dim_customer
        
        Returns:
            DataFrame with profitability features per customer
        """
        logger.info(f"Extracting profitability features for {len(customers_df)} customers")
        
        if profitability_df.empty:
            # Return empty features if no data
            features_df = customers_df[["customer_key", "customer_id"]].copy()
            features_df["net_profit_12m"] = 0
            features_df["profit_margin_12m"] = 0
            features_df["avg_balance_12m"] = 0
            return features_df
        
        # Apply temporal safety
        if "period_end_date" in profitability_df.columns:
            profitability_df = self.ensure_temporal_safety(profitability_df, "period_end_date")
        
        # Merge with customers
        merged_df = profitability_df.merge(
            customers_df[["customer_key", "customer_id"]],
            on="customer_key",
            how="left"
        )
        
        # Aggregate to customer level (latest period)
        latest_per_customer = merged_df.groupby("customer_key")["period_end_date"].idxmax()
        latest_df = merged_df.loc[latest_per_customer]
        
        features_df = latest_df[[
            "customer_key", "customer_id", "net_profit", 
            "profit_margin", "average_balance"
        ]].copy()
        
        features_df.columns = [
            "customer_key", "customer_id", "net_profit_12m",
            "profit_margin_12m", "avg_balance_12m"
        ]
        
        # Fill NaN
        features_df = features_df.fillna({
            "net_profit_12m": 0,
            "profit_margin_12m": 0,
            "avg_balance_12m": 0
        })
        
        return features_df


class RiskFeatures(Customer360Base):
    """Extract risk features."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize risk features.
        
        Args:
            as_of_date: As-of date for temporal features
        """
        super().__init__(as_of_date)
        self._register_features()
    
    def _register_features(self) -> None:
        """Register risk feature definitions."""
        features = [
            FeatureDefinition(
                name="credit_score",
                category=FeatureCategory.RISK,
                description="Current credit score",
                data_type="numeric",
                is_temporal=True,
                business_definition="FICO or equivalent credit score"
            ),
            FeatureDefinition(
                name="credit_score_trend",
                category=FeatureCategory.RISK,
                description="Credit score change over last 12 months",
                data_type="numeric",
                is_temporal=True,
                requires_historical_data=True,
                calculation_window_days=365,
                business_definition="Difference between current and 12-month-ago credit score"
            ),
            FeatureDefinition(
                name="total_exposure",
                category=FeatureCategory.RISK,
                description="Total credit exposure",
                data_type="numeric",
                is_temporal=True,
                business_definition="Total outstanding credit across all products"
            ),
            FeatureDefinition(
                name="probability_of_default",
                category=FeatureCategory.RISK,
                description="Probability of default (PD)",
                data_type="numeric",
                is_temporal=True,
                business_definition="Model-calculated probability of default"
            ),
            FeatureDefinition(
                name="risk_level",
                category=FeatureCategory.RISK,
                description="Risk category (low, medium, high, critical)",
                data_type="categorical",
                is_temporal=True,
                business_definition="Categorical risk classification"
            ),
            FeatureDefinition(
                name="is_on_watchlist",
                category=FeatureCategory.RISK,
                description="Whether customer is on risk watchlist",
                data_type="boolean",
                is_temporal=True,
                business_definition="Flag for customers requiring special monitoring"
            ),
        ]
        
        for feature in features:
            self.register_feature(feature)
    
    def extract(self, risk_df: pd.DataFrame, customers_df: pd.DataFrame) -> pd.DataFrame:
        """Extract risk features.
        
        Args:
            risk_df: DataFrame from fact_customer_risk
            customers_df: DataFrame from dim_customer
        
        Returns:
            DataFrame with risk features per customer
        """
        logger.info(f"Extracting risk features for {len(customers_df)} customers")
        
        if risk_df.empty:
            # Return empty features if no data
            features_df = customers_df[["customer_key", "customer_id"]].copy()
            features_df["credit_score"] = 0
            features_df["credit_score_trend"] = 0
            features_df["total_exposure"] = 0
            features_df["probability_of_default"] = 0
            features_df["risk_level"] = "unknown"
            features_df["is_on_watchlist"] = 0
            return features_df
        
        # Apply temporal safety
        if "period_end_date" in risk_df.columns:
            risk_df = self.ensure_temporal_safety(risk_df, "period_end_date")
        
        # Merge with customers
        merged_df = risk_df.merge(
            customers_df[["customer_key", "customer_id"]],
            on="customer_key",
            how="left"
        )
        
        # Aggregate to customer level (latest period)
        latest_per_customer = merged_df.groupby("customer_key")["period_end_date"].idxmax()
        latest_df = merged_df.loc[latest_per_customer]
        
        features_df = latest_df[[
            "customer_key", "customer_id", "credit_score",
            "credit_score_change", "total_exposure",
            "probability_of_default", "risk_level", "is_on_watchlist"
        ]].copy()
        
        features_df.columns = [
            "customer_key", "customer_id", "credit_score",
            "credit_score_trend", "total_exposure",
            "probability_of_default", "risk_level", "is_on_watchlist"
        ]
        
        # Fill NaN
        features_df = features_df.fillna({
            "credit_score": 0,
            "credit_score_trend": 0,
            "total_exposure": 0,
            "probability_of_default": 0,
            "risk_level": "unknown",
            "is_on_watchlist": 0
        })
        
        return features_df
