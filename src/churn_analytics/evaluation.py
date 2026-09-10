"""Churn model evaluation (precision, recall, F1, ROC-AUC, PR-AUC, calibration)."""

from datetime import date
from typing import Dict, Any, Optional
import logging

import pandas as pd
import numpy as np
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    precision_recall_curve,
    auc,
    confusion_matrix
)
from sklearn.calibration import calibration_curve

from src.churn_analytics.base import ChurnBase

logger = logging.getLogger(__name__)


class ChurnModelEvaluator(ChurnBase):
    """Evaluate churn prediction models with focus on interpretability."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize churn model evaluator.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
    
    def evaluate(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_proba: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """Evaluate model predictions.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_proba: Predicted probabilities (optional)
        
        Returns:
            Dictionary with evaluation metrics
        """
        evaluation = {
            "precision": precision_score(y_true, y_pred, zero_division=0),
            "recall": recall_score(y_true, y_pred, zero_division=0),
            "f1": f1_score(y_true, y_pred, zero_division=0),
            "confusion_matrix": confusion_matrix(y_true, y_pred).tolist()
        }
        
        if y_proba is not None:
            evaluation["roc_auc"] = roc_auc_score(y_true, y_proba[:, 1])
            
            # PR-AUC
            precision, recall, _ = precision_recall_curve(y_true, y_proba[:, 1])
            evaluation["pr_auc"] = auc(recall, precision)
            
            # Calibration
            prob_true, prob_pred = calibration_curve(y_true, y_proba[:, 1], n_bins=10)
            evaluation["calibration"] = {
                "prob_true": prob_true.tolist(),
                "prob_pred": prob_pred.tolist()
            }
        
        return evaluation
    
    def evaluate_model_comparison(
        self,
        y_true: np.ndarray,
        model_predictions: Dict[str, Dict[str, np.ndarray]]
    ) -> pd.DataFrame:
        """Compare multiple models.
        
        Args:
            y_true: True labels
            model_predictions: Dictionary of model name to {y_pred, y_proba}
        
        Returns:
            DataFrame with comparison
        """
        results = []
        
        for model_name, predictions in model_predictions.items():
            y_pred = predictions["y_pred"]
            y_proba = predictions.get("y_proba")
            
            metrics = self.evaluate(y_true, y_pred, y_proba)
            metrics["model"] = model_name
            results.append(metrics)
        
        return pd.DataFrame(results)
    
    def get_feature_importance_comparison(
        self,
        models: Dict[str, Any]
    ) -> pd.DataFrame:
        """Compare feature importance across models.
        
        Args:
            models: Dictionary of model name to model object
        
        Returns:
            DataFrame with feature importance comparison
        """
        importance_data = []
        
        for model_name, model in models.items():
            if hasattr(model, "get_feature_importance"):
                importance_df = model.get_feature_importance()
                importance_df["model"] = model_name
                importance_data.append(importance_df)
        
        if importance_data:
            return pd.concat(importance_data, ignore_index=True)
        else:
            return pd.DataFrame()
    
    def calculate_business_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_proba: np.ndarray,
        retention_cost: float = 100.0,
        acquisition_cost: float = 500.0
    ) -> Dict[str, Any]:
        """Calculate business-relevant metrics.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_proba: Predicted probabilities
            retention_cost: Cost of retention intervention
            acquisition_cost: Cost of customer acquisition
        
        Returns:
            Dictionary with business metrics
        """
        # True positives: correctly identified churners
        tp = ((y_true == 1) & (y_pred == 1)).sum()
        
        # False positives: incorrectly flagged as churners
        fp = ((y_true == 0) & (y_pred == 1)).sum()
        
        # False negatives: missed churners
        fn = ((y_true == 1) & (y_pred == 0)).sum()
        
        # Cost of intervention (TP + FP)
        intervention_cost = (tp + fp) * retention_cost
        
        # Cost of missed churn (FN)
        missed_churn_cost = fn * acquisition_cost
        
        # Total cost
        total_cost = intervention_cost + missed_churn_cost
        
        # Savings compared to no intervention
        no_intervention_cost = (y_true == 1).sum() * acquisition_cost
        savings = no_intervention_cost - total_cost
        
        return {
            "true_positives": int(tp),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "intervention_cost": intervention_cost,
            "missed_churn_cost": missed_churn_cost,
            "total_cost": total_cost,
            "no_intervention_cost": no_intervention_cost,
            "savings": savings,
            "savings_percentage": (savings / no_intervention_cost * 100) if no_intervention_cost > 0 else 0
        }
