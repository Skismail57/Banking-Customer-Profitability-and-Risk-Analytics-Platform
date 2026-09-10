"""Segment profiling and business interpretation."""

from datetime import date
from typing import Dict, Any, List, Optional
import logging

import pandas as pd
import numpy as np

from src.customer_segmentation.base import (
    CustomerSegmentationBase,
    SegmentProfile,
)

logger = logging.getLogger(__name__)


class SegmentProfiler(CustomerSegmentationBase):
    """Profile customer segments for business interpretation."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize segment profiler.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
    
    def profile_segment(
        self,
        df: pd.DataFrame,
        cluster_label: int,
        feature_columns: List[str],
        segment_name: Optional[str] = None
    ) -> SegmentProfile:
        """Profile a single segment.
        
        Args:
            df: DataFrame with customer data and cluster labels
            cluster_label: Cluster label to profile
            feature_columns: List of feature columns to profile
            segment_name: Optional name for the segment
        
        Returns:
            SegmentProfile with segment characteristics
        """
        segment_df = df[df["cluster"] == cluster_label]
        
        if segment_name is None:
            segment_name = f"segment_{cluster_label}"
        
        # Calculate characteristics
        characteristics = {}
        for col in feature_columns:
            if col in segment_df.columns:
                characteristics[col] = {
                    "mean": float(segment_df[col].mean()),
                    "median": float(segment_df[col].median()),
                    "std": float(segment_df[col].std()),
                    "min": float(segment_df[col].min()),
                    "max": float(segment_df[col].max())
                }
        
        # Calculate business metrics
        business_metrics = {
            "customer_count": len(segment_df),
            "percentage": (len(segment_df) / len(df)) * 100
        }
        
        # Compare to overall population
        for col in feature_columns:
            if col in df.columns and col in characteristics:
                overall_mean = df[col].mean()
                segment_mean = characteristics[col]["mean"]
                deviation = ((segment_mean - overall_mean) / overall_mean * 100) if overall_mean != 0 else 0
                characteristics[col]["deviation_from_overall_pct"] = deviation
        
        return SegmentProfile(
            segment_name=segment_name,
            customer_count=len(segment_df),
            percentage=business_metrics["percentage"],
            characteristics=characteristics,
            business_metrics=business_metrics
        )
    
    def profile_all_segments(
        self,
        df: pd.DataFrame,
        feature_columns: List[str]
    ) -> List[SegmentProfile]:
        """Profile all segments.
        
        Args:
            df: DataFrame with customer data and cluster labels
            feature_columns: List of feature columns to profile
        
        Returns:
            List of SegmentProfile objects
        """
        profiles = []
        unique_labels = df["cluster"].unique()
        
        for label in sorted(unique_labels):
            profile = self.profile_segment(df, label, feature_columns)
            profiles.append(profile)
        
        return profiles
    
    def generate_business_interpretation(
        self,
        profile: SegmentProfile
    ) -> Dict[str, Any]:
        """Generate business interpretation of a segment.
        
        Args:
            profile: SegmentProfile to interpret
        
        Returns:
            Dictionary with business interpretation
        """
        interpretation = {
            "segment_name": profile.segment_name,
            "size": f"{profile.customer_count} customers ({profile.percentage:.1f}%)",
            "key_characteristics": [],
            "business_implications": [],
            "recommended_actions": []
        }
        
        # Analyze characteristics
        for feature, stats in profile.characteristics.items():
            deviation = stats.get("deviation_from_overall_pct", 0)
            
            if abs(deviation) > 20:  # Significant deviation
                direction = "higher" if deviation > 0 else "lower"
                interpretation["key_characteristics"].append({
                    "feature": feature,
                    "value": stats["mean"],
                    "comparison": f"{direction} than average by {abs(deviation):.1f}%"
                })
        
        # Generate business implications based on characteristics
        for char in interpretation["key_characteristics"]:
            feature = char["feature"]
            
            if "profitability" in feature or "profit" in feature:
                if char["comparison"].startswith("higher"):
                    interpretation["business_implications"].append("High profitability segment - prioritize retention")
                    interpretation["recommended_actions"].append("VIP service, cross-sell opportunities")
                else:
                    interpretation["business_implications"].append("Low profitability segment - review relationship")
                    interpretation["recommended_actions"].append("Cost optimization, digital service")
            
            elif "transaction_frequency" in feature or "engagement" in feature:
                if char["comparison"].startswith("higher"):
                    interpretation["business_implications"].append("Highly engaged segment - loyalty programs")
                    interpretation["recommended_actions"].append("Rewards, advocacy programs")
                else:
                    interpretation["business_implications"].append("Low engagement segment - re-engagement needed")
                    interpretation["recommended_actions"].append("Targeted campaigns, product education")
            
            elif "balance" in feature or "exposure" in feature:
                if char["comparison"].startswith("higher"):
                    interpretation["business_implications"].append("High exposure segment - risk monitoring")
                    interpretation["recommended_actions"].append("Regular review, risk mitigation")
                else:
                    interpretation["business_implications"].append("Low exposure segment - growth opportunity")
                    interpretation["recommended_actions"].append("Cross-sell, relationship building")
        
        return interpretation
    
    def create_segment_summary(
        self,
        profiles: List[SegmentProfile]
    ) -> pd.DataFrame:
        """Create summary of all segments.
        
        Args:
            profiles: List of SegmentProfile objects
        
        Returns:
            DataFrame with segment summary
        """
        summary_data = []
        
        for profile in profiles:
            interpretation = self.generate_business_interpretation(profile)
            summary_data.append({
                "segment": profile.segment_name,
                "customer_count": profile.customer_count,
                "percentage": profile.percentage,
                "key_characteristics": ", ".join([c["feature"] for c in interpretation["key_characteristics"]]),
                "business_implications": "; ".join(interpretation["business_implications"])
            })
        
        return pd.DataFrame(summary_data)
