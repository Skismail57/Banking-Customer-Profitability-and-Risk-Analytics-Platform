"""Data Quality page for Streamlit application."""

import streamlit as st
import pandas as pd
import numpy as np
from frontend.components import filters, kpi_cards, charts, tables
from frontend.config import config


def get_data_quality_data():
    """Get data quality metrics from analytics layer.

    Returns:
        Dictionary with data quality data
    """
    # Generate mock data quality metrics
    np.random.seed(42)

    kpi_data = {
        "total_records": 1000000,
        "complete_records": 950000,
        "duplicate_records": 5000,
        "missing_values": 45000,
        "data_quality_score": 95.0
    }

    quality_metrics = pd.DataFrame({
        'table': ['customers', 'transactions', 'accounts', 'products'],
        'total_rows': [10000, 100000, 50000, 1000],
        'complete_rows': [9500, 98000, 49000, 980],
        'quality_score': [95.0, 98.0, 98.0, 98.0],
        'last_checked': pd.Timestamp.now()
    })

    return {
        'kpi_data': kpi_data,
        'quality_metrics': quality_metrics
    }


def render() -> None:
    """Render the data quality page with advanced animations."""
    st.markdown('<h1 class="main-title">Data Quality Monitoring</h1>', unsafe_allow_html=True)

    # Animated intro
    st.markdown("""
    <div style="animation: fadeIn 0.8s ease-out;">
        <p style="color: #94a3b8; font-size: 1.1rem;">
            Comprehensive data quality monitoring with completeness, accuracy, and consistency tracking.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Get data
    try:
        data = get_data_quality_data()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return
    
    st.markdown("---")
    
    # KPI Cards
    st.markdown("### Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        kpi_cards.kpi_card(
            title="Total Records",
            value=f"{data['kpi_data']['total_records']:,}",
            help_text="Total records in the database"
        )
    
    with col2:
        kpi_cards.kpi_card(
            title="Complete Records",
            value=f"{data['kpi_data']['complete_records']:,}",
            help_text="Records with complete data"
        )
    
    with col3:
        kpi_cards.kpi_card(
            title="Duplicate Records",
            value=f"{data['kpi_data']['duplicate_records']:,}",
            help_text="Number of duplicate records"
        )
    
    with col4:
        kpi_cards.kpi_card(
            title="Quality Score",
            value=f"{data['kpi_data']['data_quality_score']:.1f}%",
            help_text="Overall data quality score"
        )
    
    st.markdown("---")
    
    # Quality Metrics Table
    st.markdown("### Data Quality Metrics by Table")
    tables.data_table(data['quality_metrics'])