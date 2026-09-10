"""Unit tests for profitability tier classification."""

import pytest

from src.profitability_analytics.tiers import (
    TierThreshold,
    ProfitabilityTierEngine,
)


class TestTierThreshold:
    """Tests for TierThreshold dataclass."""
    
    def test_tier_threshold_creation(self):
        """Test creating tier threshold."""
        threshold = TierThreshold(
            name="gold",
            min_profit=50000,
            max_profit=100000,
            min_margin=15.0,
            description="High-value profitable customers"
        )
        
        assert threshold.name == "gold"
        assert threshold.min_profit == 50000
        assert threshold.max_profit == 100000
        assert threshold.min_margin == 15.0
    
    def test_to_dict(self):
        """Test serialization to dictionary."""
        threshold = TierThreshold(
            name="platinum",
            min_profit=100000,
            min_margin=25.0,
            description="Top-tier profitable customers"
        )
        
        data_dict = threshold.to_dict()
        
        assert data_dict["name"] == "platinum"
        assert data_dict["min_profit"] == 100000
        assert data_dict["min_margin"] == 25.0


class TestProfitabilityTierEngine:
    """Tests for ProfitabilityTierEngine."""
    
    def test_default_thresholds(self):
        """Test default tier thresholds are created."""
        engine = ProfitabilityTierEngine()
        
        thresholds = engine.get_all_tiers()
        
        assert len(thresholds) == 5
        tier_names = [t.name for t in thresholds]
        assert "platinum" in tier_names
        assert "gold" in tier_names
        assert "silver" in tier_names
        assert "bronze" in tier_names
        assert "unprofitable" in tier_names
    
    def test_classify_platinum(self):
        """Test platinum tier classification."""
        engine = ProfitabilityTierEngine()
        
        tier = engine.classify(net_profit=150000, profit_margin=30.0)
        
        assert tier == "platinum"
    
    def test_classify_gold(self):
        """Test gold tier classification."""
        engine = ProfitabilityTierEngine()
        
        tier = engine.classify(net_profit=75000, profit_margin=20.0)
        
        assert tier == "gold"
    
    def test_classify_silver(self):
        """Test silver tier classification."""
        engine = ProfitabilityTierEngine()
        
        tier = engine.classify(net_profit=25000, profit_margin=12.0)
        
        assert tier == "silver"
    
    def test_classify_bronze(self):
        """Test bronze tier classification."""
        engine = ProfitabilityTierEngine()
        
        tier = engine.classify(net_profit=5000, profit_margin=8.0)
        
        assert tier == "bronze"
    
    def test_classify_unprofitable(self):
        """Test unprofitable tier classification."""
        engine = ProfitabilityTierEngine()
        
        tier = engine.classify(net_profit=-1000, profit_margin=-5.0)
        
        assert tier == "unprofitable"
    
    def test_classify_without_margin(self):
        """Test classification without margin (profit-based only)."""
        engine = ProfitabilityTierEngine()
        
        tier = engine.classify(net_profit=150000, profit_margin=None)
        
        # Should still classify based on profit
        assert tier == "platinum"
    
    def test_classify_batch(self):
        """Test batch classification."""
        engine = ProfitabilityTierEngine()
        
        profits = [150000, 75000, 25000, 5000, -1000]
        margins = [30.0, 20.0, 12.0, 8.0, -5.0]
        
        tiers = engine.classify_batch(profits, margins)
        
        assert tiers == ["platinum", "gold", "silver", "bronze", "unprofitable"]
    
    def test_get_tier_definition(self):
        """Test getting tier definition."""
        engine = ProfitabilityTierEngine()
        
        tier_def = engine.get_tier_definition("platinum")
        
        assert tier_def is not None
        assert tier_def.name == "platinum"
        assert tier_def.min_profit == 100000
    
    def test_get_tier_definition_not_found(self):
        """Test getting non-existent tier."""
        engine = ProfitabilityTierEngine()
        
        tier_def = engine.get_tier_definition("nonexistent_tier")
        
        assert tier_def is None
    
    def test_update_thresholds(self):
        """Test updating tier thresholds."""
        engine = ProfitabilityTierEngine()
        
        new_thresholds = [
            TierThreshold(
                name="tier1",
                min_profit=0,
                description="Custom tier 1"
            )
        ]
        
        engine.update_thresholds(new_thresholds)
        
        thresholds = engine.get_all_tiers()
        assert len(thresholds) == 1
        assert thresholds[0].name == "tier1"
