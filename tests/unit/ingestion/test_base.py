"""Unit tests for ingestion base classes."""

import pytest
from datetime import datetime, timezone
import pandas as pd

from src.ingestion.base import IngestionMetadata, BaseExtractor, BaseLoader


class TestIngestionMetadata:
    """Tests for IngestionMetadata dataclass."""
    
    def test_metadata_creation(self):
        """Test creating metadata with required fields."""
        metadata = IngestionMetadata(
            source_name="test_source",
            source_type="csv",
            source_path="/path/to/file.csv",
            ingestion_timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
            ingestion_id="test_id",
            row_count=100,
            column_count=10
        )
        
        assert metadata.source_name == "test_source"
        assert metadata.row_count == 100
        assert metadata.column_count == 10
        assert metadata.status == "success"
    
    def test_generate_ingestion_id(self):
        """Test ingestion ID generation."""
        id1 = IngestionMetadata.generate_ingestion_id()
        id2 = IngestionMetadata.generate_ingestion_id()
        
        assert id1 != id2
        assert id1.startswith("ing_")
    
    def test_compute_schema_hash(self):
        """Test schema hash computation."""
        df1 = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
        df2 = pd.DataFrame({"col1": [3, 4], "col2": ["c", "d"]})
        df3 = pd.DataFrame({"col1": [1, 2], "col3": ["a", "b"]})
        
        hash1 = IngestionMetadata.compute_schema_hash(df1)
        hash2 = IngestionMetadata.compute_schema_hash(df2)
        hash3 = IngestionMetadata.compute_schema_hash(df3)
        
        # Same schema should produce same hash
        assert hash1 == hash2
        # Different schema should produce different hash
        assert hash1 != hash3
    
    def test_to_dict_and_from_dict(self):
        """Test metadata serialization and deserialization."""
        original = IngestionMetadata(
            source_name="test",
            source_type="csv",
            source_path="/path",
            ingestion_timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
            ingestion_id="id123",
            row_count=50,
            column_count=5
        )
        
        data_dict = original.to_dict()
        restored = IngestionMetadata.from_dict(data_dict)
        
        assert restored.source_name == original.source_name
        assert restored.row_count == original.row_count
        assert restored.ingestion_id == original.ingestion_id


class TestBaseExtractor:
    """Tests for BaseExtractor class."""
    
    def test_get_file_size(self, tmp_path):
        """Test file size retrieval."""
        # Create test file
        test_file = tmp_path / "test.csv"
        test_file.write_text("col1,col2\n1,2\n3,4")
        
        config = {"name": "test", "type": "csv", "path": str(test_file)}
        extractor = BaseExtractor(config)
        
        size = extractor.get_file_size()
        assert size is not None
        assert size > 0
    
    def test_validate_source_valid(self, tmp_path):
        """Test source validation with valid file."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("data")
        
        config = {"name": "test", "type": "csv", "path": str(test_file)}
        extractor = BaseExtractor(config)
        
        assert extractor.validate_source() is True
    
    def test_validate_source_invalid(self):
        """Test source validation with invalid file."""
        config = {"name": "test", "type": "csv", "path": "/nonexistent/file.csv"}
        extractor = BaseExtractor(config)
        
        assert extractor.validate_source() is False


class TestBaseLoader:
    """Tests for BaseLoader class."""
    
    def test_get_output_path(self, tmp_path):
        """Test output path generation."""
        config = {"path": str(tmp_path), "compress": False}
        loader = BaseLoader(config)
        
        timestamp = datetime(2024, 1, 15, 10, 30, 45)
        path = loader.get_output_path("customers", timestamp)
        
        assert "customers" in str(path)
        assert "2024/01/15" in str(path)
        assert "103045" in str(path)
    
    def test_ensure_directory(self, tmp_path):
        """Test directory creation."""
        config = {"path": str(tmp_path)}
        loader = BaseLoader(config)
        
        nested_path = tmp_path / "a" / "b" / "c" / "file.csv"
        loader.ensure_directory(nested_path)
        
        assert nested_path.parent.exists()
