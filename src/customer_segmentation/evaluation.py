"""Cluster evaluation metrics."""

from datetime import date
from typing import Dict, Any, List, Optional
import logging

import pandas as pd
import numpy as np
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score

from src.customer_segmentation.base import CustomerSegmentationBase

logger = logging.getLogger(__name__)


class ClusterEvaluator(CustomerSegmentationBase):
    """Evaluate clustering results."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize cluster evaluator.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
    
    def evaluate(
        self,
        X: np.ndarray,
        cluster_labels: np.ndarray
    ) -> Dict[str, Any]:
        """Evaluate clustering results using multiple metrics.
        
        Args:
            X: Feature matrix
            cluster_labels: Cluster labels
        
        Returns:
            Dictionary with evaluation metrics
        """
        evaluation = {
            "silhouette_score": self._calculate_silhouette(X, cluster_labels),
            "calinski_harabasz_score": self._calculate_calinski_harabasz(X, cluster_labels),
            "davies_bouldin_score": self._calculate_davies_bouldin(X, cluster_labels),
            "cluster_sizes": self._calculate_cluster_sizes(cluster_labels),
            "cluster_balance": self._calculate_cluster_balance(cluster_labels)
        }
        
        return evaluation
    
    def _calculate_silhouette(
        self,
        X: np.ndarray,
        cluster_labels: np.ndarray
    ) -> Dict[str, Any]:
        """Calculate silhouette score.
        
        Args:
            X: Feature matrix
            cluster_labels: Cluster labels
        
        Returns:
            Dictionary with silhouette score and interpretation
        """
        n_clusters = len(set(cluster_labels))
        
        if n_clusters < 2:
            return {
                "score": None,
                "interpretation": "Insufficient clusters for silhouette score"
            }
        
        score = silhouette_score(X, cluster_labels)
        
        if score > 0.7:
            interpretation = "Strong structure"
        elif score > 0.5:
            interpretation = "Reasonable structure"
        elif score > 0.25:
            interpretation = "Weak structure"
        else:
            interpretation = "No substantial structure"
        
        return {
            "score": score,
            "interpretation": interpretation
        }
    
    def _calculate_calinski_harabasz(
        self,
        X: np.ndarray,
        cluster_labels: np.ndarray
    ) -> Dict[str, Any]:
        """Calculate Calinski-Harabasz score.
        
        Args:
            X: Feature matrix
            cluster_labels: Cluster labels
        
        Returns:
            Dictionary with score and interpretation
        """
        n_clusters = len(set(cluster_labels))
        
        if n_clusters < 2:
            return {
                "score": None,
                "interpretation": "Insufficient clusters for CH score"
            }
        
        score = calinski_harabasz_score(X, cluster_labels)
        
        # Higher is better, interpretation depends on context
        return {
            "score": score,
            "interpretation": "Higher values indicate better defined clusters"
        }
    
    def _calculate_davies_bouldin(
        self,
        X: np.ndarray,
        cluster_labels: np.ndarray
    ) -> Dict[str, Any]:
        """Calculate Davies-Bouldin score.
        
        Args:
            X: Feature matrix
            cluster_labels: Cluster labels
        
        Returns:
            Dictionary with score and interpretation
        """
        n_clusters = len(set(cluster_labels))
        
        if n_clusters < 2:
            return {
                "score": None,
                "interpretation": "Insufficient clusters for DB score"
            }
        
        score = davies_bouldin_score(X, cluster_labels)
        
        # Lower is better
        if score < 0.5:
            interpretation = "Well-separated clusters"
        elif score < 1.0:
            interpretation = "Reasonably separated clusters"
        else:
            interpretation = "Poorly separated clusters"
        
        return {
            "score": score,
            "interpretation": interpretation
        }
    
    def _calculate_cluster_sizes(
        self,
        cluster_labels: np.ndarray
    ) -> Dict[str, Any]:
        """Calculate cluster sizes.
        
        Args:
            cluster_labels: Cluster labels
        
        Returns:
            Dictionary with cluster size statistics
        """
        unique_labels, counts = np.unique(cluster_labels, return_counts=True)
        
        size_dict = {str(label): int(count) for label, count in zip(unique_labels, counts)}
        
        return {
            "sizes": size_dict,
            "min_size": int(counts.min()),
            "max_size": int(counts.max()),
            "mean_size": float(counts.mean()),
            "std_size": float(counts.std())
        }
    
    def _calculate_cluster_balance(
        self,
        cluster_labels: np.ndarray
    ) -> Dict[str, Any]:
        """Calculate cluster balance.
        
        Args:
            cluster_labels: Cluster labels
        
        Returns:
            Dictionary with balance metrics
        """
        unique_labels, counts = np.unique(cluster_labels, return_counts=True)
        
        # Calculate coefficient of variation of cluster sizes
        cv = counts.std() / counts.mean() if counts.mean() > 0 else 0
        
        # Calculate Gini coefficient (inequality measure)
        sorted_counts = np.sort(counts)
        n = len(sorted_counts)
        cumsum = np.cumsum(sorted_counts)
        gini = (n + 1 - 2 * np.sum(cumsum) / cumsum[-1]) / n if cumsum[-1] > 0 else 0
        
        if cv < 0.3:
            balance = "Well-balanced"
        elif cv < 0.5:
            balance = "Moderately balanced"
        else:
            balance = "Poorly balanced"
        
        return {
            "coefficient_of_variation": cv,
            "gini_coefficient": gini,
            "balance": balance
        }
    
    def compare_clusterings(
        self,
        X: np.ndarray,
        clusterings: Dict[str, np.ndarray]
    ) -> pd.DataFrame:
        """Compare multiple clustering results.
        
        Args:
            X: Feature matrix
            clusterings: Dictionary of clustering method to labels
        
        Returns:
            DataFrame with comparison
        """
        results = []
        
        for method_name, labels in clusterings.items():
            evaluation = self.evaluate(X, labels)
            results.append({
                "method": method_name,
                "silhouette_score": evaluation["silhouette_score"]["score"],
                "calinski_harabasz_score": evaluation["calinski_harabasz_score"]["score"],
                "davies_bouldin_score": evaluation["davies_bouldin_score"]["score"],
                "n_clusters": len(set(labels)),
                "cluster_balance": evaluation["cluster_balance"]["balance"]
            })
        
        return pd.DataFrame(results)
