"""Base classes for data ingestion framework."""

import hashlib
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, List
import logging

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class IngestionMetadata:
    """Metadata for ingestion operations."""
    
    # Source information
    source_name: str
    source_type: str
    source_path: str
    
    # Ingestion timing
    ingestion_timestamp: datetime
    ingestion_id: str
    
    # Data statistics
    row_count: int
    column_count: int
    file_size_bytes: Optional[int] = None
    
    # Data quality
    null_count: int = 0
    duplicate_count: int = 0
    error_count: int = 0
    
    # Schema information
    schema_hash: Optional[str] = None
    data_hash: Optional[str] = None
    
    # Status
    status: str = "success"  # success, partial_success, failed
    error_message: Optional[str] = None
    
    # Target information
    target_path: Optional[str] = None
    target_table: Optional[str] = None
    
    # Additional metadata
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize metadata dict if not provided."""
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        data = asdict(self)
        # Convert datetime to ISO format
        data["ingestion_timestamp"] = self.ingestion_timestamp.isoformat()
        return data
    
    def to_json(self) -> str:
        """Convert metadata to JSON string."""
        return json.dumps(self.to_dict(), indent=2, default=str)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IngestionMetadata":
        """Create metadata from dictionary."""
        # Convert ISO string back to datetime
        if isinstance(data.get("ingestion_timestamp"), str):
            data["ingestion_timestamp"] = datetime.fromisoformat(data["ingestion_timestamp"])
        return cls(**data)
    
    @staticmethod
    def generate_ingestion_id() -> str:
        """Generate unique ingestion ID."""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        random_hash = hashlib.md5(str(datetime.utcnow().timestamp()).encode()).hexdigest()[:8]
        return f"ing_{timestamp}_{random_hash}"
    
    @staticmethod
    def compute_schema_hash(df: pd.DataFrame) -> str:
        """Compute hash of DataFrame schema."""
        schema_info = {
            "columns": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
        return hashlib.md5(json.dumps(schema_info, sort_keys=True).encode()).hexdigest()
    
    @staticmethod
    def compute_data_hash(df: pd.DataFrame) -> str:
        """Compute hash of DataFrame content."""
        # Use a sample for large datasets to avoid memory issues
        sample_size = min(1000, len(df))
        sample = df.sample(sample_size) if len(df) > sample_size else df
        return hashlib.md5(pd.util.hash_pandas_object(sample).values.tobytes()).hexdigest()


class BaseExtractor(ABC):
    """Base class for data extractors."""
    
    def __init__(self, source_config: Dict[str, Any]):
        """Initialize extractor.
        
        Args:
            source_config: Configuration dictionary for the source
        """
        self.source_config = source_config
        self.source_name = source_config.get("name", "unknown")
        self.source_type = source_config.get("type", "unknown")
        self.source_path = source_config.get("path", "")
        self.metadata: Optional[IngestionMetadata] = None
    
    @abstractmethod
    def extract(self) -> pd.DataFrame:
        """Extract data from source.
        
        Returns:
            DataFrame containing extracted data
        """
        pass
    
    def get_file_size(self) -> Optional[int]:
        """Get source file size in bytes."""
        try:
            path = Path(self.source_path)
            if path.exists():
                return path.stat().st_size
        except Exception as e:
            logger.warning(f"Could not get file size: {e}")
        return None
    
    def validate_source(self) -> bool:
        """Validate that source exists and is accessible.
        
        Returns:
            True if source is valid, False otherwise
        """
        path = Path(self.source_path)
        return path.exists() and path.is_file()


class BaseLoader(ABC):
    """Base class for data loaders."""
    
    def __init__(self, storage_config: Dict[str, Any]):
        """Initialize loader.
        
        Args:
            storage_config: Configuration dictionary for storage
        """
        self.storage_config = storage_config
        self.storage_path = storage_config.get("path", "")
        self.compress = storage_config.get("compress", False)
        self.compression_type = storage_config.get("compression_type", "gzip")
    
    @abstractmethod
    def load(self, df: pd.DataFrame, metadata: IngestionMetadata) -> str:
        """Load data to storage.
        
        Args:
            df: DataFrame to load
            metadata: Ingestion metadata
        
        Returns:
            Path where data was loaded
        """
        pass
    
    def ensure_directory(self, path: Path) -> None:
        """Ensure directory exists."""
        path.parent.mkdir(parents=True, exist_ok=True)
    
    def get_output_path(self, source_name: str, timestamp: datetime) -> Path:
        """Generate output path for loaded data.
        
        Args:
            source_name: Name of the data source
            timestamp: Ingestion timestamp
        
        Returns:
            Path object for output file
        """
        base_path = Path(self.storage_path)
        date_str = timestamp.strftime("%Y/%m/%d")
        time_str = timestamp.strftime("%H%M%S")
        
        # Create path: base_path/source_name/YYYY/MM/DD/source_name_HHMMSS.extension
        filename = f"{source_name}_{time_str}"
        
        if self.compress and self.compression_type == "gzip":
            filename += ".csv.gz"
        else:
            filename += ".csv"
        
        return base_path / source_name / date_str / filename


class IngestionError(Exception):
    """Base exception for ingestion errors."""
    pass


class SourceValidationError(IngestionError):
    """Exception raised when source validation fails."""
    pass


class DataQualityError(IngestionError):
    """Exception raised when data quality checks fail."""
    pass


class LoadError(IngestionError):
    """Exception raised when loading fails."""
    pass
