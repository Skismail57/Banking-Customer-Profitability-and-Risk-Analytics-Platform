"""Explainable ML using SHAP.

This module implements model explainability using SHAP (SHapley Additive exPlanations)
to provide interpretable insights into ML model predictions.

Key Features:
- Feature importance ranking
- Individual prediction explanations
- Global model interpretation
- Feature contribution analysis

NOTE: This is an analytical/educational model for decision support.
It does not make actual lending decisions.
"""

from typing import Dict, Any, List, Optional
import logging
import warnings

import pandas as pd
import numpy as np

# SHAP is optional - will use feature importance if SHAP not available
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    warnings.warn("SHAP not available. Using feature importance instead.")

from src.predictive_analytics.base import ModelBase

logger = logging.getLogger(__name__)


class ModelExplainer:
    """Model explainer using SHAP for interpretability.
    
    This class provides explainability for ML models, allowing stakeholders
    to understand why models make specific predictions.
    
    Assumptions:
    - Model is trained and available
    - Feature names are available
    - SHAP values can be computed for the model
    
    Limitations:
    - SHAP computation can be expensive for large datasets
    - Approximate SHAP values may have some error
    - Does not explain feature interactions by default
    - May not work well with all model types
    
    Fairness Considerations:
    - Analyze feature importance across demographic groups
    - Check for disparate impact in feature contributions
    - Ensure explanations are understandable to all stakeholders
    - Regular audit for bias in feature importance
    """
    
    def __init__(self, model: ModelBase, use_shap: bool = True):
        """Initialize Model Explainer.
        
        Args:
            model: Trained model to explain
            use_shap: Whether to use SHAP (falls back to feature importance if False)
        """
        self.model = model
        self.use_shap = use_shap and SHAP_AVAILABLE
        self.explainer = None
        self.shap_values = None
        
        if self.use_shap:
            self._initialize_shap_explainer()
    
    def _initialize_shap_explainer(self):
        """Initialize SHAP explainer based on model type."""
        try:
            # Try to use TreeExplainer for tree-based models
            if hasattr(self.model.model, 'feature_importances_'):
                self.explainer = shap.TreeExplainer(self.model.model)
                logger.info("Initialized SHAP TreeExplainer")
            elif hasattr(self.model.model, 'coef_'):
                # Linear model
                self.explainer = shap.LinearExplainer(self.model.model)
                logger.info("Initialized SHAP LinearExplainer")
            else:
                # Fallback to KernelExplainer (slower but general)
                self.explainer = shap.KernelExplainer(self.model.model.predict_proba)
                logger.info("Initialized SHAP KernelExplainer")
        except Exception as e:
            logger.warning(f"Could not initialize SHAP explainer: {e}. Falling back to feature importance.")
            self.use_shap = False
    
    def explain_prediction(
        self,
        features: pd.DataFrame,
        feature_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Explain a single prediction.
        
        Args:
            features: Feature values for prediction
            feature_names: Optional list of feature names
        
        Returns:
            Dictionary with explanation
        """
        if feature_names is None:
            feature_names = features.columns.tolist()
        
        if self.use_shap and self.explainer is not None:
            return self._explain_with_shap(features, feature_names)
        else:
            return self._explain_with_feature_importance(features, feature_names)
    
    def _explain_with_shap(
        self,
        features: pd.DataFrame,
        feature_names: List[str]
    ) -> Dict[str, Any]:
        """Explain prediction using SHAP.
        
        Args:
            features: Feature values
            feature_names: List of feature names
        
        Returns:
            Dictionary with SHAP explanation
        """
        try:
            # Calculate SHAP values
            shap_values = self.explainer.shap_values(features.iloc[[0]])
            
            # Get base value (expected value)
            base_value = self.explainer.expected_value
            
            # Get prediction
            prediction = self.model.model.predict(features.iloc[[0]])[0]
            
            # Calculate feature contributions
            contributions = []
            for i, feature_name in enumerate(feature_names):
                if i < len(shap_values):
                    contribution = float(shap_values[0][i])
                    contributions.append({
                        'feature': feature_name,
                        'contribution': contribution,
                        'value': float(features.iloc[0][i])
                    })
            
            # Sort by absolute contribution
            contributions.sort(key=lambda x: abs(x['contribution']), reverse=True)
            
            return {
                'method': 'SHAP',
                'prediction': float(prediction),
                'base_value': float(base_value) if not isinstance(base_value, list) else float(base_value[0]),
                'feature_contributions': contributions,
                'top_positive_features': [c for c in contributions if c['contribution'] > 0][:5],
                'top_negative_features': [c for c in contributions if c['contribution'] < 0][:5],
                'interpretation': self._interpret_shap_values(contributions, prediction)
            }
            
        except Exception as e:
            logger.error(f"Error in SHAP explanation: {e}")
            return self._explain_with_feature_importance(features, feature_names)
    
    def _explain_with_feature_importance(
        self,
        features: pd.DataFrame,
        feature_names: List[str]
    ) -> Dict[str, Any]:
        """Explain prediction using feature importance.
        
        Args:
            features: Feature values
            feature_names: List of feature names
        
        Returns:
            Dictionary with feature importance explanation
        """
        # Get feature importance from model
        if hasattr(self.model.model, 'feature_importances_'):
            importances = self.model.model.feature_importances_
        elif hasattr(self.model.model, 'coef_'):
            importances = np.abs(self.model.model.coef_[0])
        else:
            importances = np.ones(len(feature_names)) / len(feature_names)
        
        # Calculate contributions based on feature value * importance
        contributions = []
        for i, feature_name in enumerate(feature_names):
            if i < len(importances):
                contribution = float(features.iloc[0][i] * importances[i])
                contributions.append({
                    'feature': feature_name,
                    'contribution': contribution,
                    'importance': float(importances[i]),
                    'value': float(features.iloc[0][i])
                })
        
        # Sort by absolute contribution
        contributions.sort(key=lambda x: abs(x['contribution']), reverse=True)
        
        # Get prediction
        prediction = self.model.model.predict(features.iloc[[0]])[0]
        
        return {
            'method': 'feature_importance',
            'prediction': float(prediction),
            'feature_contributions': contributions,
            'top_positive_features': [c for c in contributions if c['contribution'] > 0][:5],
            'top_negative_features': [c for c in contributions if c['contribution'] < 0][:5],
            'interpretation': self._interpret_feature_importance(contributions, prediction)
        }
    
    def _interpret_shap_values(
        self,
        contributions: List[Dict[str, Any]],
        prediction: float
    ) -> str:
        """Interpret SHAP values for business context.
        
        Args:
            contributions: Feature contributions
            prediction: Model prediction
        
        Returns:
            Interpretation string
        """
        top_positive = contributions[0] if contributions and contributions[0]['contribution'] > 0 else None
        top_negative = next((c for c in contributions if c['contribution'] < 0), None)
        
        interpretation = f"Model predicts {prediction:.2f}. "
        
        if top_positive:
            interpretation += f"Primary driver: {top_positive['feature']} (contribution: {top_positive['contribution']:.3f}). "
        
        if top_negative:
            interpretation += f"Primary reducer: {top_negative['feature']} (contribution: {top_negative['contribution']:.3f})."
        
        return interpretation
    
    def _interpret_feature_importance(
        self,
        contributions: List[Dict[str, Any]],
        prediction: float
    ) -> str:
        """Interpret feature importance for business context.
        
        Args:
            contributions: Feature contributions
            prediction: Model prediction
        
        Returns:
            Interpretation string
        """
        top_positive = contributions[0] if contributions and contributions[0]['contribution'] > 0 else None
        top_negative = next((c for c in contributions if c['contribution'] < 0), None)
        
        interpretation = f"Model predicts {prediction:.2f}. "
        
        if top_positive:
            interpretation += f"Most important positive factor: {top_positive['feature']} (importance: {top_positive['importance']:.3f}). "
        
        if top_negative:
            interpretation += f"Most important negative factor: {top_negative['feature']} (importance: {top_negative['importance']:.3f})."
        
        interpretation += " Note: Based on global feature importance, not local SHAP values."
        
        return interpretation
    
    def get_global_feature_importance(
        self,
        feature_names: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Get global feature importance.
        
        Args:
            feature_names: Optional list of feature names
        
        Returns:
            DataFrame with feature importance
        """
        if hasattr(self.model.model, 'feature_importances_'):
            importances = self.model.model.feature_importances_
        elif hasattr(self.model.model, 'coef_'):
            importances = np.abs(self.model.model.coef_[0])
        else:
            logger.warning("Model does not have feature_importances_ or coef_")
            return pd.DataFrame()
        
        if feature_names is None:
            feature_names = [f'feature_{i}' for i in range(len(importances))]
        
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': importances
        }).sort_values('importance', ascending=False)
        
        return importance_df
    
    def explain_batch(
        self,
        features_df: pd.DataFrame,
        feature_names: Optional[List[str]] = None,
        max_samples: int = 100
    ) -> pd.DataFrame:
        """Explain predictions for a batch of samples.
        
        Args:
            features_df: DataFrame with features
            feature_names: Optional list of feature names
            max_samples: Maximum number of samples to explain
        
        Returns:
            DataFrame with explanations
        """
        if feature_names is None:
            feature_names = features_df.columns.tolist()
        
        # Limit samples for performance
        if len(features_df) > max_samples:
            features_df = features_df.sample(max_samples, random_state=42)
        
        explanations = []
        
        for idx, row in features_df.iterrows():
            explanation = self.explain_prediction(
                pd.DataFrame([row]),
                feature_names
            )
            explanation['sample_index'] = idx
            explanations.append(explanation)
        
        return pd.DataFrame(explanations)
    
    def generate_explanation_report(
        self,
        features_df: pd.DataFrame,
        feature_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive explanation report.
        
        Args:
            features_df: DataFrame with features
            feature_names: Optional list of feature names
        
        Returns:
            Dictionary with explanation report
        """
        logger.info("Generating explanation report")
        
        # Get global feature importance
        global_importance = self.get_global_feature_importance(feature_names)
        
        # Explain a sample of predictions
        sample_explanations = self.explain_batch(features_df, feature_names, max_samples=10)
        
        report = {
            'model_type': type(self.model.model).__name__,
            'explanation_method': 'SHAP' if self.use_shap else 'feature_importance',
            'global_feature_importance': global_importance.to_dict('records') if not global_importance.empty else [],
            'sample_explanations': sample_explanations.to_dict('records') if not sample_explanations.empty else [],
            'top_features': global_importance.head(10).to_dict('records') if not global_importance.empty else [],
            'assumptions': [
                'SHAP values represent marginal contribution of each feature',
                'Feature importance is based on the trained model',
                'Explanations are model-specific and may not generalize',
                'SHAP assumes feature independence (approximation)'
            ],
            'limitations': [
                'SHAP computation can be expensive for large datasets',
                'Approximate SHAP values may have some error',
                'Does not explain feature interactions by default',
                'May not work well with all model types'
            ],
            'fairness_considerations': [
                'Analyze feature importance across demographic groups',
                'Check for disparate impact in feature contributions',
                'Ensure explanations are understandable to stakeholders',
                'Regular audit for bias in feature importance'
            ]
        }
        
        logger.info("Explanation report generated")
        return report
