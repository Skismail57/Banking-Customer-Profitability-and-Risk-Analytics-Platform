"""ANOVA tests."""

from typing import Dict, Any, List, Optional
import logging

import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.stats.anova import anova_lm
from statsmodels.formula.api import ols

from src.statistical_analytics.base import StatisticalBase, TestResult

logger = logging.getLogger(__name__)


class ANOVAAnalyzer(StatisticalBase):
    """Perform ANOVA tests for comparing means across multiple groups."""
    
    def one_way_anova(
        self,
        df: pd.DataFrame,
        value_col: str,
        group_col: str
    ) -> TestResult:
        """Perform one-way ANOVA.
        
        Args:
            df: DataFrame with data
            value_col: Column with values to compare
            group_col: Column with group labels
        
        Returns:
            TestResult with ANOVA analysis
        """
        # Check assumptions
        groups = df[group_col].unique()
        group_data = [df[df[group_col] == group][value_col].dropna() for group in groups]
        
        if any(len(g) < 2 for g in group_data):
            return TestResult(
                test_name="One-Way ANOVA",
                null_hypothesis=f"All group means are equal for {value_col}",
                alternative_hypothesis=f"At least one group mean differs for {value_col}",
                assumptions=["Sufficient sample size per group"],
                test_statistic=0.0,
                p_value=1.0,
                business_interpretation="Insufficient data for ANOVA"
            )
        
        # Perform one-way ANOVA
        statistic, p_value = stats.f_oneway(*group_data)
        
        # Calculate effect size (eta-squared)
        # Between-group variance
        overall_mean = df[value_col].mean()
        ss_between = sum(len(g) * (g.mean() - overall_mean)**2 for g in group_data)
        # Total variance
        ss_total = sum((x - overall_mean)**2 for x in df[value_col].dropna())
        eta_squared = ss_between / ss_total if ss_total > 0 else 0
        
        assumptions = [
            "Independent observations",
            "Normally distributed populations",
            "Homoscedasticity (equal variances)",
            "Continuous dependent variable",
            "Independent groups"
        ]
        
        business_interpretation = (
            f"F-statistic: {statistic:.3f}. "
            f"{self.interpret_p_value(p_value)}. "
            f"Effect size (eta-squared): {eta_squared:.3f} ({self.interpret_effect_size(eta_squared, 'eta_squared')})."
        )
        
        return TestResult(
            test_name="One-Way ANOVA",
            null_hypothesis=f"All group means are equal for {value_col}",
            alternative_hypothesis=f"At least one group mean differs for {value_col}",
            assumptions=assumptions,
            test_statistic=statistic,
            p_value=p_value,
            effect_size=eta_squared,
            effect_size_type="eta_squared",
            business_interpretation=business_interpretation,
            additional_info={
                "groups": groups.tolist(),
                "group_means": {group: g.mean() for group, g in zip(groups, group_data)},
                "group_n": {group: len(g) for group, g in zip(groups, group_data)},
                "df_between": len(groups) - 1,
                "df_within": len(df) - len(groups)
            }
        )
    
    def two_way_anova(
        self,
        df: pd.DataFrame,
        value_col: str,
        factor1_col: str,
        factor2_col: str
    ) -> Dict[str, Any]:
        """Perform two-way ANOVA.
        
        Args:
            df: DataFrame with data
            value_col: Column with values to compare
            factor1_col: First factor column
            factor2_col: Second factor column
        
        Returns:
            Dictionary with ANOVA results
        """
        # Create formula
        formula = f"{value_col} ~ C({factor1_col}) + C({factor2_col}) + C({factor1_col}):C({factor2_col})"
        
        # Fit model
        model = ols(formula, data=df).fit()
        anova_table = anova_lm(model, typ=2)
        
        # Calculate effect sizes (partial eta-squared)
        ss_total = anova_table["sum_sq"].sum()
        anova_table["partial_eta_squared"] = anova_table["sum_sq"] / (anova_table["sum_sq"] + model.ssr)
        
        return {
            "anova_table": anova_table.to_dict(),
            "formula": formula,
            "assumptions": [
                "Independent observations",
                "Normally distributed residuals",
                "Homoscedasticity",
                "No significant outliers"
            ]
        }
