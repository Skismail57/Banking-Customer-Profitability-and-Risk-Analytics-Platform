"""Risk page for Streamlit application."""

import streamlit as st
import pandas as pd
from frontend.components import filters, kpi_cards, charts, tables
from frontend.config import config

# Use mock data loader for development
from src.data_platform.mock_data_loader import MockDataLoader as DataLoader


def get_risk_data(start_date, end_date, segments, risk_levels):
    """Get risk data from analytics layer.

    Args:
        start_date: Start date for data
        end_date: End date for data
        segments: Selected segments
        risk_levels: Selected risk levels

    Returns:
        Dictionary with risk data
    """
    data_loader = DataLoader()
    risk_data = data_loader.load_risk_data()

    # Apply segment filter only if segments are provided and not all segments
    if segments and len(segments) < 4 and 'customer_key' in risk_data.columns:
        try:
            customers = data_loader.load_customers(segments=segments)
            if 'customer_key' in customers.columns:
                risk_data = risk_data[risk_data['customer_key'].isin(customers['customer_key'])]
        except Exception:
            pass

    # Apply risk level filter only if risk_levels are provided and not all levels
    if risk_levels and len(risk_levels) < 4 and 'risk_level' in risk_data.columns:
        risk_data = risk_data[risk_data['risk_level'].isin(risk_levels)]

    # Calculate metrics with fallback values if data is empty
    if len(risk_data) == 0:
        return {
            'risk_data': risk_data,
            'high_risk_count': 0,
            'avg_risk_score': 0.0,
            'total_exposure': 0.0
        }

    return {
        'risk_data': risk_data,
        'high_risk_count': len(risk_data[risk_data['risk_level'].isin(['High', 'Critical'])]),
        'avg_risk_score': risk_data['risk_score'].mean() if 'risk_score' in risk_data.columns else 0.0,
        'total_exposure': risk_data['exposure_amount'].sum() if 'exposure_amount' in risk_data.columns else 0.0
    }


def render() -> None:
    """Render the risk page."""
    st.markdown('<h1 class="main-title">Credit Risk Analytics</h1>', unsafe_allow_html=True)

    # Intro section
    st.markdown("""
    <p style="color: #94a3b8; font-size: 1.1rem;">
        Advanced risk assessment and exposure monitoring for your banking portfolio.
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
            risk_levels = filters.risk_filter()

    # Get data
    try:
        data = get_risk_data(start_date, end_date, segments, risk_levels)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return

    st.markdown("---")

    # KPI Cards
    st.markdown("### Key Performance Indicators")

    # Handle NaN values for display
    avg_risk_score = data['avg_risk_score']
    if pd.isna(avg_risk_score):
        avg_risk_score = 0.0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        kpi_cards.kpi_card(
            title="High Risk Customers",
            value=f"{data['high_risk_count']:,}",
            help_text="Customers with high or critical risk level"
        )

    with col2:
        kpi_cards.kpi_card(
            title="Avg Risk Score",
            value=f"{avg_risk_score:.2f}",
            help_text="Average risk score across all customers"
        )

    with col3:
        kpi_cards.kpi_card(
            title="Total Exposure",
            value=f"{config.currency_symbol}{data['total_exposure']:,.0f}",
            help_text="Total exposure amount"
        )

    with col4:
        kpi_cards.kpi_card(
            title="Total Customers",
            value=f"{len(data['risk_data']):,}",
            help_text="Number of customers analyzed"
        )

    st.markdown("---")

    # Risk Data Table
    st.markdown("### Risk Analysis Data")
    tables.data_table(data['risk_data'])

    st.markdown("---")

    # Charts
    st.markdown("### Risk Analytics Charts")

    col1, col2 = st.columns(2)

    with col1:
        # Risk Level Distribution
        charts.bar_chart(
            data['risk_data'],
            x='risk_level',
            y='risk_score',
            title='Risk Score by Level'
        )

    with col2:
        # Exposure by Risk Level
        charts.bar_chart(
            data['risk_data'],
            x='risk_level',
            y='exposure_amount',
            title='Exposure by Risk Level'
        )
