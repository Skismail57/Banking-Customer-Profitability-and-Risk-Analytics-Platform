"""Clustering algorithms for customer segmentation."""

from datetime import date
from typing import Dict, Any, List, Optional, Tuple
import logging

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.metrics import silhouette_score

from src.customer_segmentation.base import (
    CustomerSegmentationBase,
    SegmentationMethod,
)

logger = logging.getLogger(__name__)


class KMeansClusterer(CustomerSegmentationBase):
    """K-Means clustering with optimal cluster selection."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize K-Means clusterer.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
    
    def find_optimal_clusters(
        self,
        X: np.ndarray,
        max_clusters: int = 10,
        method: str = "silhouette"
    ) -> int:
        """Find optimal number of clusters.
        
        Args:
            X: Feature matrix
            max_clusters: Maximum number of clusters to try
            method: Method for optimal cluster selection (silhouette, elbow)
        
        Returns:
            Optimal number of clusters
        """
        if method == "silhouette":
            return self._find_optimal_silhouette(X, max_clusters)
        elif method == "elbow":
            return self._find_optimal_elbow(X, max_clusters)
        else:
            logger.warning(f"Unknown method {method}, using default 3")
            return 3
    
    def _find_optimal_silhouette(self, X: np.ndarray, max_clusters: int) -> int:
        """Find optimal clusters using silhouette score.
        
        Args:
            X: Feature matrix
            max_clusters: Maximum number of clusters
        
        Returns:
            Optimal number of clusters
        """
        silhouette_scores = []
        cluster_range = range(2, min(max_clusters + 1, len(X)))
        
        for n_clusters in cluster_range:
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(X)
            score = silhouette_score(X, cluster_labels)
            silhouette_scores.append(score)
            logger.info(f"Clusters: {n_clusters}, Silhouette Score: {score:.4f}")
        
        optimal_clusters = cluster_range[np.argmax(silhouette_scores)]
        logger.info(f"Optimal clusters (silhouette): {optimal_clusters}")
        
        return optimal_clusters
    
    def _find_optimal_elbow(self, X: np.ndarray, max_clusters: int) -> int:
        """Find optimal clusters using elbow method.
        
        Args:
            X: Feature matrix
            max_clusters: Maximum number of clusters
        
        Returns:
            Optimal number of clusters
        """
        inertias = []
        cluster_range = range(1, min(max_clusters + 1, len(X)))
        
        for n_clusters in cluster_range:
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            kmeans.fit(X)
            inertias.append(kmeans.inertia_)
            logger.info(f"Clusters: {n_clusters}, Inertia: {kmeans.inertia_:.4f}")
        
        # Simple elbow detection: find point of maximum curvature
        inertias = np.array(inertias)
        deltas = np.diff(inertias, 2)
        optimal_clusters = cluster_range[np.argmin(deltas) + 1]
        
        logger.info(f"Optimal clusters (elbow): {optimal_clusters}")
        
        return optimal_clusters
    
    def cluster(
        self,
        X: np.ndarray,
        n_clusters: int,
        random_state: int = 42
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Perform K-Means clustering.
        
        Args:
            X: Feature matrix
            n_clusters: Number of clusters
            random_state: Random state for reproducibility
        
        Returns:
            Tuple of (cluster labels, metadata)
        """
        kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
        cluster_labels = kmeans.fit_predict(X)
        
        metadata = {
            "method": SegmentationMethod.KMEANS.value,
            "n_clusters": n_clusters,
            "inertia": kmeans.inertia_,
            "centroids": kmeans.cluster_centers_.tolist()
        }
        
        return cluster_labels, metadata


class HierarchicalClusterer(CustomerSegmentationBase):
    """Hierarchical clustering for customer segmentation."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize hierarchical clusterer.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
    
    def cluster(
        self,
        X: np.ndarray,
        n_clusters: int,
        linkage: str = "ward"
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Perform hierarchical clustering.
        
        Args:
            X: Feature matrix
            n_clusters: Number of clusters
            linkage: Linkage method (ward, complete, average, single)
        
        Returns:
            Tuple of (cluster labels, metadata)
        """
        clustering = AgglomerativeClustering(
            n_clusters=n_clusters,
            linkage=linkage
        )
        cluster_labels = clustering.fit_predict(X)
        
        metadata = {
            "method": SegmentationMethod.HIERARCHICAL.value,
            "n_clusters": n_clusters,
            "linkage": linkage
        }
        
        return cluster_labels, metadata


class DBSCANClusterer(CustomerSegmentationBase):
    """DBSCAN clustering for customer segmentation."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize DBSCAN clusterer.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
    
    def cluster(
        self,
        X: np.ndarray,
        eps: float = 0.5,
        min_samples: int = 5
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Perform DBSCAN clustering.
        
        Args:
            X: Feature matrix
            eps: Maximum distance between samples
            min_samples: Minimum samples in neighborhood
        
        Returns:
            Tuple of (cluster labels, metadata)
        """
        clustering = DBSCAN(eps=eps, min_samples=min_samples)
        cluster_labels = clustering.fit_predict(X)
        
        n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
        n_noise = list(cluster_labels).count(-1)
        
        metadata = {
            "method": SegmentationMethod.DBSCAN.value,
            "eps": eps,
            "min_samples": min_samples,
            "n_clusters": n_clusters,
            "n_noise": n_noise
        }
        
        return cluster_labels, metadata
