"""Business-rule based customer segmentation."""

from datetime import date, timedelta
from typing import Dict, Any, List, Optional
import logging

import pandas as pd

from src.customer_segmentation.base import (
    CustomerSegmentationBase,
    SegmentDefinition,
    SegmentationMethod,
)

logger = logging.getLogger(__name__)


class BusinessRuleSegmenter(CustomerSegmentationBase):
    """Segment customers using business rules."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize business rule segmenter.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
        self._define_standard_segments()
    
    def _define_standard_segments(self) -> None:
        """Define standard business-rule segments."""
        segments = [
            # Profitability-based segments
            SegmentDefinition(
                name="high_value",
                description="High value profitable customers",
                method=SegmentationMethod.BUSINESS_RULES,
                criteria={
                    "net_profit_min": 50000,
                    "profit_margin_min": 15
                },
                business_interpretation="Customers with high profitability and healthy margins",
                recommended_actions=["Priority service", "Retention programs", "Cross-sell opportunities"]
            ),
            SegmentDefinition(
                name="medium_value",
                description="Medium value customers",
                method=SegmentationMethod.BUSINESS_RULES,
                criteria={
                    "net_profit_min": 10000,
                    "net_profit_max": 50000,
                    "profit_margin_min": 10
                },
                business_interpretation="Customers with moderate profitability",
                recommended_actions=["Regular monitoring", "Growth programs", "Service optimization"]
            ),
            SegmentDefinition(
                name="low_value",
                description="Low value customers",
                method=SegmentationMethod.BUSINESS_RULES,
                criteria={
                    "net_profit_max": 10000,
                    "profit_margin_min": 5
                },
                business_interpretation="Customers with low profitability",
                recommended_actions=["Cost optimization", "Digital service", "Self-service options"]
            ),
            SegmentDefinition(
                name="unprofitable",
                description="Unprofitable customers",
                method=SegmentationMethod.BUSINESS_RULES,
                criteria={
                    "net_profit_max": 0
                },
                business_interpretation="Customers with negative profitability",
                recommended_actions=["Review relationship", "Fee adjustments", "Exit strategy"]
            ),
            # Behavior-based segments
            SegmentDefinition(
                name="highly_engaged",
                description="Highly engaged customers",
                method=SegmentationMethod.BUSINESS_RULES,
                criteria={
                    "transaction_frequency_min": 10,
                    "product_count_min": 3
                },
                business_interpretation="Customers with high engagement and product usage",
                recommended_actions=["Loyalty programs", "Premium offers", "Advocacy programs"]
            ),
            SegmentDefinition(
                name="moderately_engaged",
                description="Moderately engaged customers",
                method=SegmentationMethod.BUSINESS_RULES,
                criteria={
                    "transaction_frequency_min": 5,
                    "transaction_frequency_max": 10,
                    "product_count_min": 2
                },
                business_interpretation="Customers with moderate engagement",
                recommended_actions=["Engagement programs", "Cross-sell", "Service improvements"]
            ),
            SegmentDefinition(
                name="lowly_engaged",
                description="Lowly engaged customers",
                method=SegmentationMethod.BUSINESS_RULES,
                criteria={
                    "transaction_frequency_max": 5,
                    "product_count_max": 2
                },
                business_interpretation="Customers with low engagement",
                recommended_actions=["Re-engagement campaigns", "Product education", "Incentive programs"]
            ),
            # Lifecycle-based segments
            SegmentDefinition(
                name="new_customer",
                description="New customers",
                method=SegmentationMethod.BUSINESS_RULES,
                criteria={
                    "tenure_max_days": 90
                },
                business_interpretation="Recently acquired customers",
                recommended_actions=["Onboarding programs", "Product introduction", "Relationship building"]
            ),
            SegmentDefinition(
                name="established_customer",
                description="Established customers",
                method=SegmentationMethod.BUSINESS_RULES,
                criteria={
                    "tenure_min_days": 90,
                    "tenure_max_days": 365
                },
                business_interpretation="Customers with established relationship",
                recommended_actions=["Relationship deepening", "Cross-sell", "Loyalty programs"]
            ),
            SegmentDefinition(
                name="long_term_customer",
                description="Long-term customers",
                method=SegmentationMethod.BUSINESS_RULES,
                criteria={
                    "tenure_min_days": 365
                },
                business_interpretation="Long-standing customers",
                recommended_actions=["VIP treatment", "Retention focus", "Advocacy programs"]
            ),
        ]
        
        for segment in segments:
            self.register_segment(segment)
    
    def segment_by_profitability(
        self,
        df: pd.DataFrame,
        profit_column: str = "net_profit",
        margin_column: str = "profit_margin"
    ) -> pd.DataFrame:
        """Segment customers by profitability.
        
        Args:
            df: DataFrame with customer data
            profit_column: Name of profit column
            margin_column: Name of margin column
        
        Returns:
            DataFrame with segment assignments
        """
        df = df.copy()
        
        # Apply profitability rules
        conditions = [
            (df[profit_column] >= 50000) & (df[margin_column] >= 15),
            (df[profit_column] >= 10000) & (df[profit_column] < 50000) & (df[margin_column] >= 10),
            (df[profit_column] >= 0) & (df[profit_column] < 10000) & (df[margin_column] >= 5),
            df[profit_column] < 0
        ]
        segments = ["high_value", "medium_value", "low_value", "unprofitable"]
        
        df["segment"] = "unknown"
        for condition, segment in zip(conditions, segments):
            df.loc[condition, "segment"] = segment
        
        return df
    
    def segment_by_behavior(
        self,
        df: pd.DataFrame,
        frequency_column: str = "transaction_frequency",
        product_count_column: str = "product_count"
    ) -> pd.DataFrame:
        """Segment customers by behavior.
        
        Args:
            df: DataFrame with customer data
            frequency_column: Name of frequency column
            product_count_column: Name of product count column
        
        Returns:
            DataFrame with segment assignments
        """
        df = df.copy()
        
        # Apply behavior rules
        conditions = [
            (df[frequency_column] >= 10) & (df[product_count_column] >= 3),
            (df[frequency_column] >= 5) & (df[frequency_column] < 10) & (df[product_count_column] >= 2),
            (df[frequency_column] < 5) | (df[product_count_column] < 2)
        ]
        segments = ["highly_engaged", "moderately_engaged", "lowly_engaged"]
        
        df["behavior_segment"] = "unknown"
        for condition, segment in zip(conditions, segments):
            df.loc[condition, "behavior_segment"] = segment
        
        return df
    
    def segment_by_lifecycle(
        self,
        df: pd.DataFrame,
        tenure_column: str = "tenure_days"
    ) -> pd.DataFrame:
        """Segment customers by lifecycle stage.
        
        Args:
            df: DataFrame with customer data
            tenure_column: Name of tenure column
        
        Returns:
            DataFrame with segment assignments
        """
        df = df.copy()
        
        # Apply lifecycle rules
        conditions = [
            df[tenure_column] <= 90,
            (df[tenure_column] > 90) & (df[tenure_column] <= 365),
            df[tenure_column] > 365
        ]
        segments = ["new_customer", "established_customer", "long_term_customer"]
        
        df["lifecycle_segment"] = "unknown"
        for condition, segment in zip(conditions, segments):
            df.loc[condition, "lifecycle_segment"] = segment
        
        return df
    
    def segment_combined(
        self,
        df: pd.DataFrame,
        profit_column: str = "net_profit",
        margin_column: str = "profit_margin",
        frequency_column: str = "transaction_frequency",
        product_count_column: str = "product_count",
        tenure_column: str = "tenure_days"
    ) -> pd.DataFrame:
        """Segment customers using combined business rules.
        
        Args:
            df: DataFrame with customer data
            profit_column: Name of profit column
            margin_column: Name of margin column
            frequency_column: Name of frequency column
            product_count_column: Name of product count column
            tenure_column: Name of tenure column
        
        Returns:
            DataFrame with combined segment assignments
        """
        df = df.copy()
        
        # Apply all segmentations
        df = self.segment_by_profitability(df, profit_column, margin_column)
        df = self.segment_by_behavior(df, frequency_column, product_count_column)
        df = self.segment_by_lifecycle(df, tenure_column)
        
        # Create combined segment name
        df["combined_segment"] = (
            df["segment"] + "_" + 
            df["behavior_segment"] + "_" + 
            df["lifecycle_segment"]
        )
        
        return df
