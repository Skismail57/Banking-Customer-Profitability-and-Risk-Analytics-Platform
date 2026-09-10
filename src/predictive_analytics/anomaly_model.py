"""Transaction anomaly detection model."""

from typing import Dict, Any, List, Optional
import logging
import time

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM

from src.predictive_analytics.base import ModelBase, ModelResult, ModelType, ProblemType
from src.predictive_analytics.evaluation import ModelEvaluator

logger = logging.getLogger(__name__)


class TransactionAnomalyModel(ModelBase):
    """Transaction anomaly detection model."""
    
    def __init__(self, random_state: int = 42):
        """Initialize anomaly detection model.
        
        Args:
            random_state: Random state for reproducibility
        """
        super().__init__(random_state)
        self.evaluator = ModelEvaluator(random_state)
    
    def train(
        self,
        X_train: pd.DataFrame,
        X_val: pd.DataFrame,
        y_val: Optional[pd.Series] = None,
        model_type: str = "isolation_forest",
        contamination: float = 0.1
    ) -> ModelResult:
        """Train anomaly detection model.
        
        Args:
            X_train: Training features (normal transactions)
            X_val: Validation features
            y_val: Validation labels (optional, for evaluation)
            model_type: Type of model (isolation_forest, one_class_svm)
            contamination: Expected proportion of anomalies
        
        Returns:
            ModelResult with training results
        """
        start_time = time.time()
        
        # Select model
        if model_type == "isolation_forest":
            model = IsolationForest(
                contamination=contamination,
                random_state=self.random_state,
                n_estimators=100
            )
        elif model_type == "one_class_svm":
            model = OneClassSVM(
                nu=contamination,
                kernel="rbf",
                gamma="scale"
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        # Train model
        model.fit(X_train)
        self.model = model
        self.feature_names = X_train.columns.tolist()
        self.is_fitted = True
        
        training_time = time.time() - start_time
        
        # Evaluate on validation set if labels available
        metrics = {}
        if y_val is not None:
            # Predict anomalies (-1 = anomaly, 1 = normal)
            y_pred = model.predict(X_val)
            # Convert to binary (1 = anomaly, 0 = normal)
            y_pred_binary = (y_pred == -1).astype(int)
            
            metrics = self.evaluator.evaluate_classification(
                y_val.values, y_pred_binary
            )
        else:
            # No labels, return basic metrics
            metrics = {
                "contamination": contamination,
                "note": "No labels provided for evaluation"
            }
        
        return ModelResult(
            model_name=f"anomaly_{model_type}",
            model_type=ModelType.ANOMALY_DETECTION,
            problem_type=ProblemType.ANOMALY_DETECTION,
            metrics=metrics,
            training_time=training_time,
            model_metadata={
                "model_type": model_type,
                "contamination": contamination
            }
        )
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict anomalies.
        
        Args:
            X: Features
        
        Returns:
            Predictions (1 = anomaly, 0 = normal)
        """
        if not self.is_fitted:
            raise ValueError("Model must be trained before prediction")
        
        y_pred = self.model.predict(X)
        # Convert to binary (1 = anomaly, 0 = normal)
        return (y_pred == -1).astype(int)
    
    def predict_anomaly_score(self, X: pd.DataFrame) -> np.ndarray:
        """Predict anomaly scores.
        
        Args:
            X: Features
        
        Returns:
            Anomaly scores
        """
        if not self.is_fitted:
            raise ValueError("Model must be trained before prediction")
        
        if hasattr(self.model, "score_samples"):
            return -self.model.score_samples(X)  # Higher = more anomalous
        else:
            return self.model.decision_function(X)
