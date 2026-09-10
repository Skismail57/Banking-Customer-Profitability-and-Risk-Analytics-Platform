"""Model evaluation with appropriate metrics."""

from typing import Dict, Any, List, Optional
import logging

import pandas as pd
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    precision_recall_curve,
    auc,
    confusion_matrix,
    mean_squared_error,
    mean_absolute_error,
    r2_score
)

from src.predictive_analytics.base import ModelBase, ProblemType

logger = logging.getLogger(__name__)


class ModelEvaluator(ModelBase):
    """Evaluate models with appropriate metrics."""
    
    def evaluate_classification(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_proba: Optional[np.ndarray] = None
    ) -> Dict[str, float]:
        """Evaluate classification model.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_proba: Predicted probabilities (optional)
        
        Returns:
            Dictionary with classification metrics
        """
        metrics = {
            "accuracy": accuracy_score(y_true, y_pred),
            "precision": precision_score(y_true, y_pred, average="binary", zero_division=0),
            "recall": recall_score(y_true, y_pred, average="binary", zero_division=0),
            "f1": f1_score(y_true, y_pred, average="binary", zero_division=0),
            "confusion_matrix": confusion_matrix(y_true, y_pred).tolist()
        }
        
        if y_proba is not None:
            metrics["roc_auc"] = roc_auc_score(y_true, y_proba[:, 1])
            
            # PR-AUC
            precision, recall, _ = precision_recall_curve(y_true, y_proba[:, 1])
            metrics["pr_auc"] = auc(recall, precision)
        
        return metrics
    
    def evaluate_regression(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray
    ) -> Dict[str, float]:
        """Evaluate regression model.
        
        Args:
            y_true: True values
            y_pred: Predicted values
        
        Returns:
            Dictionary with regression metrics
        """
        mse = mean_squared_error(y_true, y_pred)
        
        return {
            "mse": mse,
            "rmse": np.sqrt(mse),
            "mae": mean_absolute_error(y_true, y_pred),
            "r2": r2_score(y_true, y_pred)
        }
    
    def evaluate_model(
        self,
        model,
        X_test: pd.DataFrame,
        y_test: pd.Series,
        problem_type: ProblemType
    ) -> Dict[str, float]:
        """Evaluate model based on problem type.
        
        Args:
            model: Trained model
            X_test: Test features
            y_test: Test target
            problem_type: Type of ML problem
        
        Returns:
            Dictionary with evaluation metrics
        """
        y_pred = model.predict(X_test)
        
        if problem_type == ProblemType.BINARY_CLASSIFICATION:
            y_proba = model.predict_proba(X_test) if hasattr(model, "predict_proba") else None
            return self.evaluate_classification(y_test.values, y_pred, y_proba)
        
        elif problem_type == ProblemType.MULTICLASS_CLASSIFICATION:
            return {
                "accuracy": accuracy_score(y_test.values, y_pred),
                "precision_macro": precision_score(y_test.values, y_pred, average="macro", zero_division=0),
                "recall_macro": recall_score(y_test.values, y_pred, average="macro", zero_division=0),
                "f1_macro": f1_score(y_test.values, y_pred, average="macro", zero_division=0)
            }
        
        elif problem_type == ProblemType.REGRESSION:
            return self.evaluate_regression(y_test.values, y_pred)
        
        else:
            return {"accuracy": accuracy_score(y_test.values, y_pred)}
    
    def get_feature_importance(
        self,
        model,
        feature_names: List[str]
    ) -> Dict[str, float]:
        """Get feature importance from model.
        
        Args:
            model: Trained model
            feature_names: List of feature names
        
        Returns:
            Dictionary with feature importance
        """
        if hasattr(model, "feature_importances_"):
            importance = model.feature_importances_
        elif hasattr(model, "coef_"):
            importance = np.abs(model.coef_[0])
        else:
            logger.warning("Model does not have feature_importances_ or coef_ attribute")
            return {}
        
        return dict(zip(feature_names, importance))
