"""Orchestrator for churn analytics."""

from datetime import date
from typing import Dict, Any, List, Optional
import logging

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

from src.churn_analytics.base import ChurnBase
from src.churn_analytics.rates import ChurnRateCalculator
from src.churn_analytics.cohort import CohortRetentionAnalyzer
from src.churn_analytics.signals import (
    ActivityDeclineDetector,
    TransactionDeclineDetector,
    BalanceDeclineDetector,
    ComplaintSignalDetector,
)
from src.churn_analytics.features import ChurnFeatureEngineer
from src.churn_analytics.models import (
    LogisticChurnModel,
    RandomForestChurnModel,
    GradientBoostingChurnModel,
)
from src.churn_analytics.evaluation import ChurnModelEvaluator

logger = logging.getLogger(__name__)


class ChurnAnalyticsOrchestrator(ChurnBase):
    """Orchestrates churn analytics operations."""
    
    def __init__(self, as_of_date: Optional[date] = None):
        """Initialize churn analytics orchestrator.
        
        Args:
            as_of_date: As-of date for temporal analysis
        """
        super().__init__(as_of_date)
        
        # Initialize components
        self.rate_calculator = ChurnRateCalculator(as_of_date)
        self.cohort_analyzer = CohortRetentionAnalyzer(as_of_date)
        self.activity_detector = ActivityDeclineDetector(as_of_date)
        self.transaction_detector = TransactionDeclineDetector(as_of_date)
        self.balance_detector = BalanceDeclineDetector(as_of_date)
        self.complaint_detector = ComplaintSignalDetector(as_of_date)
        self.feature_engineer = ChurnFeatureEngineer(as_of_date)
        self.evaluator = ChurnModelEvaluator(as_of_date)
    
    def generate_churn_report(
        self,
        df: pd.DataFrame,
        customer_column: str = "customer_key",
        churn_column: str = "is_churned"
    ) -> Dict[str, Any]:
        """Generate comprehensive churn analytics report.
        
        Args:
            df: DataFrame with customer data
            customer_column: Name of customer column
            churn_column: Name of churn indicator column
        
        Returns:
            Dictionary with churn analytics results
        """
        logger.info("Generating churn analytics report")
        
        report = {
            "metadata": {
                "as_of_date": self.as_of_date.isoformat(),
                "churn_definition": self.get_churn_definition("composite_churn").to_dict()
            },
            "rates": {},
            "signals": {}
        }
        
        # Calculate churn and retention rates
        report["rates"]["churn_rate"] = self.rate_calculator.calculate_churn_rate(
            df, customer_column, churn_column
        )
        report["rates"]["retention_rate"] = self.rate_calculator.calculate_retention_rate(
            df, customer_column, churn_column
        )
        
        return report
    
    def train_churn_models(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        models: List[str] = None
    ) -> Dict[str, Any]:
        """Train and compare churn models.
        
        Args:
            X: Feature DataFrame
            y: Target Series
            models: List of models to train (logistic, random_forest, gradient_boosting)
        
        Returns:
            Dictionary with training results and comparison
        """
        if models is None:
            models = ["logistic", "random_forest"]
        
        logger.info(f"Training churn models: {models}")
        
        trained_models = {}
        results = {}
        
        if "logistic" in models:
            logistic_model = LogisticChurnModel(self.as_of_date)
            results["logistic"] = logistic_model.train(X, y)
            trained_models["logistic"] = logistic_model
        
        if "random_forest" in models:
            rf_model = RandomForestChurnModel(self.as_of_date)
            results["random_forest"] = rf_model.train(X, y)
            trained_models["random_forest"] = rf_model
        
        if "gradient_boosting" in models:
            gb_model = GradientBoostingChurnModel(self.as_of_date)
            results["gradient_boosting"] = gb_model.train(X, y)
            trained_models["gradient_boosting"] = gb_model
        
        # Evaluate models
        model_predictions = {}
        for model_name, model in trained_models.items():
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            model_predictions[model_name] = {
                "y_pred": model.predict(X_test),
                "y_proba": model.predict_proba(X_test)
            }
        
        comparison = self.evaluator.evaluate_model_comparison(y_test, model_predictions)
        
        # Feature importance comparison
        feature_importance = self.evaluator.get_feature_importance_comparison(trained_models)
        
        return {
            "training_results": results,
            "model_comparison": comparison.to_dict("records"),
            "feature_importance": feature_importance.to_dict("records"),
            "trained_models": trained_models
        }
    
    def detect_churn_signals(
        self,
        df: pd.DataFrame,
        customer_column: str = "customer_key"
    ) -> Dict[str, Any]:
        """Detect all churn signals for customers.
        
        Args:
            df: DataFrame with customer data
            customer_column: Name of customer column
        
        Returns:
            Dictionary with all churn signals
        """
        logger.info("Detecting churn signals")
        
        signals = {}
        
        # Activity decline (placeholder - requires activity data)
        # signals["activity_decline"] = self.activity_detector.detect_activity_decline(...)
        
        # Transaction decline (placeholder - requires transaction data)
        # signals["transaction_decline"] = self.transaction_detector.detect_transaction_decline(...)
        
        # Balance decline (placeholder - requires balance data)
        # signals["balance_decline"] = self.balance_detector.detect_balance_decline(...)
        
        # Complaint signals (placeholder - requires complaint data)
        # signals["complaint_signals"] = self.complaint_detector.detect_complaint_signals(...)
        
        return signals
