"""Streamlit pages package."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from frontend.pages import (
    home,
    executive_overview,
    customer_360,
    profitability,
    risk,
    segmentation,
    churn,
    transactions,
    products,
    decision_intelligence,
    model_monitoring,
    data_quality,
    live_monitor,
)
