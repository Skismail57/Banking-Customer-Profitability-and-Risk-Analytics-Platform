"""Executive Overview page for Streamlit application."""

import streamlit as st
import pandas as pd
from datetime import date
from frontend.components import filters, kpi_cards, charts, tables
from frontend.config import config

# Use mock data loader for development
from src.data_platform.mock_data_loader import MockDataLoader as DataLoader
from src.decision_intelligence.mock_decision_engine import MockDecisionEngine as DecisionEngine


def get_executive_data(start_date, end_date, segments, regions):
    """Get executive overview data from analytics layer.

    Args:
        start_date: Start date for data
        end_date: End date for data
        segments: Selected segments
        regions: Selected regions

    Returns:
        Dictionary with executive data
    """
    data_loader = DataLoader()
    decision_engine = DecisionEngine(as_of_date=end_date, data_loader=data_loader)

    # Get executive metrics
    metrics = data_loader.get_executive_metrics(start_date, end_date)

    # Get recommendations
    recommendations = decision_engine.get_executive_recommendations(start_date, end_date, segments)

    # Get customer metrics
    customer_metrics = data_loader.load_customer_metrics()

    if segments:
        customers = data_loader.load_customers(segments=segments)
        customer_metrics = customer_metrics[customer_metrics['customer_key'].isin(customers['customer_key'])]

    # Get risk data
    risk_data = data_loader.load_risk_data()

    return {
        'metrics': metrics,
        'recommendations': recommendations,
        'customer_metrics': customer_metrics,
        'risk_data': risk_data
    }


def render() -> None:
    """Render the executive overview page."""
    st.markdown('<h1 class="main-title">Executive Overview</h1>', unsafe_allow_html=True)

    # Intro section
    st.markdown("""
    <p style="color: #94a3b8; font-size: 1.1rem;">
        Real-time insights into your banking performance metrics and key indicators.
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
        data = get_executive_data(start_date, end_date, segments, regions)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return

    st.markdown("---")

    # KPI Cards
    st.markdown("### Key Performance Indicators")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        kpi_cards.kpi_card(
            title="Total Customers",
            value=f"{data['metrics']['total_customers']:,}",
            help_text="Total active customers"
        )

    with col2:
        kpi_cards.kpi_card(
            title="Total Revenue",
            value=f"{config.currency_symbol}{data['metrics']['total_revenue']:,.0f}",
            help_text="Total revenue"
        )

    with col3:
        kpi_cards.kpi_card(
            title="Total Profit",
            value=f"{config.currency_symbol}{data['metrics']['total_profit']:,.0f}",
            help_text="Total net profit"
        )

    with col4:
        kpi_cards.kpi_card(
            title="High Risk Customers",
            value=f"{data['metrics']['high_risk_customers']:,}",
            help_text="Customers with high or critical risk"
        )

    st.markdown("---")

    # Executive Recommendations
    st.markdown("### Executive Recommendations")

    for i, rec in enumerate(data['recommendations'], 1):
        with st.expander(f"{i}. {rec['category']} - {rec['priority'].capitalize()} Priority", expanded=i==1):
            st.markdown(f"**Recommendation:** {rec['recommendation']}")
            st.markdown(f"**Expected Impact:** {rec['expected_impact']}")
            st.markdown("**Action Items:**")
            for action in rec['action_items']:
                st.markdown(f"- {action}")

    st.markdown("---")

    # Customer Metrics Summary
    st.markdown("### Customer Metrics Summary")
    tables.data_table(data['customer_metrics'])

    st.markdown("---")

    # Charts
    st.markdown("### Executive Analytics Charts")

    col1, col2 = st.columns(2)

    with col1:
        # Revenue vs Profit
        charts.bar_chart(
            data['customer_metrics'],
            x='customer_key',
            y='total_revenue',
            title='Revenue by Customer'
        )

    with col2:
        # Risk Distribution
        charts.bar_chart(
            data['risk_data'],
            x='risk_level',
            y='risk_score',
            title='Risk Score by Level'
        )
