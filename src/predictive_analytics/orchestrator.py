"""Orchestrator for predictive analytics."""

from typing import Dict, Any, List, Optional
import logging

import pandas as pd

from src.predictive_analytics.base import ModelBase, ModelType, ProblemType
from src.predictive_analytics.splitting import DataSplitter
from src.predictive_analytics.preprocessing import PreprocessingPipeline
from src.predictive_analytics.baseline import BaselineModels
from src.predictive_analytics.comparison import ModelComparator
from src.predictive_analytics.imbalance import ClassImbalanceHandler
from src.predictive_analytics.tuning import HyperparameterTuner
from src.predictive_analytics.persistence import ModelPersistence
from src.predictive_analytics.evaluation import ModelEvaluator
from src.predictive_analytics.churn_model import ChurnPredictionModel
from src.predictive_analytics.default_risk_model import DefaultRiskModel
from src.predictive_analytics.profitability_model import ProfitabilityPredictionModel
from src.predictive_analytics.clv_model import CLVPredictionModel
from src.predictive_analytics.anomaly_model import TransactionAnomalyModel

logger = logging.getLogger(__name__)


class PredictiveAnalyticsOrchestrator(ModelBase):
    """Orchestrates predictive analytics operations."""
    
    def __init__(self, random_state: int = 42):
        """Initialize predictive analytics orchestrator.
        
        Args:
            random_state: Random state for reproducibility
        """
        super().__init__(random_state)
        
        # Initialize components
        self.splitter = DataSplitter(random_state)
        self.preprocessor = PreprocessingPipeline(random_state)
        self.baseline = BaselineModels(random_state)
        self.comparator = ModelComparator(random_state)
        self.imbalance_handler = ClassImbalanceHandler(random_state)
        self.tuner = HyperparameterTuner(random_state)
        self.persistence = ModelPersistence(random_state)
        self.evaluator = ModelEvaluator(random_state)
        
        # Initialize models
        self.churn_model = ChurnPredictionModel(random_state)
        self.default_risk_model = DefaultRiskModel(random_state)
        self.profitability_model = ProfitabilityPredictionModel(random_state)
        self.clv_model = CLVPredictionModel(random_state)
        self.anomaly_model = TransactionAnomalyModel(random_state)
    
    def train_churn_model(
        self,
        df: pd.DataFrame,
        target_column: str = "is_churned",
        feature_columns: Optional[List[str]] = None,
        model_types: List[str] = None,
        handle_imbalance: bool = True
    ) -> Dict[str, Any]:
        """Train and compare churn prediction models.
        
        Args:
            df: DataFrame with customer data
            target_column: Name of target column
            feature_columns: List of feature columns
            model_types: List of model types to train
            handle_imbalance: Whether to handle class imbalance
        
        Returns:
            Dictionary with training results and comparison
        """
        if model_types is None:
            model_types = ["logistic", "random_forest"]
        
        logger.info(f"Training churn prediction models: {model_types}")
        
        # Split data
        train_df, val_df, test_df = self.splitter.split_train_val_test(
            df, target_column, random_state=self.random_state
        )
        
        # Get features and target
        if feature_columns is None:
            feature_columns = [col for col in df.columns if col != target_column]
        
        X_train, y_train = self.splitter.get_features_and_target(train_df, target_column, feature_columns)
        X_val, y_val = self.splitter.get_features_and_target(val_df, target_column, feature_columns)
        X_test, y_test = self.splitter.get_features_and_target(test_df, target_column, feature_columns)
        
        # Train models
        results = []
        for model_type in model_types:
            result = self.churn_model.train(
                X_train, y_train, X_val, y_val,
                model_type=model_type,
                handle_imbalance=handle_imbalance
            )
            results.append(result)
        
        # Compare models
        comparison = self.comparator.compare_models(results, primary_metric="f1")
        
        return {
            "model_results": [r.to_dict() for r in results],
            "comparison": comparison.to_dict("records"),
            "best_model": self.comparator.select_best_model(results, primary_metric="f1").to_dict(),
            "data_split": {
                "train_size": len(train_df),
                "val_size": len(val_df),
                "test_size": len(test_df)
            }
        }
    
    def train_profitability_model(
        self,
        df: pd.DataFrame,
        target_column: str = "net_profit",
        feature_columns: Optional[List[str]] = None,
        model_types: List[str] = None
    ) -> Dict[str, Any]:
        """Train and compare profitability prediction models.
        
        Args:
            df: DataFrame with customer data
            target_column: Name of target column
            feature_columns: List of feature columns
            model_types: List of model types to train
        
        Returns:
            Dictionary with training results and comparison
        """
        if model_types is None:
            model_types = ["linear", "random_forest"]
        
        logger.info(f"Training profitability prediction models: {model_types}")
        
        # Split data
        train_df, val_df, test_df = self.splitter.split_train_val_test(
            df, target_column, random_state=self.random_state
        )
        
        # Get features and target
        if feature_columns is None:
            feature_columns = [col for col in df.columns if col != target_column]
        
        X_train, y_train = self.splitter.get_features_and_target(train_df, target_column, feature_columns)
        X_val, y_val = self.splitter.get_features_and_target(val_df, target_column, feature_columns)
        
        # Train models
        results = []
        for model_type in model_types:
            result = self.profitability_model.train(
                X_train, y_train, X_val, y_val,
                model_type=model_type
            )
            results.append(result)
        
        # Compare models
        comparison = self.comparator.compare_models(results, primary_metric="r2")
        
        return {
            "model_results": [r.to_dict() for r in results],
            "comparison": comparison.to_dict("records"),
            "best_model": self.comparator.select_best_model(results, primary_metric="r2").to_dict()
        }
    
    def train_clv_model(
        self,
        df: pd.DataFrame,
        target_column: str = "clv",
        feature_columns: Optional[List[str]] = None,
        model_types: List[str] = None
    ) -> Dict[str, Any]:
        """Train and compare CLV prediction models.
        
        Args:
            df: DataFrame with customer data
            target_column: Name of target column
            feature_columns: List of feature columns
            model_types: List of model types to train
        
        Returns:
            Dictionary with training results and comparison
        """
        if model_types is None:
            model_types = ["linear", "random_forest"]
        
        logger.info(f"Training CLV prediction models: {model_types}")
        
        # Split data
        train_df, val_df, test_df = self.splitter.split_train_val_test(
            df, target_column, random_state=self.random_state
        )
        
        # Get features and target
        if feature_columns is None:
            feature_columns = [col for col in df.columns if col != target_column]
        
        X_train, y_train = self.splitter.get_features_and_target(train_df, target_column, feature_columns)
        X_val, y_val = self.splitter.get_features_and_target(val_df, target_column, feature_columns)
        
        # Train models
        results = []
        for model_type in model_types:
            result = self.clv_model.train(
                X_train, y_train, X_val, y_val,
                model_type=model_type
            )
            results.append(result)
        
        # Compare models
        comparison = self.comparator.compare_models(results, primary_metric="r2")
        
        return {
            "model_results": [r.to_dict() for r in results],
            "comparison": comparison.to_dict("records"),
            "best_model": self.comparator.select_best_model(results, primary_metric="r2").to_dict()
        }
    
    def train_anomaly_detection_model(
        self,
        df: pd.DataFrame,
        feature_columns: Optional[List[str]] = None,
        model_types: List[str] = None,
        contamination: float = 0.1
    ) -> Dict[str, Any]:
        """Train and compare anomaly detection models.
        
        Args:
            df: DataFrame with transaction data
            feature_columns: List of feature columns
            model_types: List of model types to train
            contamination: Expected proportion of anomalies
        
        Returns:
            Dictionary with training results and comparison
        """
        if model_types is None:
            model_types = ["isolation_forest"]
        
        logger.info(f"Training anomaly detection models: {model_types}")
        
        # Split data (no target for anomaly detection)
        train_df, val_df, test_df = self.splitter.split_train_val_test(
            df, target_column=None, random_state=self.random_state
        )
        
        # Get features
        if feature_columns is None:
            feature_columns = df.columns.tolist()
        
        X_train = train_df[feature_columns]
        X_val = val_df[feature_columns]
        
        # Train models
        results = []
        for model_type in model_types:
            result = self.anomaly_model.train(
                X_train, X_val,
                model_type=model_type,
                contamination=contamination
            )
            results.append(result)
        
        return {
            "model_results": [r.to_dict() for r in results],
            "data_split": {
                "train_size": len(train_df),
                "val_size": len(val_df),
                "test_size": len(test_df)
            }
        }
    
    def train_default_risk_model(
        self,
        df: pd.DataFrame,
        target_column: str = "is_default",
        feature_columns: Optional[List[str]] = None,
        model_types: List[str] = None,
        handle_imbalance: bool = True
    ) -> Dict[str, Any]:
        """Train and compare default risk models.
        
        Args:
            df: DataFrame with customer data
            target_column: Name of target column
            feature_columns: List of feature columns
            model_types: List of model types to train
            handle_imbalance: Whether to handle class imbalance
        
        Returns:
            Dictionary with training results and comparison
        """
        if model_types is None:
            model_types = ["logistic", "random_forest"]
        
        logger.info(f"Training default risk models: {model_types}")
        
        # Split data
        train_df, val_df, test_df = self.splitter.split_train_val_test(
            df, target_column, random_state=self.random_state
        )
        
        # Get features and target
        if feature_columns is None:
            feature_columns = [col for col in df.columns if col != target_column]
        
        X_train, y_train = self.splitter.get_features_and_target(train_df, target_column, feature_columns)
        X_val, y_val = self.splitter.get_features_and_target(val_df, target_column, feature_columns)
        
        # Train models
        results = []
        for model_type in model_types:
            result = self.default_risk_model.train(
                X_train, y_train, X_val, y_val,
                model_type=model_type,
                handle_imbalance=handle_imbalance
            )
            results.append(result)
        
        # Compare models
        comparison = self.comparator.compare_models(results, primary_metric="f1")
        
        return {
            "model_results": [r.to_dict() for r in results],
            "comparison": comparison.to_dict("records"),
            "best_model": self.comparator.select_best_model(results, primary_metric="f1").to_dict()
        }
