"""Model registry for ML model lifecycle management.

This module provides model registry capabilities for the banking analytics
platform, tracking model versions and deployments for production ML.

Assumptions:
- Models are stored in file system (existing ModelPersistence)
- Model metadata is stored in database (dim_model_registry table)
- Model promotion follows dev → staging → prod workflow

Limitations:
- No support for model A/B testing
- No support for canary deployments
- No support for automatic model retraining

Fairness Considerations:
- Model registry should track fairness metrics
- Monitor model performance across demographic segments
- Ensure model versions are validated for fairness before promotion
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
import logging
import uuid
from dataclasses import dataclass
from enum import Enum

from src.streaming.config import StreamingConfig
from src.streaming.features.feature_store import FeatureStore

logger = logging.getLogger(__name__)


class ValidationStatus(Enum):
    """Model validation status."""
    PENDING = "pending"
    VALIDATED = "validated"
    FAILED = "failed"


class DeploymentStatus(Enum):
    """Model deployment status."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    ARCHIVED = "archived"


@dataclass
class ModelMetadata:
    """Model metadata."""
    model_id: str
    model_name: str
    model_version: str
    model_type: str  # churn, risk, clv, anomaly
    framework: Optional[str]  # sklearn, xgboost, etc.
    artifact_location: Optional[str]
    training_dataset_version: Optional[str]
    feature_version: Optional[str]
    hyperparameters: Optional[Dict[str, Any]]
    metrics: Optional[Dict[str, Any]]
    validation_status: Optional[str]
    deployment_status: Optional[str]
    created_at: datetime
    promoted_at: Optional[datetime]
    archived_at: Optional[datetime]


class ModelRegistry:
    """Model registry for ML model lifecycle management.
    
    This registry tracks model versions and deployments for production ML.
    It integrates with the existing ModelPersistence for artifact storage.
    
    Key Features:
    - Register models with version tracking
    - Promote models through environments (dev → staging → prod)
    - Track model validation status
    - Query models by name, version, or deployment status
    - Support model rollback
    """
    
    def __init__(
        self,
        config: StreamingConfig,
        feature_store: FeatureStore
    ):
        """Initialize model registry.
        
        Args:
            config: Streaming configuration
            feature_store: Redis feature store for caching
        """
        self.config = config
        self.feature_store = feature_store
        
        # Registry key patterns
        self.MODEL_KEY_PATTERN = "model:{model_name}:{model_version}"
        self.MODEL_LIST_KEY_PATTERN = "models:{model_name}"
    
    def register_model(
        self,
        model_name: str,
        model_version: str,
        model_type: str,
        framework: Optional[str] = None,
        artifact_location: Optional[str] = None,
        training_dataset_version: Optional[str] = None,
        feature_version: Optional[str] = None,
        hyperparameters: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, Any]] = None
    ) -> ModelMetadata:
        """Register a new model version.
        
        Args:
            model_name: Model name (e.g., "churn_predictor")
            model_version: Model version (e.g., "v1.0.0")
            model_type: Model type (churn, risk, clv, anomaly)
            framework: ML framework (sklearn, xgboost, etc.)
            artifact_location: Path to model artifact
            training_dataset_version: Training dataset version
            feature_version: Feature version used
            hyperparameters: Model hyperparameters
            metrics: Model performance metrics
        
        Returns:
            ModelMetadata
        """
        logger.info(f"Registering model {model_name} version {model_version}")
        
        # Generate model ID
        model_id = str(uuid.uuid4())
        
        # Create metadata
        metadata = ModelMetadata(
            model_id=model_id,
            model_name=model_name,
            model_version=model_version,
            model_type=model_type,
            framework=framework,
            artifact_location=artifact_location,
            training_dataset_version=training_dataset_version,
            feature_version=feature_version,
            hyperparameters=hyperparameters,
            metrics=metrics,
            validation_status=ValidationStatus.PENDING.value,
            deployment_status=DeploymentStatus.DEVELOPMENT.value,
            created_at=datetime.utcnow(),
            promoted_at=None,
            archived_at=None
        )
        
        # Store in Redis for caching
        self._store_model_metadata(metadata)
        
        # Add to model list
        self._add_to_model_list(model_name, model_version)
        
        # Note: In production, this would also write to PostgreSQL
        # (dim_model_registry table) for long-term persistence
        
        return metadata
    
    def promote_model(
        self,
        model_name: str,
        model_version: str,
        environment: str
    ) -> bool:
        """Promote a model to an environment.
        
        Args:
            model_name: Model name
            model_version: Model version
            environment: Target environment (staging, production)
        
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Promoting model {model_name} version {model_version} to {environment}")
        
        # Get model metadata
        metadata = self.get_model(model_name, model_version)
        if not metadata:
            logger.error(f"Model {model_name} version {model_version} not found")
            return False
        
        # Validate promotion path
        current_status = metadata.deployment_status
        if environment == "staging" and current_status != DeploymentStatus.DEVELOPMENT.value:
            logger.error(f"Cannot promote from {current_status} to staging")
            return False
        if environment == "production" and current_status != DeploymentStatus.STAGING.value:
            logger.error(f"Cannot promote from {current_status} to production")
            return False
        
        # Update deployment status
        metadata.deployment_status = environment.upper()
        metadata.promoted_at = datetime.utcnow()
        
        # Store updated metadata
        self._store_model_metadata(metadata)
        
        return True
    
    def rollback_model(
        self,
        model_name: str,
        to_version: str,
        environment: str
    ) -> bool:
        """Rollback to a previous model version.
        
        Args:
            model_name: Model name
            to_version: Target version to rollback to
            environment: Environment
        
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Rolling back model {model_name} to version {to_version} in {environment}")
        
        # Get target model metadata
        metadata = self.get_model(model_name, to_version)
        if not metadata:
            logger.error(f"Model {model_name} version {to_version} not found")
            return False
        
        # Update deployment status
        metadata.deployment_status = environment.upper()
        metadata.promoted_at = datetime.utcnow()
        
        # Store updated metadata
        self._store_model_metadata(metadata)
        
        return True
    
    def get_model(
        self,
        model_name: str,
        model_version: Optional[str] = None
    ) -> Optional[ModelMetadata]:
        """Get model metadata.
        
        Args:
            model_name: Model name
            model_version: Model version (None = latest)
        
        Returns:
            ModelMetadata or None if not found
        """
        if model_version is None:
            # Get latest version
            model_version = self._get_latest_version(model_name)
            if model_version is None:
                return None
        
        model_key = self.MODEL_KEY_PATTERN.format(
            model_name=model_name,
            model_version=model_version
        )
        
        model_data = self.feature_store.redis_client.get(model_key)
        
        if model_data:
            import json
            model_dict = json.loads(model_data)
            return ModelMetadata(**model_dict)
        
        return None
    
    def list_models(
        self,
        model_name: Optional[str] = None,
        model_type: Optional[str] = None,
        deployment_status: Optional[str] = None
    ) -> List[ModelMetadata]:
        """List models matching criteria.
        
        Args:
            model_name: Filter by model name (optional)
            model_type: Filter by model type (optional)
            deployment_status: Filter by deployment status (optional)
        
        Returns:
            List of ModelMetadata
        """
        # Get all model keys
        pattern = "model:*"
        model_keys = self.feature_store.redis_client.keys(pattern)
        
        models = []
        for model_key in model_keys:
            model_data = self.feature_store.redis_client.get(model_key)
            if model_data:
                import json
                model_dict = json.loads(model_data)
                
                # Apply filters
                if model_name and model_dict.get('model_name') != model_name:
                    continue
                if model_type and model_dict.get('model_type') != model_type:
                    continue
                if deployment_status and model_dict.get('deployment_status') != deployment_status:
                    continue
                
                models.append(ModelMetadata(**model_dict))
        
        # Sort by created_at (most recent first)
        models.sort(key=lambda x: x.created_at, reverse=True)
        
        return models
    
    def get_production_model(
        self,
        model_name: str
    ) -> Optional[ModelMetadata]:
        """Get the production model for a given name.
        
        Args:
            model_name: Model name
        
        Returns:
            ModelMetadata or None if not found
        """
        models = self.list_models(
            model_name=model_name,
            deployment_status=DeploymentStatus.PRODUCTION.value
        )
        
        if models:
            return models[0]
        
        return None
    
    def _store_model_metadata(self, metadata: ModelMetadata):
        """Store model metadata in Redis.
        
        Args:
            metadata: Model metadata to store
        """
        model_key = self.MODEL_KEY_PATTERN.format(
            model_name=metadata.model_name,
            model_version=metadata.model_version
        )
        
        import json
        metadata_dict = {
            'model_id': metadata.model_id,
            'model_name': metadata.model_name,
            'model_version': metadata.model_version,
            'model_type': metadata.model_type,
            'framework': metadata.framework,
            'artifact_location': metadata.artifact_location,
            'training_dataset_version': metadata.training_dataset_version,
            'feature_version': metadata.feature_version,
            'hyperparameters': metadata.hyperparameters,
            'metrics': metadata.metrics,
            'validation_status': metadata.validation_status,
            'deployment_status': metadata.deployment_status,
            'created_at': metadata.created_at.isoformat(),
            'promoted_at': metadata.promoted_at.isoformat() if metadata.promoted_at else None,
            'archived_at': metadata.archived_at.isoformat() if metadata.archived_at else None
        }
        
        metadata_json = json.dumps(metadata_dict)
        
        # Store with long TTL (model metadata should persist)
        ttl = self.config.feature_store.snapshot_ttl_seconds
        self.feature_store.redis_client.setex(model_key, ttl, metadata_json)
    
    def _add_to_model_list(self, model_name: str, model_version: str):
        """Add model version to model list.
        
        Args:
            model_name: Model name
            model_version: Model version
        """
        list_key = self.MODEL_LIST_KEY_PATTERN.format(model_name=model_name)
        
        # Add to sorted set (score = timestamp)
        score = datetime.utcnow().timestamp()
        self.feature_store.redis_client.zadd(list_key, {model_version: score})
    
    def _get_latest_version(self, model_name: str) -> Optional[str]:
        """Get latest model version.
        
        Args:
            model_name: Model name
        
        Returns:
            Latest version or None if not found
        """
        list_key = self.MODEL_LIST_KEY_PATTERN.format(model_name=model_name)
        
        # Get highest score (most recent)
        result = self.feature_store.redis_client.zrevrange(list_key, 0, 0)
        
        if result:
            return result[0].decode()
        
        return None
