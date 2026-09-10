"""Chi-square tests."""

from typing import Dict, Any, Optional
import logging

import pandas as pd
import numpy as np
from scipy import stats

from src.statistical_analytics.base import StatisticalBase, TestResult

logger = logging.getLogger(__name__)


class ChiSquareAnalyzer(StatisticalBase):
    """Perform chi-square tests for categorical data."""
    
    def chi_square_test_of_independence(
        self,
        df: pd.DataFrame,
        col1: str,
        col2: str
    ) -> TestResult:
        """Perform chi-square test of independence.
        
        Args:
            df: DataFrame with categorical data
            col1: First categorical column
            col2: Second categorical column
        
        Returns:
            TestResult with chi-square test analysis
        """
        # Create contingency table
        contingency_table = pd.crosstab(df[col1], df[col2])
        
        # Check assumptions
        if contingency_table.sum().sum() < 25:
            return TestResult(
                test_name="Chi-Square Test of Independence",
                null_hypothesis=f"{col1} and {col2} are independent",
                alternative_hypothesis=f"{col1} and {col2} are associated",
                assumptions=["Sufficient sample size"],
                test_statistic=0.0,
                p_value=1.0,
                business_interpretation="Insufficient data for chi-square test"
            )
        
        # Perform chi-square test
        statistic, p_value, dof, expected = stats.chi2_contingency(contingency_table)
        
        # Calculate effect size (Phi coefficient for 2x2, Cramer's V for larger)
        n = contingency_table.sum().sum()
        min_dim = min(contingency_table.shape) - 1
        
        if min_dim == 1:
            # Phi coefficient for 2x2 tables
            phi = np.sqrt(statistic / n)
            effect_size = phi
            effect_type = "phi"
        else:
            # Cramer's V for larger tables
            cramers_v = np.sqrt(statistic / (n * min_dim))
            effect_size = cramers_v
            effect_type = "cramers_v"
        
        assumptions = [
            "Independent observations",
            "Sufficient sample size (expected frequencies >= 5)",
            "Categorical variables",
            "Random sampling"
        ]
        
        business_interpretation = (
            f"Chi-square statistic: {statistic:.3f}. "
            f"{self.interpret_p_value(p_value)}. "
            f"Effect size ({effect_type}): {effect_size:.3f} ({self.interpret_effect_size(effect_size, effect_type)})."
        )
        
        return TestResult(
            test_name="Chi-Square Test of Independence",
            null_hypothesis=f"{col1} and {col2} are independent",
            alternative_hypothesis=f"{col1} and {col2} are associated",
            assumptions=assumptions,
            test_statistic=statistic,
            p_value=p_value,
            effect_size=effect_size,
            effect_size_type=effect_type,
            business_interpretation=business_interpretation,
            additional_info={
                "degrees_of_freedom": dof,
                "sample_size": n,
                "contingency_table": contingency_table.to_dict(),
                "expected_frequencies": expected.tolist()
            }
        )
    
    def chi_square_goodness_of_fit(
        self,
        observed: pd.Series,
        expected: Optional[pd.Series] = None
    ) -> TestResult:
        """Perform chi-square goodness of fit test.
        
        Args:
            observed: Observed frequencies
            expected: Expected frequencies (if None, assumes uniform distribution)
        
        Returns:
            TestResult with goodness of fit analysis
        """
        observed_counts = observed.value_counts().sort_index()
        
        if expected is None:
            # Assume uniform distribution
            expected_counts = pd.Series([observed_counts.sum() / len(observed_counts)] * len(observed_counts))
        else:
            expected_counts = expected.value_counts().sort_index()
        
        # Ensure same categories
        all_categories = observed_counts.index.union(expected_counts.index)
        observed_counts = observed_counts.reindex(all_categories, fill_value=0)
        expected_counts = expected_counts.reindex(all_categories, fill_value=0)
        
        # Perform chi-square test
        statistic, p_value = stats.chisquare(f_obs=observed_counts, f_exp=expected_counts)
        
        # Calculate effect size (Phi coefficient)
        n = observed_counts.sum()
        phi = np.sqrt(statistic / n)
        
        assumptions = [
            "Independent observations",
            "Sufficient sample size (expected frequencies >= 5)",
            "Categorical data",
            "Mutually exclusive categories"
        ]
        
        business_interpretation = (
            f"Chi-square statistic: {statistic:.3f}. "
            f"{self.interpret_p_value(p_value)}. "
            f"Effect size (phi): {phi:.3f} ({self.interpret_effect_size(phi, 'phi')})."
        )
        
        return TestResult(
            test_name="Chi-Square Goodness of Fit",
            null_hypothesis="Observed distribution matches expected distribution",
            alternative_hypothesis="Observed distribution differs from expected distribution",
            assumptions=assumptions,
            test_statistic=statistic,
            p_value=p_value,
            effect_size=phi,
            effect_size_type="phi",
            business_interpretation=business_interpretation,
            additional_info={
                "observed_counts": observed_counts.to_dict(),
                "expected_counts": expected_counts.to_dict(),
                "sample_size": n
            }
        )
