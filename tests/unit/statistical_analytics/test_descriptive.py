"""Unit tests for descriptive statistics."""

import pytest
import pandas as pd
import numpy as np

from src.statistical_analytics.descriptive import DescriptiveStatistics


class TestDescriptiveStatistics:
    """Tests for DescriptiveStatistics."""
    
    def test_calculate_summary_statistics(self):
        """Test summary statistics calculation."""
        stats = DescriptiveStatistics()
        
        data = pd.Series([1, 2, 3, 4, 5])
        result = stats.calculate_summary_statistics(data, "test")
        
        assert result["mean"] == 3.0
        assert result["median"] == 3.0
        assert result["std"] > 0
        assert result["count"] == 5
    
    def test_test_normality(self):
        """Test normality test."""
        stats = DescriptiveStatistics()
        
        # Normal data
        normal_data = pd.Series(np.random.normal(0, 1, 100))
        result = stats.test_normality(normal_data, "normal")
        
        assert "p_value" in result
        assert "is_normal" in result
    
    def test_compare_distributions(self):
        """Test distribution comparison."""
        stats = DescriptiveStatistics()
        
        group1 = pd.Series([1, 2, 3, 4, 5])
        group2 = pd.Series([2, 3, 4, 5, 6])
        
        result = stats.compare_distributions(group1, group2, "Group 1", "Group 2")
        
        assert "group1" in result
        assert "group2" in result
        assert "difference" in result
