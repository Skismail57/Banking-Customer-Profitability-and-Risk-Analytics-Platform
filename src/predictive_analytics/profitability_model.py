"""Customer profitability prediction model."""

from typing import Dict, Any, List, Optional
import logging
import time

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge

from src.predictive_analytics.base import ModelBase, ModelResult, ModelType, ProblemType
from src.predictive_analytics.evaluation import ModelEvaluator

logger = logging.getLogger(__name__)


class ProfitabilityPredictionModel(ModelBase):
    """Customer profitability prediction model (regression)."""
    
    def __init__(self, random_state: int = 42):
        """Initialize profitability prediction model.
        
        Args:
            random_state: Random state for reproducibility
        """
        super().__init__(random_state)
        self.evaluator = ModelEvaluator(random_state)
    
    def train(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: pd.DataFrame,
        y_val: pd.Series,
        model_type: str = "random_forest"
    ) -> ModelResult:
        """Train profitability prediction model.
        
        Args:
            X_train: Training features
            y_train: Training target
            X_val: Validation features
            y_val: Validation target
            model_type: Type of model (linear, ridge, random_forest, gradient_boosting)
        
        Returns:
            ModelResult with training results
        """
        start_time = time.time()
        
        # Select model
        if model_type == "linear":
            model = LinearRegression()
        elif model_type == "ridge":
            model = Ridge(random_state=self.random_state)
        elif model_type == "random_forest":
            model = RandomForestRegressor(
                n_estimators=100,
                random_state=self.random_state,
                max_depth=10
            )
        elif model_type == "gradient_boosting":
            model = GradientBoostingRegressor(
                n_estimators=100,
                random_state=self.random_state,
                max_depth=5,
                learning_rate=0.1
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        # Train model
        model.fit(X_train, y_train)
        self.model = model
        self.feature_names = X_train.columns.tolist()
        self.is_fitted = True
        
        training_time = time.time() - start_time
        
        # Evaluate on validation set
        metrics = self.evaluator.evaluate_model(
            model, X_val, y_val, ProblemType.REGRESSION
        )
        
        # Get feature importance
        feature_importance = self.evaluator.get_feature_importance(model, self.feature_names)
        
        return ModelResult(
            model_name=f"profitability_{model_type}",
            model_type=ModelType.PROFITABILITY_PREDICTION,
            problem_type=ProblemType.REGRESSION,
            metrics=metrics,
            feature_importance=feature_importance,
            training_time=training_time,
            model_metadata={
                "model_type": model_type
            }
        )
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict profitability.
        
        Args:
            X: Features
        
        Returns:
            Predicted profitability values
        """
        if not self.is_fitted:
            raise ValueError("Model must be trained before prediction")
        
        return self.model.predict(X)
