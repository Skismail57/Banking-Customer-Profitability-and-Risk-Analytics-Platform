"""Orchestrator for Customer 360 feature generation."""

from datetime import date
from typing import Dict, Any, Optional, List
import logging

import pandas as pd

from src.customer_intelligence.features import (
    DemographicFeatures,
    AccountFeatures,
    TransactionFeatures,
    LoanFeatures,
    InteractionFeatures,
    ProfitabilityFeatures,
    RiskFeatures,
)
from src.customer_intelligence.base import FeatureCategory

logger = logging.getLogger(__name__)


class Customer360Orchestrator:
    """Orchestrates the generation of Customer 360 features."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize Customer 360 orchestrator.
        
        Args:
            as_of_date: As-of date for temporal features (prevents future data leakage)
        """
        self.as_of_date = as_of_date or date.today()
        
        # Initialize feature extractors
        self.demographic_extractor = DemographicFeatures(self.as_of_date)
        self.account_extractor = AccountFeatures(self.as_of_date)
        self.transaction_extractor = TransactionFeatures(self.as_of_date)
        self.loan_extractor = LoanFeatures(self.as_of_date)
        self.interaction_extractor = InteractionFeatures(self.as_of_date)
        self.profitability_extractor = ProfitabilityFeatures(self.as_of_date)
        self.risk_extractor = RiskFeatures(self.as_of_date)
    
    def generate_customer_360(
        self,
        customers_df: pd.DataFrame,
        accounts_df: pd.DataFrame,
        transactions_df: pd.DataFrame,
        loans_df: pd.DataFrame,
        interactions_df: pd.DataFrame,
        profitability_df: pd.DataFrame,
        risk_df: pd.DataFrame,
        transaction_window_days: int = 90
    ) -> pd.DataFrame:
        """Generate comprehensive Customer 360 view.
        
        Args:
            customers_df: DataFrame from dim_customer
            accounts_df: DataFrame from dim_account
            transactions_df: DataFrame from fact_transaction
            loans_df: DataFrame from fact_loan
            interactions_df: DataFrame from fact_customer_interaction
            profitability_df: DataFrame from fact_customer_profitability
            risk_df: DataFrame from fact_customer_risk
            transaction_window_days: Window for transaction features
        
        Returns:
            DataFrame with all Customer 360 features
        """
        logger.info(f"Generating Customer 360 features as of {self.as_of_date}")
        
        # Extract demographic features
        logger.info("Extracting demographic features...")
        demographic_df = self.demographic_extractor.extract(customers_df)
        
        # Extract account features
        logger.info("Extracting account features...")
        account_df = self.account_extractor.extract(accounts_df, customers_df)
        
        # Extract transaction features
        logger.info("Extracting transaction features...")
        transaction_df = self.transaction_extractor.extract(
            transactions_df, customers_df, transaction_window_days
        )
        
        # Extract loan features
        logger.info("Extracting loan features...")
        loan_df = self.loan_extractor.extract(loans_df, accounts_df, customers_df)
        
        # Extract interaction features
        logger.info("Extracting interaction features...")
        interaction_df = self.interaction_extractor.extract(
            interactions_df, customers_df, transaction_window_days
        )
        
        # Extract profitability features
        logger.info("Extracting profitability features...")
        profitability_df_extracted = self.profitability_extractor.extract(
            profitability_df, customers_df
        )
        
        # Extract risk features
        logger.info("Extracting risk features...")
        risk_df_extracted = self.risk_extractor.extract(risk_df, customers_df)
        
        # Merge all features on customer_key
        logger.info("Merging all features...")
        customer_360_df = self._merge_features(
            demographic_df,
            account_df,
            transaction_df,
            loan_df,
            interaction_df,
            profitability_df_extracted,
            risk_df_extracted
        )
        
        # Add as_of_date
        customer_360_df["as_of_date"] = self.as_of_date
        
        logger.info(f"Customer 360 generation complete. {len(customer_360_df)} customers.")
        
        return customer_360_df
    
    def _merge_features(
        self,
        demographic_df: pd.DataFrame,
        account_df: pd.DataFrame,
        transaction_df: pd.DataFrame,
        loan_df: pd.DataFrame,
        interaction_df: pd.DataFrame,
        profitability_df: pd.DataFrame,
        risk_df: pd.DataFrame
    ) -> pd.DataFrame:
        """Merge all feature DataFrames on customer_key.
        
        Args:
            demographic_df: Demographic features
            account_df: Account features
            transaction_df: Transaction features
            loan_df: Loan features
            interaction_df: Interaction features
            profitability_df: Profitability features
            risk_df: Risk features
        
        Returns:
            Merged DataFrame with all features
        """
        # Start with demographic features as base
        merged_df = demographic_df.copy()
        
        # Merge account features
        if "customer_key" in account_df.columns:
            merged_df = merged_df.merge(
                account_df.drop(columns=["customer_id"], errors="ignore"),
                on="customer_key",
                how="left",
                suffixes=("", "_account")
            )
        
        # Merge transaction features
        if "customer_key" in transaction_df.columns:
            merged_df = merged_df.merge(
                transaction_df.drop(columns=["customer_id"], errors="ignore"),
                on="customer_key",
                how="left",
                suffixes=("", "_transaction")
            )
        
        # Merge loan features
        if "customer_key" in loan_df.columns:
            merged_df = merged_df.merge(
                loan_df.drop(columns=["customer_id"], errors="ignore"),
                on="customer_key",
                how="left",
                suffixes=("", "_loan")
            )
        
        # Merge interaction features
        if "customer_key" in interaction_df.columns:
            merged_df = merged_df.merge(
                interaction_df.drop(columns=["customer_id"], errors="ignore"),
                on="customer_key",
                how="left",
                suffixes=("", "_interaction")
            )
        
        # Merge profitability features
        if "customer_key" in profitability_df.columns:
            merged_df = merged_df.merge(
                profitability_df.drop(columns=["customer_id"], errors="ignore"),
                on="customer_key",
                how="left",
                suffixes=("", "_profitability")
            )
        
        # Merge risk features
        if "customer_key" in risk_df.columns:
            merged_df = merged_df.merge(
                risk_df.drop(columns=["customer_id"], errors="ignore"),
                on="customer_key",
                how="left",
                suffixes=("", "_risk")
            )
        
        # Fill NaN values with appropriate defaults
        merged_df = self._fill_missing_values(merged_df)
        
        return merged_df
    
    def _fill_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fill missing values with appropriate defaults.
        
        Args:
            df: DataFrame to fill
        
        Returns:
            DataFrame with filled values
        """
        # Numeric columns - fill with 0
        numeric_columns = df.select_dtypes(include=["number"]).columns
        df[numeric_columns] = df[numeric_columns].fillna(0)
        
        # String columns - fill with empty string or "unknown"
        string_columns = df.select_dtypes(include=["object"]).columns
        for col in string_columns:
            if col not in ["customer_id"]:
                df[col] = df[col].fillna("unknown")
        
        # Boolean columns - fill with False
        boolean_columns = df.select_dtypes(include=["boolean"]).columns
        df[boolean_columns] = df[boolean_columns].fillna(False)
        
        return df
    
    def get_feature_registry(self) -> Dict[str, Any]:
        """Get all registered feature definitions.
        
        Returns:
            Dictionary of all feature definitions
        """
        registry = {}
        
        extractors = [
            ("demographic", self.demographic_extractor),
            ("account", self.account_extractor),
            ("transaction", self.transaction_extractor),
            ("loan", self.loan_extractor),
            ("interaction", self.interaction_extractor),
            ("profitability", self.profitability_extractor),
            ("risk", self.risk_extractor),
        ]
        
        for name, extractor in extractors:
            registry[name] = {
                feature.name: feature.to_dict()
                for feature in extractor.feature_registry.values()
            }
        
        return registry
    
    def get_features_by_category(self, category: FeatureCategory) -> List[Dict[str, Any]]:
        """Get all features in a specific category.
        
        Args:
            category: FeatureCategory to filter by
        
        Returns:
            List of feature definitions
        """
        features = []
        
        extractors = [
            self.demographic_extractor,
            self.account_extractor,
            self.transaction_extractor,
            self.loan_extractor,
            self.interaction_extractor,
            self.profitability_extractor,
            self.risk_extractor,
        ]
        
        for extractor in extractors:
            category_features = extractor.get_features_by_category(category)
            features.extend([f.to_dict() for f in category_features])
        
        return features
    
    def generate_feature_summary(self, customer_360_df: pd.DataFrame) -> Dict[str, Any]:
        """Generate summary statistics for Customer 360 features.
        
        Args:
            customer_360_df: Customer 360 DataFrame
        
        Returns:
            Summary statistics dictionary
        """
        summary = {
            "as_of_date": self.as_of_date.isoformat(),
            "total_customers": len(customer_360_df),
            "feature_count": len(customer_360_df.columns),
            "categories": {}
        }
        
        # Summarize by category
        category_columns = {
            FeatureCategory.DEMOGRAPHIC: ["age", "age_group", "gender", "marital_status", "tenure_years"],
            FeatureCategory.ACCOUNT: ["account_count", "active_account_count", "total_balance", "product_diversity"],
            FeatureCategory.TRANSACTION: ["transaction_count_30d", "transaction_volume_30d", "days_since_last_transaction"],
            FeatureCategory.LOAN: ["loan_count", "total_loan_exposure", "credit_utilization"],
            FeatureCategory.INTERACTION: ["interaction_count_90d", "avg_satisfaction_score", "has_complaints"],
            FeatureCategory.PROFITABILITY: ["net_profit_12m", "profit_margin_12m"],
            FeatureCategory.RISK: ["credit_score", "probability_of_default", "risk_level"],
        }
        
        for category, columns in category_columns.items():
            available_columns = [col for col in columns if col in customer_360_df.columns]
            if available_columns:
                summary["categories"][category.value] = {
                    "feature_count": len(available_columns),
                    "features": available_columns
                }
        
        return summary
