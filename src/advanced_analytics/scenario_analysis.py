"""Scenario Analysis.

This module implements scenario analysis to evaluate portfolio performance
under different economic conditions and stress scenarios.

Key Scenarios:
- Economic downturn
- Interest rate changes
- Unemployment spikes
- Market volatility
- Sector-specific shocks

NOTE: This is an analytical/educational model for decision support.
It does not make actual lending decisions.
"""

from typing import Dict, Any, List, Optional
from datetime import date
from enum import Enum
import logging

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class ScenarioType(Enum):
    """Types of scenarios to analyze."""
    BASELINE = "baseline"
    ECONOMIC_DOWNTURN = "economic_downturn"
    INTEREST_RATE_RISE = "interest_rate_rise"
    UNEMPLOYMENT_SPIKE = "unemployment_spike"
    MARKET_VOLATILITY = "market_volatility"
    SECTOR_SHOCK = "sector_shock"


class ScenarioAnalyzer:
    """Analyze portfolio performance under different scenarios.
    
    This class evaluates how the portfolio would perform under various
    economic stress scenarios.
    
    Assumptions:
    - Scenario parameters are based on historical stress events
    - Customer behavior follows historical patterns under stress
    - Correlations between risk factors are stable
    - Stress events are independent
    
    Limitations:
    - Cannot predict unprecedented events (black swans)
    - Assumes historical patterns will repeat
    - Does not account for policy interventions
    - May overestimate or underestimate actual impact
    
    Fairness Considerations:
    - Analyze scenario impact across demographic groups
    - Check for disparate impact under stress scenarios
    - Ensure stress testing considers vulnerable populations
    - Regular audit for bias in scenario assumptions
    """
    
    def __init__(self):
        """Initialize Scenario Analyzer."""
        # Scenario parameters (configurable)
        self.scenario_parameters = {
            ScenarioType.ECONOMIC_DOWNTURN: {
                'gdp_decline': -0.05,  # 5% GDP decline
                'unemployment_increase': 0.03,  # 3% increase
                'default_rate_multiplier': 2.0,  # 2x default rate
                'profitability_decline': -0.20  # 20% profitability decline
            },
            ScenarioType.INTEREST_RATE_RISE: {
                'rate_increase': 0.02,  # 2% rate increase
                'payment_increase': 0.15,  # 15% payment increase
                'default_rate_multiplier': 1.5,  # 1.5x default rate
                'profitability_decline': -0.10  # 10% profitability decline
            },
            ScenarioType.UNEMPLOYMENT_SPIKE: {
                'unemployment_increase': 0.05,  # 5% increase
                'default_rate_multiplier': 2.5,  # 2.5x default rate
                'profitability_decline': -0.25  # 25% profitability decline
            },
            ScenarioType.MARKET_VOLATILITY: {
                'volatility_increase': 2.0,  # 2x volatility
                'default_rate_multiplier': 1.3,  # 1.3x default rate
                'profitability_decline': -0.15  # 15% profitability decline
            }
        }
    
    def run_scenario_analysis(
        self,
        portfolio_df: pd.DataFrame,
        scenario_type: ScenarioType
    ) -> Dict[str, Any]:
        """Run scenario analysis for a specific scenario.
        
        Args:
            portfolio_df: DataFrame with portfolio data
            scenario_type: Type of scenario to analyze
        
        Returns:
            Dictionary with scenario analysis results
        """
        logger.info(f"Running scenario analysis: {scenario_type.value}")
        
        params = self.scenario_parameters.get(scenario_type, {})
        
        if not params:
            logger.warning(f"No parameters for scenario: {scenario_type.value}")
            return {}
        
        # Calculate baseline metrics
        baseline = self._calculate_baseline_metrics(portfolio_df)
        
        # Apply scenario impacts
        scenario_impact = self._apply_scenario_impact(portfolio_df, params)
        
        # Calculate scenario metrics
        scenario = self._calculate_scenario_metrics(portfolio_df, scenario_impact)
        
        # Calculate impact
        impact = self._calculate_impact(baseline, scenario)
        
        return {
            'scenario_type': scenario_type.value,
            'scenario_parameters': params,
            'baseline': baseline,
            'scenario': scenario,
            'impact': impact,
            'assumptions': [
                f"Scenario based on {scenario_type.value} parameters",
                'Customer behavior follows historical patterns',
                'Correlations between risk factors are stable'
            ],
            'limitations': [
                'Cannot predict unprecedented events',
                'Assumes historical patterns will repeat',
                'Does not account for policy interventions',
                'May overestimate or underestimate actual impact'
            ]
        }
    
    def _calculate_baseline_metrics(self, portfolio_df: pd.DataFrame) -> Dict[str, float]:
        """Calculate baseline portfolio metrics.
        
        Args:
            portfolio_df: DataFrame with portfolio data
        
        Returns:
            Dictionary with baseline metrics
        """
        return {
            'total_exposure': portfolio_df['exposure_amount'].sum() if 'exposure_amount' in portfolio_df.columns else 0,
            'total_profit': portfolio_df['net_profit'].sum() if 'net_profit' in portfolio_df.columns else 0,
            'avg_risk_score': portfolio_df['risk_level'].map({'low': 1, 'medium': 2, 'high': 3, 'critical': 4}).mean() if 'risk_level' in portfolio_df.columns else 2,
            'default_rate': 0.02,  # Placeholder baseline default rate
            'customer_count': len(portfolio_df)
        }
    
    def _apply_scenario_impact(
        self,
        portfolio_df: pd.DataFrame,
        params: Dict[str, float]
    ) -> pd.DataFrame:
        """Apply scenario impact to portfolio.
        
        Args:
            portfolio_df: DataFrame with portfolio data
            params: Scenario parameters
        
        Returns:
            DataFrame with scenario impacts
        """
        impact_df = portfolio_df.copy()
        
        # Apply profitability decline
        if 'profitability_decline' in params and 'net_profit' in impact_df.columns:
            impact_df['scenario_profit'] = impact_df['net_profit'] * (1 + params['profitability_decline'])
        else:
            impact_df['scenario_profit'] = impact_df.get('net_profit', 0)
        
        # Apply default rate multiplier
        if 'default_rate_multiplier' in params:
            impact_df['scenario_default_rate'] = 0.02 * params['default_rate_multiplier']
        else:
            impact_df['scenario_default_rate'] = 0.02
        
        # Apply payment increase (for interest rate scenarios)
        if 'payment_increase' in params:
            impact_df['scenario_payment_increase'] = params['payment_increase']
        else:
            impact_df['scenario_payment_increase'] = 0
        
        return impact_df
    
    def _calculate_scenario_metrics(
        self,
        portfolio_df: pd.DataFrame,
        impact_df: pd.DataFrame
    ) -> Dict[str, float]:
        """Calculate scenario portfolio metrics.
        
        Args:
            portfolio_df: Original portfolio DataFrame
            impact_df: DataFrame with scenario impacts
        
        Returns:
            Dictionary with scenario metrics
        """
        total_exposure = impact_df['exposure_amount'].sum() if 'exposure_amount' in impact_df.columns else 0
        scenario_profit = impact_df['scenario_profit'].sum()
        scenario_default_rate = impact_df['scenario_default_rate'].mean()
        
        # Calculate expected credit loss under scenario
        expected_credit_loss = total_exposure * scenario_default_rate * 0.5  # 50% LGD
        
        return {
            'total_exposure': total_exposure,
            'total_profit': scenario_profit,
            'expected_credit_loss': expected_credit_loss,
            'risk_adjusted_profit': scenario_profit - expected_credit_loss,
            'default_rate': scenario_default_rate,
            'customer_count': len(portfolio_df)
        }
    
    def _calculate_impact(
        self,
        baseline: Dict[str, float],
        scenario: Dict[str, float]
    ) -> Dict[str, Any]:
        """Calculate impact of scenario on portfolio.
        
        Args:
            baseline: Baseline metrics
            scenario: Scenario metrics
        
        Returns:
            Dictionary with impact analysis
        """
        profit_change = scenario['total_profit'] - baseline['total_profit']
        profit_change_pct = (profit_change / baseline['total_profit'] * 100) if baseline['total_profit'] != 0 else 0
        
        default_rate_change = scenario['default_rate'] - baseline['default_rate']
        ecl_change = scenario['expected_credit_loss'] - (baseline['total_exposure'] * baseline['default_rate'] * 0.5)
        
        return {
            'profit_change': profit_change,
            'profit_change_pct': profit_change_pct,
            'default_rate_change': default_rate_change,
            'expected_credit_loss': scenario['expected_credit_loss'],
            'ecl_change': ecl_change,
            'risk_adjusted_profit_change': scenario['risk_adjusted_profit'] - (baseline['total_profit'] - baseline['total_exposure'] * baseline['default_rate'] * 0.5)
        }
    
    def run_all_scenarios(
        self,
        portfolio_df: pd.DataFrame
    ) -> Dict[str, Any]:
        """Run all predefined scenarios.
        
        Args:
            portfolio_df: DataFrame with portfolio data
        
        Returns:
            Dictionary with all scenario results
        """
        logger.info("Running all scenario analyses")
        
        results = {}
        
        for scenario_type in ScenarioType:
            if scenario_type == ScenarioType.BASELINE:
                continue
            
            try:
                scenario_result = self.run_scenario_analysis(portfolio_df, scenario_type)
                results[scenario_type.value] = scenario_result
            except Exception as e:
                logger.error(f"Error running scenario {scenario_type.value}: {e}")
                results[scenario_type.value] = {'error': str(e)}
        
        # Generate summary
        summary = self._generate_scenario_summary(results)
        
        return {
            'scenarios': results,
            'summary': summary,
            'assumptions': [
                'Scenarios based on historical stress events',
                'Customer behavior follows historical patterns',
                'Correlations between risk factors are stable'
            ],
            'limitations': [
                'Cannot predict unprecedented events',
                'Assumes historical patterns will repeat',
                'Does not account for policy interventions',
                'May overestimate or underestimate actual impact'
            ],
            'fairness_considerations': [
                'Analyze scenario impact across demographic groups',
                'Check for disparate impact under stress scenarios',
                'Ensure stress testing considers vulnerable populations',
                'Regular audit for bias in scenario assumptions'
            ]
        }
    
    def _generate_scenario_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of scenario results.
        
        Args:
            results: Dictionary with scenario results
        
        Returns:
            Dictionary with scenario summary
        """
        summary = {
            'worst_case_scenario': None,
            'worst_profit_loss': 0,
            'best_case_scenario': None,
            'best_profit_outcome': float('inf'),
            'avg_profit_change': 0,
            'avg_ecl_increase': 0
        }
        
        profit_changes = []
        ecl_changes = []
        
        for scenario_name, result in results.items():
            if 'error' in result:
                continue
            
            impact = result.get('impact', {})
            profit_change = impact.get('profit_change', 0)
            ecl_change = impact.get('ecl_change', 0)
            
            profit_changes.append(profit_change)
            ecl_changes.append(ecl_change)
            
            if profit_change < summary['worst_profit_loss']:
                summary['worst_profit_loss'] = profit_change
                summary['worst_case_scenario'] = scenario_name
            
            if profit_change < summary['best_profit_outcome']:
                summary['best_profit_outcome'] = profit_change
                summary['best_case_scenario'] = scenario_name
        
        if profit_changes:
            summary['avg_profit_change'] = np.mean(profit_changes)
            summary['avg_ecl_increase'] = np.mean(ecl_changes)
        
        return summary
