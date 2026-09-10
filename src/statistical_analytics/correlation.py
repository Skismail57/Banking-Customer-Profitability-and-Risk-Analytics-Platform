"""Correlation analysis."""

from typing import Dict, Any, List, Optional
import logging

import pandas as pd
import numpy as np
from scipy import stats

from src.statistical_analytics.base import StatisticalBase, TestResult

logger = logging.getLogger(__name__)


class CorrelationAnalyzer(StatisticalBase):
    """Analyze correlations between variables."""
    
    def calculate_correlation(
        self,
        x: pd.Series,
        y: pd.Series,
        method: str = "pearson",
        x_name: str = "x",
        y_name: str = "y"
    ) -> TestResult:
        """Calculate correlation between two variables.
        
        Args:
            x: Series for variable x
            y: Series for variable y
            method: Correlation method (pearson, spearman, kendall)
            x_name: Name of variable x
            y_name: Name of variable y
        
        Returns:
            TestResult with correlation analysis
        """
        # Remove missing values
        df = pd.DataFrame({x_name: x, y_name: y}).dropna()
        
        if len(df) < 3:
            return TestResult(
                test_name=f"{method.capitalize()} Correlation",
                null_hypothesis=f"No correlation between {x_name} and {y_name}",
                alternative_hypothesis=f"Correlation exists between {x_name} and {y_name}",
                assumptions=["Sufficient sample size"],
                test_statistic=0.0,
                p_value=1.0,
                business_interpretation="Insufficient data for correlation analysis"
            )
        
        # Calculate correlation
        if method == "pearson":
            corr, p_value = stats.pearsonr(df[x_name], df[y_name])
            assumptions = [
                "Linear relationship between variables",
                "Variables are normally distributed",
                "Homoscedasticity",
                "No significant outliers"
            ]
        elif method == "spearman":
            corr, p_value = stats.spearmanr(df[x_name], df[y_name])
            assumptions = [
                "Monotonic relationship between variables",
                "Ordinal or continuous variables",
                "No normality assumption"
            ]
        elif method == "kendall":
            corr, p_value = stats.kendalltau(df[x_name], df[y_name])
            assumptions = [
                "Ordinal data",
                "No normality assumption",
                "Robust to outliers"
            ]
        else:
            raise ValueError(f"Unknown correlation method: {method}")
        
        # Interpret correlation strength
        abs_corr = abs(corr)
        if abs_corr < 0.1:
            strength = "Negligible"
        elif abs_corr < 0.3:
            strength = "Weak"
        elif abs_corr < 0.5:
            strength = "Moderate"
        elif abs_corr < 0.7:
            strength = "Strong"
        else:
            strength = "Very strong"
        
        direction = "positive" if corr > 0 else "negative"
        
        business_interpretation = (
            f"{strength} {direction} correlation ({corr:.3f}) between {x_name} and {y_name}. "
            f"{self.interpret_p_value(p_value)}."
        )
        
        return TestResult(
            test_name=f"{method.capitalize()} Correlation",
            null_hypothesis=f"No correlation between {x_name} and {y_name}",
            alternative_hypothesis=f"Correlation exists between {x_name} and {y_name}",
            assumptions=assumptions,
            test_statistic=corr,
            p_value=p_value,
            effect_size=abs(corr),
            effect_size_type="correlation_coefficient",
            business_interpretation=business_interpretation,
            additional_info={
                "method": method,
                "sample_size": len(df),
                "correlation_strength": strength,
                "correlation_direction": direction
            }
        )
    
    def calculate_correlation_matrix(
        self,
        df: pd.DataFrame,
        method: str = "pearson"
    ) -> pd.DataFrame:
        """Calculate correlation matrix for multiple variables.
        
        Args:
            df: DataFrame with variables
            method: Correlation method
        
        Returns:
            Correlation matrix
        """
        return df.corr(method=method)
