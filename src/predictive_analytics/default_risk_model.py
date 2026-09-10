"""Default-risk classification model."""

from typing import Dict, Any, List, Optional
import logging
import time

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression

from src.predictive_analytics.base import ModelBase, ModelResult, ModelType, ProblemType
from src.predictive_analytics.evaluation import ModelEvaluator
from src.predictive_analytics.imbalance import ClassImbalanceHandler

logger = logging.getLogger(__name__)


class DefaultRiskModel(ModelBase):
    """Default risk classification model."""
    
    def __init__(self, random_state: int = 42):
        """Initialize default risk model.
        
        Args:
            random_state: Random state for reproducibility
        """
        super().__init__(random_state)
        self.evaluator = ModelEvaluator(random_state)
        self.imbalance_handler = ClassImbalanceHandler(random_state)
    
    def train(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: pd.DataFrame,
        y_val: pd.Series,
        model_type: str = "random_forest",
        handle_imbalance: bool = True,
        imbalance_method: str = "smote"
    ) -> ModelResult:
        """Train default risk model.
        
        Args:
            X_train: Training features
            y_train: Training target
            X_val: Validation features
            y_val: Validation target
            model_type: Type of model (logistic, random_forest, gradient_boosting)
            handle_imbalance: Whether to handle class imbalance
            imbalance_method: Method for imbalance handling
        
        Returns:
            ModelResult with training results
        """
        start_time = time.time()
        
        # Handle class imbalance
        if handle_imbalance:
            X_train_resampled, y_train_resampled = self.imbalance_handler.handle_imbalance(
                X_train, y_train, method=imbalance_method
            )
        else:
            X_train_resampled, y_train_resampled = X_train, y_train
        
        # Select model
        if model_type == "logistic":
            model = LogisticRegression(
                random_state=self.random_state,
                max_iter=1000,
                class_weight="balanced"
            )
        elif model_type == "random_forest":
            model = RandomForestClassifier(
                n_estimators=100,
                random_state=self.random_state,
                class_weight="balanced",
                max_depth=10
            )
        elif model_type == "gradient_boosting":
            model = GradientBoostingClassifier(
                n_estimators=100,
                random_state=self.random_state,
                max_depth=5,
                learning_rate=0.1
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        # Train model
        model.fit(X_train_resampled, y_train_resampled)
        self.model = model
        self.feature_names = X_train.columns.tolist()
        self.is_fitted = True
        
        training_time = time.time() - start_time
        
        # Evaluate on validation set
        metrics = self.evaluator.evaluate_model(
            model, X_val, y_val, ProblemType.BINARY_CLASSIFICATION
        )
        
        # Get feature importance
        feature_importance = self.evaluator.get_feature_importance(model, self.feature_names)
        
        return ModelResult(
            model_name=f"default_risk_{model_type}",
            model_type=ModelType.DEFAULT_RISK,
            problem_type=ProblemType.BINARY_CLASSIFICATION,
            metrics=metrics,
            feature_importance=feature_importance,
            training_time=training_time,
            model_metadata={
                "model_type": model_type,
                "handle_imbalance": handle_imbalance,
                "imbalance_method": imbalance_method,
                "imbalance_info": self.imbalance_handler.check_imbalance(y_train)
            }
        )
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict default risk.
        
        Args:
            X: Features
        
        Returns:
            Predictions (0 = no default, 1 = default)
        """
        if not self.is_fitted:
            raise ValueError("Model must be trained before prediction")
        
        return self.model.predict(X)
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Predict default risk probabilities.
        
        Args:
            X: Features
        
        Returns:
            Predicted probabilities
        """
        if not self.is_fitted:
            raise ValueError("Model must be trained before prediction")
        
        return self.model.predict_proba(X)
