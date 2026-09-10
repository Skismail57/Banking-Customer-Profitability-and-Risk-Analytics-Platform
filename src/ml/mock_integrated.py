"""Mock Integrated ML Layer for development without trained models."""

from typing import Dict, Any, Optional, List
from datetime import date
import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class MockIntegratedMLLayer:
    """Mock integrated ML layer for development."""
    
    def __init__(self, data_loader=None):
        """Initialize mock ML layer.
        
        Args:
            data_loader: Data loader instance
        """
        self.data_loader = data_loader
        self.models = {
            'churn': MockChurnModel(),
            'risk': MockRiskModel(),
            'profitability': MockProfitabilityModel()
        }
    
    def predict_churn(self, customer_data: pd.DataFrame) -> pd.DataFrame:
        """Predict churn probability."""
        return self.models['churn'].predict(customer_data)
    
    def predict_risk(self, customer_data: pd.DataFrame) -> pd.DataFrame:
        """Predict risk score."""
        return self.models['risk'].predict(customer_data)
    
    def predict_profitability(self, customer_data: pd.DataFrame) -> pd.DataFrame:
        """Predict customer profitability."""
        return self.models['profitability'].predict(customer_data)


class MockChurnModel:
    """Mock churn prediction model."""
    
    def predict(self, customer_data: pd.DataFrame) -> pd.DataFrame:
        """Generate mock churn predictions."""
        np.random.seed(42)
        customer_data = customer_data.copy()
        customer_data['churn_probability'] = np.random.uniform(0, 1, len(customer_data))
        customer_data['churn_risk'] = pd.cut(
            customer_data['churn_probability'],
            bins=[0, 0.3, 0.6, 1.0],
            labels=['Low', 'Medium', 'High']
        )
        return customer_data


class MockRiskModel:
    """Mock risk prediction model."""
    
    def predict(self, customer_data: pd.DataFrame) -> pd.DataFrame:
        """Generate mock risk predictions."""
        np.random.seed(42)
        customer_data = customer_data.copy()
        customer_data['risk_score'] = np.random.uniform(0, 1, len(customer_data))
        customer_data['risk_level'] = pd.cut(
            customer_data['risk_score'],
            bins=[0, 0.25, 0.5, 0.75, 1.0],
            labels=['Low', 'Medium', 'High', 'Critical']
        )
        return customer_data


class MockProfitabilityModel:
    """Mock profitability prediction model."""
    
    def predict(self, customer_data: pd.DataFrame) -> pd.DataFrame:
        """Generate mock profitability predictions."""
        np.random.seed(42)
        customer_data = customer_data.copy()
        customer_data['predicted_profit'] = np.random.uniform(100, 10000, len(customer_data))
        customer_data['profit_tier'] = pd.cut(
            customer_data['predicted_profit'],
            bins=[0, 1000, 5000, 10000],
            labels=['Low', 'Medium', 'High']
        )
        return customer_data