"""Portfolio Concentration Analysis.

This module implements comprehensive concentration analysis to identify
portfolio concentration risks across multiple dimensions.

Key Concentration Metrics:
- Herfindahl-Hirschman Index (HHI)
- Gini Coefficient
- Concentration Ratios (CR3, CR5, CR10)
- Sector/Geographic concentration
- Large exposure limits

NOTE: This is an analytical/educational model for decision support.
It does not make actual lending decisions.
"""

from typing import Dict, Any, List, Optional
import logging

import pandas as pd
import numpy as np

from src.advanced_risk_analytics.base import RiskBase

logger = logging.getLogger(__name__)


class ConcentrationAnalyzer(RiskBase):
    """Analyze concentration across various dimensions.
    
    This class implements comprehensive concentration analysis to identify
    portfolio concentration risks.
    
    Assumptions:
    - Concentration thresholds based on regulatory guidelines
    - HHI interpretation follows standard banking practices
    - Concentration ratios are calculated on exposure amounts
    
    Limitations:
    - Does not account for correlation between exposures
    - Assumes independence of concentration risks
    - May not capture all dimensions of concentration
    - Thresholds may need calibration for different portfolios
    
    Fairness Considerations:
    - Analyze concentration across demographic groups
    - Check for disparate impact in concentration limits
    - Ensure diversification benefits are accessible to all segments
    - Regular audit for bias in concentration assessment
    """
    
    def analyze_segment_concentration(
        self,
        df: pd.DataFrame,
        segment_column: str = "segment",
        exposure_column: str = "exposure_amount"
    ) -> Dict[str, Any]:
        """Analyze concentration by segment.
        
        Args:
            df: DataFrame with customer data
            segment_column: Name of segment column
            exposure_column: Name of exposure column
        
        Returns:
            Dictionary with concentration analysis
        """
        total_exposure = df[exposure_column].sum()
        
        # Calculate concentration by segment
        segment_exposure = df.groupby(segment_column)[exposure_column].sum()
        segment_exposure_pct = segment_exposure / total_exposure
        
        # Identify concentrated segments
        warning_threshold = 0.25  # 25%
        critical_threshold = 0.40  # 40%
        
        warning_segments = segment_exposure_pct[segment_exposure_pct >= warning_threshold]
        critical_segments = segment_exposure_pct[segment_exposure_pct >= critical_threshold]
        
        # Calculate HHI
        hhi = (segment_exposure_pct ** 2).sum()
        
        # Calculate concentration ratios
        sorted_exposure = segment_exposure_pct.sort_values(ascending=False)
        cr3 = sorted_exposure.head(3).sum()
        cr5 = sorted_exposure.head(5).sum()
        cr10 = sorted_exposure.head(10).sum()
        
        # Calculate Gini coefficient
        gini = self._calculate_gini_coefficient(sorted_exposure.values)
        
        return {
            "segment_exposure": segment_exposure.to_dict(),
            "segment_exposure_pct": segment_exposure_pct.to_dict(),
            "warning_segments": warning_segments.to_dict(),
            "critical_segments": critical_segments.to_dict(),
            "hhi": float(hhi),
            "hhi_interpretation": self._interpret_hhi(hhi),
            "cr3": float(cr3),
            "cr5": float(cr5),
            "cr10": float(cr10),
            "gini_coefficient": float(gini),
            "total_exposure": float(total_exposure),
            "assumptions": [
                'HHI interpretation: <0.15 unconcentrated, 0.15-0.25 moderately concentrated, >0.25 highly concentrated',
                'Concentration ratios based on exposure amounts',
                'Warning threshold: 25%, Critical threshold: 40%'
            ],
            "limitations": [
                'Does not account for correlation between exposures',
                'Assumes independence of concentration risks',
                'May not capture all dimensions of concentration',
                'Thresholds may need calibration'
            ]
        }
    
    def analyze_geographic_concentration(
        self,
        df: pd.DataFrame,
        region_column: str = "region",
        exposure_column: str = "exposure_amount"
    ) -> Dict[str, Any]:
        """Analyze concentration by geographic region.
        
        Args:
            df: DataFrame with customer data
            region_column: Name of region column
            exposure_column: Name of exposure column
        
        Returns:
            Dictionary with geographic concentration analysis
        """
        total_exposure = df[exposure_column].sum()
        
        # Calculate concentration by region
        region_exposure = df.groupby(region_column)[exposure_column].sum()
        region_exposure_pct = region_exposure / total_exposure
        
        # Calculate HHI
        hhi = (region_exposure_pct ** 2).sum()
        
        # Calculate concentration ratios
        sorted_exposure = region_exposure_pct.sort_values(ascending=False)
        cr3 = sorted_exposure.head(3).sum()
        cr5 = sorted_exposure.head(5).sum()
        
        return {
            "region_exposure": region_exposure.to_dict(),
            "region_exposure_pct": region_exposure_pct.to_dict(),
            "hhi": float(hhi),
            "hhi_interpretation": self._interpret_hhi(hhi),
            "cr3": float(cr3),
            "cr5": float(cr5),
            "total_exposure": float(total_exposure)
        }
    
    def analyze_product_concentration(
        self,
        df: pd.DataFrame,
        product_column: str = "product_category",
        exposure_column: str = "exposure_amount"
    ) -> Dict[str, Any]:
        """Analyze concentration by product type.
        
        Args:
            df: DataFrame with customer data
            product_column: Name of product column
            exposure_column: Name of exposure column
        
        Returns:
            Dictionary with product concentration analysis
        """
        total_exposure = df[exposure_column].sum()
        
        # Calculate concentration by product
        product_exposure = df.groupby(product_column)[exposure_column].sum()
        product_exposure_pct = product_exposure / total_exposure
        
        # Calculate HHI
        hhi = (product_exposure_pct ** 2).sum()
        
        return {
            "product_exposure": product_exposure.to_dict(),
            "product_exposure_pct": product_exposure_pct.to_dict(),
            "hhi": float(hhi),
            "hhi_interpretation": self._interpret_hhi(hhi),
            "total_exposure": float(total_exposure)
        }
    
    def analyze_large_exposures(
        self,
        df: pd.DataFrame,
        customer_column: str = "customer_key",
        exposure_column: str = "exposure_amount",
        large_exposure_threshold: float = 0.10
    ) -> Dict[str, Any]:
        """Analyze large exposures (single customer concentration).
        
        Args:
            df: DataFrame with customer data
            customer_column: Name of customer column
            exposure_column: Name of exposure column
            large_exposure_threshold: Threshold for large exposure (default 10%)
        
        Returns:
            Dictionary with large exposure analysis
        """
        total_exposure = df[exposure_column].sum()
        
        # Calculate exposure per customer with percentage
        customer_exposure = df.groupby(customer_column)[exposure_column].sum()
        customer_exposure_pct = customer_exposure / total_exposure
        
        # Identify large exposures
        large_exposures = customer_exposure_pct[customer_exposure_pct >= large_exposure_threshold]
        
        # Sort by exposure
        large_exposures_sorted = large_exposures.sort_values(ascending=False)
        
        return {
            "large_exposures": large_exposures_sorted.to_dict(),
            "large_exposure_count": len(large_exposures),
            "large_exposure_total_pct": float(large_exposures.sum()),
            "threshold": large_exposure_threshold,
            "total_exposure": float(total_exposure)
        }
    
    def _calculate_gini_coefficient(self, values: np.ndarray) -> float:
        """Calculate Gini coefficient for concentration measurement.
        
        Args:
            values: Array of values (exposure percentages)
        
        Returns:
            Gini coefficient (0 = perfect equality, 1 = perfect inequality)
        """
        sorted_values = np.sort(values)
        n = len(values)
        cumsum = np.cumsum(sorted_values)
        
        return (n + 1 - 2 * np.sum(cumsum) / cumsum[-1]) / n if cumsum[-1] > 0 else 0
    
    def _interpret_hhi(self, hhi: float) -> str:
        """Interpret HHI value.
        
        Args:
            hhi: HHI value
        
        Returns:
            Interpretation string
        """
        if hhi < 0.15:
            return "Unconcentrated"
        elif hhi < 0.25:
            return "Moderately concentrated"
        else:
            return "Highly concentrated"
    
    def generate_concentration_report(
        self,
        df: pd.DataFrame
    ) -> Dict[str, Any]:
        """Generate comprehensive concentration report.
        
        Args:
            df: DataFrame with portfolio data
        
        Returns:
            Dictionary with concentration report
        """
        logger.info("Generating concentration report")
        
        report = {
            'segment_concentration': self.analyze_segment_concentration(df),
            'geographic_concentration': self.analyze_geographic_concentration(df) if 'region' in df.columns else {},
            'product_concentration': self.analyze_product_concentration(df) if 'product_category' in df.columns else {},
            'large_exposures': self.analyze_large_exposures(df),
            'assumptions': [
                'HHI interpretation: <0.15 unconcentrated, 0.15-0.25 moderately concentrated, >0.25 highly concentrated',
                'Large exposure threshold: 10% of total exposure',
                'Concentration ratios based on exposure amounts'
            ],
            'limitations': [
                'Does not account for correlation between exposures',
                'Assumes independence of concentration risks',
                'May not capture all dimensions of concentration',
                'Thresholds may need calibration'
            ],
            'fairness_considerations': [
                'Analyze concentration across demographic groups',
                'Check for disparate impact in concentration limits',
                'Ensure diversification benefits are accessible',
                'Regular audit for bias in concentration assessment'
            ]
        }
        
        logger.info("Concentration report generated")
        return report
