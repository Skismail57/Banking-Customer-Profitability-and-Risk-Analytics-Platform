"""Integrated Statistical Analytics.

This module connects Statistical Analytics to Core Analytics outputs,
providing statistical analysis on profitability, risk, and behavior metrics.

Architecture Position:
Core Analytics → Statistical Analytics → ML
"""

from typing import Dict, Any, Optional, List
from datetime import date
import logging

import pandas as pd
import numpy as np
from scipy import stats

from src.data_platform.data_loader import DataLoader
from src.statistical_analytics.base import StatisticalBase, TestResult

logger = logging.getLogger(__name__)


class IntegratedStatisticalAnalytics(StatisticalBase):
    """Integrated Statistical Analytics for Core Analytics outputs.
    
    This class provides statistical analysis on the outputs from the Core Analytics
    layer, including hypothesis testing, correlation analysis, and trend analysis.
    """
    
    def __init__(
        self,
        as_of_date: Optional[date] = None,
        data_loader: Optional[DataLoader] = None
    ):
        """Initialize Integrated Statistical Analytics.
        
        Args:
            as_of_date: As-of date for analysis
            data_loader: Data loader instance
        """
        super().__init__()
        self.as_of_date = as_of_date or date.today()
        self.data_loader = data_loader or DataLoader()
    
    def analyze_profitability_by_segment(self) -> TestResult:
        """Analyze profitability differences across segments using ANOVA.
        
        Returns:
            TestResult with ANOVA analysis
        """
        logger.info("Analyzing profitability by segment")
        
        # Load customer metrics
        metrics_df = self.data_loader.load_customer_metrics(as_of_date=self.as_of_date)
        
        if metrics_df.empty or 'segment' not in metrics_df.columns or 'net_profit' not in metrics_df.columns:
            logger.warning("Insufficient data for segment profitability analysis")
            return TestResult(
                test_name="ANOVA: Profitability by Segment",
                null_hypothesis="All segments have equal mean profitability",
                alternative_hypothesis="At least one segment has different mean profitability",
                assumptions=["Normality of residuals", "Homogeneity of variances", "Independent observations"],
                test_statistic=np.nan,
                p_value=np.nan,
                business_interpretation="Insufficient data for analysis"
            )
        
        # Group by segment
        segments = metrics_df['segment'].unique()
        segment_profits = [metrics_df[metrics_df['segment'] == seg]['net_profit'].dropna() for seg in segments]
        
        # Remove empty groups
        segment_profits = [profits for profits in segment_profits if len(profits) > 0]
        
        if len(segment_profits) < 2:
            logger.warning("Insufficient segments for ANOVA")
            return TestResult(
                test_name="ANOVA: Profitability by Segment",
                null_hypothesis="All segments have equal mean profitability",
                alternative_hypothesis="At least one segment has different mean profitability",
                assumptions=["Normality of residuals", "Homogeneity of variances", "Independent observations"],
                test_statistic=np.nan,
                p_value=np.nan,
                business_interpretation="Insufficient segments for analysis"
            )
        
        # Perform ANOVA
        f_stat, p_value = stats.f_oneway(*segment_profits)
        
        # Calculate effect size (eta-squared)
        total_var = np.var(metrics_df['net_profit'].dropna())
        between_var = np.var([np.mean(profits) for profits in segment_profits])
        eta_squared = between_var / total_var if total_var > 0 else 0
        
        # Business interpretation
        if p_value < self.alpha:
            interpretation = f"Statistically significant difference in profitability across segments (p={p_value:.4f}). Business action: Investigate high-performing segments for best practices."
        else:
            interpretation = f"No statistically significant difference in profitability across segments (p={p_value:.4f}). Business action: Segment differentiation may not be driving profitability."
        
        return TestResult(
            test_name="ANOVA: Profitability by Segment",
            null_hypothesis="All segments have equal mean profitability",
            alternative_hypothesis="At least one segment has different mean profitability",
            assumptions=["Normality of residuals", "Homogeneity of variances", "Independent observations"],
            test_statistic=float(f_stat),
            p_value=float(p_value),
            effect_size=float(eta_squared),
            effect_size_type="eta_squared",
            business_interpretation=interpretation,
            additional_info={
                "segments_analyzed": len(segments),
                "segment_means": {seg: float(metrics_df[metrics_df['segment'] == seg]['net_profit'].mean()) 
                                for seg in segments if seg in metrics_df['segment'].values}
            }
        )
    
    def analyze_risk_profitability_correlation(self) -> TestResult:
        """Analyze correlation between risk level and profitability.
        
        Returns:
            TestResult with correlation analysis
        """
        logger.info("Analyzing risk-profitability correlation")
        
        # Load customer metrics
        metrics_df = self.data_loader.load_customer_metrics(as_of_date=self.as_of_date)
        
        if metrics_df.empty or 'risk_level' not in metrics_df.columns or 'net_profit' not in metrics_df.columns:
            logger.warning("Insufficient data for risk-profitability correlation")
            return TestResult(
                test_name="Correlation: Risk vs Profitability",
                null_hypothesis="No correlation between risk level and profitability",
                alternative_hypothesis="Correlation exists between risk level and profitability",
                assumptions=["Linear relationship", "Bivariate normality"],
                test_statistic=np.nan,
                p_value=np.nan,
                business_interpretation="Insufficient data for analysis"
            )
        
        # Convert risk level to numeric
        risk_mapping = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
        metrics_df['risk_numeric'] = metrics_df['risk_level'].map(risk_mapping)
        
        # Remove NaN values
        analysis_df = metrics_df[['risk_numeric', 'net_profit']].dropna()
        
        if len(analysis_df) < 3:
            logger.warning("Insufficient data for correlation analysis")
            return TestResult(
                test_name="Correlation: Risk vs Profitability",
                null_hypothesis="No correlation between risk level and profitability",
                alternative_hypothesis="Correlation exists between risk level and profitability",
                assumptions=["Linear relationship", "Bivariate normality"],
                test_statistic=np.nan,
                p_value=np.nan,
                business_interpretation="Insufficient data for analysis"
            )
        
        # Calculate correlation
        correlation, p_value = stats.pearsonr(analysis_df['risk_numeric'], analysis_df['net_profit'])
        
        # Business interpretation
        if abs(correlation) > 0.5:
            strength = "strong"
        elif abs(correlation) > 0.3:
            strength = "moderate"
        elif abs(correlation) > 0.1:
            strength = "weak"
        else:
            strength = "negligible"
        
        direction = "positive" if correlation > 0 else "negative"
        
        if p_value < self.alpha:
            interpretation = f"Statistically significant {strength} {direction} correlation (r={correlation:.3f}, p={p_value:.4f}). Business action: {'Higher risk customers are more profitable (consider risk-adjusted profitability)' if correlation > 0 else 'Higher risk customers are less profitable (risk management is effective)'}"
        else:
            interpretation = f"No statistically significant correlation (r={correlation:.3f}, p={p_value:.4f}). Business action: Risk level may not be a primary driver of profitability."
        
        return TestResult(
            test_name="Correlation: Risk vs Profitability",
            null_hypothesis="No correlation between risk level and profitability",
            alternative_hypothesis="Correlation exists between risk level and profitability",
            assumptions=["Linear relationship", "Bivariate normality"],
            test_statistic=float(correlation),
            p_value=float(p_value),
            effect_size=float(abs(correlation)),
            effect_size_type="pearson_r",
            business_interpretation=interpretation
        )
    
    def analyze_churn_drivers(self) -> Dict[str, TestResult]:
        """Analyze factors that drive churn using statistical tests.
        
        Returns:
            Dictionary of test results for various churn drivers
        """
        logger.info("Analyzing churn drivers")
        
        results = {}
        
        # Load customer metrics
        metrics_df = self.data_loader.load_customer_metrics(as_of_date=self.as_of_date)
        
        if metrics_df.empty:
            logger.warning("Insufficient data for churn driver analysis")
            return results
        
        # Analyze churn vs profitability
        if 'churn_probability' in metrics_df.columns and 'net_profit' in metrics_df.columns:
            analysis_df = metrics_df[['churn_probability', 'net_profit']].dropna()
            
            if len(analysis_df) >= 3:
                correlation, p_value = stats.pearsonr(analysis_df['churn_probability'], analysis_df['net_profit'])
                
                results['churn_profitability_correlation'] = TestResult(
                    test_name="Correlation: Churn Probability vs Profitability",
                    null_hypothesis="No correlation between churn probability and profitability",
                    alternative_hypothesis="Correlation exists between churn probability and profitability",
                    assumptions=["Linear relationship"],
                    test_statistic=float(correlation),
                    p_value=float(p_value),
                    business_interpretation=f"Correlation: {correlation:.3f}, p={p_value:.4f}"
                )
        
        # Analyze churn vs credit utilization
        if 'churn_probability' in metrics_df.columns and 'credit_utilization' in metrics_df.columns:
            analysis_df = metrics_df[['churn_probability', 'credit_utilization']].dropna()
            
            if len(analysis_df) >= 3:
                correlation, p_value = stats.pearsonr(analysis_df['churn_probability'], analysis_df['credit_utilization'])
                
                results['churn_utilization_correlation'] = TestResult(
                    test_name="Correlation: Churn Probability vs Credit Utilization",
                    null_hypothesis="No correlation between churn probability and credit utilization",
                    alternative_hypothesis="Correlation exists between churn probability and credit utilization",
                    assumptions=["Linear relationship"],
                    test_statistic=float(correlation),
                    p_value=float(p_value),
                    business_interpretation=f"Correlation: {correlation:.3f}, p={p_value:.4f}"
                )
        
        # Analyze churn by segment (chi-square test)
        if 'churn_probability' in metrics_df.columns and 'segment' in metrics_df.columns:
            # Create high churn flag
            metrics_df['high_churn'] = metrics_df['churn_probability'] > 0.5
            
            # Create contingency table
            contingency = pd.crosstab(metrics_df['segment'], metrics_df['high_churn'])
            
            if contingency.shape[0] >= 2 and contingency.shape[1] >= 2:
                chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
                
                results['churn_segment_chi_square'] = TestResult(
                    test_name="Chi-Square: Churn by Segment",
                    null_hypothesis="Churn probability is independent of segment",
                    alternative_hypothesis="Churn probability depends on segment",
                    assumptions=["Independent observations", "Expected frequency >= 5"],
                    test_statistic=float(chi2),
                    p_value=float(p_value),
                    business_interpretation=f"Chi-square: {chi2:.3f}, p={p_value:.4f}"
                )
        
        logger.info(f"Analyzed {len(results)} churn drivers")
        return results
    
    def analyze_clv_distribution(self) -> Dict[str, Any]:
        """Analyze CLV distribution across customers.
        
        Returns:
            Dictionary with CLV distribution statistics
        """
        logger.info("Analyzing CLV distribution")
        
        # Load customer metrics
        metrics_df = self.data_loader.load_customer_metrics(as_of_date=self.as_of_date)
        
        if metrics_df.empty or 'clv' not in metrics_df.columns:
            logger.warning("Insufficient data for CLV distribution analysis")
            return {}
        
        clv_values = metrics_df['clv'].dropna()
        
        if len(clv_values) == 0:
            return {}
        
        distribution = {
            'mean': float(clv_values.mean()),
            'median': float(clv_values.median()),
            'std': float(clv_values.std()),
            'min': float(clv_values.min()),
            'max': float(clv_values.max()),
            'percentiles': {
                '25th': float(clv_values.quantile(0.25)),
                '50th': float(clv_values.quantile(0.50)),
                '75th': float(clv_values.quantile(0.75)),
                '90th': float(clv_values.quantile(0.90)),
                '95th': float(clv_values.quantile(0.95))
            },
            'total_clv': float(clv_values.sum()),
            'customer_count': len(clv_values)
        }
        
        # Pareto analysis (80/20 rule)
        clv_sorted = clv_values.sort_values(ascending=False)
        top_20_percent_count = int(len(clv_sorted) * 0.2)
        top_20_percent_clv = clv_sorted.head(top_20_percent_count).sum()
        pareto_ratio = top_20_percent_clv / clv_sorted.sum()
        
        distribution['pareto_analysis'] = {
            'top_20_percent_customers_contribute': float(pareto_ratio),
            'interpretation': f"Top 20% of customers contribute {pareto_ratio:.1%} of total CLV"
        }
        
        logger.info("CLV distribution analysis completed")
        return distribution
    
    def perform_trend_analysis(
        self,
        metric: str,
        periods: int = 12
    ) -> Dict[str, Any]:
        """Perform trend analysis on a metric over time.
        
        Args:
            metric: Metric to analyze (e.g., 'net_profit', 'clv')
            periods: Number of periods to analyze
        
        Returns:
            Dictionary with trend analysis results
        """
        logger.info(f"Performing trend analysis for metric: {metric}")
        
        # This would require historical data from fact_customer_metrics
        # For now, return placeholder
        
        return {
            'metric': metric,
            'trend': 'stable',
            'growth_rate': 0.0,
            'interpretation': 'Trend analysis requires historical data'
        }
