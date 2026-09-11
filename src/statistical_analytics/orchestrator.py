"""Orchestrator for statistical analytics."""

from typing import Dict, Any, List, Optional
import logging

import pandas as pd
import numpy as np

from src.statistical_analytics.base import StatisticalBase
from src.statistical_analytics.descriptive import DescriptiveStatistics
from src.statistical_analytics.correlation import CorrelationAnalyzer
from src.statistical_analytics.confidence import ConfidenceIntervalCalculator
from src.statistical_analytics.t_tests import TTestAnalyzer
from src.statistical_analytics.chi_square import ChiSquareAnalyzer
from src.statistical_analytics.anova import ANOVAAnalyzer
from src.statistical_analytics.nonparametric import NonParametricAnalyzer
from src.statistical_analytics.regression import RegressionAnalyzer
from src.statistical_analytics.business_tests import BusinessQuestionTests

logger = logging.getLogger(__name__)


class StatisticalOrchestrator(StatisticalBase):
    """Orchestrates statistical analytics operations."""
    
    def __init__(self, alpha: float = 0.05):
        """Initialize statistical orchestrator.
        
        Args:
            alpha: Significance level
        """
        super().__init__(alpha)
        
        # Initialize components
        self.descriptive = DescriptiveStatistics(alpha)
        self.correlation = CorrelationAnalyzer(alpha)
        self.confidence = ConfidenceIntervalCalculator(alpha)
        self.t_tester = TTestAnalyzer(alpha)
        self.chi_tester = ChiSquareAnalyzer(alpha)
        self.anova_tester = ANOVAAnalyzer(alpha)
        self.nonparametric = NonParametricAnalyzer(alpha)
        self.regression = RegressionAnalyzer(alpha)
        self.business_tests = BusinessQuestionTests(alpha)
    
    def generate_statistical_report(
        self,
        df: pd.DataFrame,
        columns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive statistical report.
        
        Args:
            df: DataFrame with data
            columns: Columns to analyze (if None, analyze all numeric)
        
        Returns:
            Dictionary with statistical report
        """
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        logger.info(f"Generating statistical report for {len(columns)} columns")
        
        report = {
            "metadata": {
                "alpha": self.alpha,
                "columns_analyzed": columns,
                "total_rows": len(df)
            },
            "descriptive_statistics": {},
            "normality_tests": {},
            "correlations": {}
        }
        
        # Descriptive statistics
        for col in columns:
            report["descriptive_statistics"][col] = self.descriptive.calculate_summary_statistics(
                df[col], col
            )
            report["normality_tests"][col] = self.descriptive.test_normality(df[col], col)
        
        # Correlation matrix
        if len(columns) > 1:
            report["correlations"]["matrix"] = self.correlation.calculate_correlation_matrix(
                df[columns]
            ).to_dict()
        
        return report
    
    def run_business_question_analysis(
        self,
        df: pd.DataFrame,
        questions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Run statistical tests for business questions.
        
        Args:
            df: DataFrame with customer data
            questions: List of business questions to test
        
        Returns:
            Dictionary with test results
        """
        if questions is None:
            questions = [
                "profitability_by_segment",
                "churn_by_customer_group",
                "credit_utilization_churn",
                "product_ownership_profitability",
                "payment_behavior_risk_group"
            ]
        
        logger.info(f"Running business question analysis for {len(questions)} questions")
        
        results = {}
        
        if "profitability_by_segment" in questions:
            results["profitability_by_segment"] = self.business_tests.test_profitability_by_segment(df).to_dict()
        
        if "churn_by_customer_group" in questions:
            results["churn_by_customer_group"] = self.business_tests.test_churn_by_customer_group(df).to_dict()
        
        if "credit_utilization_churn" in questions:
            results["credit_utilization_churn"] = self.business_tests.test_credit_utilization_churn_relationship(df).to_dict()
        
        if "product_ownership_profitability" in questions:
            results["product_ownership_profitability"] = self.business_tests.test_product_ownership_profitability_relationship(df).to_dict()
        
        if "payment_behavior_risk_group" in questions:
            results["payment_behavior_risk_group"] = self.business_tests.test_payment_behavior_by_risk_group(df).to_dict()
        
        return results
