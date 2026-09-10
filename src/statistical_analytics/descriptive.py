"""Descriptive statistics and distributions."""

from typing import Dict, Any, List
import logging

import pandas as pd
import numpy as np
from scipy import stats

from src.statistical_analytics.base import StatisticalBase

logger = logging.getLogger(__name__)


class DescriptiveStatistics(StatisticalBase):
    """Calculate descriptive statistics and analyze distributions."""
    
    def calculate_summary_statistics(
        self,
        data: pd.Series,
        column_name: str = "value"
    ) -> Dict[str, Any]:
        """Calculate summary statistics for a variable.
        
        Args:
            data: Series with data
            column_name: Name of the variable
        
        Returns:
            Dictionary with summary statistics
        """
        data = data.dropna()
        
        return {
            "column": column_name,
            "count": len(data),
            "mean": data.mean(),
            "median": data.median(),
            "mode": data.mode().iloc[0] if len(data.mode()) > 0 else None,
            "std": data.std(),
            "variance": data.var(),
            "min": data.min(),
            "max": data.max(),
            "range": data.max() - data.min(),
            "q1": data.quantile(0.25),
            "q3": data.quantile(0.75),
            "iqr": data.quantile(0.75) - data.quantile(0.25),
            "skewness": data.skew(),
            "kurtosis": data.kurtosis(),
            "coefficient_of_variation": data.std() / data.mean() if data.mean() != 0 else None
        }
    
    def test_normality(
        self,
        data: pd.Series,
        column_name: str = "value"
    ) -> Dict[str, Any]:
        """Test for normality using Shapiro-Wilk test.
        
        Args:
            data: Series with data
            column_name: Name of the variable
        
        Returns:
            Dictionary with test results
        """
        data = data.dropna()
        
        if len(data) < 3:
            return {
                "column": column_name,
                "test": "Shapiro-Wilk",
                "statistic": None,
                "p_value": None,
                "is_normal": None,
                "interpretation": "Insufficient data for normality test"
            }
        
        statistic, p_value = stats.shapiro(data)
        
        return {
            "column": column_name,
            "test": "Shapiro-Wilk",
            "statistic": statistic,
            "p_value": p_value,
            "is_normal": p_value > self.alpha,
            "interpretation": self.interpret_p_value(p_value)
        }
    
    def compare_distributions(
        self,
        data1: pd.Series,
        data2: pd.Series,
        group1_name: str = "Group 1",
        group2_name: str = "Group 2"
    ) -> Dict[str, Any]:
        """Compare distributions between two groups.
        
        Args:
            data1: Series for group 1
            data2: Series for group 2
            group1_name: Name of group 1
            group2_name: Name of group 2
        
        Returns:
            Dictionary with comparison results
        """
        data1 = data1.dropna()
        data2 = data2.dropna()
        
        stats1 = self.calculate_summary_statistics(data1, group1_name)
        stats2 = self.calculate_summary_statistics(data2, group2_name)
        
        return {
            "group1": stats1,
            "group2": stats2,
            "difference": {
                "mean_diff": stats1["mean"] - stats2["mean"],
                "median_diff": stats1["median"] - stats2["median"],
                "std_diff": stats1["std"] - stats2["std"]
            }
        }
