"""Products page for Streamlit application."""

import streamlit as st
import pandas as pd
from frontend.components import filters, kpi_cards, charts, tables
from frontend.config import config

# Use mock data loader for development
from src.data_platform.mock_data_loader import MockDataLoader as DataLoader


def get_product_data(start_date, end_date, products, segments):
    """Get product data from analytics layer.

    Args:
        start_date: Start date for data
        end_date: End date for data
        products: Selected products
        segments: Selected segments

    Returns:
        Dictionary with product data
    """
    data_loader = DataLoader()
    product_data = data_loader.load_product_data()

    if products:
        product_data = product_data[product_data['product_type'].isin(products)]

    return {
        'product_data': product_data,
        'total_products': len(product_data),
        'total_revenue': product_data['total_revenue'].sum()
    }


def render() -> None:
    """Render the products page."""
    st.markdown('<h1 class="main-title">Product Analytics</h1>', unsafe_allow_html=True)

    # Intro section
    st.markdown("""
    <p style="color: #94a3b8; font-size: 1.1rem;">
        Comprehensive product performance analysis with revenue, NPL rates, and customer metrics.
    </p>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Filters
    st.markdown("### Filters")
    with st.expander("Filter Options", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            start_date, end_date = filters.date_range_filter()
            products = filters.product_filter(["Checking", "Savings", "Credit Card", "Loan", "Mortgage"])

        with col2:
            segments = filters.segment_filter(["Retail", "Commercial", "Wealth", "SME"])

    # Get data
    try:
        data = get_product_data(start_date, end_date, products, segments)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return

    st.markdown("---")

    # KPI Cards
    st.markdown("### Key Performance Indicators")

    col1, col2, col3 = st.columns(3)

    with col1:
        kpi_cards.kpi_card(
            title="Total Products",
            value=f"{data['total_products']}",
            help_text="Number of product types"
        )

    with col2:
        kpi_cards.kpi_card(
            title="Total Revenue",
            value=f"{config.currency_symbol}{data['total_revenue']:,.0f}",
            help_text="Total revenue across all products"
        )

    with col3:
        kpi_cards.kpi_card(
            title="Total Customers",
            value=f"{data['product_data']['total_customers'].sum():,}",
            help_text="Total customers across products"
        )

    st.markdown("---")

    # Product Data Table
    st.markdown("### Product Performance")
    tables.data_table(data['product_data'])

    st.markdown("---")

    # Charts
    st.markdown("### Product Analytics Charts")

    col1, col2 = st.columns(2)

    with col1:
        # Revenue by Product
        charts.bar_chart(
            data['product_data'],
            x='product_type',
            y='total_revenue',
            title='Total Revenue'
        )

    with col2:
        # Customer Distribution
        charts.bar_chart(
            data['product_data'],
            x='product_type',
            y='total_customers',
            title='Customer Distribution'
        )

    st.markdown("---")

    # Average Balance by Product
    st.markdown("### Average Balance")
    charts.bar_chart(
        data['product_data'],
        x='product_type',
        y='avg_balance',
        title='Average Balance'
    )

    st.markdown("---")

    # NPL Rate by Product
    st.markdown("### NPL Rate")
    charts.bar_chart(
        data['product_data'],
        x='product_type',
        y='npl_rate',
        title='NPL Rate'
    )
