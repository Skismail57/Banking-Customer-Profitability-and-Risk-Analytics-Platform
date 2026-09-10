"""ML tests for model prediction pipeline."""

import pytest
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score


@pytest.mark.ml
class TestModelPipeline:
    """Tests for ML model prediction pipeline."""
    
    def test_model_initialization(self):
        """Test model initialization."""
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        assert model is not None
    
    def test_model_training(self, sample_customer_metrics):
        """Test model training."""
        df = sample_customer_metrics
        
        # Prepare features
        features = ["net_profit", "exposure_amount", "credit_utilization", "credit_score"]
        X = df[features].fillna(0)
        y = (df["churn_probability"] > 0.5).astype(int)
        
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X, y)
        
        assert hasattr(model, 'feature_importances_')
    
    def test_model_prediction(self, sample_customer_metrics):
        """Test model prediction."""
        df = sample_customer_metrics
        
        # Prepare features
        features = ["net_profit", "exposure_amount", "credit_utilization", "credit_score"]
        X = df[features].fillna(0)
        y = (df["churn_probability"] > 0.5).astype(int)
        
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X, y)
        
        predictions = model.predict(X)
        
        assert len(predictions) == len(df)
        assert all(pred in [0, 1] for pred in predictions)
    
    def test_model_probability_prediction(self, sample_customer_metrics):
        """Test model probability prediction."""
        df = sample_customer_metrics
        
        # Prepare features
        features = ["net_profit", "exposure_amount", "credit_utilization", "credit_score"]
        X = df[features].fillna(0)
        y = (df["churn_probability"] > 0.5).astype(int)
        
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X, y)
        
        probabilities = model.predict_proba(X)
        
        assert probabilities.shape[0] == len(df)
        assert probabilities.shape[1] == 2  # Binary classification
        assert np.abs(probabilities.sum(axis=1) - 1.0).max() < 0.01  # Probabilities sum to 1
    
    def test_model_accuracy(self, sample_customer_metrics):
        """Test model accuracy calculation."""
        df = sample_customer_metrics
        
        # Prepare features
        features = ["net_profit", "exposure_amount", "credit_utilization", "credit_score"]
        X = df[features].fillna(0)
        y = (df["churn_probability"] > 0.5).astype(int)
        
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X, y)
        
        predictions = model.predict(X)
        accuracy = accuracy_score(y, predictions)
        
        assert accuracy >= 0  # Accuracy should be non-negative
        assert accuracy <= 1  # Accuracy should not exceed 1
    
    def test_model_precision(self, sample_customer_metrics):
        """Test model precision calculation."""
        df = sample_customer_metrics
        
        # Prepare features
        features = ["net_profit", "exposure_amount", "credit_utilization", "credit_score"]
        X = df[features].fillna(0)
        y = (df["churn_probability"] > 0.5).astype(int)
        
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X, y)
        
        predictions = model.predict(X)
        precision = precision_score(y, predictions, zero_division=0)
        
        assert precision >= 0  # Precision should be non-negative
        assert precision <= 1  # Precision should not exceed 1
    
    def test_model_recall(self, sample_customer_metrics):
        """Test model recall calculation."""
        df = sample_customer_metrics
        
        # Prepare features
        features = ["net_profit", "exposure_amount", "credit_utilization", "credit_score"]
        X = df[features].fillna(0)
        y = (df["churn_probability"] > 0.5).astype(int)
        
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X, y)
        
        predictions = model.predict(X)
        recall = recall_score(y, predictions, zero_division=0)
        
        assert recall >= 0  # Recall should be non-negative
        assert recall <= 1  # Recall should not exceed 1
    
    def test_feature_importance_extraction(self, sample_customer_metrics):
        """Test feature importance extraction."""
        df = sample_customer_metrics
        
        # Prepare features
        features = ["net_profit", "exposure_amount", "credit_utilization", "credit_score"]
        X = df[features].fillna(0)
        y = (df["churn_probability"] > 0.5).astype(int)
        
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X, y)
        
        importances = model.feature_importances_
        
        assert len(importances) == len(features)
        assert all(imp >= 0 for imp in importances)
        assert sum(importances) <= 1.01  # Should sum to approximately 1
    
    def test_model_with_null_features(self, sample_null_data):
        """Test model handling of null features."""
        df = sample_null_data
        
        # Prepare features
        features = ["net_profit", "churn_probability"]
        X = df[features].fillna(0)
        y = (df["risk_level"] == "high").astype(int)
        
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X, y)
        
        predictions = model.predict(X)
        
        assert len(predictions) == len(df)
