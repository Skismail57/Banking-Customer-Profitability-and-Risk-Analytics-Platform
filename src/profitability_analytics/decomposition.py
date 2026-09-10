"""Customer Profitability Decomposition.

This module decomposes customer profitability into its component parts to understand
the drivers of profitability and identify opportunities for improvement.

Key Decomposition Dimensions:
- Revenue decomposition (interest, fees, service charges)
- Cost decomposition (servicing, operational, incentive, expected credit loss)
- Product-level profitability
- Segment-level profitability
- Risk-adjusted profitability

NOTE: This is an analytical/educational model for decision support.
It does not make actual lending decisions.
"""

from typing import Dict, Any, List, Optional
from datetime import date
import logging

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class ProfitabilityDecomposer:
    """Decompose customer profitability into component parts.
    
    This class provides detailed breakdowns of profitability to understand
    what drives customer value and where improvements can be made.
    
    Assumptions:
    - Profitability data is available at the customer and product level
    - Cost allocation rules are consistent across customers
    - Expected credit loss calculations are based on risk models
    
    Limitations:
    - Cost allocation may not be perfectly accurate
    - Does not account for indirect costs
    - Expected credit loss is a model estimate
    - May not capture all revenue and cost components
    
    Fairness Considerations:
    - Analyze profitability decomposition across demographic groups
    - Check for disparate impact in cost allocation
    - Ensure profitability metrics are not biased
    - Regular audit for bias in profitability assessment
    """
    
    def decompose_customer_profitability(
        self,
        profitability_df: pd.DataFrame,
        customer_key: str
    ) -> Dict[str, Any]:
        """Decompose profitability for a single customer.
        
        Args:
            profitability_df: DataFrame with profitability data
            customer_key: Customer key to analyze
        
        Returns:
            Dictionary with profitability decomposition
        """
        customer_profit = profitability_df[profitability_df['customer_key'] == customer_key]
        
        if customer_profit.empty:
            return {'error': 'Customer not found'}
        
        # Aggregate across all products
        revenue_components = {
            'interest_income': customer_profit['interest_income'].fillna(0).sum(),
            'fee_income': customer_profit['fee_income'].fillna(0).sum(),
            'service_charge_income': customer_profit['service_charge_income'].fillna(0).sum(),
            'product_revenue': customer_profit['product_revenue'].fillna(0).sum()
        }
        
        cost_components = {
            'servicing_cost': customer_profit['servicing_cost'].fillna(0).sum(),
            'operational_cost': customer_profit['operational_cost'].fillna(0).sum(),
            'incentive_cost': customer_profit['incentive_cost'].fillna(0).sum(),
            'expected_credit_loss': customer_profit['expected_credit_loss'].fillna(0).sum()
        }
        
        total_revenue = sum(revenue_components.values())
        total_cost = sum(cost_components.values())
        net_profit = total_revenue - total_cost
        
        # Calculate percentages
        revenue_pct = {k: (v / total_revenue * 100) if total_revenue > 0 else 0 for k, v in revenue_components.items()}
        cost_pct = {k: (v / total_cost * 100) if total_cost > 0 else 0 for k, v in cost_components.items()}
        
        return {
            'customer_key': customer_key,
            'revenue_components': revenue_components,
            'cost_components': cost_components,
            'total_revenue': float(total_revenue),
            'total_cost': float(total_cost),
            'net_profit': float(net_profit),
            'profit_margin': float((net_profit / total_revenue * 100) if total_revenue > 0 else 0),
            'revenue_pct': revenue_pct,
            'cost_pct': cost_pct,
            'product_breakdown': self._decompose_by_product(customer_profit)
        }
    
    def _decompose_by_product(self, customer_profit: pd.DataFrame) -> List[Dict[str, Any]]:
        """Decompose profitability by product.
        
        Args:
            customer_profit: DataFrame with customer profitability data
        
        Returns:
            List of product-level profitability breakdowns
        """
        product_breakdown = []
        
        for _, row in customer_profit.iterrows():
            revenue = (
                row.get('interest_income', 0) +
                row.get('fee_income', 0) +
                row.get('service_charge_income', 0) +
                row.get('product_revenue', 0)
            )
            cost = (
                row.get('servicing_cost', 0) +
                row.get('operational_cost', 0) +
                row.get('incentive_cost', 0) +
                row.get('expected_credit_loss', 0)
            )
            
            product_breakdown.append({
                'product_key': row.get('product_key'),
                'revenue': float(revenue),
                'cost': float(cost),
                'net_profit': float(revenue - cost),
                'profit_margin': float(((revenue - cost) / revenue * 100) if revenue > 0 else 0)
            })
        
        return product_breakdown
    
    def decompose_segment_profitability(
        self,
        profitability_df: pd.DataFrame,
        metrics_df: pd.DataFrame
    ) -> Dict[str, Any]:
        """Decompose profitability by segment.
        
        Args:
            profitability_df: DataFrame with profitability data
            metrics_df: DataFrame with customer metrics (for segment info)
        
        Returns:
            Dictionary with segment profitability decomposition
        """
        # Merge profitability with segment info
        merged_df = profitability_df.merge(
            metrics_df[['customer_key', 'segment']],
            on='customer_key',
            how='left'
        )
        
        segment_decomposition = {}
        
        for segment in merged_df['segment'].unique():
            segment_data = merged_df[merged_df['segment'] == segment]
            
            revenue_components = {
                'interest_income': segment_data['interest_income'].fillna(0).sum(),
                'fee_income': segment_data['fee_income'].fillna(0).sum(),
                'service_charge_income': segment_data['service_charge_income'].fillna(0).sum(),
                'product_revenue': segment_data['product_revenue'].fillna(0).sum()
            }
            
            cost_components = {
                'servicing_cost': segment_data['servicing_cost'].fillna(0).sum(),
                'operational_cost': segment_data['operational_cost'].fillna(0).sum(),
                'incentive_cost': segment_data['incentive_cost'].fillna(0).sum(),
                'expected_credit_loss': segment_data['expected_credit_loss'].fillna(0).sum()
            }
            
            total_revenue = sum(revenue_components.values())
            total_cost = sum(cost_components.values())
            net_profit = total_revenue - total_cost
            
            segment_decomposition[segment] = {
                'revenue_components': {k: float(v) for k, v in revenue_components.items()},
                'cost_components': {k: float(v) for k, v in cost_components.items()},
                'total_revenue': float(total_revenue),
                'total_cost': float(total_cost),
                'net_profit': float(net_profit),
                'profit_margin': float((net_profit / total_revenue * 100) if total_revenue > 0 else 0),
                'customer_count': len(segment_data['customer_key'].unique())
            }
        
        return segment_decomposition
    
    def calculate_risk_adjusted_profitability(
        self,
        profitability_df: pd.DataFrame,
        metrics_df: pd.DataFrame
    ) -> pd.DataFrame:
        """Calculate risk-adjusted profitability for customers.
        
        Args:
            profitability_df: DataFrame with profitability data
            metrics_df: DataFrame with customer metrics (for risk info)
        
        Returns:
            DataFrame with risk-adjusted profitability
        """
        # Merge profitability with risk metrics
        merged_df = profitability_df.merge(
            metrics_df[['customer_key', 'risk_level', 'churn_probability']],
            on='customer_key',
            how='left'
        )
        
        # Define risk adjustment factors
        risk_factors = {'low': 1.0, 'medium': 0.95, 'high': 0.85, 'critical': 0.70}
        
        # Calculate risk-adjusted profit
        results = []
        
        for _, row in merged_df.iterrows():
            revenue = (
                row.get('interest_income', 0) +
                row.get('fee_income', 0) +
                row.get('service_charge_income', 0) +
                row.get('product_revenue', 0)
            )
            cost = (
                row.get('servicing_cost', 0) +
                row.get('operational_cost', 0) +
                row.get('incentive_cost', 0) +
                row.get('expected_credit_loss', 0)
            )
            
            net_profit = revenue - cost
            risk_level = row.get('risk_level', 'medium')
            risk_factor = risk_factors.get(risk_level, 0.95)
            
            risk_adjusted_profit = net_profit * risk_factor
            
            results.append({
                'customer_key': row['customer_key'],
                'net_profit': float(net_profit),
                'risk_level': risk_level,
                'risk_factor': risk_factor,
                'risk_adjusted_profit': float(risk_adjusted_profit),
                'profit_adjustment': float(risk_adjusted_profit - net_profit)
            })
        
        return pd.DataFrame(results)
    
    def analyze_profitability_drivers(
        self,
        profitability_df: pd.DataFrame
    ) -> Dict[str, Any]:
        """Analyze the key drivers of profitability across the portfolio.
        
        Args:
            profitability_df: DataFrame with profitability data
        
        Returns:
            Dictionary with profitability driver analysis
        """
        # Calculate totals
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
        
        # Calculate driver contributions
        revenue_drivers = {
            'interest_income': float(profitability_df['interest_income'].fillna(0).sum()),
            'fee_income': float(profitability_df['fee_income'].fillna(0).sum()),
            'service_charge_income': float(profitability_df['service_charge_income'].fillna(0).sum()),
            'product_revenue': float(profitability_df['product_revenue'].fillna(0).sum())
        }
        
        cost_drivers = {
            'servicing_cost': float(profitability_df['servicing_cost'].fillna(0).sum()),
            'operational_cost': float(profitability_df['operational_cost'].fillna(0).sum()),
            'incentive_cost': float(profitability_df['incentive_cost'].fillna(0).sum()),
            'expected_credit_loss': float(profitability_df['expected_credit_loss'].fillna(0).sum())
        }
        
        # Calculate percentages
        revenue_pct = {k: (v / total_revenue * 100) if total_revenue > 0 else 0 for k, v in revenue_drivers.items()}
        cost_pct = {k: (v / total_cost * 100) if total_cost > 0 else 0 for k, v in cost_drivers.items()}
        
        # Identify top drivers
        top_revenue_driver = max(revenue_drivers.items(), key=lambda x: x[1])
        top_cost_driver = max(cost_drivers.items(), key=lambda x: x[1])
        
        return {
            'total_revenue': float(total_revenue),
            'total_cost': float(total_cost),
            'net_profit': float(net_profit),
            'profit_margin': float((net_profit / total_revenue * 100) if total_revenue > 0 else 0),
            'revenue_drivers': revenue_drivers,
            'cost_drivers': cost_drivers,
            'revenue_pct': revenue_pct,
            'cost_pct': cost_pct,
            'top_revenue_driver': top_revenue_driver,
            'top_cost_driver': top_cost_driver,
            'insights': [
                f"Top revenue driver: {top_revenue_driver[0]} (${top_revenue_driver[1]:,.2f}, {revenue_pct[top_revenue_driver[0]]:.1f}%)",
                f"Top cost driver: {top_cost_driver[0]} (${top_cost_driver[1]:,.2f}, {cost_pct[top_cost_driver[0]]:.1f}%)",
                f"Expected credit loss accounts for {cost_pct['expected_credit_loss']:.1f}% of total costs"
            ],
            'assumptions': [
                'Cost allocation rules are consistent',
                'Expected credit loss based on risk models',
                'Revenue components are mutually exclusive'
            ],
            'limitations': [
                'Cost allocation may not be perfectly accurate',
                'Does not account for indirect costs',
                'Expected credit loss is a model estimate'
            ],
            'fairness_considerations': [
                'Analyze profitability drivers across demographic groups',
                'Check for disparate impact in cost allocation',
                'Ensure profitability metrics are not biased',
                'Regular audit for bias in profitability assessment'
            ]
        }
