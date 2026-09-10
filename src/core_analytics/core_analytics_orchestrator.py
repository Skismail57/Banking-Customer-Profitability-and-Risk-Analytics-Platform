"""Core Analytics Orchestrator.

This orchestrator integrates Profitability, Risk, and Behavior analytics
to produce unified customer metrics stored in fact_customer_metrics.

Architecture:
Customer 360/Transaction/Product Analytics → Core Analytics → Statistical Analytics
"""

from typing import Dict, Any, Optional, List
from datetime import date
import logging

import pandas as pd

from src.data_platform.data_loader import DataLoader
from src.profitability_analytics.orchestrator import ProfitabilityOrchestrator
from src.credit_risk_analytics.orchestrator import CreditRiskOrchestrator
from src.advanced_risk_analytics.orchestrator import AdvancedRiskOrchestrator
from src.churn_analytics.orchestrator import ChurnOrchestrator
from src.clv_analytics.orchestrator import CLVOrchestrator

logger = logging.getLogger(__name__)


class CoreAnalyticsOrchestrator:
    """Core Analytics Orchestrator.
    
    This class orchestrates the calculation of all core analytics (profitability,
    risk, behavior) and stores the results in fact_customer_metrics.
    """
    
    def __init__(
        self,
        as_of_date: Optional[date] = None,
        data_loader: Optional[DataLoader] = None
    ):
        """Initialize Core Analytics Orchestrator.
        
        Args:
            as_of_date: As-of date for analytics calculation
            data_loader: Data loader instance
        """
        self.as_of_date = as_of_date or date.today()
        self.data_loader = data_loader or DataLoader()
        
        # Initialize analytics orchestrators
        self.profitability_orchestrator = ProfitabilityOrchestrator(as_of_date=self.as_of_date)
        self.credit_risk_orchestrator = CreditRiskOrchestrator(as_of_date=self.as_of_date)
        self.advanced_risk_orchestrator = AdvancedRiskOrchestrator(as_of_date=self.as_of_date)
        self.churn_orchestrator = ChurnOrchestrator(as_of_date=self.as_of_date)
        self.clv_orchestrator = CLVOrchestrator(as_of_date=self.as_of_date)
    
    def calculate_core_metrics(
        self,
        customer_keys: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Calculate core metrics for customers.
        
        This method integrates profitability, risk, and behavior analytics
        to produce a unified view of customer metrics.
        
        Args:
            customer_keys: Optional list of customer keys to calculate metrics for.
                          If None, calculates for all customers.
        
        Returns:
            DataFrame with core metrics for all customers
        """
        logger.info(f"Calculating core metrics for as_of_date: {self.as_of_date}")
        
        # Load customer data
        if customer_keys:
            customers_df = self.data_loader.load_customers(customer_keys=customer_keys)
        else:
            customers_df = self.data_loader.load_customers()
        
        if customers_df.empty:
            logger.warning("No customers found")
            return pd.DataFrame()
        
        # Initialize results DataFrame
        results = []
        
        for customer_key in customers_df['customer_key']:
            customer_metrics = self._calculate_customer_core_metrics(customer_key)
            if customer_metrics:
                results.append(customer_metrics)
        
        metrics_df = pd.DataFrame(results)
        
        logger.info(f"Calculated core metrics for {len(metrics_df)} customers")
        return metrics_df
    
    def _calculate_customer_core_metrics(self, customer_key: str) -> Dict[str, Any]:
        """Calculate core metrics for a single customer.
        
        Args:
            customer_key: Customer key
        
        Returns:
            Dictionary with core metrics
        """
        logger.debug(f"Calculating core metrics for customer: {customer_key}")
        
        metrics = {
            'customer_key': customer_key,
            'as_of_date': self.as_of_date
        }
        
        # Load customer data
        customers_df = self.data_loader.load_customers(customer_keys=[customer_key])
        if customers_df.empty:
            return {}
        
        customer_data = customers_df.iloc[0]
        metrics['segment'] = customer_data.get('segment')
        
        # Calculate Profitability Metrics
        profitability_metrics = self._calculate_profitability_metrics(customer_key)
        metrics.update(profitability_metrics)
        
        # Calculate Risk Metrics
        risk_metrics = self._calculate_risk_metrics(customer_key)
        metrics.update(risk_metrics)
        
        # Calculate Churn Metrics
        churn_metrics = self._calculate_churn_metrics(customer_key)
        metrics.update(churn_metrics)
        
        # Calculate CLV Metrics
        clv_metrics = self._calculate_clv_metrics(customer_key)
        metrics.update(clv_metrics)
        
        return metrics
    
    def _calculate_profitability_metrics(self, customer_key: str) -> Dict[str, Any]:
        """Calculate profitability metrics for a customer.
        
        Args:
            customer_key: Customer key
        
        Returns:
            Dictionary with profitability metrics
        """
        try:
            # Load profitability data
            profitability_df = self.data_loader.load_customer_profitability(customer_key=customer_key)
            
            if profitability_df.empty:
                return {
                    'net_profit': None,
                    'revenue': None,
                    'cost': None,
                    'profit_margin': None,
                    'risk_adjusted_profit': None
                }
            
            # Calculate aggregate profitability
            total_revenue = (
                profitability_df['interest_income'].fillna(0).sum() +
                profitability_df['fee_income'].fillna(0).sum() +
                profitability_df['service_charge_income'].fillna(0).sum() +
                profitability_df['product_revenue'].fillna(0).sum()
            )
            
            total_cost = (
                profitability_df['servicing_cost'].fillna(0).sum() +
                profitability_df['operational_cost'].fillna(0).sum() +
                profitability_df['incentive_cost'].fillna(0).sum() +
                profitability_df['expected_credit_loss'].fillna(0).sum()
            )
            
            net_profit = total_revenue - total_cost
            profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else None
            
            # Risk-adjusted profit (simplified: reduce profit by risk factor)
            # This would use actual risk calculations from risk analytics
            risk_adjusted_profit = net_profit * 0.95  # Placeholder risk adjustment
            
            return {
                'net_profit': float(net_profit),
                'revenue': float(total_revenue),
                'cost': float(total_cost),
                'profit_margin': float(profit_margin) if profit_margin is not None else None,
                'risk_adjusted_profit': float(risk_adjusted_profit)
            }
            
        except Exception as e:
            logger.error(f"Error calculating profitability metrics for {customer_key}: {e}")
            return {
                'net_profit': None,
                'revenue': None,
                'cost': None,
                'profit_margin': None,
                'risk_adjusted_profit': None
            }
    
    def _calculate_risk_metrics(self, customer_key: str) -> Dict[str, Any]:
        """Calculate risk metrics for a customer.
        
        Args:
            customer_key: Customer key
        
        Returns:
            Dictionary with risk metrics
        """
        try:
            # Load loan data
            loans_df = self.data_loader.load_loans(customer_key=customer_key)
            
            # Load account data
            accounts_df = self.data_loader.load_accounts(customer_key=customer_key)
            
            # Load payment data
            payments_df = self.data_loader.load_payments(customer_key=customer_key)
            
            # Calculate exposure
            total_exposure = 0.0
            if not loans_df.empty:
                total_exposure += loans_df['current_balance'].fillna(0).sum()
            if not accounts_df.empty:
                total_exposure += accounts_df['current_balance'].fillna(0).sum()
            
            # Calculate credit utilization
            credit_utilization = None
            if not accounts_df.empty and not accounts_df['credit_limit'].isna().all():
                total_balance = accounts_df['current_balance'].fillna(0).sum()
                total_limit = accounts_df['credit_limit'].fillna(0).sum()
                credit_utilization = (total_balance / total_limit) if total_limit > 0 else None
            
            # Calculate days past due
            days_past_due = None
            if not loans_df.empty:
                days_past_due = int(loans_df['days_past_due'].max())
            
            # Calculate credit score (placeholder - would come from credit bureau)
            credit_score = None  # Would be loaded from actual data
            
            # Calculate balance-to-income ratio
            balance_to_income_ratio = None
            if not loans_df.empty:
                total_balance = loans_df['current_balance'].fillna(0).sum()
                # Would need income data to calculate actual ratio
                balance_to_income_ratio = total_balance / 50000  # Placeholder
            
            # Determine risk level using advanced risk analytics
            risk_level = self._determine_risk_level(
                credit_utilization=credit_utilization,
                days_past_due=days_past_due,
                credit_score=credit_score,
                balance_to_income_ratio=balance_to_income_ratio
            )
            
            # Determine risk trend (placeholder)
            risk_trend = 'stable'
            
            return {
                'risk_level': risk_level,
                'risk_trend': risk_trend,
                'exposure_amount': float(total_exposure),
                'credit_utilization': float(credit_utilization) if credit_utilization is not None else None,
                'days_past_due': days_past_due,
                'credit_score': credit_score,
                'balance_to_income_ratio': float(balance_to_income_ratio) if balance_to_income_ratio is not None else None
            }
            
        except Exception as e:
            logger.error(f"Error calculating risk metrics for {customer_key}: {e}")
            return {
                'risk_level': None,
                'risk_trend': None,
                'exposure_amount': None,
                'credit_utilization': None,
                'days_past_due': None,
                'credit_score': None,
                'balance_to_income_ratio': None
            }
    
    def _determine_risk_level(
        self,
        credit_utilization: Optional[float],
        days_past_due: Optional[int],
        credit_score: Optional[int],
        balance_to_income_ratio: Optional[float]
    ) -> Optional[str]:
        """Determine risk level based on risk metrics.
        
        Args:
            credit_utilization: Credit utilization ratio
            days_past_due: Days past due
            credit_score: Credit score
            balance_to_income_ratio: Balance-to-income ratio
        
        Returns:
            Risk level (low, medium, high, critical)
        """
        risk_score = 0
        
        # Credit utilization contribution
        if credit_utilization is not None:
            if credit_utilization >= 0.85:
                risk_score += 3
            elif credit_utilization >= 0.60:
                risk_score += 2
            elif credit_utilization >= 0.30:
                risk_score += 1
        
        # Days past due contribution
        if days_past_due is not None:
            if days_past_due >= 90:
                risk_score += 4
            elif days_past_due >= 60:
                risk_score += 3
            elif days_past_due >= 30:
                risk_score += 2
            elif days_past_due > 0:
                risk_score += 1
        
        # Credit score contribution
        if credit_score is not None:
            if credit_score < 500:
                risk_score += 3
            elif credit_score < 600:
                risk_score += 2
            elif credit_score < 700:
                risk_score += 1
        
        # Balance-to-income ratio contribution
        if balance_to_income_ratio is not None:
            if balance_to_income_ratio >= 0.60:
                risk_score += 3
            elif balance_to_income_ratio >= 0.40:
                risk_score += 2
            elif balance_to_income_ratio >= 0.20:
                risk_score += 1
        
        # Determine risk level
        if risk_score >= 7:
            return 'critical'
        elif risk_score >= 5:
            return 'high'
        elif risk_score >= 3:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_churn_metrics(self, customer_key: str) -> Dict[str, Any]:
        """Calculate churn metrics for a customer.
        
        Args:
            customer_key: Customer key
        
        Returns:
            Dictionary with churn metrics
        """
        try:
            # Load transaction data for behavioral analysis
            transactions_df = self.data_loader.load_transactions(customer_key=customer_key)
            
            # Calculate churn probability using churn analytics
            # This would use the actual churn model
            churn_probability = self._estimate_churn_probability(
                transactions_df=transactions_df,
                customer_key=customer_key
            )
            
            # Determine churn risk level
            churn_risk_level = self._determine_churn_risk_level(churn_probability)
            
            return {
                'churn_probability': float(churn_probability) if churn_probability is not None else None,
                'churn_risk_level': churn_risk_level
            }
            
        except Exception as e:
            logger.error(f"Error calculating churn metrics for {customer_key}: {e}")
            return {
                'churn_probability': None,
                'churn_risk_level': None
            }
    
    def _estimate_churn_probability(
        self,
        transactions_df: pd.DataFrame,
        customer_key: str
    ) -> Optional[float]:
        """Estimate churn probability (placeholder).
        
        Args:
            transactions_df: Transaction data
            customer_key: Customer key
        
        Returns:
            Churn probability (0-1)
        """
        # Placeholder: would use actual churn model
        # For now, estimate based on transaction activity
        if transactions_df.empty:
            return 0.5  # Default probability
        
        # Calculate transaction frequency
        transactions_df['transaction_date'] = pd.to_datetime(transactions_df['transaction_date'])
        recent_transactions = transactions_df[
            transactions_df['transaction_date'] >= pd.Timestamp(self.as_of_date) - pd.Timedelta(days=30)
        ]
        
        if len(recent_transactions) == 0:
            return 0.7  # High churn risk if no recent activity
        elif len(recent_transactions) < 5:
            return 0.4  # Moderate churn risk
        else:
            return 0.15  # Low churn risk
    
    def _determine_churn_risk_level(self, churn_probability: Optional[float]) -> Optional[str]:
        """Determine churn risk level.
        
        Args:
            churn_probability: Churn probability
        
        Returns:
            Churn risk level
        """
        if churn_probability is None:
            return None
        elif churn_probability >= 0.7:
            return 'high'
        elif churn_probability >= 0.4:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_clv_metrics(self, customer_key: str) -> Dict[str, Any]:
        """Calculate CLV metrics for a customer.
        
        Args:
            customer_key: Customer key
        
        Returns:
            Dictionary with CLV metrics
        """
        try:
            # Load profitability data for CLV calculation
            profitability_df = self.data_loader.load_customer_profitability(customer_key=customer_key)
            
            # Calculate CLV using CLV analytics
            clv = self._calculate_clv(profitability_df)
            
            # Determine CLV trend (placeholder)
            clv_trend = 'stable'
            
            return {
                'clv': float(clv) if clv is not None else None,
                'clv_trend': clv_trend
            }
            
        except Exception as e:
            logger.error(f"Error calculating CLV metrics for {customer_key}: {e}")
            return {
                'clv': None,
                'clv_trend': None
            }
    
    def _calculate_clv(self, profitability_df: pd.DataFrame) -> Optional[float]:
        """Calculate CLV (placeholder).
        
        Args:
            profitability_df: Profitability data
        
        Returns:
            CLV value
        """
        if profitability_df.empty:
            return None
        
        # Simple CLV calculation: average monthly profit * 12 * 5 years
        total_profit = (
            profitability_df['interest_income'].fillna(0).sum() +
            profitability_df['fee_income'].fillna(0).sum() -
            profitability_df['servicing_cost'].fillna(0).sum() -
            profitability_df['operational_cost'].fillna(0).sum()
        )
        
        avg_monthly_profit = total_profit / len(profitability_df) if len(profitability_df) > 0 else 0
        clv = avg_monthly_profit * 12 * 5  # 5-year projection
        
        return clv
    
    def persist_core_metrics(self, metrics_df: pd.DataFrame) -> None:
        """Persist core metrics to fact_customer_metrics table.
        
        Args:
            metrics_df: DataFrame with core metrics
        """
        logger.info(f"Persisting {len(metrics_df)} core metrics to fact_customer_metrics")
        
        # This would use SQLAlchemy to insert/update the fact table
        # For now, just log the action
        logger.info("Core metrics persistence would be implemented here")
