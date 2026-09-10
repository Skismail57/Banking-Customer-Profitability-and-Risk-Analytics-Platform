"""Integrated ML Layer.

This module connects the ML layer (Churn/CLV, Risk Models) to Statistical Analytics
outputs, providing machine learning predictions for decision-making.

Architecture Position:
Statistical Analytics → ML (Churn/CLV, Risk Models) → Decision Engine
"""

from typing import Dict, Any, Optional, List
from datetime import date
import logging
import pickle
from pathlib import Path

import pandas as pd
import numpy as np

from src.data_platform.data_loader import DataLoader
from src.churn_analytics.models import LogisticChurnModel, RandomForestChurnModel, GradientBoostingChurnModel
from src.predictive_analytics.base import ModelBase, ModelType, ProblemType, ModelResult

logger = logging.getLogger(__name__)


class IntegratedMLLayer:
    """Integrated ML Layer for Churn, CLV, and Risk predictions.
    
    This class orchestrates ML models and provides predictions that feed
    into the Decision Engine.
    """
    
    def __init__(
        self,
        as_of_date: Optional[date] = None,
        data_loader: Optional[DataLoader] = None,
        model_dir: Optional[str] = None
    ):
        """Initialize Integrated ML Layer.
        
        Args:
            as_of_date: As-of date for predictions
            data_loader: Data loader instance
            model_dir: Directory for model persistence
        """
        self.as_of_date = as_of_date or date.today()
        self.data_loader = data_loader or DataLoader()
        self.model_dir = Path(model_dir) if model_dir else Path("models")
        self.model_dir.mkdir(exist_ok=True)
        
        # Initialize models
        self.churn_models = {
            'logistic': LogisticChurnModel(as_of_date=self.as_of_date),
            'random_forest': RandomForestChurnModel(as_of_date=self.as_of_date),
            'gradient_boosting': GradientBoostingChurnModel(as_of_date=self.as_of_date)
        }
        
        self.is_fitted = False
    
    def train_churn_models(
        self,
        features_df: pd.DataFrame,
        target_column: str = 'churn_label',
        test_size: float = 0.2
    ) -> Dict[str, ModelResult]:
        """Train all churn models.
        
        Args:
            features_df: DataFrame with features and target
            target_column: Name of target column
            test_size: Test set size
        
        Returns:
            Dictionary of model results by model name
        """
        logger.info("Training churn models")
        
        results = {}
        
        # Prepare features and target
        X = features_df.drop(columns=[target_column])
        y = features_df[target_column]
        
        for model_name, model in self.churn_models.items():
            try:
                logger.info(f"Training {model_name} churn model")
                train_result = model.train(X, y, test_size=test_size)
                
                results[model_name] = ModelResult(
                    model_name=model_name,
                    model_type=ModelType.CHURN_PREDICTION,
                    problem_type=ProblemType.BINARY_CLASSIFICATION,
                    metrics=train_result,
                    feature_importance=model.get_feature_importance().to_dict('records') if hasattr(model, 'get_feature_importance') else None
                )
                
                # Persist model
                self._persist_model(model, f"churn_{model_name}")
                
                logger.info(f"{model_name} churn model trained successfully")
                
            except Exception as e:
                logger.error(f"Error training {model_name} churn model: {e}")
                results[model_name] = ModelResult(
                    model_name=model_name,
                    model_type=ModelType.CHURN_PREDICTION,
                    problem_type=ProblemType.BINARY_CLASSIFICATION,
                    metrics={'error': str(e)}
                )
        
        self.is_fitted = True
        logger.info(f"Trained {len(results)} churn models")
        return results
    
    def predict_churn(
        self,
        features_df: pd.DataFrame,
        model_name: str = 'gradient_boosting'
    ) -> pd.DataFrame:
        """Predict churn for customers.
        
        Args:
            features_df: DataFrame with features
            model_name: Name of model to use
        
        Returns:
            DataFrame with predictions
        """
        logger.info(f"Predicting churn using {model_name} model")
        
        # Load model if not fitted
        if not self.is_fitted or not self.churn_models[model_name].is_fitted:
            self._load_model(self.churn_models[model_name], f"churn_{model_name}")
        
        # Make predictions
        predictions = self.churn_models[model_name].predict(features_df)
        probabilities = self.churn_models[model_name].predict_proba(features_df)
        
        # Create results DataFrame
        results_df = features_df.copy()
        results_df['churn_prediction'] = predictions
        results_df['churn_probability'] = probabilities[:, 1]  # Probability of churn (class 1)
        
        logger.info(f"Generated churn predictions for {len(results_df)} customers")
        return results_df
    
    def predict_clv(
        self,
        features_df: pd.DataFrame
    ) -> pd.DataFrame:
        """Predict Customer Lifetime Value.
        
        Args:
            features_df: DataFrame with features
        
        Returns:
            DataFrame with CLV predictions
        """
        logger.info("Predicting CLV")
        
        # Placeholder: would use actual CLV model
        # For now, use simple heuristic based on profitability
        results_df = features_df.copy()
        
        if 'net_profit' in features_df.columns:
            # Simple CLV: annual profit * 5 years
            results_df['clv_prediction'] = features_df['net_profit'] * 12 * 5
        else:
            results_df['clv_prediction'] = 0
        
        logger.info(f"Generated CLV predictions for {len(results_df)} customers")
        return results_df
    
    def predict_risk(
        self,
        features_df: pd.DataFrame
    ) -> pd.DataFrame:
        """Predict risk for customers.
        
        Args:
            features_df: DataFrame with features
        
        Returns:
            DataFrame with risk predictions
        """
        logger.info("Predicting risk")
        
        # Placeholder: would use actual risk model
        # For now, use heuristic based on existing risk metrics
        results_df = features_df.copy()
        
        if 'credit_utilization' in features_df.columns and 'days_past_due' in features_df.columns:
            # Simple risk score calculation
            results_df['risk_score'] = (
                features_df['credit_utilization'].fillna(0) * 0.5 +
                (features_df['days_past_due'].fillna(0) / 365) * 0.5
            )
            
            # Determine risk level
            results_df['predicted_risk_level'] = pd.cut(
                results_df['risk_score'],
                bins=[0, 0.3, 0.6, 0.85, 1.0],
                labels=['low', 'medium', 'high', 'critical'],
                include_lowest=True
            ).astype(str)
        else:
            results_df['risk_score'] = 0.5
            results_df['predicted_risk_level'] = 'medium'
        
        logger.info(f"Generated risk predictions for {len(results_df)} customers")
        return results_df
    
    def generate_ml_features(
        self,
        customer_keys: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Generate ML features from customer data.
        
        Args:
            customer_keys: Optional list of customer keys
        
        Returns:
            DataFrame with ML features
        """
        logger.info("Generating ML features")
        
        # Load customer metrics (Core Analytics output)
        metrics_df = self.data_loader.load_customer_metrics(
            as_of_date=self.as_of_date,
            customer_keys=customer_keys
        )
        
        if metrics_df.empty:
            logger.warning("No customer metrics found for feature generation")
            return pd.DataFrame()
        
        # Select and engineer features
        features_df = metrics_df[[
            'customer_key',
            'net_profit',
            'profit_margin',
            'risk_level',
            'credit_utilization',
            'days_past_due',
            'credit_score',
            'balance_to_income_ratio',
            'segment'
        ]].copy()
        
        # Encode categorical variables
        if 'risk_level' in features_df.columns:
            risk_mapping = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
            features_df['risk_level_numeric'] = features_df['risk_level'].map(risk_mapping)
        
        if 'segment' in features_df.columns:
            # One-hot encode segment
            segment_dummies = pd.get_dummies(features_df['segment'], prefix='segment')
            features_df = pd.concat([features_df, segment_dummies], axis=1)
        
        # Fill missing values
        numeric_columns = features_df.select_dtypes(include=[np.number]).columns
        features_df[numeric_columns] = features_df[numeric_columns].fillna(0)
        
        logger.info(f"Generated ML features for {len(features_df)} customers")
        return features_df
    
    def get_model_performance_summary(self) -> Dict[str, Any]:
        """Get summary of model performance.
        
        Returns:
            Dictionary with model performance summary
        """
        logger.info("Getting model performance summary")
        
        # This would load performance metrics from fact_model_performance
        # For now, return placeholder
        return {
            'churn_models': {
                'logistic': {'accuracy': 0.85, 'auc_roc': 0.82},
                'random_forest': {'accuracy': 0.88, 'auc_roc': 0.86},
                'gradient_boosting': {'accuracy': 0.90, 'auc_roc': 0.89}
            },
            'clv_model': {'rmse': 1500, 'r2': 0.75},
            'risk_model': {'accuracy': 0.82, 'auc_roc': 0.80}
        }
    
    def _persist_model(self, model: ModelBase, model_name: str) -> None:
        """Persist model to disk.
        
        Args:
            model: Model to persist
            model_name: Name for the model file
        """
        model_path = self.model_dir / f"{model_name}.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        logger.info(f"Model persisted to {model_path}")
    
    def _load_model(self, model: ModelBase, model_name: str) -> None:
        """Load model from disk.
        
        Args:
            model: Model object to load into
            model_name: Name of the model file
        """
        model_path = self.model_dir / f"{model_name}.pkl"
        if model_path.exists():
            with open(model_path, 'rb') as f:
                loaded_model = pickle.load(f)
                # Copy loaded model attributes to the model object
                model.model = loaded_model.model
                model.feature_names = loaded_model.feature_names
                model.is_fitted = loaded_model.is_fitted
            logger.info(f"Model loaded from {model_path}")
        else:
            logger.warning(f"Model file not found: {model_path}")
