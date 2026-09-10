"""Customer 360 Platform - Data Platform Integration Layer.

This module provides a unified view of customer data by integrating
demographics, accounts, loans, transactions, and profitability data.

Architecture Position:
Banking Data → Data Platform → Customer 360 Analytics → Core Analytics
"""

from typing import Dict, Any, Optional, List
from datetime import date, timedelta
import logging

import pandas as pd

from src.data_platform.data_loader import DataLoader
from src.customer_intelligence.base import Customer360Base, FeatureDefinition, FeatureCategory

logger = logging.getLogger(__name__)


class Customer360Platform(Customer360Base):
    """Customer 360 Platform for unified customer view.
    
    This class integrates data from multiple sources to provide a comprehensive
    view of each customer, serving as the foundation for all analytics.
    """
    
    def __init__(self, as_of_date: Optional[date] = None, data_loader: Optional[DataLoader] = None):
        """Initialize Customer 360 Platform.
        
        Args:
            as_of_date: As-of date for temporal analysis
            data_loader: Data loader instance (creates default if not provided)
        """
        super().__init__(as_of_date)
        self.data_loader = data_loader or DataLoader()
        
        # Register standard Customer 360 features
        self._register_customer_360_features()
    
    def _register_customer_360_features(self) -> None:
        """Register standard Customer 360 features."""
        features = [
            # Demographic Features
            FeatureDefinition(
                name="customer_age",
                category=FeatureCategory.DEMOGRAPHIC,
                description="Customer age in years",
                data_type="numeric",
                is_temporal=False,
                business_definition="Customer's current age based on birth date"
            ),
            FeatureDefinition(
                name="income_level",
                category=FeatureCategory.DEMOGRAPHIC,
                description="Customer income level category",
                data_type="categorical",
                is_temporal=False,
                business_definition="Categorization of customer's income level"
            ),
            FeatureDefinition(
                name="customer_tenure_days",
                category=FeatureCategory.DEMOGRAPHIC,
                description="Number of days customer has been with the bank",
                data_type="numeric",
                is_temporal=True,
                business_definition="Tenure calculated from customer_since date to as_of_date"
            ),
            # Account Features
            FeatureDefinition(
                name="total_accounts",
                category=FeatureCategory.ACCOUNT,
                description="Total number of active accounts",
                data_type="numeric",
                is_temporal=True,
                requires_historical_data=True,
                business_definition="Count of all active accounts for the customer"
            ),
            FeatureDefinition(
                name="total_balance",
                category=FeatureCategory.ACCOUNT,
                description="Total balance across all accounts",
                data_type="numeric",
                is_temporal=True,
                requires_historical_data=True,
                business_definition="Sum of balances across all accounts"
            ),
            FeatureDefinition(
                name="avg_account_balance",
                category=FeatureCategory.ACCOUNT,
                description="Average balance per account",
                data_type="numeric",
                is_temporal=True,
                requires_historical_data=True,
                business_definition="Average balance across all accounts"
            ),
            # Loan Features
            FeatureDefinition(
                name="total_loans",
                category=FeatureCategory.LOAN,
                description="Total number of active loans",
                data_type="numeric",
                is_temporal=True,
                requires_historical_data=True,
                business_definition="Count of all active loans for the customer"
            ),
            FeatureDefinition(
                name="total_loan_balance",
                category=FeatureCategory.LOAN,
                description="Total outstanding loan balance",
                data_type="numeric",
                is_temporal=True,
                requires_historical_data=True,
                business_definition="Sum of outstanding balances across all loans"
            ),
            FeatureDefinition(
                name="avg_loan_amount",
                category=FeatureCategory.LOAN,
                description="Average loan amount",
                data_type="numeric",
                is_temporal=True,
                requires_historical_data=True,
                business_definition="Average original loan amount across all loans"
            ),
            # Transaction Features
            FeatureDefinition(
                name="transaction_count_30d",
                category=FeatureCategory.TRANSACTION,
                description="Number of transactions in last 30 days",
                data_type="numeric",
                is_temporal=True,
                requires_historical_data=True,
                calculation_window_days=30,
                business_definition="Count of transactions in the 30 days prior to as_of_date"
            ),
            FeatureDefinition(
                name="transaction_volume_30d",
                category=FeatureCategory.TRANSACTION,
                description="Total transaction volume in last 30 days",
                data_type="numeric",
                is_temporal=True,
                requires_historical_data=True,
                calculation_window_days=30,
                business_definition="Sum of transaction amounts in the 30 days prior to as_of_date"
            ),
            FeatureDefinition(
                name="avg_transaction_value_30d",
                category=FeatureCategory.TRANSACTION,
                description="Average transaction value in last 30 days",
                data_type="numeric",
                is_temporal=True,
                requires_historical_data=True,
                calculation_window_days=30,
                business_definition="Average transaction amount in the 30 days prior to as_of_date"
            ),
            # Profitability Features
            FeatureDefinition(
                name="net_profit",
                category=FeatureCategory.PROFITABILITY,
                description="Net profit for the customer",
                data_type="numeric",
                is_temporal=True,
                requires_historical_data=True,
                business_definition="Revenue minus all costs including expected credit loss"
            ),
            FeatureDefinition(
                name="profit_margin",
                category=FeatureCategory.PROFITABILITY,
                description="Profit margin percentage",
                data_type="percentage",
                is_temporal=True,
                requires_historical_data=True,
                business_definition="Net profit as percentage of gross revenue"
            ),
            FeatureDefinition(
                name="clv",
                category=FeatureCategory.PROFITABILITY,
                description="Customer lifetime value",
                data_type="numeric",
                is_temporal=True,
                requires_historical_data=True,
                business_definition="Predicted total value of customer relationship"
            ),
            # Risk Features
            FeatureDefinition(
                name="risk_level",
                category=FeatureCategory.RISK,
                description="Customer risk level",
                data_type="categorical",
                is_temporal=True,
                requires_historical_data=True,
                business_definition="Categorical risk assessment (low, medium, high, critical)"
            ),
            FeatureDefinition(
                name="credit_utilization",
                category=FeatureCategory.RISK,
                description="Credit utilization ratio",
                data_type="percentage",
                is_temporal=True,
                requires_historical_data=True,
                business_definition="Percentage of available credit being used"
            ),
            FeatureDefinition(
                name="credit_score",
                category=FeatureCategory.RISK,
                description="Credit score",
                data_type="numeric",
                is_temporal=True,
                requires_historical_data=True,
                business_definition="Customer's credit score (300-850)"
            ),
        ]
        
        for feature in features:
            self.register_feature(feature)
    
    def get_customer_360(
        self,
        customer_key: str,
        include_transactions: bool = True,
        transaction_window_days: int = 90
    ) -> Dict[str, Any]:
        """Get comprehensive Customer 360 view for a single customer.
        
        Args:
            customer_key: Customer key
            include_transactions: Whether to include transaction data
            transaction_window_days: Number of days of transaction history to include
        
        Returns:
            Dictionary with complete Customer 360 view
        """
        logger.info(f"Generating Customer 360 for customer: {customer_key}")
        
        # Load customer demographics
        customers_df = self.data_loader.load_customers(customer_keys=[customer_key])
        if customers_df.empty:
            logger.warning(f"Customer not found: {customer_key}")
            return {}
        
        customer_data = customers_df.iloc[0].to_dict()
        
        # Load customer metrics (Core Analytics output)
        metrics_df = self.data_loader.load_customer_metrics(customer_keys=[customer_key])
        if not metrics_df.empty:
            metrics_data = metrics_df.iloc[0].to_dict()
            customer_data.update(metrics_data)
        
        # Load accounts
        accounts_df = self.data_loader.load_accounts(customer_key=customer_key)
        account_summary = self._summarize_accounts(accounts_df)
        customer_data['accounts'] = account_summary
        
        # Load loans
        loans_df = self.data_loader.load_loans(customer_key=customer_key)
        loan_summary = self._summarize_loans(loans_df)
        customer_data['loans'] = loan_summary
        
        # Load transactions
        if include_transactions:
            start_date = self.as_of_date - timedelta(days=transaction_window_days)
            transactions_df = self.data_loader.load_transactions(
                customer_key=customer_key,
                start_date=start_date,
                end_date=self.as_of_date
            )
            transaction_summary = self._summarize_transactions(transactions_df)
            customer_data['transactions'] = transaction_summary
        
        # Load profitability
        profitability_df = self.data_loader.load_customer_profitability(customer_key=customer_key)
        profitability_summary = self._summarize_profitability(profitability_df)
        customer_data['profitability_history'] = profitability_summary
        
        # Load recommendations (Decision Engine output)
        recommendations_df = self.data_loader.load_recommendations(customer_key=customer_key)
        customer_data['recommendations'] = recommendations_df.to_dict('records') if not recommendations_df.empty else []
        
        logger.info(f"Customer 360 generated successfully for: {customer_key}")
        return customer_data
    
    def get_customer_360_batch(
        self,
        customer_keys: List[str],
        include_transactions: bool = False
    ) -> pd.DataFrame:
        """Get Customer 360 view for multiple customers.
        
        Args:
            customer_keys: List of customer keys
            include_transactions: Whether to include transaction data (expensive for batch)
        
        Returns:
            DataFrame with Customer 360 data for all customers
        """
        logger.info(f"Generating Customer 360 for {len(customer_keys)} customers")
        
        results = []
        
        for customer_key in customer_keys:
            customer_360 = self.get_customer_360(
                customer_key=customer_key,
                include_transactions=include_transactions
            )
            if customer_360:
                results.append(customer_360)
        
        df = pd.DataFrame(results)
        logger.info(f"Generated Customer 360 for {len(df)} customers")
        return df
    
    def _summarize_accounts(self, accounts_df: pd.DataFrame) -> Dict[str, Any]:
        """Summarize account data.
        
        Args:
            accounts_df: DataFrame with account data
        
        Returns:
            Dictionary with account summary
        """
        if accounts_df.empty:
            return {
                "total_accounts": 0,
                "total_balance": 0,
                "account_types": {}
            }
        
        summary = {
            "total_accounts": len(accounts_df),
            "total_balance": float(accounts_df['current_balance'].sum()),
            "avg_balance": float(accounts_df['current_balance'].mean()),
            "account_types": accounts_df['account_type'].value_counts().to_dict(),
            "accounts": accounts_df.to_dict('records')
        }
        
        return summary
    
    def _summarize_loans(self, loans_df: pd.DataFrame) -> Dict[str, Any]:
        """Summarize loan data.
        
        Args:
            loans_df: DataFrame with loan data
        
        Returns:
            Dictionary with loan summary
        """
        if loans_df.empty:
            return {
                "total_loans": 0,
                "total_balance": 0,
                "loan_status": {}
            }
        
        summary = {
            "total_loans": len(loans_df),
            "total_balance": float(loans_df['current_balance'].sum()),
            "avg_balance": float(loans_df['current_balance'].mean()),
            "avg_loan_amount": float(loans_df['loan_amount'].mean()),
            "loan_status": loans_df['loan_status'].value_counts().to_dict(),
            "avg_days_past_due": float(loans_df['days_past_due'].mean()),
            "loans": loans_df.to_dict('records')
        }
        
        return summary
    
    def _summarize_transactions(self, transactions_df: pd.DataFrame) -> Dict[str, Any]:
        """Summarize transaction data.
        
        Args:
            transactions_df: DataFrame with transaction data
        
        Returns:
            Dictionary with transaction summary
        """
        if transactions_df.empty:
            return {
                "total_transactions": 0,
                "total_volume": 0,
                "transaction_types": {}
            }
        
        summary = {
            "total_transactions": len(transactions_df),
            "total_volume": float(transactions_df['amount'].abs().sum()),
            "avg_transaction_value": float(transactions_df['amount'].abs().mean()),
            "transaction_types": transactions_df['transaction_type'].value_counts().to_dict(),
            "merchant_categories": transactions_df['merchant_category'].value_counts().to_dict(),
            "transactions": transactions_df.to_dict('records')
        }
        
        return summary
    
    def _summarize_profitability(self, profitability_df: pd.DataFrame) -> Dict[str, Any]:
        """Summarize profitability data.
        
        Args:
            profitability_df: DataFrame with profitability data
        
        Returns:
            Dictionary with profitability summary
        """
        if profitability_df.empty:
            return {
                "total_profit": 0,
                "avg_monthly_profit": 0,
                "profit_trend": "stable"
            }
        
        total_profit = float(profitability_df['interest_income'].fillna(0) + 
                           profitability_df['fee_income'].fillna(0) + 
                           profitability_df['service_charge_income'].fillna(0) - 
                           profitability_df['servicing_cost'].fillna(0) - 
                           profitability_df['operational_cost'].fillna(0))
        
        summary = {
            "total_profit": total_profit,
            "avg_monthly_profit": total_profit / len(profitability_df) if len(profitability_df) > 0 else 0,
            "periods": len(profitability_df),
            "profitability_history": profitability_df.to_dict('records')
        }
        
        return summary
