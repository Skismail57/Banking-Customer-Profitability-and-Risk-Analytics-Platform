"""Data loaders for different storage stages."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import logging

import pandas as pd

from src.ingestion.base import BaseLoader, IngestionMetadata, LoadError

logger = logging.getLogger(__name__)


class RawLoader(BaseLoader):
    """Loader for raw data storage (immutable)."""
    
    def __init__(self, storage_config: Dict[str, Any]):
        """Initialize raw loader.
        
        Args:
            storage_config: Configuration dictionary with:
                - path: Base storage path
                - compress: Whether to compress output
                - compression_type: Compression type (gzip, etc.)
        """
        super().__init__(storage_config)
        self.metadata_path = Path(storage_config.get("metadata_path", "data/metadata"))
    
    def load(self, df: pd.DataFrame, metadata: IngestionMetadata) -> str:
        """Load data to raw storage with metadata.
        
        Args:
            df: DataFrame to load
            metadata: Ingestion metadata
        
        Returns:
            Path where data was loaded
        
        Raises:
            LoadError: If loading fails
        """
        try:
            logger.info(f"Loading data to raw storage: {self.source_name}")
            
            # Generate output path
            output_path = self.get_output_path(metadata.source_name, metadata.ingestion_timestamp)
            self.ensure_directory(output_path)
            
            # Save data
            if self.compress and self.compression_type == "gzip":
                df.to_csv(output_path, index=False, compression="gzip")
            else:
                df.to_csv(output_path, index=False)
            
            logger.info(f"Data saved to: {output_path}")
            
            # Save metadata
            metadata.target_path = str(output_path)
            metadata_path = self._save_metadata(metadata, output_path)
            
            logger.info(f"Metadata saved to: {metadata_path}")
            
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error loading to raw storage: {e}")
            raise LoadError(f"Failed to load data to raw storage: {e}")
    
    def _save_metadata(self, metadata: IngestionMetadata, data_path: Path) -> Path:
        """Save metadata alongside data.
        
        Args:
            metadata: Ingestion metadata
            data_path: Path where data was saved
        
        Returns:
            Path where metadata was saved
        """
        metadata_filename = data_path.stem + "_metadata.json"
        metadata_path = data_path.parent / metadata_filename
        
        with open(metadata_path, "w") as f:
            f.write(metadata.to_json())
        
        return metadata_path


class StagingLoader(BaseLoader):
    """Loader for staging data storage (validated and cleaned)."""
    
    def __init__(self, storage_config: Dict[str, Any]):
        """Initialize staging loader.
        
        Args:
            storage_config: Configuration dictionary
        """
        super().__init__(storage_config)
    
    def load(self, df: pd.DataFrame, metadata: IngestionMetadata) -> str:
        """Load data to staging storage.
        
        Args:
            df: DataFrame to load
            metadata: Ingestion metadata
        
        Returns:
            Path where data was loaded
        """
        try:
            logger.info(f"Loading data to staging storage: {metadata.source_name}")
            
            # Generate output path
            output_path = self.get_output_path(metadata.source_name, metadata.ingestion_timestamp)
            self.ensure_directory(output_path)
            
            # Save data (always compress for staging)
            df.to_parquet(output_path.with_suffix(".parquet"), index=True)
            
            logger.info(f"Data saved to: {output_path.with_suffix('.parquet')}")
            
            # Update metadata
            metadata.target_path = str(output_path.with_suffix(".parquet"))
            
            return str(output_path.with_suffix(".parquet"))
            
        except Exception as e:
            logger.error(f"Error loading to staging storage: {e}")
            raise LoadError(f"Failed to load data to staging storage: {e}")


class WarehouseLoader(BaseLoader):
    """Loader for warehouse storage (database)."""
    
    def __init__(self, storage_config: Dict[str, Any], db_manager):
        """Initialize warehouse loader.
        
        Args:
            storage_config: Configuration dictionary
            db_manager: Database manager instance
        """
        super().__init__(storage_config)
        self.db_manager = db_manager
    
    def load(self, df: pd.DataFrame, metadata: IngestionMetadata) -> str:
        """Load data to warehouse database.
        
        Args:
            df: DataFrame to load
            metadata: Ingestion metadata with target_table
        
        Returns:
            Table name where data was loaded
        """
        try:
            logger.info(f"Loading data to warehouse table: {metadata.target_table}")
            
            if not metadata.target_table:
                raise LoadError("Target table not specified in metadata")
            
            # Get database session
            session = self.db_manager.get_session()
            
            try:
                # Load data to database
                df.to_sql(
                    metadata.target_table,
                    self.db_manager.get_engine(),
                    if_exists="append",
                    index=False,
                    chunksize=10000
                )
                
                logger.info(f"Loaded {len(df)} rows to table: {metadata.target_table}")
                
                session.commit()
                
                return metadata.target_table
                
            except Exception as e:
                session.rollback()
                raise
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"Error loading to warehouse: {e}")
            raise LoadError(f"Failed to load data to warehouse: {e}")
