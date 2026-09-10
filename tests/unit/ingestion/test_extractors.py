"""Unit tests for data extractors."""

import pytest
from datetime import datetime
import pandas as pd
from pathlib import Path

from src.ingestion.extractors import CSVExtractor, ParquetExtractor, ExtractorFactory
from src.ingestion.base import SourceValidationError


class TestCSVExtractor:
    """Tests for CSVExtractor."""
    
    def test_extract_csv(self, tmp_path):
        """Test CSV extraction."""
        # Create test CSV file
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("col1,col2,col3\n1,2,3\n4,5,6\n")
        
        config = {
            "name": "test",
            "type": "csv",
            "path": str(csv_file),
            "delimiter": ",",
            "encoding": "utf-8",
            "has_header": True
        }
        
        extractor = CSVExtractor(config)
        df = extractor.extract()
        
        assert len(df) == 2
        assert list(df.columns) == ["col1", "col2", "col3"]
        assert extractor.metadata is not None
        assert extractor.metadata.row_count == 2
        assert extractor.metadata.column_count == 3
    
    def test_extract_csv_with_custom_delimiter(self, tmp_path):
        """Test CSV extraction with custom delimiter."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("col1;col2;col3\n1;2;3\n4;5;6\n")
        
        config = {
            "name": "test",
            "type": "csv",
            "path": str(csv_file),
            "delimiter": ";",
            "encoding": "utf-8",
            "has_header": True
        }
        
        extractor = CSVExtractor(config)
        df = extractor.extract()
        
        assert len(df) == 2
        assert list(df.columns) == ["col1", "col2", "col3"]
    
    def test_extract_csv_invalid_source(self):
        """Test CSV extraction with invalid source."""
        config = {
            "name": "test",
            "type": "csv",
            "path": "/nonexistent/file.csv"
        }
        
        extractor = CSVExtractor(config)
        
        with pytest.raises(SourceValidationError):
            extractor.extract()


class TestParquetExtractor:
    """Tests for ParquetExtractor."""
    
    def test_extract_parquet(self, tmp_path):
        """Test Parquet extraction."""
        # Create test DataFrame and save as Parquet
        df = pd.DataFrame({
            "col1": [1, 2, 3],
            "col2": ["a", "b", "c"],
            "col3": [1.1, 2.2, 3.3]
        })
        
        parquet_file = tmp_path / "test.parquet"
        df.to_parquet(parquet_file, engine="pyarrow")
        
        config = {
            "name": "test",
            "type": "parquet",
            "path": str(parquet_file),
            "engine": "pyarrow"
        }
        
        extractor = ParquetExtractor(config)
        df_extracted = extractor.extract()
        
        assert len(df_extracted) == 3
        assert extractor.metadata is not None
        assert extractor.metadata.row_count == 3
    
    def test_extract_parquet_invalid_source(self):
        """Test Parquet extraction with invalid source."""
        config = {
            "name": "test",
            "type": "parquet",
            "path": "/nonexistent/file.parquet"
        }
        
        extractor = ParquetExtractor(config)
        
        with pytest.raises(SourceValidationError):
            extractor.extract()


class TestExtractorFactory:
    """Tests for ExtractorFactory."""
    
    def test_create_csv_extractor(self):
        """Test creating CSV extractor via factory."""
        config = {"type": "csv", "path": "/path/to/file.csv"}
        extractor = ExtractorFactory.create_extractor(config)
        
        assert isinstance(extractor, CSVExtractor)
    
    def test_create_parquet_extractor(self):
        """Test creating Parquet extractor via factory."""
        config = {"type": "parquet", "path": "/path/to/file.parquet"}
        extractor = ExtractorFactory.create_extractor(config)
        
        assert isinstance(extractor, ParquetExtractor)
    
    def test_create_unsupported_extractor(self):
        """Test creating unsupported extractor type."""
        config = {"type": "json", "path": "/path/to/file.json"}
        
        with pytest.raises(ValueError, match="Unsupported source type"):
            ExtractorFactory.create_extractor(config)
