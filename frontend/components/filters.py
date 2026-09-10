"""Reusable filter components."""

import streamlit as st
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import pandas as pd

from frontend.config import config


def date_range_filter(
    key: str = "date_range",
    default_days: int = 30
) -> tuple:
    """Create a date range filter.
    
    Args:
        key: Unique key for the filter
        default_days: Default number of days to show
    
    Returns:
        Tuple of (start_date, end_date)
    """
    col1, col2 = st.columns(2)
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=default_days)
    
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=start_date,
            key=f"{key}_start"
        )
    
    with col2:
        end_date = st.date_input(
            "End Date",
            value=end_date,
            key=f"{key}_end"
        )
    
    return start_date, end_date


def segment_filter(
    segments: List[str],
    key: str = "segment",
    default: Optional[List[str]] = None
) -> List[str]:
    """Create a segment filter.
    
    Args:
        segments: List of available segments
        key: Unique key for the filter
        default: Default selected segments
    
    Returns:
        List of selected segments
    """
    if default is None:
        default = segments
    
    selected = st.multiselect(
        "Select Segments",
        options=segments,
        default=default,
        key=key
    )
    
    return selected if selected else segments


def risk_filter(
    key: str = "risk",
    default: Optional[List[str]] = None
) -> List[str]:
    """Create a risk level filter.
    
    Args:
        key: Unique key for the filter
        default: Default selected risk levels
    
    Returns:
        List of selected risk levels
    """
    if default is None:
        default = config.risk_levels
    
    selected = st.multiselect(
        "Select Risk Levels",
        options=config.risk_levels,
        default=default,
        key=key
    )
    
    return selected if selected else config.risk_levels


def customer_search(
    key: str = "customer_search"
) -> str:
    """Create a customer search filter.
    
    Args:
        key: Unique key for the filter
    
    Returns:
        Search query string
    """
    search_query = st.text_input(
        "Search Customer",
        placeholder="Enter customer name or ID...",
        key=key
    )
    
    return search_query


def region_filter(
    regions: List[str],
    key: str = "region",
    default: Optional[List[str]] = None
) -> List[str]:
    """Create a region filter.
    
    Args:
        regions: List of available regions
        key: Unique key for the filter
        default: Default selected regions
    
    Returns:
        List of selected regions
    """
    if default is None:
        default = regions
    
    selected = st.multiselect(
        "Select Regions",
        options=regions,
        default=default,
        key=key
    )
    
    return selected if selected else regions


def product_filter(
    products: List[str],
    key: str = "product",
    default: Optional[List[str]] = None
) -> List[str]:
    """Create a product filter.
    
    Args:
        products: List of available products
        key: Unique key for the filter
        default: Default selected products
    
    Returns:
        List of selected products
    """
    if default is None:
        default = products
    
    selected = st.multiselect(
        "Select Products",
        options=products,
        default=default,
        key=key
    )
    
    return selected if selected else products


def priority_filter(
    key: str = "priority",
    default: Optional[List[str]] = None
) -> List[str]:
    """Create a priority filter for recommendations.

    Args:
        key: Unique key for the filter
        default: Default selected priorities

    Returns:
        List of selected priorities
    """
    priorities = ["high", "medium", "low"]

    if default is None:
        default = priorities

    selected = st.multiselect(
        "Select Priorities",
        options=priorities,
        default=default,
        key=key
    )

    return selected if selected else priorities


def confidence_filter(
    key: str = "confidence",
    default: Optional[List[str]] = None
) -> List[str]:
    """Create a confidence filter for recommendations.
    
    Args:
        key: Unique key for the filter
        default: Default selected confidence levels
    
    Returns:
        List of selected confidence levels
    """
    confidence_levels = ["high", "medium", "low"]
    
    if default is None:
        default = confidence_levels
    
    selected = st.multiselect(
        "Select Confidence Levels",
        options=confidence_levels,
        default=default,
        key=key
    )
    
    return selected if selected else confidence_levels


def apply_filters(
    df: pd.DataFrame,
    filters: Dict[str, Any]
) -> pd.DataFrame:
    """Apply filters to a DataFrame.
    
    Args:
        df: DataFrame to filter
        filters: Dictionary of filter conditions
    
    Returns:
        Filtered DataFrame
    """
    filtered_df = df.copy()
    
    # Date range filter
    if "date_column" in filters and "start_date" in filters and "end_date" in filters:
        filtered_df = filtered_df[
            (filtered_df[filters["date_column"]] >= filters["start_date"]) &
            (filtered_df[filters["date_column"]] <= filters["end_date"])
        ]
    
    # Segment filter
    if "segment" in filters and filters["segment"]:
        filtered_df = filtered_df[filtered_df["segment"].isin(filters["segment"])]
    
    # Risk level filter
    if "risk_level" in filters and filters["risk_level"]:
        filtered_df = filtered_df[filtered_df["risk_level"].isin(filters["risk_level"])]
    
    # Region filter
    if "region" in filters and filters["region"]:
        filtered_df = filtered_df[filtered_df["region"].isin(filters["region"])]
    
    # Product filter
    if "product" in filters and filters["product"]:
        filtered_df = filtered_df[filtered_df["product"].isin(filters["product"])]
    
    # Customer search
    if "customer_search" in filters and filters["customer_search"]:
        search_term = filters["customer_search"].lower()
        filtered_df = filtered_df[
            filtered_df["customer_name"].str.lower().str.contains(search_term, na=False) |
            filtered_df["customer_id"].astype(str).str.contains(search_term, na=False)
        ]
    
    return filtered_df
