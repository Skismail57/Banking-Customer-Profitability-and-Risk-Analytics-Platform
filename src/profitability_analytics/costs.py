"""Cost calculators for profitability analytics."""

from datetime import date
from typing import Dict, Any, Optional
import logging

import pandas as pd

from src.profitability_analytics.base import (
    ProfitabilityBase,
    ValueType,
    ProfitabilityValue,
)

logger = logging.getLogger(__name__)


class CostCalculator(ProfitabilityBase):
    """Calculate cost components for profitability analysis."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize cost calculator.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
    
    def calculate_servicing_cost(
        self,
        df: pd.DataFrame,
        servicing_cost_column: str = "servicing_cost"
    ) -> ProfitabilityValue:
        """Calculate direct servicing costs.
        
        Args:
            df: DataFrame with servicing cost data
            servicing_cost_column: Name of servicing cost column
        
        Returns:
            ProfitabilityValue with servicing cost
        """
        if servicing_cost_column not in df.columns:
            logger.warning(f"Servicing cost column {servicing_cost_column} not found")
            return ProfitabilityValue(
                value=0.0,
                value_type=ValueType.MISSING,
                source="not_available",
                metadata={"reason": f"Column {servicing_cost_column} not found"}
            )
        
        total_servicing_cost = df[servicing_cost_column].sum()
        
        return ProfitabilityValue(
            value=total_servicing_cost,
            value_type=ValueType.OBSERVED,
            source="transaction_data",
            confidence=1.0,
            metadata={"row_count": len(df)}
        )
    
    def calculate_operational_cost(
        self,
        df: pd.DataFrame,
        allocation_method: str = "proportional_to_revenue",
        total_operational_overhead: Optional[float] = None
    ) -> ProfitabilityValue:
        """Calculate allocated operational costs.
        
        Args:
            df: DataFrame for allocation basis
            allocation_method: Method for allocating operational costs
            total_operational_overhead: Total operational overhead to allocate
        
        Returns:
            ProfitabilityValue with operational cost
        """
        if total_operational_overhead is None:
            logger.warning("Total operational overhead not provided")
            return ProfitabilityValue(
                value=0.0,
                value_type=ValueType.MISSING,
                source="not_available",
                metadata={"reason": "Total operational overhead not provided"}
            )
        
        # This is an estimated allocation
        allocated_cost = total_operational_overhead  # Simplified allocation
        
        return ProfitabilityValue(
            value=allocated_cost,
            value_type=ValueType.ESTIMATED,
            source="allocated",
            confidence=0.6,  # Lower confidence for allocations
            metadata={
                "allocation_method": allocation_method,
                "total_overhead": total_operational_overhead
            }
        )
    
    def calculate_incentive_cost(
        self,
        df: pd.DataFrame,
        incentive_column: str = "incentive_amount"
    ) -> ProfitabilityValue:
        """Calculate incentive and reward costs.
        
        Args:
            df: DataFrame with incentive data
            incentive_column: Name of incentive column
        
        Returns:
            ProfitabilityValue with incentive cost
        """
        if incentive_column not in df.columns:
            logger.warning(f"Incentive column {incentive_column} not found")
            return ProfitabilityValue(
                value=0.0,
                value_type=ValueType.MISSING,
                source="not_available",
                metadata={"reason": f"Column {incentive_column} not found"}
            )
        
        total_incentive_cost = df[incentive_column].sum()
        
        return ProfitabilityValue(
            value=total_incentive_cost,
            value_type=ValueType.OBSERVED,
            source="transaction_data",
            confidence=1.0,
            metadata={"row_count": len(df)}
        )
    
    def calculate_expected_credit_loss(
        self,
        df: pd.DataFrame,
        pd_column: str = "probability_of_default",
        lgd_column: str = "loss_given_default",
        ead_column: str = "exposure_at_default",
        balance_column: str = "current_balance"
    ) -> ProfitabilityValue:
        """Calculate expected credit loss (ECL) using risk model outputs.
        
        Args:
            df: DataFrame with risk data
            pd_column: Probability of default column
            lgd_column: Loss given default column
            ead_column: Exposure at default column
            balance_column: Current balance column (fallback if EAD not available)
        
        Returns:
            ProfitabilityValue with expected credit loss
        """
        # Check if risk model outputs are available
        has_pd = pd_column in df.columns
        has_lgd = lgd_column in df.columns
        has_ead = ead_column in df.columns
        has_balance = balance_column in df.columns
        
        if not (has_pd and has_lgd and (has_ead or has_balance)):
            logger.warning("Insufficient risk data for ECL calculation")
            return ProfitabilityValue(
                value=0.0,
                value_type=ValueType.MISSING,
                source="not_available",
                metadata={
                    "reason": "Insufficient risk data",
                    "has_pd": has_pd,
                    "has_lgd": has_lgd,
                    "has_ead": has_ead,
                    "has_balance": has_balance
                }
            )
        
        # Calculate ECL: ECL = PD * LGD * EAD
        df_calc = df.copy()
        
        # Use EAD if available, otherwise use balance
        exposure_column = ead_column if has_ead else balance_column
        
        df_calc["ecl"] = df_calc[pd_column] * df_calc[lgd_column] * df_calc[exposure_column]
        
        total_ecl = df_calc["ecl"].sum()
        
        return ProfitabilityValue(
            value=total_ecl,
            value_type=ValueType.MODELED,
            source="risk_model",
            confidence=0.7,  # Model-based, moderate confidence
            metadata={
                "calculation_method": "PD * LGD * EAD",
                "row_count": len(df_calc),
                "uses_ead": has_ead,
                "uses_balance_fallback": not has_ead and has_balance
            }
        )
    
    def calculate_total_cost(
        self,
        servicing_cost: Optional[ProfitabilityValue] = None,
        operational_cost: Optional[ProfitabilityValue] = None,
        incentive_cost: Optional[ProfitabilityValue] = None,
        expected_credit_loss: Optional[ProfitabilityValue] = None
    ) -> ProfitabilityValue:
        """Calculate total cost from all components.
        
        Args:
            servicing_cost: Servicing cost value
            operational_cost: Operational cost value
            incentive_cost: Incentive cost value
            expected_credit_loss: Expected credit loss value
        
        Returns:
            ProfitabilityValue with total cost
        """
        components = {
            "servicing_cost": servicing_cost,
            "operational_cost": operational_cost,
            "incentive_cost": incentive_cost,
            "expected_credit_loss": expected_credit_loss
        }
        
        # Sum available components
        total_cost = 0.0
        available_components = []
        missing_components = []
        
        for name, value in components.items():
            if value is not None and value.value_type != ValueType.MISSING:
                total_cost += value.value
                available_components.append(name)
            else:
                missing_components.append(name)
        
        # Determine value type based on components
        if len(available_components) == 0:
            value_type = ValueType.MISSING
            confidence = 0.0
        elif len(missing_components) == 0:
            # If all components are observed, total is observed
            all_observed = all(c.value_type == ValueType.OBSERVED for c in components.values() if c is not None)
            value_type = ValueType.OBSERVED if all_observed else ValueType.ESTIMATED
            confidence = 1.0 if all_observed else 0.8
        else:
            value_type = ValueType.ESTIMATED
            # Confidence based on proportion of available components
            confidence = len(available_components) / len(components)
        
        return ProfitabilityValue(
            value=total_cost,
            value_type=value_type,
            source="calculated",
            confidence=confidence,
            metadata={
                "available_components": available_components,
                "missing_components": missing_components,
                "component_count": len(available_components)
            }
        )
    
    def calculate_cost_breakdown(
        self,
        df: pd.DataFrame,
        columns: Dict[str, str],
        total_operational_overhead: Optional[float] = None
    ) -> Dict[str, ProfitabilityValue]:
        """Calculate breakdown of all cost components.
        
        Args:
            df: DataFrame with cost data
            columns: Dictionary mapping component names to column names
            total_operational_overhead: Total operational overhead for allocation
        
        Returns:
            Dictionary of ProfitabilityValues for each component
        """
        breakdown = {}
        
        # Calculate individual components
        if "servicing_cost" in columns:
            breakdown["servicing_cost"] = self.calculate_servicing_cost(df, columns["servicing_cost"])
        
        if "operational_cost" in columns or total_operational_overhead is not None:
            breakdown["operational_cost"] = self.calculate_operational_cost(
                df, total_operational_overhead=total_operational_overhead
            )
        
        if "incentive_cost" in columns:
            breakdown["incentive_cost"] = self.calculate_incentive_cost(df, columns["incentive_cost"])
        
        # Calculate ECL from risk columns
        risk_columns = {
            "pd_column": columns.get("probability_of_default"),
            "lgd_column": columns.get("loss_given_default"),
            "ead_column": columns.get("exposure_at_default"),
            "balance_column": columns.get("current_balance")
        }
        if any(risk_columns.values()):
            breakdown["expected_credit_loss"] = self.calculate_expected_credit_loss(
                df, **{k: v for k, v in risk_columns.items() if v is not None}
            )
        
        # Calculate total cost
        breakdown["total_cost"] = self.calculate_total_cost(
            servicing_cost=breakdown.get("servicing_cost"),
            operational_cost=breakdown.get("operational_cost"),
            incentive_cost=breakdown.get("incentive_cost"),
            expected_credit_loss=breakdown.get("expected_credit_loss")
        )
        
        return breakdown
