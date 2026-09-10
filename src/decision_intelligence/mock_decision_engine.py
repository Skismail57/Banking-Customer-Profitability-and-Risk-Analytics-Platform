"""Mock Decision Engine for development without ML models."""

from typing import Dict, Any, Optional, List
from datetime import date
import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class MockDecisionEngine:
    """Mock decision engine for development without ML models."""
    
    def __init__(self, as_of_date: Optional[date] = None, data_loader=None):
        """Initialize mock decision engine.
        
        Args:
            as_of_date: As-of date for analysis
            data_loader: Data loader instance
        """
        self.as_of_date = as_of_date or date.today()
        self.data_loader = data_loader
    
    def get_executive_recommendations(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        segments: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Get executive-level recommendations."""
        return [
            {
                'category': 'Profitability',
                'priority': 'high',
                'recommendation': 'Focus on high-value customer retention',
                'expected_impact': '+15% revenue',
                'action_items': ['Implement loyalty program', 'Personalized offers']
            },
            {
                'category': 'Risk',
                'priority': 'medium',
                'recommendation': 'Review credit exposure in commercial segment',
                'expected_impact': '-10% risk',
                'action_items': ['Stress testing', 'Portfolio review']
            },
            {
                'category': 'Growth',
                'priority': 'low',
                'recommendation': 'Expand digital channel presence',
                'expected_impact': '+5% acquisition',
                'action_items': ['Mobile app enhancements', 'Digital marketing']
            }
        ]
    
    def get_customer_recommendations(self, customer_key: str) -> List[Dict[str, Any]]:
        """Get customer-specific recommendations."""
        return [
            {
                'category': 'Cross-sell',
                'product': 'Credit Card',
                'probability': 0.75,
                'reason': 'High transaction volume in checking account'
            },
            {
                'category': 'Retention',
                'action': 'Rate optimization',
                'probability': 0.60,
                'reason': 'Competitive rate analysis'
            }
        ]
    
    def get_segment_insights(self, segment: str) -> Dict[str, Any]:
        """Get segment-level insights."""
        np.random.seed(42)
        return {
            'segment': segment,
            'total_customers': np.random.randint(100, 500),
            'avg_profitability': np.random.uniform(100, 1000),
            'growth_rate': np.random.uniform(-0.1, 0.2),
            'risk_level': np.random.choice(['Low', 'Medium', 'High']),
            'top_opportunities': [
                'Digital adoption',
                'Product bundling',
                'Referral programs'
            ]
        }