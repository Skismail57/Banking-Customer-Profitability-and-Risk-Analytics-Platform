"""Unit tests for Historical CLV calculation."""

import pytest
import pandas as pd
from datetime import date, timedelta

from src.clv_analytics.historical import HistoricalCLVCalculator
from src.clv_analytics.base import CLVParameters


class TestHistoricalCLVCalculator:
    """Tests for HistoricalCLVCalculator."""
    
    def test_calculate_historical_clv(self):
        """Test historical CLV calculation."""
        calculator = HistoricalCLVCalculator()
        
        df = pd.DataFrame({
            "customer_key": [1, 1, 1],
            "net_profit": [100, 150, 200],
            "as_of_date": [
                date(2023, 1, 1),
                date(2023, 2, 1),
                date(2023, 3, 1)
            ]
        })
        
        result = calculator.calculate(df)
        
        assert result.clv_value == 450  # Sum of profits
        assert result.components["historical_profit"] == 450
        assert result.clv_type.value == "historical"
    
    def test_calculate_batch(self):
        """Test batch historical CLV calculation."""
        calculator = HistoricalCLVCalculator()
        
        df = pd.DataFrame({
            "customer_key": [1, 1, 2, 2],
            "net_profit": [100, 150, 200, 250],
            "as_of_date": [
                date(2023, 1, 1),
                date(2023, 2, 1),
                date(2023, 1, 1),
                date(2023, 2, 1)
            ]
        })
        
        results = calculator.calculate_batch(df)
        
        assert len(results) == 2
        assert results.loc[results["customer_key"] == 1, "clv_value"].values[0] == 250
        assert results.loc[results["customer_key"] == 2, "clv_value"].values[0] == 450
