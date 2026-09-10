"""Streamlit application configuration."""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class AppConfig:
    """Application configuration."""
    
    # Database configuration
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "5432"))
    db_name: str = os.getenv("DB_NAME", "banking_analytics")
    db_user: str = os.getenv("DB_USER", "postgres")
    db_password: str = os.getenv("DB_PASSWORD", "")
    
    # Cache configuration
    cache_ttl: int = 3600  # 1 hour
    cache_max_entries: int = 100

    # Currency configuration
    currency_symbol: str = "₹"
    currency_code: str = "INR"
    
    # Pagination
    default_page_size: int = 50
    max_page_size: int = 500
    
    # Chart configuration
    default_chart_height: int = 400
    default_chart_width: int = 800
    
    # Theme - Modern Gradient Colors
    primary_color: str = "#6366f1"  # Indigo
    secondary_color: str = "#8b5cf6"  # Purple
    success_color: str = "#10b981"  # Emerald
    warning_color: str = "#f59e0b"  # Amber
    danger_color: str = "#ef4444"  # Red
    accent_color: str = "#06b6d4"  # Cyan
    gradient_start: str = "#667eea"  # Purple
    gradient_end: str = "#764ba2"  # Deep Purple
    
    # Risk levels
    risk_levels: list = None
    risk_colors: dict = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.risk_levels is None:
            self.risk_levels = ["low", "medium", "high", "critical"]
        
        if self.risk_colors is None:
            self.risk_colors = {
                "low": "#2ca02c",
                "medium": "#ff7f0e",
                "high": "#d62728",
                "critical": "#9467bd",
            }


# Global configuration instance
config = AppConfig()
