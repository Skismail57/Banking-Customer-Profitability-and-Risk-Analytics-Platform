"""Cross-validation and hyperparameter tuning."""

from typing import Dict, Any, List, Optional
import logging

import pandas as pd
import numpy as np
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, cross_val_score
from sklearn.metrics import make_scorer

from src.predictive_analytics.base import ModelBase, ProblemType

logger = logging.getLogger(__name__)


class HyperparameterTuner(ModelBase):
    """Hyperparameter tuning with cross-validation."""
    
    def cross_validate(
        self,
        model,
        X: pd.DataFrame,
        y: pd.Series,
        cv: int = 5,
        scoring: Optional[str] = None
    ) -> Dict[str, Any]:
        """Perform cross-validation.
        
        Args:
            model: Model to evaluate
            X: Features
            y: Target
            cv: Number of folds
            scoring: Scoring metric
        
        Returns:
            Dictionary with CV results
        """
        if scoring is None:
            scoring = "f1" if len(y.unique()) == 2 else "accuracy"
        
        scores = cross_val_score(model, X, y, cv=cv, scoring=scoring)
        
        return {
            "cv_scores": scores.tolist(),
            "mean_score": scores.mean(),
            "std_score": scores.std(),
            "scoring": scoring,
            "cv_folds": cv
        }
    
    def grid_search(
        self,
        model,
        param_grid: Dict[str, List],
        X: pd.DataFrame,
        y: pd.Series,
        cv: int = 5,
        scoring: Optional[str] = None,
        n_jobs: int = -1
    ) -> Dict[str, Any]:
        """Perform grid search hyperparameter tuning.
        
        Args:
            model: Model to tune
            param_grid: Parameter grid
            X: Features
            y: Target
            cv: Number of folds
            scoring: Scoring metric
            n_jobs: Number of parallel jobs
        
        Returns:
            Dictionary with tuning results
        """
        if scoring is None:
            scoring = "f1" if len(y.unique()) == 2 else "accuracy"
        
        grid_search = GridSearchCV(
            model, param_grid, cv=cv, scoring=scoring, n_jobs=n_jobs, verbose=0
        )
        
        grid_search.fit(X, y)
        
        return {
            "best_params": grid_search.best_params_,
            "best_score": grid_search.best_score_,
            "best_model": grid_search.best_estimator_,
            "cv_results": grid_search.cv_results_,
            "scoring": scoring
        }
    
    def randomized_search(
        self,
        model,
        param_distributions: Dict[str, List],
        X: pd.DataFrame,
        y: pd.Series,
        n_iter: int = 10,
        cv: int = 5,
        scoring: Optional[str] = None,
        n_jobs: int = -1,
        random_state: Optional[int] = None
    ) -> Dict[str, Any]:
        """Perform randomized search hyperparameter tuning.
        
        Args:
            model: Model to tune
            param_distributions: Parameter distributions
            X: Features
            y: Target
            n_iter: Number of iterations
            cv: Number of folds
            scoring: Scoring metric
            n_jobs: Number of parallel jobs
            random_state: Random state
        
        Returns:
            Dictionary with tuning results
        """
        if random_state is None:
            random_state = self.random_state
        
        if scoring is None:
            scoring = "f1" if len(y.unique()) == 2 else "accuracy"
        
        random_search = RandomizedSearchCV(
            model, param_distributions, n_iter=n_iter, cv=cv,
            scoring=scoring, n_jobs=n_jobs, random_state=random_state, verbose=0
        )
        
        random_search.fit(X, y)
        
        return {
            "best_params": random_search.best_params_,
            "best_score": random_search.best_score_,
            "best_model": random_search.best_estimator_,
            "scoring": scoring
        }
