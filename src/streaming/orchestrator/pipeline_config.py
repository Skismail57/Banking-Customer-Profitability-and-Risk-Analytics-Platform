"""Pipeline configuration loader.

This module provides configuration loading for the streaming pipeline,
including component enable/disable flags and processing rules.
"""

from typing import Dict, Any, Optional, List
import logging
import yaml
from pathlib import Path

from src.streaming.config import StreamingConfig

logger = logging.getLogger(__name__)


class PipelineConfig:
    """Pipeline configuration.
    
    This class loads and manages pipeline configuration, including:
    - Component enable/disable flags
    - Processing rules
    - Threshold configurations
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize pipeline configuration.
        
        Args:
            config_path: Path to pipeline configuration file
        """
        self.config_path = config_path or "config/pipeline.yaml"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load pipeline configuration from file.
        
        Returns:
            Configuration dictionary
        """
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = yaml.safe_load(f)
                logger.info(f"Loaded pipeline configuration from {self.config_path}")
                return config
            else:
                logger.warning(f"Pipeline config file not found at {self.config_path}, using defaults")
                return self._get_default_config()
        except Exception as e:
            logger.error(f"Error loading pipeline configuration: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default pipeline configuration.
        
        Returns:
            Default configuration dictionary
        """
        return {
            'components': {
                'anomaly_detection': {
                    'enabled': True,
                    'methods': ['iqr', 'zscore'],
                    'thresholds': {
                        'amount_threshold': 3.0,
                        'velocity_window_minutes': 60,
                        'velocity_max_transactions': 10
                    }
                },
                'risk_scoring': {
                    'enabled': True,
                    'risk_types': ['credit', 'payment', 'concentration']
                },
                'early_warning': {
                    'enabled': True,
                    'warning_types': ['utilization', 'payment', 'balance']
                },
                'alert_generation': {
                    'enabled': True,
                    'min_severity': 'high',
                    'deduplication_window_seconds': 300
                },
                'model_inference': {
                    'enabled': True,
                    'models': ['churn_predictor', 'risk_predictor', 'clv_predictor']
                },
                'decision_audit': {
                    'enabled': True,
                    'snapshot_features': True
                }
            },
            'processing': {
                'batch_size': 100,
                'max_latency_ms': 1000,
                'parallel_workers': 4
            },
            'topics': {
                'input_topic': 'banking.events.raw',
                'output_topic': 'banking.events.processed',
                'dlq_topic': 'banking.dlq'
            }
        }
    
    def is_component_enabled(self, component_name: str) -> bool:
        """Check if a component is enabled.
        
        Args:
            component_name: Component name (e.g., 'anomaly_detection')
        
        Returns:
            True if enabled, False otherwise
        """
        return self.config.get('components', {}).get(component_name, {}).get('enabled', True)
    
    def get_component_config(self, component_name: str) -> Dict[str, Any]:
        """Get configuration for a component.
        
        Args:
            component_name: Component name
        
        Returns:
            Component configuration dictionary
        """
        return self.config.get('components', {}).get(component_name, {})
    
    def get_processing_config(self) -> Dict[str, Any]:
        """Get processing configuration.
        
        Returns:
            Processing configuration dictionary
        """
        return self.config.get('processing', {})
    
    def get_topic_config(self) -> Dict[str, Any]:
        """Get topic configuration.
        
        Returns:
            Topic configuration dictionary
        """
        return self.config.get('topics', {})
    
    def get_anomaly_thresholds(self) -> Dict[str, Any]:
        """Get anomaly detection thresholds.
        
        Returns:
            Thresholds dictionary
        """
        return self.get_component_config('anomaly_detection').get('thresholds', {})
    
    def get_alert_min_severity(self) -> str:
        """Get minimum alert severity.
        
        Returns:
            Minimum severity level
        """
        return self.get_component_config('alert_generation').get('min_severity', 'high')
    
    def get_enabled_models(self) -> List[str]:
        """Get list of enabled models.
        
        Returns:
            List of model names
        """
        return self.get_component_config('model_inference').get('models', [])
    
    def save_config(self, config_path: Optional[str] = None):
        """Save configuration to file.
        
        Args:
            config_path: Path to save configuration (uses default if None)
        """
        save_path = config_path or self.config_path
        
        try:
            with open(save_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
            logger.info(f"Saved pipeline configuration to {save_path}")
        except Exception as e:
            logger.error(f"Error saving pipeline configuration: {e}")
    
    def update_component_config(
        self,
        component_name: str,
        config_updates: Dict[str, Any]
    ):
        """Update configuration for a component.
        
        Args:
            component_name: Component name
            config_updates: Configuration updates
        """
        if component_name not in self.config.get('components', {}):
            self.config.setdefault('components', {})[component_name] = {}
        
        self.config['components'][component_name].update(config_updates)
        logger.info(f"Updated configuration for component {component_name}")
