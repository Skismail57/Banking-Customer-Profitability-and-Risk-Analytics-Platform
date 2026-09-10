"""Unit tests for decision intelligence rules engine."""

import pytest
from src.decision_intelligence.rules_engine import RulesEngine
from src.decision_intelligence.base import Recommendation, Priority, ConfidenceLevel
from datetime import date


@pytest.mark.unit
class TestRulesEngine:
    """Tests for RulesEngine class."""
    
    def test_rules_engine_initialization(self):
        """Test rules engine initialization."""
        engine = RulesEngine()
        assert engine is not None
        assert len(engine.rules) == 0
    
    def test_register_rule(self):
        """Test registering a rule."""
        engine = RulesEngine()
        
        def condition(data):
            return data.get("net_profit", 0) > 5000
        
        def action(data):
            return {
                "triggering_metrics": {"net_profit": data.get("net_profit")},
                "reason": "High profitability",
                "recommended_action": "Offer premium product",
                "priority": Priority.HIGH,
                "confidence": ConfidenceLevel.HIGH,
                "limitations": ["Based on current snapshot"]
            }
        
        engine.register_rule("high_profit_rule", condition, action)
        assert len(engine.rules) == 1
        assert engine.rules[0]["name"] == "high_profit_rule"
    
    def test_evaluate_rules_matching_condition(self):
        """Test evaluating rules with matching condition."""
        engine = RulesEngine()
        
        def condition(data):
            return data.get("net_profit", 0) > 5000
        
        def action(data):
            return {
                "triggering_metrics": {"net_profit": data.get("net_profit")},
                "reason": "High profitability",
                "recommended_action": "Offer premium product",
                "priority": Priority.HIGH,
                "confidence": ConfidenceLevel.HIGH,
                "limitations": ["Based on current snapshot"]
            }
        
        engine.register_rule("high_profit_rule", condition, action)
        
        customer_data = {
            "customer_key": "CUST_001",
            "segment": "premium",
            "net_profit": 10000
        }
        
        recommendations = engine.evaluate_rules(customer_data, customer_key="CUST_001")
        assert len(recommendations) == 1
        assert recommendations[0].priority == Priority.HIGH
    
    def test_evaluate_rules_non_matching_condition(self):
        """Test evaluating rules with non-matching condition."""
        engine = RulesEngine()
        
        def condition(data):
            return data.get("net_profit", 0) > 5000
        
        def action(data):
            return {
                "triggering_metrics": {"net_profit": data.get("net_profit")},
                "reason": "High profitability",
                "recommended_action": "Offer premium product",
                "priority": Priority.HIGH,
                "confidence": ConfidenceLevel.HIGH,
                "limitations": ["Based on current snapshot"]
            }
        
        engine.register_rule("high_profit_rule", condition, action)
        
        customer_data = {
            "customer_key": "CUST_001",
            "segment": "standard",
            "net_profit": 1000
        }
        
        recommendations = engine.evaluate_rules(customer_data, customer_key="CUST_001")
        assert len(recommendations) == 0
    
    def test_evaluate_multiple_rules(self):
        """Test evaluating multiple rules."""
        engine = RulesEngine()
        
        def condition1(data):
            return data.get("net_profit", 0) > 5000
        
        def action1(data):
            return {
                "triggering_metrics": {"net_profit": data.get("net_profit")},
                "reason": "High profitability",
                "recommended_action": "Offer premium product",
                "priority": Priority.HIGH,
                "confidence": ConfidenceLevel.HIGH,
                "limitations": ["Based on current snapshot"]
            }
        
        def condition2(data):
            return data.get("risk_level") == "high"
        
        def action2(data):
            return {
                "triggering_metrics": {"risk_level": data.get("risk_level")},
                "reason": "High risk",
                "recommended_action": "Risk monitoring",
                "priority": Priority.CRITICAL,
                "confidence": ConfidenceLevel.MEDIUM,
                "limitations": ["Risk may change"]
            }
        
        engine.register_rule("high_profit_rule", condition1, action1)
        engine.register_rule("high_risk_rule", condition2, action2)
        
        customer_data = {
            "customer_key": "CUST_001",
            "segment": "premium",
            "net_profit": 10000,
            "risk_level": "high"
        }
        
        recommendations = engine.evaluate_rules(customer_data, customer_key="CUST_001")
        assert len(recommendations) == 2
