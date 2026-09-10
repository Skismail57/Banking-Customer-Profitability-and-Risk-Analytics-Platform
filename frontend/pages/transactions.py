"""Transactions page for Streamlit application."""

import streamlit as st
import pandas as pd
from frontend.components import filters, kpi_cards, charts, tables
from frontend.config import config

# Use mock data loader for development
from src.data_platform.mock_data_loader import MockDataLoader as DataLoader


def get_transaction_data(start_date, end_date, products, channels):
    """Get transaction data from analytics layer.

    Args:
        start_date: Start date for data
        end_date: End date for data
        products: Selected products
        channels: Selected channels

    Returns:
        Dictionary with transaction data
    """
    data_loader = DataLoader()
    transaction_data = data_loader.load_transactions(start_date=start_date, end_date=end_date, limit=1000)

    if products:
        transaction_data = transaction_data[transaction_data['product_type'].isin(products)]

    return {
        'transaction_data': transaction_data,
        'total_transactions': len(transaction_data),
        'total_volume': transaction_data['amount'].sum(),
        'avg_transaction': transaction_data['amount'].mean()
    }


def render() -> None:
    """Render the transactions page."""
    st.markdown('<h1 class="main-title">Transaction Analytics</h1>', unsafe_allow_html=True)

    # Intro section
    st.markdown("""
    <p style="color: #94a3b8; font-size: 1.1rem;">
        Real-time transaction monitoring with advanced analytics and fraud detection insights.
    </p>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Filters
    st.markdown("### Filters")
    with st.expander("Filter Options", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            start_date, end_date = filters.date_range_filter()
            products = filters.product_filter(["Checking", "Savings", "Credit Card", "Loan"])

        with col2:
            channels = st.multiselect(
                "Select Channels",
                options=["online", "mobile", "branch", "atm"],
                default=["online", "mobile", "branch", "atm"]
            )

    # Get data
    try:
        data = get_transaction_data(start_date, end_date, products, channels)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return

    st.markdown("---")

    # KPI Cards
    st.markdown("### Key Performance Indicators")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        kpi_cards.kpi_card(
            title="Total Transactions",
            value=f"{data['total_transactions']:,}",
            help_text="Total number of transactions"
        )

    with col2:
        kpi_cards.kpi_card(
            title="Total Volume",
            value=f"{config.currency_symbol}{data['total_volume']:,.0f}",
            help_text="Total transaction value"
        )

    with col3:
        kpi_cards.kpi_card(
            title="Avg Transaction",
            value=f"{config.currency_symbol}{data['avg_transaction']:,.0f}",
            help_text="Average transaction amount"
        )

    with col4:
        kpi_cards.kpi_card(
            title="Unique Customers",
            value=f"{data['transaction_data']['customer_key'].nunique():,}",
            help_text="Number of unique customers"
        )

    st.markdown("---")

    # Transaction Data Table
    st.markdown("### Recent Transactions")
    tables.data_table(data['transaction_data'])

    st.markdown("---")

    # Charts
    st.markdown("### Transaction Analytics Charts")

    col1, col2 = st.columns(2)

    with col1:
        # Transaction Type Distribution
        charts.bar_chart(
            data['transaction_data'],
            x='transaction_type',
            y='amount',
            title='Transaction Amount by Type'
        )

    with col2:
        # Product Type Distribution
        charts.bar_chart(
            data['transaction_data'],
            x='product_type',
            y='amount',
            title='Transaction Amount by Product'
        )
