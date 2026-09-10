"""Unit tests for data splitting."""

import pytest
import pandas as pd

from src.predictive_analytics.splitting import DataSplitter


class TestDataSplitter:
    """Tests for DataSplitter."""
    
    def test_split_train_val_test(self):
        """Test train/validation/test split."""
        splitter = DataSplitter()
        
        df = pd.DataFrame({
            "customer_key": range(100),
            "target": [0] * 80 + [1] * 20
        })
        
        train_df, val_df, test_df = splitter.split_train_val_test(df, "target")
        
        assert len(train_df) + len(val_df) + len(test_df) == 100
        assert len(train_df) > 0
        assert len(val_df) > 0
        assert len(test_df) > 0
    
    def test_get_features_and_target(self):
        """Test separating features and target."""
        splitter = DataSplitter()
        
        df = pd.DataFrame({
            "feature1": [1, 2, 3],
            "feature2": [4, 5, 6],
            "target": [0, 1, 0]
        })
        
        X, y = splitter.get_features_and_target(df, "target")
        
        assert list(X.columns) == ["feature1", "feature2"]
        assert len(y) == 3
