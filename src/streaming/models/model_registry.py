"""Model registry for ML model management.

This module provides model registry capabilities for the banking analytics
platform, managing model versions, deployments, and rollbacks.

Assumptions:
- Models are stored in a model repository (S3, local filesystem, or MLflow)
- Model metadata is stored in Redis for fast access
- Model artifacts include model files, configuration, and performance metrics

Limitations:
- Model storage requires external repository (not implemented here)
- No support for model A/B testing
- No support for multi-armed bandit deployment

Fairness Considerations:
- Model registry should track fairness metrics for each version
- Ensure model deployment considers fairness impact
- Provide model version comparison for bias analysis
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from enum import Enum
import logging
import uuid
from dataclasses import dataclass
from collections import defaultdict

from src.streaming.config import StreamingConfig
from src.streaming.features.feature_store import FeatureStore

logger = logging.getLogger(__name__)


class ModelStatus(Enum):
    """Model deployment status."""
    REGISTERED = "registered"
    STAGED = "staged"
    DEPLOYED = "deployed"
    RETIRED = "retired"
    FAILED = "failed"


@dataclass
class ModelVersion:
    """Model version metadata."""
    model_id: str
    version: str
    model_type: str  # risk, anomaly, recommendation
    framework: str  # sklearn, tensorflow, pytorch
    created_at: datetime
    created_by: str
    model_path: str
    feature_schema: Dict[str, Any]
    performance_metrics: Dict[str, float]
    fairness_metrics: Optional[Dict[str, float]] = None
    status: str = ModelStatus.REGISTERED.value
    description: Optional[str] = None
    hyperparameters: Optional[Dict[str, Any]] = None


@dataclass
class ModelDeployment:
    """Model deployment record."""
    deployment_id: str
    model_id: str
    version: str
    environment: str  # development, staging, production
    deployed_at: datetime
    deployed_by: str
    status: str
    deployment_config: Dict[str, Any]
    rollback_version: Optional[str] = None


class ModelRegistry:
    """Model registry for ML model management.
    
    This registry manages model versions, deployments, and rollbacks for
    the streaming platform.
    
    Key Features:
    - Register and track model versions
    - Deploy models to different environments
    - Rollback to previous versions
    - Track model performance and fairness metrics
    - Maintain deployment history
    """
    
    def __init__(
        self,
        config: StreamingConfig,
        feature_store: FeatureStore
    ):
        """Initialize model registry.
        
        Args:
            config: Streaming configuration
            feature_store: Redis feature store for metadata storage
        """
        self.config = config
        self.feature_store = feature_store
        
        # Key patterns
        self.MODEL_KEY_PATTERN = "model:{model_id}"
        self.DEPLOYMENT_KEY_PATTERN = "deployment:{deployment_id}"
        self.ENVIRONMENT_KEY_PATTERN = "environment:{environment}:current_model"
    
    def register_model(
        self,
        model_type: str,
        framework: str,
        model_path: str,
        feature_schema: Dict[str, Any],
        performance_metrics: Dict[str, float],
        created_by: str,
        fairness_metrics: Optional[Dict[str, float]] = None,
        description: Optional[str] = None,
        hyperparameters: Optional[Dict[str, Any]] = None
    ) -> ModelVersion:
        """Register a new model version.
        
        Args:
            model_type: Type of model (risk, anomaly, recommendation)
            framework: ML framework (sklearn, tensorflow, pytorch)
            model_path: Path to model artifacts
            feature_schema: Schema of expected features
            performance_metrics: Model performance metrics
            created_by: User who created the model
            fairness_metrics: Fairness metrics (optional)
            description: Model description
            hyperparameters: Model hyperparameters
        
        Returns:
            ModelVersion
        """
        logger.info(f"Registering new {model_type} model by {created_by}")
        
        # Generate model ID
        model_id = str(uuid.uuid4())
        version = self._generate_version(model_type)
        
        # Create model version
        model_version = ModelVersion(
            model_id=model_id,
            version=version,
            model_type=model_type,
            framework=framework,
            created_at=datetime.now(timezone.utc).replace(tzinfo=None),
            created_by=created_by,
            model_path=model_path,
            feature_schema=feature_schema,
            performance_metrics=performance_metrics,
            fairness_metrics=fairness_metrics,
            status=ModelStatus.REGISTERED.value,
            description=description,
            hyperparameters=hyperparameters
        )
        
        # Store in Redis
        self._store_model_version(model_version)
        
        return model_version
    
    def deploy_model(
        self,
        model_id: str,
        environment: str,
        deployed_by: str,
        deployment_config: Optional[Dict[str, Any]] = None
    ) -> ModelDeployment:
        """Deploy a model to an environment.
        
        Args:
            model_id: Model identifier
            environment: Target environment (development, staging, production)
            deployed_by: User deploying the model
            deployment_config: Deployment configuration
        
        Returns:
            ModelDeployment
        """
        logger.info(f"Deploying model {model_id} to {environment} by {deployed_by}")
        
        # Get model version
        model_version = self.get_model(model_id)
        if not model_version:
            raise ValueError(f"Model {model_id} not found")
        
        # Get current deployed model for rollback
        current_deployment = self.get_current_deployment(environment)
        rollback_version = current_deployment.version if current_deployment else None
        
        # Create deployment record
        deployment_id = str(uuid.uuid4())
        deployment = ModelDeployment(
            deployment_id=deployment_id,
            model_id=model_id,
            version=model_version.version,
            environment=environment,
            deployed_at=datetime.now(timezone.utc).replace(tzinfo=None),
            deployed_by=deployed_by,
            status=ModelStatus.DEPLOYED.value,
            deployment_config=deployment_config or {},
            rollback_version=rollback_version
        )
        
        # Store deployment
        self._store_deployment(deployment)
        
        # Update environment current model
        self._update_environment_current_model(environment, model_id, model_version.version)
        
        # Update model status
        model_version.status = ModelStatus.DEPLOYED.value
        self._store_model_version(model_version)
        
        return deployment
    
    def rollback_model(
        self,
        environment: str,
        rolled_back_by: str
    ) -> Optional[ModelDeployment]:
        """Rollback to previous model version.
        
        Args:
            environment: Environment to rollback
            rolled_back_by: User performing rollback
        
        Returns:
            New deployment record or None if no rollback target
        """
        logger.info(f"Rolling back {environment} by {rolled_back_by}")
        
        # Get current deployment
        current_deployment = self.get_current_deployment(environment)
        if not current_deployment:
            logger.warning(f"No current deployment in {environment}")
            return None
        
        rollback_version = current_deployment.rollback_version
        if not rollback_version:
            logger.warning(f"No rollback version available in {environment}")
            return None
        
        # Find model with rollback version
        model_version = self._find_model_by_version(current_deployment.model_id, rollback_version)
        if not model_version:
            logger.warning(f"Rollback version {rollback_version} not found")
            return None
        
        # Deploy rollback version
        return self.deploy_model(
            model_version.model_id,
            environment,
            rolled_back_by,
            {'rollback': True, 'from_version': current_deployment.version}
        )
    
    def get_model(self, model_id: str) -> Optional[ModelVersion]:
        """Get model version by ID.
        
        Args:
            model_id: Model identifier
        
        Returns:
            ModelVersion or None if not found
        """
        model_key = self.MODEL_KEY_PATTERN.format(model_id=model_id)
        model_data = self.feature_store.redis_client.get(model_key)
        
        if model_data:
            import json
            model_dict = json.loads(model_data)
            return self._dict_to_model_version(model_dict)
        
        return None
    
    def get_current_deployment(self, environment: str) -> Optional[ModelDeployment]:
        """Get current deployment for environment.
        
        Args:
            environment: Environment name
        
        Returns:
            ModelDeployment or None if not found
        """
        env_key = self.ENVIRONMENT_KEY_PATTERN.format(environment=environment)
        current_model = self.feature_store.redis_client.get(env_key)
        
        if current_model:
            import json
            current_dict = json.loads(current_model)
            deployment_id = current_dict.get('deployment_id')
            
            if deployment_id:
                deployment_key = self.DEPLOYMENT_KEY_PATTERN.format(deployment_id=deployment_id)
                deployment_data = self.feature_store.redis_client.get(deployment_key)
                
                if deployment_data:
                    deployment_dict = json.loads(deployment_data)
                    return self._dict_to_deployment(deployment_dict)
        
        return None
    
    def list_models(
        self,
        model_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[ModelVersion]:
        """List models with optional filters.
        
        Args:
            model_type: Filter by model type
            status: Filter by status
        
        Returns:
            List of ModelVersion
        """
        pattern = f"model:*"
        model_keys = self.feature_store.redis_client.keys(pattern)
        
        models = []
        for model_key in model_keys:
            model_data = self.feature_store.redis_client.get(model_key)
            if model_data:
                import json
                model_dict = json.loads(model_data)
                model_version = self._dict_to_model_version(model_dict)
                
                # Apply filters
                if model_type and model_version.model_type != model_type:
                    continue
                if status and model_version.status != status:
                    continue
                
                models.append(model_version)
        
        return models
    
    def _generate_version(self, model_type: str) -> str:
        """Generate version string for model.
        
        Args:
            model_type: Model type
        
        Returns:
            Version string
        """
        # Get existing models of this type
        existing_models = self.list_models(model_type=model_type)
        
        if not existing_models:
            return "1.0.0"
        
        # Extract version numbers and increment
        versions = [m.version for m in existing_models]
        max_version = max(versions, key=lambda v: [int(x) for x in v.split('.')])
        
        major, minor, patch = max_version.split('.')
        return f"{major}.{int(minor) + 1}.0"
    
    def _store_model_version(self, model_version: ModelVersion):
        """Store model version in Redis.
        
        Args:
            model_version: Model version to store
        """
        model_key = self.MODEL_KEY_PATTERN.format(model_id=model_version.model_id)
        
        model_dict = {
            'model_id': model_version.model_id,
            'version': model_version.version,
            'model_type': model_version.model_type,
            'framework': model_version.framework,
            'created_at': model_version.created_at.isoformat(),
            'created_by': model_version.created_by,
            'model_path': model_version.model_path,
            'feature_schema': model_version.feature_schema,
            'performance_metrics': model_version.performance_metrics,
            'fairness_metrics': model_version.fairness_metrics,
            'status': model_version.status,
            'description': model_version.description,
            'hyperparameters': model_version.hyperparameters
        }
        
        import json
        model_json = json.dumps(model_dict)
        
        # Store with long TTL for model retention
        ttl = 365 * 24 * 60 * 60  # 1 year
        self.feature_store.redis_client.setex(model_key, ttl, model_json)
    
    def _store_deployment(self, deployment: ModelDeployment):
        """Store deployment record in Redis.
        
        Args:
            deployment: Deployment to store
        """
        deployment_key = self.DEPLOYMENT_KEY_PATTERN.format(deployment_id=deployment.deployment_id)
        
        deployment_dict = {
            'deployment_id': deployment.deployment_id,
            'model_id': deployment.model_id,
            'version': deployment.version,
            'environment': deployment.environment,
            'deployed_at': deployment.deployed_at.isoformat(),
            'deployed_by': deployment.deployed_by,
            'status': deployment.status,
            'deployment_config': deployment.deployment_config,
            'rollback_version': deployment.rollback_version
        }
        
        import json
        deployment_json = json.dumps(deployment_dict)
        
        # Store with TTL from config
        ttl = self.config.feature_store.ttl_seconds
        self.feature_store.redis_client.setex(deployment_key, ttl, deployment_json)
    
    def _update_environment_current_model(
        self,
        environment: str,
        model_id: str,
        version: str
    ):
        """Update current model for environment.
        
        Args:
            environment: Environment name
            model_id: Model identifier
            version: Model version
        """
        env_key = self.ENVIRONMENT_KEY_PATTERN.format(environment=environment)
        
        # Get current deployment to get deployment_id
        current_deployment = self.get_current_deployment(environment)
        deployment_id = current_deployment.deployment_id if current_deployment else str(uuid.uuid4())
        
        current_dict = {
            'model_id': model_id,
            'version': version,
            'deployment_id': deployment_id,
            'updated_at': datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
        }
        
        import json
        current_json = json.dumps(current_dict)
        
        ttl = self.config.feature_store.ttl_seconds
        self.feature_store.redis_client.setex(env_key, ttl, current_json)
    
    def _find_model_by_version(
        self,
        model_id: str,
        version: str
    ) -> Optional[ModelVersion]:
        """Find model by ID and version.
        
        Args:
            model_id: Model identifier
            version: Version string
        
        Returns:
            ModelVersion or None if not found
        """
        # For simplicity, just get the model and check version
        # In production, this would query a proper index
        model = self.get_model(model_id)
        if model and model.version == version:
            return model
        return None
    
    def _dict_to_model_version(self, model_dict: Dict[str, Any]) -> ModelVersion:
        """Convert dictionary to ModelVersion.
        
        Args:
            model_dict: Model dictionary
        
        Returns:
            ModelVersion
        """
        return ModelVersion(
            model_id=model_dict['model_id'],
            version=model_dict['version'],
            model_type=model_dict['model_type'],
            framework=model_dict['framework'],
            created_at=datetime.fromisoformat(model_dict['created_at']),
            created_by=model_dict['created_by'],
            model_path=model_dict['model_path'],
            feature_schema=model_dict['feature_schema'],
            performance_metrics=model_dict['performance_metrics'],
            fairness_metrics=model_dict.get('fairness_metrics'),
            status=model_dict['status'],
            description=model_dict.get('description'),
            hyperparameters=model_dict.get('hyperparameters')
        )
    
    def _dict_to_deployment(self, deployment_dict: Dict[str, Any]) -> ModelDeployment:
        """Convert dictionary to ModelDeployment.
        
        Args:
            deployment_dict: Deployment dictionary
        
        Returns:
            ModelDeployment
        """
        return ModelDeployment(
            deployment_id=deployment_dict['deployment_id'],
            model_id=deployment_dict['model_id'],
            version=deployment_dict['version'],
            environment=deployment_dict['environment'],
            deployed_at=datetime.fromisoformat(deployment_dict['deployed_at']),
            deployed_by=deployment_dict['deployed_by'],
            status=deployment_dict['status'],
            deployment_config=deployment_dict['deployment_config'],
            rollback_version=deployment_dict.get('rollback_version')
        )
