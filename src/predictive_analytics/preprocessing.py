"""Preprocessing pipelines and feature engineering."""

from typing import Dict, Any, List, Optional
import logging

import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

from src.predictive_analytics.base import ModelBase

logger = logging.getLogger(__name__)


class PreprocessingPipeline(ModelBase):
    """Create preprocessing pipelines for ML models."""
    
    def create_preprocessing_pipeline(
        self,
        numeric_features: List[str],
        categorical_features: List[str],
        numeric_transformer: str = "standard",
        categorical_transformer: str = "onehot"
    ) -> ColumnTransformer:
        """Create preprocessing pipeline.
        
        Args:
            numeric_features: List of numeric feature columns
            categorical_features: List of categorical feature columns
            numeric_transformer: Type of numeric transformation (standard, minmax)
            categorical_transformer: Type of categorical transformation (onehot)
        
        Returns:
            ColumnTransformer with preprocessing steps
        """
        # Numeric preprocessing
        if numeric_transformer == "standard":
            numeric_transformer_pipeline = Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler())
            ])
        elif numeric_transformer == "minmax":
            numeric_transformer_pipeline = Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", MinMaxScaler())
            ])
        else:
            numeric_transformer_pipeline = Pipeline([
                ("imputer", SimpleImputer(strategy="median"))
            ])
        
        # Categorical preprocessing
        if categorical_transformer == "onehot":
            categorical_transformer_pipeline = Pipeline([
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
            ])
        else:
            categorical_transformer_pipeline = Pipeline([
                ("imputer", SimpleImputer(strategy="most_frequent"))
            ])
        
        # Combine transformers
        preprocessor = ColumnTransformer(
            transformers=[
                ("num", numeric_transformer_pipeline, numeric_features),
                ("cat", categorical_transformer_pipeline, categorical_features)
            ]
        )
        
        return preprocessor
    
    def engineer_features(
        self,
        df: pd.DataFrame,
        feature_configs: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> pd.DataFrame:
        """Engineer features based on configuration.
        
        Args:
            df: DataFrame with base features
            feature_configs: Configuration for feature engineering
        
        Returns:
            DataFrame with engineered features
        """
        df = df.copy()
        
        if feature_configs is None:
            return df
        
        for feature_name, config in feature_configs.items():
            feature_type = config.get("type", "derived")
            
            if feature_type == "ratio":
                numerator = config["numerator"]
                denominator = config["denominator"]
                df[feature_name] = df[numerator] / (df[denominator] + 1e-8)
            
            elif feature_type == "log":
                source = config["source"]
                df[feature_name] = np.log1p(df[source])
            
            elif feature_type == "bin":
                source = config["source"]
                bins = config.get("bins", 5)
                df[feature_name] = pd.cut(df[source], bins=bins, labels=False)
            
            elif feature_type == "interaction":
                features = config["features"]
                operation = config.get("operation", "multiply")
                
                if operation == "multiply":
                    df[feature_name] = df[features[0]] * df[features[1]]
                elif operation == "add":
                    df[feature_name] = df[features[0]] + df[features[1]]
        
        return df
