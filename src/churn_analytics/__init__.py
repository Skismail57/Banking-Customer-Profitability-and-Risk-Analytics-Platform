"""Churn Analytics package."""

from src.churn_analytics.base import (
    ChurnDefinition,
    ChurnBase,
)
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
from src.churn_analytics.orchestrator import ChurnAnalyticsOrchestrator

__all__ = [
    "ChurnDefinition",
    "ChurnBase",
    "ChurnRateCalculator",
    "CohortRetentionAnalyzer",
    "ActivityDeclineDetector",
    "TransactionDeclineDetector",
    "BalanceDeclineDetector",
    "ComplaintSignalDetector",
    "ChurnFeatureEngineer",
    "LogisticChurnModel",
    "RandomForestChurnModel",
    "GradientBoostingChurnModel",
    "ChurnModelEvaluator",
    "ChurnAnalyticsOrchestrator",
]
