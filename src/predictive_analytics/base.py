"""Base classes for predictive analytics."""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Types of predictive models."""
    CHURN_PREDICTION = "churn_prediction"
    DEFAULT_RISK = "default_risk"
    PROFITABILITY_PREDICTION = "profitability_prediction"
    CLV_PREDICTION = "clv_prediction"
    ANOMALY_DETECTION = "anomaly_detection"


class ProblemType(Enum):
    """Types of machine learning problems."""
    BINARY_CLASSIFICATION = "binary_classification"
    MULTICLASS_CLASSIFICATION = "multiclass_classification"
    REGRESSION = "regression"
    ANOMALY_DETECTION = "anomaly_detection"


@dataclass
class ModelResult:
    """Result of model training/prediction."""
    
    model_name: str
    model_type: ModelType
    problem_type: ProblemType
    metrics: Dict[str, float]
    feature_importance: Optional[Dict[str, float]] = None
    predictions: Optional[Any] = None
    training_time: Optional[float] = None
    model_metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "model_name": self.model_name,
            "model_type": self.model_type.value,
            "problem_type": self.problem_type.value,
            "metrics": self.metrics,
            "feature_importance": self.feature_importance,
            "training_time": self.training_time,
            "model_metadata": self.model_metadata or {}
        }


class ModelBase:
    """Base class for predictive models."""
    
    def __init__(self, random_state: int = 42):
        """Initialize model base.
        
        Args:
            random_state: Random state for reproducibility
        """
        self.random_state = random_state
        self.model = None
        self.feature_names = None
        self.is_fitted = False
    
    def get_appropriate_metrics(self, problem_type: ProblemType) -> List[str]:
        """Get appropriate metrics for problem type.
        
        Args:
            problem_type: Type of ML problem
        
        Returns:
            List of metric names
        """
        if problem_type == ProblemType.BINARY_CLASSIFICATION:
            return ["accuracy", "precision", "recall", "f1", "roc_auc", "pr_auc"]
        elif problem_type == ProblemType.MULTICLASS_CLASSIFICATION:
            return ["accuracy", "precision_macro", "recall_macro", "f1_macro"]
        elif problem_type == ProblemType.REGRESSION:
            return ["mse", "rmse", "mae", "r2"]
        elif problem_type == ProblemType.ANOMALY_DETECTION:
            return ["precision", "recall", "f1", "auc_roc"]
        else:
            return ["accuracy"]
