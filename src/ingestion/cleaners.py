"""Data cleaning and transformation utilities."""

from typing import Dict, Any, List, Optional, Callable
import logging

import pandas as pd
import numpy as np

from src.ingestion.schema import DataQualityChecker

logger = logging.getLogger(__name__)


class DataCleaner:
    """Clean and transform data according to configuration."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize data cleaner.
        
        Args:
            config: Configuration dictionary with:
                - handle_duplicates: Whether to handle duplicates
                - duplicate_strategy: Strategy for duplicates (keep_first, keep_last, drop_all)
                - trim_strings: Whether to trim string whitespace
                - standardize_dates: Whether to standardize date formats
                - fill_numeric: Value to fill numeric nulls
                - fill_string: Value to fill string nulls
        """
        self.config = config
    
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply cleaning operations to DataFrame.
        
        Args:
            df: DataFrame to clean
        
        Returns:
            Cleaned DataFrame
        """
        logger.info(f"Cleaning DataFrame with {len(df)} rows")
        
        df_cleaned = df.copy()
        
        # Handle duplicates
        if self.config.get("handle_duplicates", True):
            df_cleaned = self._handle_duplicates(df_cleaned)
        
        # Trim strings
        if self.config.get("trim_strings", True):
            df_cleaned = self._trim_strings(df_cleaned)
        
        # Standardize dates
        if self.config.get("standardize_dates", False):
            df_cleaned = self._standardize_dates(df_cleaned)
        
        # Fill null values
        df_cleaned = self._fill_nulls(df_cleaned)
        
        # Remove empty rows
        df_cleaned = self._remove_empty_rows(df_cleaned)
        
        logger.info(f"Cleaning complete. Rows: {len(df)} -> {len(df_cleaned)}")
        
        return df_cleaned
    
    def _handle_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle duplicate rows based on strategy.
        
        Args:
            df: DataFrame to process
        
        Returns:
            DataFrame with duplicates handled
        """
        strategy = self.config.get("duplicate_strategy", "keep_first")
        duplicate_count = df.duplicated().sum()
        
        if duplicate_count == 0:
            return df
        
        logger.info(f"Found {duplicate_count} duplicate rows, using strategy: {strategy}")
        
        if strategy == "keep_first":
            return df.drop_duplicates(keep="first")
        elif strategy == "keep_last":
            return df.drop_duplicates(keep="last")
        elif strategy == "drop_all":
            return df[~df.duplicated(keep=False)]
        else:
            logger.warning(f"Unknown duplicate strategy: {strategy}, keeping first")
            return df.drop_duplicates(keep="first")
    
    def _trim_strings(self, df: pd.DataFrame) -> pd.DataFrame:
        """Trim whitespace from string columns.
        
        Args:
            df: DataFrame to process
        
        Returns:
            DataFrame with trimmed strings
        """
        string_columns = df.select_dtypes(include=["object", "string"]).columns
        
        for column in string_columns:
            df[column] = df[column].astype(str).str.strip()
        
        return df
    
    def _standardize_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize date columns to datetime format.
        
        Args:
            df: DataFrame to process
        
        Returns:
            DataFrame with standardized dates
        """
        # Try to convert object columns that look like dates
        for column in df.select_dtypes(include=["object"]).columns:
            # Heuristic: if column name contains 'date' or 'time'
            if "date" in column.lower() or "time" in column.lower():
                try:
                    df[column] = pd.to_datetime(df[column], errors="coerce")
                    logger.info(f"Converted column '{column}' to datetime")
                except Exception as e:
                    logger.warning(f"Could not convert column '{column}' to datetime: {e}")
        
        return df
    
    def _fill_nulls(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fill null values based on column type.
        
        Args:
            df: DataFrame to process
        
        Returns:
            DataFrame with nulls filled
        """
        fill_numeric = self.config.get("fill_numeric")
        fill_string = self.config.get("fill_string")
        
        # Fill numeric columns
        if fill_numeric is not None:
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            df[numeric_columns] = df[numeric_columns].fillna(fill_numeric)
        
        # Fill string columns
        if fill_string is not None:
            string_columns = df.select_dtypes(include=["object", "string"]).columns
            df[string_columns] = df[string_columns].fillna(fill_string)
        
        return df
    
    def _remove_empty_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove rows where all values are null.
        
        Args:
            df: DataFrame to process
        
        Returns:
            DataFrame with empty rows removed
        """
        before_count = len(df)
        df = df.dropna(how="all")
        after_count = len(df)
        
        if before_count != after_count:
            logger.info(f"Removed {before_count - after_count} empty rows")
        
        return df


class DataTransformer:
    """Transform data to match target schema."""
    
    def __init__(self, target_schema: Dict[str, Any]):
        """Initialize transformer.
        
        Args:
            target_schema: Target schema with:
                - column_mappings: Dict mapping source columns to target columns
                - column_types: Dict mapping target columns to desired types
                - derived_columns: Dict of column names and transformation functions
        """
        self.target_schema = target_schema
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform DataFrame to match target schema.
        
        Args:
            df: DataFrame to transform
        
        Returns:
            Transformed DataFrame
        """
        logger.info(f"Transforming DataFrame to target schema")
        
        df_transformed = df.copy()
        
        # Rename columns
        df_transformed = self._rename_columns(df_transformed)
        
        # Select only target columns
        df_transformed = self._select_columns(df_transformed)
        
        # Convert column types
        df_transformed = self._convert_types(df_transformed)
        
        # Add derived columns
        df_transformed = self._add_derived_columns(df_transformed)
        
        logger.info(f"Transformation complete. Columns: {len(df.columns)} -> {len(df_transformed.columns)}")
        
        return df_transformed
    
    def _rename_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Rename columns according to mapping.
        
        Args:
            df: DataFrame to process
        
        Returns:
            DataFrame with renamed columns
        """
        column_mappings = self.target_schema.get("column_mappings", {})
        
        if column_mappings:
            df = df.rename(columns=column_mappings)
            logger.info(f"Renamed {len(column_mappings)} columns")
        
        return df
    
    def _select_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Select only columns in target schema.
        
        Args:
            df: DataFrame to process
        
        Returns:
            DataFrame with selected columns
        """
        target_columns = self.target_schema.get("target_columns", [])
        
        if target_columns:
            # Keep only columns that exist in DataFrame
            existing_columns = [col for col in target_columns if col in df.columns]
            missing_columns = set(target_columns) - set(existing_columns)
            
            if missing_columns:
                logger.warning(f"Missing target columns: {missing_columns}")
            
            df = df[existing_columns]
        
        return df
    
    def _convert_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert column types according to schema.
        
        Args:
            df: DataFrame to process
        
        Returns:
            DataFrame with converted types
        """
        column_types = self.target_schema.get("column_types", {})
        
        for column, target_type in column_types.items():
            if column in df.columns:
                try:
                    if target_type == "int":
                        df[column] = pd.to_numeric(df[column], errors="coerce").astype("Int64")
                    elif target_type == "float":
                        df[column] = pd.to_numeric(df[column], errors="coerce")
                    elif target_type == "string":
                        df[column] = df[column].astype(str)
                    elif target_type == "datetime":
                        df[column] = pd.to_datetime(df[column], errors="coerce")
                    elif target_type == "bool":
                        df[column] = df[column].astype(bool)
                    
                    logger.info(f"Converted column '{column}' to {target_type}")
                    
                except Exception as e:
                    logger.warning(f"Could not convert column '{column}' to {target_type}: {e}")
        
        return df
    
    def _add_derived_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add derived columns using transformation functions.
        
        Args:
            df: DataFrame to process
        
        Returns:
            DataFrame with derived columns
        """
        derived_columns = self.target_schema.get("derived_columns", {})
        
        for column, func in derived_columns.items():
            try:
                if callable(func):
                    df[column] = func(df)
                    logger.info(f"Added derived column '{column}'")
            except Exception as e:
                logger.warning(f"Could not add derived column '{column}': {e}")
        
        return df
