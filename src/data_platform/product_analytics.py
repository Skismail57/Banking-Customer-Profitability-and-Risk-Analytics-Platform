"""Product Analytics Platform - Data Platform Integration Layer.

This module provides product-level analytics and serves as the foundation
for product performance insights and cross-sell analysis.

Architecture Position:
Banking Data → Data Platform → Product Analytics → Core Analytics
"""

from typing import Dict, Any, Optional, List
from datetime import date, timedelta
import logging

import pandas as pd

from src.data_platform.data_loader import DataLoader

logger = logging.getLogger(__name__)


class ProductAnalyticsPlatform:
    """Product Analytics Platform for product-level insights.
    
    This class provides comprehensive product analytics including performance,
    adoption, and cross-sell analysis.
    """
    
    def __init__(self, as_of_date: Optional[date] = None, data_loader: Optional[DataLoader] = None):
        """Initialize Product Analytics Platform.
        
        Args:
            as_of_date: As-of date for temporal analysis
            data_loader: Data loader instance (creates default if not provided)
        """
        self.as_of_date = as_of_date or date.today()
        self.data_loader = data_loader or DataLoader()
    
    def get_product_performance(
        self,
        product_keys: Optional[List[str]] = None,
        categories: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Get product performance metrics.
        
        Args:
            product_keys: Optional list of product keys to filter
            categories: Optional list of product categories to filter
        
        Returns:
            DataFrame with product performance metrics
        """
        logger.info("Calculating product performance metrics")
        
        # Load products
        products_df = self.data_loader.load_products(
            product_keys=product_keys,
            categories=categories
        )
        
        if products_df.empty:
            logger.warning("No products found")
            return pd.DataFrame()
        
        # Load customer metrics to get product-level insights
        metrics_df = self.data_loader.load_customer_metrics()
        
        if metrics_df.empty:
            logger.warning("No customer metrics found")
            return products_df
        
        # Aggregate by product (this would require product-level metrics in the schema)
        # For now, return product information with placeholder metrics
        performance_df = products_df.copy()
        
        # Add placeholder performance metrics
        performance_df['customer_count'] = 0  # Would be calculated from actual data
        performance_df['total_balance'] = 0  # Would be calculated from actual data
        performance_df['avg_balance'] = 0  # Would be calculated from actual data
        performance_df['profitability'] = 0  # Would be calculated from actual data
        
        logger.info(f"Product performance calculated for {len(performance_df)} products")
        return performance_df
    
    def get_product_adoption(
        self,
        customer_keys: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Get product adoption by customer.
        
        Args:
            customer_keys: Optional list of customer keys to filter
        
        Returns:
            DataFrame with product adoption data
        """
        logger.info("Calculating product adoption")
        
        # Load customers
        customers_df = self.data_loader.load_customers(customer_keys=customer_keys)
        
        if customers_df.empty:
            logger.warning("No customers found")
            return pd.DataFrame()
        
        # Load accounts and loans to determine product adoption
        adoption_data = []
        
        for customer_key in customers_df['customer_key']:
            accounts_df = self.data_loader.load_accounts(customer_key=customer_key)
            loans_df = self.data_loader.load_loans(customer_key=customer_key)
            
            products_held = set()
            
            if not accounts_df.empty:
                products_held.update(accounts_df['product_key'].tolist())
            
            if not loans_df.empty:
                products_held.update(loans_df['product_key'].tolist())
            
            adoption_data.append({
                'customer_key': customer_key,
                'products_held': list(products_held),
                'product_count': len(products_held)
            })
        
        adoption_df = pd.DataFrame(adoption_data)
        
        logger.info(f"Product adoption calculated for {len(adoption_df)} customers")
        return adoption_df
    
    def get_cross_sell_opportunities(
        self,
        customer_keys: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Identify cross-sell opportunities.
        
        Args:
            customer_keys: Optional list of customer keys to analyze
        
        Returns:
            DataFrame with cross-sell opportunities
        """
        logger.info("Identifying cross-sell opportunities")
        
        # Load all products
        products_df = self.data_loader.load_products(is_active=True)
        
        if products_df.empty:
            logger.warning("No active products found")
            return pd.DataFrame()
        
        # Get product adoption
        adoption_df = self.get_product_adoption(customer_keys=customer_keys)
        
        if adoption_df.empty:
            return pd.DataFrame()
        
        # Identify opportunities (products not held)
        opportunities = []
        
        for _, row in adoption_df.iterrows():
            customer_key = row['customer_key']
            products_held = set(row['products_held'])
            
            for _, product in products_df.iterrows():
                if product['product_key'] not in products_held:
                    opportunities.append({
                        'customer_key': customer_key,
                        'product_key': product['product_key'],
                        'product_name': product['product_name'],
                        'product_category': product['product_category'],
                        'opportunity_type': 'cross_sell'
                    })
        
        opportunities_df = pd.DataFrame(opportunities)
        
        logger.info(f"Identified {len(opportunities_df)} cross-sell opportunities")
        return opportunities_df
    
    def get_product_profitability(
        self,
        product_keys: Optional[List[str]] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> pd.DataFrame:
        """Get product-level profitability.
        
        Args:
            product_keys: Optional list of product keys to filter
            start_date: Optional start date
            end_date: Optional end date
        
        Returns:
            DataFrame with product profitability
        """
        logger.info("Calculating product profitability")
        
        # Load profitability data
        profitability_df = self.data_loader.load_customer_profitability(
            start_date=start_date,
            end_date=end_date
        )
        
        if profitability_df.empty:
            logger.warning("No profitability data found")
            return pd.DataFrame()
        
        # Filter by product keys if provided
        if product_keys:
            profitability_df = profitability_df[
                profitability_df['product_key'].isin(product_keys)
            ]
        
        # Aggregate by product
        product_profitability = profitability_df.groupby('product_key').agg({
            'interest_income': 'sum',
            'fee_income': 'sum',
            'service_charge_income': 'sum',
            'product_revenue': 'sum',
            'servicing_cost': 'sum',
            'operational_cost': 'sum',
            'incentive_cost': 'sum',
            'expected_credit_loss': 'sum'
        }).reset_index()
        
        # Calculate net profit
        product_profitability['net_profit'] = (
            product_profitability['interest_income'] +
            product_profitability['fee_income'] +
            product_profitability['service_charge_income'] +
            product_profitability['product_revenue'] -
            product_profitability['servicing_cost'] -
            product_profitability['operational_cost'] -
            product_profitability['incentive_cost'] -
            product_profitability['expected_credit_loss']
        )
        
        # Load product names
        products_df = self.data_loader.load_products()
        
        if not products_df.empty:
            product_profitability = product_profitability.merge(
                products_df[['product_key', 'product_name', 'product_category']],
                on='product_key',
                how='left'
            )
        
        logger.info(f"Product profitability calculated for {len(product_profitability)} products")
        return product_profitability
