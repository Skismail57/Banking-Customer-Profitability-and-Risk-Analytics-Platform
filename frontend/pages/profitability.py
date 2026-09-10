"""Profitability page for Streamlit application."""

import streamlit as st
import pandas as pd
from frontend.components import filters, kpi_cards, charts, tables
from frontend.config import config

# Use mock data loader for development
from src.data_platform.mock_data_loader import MockDataLoader as DataLoader


def get_profitability_data(start_date, end_date, segments, regions):
    """Get profitability data from analytics layer.

    Args:
        start_date: Start date for data
        end_date: End date for data
        segments: Selected segments
        regions: Selected regions

    Returns:
        Dictionary with profitability data
    """
    data_loader = DataLoader()
    customer_metrics = data_loader.load_customer_metrics()

    # Only filter if columns exist
    if segments and 'segment' in customer_metrics.columns:
        customer_metrics = customer_metrics[customer_metrics['segment'].isin(segments)]

    if regions and 'region' in customer_metrics.columns:
        customer_metrics = customer_metrics[customer_metrics['region'].isin(regions)]

    return {
        'customer_metrics': customer_metrics,
        'total_revenue': customer_metrics['total_revenue'].sum(),
        'total_profit': customer_metrics['net_profit'].sum(),
        'avg_profit_per_customer': customer_metrics['net_profit'].mean()
    }


def render() -> None:
    """Render the profitability page."""
    st.markdown('<h1 class="main-title">Profitability Analytics</h1>', unsafe_allow_html=True)

    # Intro section
    st.markdown("""
    <p style="color: #94a3b8; font-size: 1.1rem;">
        Comprehensive profitability analysis with revenue, profit, and customer metrics.
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
        data = get_profitability_data(start_date, end_date, segments, regions)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return

    st.markdown("---")

    # KPI Cards
    st.markdown("### Key Performance Indicators")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        kpi_cards.kpi_card(
            title="Total Revenue",
            value=f"{config.currency_symbol}{data['total_revenue']:,.0f}",
            help_text="Total revenue from all customers"
        )

    with col2:
        kpi_cards.kpi_card(
            title="Total Profit",
            value=f"{config.currency_symbol}{data['total_profit']:,.0f}",
            help_text="Total net profit"
        )

    with col3:
        kpi_cards.kpi_card(
            title="Avg Profit/Customer",
            value=f"{config.currency_symbol}{data['avg_profit_per_customer']:,.0f}",
            help_text="Average profit per customer"
        )

    with col4:
        kpi_cards.kpi_card(
            title="Total Customers",
            value=f"{len(data['customer_metrics']):,}",
            help_text="Number of customers analyzed"
        )

    st.markdown("---")

    # Customer Profitability Table
    st.markdown("### Customer Profitability")
    tables.data_table(data['customer_metrics'])

    st.markdown("---")

    # Charts
    st.markdown("### Profitability Charts")

    col1, col2 = st.columns(2)

    with col1:
        # Revenue Distribution
        charts.bar_chart(
            data['customer_metrics'],
            x='customer_key',
            y='total_revenue',
            title='Revenue by Customer'
        )

    with col2:
        # Profit Distribution
        charts.bar_chart(
            data['customer_metrics'],
            x='customer_key',
            y='net_profit',
            title='Profit by Customer'
        )
