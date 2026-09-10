"""Model comparison framework."""

from typing import Dict, Any, List
import logging

import pandas as pd

from src.predictive_analytics.base import ModelBase, ModelResult

logger = logging.getLogger(__name__)


class ModelComparator(ModelBase):
    """Compare multiple models."""
    
    def compare_models(
        self,
        results: List[ModelResult],
        primary_metric: str = "f1"
    ) -> pd.DataFrame:
        """Compare model results.
        
        Args:
            results: List of ModelResult objects
            primary_metric: Primary metric for ranking
        
        Returns:
            DataFrame with comparison
        """
        comparison_data = []
        
        for result in results:
            row = {
                "model_name": result.model_name,
                "training_time": result.training_time
            }
            row.update(result.metrics)
            comparison_data.append(row)
        
        comparison_df = pd.DataFrame(comparison_data)
        
        # Sort by primary metric (descending for most metrics)
        if primary_metric in comparison_df.columns:
            comparison_df = comparison_df.sort_values(primary_metric, ascending=False)
        
        return comparison_df
    
    def select_best_model(
        self,
        results: List[ModelResult],
        primary_metric: str = "f1"
    ) -> ModelResult:
        """Select best model based on primary metric.
        
        Args:
            results: List of ModelResult objects
            primary_metric: Primary metric for selection
        
        Returns:
            Best ModelResult
        """
        comparison_df = self.compare_models(results, primary_metric)
        
        best_model_name = comparison_df.iloc[0]["model_name"]
        
        for result in results:
            if result.model_name == best_model_name:
                return result
        
        return results[0]
