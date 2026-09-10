"""Customer risk migration analysis.

This module implements a comprehensive risk migration matrix that tracks
how customers move between risk levels over time. This is critical for:
- Portfolio risk monitoring
- Capital planning
- Stress testing
- Regulatory reporting (e.g., Basel III)

NOTE: This is an analytical/educational model for decision support.
It does not make actual lending decisions.
"""

from typing import Dict, Any, List, Optional
from datetime import date, timedelta
import logging

import pandas as pd
import numpy as np

from src.advanced_risk_analytics.base import RiskBase, RiskLevel

logger = logging.getLogger(__name__)


class CustomerRiskMigration(RiskBase):
    """Analyze customer risk migration over time.
    
    This class implements a risk migration matrix that shows how customers
    transition between risk levels (low, medium, high, critical) over time.
    
    Assumptions:
    - Risk levels are calculated based on credit utilization and days past due
    - Historical data is available for multiple periods
    - Risk definitions are consistent over time
    
    Limitations:
    - Does not account for external economic factors
    - Assumes risk level transitions are independent
    - May not capture sudden risk events (e.g., job loss, medical emergency)
    - Based on historical patterns which may not predict future migrations
    
    Fairness Considerations:
    - Risk scoring should be regularly audited for bias
    - Consider demographic parity in risk level distributions
    - Ensure equal access to credit improvement opportunities
    """
    
    def analyze_risk_migration(
        self,
        df: pd.DataFrame,
        customer_column: str = "customer_key",
        date_column: str = "as_of_date",
        utilization_column: str = "credit_utilization",
        dpd_column: str = "days_past_due"
    ) -> Dict[str, Any]:
        """Analyze risk migration for a customer over time.
        
        Args:
            df: DataFrame with customer risk data
            customer_column: Name of customer column
            date_column: Name of date column
            utilization_column: Name of utilization column
            dpd_column: Name of DPD column
        
        Returns:
            Dictionary with risk migration analysis
        """
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])
        df = df.sort_values(date_column)
        
        # Calculate risk level for each period
        risk_levels = []
        for _, row in df.iterrows():
            risk_level = self.determine_risk_level(
                utilization=row[utilization_column],
                dpd=row[dpd_column]
            )
            risk_levels.append(risk_level.value)
        
        df["risk_level"] = risk_levels
        
        # Identify transitions
        transitions = []
        for i in range(1, len(df)):
            if df["risk_level"].iloc[i] != df["risk_level"].iloc[i-1]:
                transitions.append({
                    "from": df["risk_level"].iloc[i-1],
                    "to": df["risk_level"].iloc[i],
                    "date": df[date_column].iloc[i].isoformat()
                })
        
        # Count transitions by type
        transition_counts = {}
        for transition in transitions:
            key = f"{transition['from']} -> {transition['to']}"
            transition_counts[key] = transition_counts.get(key, 0) + 1
        
        return {
            "current_risk_level": df["risk_level"].iloc[-1] if len(df) > 0 else None,
            "initial_risk_level": df["risk_level"].iloc[0] if len(df) > 0 else None,
            "transitions": transitions,
            "transition_counts": transition_counts,
            "total_transitions": len(transitions)
        }
    
    def generate_migration_matrix(
        self,
        metrics_df: pd.DataFrame,
        from_date: date,
        to_date: date,
        customer_column: str = "customer_key"
    ) -> pd.DataFrame:
        """Generate a risk migration matrix for the portfolio.
        
        The migration matrix shows the probability of customers moving from
        one risk level to another over a specified time period.
        
        Args:
            metrics_df: DataFrame with customer metrics over time
            from_date: Start date for migration analysis
            to_date: End date for migration analysis
            customer_column: Name of customer column
        
        Returns:
            DataFrame with migration matrix (rows = from_risk, cols = to_risk)
        """
        logger.info(f"Generating migration matrix from {from_date} to {to_date}")
        
        # Get risk levels at from_date
        from_risk = metrics_df[metrics_df['as_of_date'] == from_date][
            [customer_column, 'risk_level']
        ].copy()
        from_risk.columns = [customer_column, 'from_risk']
        
        # Get risk levels at to_date
        to_risk = metrics_df[metrics_df['as_of_date'] == to_date][
            [customer_column, 'risk_level']
        ].copy()
        to_risk.columns = [customer_column, 'to_risk']
        
        # Merge to get transitions
        transitions = from_risk.merge(to_risk, on=customer_column, how='inner')
        
        if transitions.empty:
            logger.warning("No matching customers for migration matrix")
            return pd.DataFrame()
        
        # Count transitions
        migration_counts = transitions.groupby(['from_risk', 'to_risk']).size().unstack(fill_value=0)
        
        # Convert to probabilities (row-normalized)
        migration_matrix = migration_counts.div(migration_counts.sum(axis=1), axis=0)
        
        logger.info(f"Migration matrix generated with shape {migration_matrix.shape}")
        return migration_matrix
    
    def calculate_migration_rates(
        self,
        migration_matrix: pd.DataFrame
    ) -> Dict[str, Any]:
        """Calculate migration rate metrics.
        
        Args:
            migration_matrix: Migration matrix from generate_migration_matrix
        
        Returns:
            Dictionary with migration rate metrics
        """
        if migration_matrix.empty:
            return {}
        
        metrics = {}
        
        # Upgrade rate (moving to better risk level)
        upgrade_rate = 0
        # Downgrade rate (moving to worse risk level)
        downgrade_rate = 0
        # Stability rate (staying in same risk level)
        stability_rate = 0
        
        risk_order = ['low', 'medium', 'high', 'critical']
        
        for from_risk in migration_matrix.index:
            for to_risk in migration_matrix.columns:
                probability = migration_matrix.loc[from_risk, to_risk]
                
                from_idx = risk_order.index(from_risk)
                to_idx = risk_order.index(to_risk)
                
                if to_idx < from_idx:
                    upgrade_rate += probability
                elif to_idx > from_idx:
                    downgrade_rate += probability
                else:
                    stability_rate += probability
        
        # Average across all risk levels
        num_risk_levels = len(migration_matrix.index)
        metrics['avg_upgrade_rate'] = upgrade_rate / num_risk_levels
        metrics['avg_downgrade_rate'] = downgrade_rate / num_risk_levels
        metrics['avg_stability_rate'] = stability_rate / num_risk_levels
        
        # Worst-case migration (to critical)
        metrics['to_critical_rate'] = migration_matrix.get('critical', pd.Series()).mean()
        
        # Best-case migration (to low)
        metrics['to_low_rate'] = migration_matrix.get('low', pd.Series()).mean()
        
        return metrics
    
    def identify_risk_migrators(
        self,
        metrics_df: pd.DataFrame,
        from_date: date,
        to_date: date,
        migration_type: str = "downgrade",
        customer_column: str = "customer_key"
    ) -> pd.DataFrame:
        """Identify customers with specific risk migrations.
        
        Args:
            metrics_df: DataFrame with customer metrics over time
            from_date: Start date
            to_date: End date
            migration_type: Type of migration to identify (upgrade, downgrade, any)
            customer_column: Name of customer column
        
        Returns:
            DataFrame with customers who had the specified migration
        """
        # Get risk levels at both dates
        from_risk = metrics_df[metrics_df['as_of_date'] == from_date][
            [customer_column, 'risk_level']
        ].copy()
        from_risk.columns = [customer_column, 'from_risk']
        
        to_risk = metrics_df[metrics_df['as_of_date'] == to_date][
            [customer_column, 'risk_level']
        ].copy()
        to_risk.columns = [customer_column, 'to_risk']
        
        # Merge
        transitions = from_risk.merge(to_risk, on=customer_column, how='inner')
        
        if transitions.empty:
            return pd.DataFrame()
        
        # Define risk order
        risk_order = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
        
        # Calculate migration direction
        transitions['from_score'] = transitions['from_risk'].map(risk_order)
        transitions['to_score'] = transitions['to_risk'].map(risk_order)
        transitions['migration'] = transitions['to_score'] - transitions['from_score']
        
        # Filter by migration type
        if migration_type == "upgrade":
            migrators = transitions[transitions['migration'] < 0]
        elif migration_type == "downgrade":
            migrators = transitions[transitions['migration'] > 0]
        else:
            migrators = transitions[transitions['migration'] != 0]
        
        return migrators
    
    def calculate_expected_credit_loss_migration(
        self,
        migration_matrix: pd.DataFrame,
        exposure_by_risk: Dict[str, float],
        lgd_by_risk: Dict[str, float]
    ) -> Dict[str, Any]:
        """Calculate expected credit loss considering risk migration.
        
        This implements a simplified version of the Basel III migration approach.
        
        Args:
            migration_matrix: Migration matrix
            exposure_by_risk: Exposure amount by risk level
            lgd_by_risk: Loss given default by risk level
        
        Returns:
            Dictionary with ECL calculation
        """
        risk_levels = ['low', 'medium', 'high', 'critical']
        
        total_ecl = 0
        ecl_by_risk = {}
        
        for from_risk in risk_levels:
            if from_risk not in migration_matrix.index:
                continue
            
            from_exposure = exposure_by_risk.get(from_risk, 0)
            
            for to_risk in risk_levels:
                if to_risk not in migration_matrix.columns:
                    continue
                
                migration_prob = migration_matrix.loc[from_risk, to_risk]
                lgd = lgd_by_risk.get(to_risk, 0.5)  # Default 50% LGD
                
                # Assume only critical risk level defaults
                if to_risk == 'critical':
                    ecl = from_exposure * migration_prob * lgd
                    total_ecl += ecl
        
        return {
            'total_expected_credit_loss': total_ecl,
            'ecl_by_risk': ecl_by_risk,
            'assumptions': [
                'Migration matrix based on historical patterns',
                'Loss given default by risk level',
                'Only critical risk level assumed to default',
                'Simplified Basel III approach'
            ],
            'limitations': [
                'Does not account for correlation between defaults',
                'Assumes independence of migrations',
                'Historical patterns may not predict future',
                'Economic conditions not considered'
            ]
        }
