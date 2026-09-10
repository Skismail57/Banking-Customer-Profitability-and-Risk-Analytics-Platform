"""Data Platform Integration Layer.

This layer provides unified access to banking data and serves as the foundation
for all analytics modules. It integrates Customer 360, Transaction, and Product Analytics.

Architecture:
Banking Data → Data Platform → Customer 360/Transaction/Product Analytics → Core Analytics
"""

from src.data_platform.customer_360 import Customer360Platform
from src.data_platform.transaction_analytics import TransactionAnalyticsPlatform
from src.data_platform.product_analytics import ProductAnalyticsPlatform
from src.data_platform.data_loader import DataLoader

__all__ = [
    'Customer360Platform',
    'TransactionAnalyticsPlatform',
    'ProductAnalyticsPlatform',
    'DataLoader'
]
