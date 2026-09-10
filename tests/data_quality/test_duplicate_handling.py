"""Data quality tests for duplicate handling."""

import pytest
import pandas as pd


@pytest.mark.data_quality
class TestDuplicateHandling:
    """Tests for duplicate handling."""
    
    def test_duplicate_detection(self, sample_duplicate_data):
        """Test detection of duplicate rows."""
        df = sample_duplicate_data
        
        # Count duplicates
        duplicate_count = df.duplicated().sum()
        assert duplicate_count == 2
    
    def test_duplicate_removal(self, sample_duplicate_data):
        """Test removal of duplicate rows."""
        df = sample_duplicate_data
        
        # Remove duplicates
        deduped_df = df.drop_duplicates()
        assert len(deduped_df) == 3
    
    def test_duplicate_removal_subset(self, sample_duplicate_data):
        """Test removal of duplicates based on subset of columns."""
        df = sample_duplicate_data
        
        # Remove duplicates based on customer_key only
        deduped_df = df.drop_duplicates(subset=["customer_key"])
        assert len(deduped_df) == 3
    
    def test_duplicate_keep_first(self, sample_duplicate_data):
        """Test keeping first occurrence of duplicates."""
        df = sample_duplicate_data
        
        # Keep first occurrence
        deduped_df = df.drop_duplicates(keep="first")
        assert len(deduped_df) == 3
        assert deduped_df.iloc[0]["customer_key"] == "CUST_001"
    
    def test_duplicate_keep_last(self, sample_duplicate_data):
        """Test keeping last occurrence of duplicates."""
        df = sample_duplicate_data
        
        # Keep last occurrence
        deduped_df = df.drop_duplicates(keep="last")
        assert len(deduped_df) == 3
