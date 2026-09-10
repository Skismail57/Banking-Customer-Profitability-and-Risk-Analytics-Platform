"""Confidence interval calculations."""

from typing import Dict, Any, Optional
import logging

import pandas as pd
import numpy as np
from scipy import stats

from src.statistical_analytics.base import StatisticalBase

logger = logging.getLogger(__name__)


class ConfidenceIntervalCalculator(StatisticalBase):
    """Calculate confidence intervals for means and proportions."""
    
    def calculate_mean_ci(
        self,
        data: pd.Series,
        confidence_level: float = 0.95
    ) -> Dict[str, Any]:
        """Calculate confidence interval for mean.
        
        Args:
            data: Series with data
            confidence_level: Confidence level (default 0.95)
        
        Returns:
            Dictionary with CI results
        """
        data = data.dropna()
        
        if len(data) < 2:
            return {
                "mean": None,
                "std": None,
                "std_error": None,
                "ci_lower": None,
                "ci_upper": None,
                "confidence_level": confidence_level,
                "interpretation": "Insufficient data"
            }
        
        mean = data.mean()
        std = data.std()
        std_error = std / np.sqrt(len(data))
        
        # Calculate critical value
        alpha = 1 - confidence_level
        df = len(data) - 1
        t_critical = stats.t.ppf(1 - alpha / 2, df)
        
        # Calculate CI
        margin_of_error = t_critical * std_error
        ci_lower = mean - margin_of_error
        ci_upper = mean + margin_of_error
        
        return {
            "mean": mean,
            "std": std,
            "std_error": std_error,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "margin_of_error": margin_of_error,
            "confidence_level": confidence_level,
            "sample_size": len(data),
            "degrees_of_freedom": df,
            "t_critical": t_critical,
            "interpretation": (
                f"We are {confidence_level * 100:.0f}% confident that the true mean "
                f"is between {ci_lower:.2f} and {ci_upper:.2f}"
            )
        }
    
    def calculate_proportion_ci(
        self,
        successes: int,
        n: int,
        confidence_level: float = 0.95,
        method: str = "normal"
    ) -> Dict[str, Any]:
        """Calculate confidence interval for proportion.
        
        Args:
            successes: Number of successes
            n: Total number of trials
            confidence_level: Confidence level
            method: Method for CI calculation (normal, wilson, exact)
        
        Returns:
            Dictionary with CI results
        """
        if n == 0:
            return {
                "proportion": None,
                "ci_lower": None,
                "ci_upper": None,
                "confidence_level": confidence_level,
                "interpretation": "No data"
            }
        
        p = successes / n
        
        if method == "normal":
            # Normal approximation
            std_error = np.sqrt(p * (1 - p) / n)
            z_critical = stats.norm.ppf(1 - (1 - confidence_level) / 2)
            margin_of_error = z_critical * std_error
            ci_lower = max(0, p - margin_of_error)
            ci_upper = min(1, p + margin_of_error)
        
        elif method == "wilson":
            # Wilson score interval
            z = stats.norm.ppf(1 - (1 - confidence_level) / 2)
            denominator = 1 + z**2 / n
            center = (p + z**2 / (2 * n)) / denominator
            margin = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denominator
            ci_lower = max(0, center - margin)
            ci_upper = min(1, center + margin)
        
        elif method == "exact":
            # Exact binomial (Clopper-Pearson)
            ci_lower = stats.beta.ppf((1 - confidence_level) / 2, successes, n - successes + 1)
            ci_upper = stats.beta.ppf(1 - (1 - confidence_level) / 2, successes + 1, n - successes)
        
        else:
            raise ValueError(f"Unknown method: {method}")
        
        return {
            "proportion": p,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "confidence_level": confidence_level,
            "sample_size": n,
            "successes": successes,
            "method": method,
            "interpretation": (
                f"We are {confidence_level * 100:.0f}% confident that the true proportion "
                f"is between {ci_lower:.4f} and {ci_upper:.4f}"
            )
        }
