"""T-tests (independent, paired)."""

from typing import Dict, Any, Optional
import logging

import pandas as pd
import numpy as np
from scipy import stats

from src.statistical_analytics.base import StatisticalBase, TestResult

logger = logging.getLogger(__name__)


class TTestAnalyzer(StatisticalBase):
    """Perform t-tests for comparing means."""
    
    def independent_t_test(
        self,
        group1: pd.Series,
        group2: pd.Series,
        group1_name: str = "Group 1",
        group2_name: str = "Group 2",
        equal_var: bool = True
    ) -> TestResult:
        """Perform independent samples t-test.
        
        Args:
            group1: Series for group 1
            group2: Series for group 2
            group1_name: Name of group 1
            group2_name: Name of group 2
            equal_var: Assume equal variances (True) or use Welch's t-test (False)
        
        Returns:
            TestResult with t-test analysis
        """
        group1 = group1.dropna()
        group2 = group2.dropna()
        
        if len(group1) < 2 or len(group2) < 2:
            return TestResult(
                test_name="Independent Samples T-Test",
                null_hypothesis=f"Mean of {group1_name} equals mean of {group2_name}",
                alternative_hypothesis=f"Mean of {group1_name} differs from mean of {group2_name}",
                assumptions=["Sufficient sample size"],
                test_statistic=0.0,
                p_value=1.0,
                business_interpretation="Insufficient data for t-test"
            )
        
        # Perform t-test
        statistic, p_value = stats.ttest_ind(group1, group2, equal_var=equal_var)
        
        # Calculate effect size (Cohen's d)
        pooled_std = np.sqrt(((len(group1) - 1) * group1.var() + (len(group2) - 1) * group2.var()) / 
                             (len(group1) + len(group2) - 2))
        cohens_d = (group1.mean() - group2.mean()) / pooled_std if pooled_std > 0 else 0
        
        # Calculate confidence interval for difference
        mean_diff = group1.mean() - group2.mean()
        std_error = np.sqrt(group1.var() / len(group1) + group2.var() / len(group2))
        df = len(group1) + len(group2) - 2
        t_critical = stats.t.ppf(1 - self.alpha / 2, df)
        margin_of_error = t_critical * std_error
        ci_lower = mean_diff - margin_of_error
        ci_upper = mean_diff + margin_of_error
        
        assumptions = [
            "Independent observations",
            "Normally distributed populations",
            "Homoscedasticity (equal variances)" if equal_var else "Unequal variances allowed (Welch's t-test)",
            "Continuous dependent variable"
        ]
        
        business_interpretation = (
            f"Mean difference: {mean_diff:.2f} ({group1_name} - {group2_name}). "
            f"{self.interpret_p_value(p_value)}. "
            f"Effect size (Cohen's d): {cohens_d:.3f} ({self.interpret_effect_size(cohens_d, 'cohens_d')})."
        )
        
        return TestResult(
            test_name="Independent Samples T-Test",
            null_hypothesis=f"Mean of {group1_name} equals mean of {group2_name}",
            alternative_hypothesis=f"Mean of {group1_name} differs from mean of {group2_name}",
            assumptions=assumptions,
            test_statistic=statistic,
            p_value=p_value,
            confidence_interval=(ci_lower, ci_upper),
            effect_size=cohens_d,
            effect_size_type="cohens_d",
            business_interpretation=business_interpretation,
            additional_info={
                "group1_mean": group1.mean(),
                "group2_mean": group2.mean(),
                "group1_std": group1.std(),
                "group2_std": group2.std(),
                "group1_n": len(group1),
                "group2_n": len(group2),
                "mean_difference": mean_diff,
                "equal_var": equal_var
            }
        )
    
    def paired_t_test(
        self,
        before: pd.Series,
        after: pd.Series,
        condition_name: str = "Condition"
    ) -> TestResult:
        """Perform paired samples t-test.
        
        Args:
            before: Series before treatment
            after: Series after treatment
            condition_name: Name of the condition/treatment
        
        Returns:
            TestResult with paired t-test analysis
        """
        # Remove missing values pairwise
        df = pd.DataFrame({"before": before, "after": after}).dropna()
        
        if len(df) < 2:
            return TestResult(
                test_name="Paired Samples T-Test",
                null_hypothesis=f"Mean difference equals zero for {condition_name}",
                alternative_hypothesis=f"Mean difference differs from zero for {condition_name}",
                assumptions=["Sufficient paired observations"],
                test_statistic=0.0,
                p_value=1.0,
                business_interpretation="Insufficient data for paired t-test"
            )
        
        # Calculate differences
        differences = df["after"] - df["before"]
        
        # Perform paired t-test
        statistic, p_value = stats.ttest_rel(df["before"], df["after"])
        
        # Calculate effect size (Cohen's d for paired)
        cohens_d = differences.mean() / differences.std() if differences.std() > 0 else 0
        
        # Calculate confidence interval for mean difference
        std_error = differences.std() / np.sqrt(len(differences))
        df = len(differences) - 1
        t_critical = stats.t.ppf(1 - self.alpha / 2, df)
        margin_of_error = t_critical * std_error
        ci_lower = differences.mean() - margin_of_error
        ci_upper = differences.mean() + margin_of_error
        
        assumptions = [
            "Paired observations (same subjects)",
            "Normally distributed differences",
            "Continuous dependent variable",
            "Independence between pairs"
        ]
        
        business_interpretation = (
            f"Mean difference: {differences.mean():.2f} (after - before). "
            f"{self.interpret_p_value(p_value)}. "
            f"Effect size (Cohen's d): {cohens_d:.3f} ({self.interpret_effect_size(cohens_d, 'cohens_d')})."
        )
        
        return TestResult(
            test_name="Paired Samples T-Test",
            null_hypothesis=f"Mean difference equals zero for {condition_name}",
            alternative_hypothesis=f"Mean difference differs from zero for {condition_name}",
            assumptions=assumptions,
            test_statistic=statistic,
            p_value=p_value,
            confidence_interval=(ci_lower, ci_upper),
            effect_size=cohens_d,
            effect_size_type="cohens_d",
            business_interpretation=business_interpretation,
            additional_info={
                "before_mean": df["before"].mean(),
                "after_mean": df["after"].mean(),
                "mean_difference": differences.mean(),
                "std_difference": differences.std(),
                "n_pairs": len(differences)
            }
        )
