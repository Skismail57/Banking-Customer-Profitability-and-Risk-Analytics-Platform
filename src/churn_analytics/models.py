"""Churn prediction models (Logistic Regression, Random Forest, Gradient Boosting)."""

from datetime import date
from typing import Dict, Any, Optional, Tuple
import logging

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split

from src.churn_analytics.base import ChurnBase

logger = logging.getLogger(__name__)


class LogisticChurnModel(ChurnBase):
    """Logistic Regression churn model with interpretability focus."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize logistic churn model.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
        self.model = LogisticRegression(
            random_state=42,
            max_iter=1000,
            class_weight="balanced"
        )
        self.feature_names = None
    
    def train(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        test_size: float = 0.2
    ) -> Dict[str, Any]:
        """Train logistic regression model.
        
        Args:
            X: Feature DataFrame
            y: Target Series (churn label)
            test_size: Test set size
        
        Returns:
            Dictionary with training results
        """
        self.feature_names = X.columns.tolist()
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        self.model.fit(X_train, y_train)
        
        return {
            "train_score": self.model.score(X_train, y_train),
            "test_score": self.model.score(X_test, y_test),
            "feature_names": self.feature_names
        }
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict churn.
        
        Args:
            X: Feature DataFrame
        
        Returns:
            Predictions (0 = retained, 1 = churned)
        """
        return self.model.predict(X)
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Predict churn probabilities.
        
        Args:
            X: Feature DataFrame
        
        Returns:
            Predicted probabilities
        """
        return self.model.predict_proba(X)
    
    def get_feature_importance(self) -> pd.DataFrame:
        """Get feature importance (coefficients).
        
        Returns:
            DataFrame with feature coefficients
        """
        if self.feature_names is None:
            return pd.DataFrame()
        
        importance = pd.DataFrame({
            "feature": self.feature_names,
            "coefficient": self.model.coef_[0],
            "abs_coefficient": np.abs(self.model.coef_[0])
        }).sort_values("abs_coefficient", ascending=False)
        
        return importance


class RandomForestChurnModel(ChurnBase):
    """Random Forest churn model."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize random forest churn model.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
        self.model = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            class_weight="balanced",
            max_depth=10
        )
        self.feature_names = None
    
    def train(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        test_size: float = 0.2
    ) -> Dict[str, Any]:
        """Train random forest model.
        
        Args:
            X: Feature DataFrame
            y: Target Series (churn label)
            test_size: Test set size
        
        Returns:
            Dictionary with training results
        """
        self.feature_names = X.columns.tolist()
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        self.model.fit(X_train, y_train)
        
        return {
            "train_score": self.model.score(X_train, y_train),
            "test_score": self.model.score(X_test, y_test),
            "feature_names": self.feature_names
        }
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict churn.
        
        Args:
            X: Feature DataFrame
        
        Returns:
            Predictions (0 = retained, 1 = churned)
        """
        return self.model.predict(X)
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Predict churn probabilities.
        
        Args:
            X: Feature DataFrame
        
        Returns:
            Predicted probabilities
        """
        return self.model.predict_proba(X)
    
    def get_feature_importance(self) -> pd.DataFrame:
        """Get feature importance.
        
        Returns:
            DataFrame with feature importance
        """
        if self.feature_names is None:
            return pd.DataFrame()
        
        importance = pd.DataFrame({
            "feature": self.feature_names,
            "importance": self.model.feature_importances_
        }).sort_values("importance", ascending=False)
        
        return importance


class GradientBoostingChurnModel(ChurnBase):
    """Gradient Boosting churn model."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize gradient boosting churn model.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
        self.model = GradientBoostingClassifier(
            n_estimators=100,
            random_state=42,
            max_depth=5,
            learning_rate=0.1
        )
        self.feature_names = None
    
    def train(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        test_size: float = 0.2
    ) -> Dict[str, Any]:
        """Train gradient boosting model.
        
        Args:
            X: Feature DataFrame
            y: Target Series (churn label)
            test_size: Test set size
        
        Returns:
            Dictionary with training results
        """
        self.feature_names = X.columns.tolist()
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        self.model.fit(X_train, y_train)
        
        return {
            "train_score": self.model.score(X_train, y_train),
            "test_score": self.model.score(X_test, y_test),
            "feature_names": self.feature_names
        }
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict churn.
        
        Args:
            X: Feature DataFrame
        
        Returns:
            Predictions (0 = retained, 1 = churned)
        """
        return self.model.predict(X)
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Predict churn probabilities.
        
        Args:
            X: Feature DataFrame
        
        Returns:
            Predicted probabilities
        """
        return self.model.predict_proba(X)
    
    def get_feature_importance(self) -> pd.DataFrame:
        """Get feature importance.
        
        Returns:
            DataFrame with feature importance
        """
        if self.feature_names is None:
            return pd.DataFrame()
        
        importance = pd.DataFrame({
            "feature": self.feature_names,
            "importance": self.model.feature_importances_
        }).sort_values("importance", ascending=False)
        
        return importance
