"""Data extractors for different file formats."""

from datetime import datetime
from typing import Dict, Any, Optional
import logging

import pandas as pd

from src.ingestion.base import BaseExtractor, IngestionMetadata, SourceValidationError

logger = logging.getLogger(__name__)


class CSVExtractor(BaseExtractor):
    """Extractor for CSV files."""
    
    def __init__(self, source_config: Dict[str, Any]):
        """Initialize CSV extractor.
        
        Args:
            source_config: Configuration dictionary with keys:
                - path: Path to CSV file
                - delimiter: CSV delimiter (default: ,)
                - encoding: File encoding (default: utf-8)
                - has_header: Whether file has header (default: True)
                - name: Source name (for metadata)
        """
        super().__init__(source_config)
        self.delimiter = source_config.get("delimiter", ",")
        self.encoding = source_config.get("encoding", "utf-8")
        self.has_header = source_config.get("has_header", True)
    
    def extract(self) -> pd.DataFrame:
        """Extract data from CSV file.
        
        Returns:
            DataFrame containing extracted data
        
        Raises:
            SourceValidationError: If source file is invalid
        """
        logger.info(f"Extracting data from CSV: {self.source_path}")
        
        # Validate source
        if not self.validate_source():
            raise SourceValidationError(f"Source file not found or invalid: {self.source_path}")
        
        try:
            # Read CSV file
            df = pd.read_csv(
                self.source_path,
                delimiter=self.delimiter,
                encoding=self.encoding,
                header=0 if self.has_header else None,
                low_memory=False
            )
            
            logger.info(f"Successfully extracted {len(df)} rows, {len(df.columns)} columns")
            
            # Create metadata
            self.metadata = IngestionMetadata(
                source_name=self.source_name,
                source_type=self.source_type,
                source_path=self.source_path,
                ingestion_timestamp=datetime.utcnow(),
                ingestion_id=IngestionMetadata.generate_ingestion_id(),
                row_count=len(df),
                column_count=len(df.columns),
                file_size_bytes=self.get_file_size(),
                schema_hash=IngestionMetadata.compute_schema_hash(df),
                data_hash=IngestionMetadata.compute_data_hash(df),
                null_count=df.isnull().sum().sum(),
                duplicate_count=df.duplicated().sum()
            )
            
            return df
            
        except Exception as e:
            logger.error(f"Error extracting CSV: {e}")
            raise


class ParquetExtractor(BaseExtractor):
    """Extractor for Parquet files."""
    
    def __init__(self, source_config: Dict[str, Any]):
        """Initialize Parquet extractor.
        
        Args:
            source_config: Configuration dictionary with keys:
                - path: Path to Parquet file
                - name: Source name (for metadata)
        """
        super().__init__(source_config)
        self.engine = source_config.get("engine", "pyarrow")
    
    def extract(self) -> pd.DataFrame:
        """Extract data from Parquet file.
        
        Returns:
            DataFrame containing extracted data
        
        Raises:
            SourceValidationError: If source file is invalid
        """
        logger.info(f"Extracting data from Parquet: {self.source_path}")
        
        # Validate source
        if not self.validate_source():
            raise SourceValidationError(f"Source file not found or invalid: {self.source_path}")
        
        try:
            # Read Parquet file
            df = pd.read_parquet(self.source_path, engine=self.engine)
            
            logger.info(f"Successfully extracted {len(df)} rows, {len(df.columns)} columns")
            
            # Create metadata
            self.metadata = IngestionMetadata(
                source_name=self.source_name,
                source_type=self.source_type,
                source_path=self.source_path,
                ingestion_timestamp=datetime.utcnow(),
                ingestion_id=IngestionMetadata.generate_ingestion_id(),
                row_count=len(df),
                column_count=len(df.columns),
                file_size_bytes=self.get_file_size(),
                schema_hash=IngestionMetadata.compute_schema_hash(df),
                data_hash=IngestionMetadata.compute_data_hash(df),
                null_count=df.isnull().sum().sum(),
                duplicate_count=df.duplicated().sum()
            )
            
            return df
            
        except Exception as e:
            logger.error(f"Error extracting Parquet: {e}")
            raise


class ExtractorFactory:
    """Factory for creating extractors based on source type."""
    
    @staticmethod
    def create_extractor(source_config: Dict[str, Any]) -> BaseExtractor:
        """Create appropriate extractor based on source type.
        
        Args:
            source_config: Configuration dictionary
        
        Returns:
            BaseExtractor instance
        
        Raises:
            ValueError: If source type is not supported
        """
        source_type = source_config.get("type", "").lower()
        
        extractors = {
            "csv": CSVExtractor,
            "parquet": ParquetExtractor,
        }
        
        extractor_class = extractors.get(source_type)
        
        if extractor_class is None:
            raise ValueError(f"Unsupported source type: {source_type}. Supported types: {list(extractors.keys())}")
        
        return extractor_class(source_config)
