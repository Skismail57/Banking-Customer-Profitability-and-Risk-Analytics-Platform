"""Unit tests for data cleaners."""

import pytest
import pandas as pd
import numpy as np

from src.ingestion.cleaners import DataCleaner, DataTransformer


class TestDataCleaner:
    """Tests for DataCleaner."""
    
    def test_handle_duplicates_keep_first(self):
        """Test duplicate handling with keep_first strategy."""
        df = pd.DataFrame({
            "col1": [1, 2, 2, 3],
            "col2": ["a", "b", "b", "c"]
        })
        
        config = {
            "handle_duplicates": True,
            "duplicate_strategy": "keep_first"
        }
        
        cleaner = DataCleaner(config)
        df_cleaned = cleaner.clean(df)
        
        assert len(df_cleaned) == 3
        assert df_cleaned.iloc[1]["col1"] == 2  # First occurrence kept
    
    def test_handle_duplicates_keep_last(self):
        """Test duplicate handling with keep_last strategy."""
        df = pd.DataFrame({
            "col1": [1, 2, 2, 3],
            "col2": ["a", "b", "b", "c"]
        })
        
        config = {
            "handle_duplicates": True,
            "duplicate_strategy": "keep_last"
        }
        
        cleaner = DataCleaner(config)
        df_cleaned = cleaner.clean(df)
        
        assert len(df_cleaned) == 3
    
    def test_handle_duplicates_drop_all(self):
        """Test duplicate handling with drop_all strategy."""
        df = pd.DataFrame({
            "col1": [1, 2, 2, 3],
            "col2": ["a", "b", "b", "c"]
        })
        
        config = {
            "handle_duplicates": True,
            "duplicate_strategy": "drop_all"
        }
        
        cleaner = DataCleaner(config)
        df_cleaned = cleaner.clean(df)
        
        assert len(df_cleaned) == 2  # Only unique rows kept
    
    def test_trim_strings(self):
        """Test string trimming."""
        df = pd.DataFrame({
            "col1": ["  hello  ", "  world  ", "test"],
            "col2": [1, 2, 3]
        })
        
        config = {"trim_strings": True}
        cleaner = DataCleaner(config)
        df_cleaned = cleaner.clean(df)
        
        assert df_cleaned["col1"].iloc[0] == "hello"
        assert df_cleaned["col1"].iloc[1] == "world"
        assert df_cleaned["col1"].iloc[2] == "test"
    
    def test_fill_nulls_numeric(self):
        """Test filling null values in numeric columns."""
        df = pd.DataFrame({
            "col1": [1, np.nan, 3],
            "col2": [4.5, np.nan, 6.7]
        })
        
        config = {"fill_numeric": 0}
        cleaner = DataCleaner(config)
        df_cleaned = cleaner.clean(df)
        
        assert df_cleaned["col1"].isnull().sum() == 0
        assert df_cleaned["col1"].iloc[1] == 0
    
    def test_fill_nulls_string(self):
        """Test filling null values in string columns."""
        df = pd.DataFrame({
            "col1": ["a", None, "c"],
            "col2": [1, 2, 3]
        })
        
        config = {"fill_string": "unknown"}
        cleaner = DataCleaner(config)
        df_cleaned = cleaner.clean(df)
        
        assert df_cleaned["col1"].isnull().sum() == 0
        assert df_cleaned["col1"].iloc[1] == "unknown"
    
    def test_remove_empty_rows(self):
        """Test removal of completely empty rows."""
        df = pd.DataFrame({
            "col1": [1, np.nan, 3],
            "col2": [4, np.nan, 6]
        })
        
        config = {}
        cleaner = DataCleaner(config)
        df_cleaned = cleaner.clean(df)
        
        assert len(df_cleaned) == 2  # Empty row removed


class TestDataTransformer:
    """Tests for DataTransformer."""
    
    def test_rename_columns(self):
        """Test column renaming."""
        df = pd.DataFrame({
            "old_col1": [1, 2, 3],
            "old_col2": ["a", "b", "c"]
        })
        
        schema = {
            "column_mappings": {
                "old_col1": "new_col1",
                "old_col2": "new_col2"
            },
            "target_columns": ["new_col1", "new_col2"]
        }
        
        transformer = DataTransformer(schema)
        df_transformed = transformer.transform(df)
        
        assert "new_col1" in df_transformed.columns
        assert "new_col2" in df_transformed.columns
        assert "old_col1" not in df_transformed.columns
    
    def test_select_columns(self):
        """Test column selection."""
        df = pd.DataFrame({
            "col1": [1, 2, 3],
            "col2": ["a", "b", "c"],
            "col3": [4.5, 5.5, 6.5]
        })
        
        schema = {
            "target_columns": ["col1", "col2"]
        }
        
        transformer = DataTransformer(schema)
        df_transformed = transformer.transform(df)
        
        assert list(df_transformed.columns) == ["col1", "col2"]
    
    def test_convert_types_int(self):
        """Test type conversion to integer."""
        df = pd.DataFrame({
            "col1": ["1", "2", "3"],
            "col2": ["a", "b", "c"]
        })
        
        schema = {
            "column_types": {
                "col1": "int"
            },
            "target_columns": ["col1", "col2"]
        }
        
        transformer = DataTransformer(schema)
        df_transformed = transformer.transform(df)
        
        # Note: Int64 allows nulls
        assert pd.api.types.is_integer_dtype(df_transformed["col1"])
    
    def test_convert_types_float(self):
        """Test type conversion to float."""
        df = pd.DataFrame({
            "col1": ["1.5", "2.5", "3.5"],
            "col2": ["a", "b", "c"]
        })
        
        schema = {
            "column_types": {
                "col1": "float"
            },
            "target_columns": ["col1", "col2"]
        }
        
        transformer = DataTransformer(schema)
        df_transformed = transformer.transform(df)
        
        assert pd.api.types.is_float_dtype(df_transformed["col1"])
    
    def test_add_derived_columns(self):
        """Test adding derived columns."""
        df = pd.DataFrame({
            "col1": [1, 2, 3],
            "col2": [10, 20, 30]
        })
        
        def sum_cols(df):
            return df["col1"] + df["col2"]
        
        schema = {
            "derived_columns": {
                "col_sum": sum_cols
            },
            "target_columns": ["col1", "col2"]
        }
        
        transformer = DataTransformer(schema)
        df_transformed = transformer.transform(df)
        
        assert "col_sum" in df_transformed.columns
        assert df_transformed["col_sum"].iloc[0] == 11
