"""Unit tests for business-rule segmentation."""

import pytest
import pandas as pd

from src.customer_segmentation.business_rules import BusinessRuleSegmenter


class TestBusinessRuleSegmenter:
    """Tests for BusinessRuleSegmenter."""
    
    def test_initialization(self):
        """Test segmenter initialization."""
        segmenter = BusinessRuleSegmenter()
        
        assert len(segmenter.segment_registry) > 0
        assert "high_value" in segmenter.segment_registry
    
    def test_segment_by_profitability(self):
        """Test profitability-based segmentation."""
        segmenter = BusinessRuleSegmenter()
        
        df = pd.DataFrame({
            "customer_id": [1, 2, 3, 4],
            "net_profit": [60000, 30000, 5000, -1000],
            "profit_margin": [20, 12, 8, -5]
        })
        
        result = segmenter.segment_by_profitability(df)
        
        assert "segment" in result.columns
        assert result.loc[0, "segment"] == "high_value"
        assert result.loc[1, "segment"] == "medium_value"
        assert result.loc[2, "segment"] == "low_value"
        assert result.loc[3, "segment"] == "unprofitable"
    
    def test_segment_by_behavior(self):
        """Test behavior-based segmentation."""
        segmenter = BusinessRuleSegmenter()
        
        df = pd.DataFrame({
            "customer_id": [1, 2, 3],
            "transaction_frequency": [15, 7, 3],
            "product_count": [4, 2, 1]
        })
        
        result = segmenter.segment_by_behavior(df)
        
        assert "behavior_segment" in result.columns
        assert result.loc[0, "behavior_segment"] == "highly_engaged"
        assert result.loc[1, "behavior_segment"] == "moderately_engaged"
        assert result.loc[2, "behavior_segment"] == "lowly_engaged"
    
    def test_segment_by_lifecycle(self):
        """Test lifecycle-based segmentation."""
        segmenter = BusinessRuleSegmenter()
        
        df = pd.DataFrame({
            "customer_id": [1, 2, 3],
            "tenure_days": [30, 180, 400]
        })
        
        result = segmenter.segment_by_lifecycle(df)
        
        assert "lifecycle_segment" in result.columns
        assert result.loc[0, "lifecycle_segment"] == "new_customer"
        assert result.loc[1, "lifecycle_segment"] == "established_customer"
        assert result.loc[2, "lifecycle_segment"] == "long_term_customer"
