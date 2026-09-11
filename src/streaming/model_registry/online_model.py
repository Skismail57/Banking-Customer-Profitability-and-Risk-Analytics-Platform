"""Online model inference for real-time scoring.

This module provides real-time model inference capabilities for the banking analytics
platform, loading and using models for real-time scoring.

Assumptions:
- Models are loaded from file system (existing ModelPersistence)
- Model metadata is retrieved from ModelRegistry
- Features are retrieved from Redis feature store

Limitations:
- Model loading may be slow for large models
- No support for model batching for efficiency
- No support for model versioning at inference time (uses production model)

Fairness Considerations:
- Model predictions should include confidence intervals
- Monitor prediction distribution across demographic segments
- Provide explanation for predictions when possible
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional, Union
import logging
import pickle
import numpy as np

from src.streaming.config import StreamingConfig
from src.streaming.features.feature_store import FeatureStore
from src.streaming.model_registry.registry import ModelRegistry

logger = logging.getLogger(__name__)


class OnlineModel:
    """Online model inference for real-time scoring.
    
    This class loads and uses ML models for real-time inference in the
    streaming pipeline. It integrates with ModelRegistry for model
    versioning and FeatureStore for feature retrieval.
    
    Key Features:
    - Loads models from file system
    - Retrieves model metadata from registry
    - Performs real-time inference on features
    - Supports multiple model types (sklearn, xgboost, etc.)
    - Caches loaded models for performance
    """
    
    def __init__(
        self,
        config: StreamingConfig,
        feature_store: FeatureStore,
        model_registry: ModelRegistry
    ):
        """Initialize online model.
        
        Args:
            config: Streaming configuration
            feature_store: Redis feature store for feature retrieval
            model_registry: Model registry for model metadata
        """
        self.config = config
        self.feature_store = feature_store
        self.model_registry = model_registry
        
        # Model cache
        self._model_cache = {}
    
    def predict(
        self,
        model_name: str,
        features: Dict[str, Any],
        model_version: Optional[str] = None
    ) -> Dict[str, Any]:
        """Perform real-time prediction.
        
        Args:
            model_name: Model name (e.g., "churn_predictor")
            features: Feature dictionary
            model_version: Model version (None = production)
        
        Returns:
            Dictionary with prediction results
        """
        logger.debug(f"Predicting with model {model_name}")
        
        # Get model metadata
        if model_version is None:
            metadata = self.model_registry.get_production_model(model_name)
        else:
            metadata = self.model_registry.get_model(model_name, model_version)
        
        if not metadata:
            logger.error(f"Model {model_name} version {model_version} not found")
            return {
                'success': False,
                'error': 'Model not found',
                'prediction': None
            }
        
        # Load model (cached)
        model = self._load_model(metadata)
        if model is None:
            logger.error(f"Failed to load model {model_name} version {model_version}")
            return {
                'success': False,
                'error': 'Model load failed',
                'prediction': None
            }
        
        # Prepare features
        feature_vector = self._prepare_features(features, metadata)
        if feature_vector is None:
            logger.error(f"Failed to prepare features for model {model_name}")
            return {
                'success': False,
                'error': 'Feature preparation failed',
                'prediction': None
            }
        
        # Perform prediction
        try:
            prediction = model.predict([feature_vector])[0]
            
            # Get probability if available
            probability = None
            if hasattr(model, 'predict_proba'):
                probabilities = model.predict_proba([feature_vector])[0]
                probability = float(max(probabilities))
            
            return {
                'success': True,
                'prediction': float(prediction),
                'probability': probability,
                'model_name': model_name,
                'model_version': metadata.model_version,
                'model_type': metadata.model_type,
                'feature_version': metadata.feature_version,
                'predicted_at': datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
            }
        
        except Exception as e:
            logger.error(f"Prediction failed for model {model_name}: {e}")
            return {
                'success': False,
                'error': str(e),
                'prediction': None
            }
    
    def predict_churn(
        self,
        customer_key: str,
        model_version: Optional[str] = None
    ) -> Dict[str, Any]:
        """Predict churn probability for a customer.
        
        Args:
            customer_key: Customer identifier
            model_version: Model version (None = production)
        
        Returns:
            Dictionary with prediction results
        """
        logger.debug(f"Predicting churn for customer {customer_key}")
        
        # Retrieve customer features from Redis
        features = self._get_customer_features(customer_key)
        if not features:
            return {
                'success': False,
                'error': 'Features not found',
                'prediction': None
            }
        
        # Predict using churn model
        return self.predict(
            model_name='churn_predictor',
            features=features,
            model_version=model_version
        )
    
    def predict_risk(
        self,
        customer_key: str,
        model_version: Optional[str] = None
    ) -> Dict[str, Any]:
        """Predict risk score for a customer.
        
        Args:
            customer_key: Customer identifier
            model_version: Model version (None = production)
        
        Returns:
            Dictionary with prediction results
        """
        logger.debug(f"Predicting risk for customer {customer_key}")
        
        # Retrieve customer features from Redis
        features = self._get_customer_features(customer_key)
        if not features:
            return {
                'success': False,
                'error': 'Features not found',
                'prediction': None
            }
        
        # Predict using risk model
        return self.predict(
            model_name='risk_predictor',
            features=features,
            model_version=model_version
        )
    
    def predict_clv(
        self,
        customer_key: str,
        model_version: Optional[str] = None
    ) -> Dict[str, Any]:
        """Predict customer lifetime value.
        
        Args:
            customer_key: Customer identifier
            model_version: Model version (None = production)
        
        Returns:
            Dictionary with prediction results
        """
        logger.debug(f"Predicting CLV for customer {customer_key}")
        
        # Retrieve customer features from Redis
        features = self._get_customer_features(customer_key)
        if not features:
            return {
                'success': False,
                'error': 'Features not found',
                'prediction': None
            }
        
        # Predict using CLV model
        return self.predict(
            model_name='clv_predictor',
            features=features,
            model_version=model_version
        )
    
    def _load_model(self, metadata):
        """Load model from file system.
        
        Args:
            metadata: Model metadata
        
        Returns:
            Loaded model or None if failed
        """
        # Check cache
        cache_key = f"{metadata.model_name}:{metadata.model_version}"
        if cache_key in self._model_cache:
            return self._model_cache[cache_key]
        
        # Load from file
        artifact_location = metadata.artifact_location
        if not artifact_location:
            logger.error(f"No artifact location for model {metadata.model_name}")
            return None
        
        try:
            with open(artifact_location, 'rb') as f:
                model = pickle.load(f)
            
            # Cache the model
            self._model_cache[cache_key] = model
            
            logger.info(f"Loaded model {metadata.model_name} version {metadata.model_version}")
            return model
        
        except Exception as e:
            logger.error(f"Failed to load model from {artifact_location}: {e}")
            return None
    
    def _prepare_features(
        self,
        features: Dict[str, Any],
        metadata
    ) -> Optional[np.ndarray]:
        """Prepare features for model input.
        
        Args:
            features: Feature dictionary
            metadata: Model metadata
        
        Returns:
        Feature vector or None if failed
        """
        # Get feature names from model metadata if available
        feature_names = metadata.hyperparameters.get('feature_names') if metadata.hyperparameters else None
        
        if feature_names:
            # Extract features in order
            try:
                feature_vector = [features.get(name, 0.0) for name in feature_names]
                return np.array(feature_vector)
            except Exception as e:
                logger.error(f"Failed to extract features: {e}")
                return None
        else:
            # Use all features (sorted by key for consistency)
            try:
                feature_vector = [features[k] for k in sorted(features.keys())]
                return np.array(feature_vector)
            except Exception as e:
                logger.error(f"Failed to extract features: {e}")
                return None
    
    def _get_customer_features(self, customer_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve customer features from Redis.
        
        Args:
            customer_key: Customer identifier
        
        Returns:
            Feature dictionary or None if not found
        """
        try:
            feature_key = f"customer:{customer_key}:features"
            features_data = self.feature_store.redis_client.get(feature_key)
            
            if features_data:
                import json
                return json.loads(features_data)
            
            logger.warning(f"No features found for customer {customer_key}")
            return None
        
        except Exception as e:
            logger.error(f"Error retrieving features for customer {customer_key}: {e}")
            return None
    
    def clear_cache(self):
        """Clear model cache."""
        logger.info("Clearing model cache")
        self._model_cache.clear()
    
    def get_cached_models(self) -> list:
        """Get list of cached models.
        
        Returns:
            List of cached model keys
        """
        return list(self._model_cache.keys())
