"""Churn page for Streamlit application."""

import streamlit as st
import pandas as pd
from frontend.components import filters, kpi_cards, charts, tables
from frontend.config import config

# Use mock data loader for development
from src.data_platform.mock_data_loader import MockDataLoader as DataLoader


def get_churn_data(start_date, end_date, segments, regions):
    """Get churn data from analytics layer.

    Args:
        start_date: Start date for data
        end_date: End date for data
        segments: Selected segments
        regions: Selected regions

    Returns:
        Dictionary with churn data
    """
    data_loader = DataLoader()
    churn_data = data_loader.load_churn_predictions()

    if segments:
        customers = data_loader.load_customers(segments=segments)
        churn_data = churn_data[churn_data['customer_key'].isin(customers['customer_key'])]

    high_churn_risk = len(churn_data[churn_data['churn_risk'] == 'High'])
    avg_churn_probability = churn_data['churn_probability'].mean()

    return {
        'churn_data': churn_data,
        'high_churn_risk': high_churn_risk,
        'avg_churn_probability': avg_churn_probability
    }


def render() -> None:
    """Render the churn page."""
    st.markdown('<h1 class="main-title">Churn Analytics</h1>', unsafe_allow_html=True)

    # Intro section
    st.markdown("""
    <p style="color: #94a3b8; font-size: 1.1rem;">
        Customer churn prediction and analysis with risk identification.
    </p>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Filters
    st.markdown("### Filters")
    with st.expander("Filter Options", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            start_date, end_date = filters.date_range_filter()
            segments = filters.segment_filter(["Retail", "Commercial", "Wealth", "SME"])

        with col2:
            regions = filters.region_filter(["North", "South", "East", "West"])

    # Get data
    try:
        data = get_churn_data(start_date, end_date, segments, regions)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return

    st.markdown("---")

    # KPI Cards
    st.markdown("### Key Performance Indicators")

    col1, col2, col3 = st.columns(3)

    with col1:
        kpi_cards.kpi_card(
            title="High Churn Risk",
            value=f"{data['high_churn_risk']:,}",
            help_text="Customers with high churn risk"
        )

    with col2:
        kpi_cards.kpi_card(
            title="Avg Churn Probability",
            value=f"{data['avg_churn_probability']:.2%}",
            help_text="Average churn probability"
        )

    with col3:
        kpi_cards.kpi_card(
            title="Total Customers",
            value=f"{len(data['churn_data']):,}",
            help_text="Number of customers analyzed"
        )

    st.markdown("---")

    # Churn Data Table
    st.markdown("### Churn Predictions")
    tables.data_table(data['churn_data'])

    st.markdown("---")

    # Charts
    st.markdown("### Churn Analytics Charts")

    col1, col2 = st.columns(2)

    with col1:
        # Churn Risk Distribution
        charts.bar_chart(
            data['churn_data'],
            x='churn_risk',
            y='churn_probability',
            title='Churn Risk Distribution'
        )

    with col2:
        # Churn Probability Distribution
        charts.histogram(
            data['churn_data'],
            'churn_probability',
            title='Churn Probability Distribution',
            nbins=30
        )

    st.markdown("---")

    # High Churn Risk Customers
    st.markdown("### High Churn Risk Customers")
    high_churn = data['churn_data'][data['churn_data']['churn_risk'] == 'High']
    if len(high_churn) > 0:
        tables.data_table(high_churn.head(20))
