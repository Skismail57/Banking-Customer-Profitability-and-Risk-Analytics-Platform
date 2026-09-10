"""Non-parametric tests (Mann-Whitney, Kruskal-Wallis)."""

from typing import Dict, Any, Optional
import logging

import pandas as pd
import numpy as np
from scipy import stats

from src.statistical_analytics.base import StatisticalBase, TestResult

logger = logging.getLogger(__name__)


class NonParametricAnalyzer(StatisticalBase):
    """Perform non-parametric tests when assumptions are violated."""
    
    def mann_whitney_u_test(
        self,
        group1: pd.Series,
        group2: pd.Series,
        group1_name: str = "Group 1",
        group2_name: str = "Group 2"
    ) -> TestResult:
        """Perform Mann-Whitney U test (Wilcoxon rank-sum test).
        
        Args:
            group1: Series for group 1
            group2: Series for group 2
            group1_name: Name of group 1
            group2_name: Name of group 2
        
        Returns:
            TestResult with Mann-Whitney U test analysis
        """
        group1 = group1.dropna()
        group2 = group2.dropna()
        
        if len(group1) < 2 or len(group2) < 2:
            return TestResult(
                test_name="Mann-Whitney U Test",
                null_hypothesis=f"Distributions of {group1_name} and {group2_name} are equal",
                alternative_hypothesis=f"Distributions of {group1_name} and {group2_name} differ",
                assumptions=["Sufficient sample size"],
                test_statistic=0.0,
                p_value=1.0,
                business_interpretation="Insufficient data for Mann-Whitney U test"
            )
        
        # Perform Mann-Whitney U test
        statistic, p_value = stats.mannwhitneyu(group1, group2, alternative='two-sided')
        
        # Calculate effect size (r = Z / sqrt(N))
        # Calculate Z-score from U statistic
        n1, n2 = len(group1), len(group2)
        mean_u = n1 * n2 / 2
        std_u = np.sqrt(n1 * n2 * (n1 + n2 + 1) / 12)
        z_score = (statistic - mean_u) / std_u if std_u > 0 else 0
        effect_size_r = abs(z_score) / np.sqrt(n1 + n2)
        
        assumptions = [
            "Independent observations",
            "Ordinal or continuous data",
            "Similar shape distributions (for median comparison)",
            "No normality assumption"
        ]
        
        business_interpretation = (
            f"U-statistic: {statistic:.3f}. "
            f"{self.interpret_p_value(p_value)}. "
            f"Effect size (r): {effect_size_r:.3f} ({self.interpret_effect_size(effect_size_r, 'cohens_d')})."
        )
        
        return TestResult(
            test_name="Mann-Whitney U Test",
            null_hypothesis=f"Distributions of {group1_name} and {group2_name} are equal",
            alternative_hypothesis=f"Distributions of {group1_name} and {group2_name} differ",
            assumptions=assumptions,
            test_statistic=statistic,
            p_value=p_value,
            effect_size=effect_size_r,
            effect_size_type="r",
            business_interpretation=business_interpretation,
            additional_info={
                "group1_median": group1.median(),
                "group2_median": group2.median(),
                "group1_n": n1,
                "group2_n": n2,
                "z_score": z_score
            }
        )
    
    def kruskal_wallis_test(
        self,
        df: pd.DataFrame,
        value_col: str,
        group_col: str
    ) -> TestResult:
        """Perform Kruskal-Wallis H-test.
        
        Args:
            df: DataFrame with data
            value_col: Column with values to compare
            group_col: Column with group labels
        
        Returns:
            TestResult with Kruskal-Wallis test analysis
        """
        groups = df[group_col].unique()
        group_data = [df[df[group_col] == group][value_col].dropna() for group in groups]
        
        if any(len(g) < 2 for g in group_data):
            return TestResult(
                test_name="Kruskal-Wallis H-Test",
                null_hypothesis=f"All group distributions are equal for {value_col}",
                alternative_hypothesis=f"At least one group distribution differs for {value_col}",
                assumptions=["Sufficient sample size per group"],
                test_statistic=0.0,
                p_value=1.0,
                business_interpretation="Insufficient data for Kruskal-Wallis test"
            )
        
        # Perform Kruskal-Wallis test
        statistic, p_value = stats.kruskal(*group_data)
        
        # Calculate effect size (eta-squared based on H statistic)
        n = len(df)
        eta_squared = (statistic - len(groups) + 1) / (n - len(groups)) if n > len(groups) else 0
        
        assumptions = [
            "Independent observations",
            "Ordinal or continuous data",
            "Similar shape distributions",
            "No normality assumption",
            "Independent groups"
        ]
        
        business_interpretation = (
            f"H-statistic: {statistic:.3f}. "
            f"{self.interpret_p_value(p_value)}. "
            f"Effect size (eta-squared): {eta_squared:.3f} ({self.interpret_effect_size(eta_squared, 'eta_squared')})."
        )
        
        return TestResult(
            test_name="Kruskal-Wallis H-Test",
            null_hypothesis=f"All group distributions are equal for {value_col}",
            alternative_hypothesis=f"At least one group distribution differs for {value_col}",
            assumptions=assumptions,
            test_statistic=statistic,
            p_value=p_value,
            effect_size=eta_squared,
            effect_size_type="eta_squared",
            business_interpretation=business_interpretation,
            additional_info={
                "groups": groups.tolist(),
                "group_medians": {group: g.median() for group, g in zip(groups, group_data)},
                "group_n": {group: len(g) for group, g in zip(groups, group_data)},
                "df": len(groups) - 1
            }
        )
