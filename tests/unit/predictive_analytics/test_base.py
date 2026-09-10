"""Unit tests for predictive analytics base classes."""

import pytest

from src.predictive_analytics.base import ModelType, ProblemType, ModelResult, ModelBase


class TestModelType:
    """Tests for ModelType enum."""
    
    def test_model_type_enum_values(self):
        """Test ModelType enum has expected values."""
        assert ModelType.CHURN_PREDICTION.value == "churn_prediction"
        assert ModelType.DEFAULT_RISK.value == "default_risk"
        assert ModelType.PROFITABILITY_PREDICTION.value == "profitability_prediction"
        assert ModelType.CLV_PREDICTION.value == "clv_prediction"
        assert ModelType.ANOMALY_DETECTION.value == "anomaly_detection"


class TestProblemType:
    """Tests for ProblemType enum."""
    
    def test_problem_type_enum_values(self):
        """Test ProblemType enum has expected values."""
        assert ProblemType.BINARY_CLASSIFICATION.value == "binary_classification"
        assert ProblemType.MULTICLASS_CLASSIFICATION.value == "multiclass_classification"
        assert ProblemType.REGRESSION.value == "regression"
        assert ProblemType.ANOMALY_DETECTION.value == "anomaly_detection"


class TestModelResult:
    """Tests for ModelResult dataclass."""
    
    def test_model_result_creation(self):
        """Test creating model result."""
        result = ModelResult(
            model_name="test_model",
            model_type=ModelType.CHURN_PREDICTION,
            problem_type=ProblemType.BINARY_CLASSIFICATION,
            metrics={"accuracy": 0.85}
        )
        
        assert result.model_name == "test_model"
        assert result.metrics["accuracy"] == 0.85
    
    def test_to_dict(self):
        """Test serialization to dictionary."""
        result = ModelResult(
            model_name="test_model",
            model_type=ModelType.CHURN_PREDICTION,
            problem_type=ProblemType.BINARY_CLASSIFICATION,
            metrics={"accuracy": 0.85}
        )
        
        data_dict = result.to_dict()
        
        assert data_dict["model_name"] == "test_model"
        assert data_dict["model_type"] == "churn_prediction"


class TestModelBase:
    """Tests for ModelBase class."""
    
    def test_initialization(self):
        """Test base class initialization."""
        base = ModelBase()
        
        assert base.random_state == 42
    
    def test_custom_random_state(self):
        """Test custom random state."""
        base = ModelBase(random_state=123)
        
        assert base.random_state == 123
    
    def test_get_appropriate_metrics_binary_classification(self):
        """Test metrics for binary classification."""
        base = ModelBase()
        metrics = base.get_appropriate_metrics(ProblemType.BINARY_CLASSIFICATION)
        
        assert "accuracy" in metrics
        assert "precision" in metrics
        assert "recall" in metrics
        assert "f1" in metrics
        assert "roc_auc" in metrics
    
    def test_get_appropriate_metrics_regression(self):
        """Test metrics for regression."""
        base = ModelBase()
        metrics = base.get_appropriate_metrics(ProblemType.REGRESSION)
        
        assert "mse" in metrics
        assert "rmse" in metrics
        assert "mae" in metrics
        assert "r2" in metrics
