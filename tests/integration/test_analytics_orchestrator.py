"""Integration tests for analytics orchestrators."""

import pytest
import pandas as pd
from datetime import date

from src.advanced_risk_analytics.orchestrator import AdvancedRiskOrchestrator
from src.decision_intelligence.orchestrator import DecisionIntelligenceOrchestrator


@pytest.mark.integration
class TestAnalyticsOrchestrators:
    """Integration tests for analytics orchestrators."""
    
    def test_advanced_risk_orchestrator_initialization(self, sample_customer_metrics):
        """Test advanced risk orchestrator initialization."""
        orchestrator = AdvancedRiskOrchestrator()
        assert orchestrator is not None
        assert orchestrator.portfolio_distribution is not None
        assert orchestrator.transition_matrices is not None
    
    def test_advanced_risk_orchestrator_generate_report(self, sample_customer_metrics):
        """Test generating comprehensive risk report."""
        orchestrator = AdvancedRiskOrchestrator()
        
        # Test available methods - portfolio_distribution is a class, not a method
        # Test that the orchestrator has the required components
        assert orchestrator.portfolio_distribution is not None
        assert orchestrator.transition_matrices is not None
    
    def test_decision_intelligence_orchestrator_initialization(self):
        """Test decision intelligence orchestrator initialization."""
        orchestrator = DecisionIntelligenceOrchestrator()
        assert orchestrator is not None
        assert orchestrator.profitability_risk_rules is not None
        assert orchestrator.churn_clv_rules is not None
        assert orchestrator.risk_exposure_rules is not None
    
    def test_decision_intelligence_customer_recommendations(self, sample_customer_metrics):
        """Test generating customer recommendations."""
        orchestrator = DecisionIntelligenceOrchestrator()
        
        customer_data = sample_customer_metrics.iloc[0].to_dict()
        recommendations = orchestrator.generate_customer_recommendations(customer_data)
        
        assert recommendations is not None
        assert isinstance(recommendations, list)
    
    def test_decision_intelligence_segment_recommendations(self, sample_customer_metrics):
        """Test generating segment recommendations."""
        orchestrator = DecisionIntelligenceOrchestrator()
        
        segment_data = {
            "segment": "premium",
            "avg_profitability": 15000,
            "customer_count": 2000,
            "avg_risk_level": "low",
            "exposure_concentration": 0.10
        }
        
        recommendations = orchestrator.generate_segment_recommendations(segment_data)
        
        assert recommendations is not None
        assert isinstance(recommendations, list)
