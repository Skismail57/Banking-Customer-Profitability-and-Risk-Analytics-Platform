"""Business question tests (profitability vs segments, churn vs groups, etc.)."""

from typing import Dict, Any, List, Optional
import logging

import pandas as pd

from src.statistical_analytics.base import StatisticalBase, TestResult
from src.statistical_analytics.t_tests import TTestAnalyzer
from src.statistical_analytics.chi_square import ChiSquareAnalyzer
from src.statistical_analytics.anova import ANOVAAnalyzer
from src.statistical_analytics.correlation import CorrelationAnalyzer

logger = logging.getLogger(__name__)


class BusinessQuestionTests(StatisticalBase):
    """Statistical tests for specific business questions."""
    
    def __init__(self, alpha: float = 0.05):
        """Initialize business question tests.
        
        Args:
            alpha: Significance level
        """
        super().__init__(alpha)
        self.t_tester = TTestAnalyzer(alpha)
        self.chi_tester = ChiSquareAnalyzer(alpha)
        self.anova_tester = ANOVAAnalyzer(alpha)
        self.correlation_tester = CorrelationAnalyzer(alpha)
    
    def test_profitability_by_segment(
        self,
        df: pd.DataFrame,
        profitability_col: str = "net_profit",
        segment_col: str = "segment"
    ) -> TestResult:
        """Test if customer profitability differs between segments.
        
        Business Question: Does customer profitability differ between segments?
        
        Args:
            df: DataFrame with customer data
            profitability_col: Column with profitability values
            segment_col: Column with segment labels
        
        Returns:
            TestResult with ANOVA analysis
        """
        segments = df[segment_col].unique()
        
        if len(segments) < 2:
            return TestResult(
                test_name="Profitability by Segment",
                null_hypothesis="Customer profitability is equal across segments",
                alternative_hypothesis="Customer profitability differs between segments",
                assumptions=["Multiple segments"],
                test_statistic=0.0,
                p_value=1.0,
                business_interpretation="Insufficient segments for comparison"
            )
        
        if len(segments) == 2:
            # Use t-test for two segments
            segment1 = df[df[segment_col] == segments[0]][profitability_col]
            segment2 = df[df[segment_col] == segments[1]][profitability_col]
            
            result = self.t_tester.independent_t_test(
                segment1, segment2, segments[0], segments[1]
            )
            
            result.test_name = "Profitability by Segment (T-Test)"
            result.null_hypothesis = "Customer profitability is equal across segments"
            result.alternative_hypothesis = "Customer profitability differs between segments"
            
            # Add business interpretation
            mean_diff = result.additional_info["mean_difference"]
            if result.p_value < self.alpha:
                result.business_interpretation += (
                    f" Statistically significant difference in profitability between segments. "
                    f"Segment {segments[0]} has {'higher' if mean_diff > 0 else 'lower'} profitability "
                    f"by ${abs(mean_diff):.2f} on average."
                )
            else:
                result.business_interpretation += (
                    " No statistically significant difference in profitability between segments."
                )
            
            return result
        else:
            # Use ANOVA for multiple segments
            result = self.anova_tester.one_way_anova(df, profitability_col, segment_col)
            
            result.test_name = "Profitability by Segment (ANOVA)"
            
            # Add business interpretation
            if result.p_value < self.alpha:
                result.business_interpretation += (
                    " Statistically significant difference in profitability across segments. "
                    "Consider post-hoc tests to identify which segments differ."
                )
            else:
                result.business_interpretation += (
                    " No statistically significant difference in profitability across segments."
                )
            
            return result
    
    def test_churn_by_customer_group(
        self,
        df: pd.DataFrame,
        churn_col: str = "is_churned",
        group_col: str = "customer_group"
    ) -> TestResult:
        """Test if churn differs significantly between customer groups.
        
        Business Question: Does churn differ significantly between customer groups?
        
        Args:
            df: DataFrame with customer data
            churn_col: Column with churn indicator (binary)
            group_col: Column with group labels
        
        Returns:
            TestResult with chi-square test analysis
        """
        result = self.chi_tester.chi_square_test_of_independence(df, group_col, churn_col)
        
        result.test_name = "Churn by Customer Group"
        result.null_hypothesis = "Churn rate is independent of customer group"
        result.alternative_hypothesis = "Churn rate differs by customer group"
        
        # Add business interpretation
        if result.p_value < self.alpha:
            result.business_interpretation += (
                " Statistically significant association between customer group and churn. "
                "Some customer groups have higher churn rates than others."
            )
        else:
            result.business_interpretation += (
                " No statistically significant association between customer group and churn."
            )
        
        return result
    
    def test_credit_utilization_churn_relationship(
        self,
        df: pd.DataFrame,
        utilization_col: str = "credit_utilization",
        churn_col: str = "is_churned"
    ) -> TestResult:
        """Test if credit utilization relates to churn.
        
        Business Question: Does credit utilization relate to churn?
        
        Args:
            df: DataFrame with customer data
            utilization_col: Column with credit utilization values
            churn_col: Column with churn indicator (binary)
        
        Returns:
            TestResult with t-test analysis
        """
        churned = df[df[churn_col] == 1][utilization_col]
        not_churned = df[df[churn_col] == 0][utilization_col]
        
        result = self.t_tester.independent_t_test(
            churned, not_churned, "Churned", "Not Churned"
        )
        
        result.test_name = "Credit Utilization vs Churn"
        result.null_hypothesis = "Credit utilization is equal between churned and non-churned customers"
        result.alternative_hypothesis = "Credit utilization differs between churned and non-churned customers"
        
        # Add business interpretation
        mean_diff = result.additional_info["mean_difference"]
        if result.p_value < self.alpha:
            result.business_interpretation += (
                f" Statistically significant difference in credit utilization. "
                f"{'Churned' if mean_diff > 0 else 'Non-churned'} customers have "
                f"{'higher' if mean_diff > 0 else 'lower'} credit utilization "
                f"by {abs(mean_diff):.2%} on average."
            )
        else:
            result.business_interpretation += (
                " No statistically significant difference in credit utilization between groups."
            )
        
        return result
    
    def test_product_ownership_profitability_relationship(
        self,
        df: pd.DataFrame,
        product_count_col: str = "product_count",
        profitability_col: str = "net_profit"
    ) -> TestResult:
        """Test if product ownership relates to profitability.
        
        Business Question: Does product ownership relate to profitability?
        
        Args:
            df: DataFrame with customer data
            product_count_col: Column with product count
            profitability_col: Column with profitability values
        
        Returns:
            TestResult with correlation analysis
        """
        result = self.correlation_tester.calculate_correlation(
            df[product_count_col],
            df[profitability_col],
            method="pearson",
            x_name="Product Count",
            y_name="Profitability"
        )
        
        result.test_name = "Product Ownership vs Profitability"
        result.null_hypothesis = "No correlation between product ownership and profitability"
        result.alternative_hypothesis = "Correlation exists between product ownership and profitability"
        
        # Add business interpretation
        if result.p_value < self.alpha:
            direction = result.additional_info["correlation_direction"]
            strength = result.additional_info["correlation_strength"]
            result.business_interpretation += (
                f" Statistically significant {strength.lower()} {direction} correlation. "
                f"Customers with more products tend to have {'higher' if direction == 'positive' else 'lower'} profitability."
            )
        else:
            result.business_interpretation += (
                " No statistically significant correlation between product ownership and profitability."
            )
        
        return result
    
    def test_payment_behavior_by_risk_group(
        self,
        df: pd.DataFrame,
        payment_behavior_col: str = "on_time_payment_rate",
        risk_group_col: str = "risk_band"
    ) -> TestResult:
        """Test if payment behavior differs between risk groups.
        
        Business Question: Does payment behavior differ between risk groups?
        
        Args:
            df: DataFrame with customer data
            payment_behavior_col: Column with payment behavior metric
            risk_group_col: Column with risk group labels
        
        Returns:
            TestResult with ANOVA analysis
        """
        result = self.anova_tester.one_way_anova(df, payment_behavior_col, risk_group_col)
        
        result.test_name = "Payment Behavior by Risk Group"
        result.null_hypothesis = "Payment behavior is equal across risk groups"
        result.alternative_hypothesis = "Payment behavior differs between risk groups"
        
        # Add business interpretation
        if result.p_value < self.alpha:
            result.business_interpretation += (
                " Statistically significant difference in payment behavior across risk groups. "
                "Higher risk groups show different payment patterns."
            )
        else:
            result.business_interpretation += (
                " No statistically significant difference in payment behavior across risk groups."
            )
        
        return result
