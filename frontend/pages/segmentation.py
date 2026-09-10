"""Segmentation page for Streamlit application."""

import streamlit as st
import pandas as pd
from frontend.components import filters, kpi_cards, charts, tables
from frontend.config import config

# Use mock data loader for development
from src.data_platform.mock_data_loader import MockDataLoader as DataLoader


def get_segmentation_data(start_date, end_date, segments, regions):
    """Get segmentation data from analytics layer.

    Args:
        start_date: Start date for data
        end_date: End date for data
        segments: Selected segments
        regions: Selected regions

    Returns:
        Dictionary with segmentation data
    """
    data_loader = DataLoader()
    segmentation_data = data_loader.load_segmentation_data()

    if segments:
        segmentation_data = segmentation_data[segmentation_data['segment'].isin(segments)]

    # Calculate aggregates for KPIs
    segment_counts = segmentation_data.groupby('segment').size().reset_index(name='customer_count')

    return {
        'segmentation_data': segmentation_data,
        'segment_counts': segment_counts,
        'total_segments': len(segment_counts),
        'largest_segment': segment_counts.loc[segment_counts['customer_count'].idxmax(), 'segment'] if len(segment_counts) > 0 else None
    }


def render() -> None:
    """Render the segmentation page."""
    st.markdown('<h1 class="main-title">Customer Segmentation</h1>', unsafe_allow_html=True)

    # Intro section
    st.markdown("""
    <p style="color: #94a3b8; font-size: 1.1rem;">
        Intelligent customer segmentation with detailed behavioral and value analysis.
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
        data = get_segmentation_data(start_date, end_date, segments, regions)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return

    st.markdown("---")

    # KPI Cards
    st.markdown("### Key Performance Indicators")

    col1, col2, col3 = st.columns(3)

    with col1:
        kpi_cards.kpi_card(
            title="Total Segments",
            value=f"{data['total_segments']}",
            help_text="Number of customer segments"
        )

    with col2:
        kpi_cards.kpi_card(
            title="Largest Segment",
            value=data['largest_segment'] or "N/A",
            help_text="Segment with most customers"
        )

    with col3:
        kpi_cards.kpi_card(
            title="Total Customers",
            value=f"{len(data['segmentation_data']):,}",
            help_text="Number of customers segmented"
        )

    st.markdown("---")

    # Segmentation Data Table
    st.markdown("### Customer Segments")
    tables.data_table(data['segmentation_data'])

    st.markdown("---")

    # Charts
    st.markdown("### Segmentation Analytics Charts")

    col1, col2 = st.columns(2)

    with col1:
        # Customer Distribution by Segment
        charts.bar_chart(
            data['segment_counts'],
            x='segment',
            y='customer_count',
            title='Customer Distribution by Segment'
        )

    with col2:
        # Revenue by Segment
        charts.bar_chart(
            data['segmentation_data'],
            x='segment',
            y='total_revenue',
            title='Revenue by Segment'
        )

    st.markdown("---")

    # Average Balance by Segment
    st.markdown("### Average Balance by Segment")
    charts.bar_chart(
        data['segmentation_data'],
        x='segment',
        y='account_balance',
        title='Average Balance by Segment'
    )
