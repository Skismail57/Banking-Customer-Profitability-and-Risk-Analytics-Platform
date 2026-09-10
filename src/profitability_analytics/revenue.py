"""Revenue calculators for profitability analytics."""

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


class RevenueCalculator(ProfitabilityBase):
    """Calculate revenue components for profitability analysis."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize revenue calculator.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
    
    def calculate_interest_income(
        self,
        df: pd.DataFrame,
        interest_column: str = "interest_accrued"
    ) -> ProfitabilityValue:
        """Calculate interest income from loan and deposit products.
        
        Args:
            df: DataFrame with interest data
            interest_column: Name of interest column
        
        Returns:
            ProfitabilityValue with interest income
        """
        if interest_column not in df.columns:
            logger.warning(f"Interest column {interest_column} not found")
            return ProfitabilityValue(
                value=0.0,
                value_type=ValueType.MISSING,
                source="not_available",
                metadata={"reason": f"Column {interest_column} not found"}
            )
        
        total_interest = df[interest_column].sum()
        
        return ProfitabilityValue(
            value=total_interest,
            value_type=ValueType.OBSERVED,
            source="transaction_data",
            confidence=1.0,
            metadata={"row_count": len(df)}
        )
    
    def calculate_fee_income(
        self,
        df: pd.DataFrame,
        fee_column: str = "fee_amount"
    ) -> ProfitabilityValue:
        """Calculate fee income from various services.
        
        Args:
            df: DataFrame with fee data
            fee_column: Name of fee column
        
        Returns:
            ProfitabilityValue with fee income
        """
        if fee_column not in df.columns:
            logger.warning(f"Fee column {fee_column} not found")
            return ProfitabilityValue(
                value=0.0,
                value_type=ValueType.MISSING,
                source="not_available",
                metadata={"reason": f"Column {fee_column} not found"}
            )
        
        total_fees = df[fee_column].sum()
        
        return ProfitabilityValue(
            value=total_fees,
            value_type=ValueType.OBSERVED,
            source="transaction_data",
            confidence=1.0,
            metadata={"row_count": len(df)}
        )
    
    def calculate_service_charge_income(
        self,
        df: pd.DataFrame,
        service_charge_column: str = "service_charge"
    ) -> ProfitabilityValue:
        """Calculate service charge income.
        
        Args:
            df: DataFrame with service charge data
            service_charge_column: Name of service charge column
        
        Returns:
            ProfitabilityValue with service charge income
        """
        if service_charge_column not in df.columns:
            logger.warning(f"Service charge column {service_charge_column} not found")
            return ProfitabilityValue(
                value=0.0,
                value_type=ValueType.MISSING,
                source="not_available",
                metadata={"reason": f"Column {service_charge_column} not found"}
            )
        
        total_service_charges = df[service_charge_column].sum()
        
        return ProfitabilityValue(
            value=total_service_charges,
            value_type=ValueType.OBSERVED,
            source="transaction_data",
            confidence=1.0,
            metadata={"row_count": len(df)}
        )
    
    def calculate_product_revenue(
        self,
        df: pd.DataFrame,
        product_revenue_column: str = "product_revenue"
    ) -> ProfitabilityValue:
        """Calculate product-specific revenue.
        
        Args:
            df: DataFrame with product revenue data
            product_revenue_column: Name of product revenue column
        
        Returns:
            ProfitabilityValue with product revenue
        """
        if product_revenue_column not in df.columns:
            logger.warning(f"Product revenue column {product_revenue_column} not found")
            return ProfitabilityValue(
                value=0.0,
                value_type=ValueType.MISSING,
                source="not_available",
                metadata={"reason": f"Column {product_revenue_column} not found"}
            )
        
        total_product_revenue = df[product_revenue_column].sum()
        
        return ProfitabilityValue(
            value=total_product_revenue,
            value_type=ValueType.OBSERVED,
            source="transaction_data",
            confidence=1.0,
            metadata={"row_count": len(df)}
        )
    
    def calculate_gross_revenue(
        self,
        interest_income: Optional[ProfitabilityValue] = None,
        fee_income: Optional[ProfitabilityValue] = None,
        service_charge_income: Optional[ProfitabilityValue] = None,
        product_revenue: Optional[ProfitabilityValue] = None
    ) -> ProfitabilityValue:
        """Calculate gross revenue from all components.
        
        Args:
            interest_income: Interest income value
            fee_income: Fee income value
            service_charge_income: Service charge income value
            product_revenue: Product revenue value
        
        Returns:
            ProfitabilityValue with gross revenue
        """
        components = {
            "interest_income": interest_income,
            "fee_income": fee_income,
            "service_charge_income": service_charge_income,
            "product_revenue": product_revenue
        }
        
        # Sum available components
        total_revenue = 0.0
        available_components = []
        missing_components = []
        
        for name, value in components.items():
            if value is not None and value.value_type != ValueType.MISSING:
                total_revenue += value.value
                available_components.append(name)
            else:
                missing_components.append(name)
        
        # Determine value type based on components
        if len(available_components) == 0:
            value_type = ValueType.MISSING
            confidence = 0.0
        elif len(missing_components) == 0:
            value_type = ValueType.OBSERVED
            confidence = 1.0
        else:
            value_type = ValueType.ESTIMATED
            # Confidence based on proportion of available components
            confidence = len(available_components) / len(components)
        
        return ProfitabilityValue(
            value=total_revenue,
            value_type=value_type,
            source="calculated",
            confidence=confidence,
            metadata={
                "available_components": available_components,
                "missing_components": missing_components,
                "component_count": len(available_components)
            }
        )
    
    def calculate_revenue_breakdown(
        self,
        df: pd.DataFrame,
        columns: Dict[str, str]
    ) -> Dict[str, ProfitabilityValue]:
        """Calculate breakdown of all revenue components.
        
        Args:
            df: DataFrame with revenue data
            columns: Dictionary mapping component names to column names
                   e.g., {"interest_income": "interest_accrued", "fee_income": "fee_amount"}
        
        Returns:
            Dictionary of ProfitabilityValues for each component
        """
        breakdown = {}
        
        # Calculate individual components
        if "interest_income" in columns:
            breakdown["interest_income"] = self.calculate_interest_income(df, columns["interest_income"])
        
        if "fee_income" in columns:
            breakdown["fee_income"] = self.calculate_fee_income(df, columns["fee_income"])
        
        if "service_charge_income" in columns:
            breakdown["service_charge_income"] = self.calculate_service_charge_income(
                df, columns["service_charge_income"]
            )
        
        if "product_revenue" in columns:
            breakdown["product_revenue"] = self.calculate_product_revenue(df, columns["product_revenue"])
        
        # Calculate gross revenue
        breakdown["gross_revenue"] = self.calculate_gross_revenue(
            interest_income=breakdown.get("interest_income"),
            fee_income=breakdown.get("fee_income"),
            service_charge_income=breakdown.get("service_charge_income"),
            product_revenue=breakdown.get("product_revenue")
        )
        
        return breakdown
