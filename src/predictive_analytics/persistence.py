"""Model persistence and reproducibility."""

from typing import Dict, Any, Optional
import logging
import json
from datetime import datetime
import hashlib

import pandas as pd
import joblib
import pickle

from src.predictive_analytics.base import ModelBase

logger = logging.getLogger(__name__)


class ModelPersistence(ModelBase):
    """Handle model persistence and reproducibility."""
    
    def save_model(
        self,
        model,
        model_name: str,
        model_version: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Save model with metadata.
        
        Args:
            model: Trained model
            model_name: Name of the model
            model_version: Version of the model
            metadata: Additional metadata
        
        Returns:
            File path where model was saved
        """
        timestamp = datetime.now().isoformat()
        
        # Create model metadata
        model_metadata = {
            "model_name": model_name,
            "model_version": model_version,
            "saved_at": timestamp,
            "random_state": self.random_state,
            "metadata": metadata or {}
        }
        
        # Generate file path
        file_hash = hashlib.md5(f"{model_name}_{model_version}_{timestamp}".encode()).hexdigest()[:8]
        file_path = f"models/{model_name}_{model_version}_{file_hash}.pkl"
        
        # Save model and metadata
        model_data = {
            "model": model,
            "metadata": model_metadata
        }
        
        joblib.dump(model_data, file_path)
        
        # Save metadata separately
        metadata_path = file_path.replace(".pkl", "_metadata.json")
        with open(metadata_path, "w") as f:
            json.dump(model_metadata, f, indent=2)
        
        logger.info(f"Model saved to {file_path}")
        
        return file_path
    
    def load_model(self, file_path: str) -> Dict[str, Any]:
        """Load model with metadata.
        
        Args:
            file_path: Path to model file
        
        Returns:
            Dictionary with model and metadata
        """
        model_data = joblib.load(file_path)
        
        return {
            "model": model_data["model"],
            "metadata": model_data["metadata"]
        }
    
    def get_model_metadata(self, file_path: str) -> Dict[str, Any]:
        """Get model metadata without loading the model.
        
        Args:
            file_path: Path to model file
        
        Returns:
            Model metadata
        """
        metadata_path = file_path.replace(".pkl", "_metadata.json")
        
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
        
        return metadata
