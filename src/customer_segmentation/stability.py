"""Segment stability analysis."""

from datetime import date
from typing import Dict, Any, List, Optional
import logging

import pandas as pd
import numpy as np
from sklearn.metrics import adjusted_rand_score, adjusted_mutual_info_score

from src.customer_segmentation.base import CustomerSegmentationBase

logger = logging.getLogger(__name__)


class StabilityAnalyzer(CustomerSegmentationBase):
    """Analyze stability of segmentation over time or across methods."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize stability analyzer.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
    
    def compare_segmentations(
        self,
        labels1: np.ndarray,
        labels2: np.ndarray,
        method: str = "ari"
    ) -> Dict[str, Any]:
        """Compare two segmentations.
        
        Args:
            labels1: First set of cluster labels
            labels2: Second set of cluster labels
            method: Comparison method (ari, ami)
        
        Returns:
            Dictionary with comparison metrics
        """
        if len(labels1) != len(labels2):
            logger.error("Label arrays must have same length")
            return {"error": "Label arrays must have same length"}
        
        if method == "ari":
            score = adjusted_rand_score(labels1, labels2)
            metric_name = "Adjusted Rand Index"
        elif method == "ami":
            score = adjusted_mutual_info_score(labels1, labels2)
            metric_name = "Adjusted Mutual Information"
        else:
            logger.warning(f"Unknown method {method}, using ARI")
            score = adjusted_rand_score(labels1, labels2)
            metric_name = "Adjusted Rand Index"
        
        # Interpret score
        if score > 0.8:
            stability = "Very stable"
        elif score > 0.6:
            stability = "Stable"
        elif score > 0.4:
            stability = "Moderately stable"
        else:
            stability = "Unstable"
        
        return {
            "metric": metric_name,
            "score": score,
            "stability": stability,
            "interpretation": f"{metric_name} of {score:.4f} indicates {stability} segmentation"
        }
    
    def bootstrap_stability(
        self,
        X: np.ndarray,
        clusterer,
        n_bootstrap: int = 10,
        sample_ratio: float = 0.8,
        random_state: int = 42
    ) -> Dict[str, Any]:
        """Assess stability using bootstrap sampling.
        
        Args:
            X: Feature matrix
            clusterer: Clustering algorithm with fit_predict method
            n_bootstrap: Number of bootstrap iterations
            sample_ratio: Ratio of data to sample each iteration
            random_state: Random state for reproducibility
        
        Returns:
            Dictionary with stability metrics
        """
        np.random.seed(random_state)
        n_samples = len(X)
        
        # Original clustering
        original_labels = clusterer.fit_predict(X)
        
        stability_scores = []
        
        for i in range(n_bootstrap):
            # Bootstrap sample
            sample_indices = np.random.choice(
                n_samples,
                size=int(n_samples * sample_ratio),
                replace=True
            )
            X_sample = X[sample_indices]
            
            # Cluster on sample
            sample_labels = clusterer.fit_predict(X_sample)
            
            # Map back to original indices
            original_sample_labels = original_labels[sample_indices]
            
            # Calculate ARI
            score = adjusted_rand_score(original_sample_labels, sample_labels)
            stability_scores.append(score)
        
        mean_stability = np.mean(stability_scores)
        std_stability = np.std(stability_scores)
        
        if mean_stability > 0.8:
            stability = "Very stable"
        elif mean_stability > 0.6:
            stability = "Stable"
        elif mean_stability > 0.4:
            stability = "Moderately stable"
        else:
            stability = "Unstable"
        
        return {
            "mean_stability": mean_stability,
            "std_stability": std_stability,
            "stability": stability,
            "bootstrap_scores": stability_scores,
            "interpretation": f"Mean ARI of {mean_stability:.4f} indicates {stability} clustering"
        }
    
    def temporal_stability(
        self,
        segmentations: Dict[str, np.ndarray],
        reference_period: str
    ) -> pd.DataFrame:
        """Analyze stability across time periods.
        
        Args:
            segmentations: Dictionary of period to cluster labels
            reference_period: Reference period to compare against
        
        Returns:
            DataFrame with temporal stability metrics
        """
        if reference_period not in segmentations:
            logger.error(f"Reference period {reference_period} not found")
            return pd.DataFrame()
        
        reference_labels = segmentations[reference_period]
        results = []
        
        for period, labels in segmentations.items():
            if period == reference_period:
                continue
            
            comparison = self.compare_segmentations(reference_labels, labels)
            results.append({
                "period": period,
                "reference_period": reference_period,
                "stability_score": comparison["score"],
                "stability": comparison["stability"]
            })
        
        return pd.DataFrame(results)
