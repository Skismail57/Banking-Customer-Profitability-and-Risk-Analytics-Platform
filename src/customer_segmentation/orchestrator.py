"""Orchestrator for customer segmentation."""

from datetime import date
from typing import Dict, Any, List, Optional
import logging

import pandas as pd
import numpy as np

from src.customer_segmentation.base import (
    CustomerSegmentationBase,
    SegmentationMethod,
)
from src.customer_segmentation.business_rules import BusinessRuleSegmenter
from src.customer_segmentation.features import FeatureEngineer
from src.customer_segmentation.clustering import (
    KMeansClusterer,
    HierarchicalClusterer,
    DBSCANClusterer,
)
from src.customer_segmentation.evaluation import ClusterEvaluator
from src.customer_segmentation.profiling import SegmentProfiler
from src.customer_segmentation.stability import StabilityAnalyzer

logger = logging.getLogger(__name__)


class SegmentationOrchestrator(CustomerSegmentationBase):
    """Orchestrates customer segmentation operations."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize segmentation orchestrator.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
        
        # Initialize components
        self.business_segmenter = BusinessRuleSegmenter(as_of_date)
        self.feature_engineer = FeatureEngineer(as_of_date)
        self.kmeans_clusterer = KMeansClusterer(as_of_date)
        self.hierarchical_clusterer = HierarchicalClusterer(as_of_date)
        self.dbscan_clusterer = DBSCANClusterer(as_of_date)
        self.evaluator = ClusterEvaluator(as_of_date)
        self.profiler = SegmentProfiler(as_of_date)
        self.stability_analyzer = StabilityAnalyzer(as_of_date)
    
    def run_business_rule_segmentation(
        self,
        df: pd.DataFrame,
        segment_type: str = "combined"
    ) -> Dict[str, Any]:
        """Run business-rule based segmentation.
        
        Args:
            df: DataFrame with customer data
            segment_type: Type of segmentation (profitability, behavior, lifecycle, combined)
        
        Returns:
            Dictionary with segmentation results
        """
        logger.info(f"Running business-rule segmentation: {segment_type}")
        
        if segment_type == "profitability":
            result_df = self.business_segmenter.segment_by_profitability(df)
        elif segment_type == "behavior":
            result_df = self.business_segmenter.segment_by_behavior(df)
        elif segment_type == "lifecycle":
            result_df = self.business_segmenter.segment_by_lifecycle(df)
        elif segment_type == "combined":
            result_df = self.business_segmenter.segment_combined(df)
        else:
            logger.error(f"Unknown segment type: {segment_type}")
            return {"error": f"Unknown segment type: {segment_type}"}
        
        # Count segments
        segment_counts = result_df["segment"].value_counts().to_dict()
        
        return {
            "method": SegmentationMethod.BUSINESS_RULES.value,
            "segment_type": segment_type,
            "segment_counts": segment_counts,
            "segmented_df": result_df
        }
    
    def run_clustering_segmentation(
        self,
        df: pd.DataFrame,
        feature_columns: List[str],
        method: str = "kmeans",
        n_clusters: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Run data-driven clustering segmentation.
        
        Args:
            df: DataFrame with customer data
            feature_columns: List of feature columns to use
            method: Clustering method (kmeans, hierarchical, dbscan)
            n_clusters: Number of clusters (for kmeans/hierarchical)
            **kwargs: Additional method-specific parameters
        
        Returns:
            Dictionary with clustering results
        """
        logger.info(f"Running clustering segmentation: {method}")
        
        # Extract features
        features_df = self.feature_engineer.extract_features(df, feature_columns)
        
        # Handle missing values
        features_df = self.feature_engineer.handle_missing_values(features_df, strategy="median")
        
        # Scale features
        features_scaled = self.feature_engineer.scale_features(features_df, method="standard")
        
        X = features_scaled.values
        
        # Perform clustering
        if method == "kmeans":
            if n_clusters is None:
                n_clusters = self.kmeans_clusterer.find_optimal_clusters(X, max_clusters=10)
                logger.info(f"Optimal clusters found: {n_clusters}")
            
            cluster_labels, metadata = self.kmeans_clusterer.cluster(X, n_clusters)
        
        elif method == "hierarchical":
            if n_clusters is None:
                n_clusters = 4  # Default for hierarchical
                logger.info(f"Using default clusters: {n_clusters}")
            
            linkage = kwargs.get("linkage", "ward")
            cluster_labels, metadata = self.hierarchical_clusterer.cluster(X, n_clusters, linkage)
        
        elif method == "dbscan":
            eps = kwargs.get("eps", 0.5)
            min_samples = kwargs.get("min_samples", 5)
            cluster_labels, metadata = self.dbscan_clusterer.cluster(X, eps, min_samples)
        
        else:
            logger.error(f"Unknown clustering method: {method}")
            return {"error": f"Unknown clustering method: {method}"}
        
        # Add cluster labels to original dataframe
        result_df = df.copy()
        result_df["cluster"] = cluster_labels
        
        # Evaluate clustering
        evaluation = self.evaluator.evaluate(X, cluster_labels)
        
        return {
            "method": method,
            "metadata": metadata,
            "evaluation": evaluation,
            "segmented_df": result_df,
            "features_used": feature_columns
        }
    
    def compare_segmentation_methods(
        self,
        df: pd.DataFrame,
        feature_columns: List[str],
        methods: List[str] = None
    ) -> Dict[str, Any]:
        """Compare multiple segmentation methods.
        
        Args:
            df: DataFrame with customer data
            feature_columns: List of feature columns to use
            methods: List of methods to compare
        
        Returns:
            Dictionary with comparison results
        """
        if methods is None:
            methods = ["kmeans", "hierarchical"]
        
        logger.info(f"Comparing segmentation methods: {methods}")
        
        results = {}
        clusterings = {}
        
        # Extract and prepare features once
        features_df = self.feature_engineer.extract_features(df, feature_columns)
        features_df = self.feature_engineer.handle_missing_values(features_df, strategy="median")
        features_scaled = self.feature_engineer.scale_features(features_df, method="standard")
        X = features_scaled.values
        
        # Run each method
        for method in methods:
            if method == "kmeans":
                n_clusters = self.kmeans_clusterer.find_optimal_clusters(X, max_clusters=10)
                labels, metadata = self.kmeans_clusterer.cluster(X, n_clusters)
            elif method == "hierarchical":
                labels, metadata = self.hierarchical_clusterer.cluster(X, 4)
            elif method == "dbscan":
                labels, metadata = self.dbscan_clusterer.cluster(X, 0.5, 5)
            else:
                continue
            
            results[method] = {
                "labels": labels,
                "metadata": metadata,
                "evaluation": self.evaluator.evaluate(X, labels)
            }
            clusterings[method] = labels
        
        # Compare clusterings
        comparison_df = self.evaluator.compare_clusterings(X, clusterings)
        
        return {
            "method_results": results,
            "comparison": comparison_df.to_dict("records")
        }
    
    def generate_segment_profiles(
        self,
        df: pd.DataFrame,
        feature_columns: List[str]
    ) -> Dict[str, Any]:
        """Generate segment profiles.
        
        Args:
            df: DataFrame with customer data and cluster labels
            feature_columns: List of feature columns to profile
        
        Returns:
            Dictionary with segment profiles
        """
        logger.info("Generating segment profiles")
        
        profiles = self.profiler.profile_all_segments(df, feature_columns)
        summary_df = self.profiler.create_segment_summary(profiles)
        
        # Generate business interpretations
        interpretations = []
        for profile in profiles:
            interpretation = self.profiler.generate_business_interpretation(profile)
            interpretations.append(interpretation)
        
        return {
            "profiles": [p.to_dict() for p in profiles],
            "summary": summary_df.to_dict("records"),
            "interpretations": interpretations
        }
    
    def analyze_stability(
        self,
        X: np.ndarray,
        clusterer,
        method: str = "bootstrap"
    ) -> Dict[str, Any]:
        """Analyze segmentation stability.
        
        Args:
            X: Feature matrix
            clusterer: Clustering algorithm
            method: Stability analysis method (bootstrap)
        
        Returns:
            Dictionary with stability analysis
        """
        logger.info(f"Analyzing stability using {method}")
        
        if method == "bootstrap":
            return self.stability_analyzer.bootstrap_stability(X, clusterer)
        else:
            logger.error(f"Unknown stability method: {method}")
            return {"error": f"Unknown stability method: {method}"}
