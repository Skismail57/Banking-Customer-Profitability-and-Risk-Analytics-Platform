"""Data ingestion package for banking analytics platform."""

from src.ingestion.base import BaseExtractor, BaseLoader, IngestionMetadata
from src.ingestion.extractors import CSVExtractor, ParquetExtractor
from src.ingestion.loaders import RawLoader, StagingLoader, WarehouseLoader
from src.ingestion.cleaners import DataCleaner
from src.ingestion.orchestrator import IngestionOrchestrator

__all__ = [
    "BaseExtractor",
    "BaseLoader",
    "IngestionMetadata",
    "CSVExtractor",
    "ParquetExtractor",
    "RawLoader",
    "StagingLoader",
    "WarehouseLoader",
    "DataCleaner",
    "IngestionOrchestrator",
]
