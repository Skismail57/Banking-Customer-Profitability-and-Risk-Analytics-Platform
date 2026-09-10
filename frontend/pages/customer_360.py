"""Customer 360 page for Streamlit application."""

import streamlit as st
import pandas as pd
from frontend.components import filters, kpi_cards, charts, tables
from frontend.config import config

# Use mock data loader for development
from src.data_platform.mock_data_loader import MockDataLoader as DataLoader


def get_customer_data(customer_key):
    """Get customer 360 data from analytics layer.

    Args:
        customer_key: Customer identifier

    Returns:
        Dictionary with customer data
    """
    data_loader = DataLoader()
    return data_loader.get_customer_360(customer_key)


def render() -> None:
    """Render the customer 360 page with advanced animations."""
    st.markdown('<h1 class="main-title">Customer 360</h1>', unsafe_allow_html=True)

    # Intro section
    st.markdown("""
    <p style="color: #94a3b8; font-size: 1.1rem;">
        Complete customer profile with comprehensive metrics, risk assessment, and behavioral analysis.
    </p>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Customer search
    st.markdown("### Customer Search")
    search_query = filters.customer_search()

    # For demo, use a default customer if no search
    customer_key = search_query if search_query else "CUST_000000"
    
    # Get data
    try:
        data = get_customer_data(customer_key)
    except Exception as e:
        st.error(f"Error loading customer data: {e}")
        return
    
    if data is None:
        st.warning(f"Customer {customer_key} not found")
        return
    
    st.markdown("---")
    
    # Customer Profile
    st.markdown("### Customer Profile")
    
    if data['customer']:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"**Customer Name**: {data['customer']['customer_name']}")
            st.markdown(f"**Segment**: {data['customer']['segment']}")
            st.markdown(f"**Region**: {data['customer']['region']}")
        
        with col2:
            st.markdown(f"**Age**: {data['customer']['age']}")
            st.markdown(f"**Gender**: {data['customer']['gender']}")
            st.markdown(f"**Tenure**: {data['customer']['tenure_months']} months")
        
        with col3:
            st.markdown(f"**Account Balance**: {config.currency_symbol}{data['customer']['account_balance']:,.0f}")
            st.markdown(f"**Credit Score**: {data['customer']['credit_score']}")
    
    st.markdown("---")
    
    # Customer Metrics
    st.markdown("### Customer Metrics")

    if data['metrics']:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            kpi_cards.kpi_card(
                title="Total Revenue",
                value=f"{config.currency_symbol}{data['metrics']['total_revenue']:,.0f}",
                help_text="Total revenue"
            )

        with col2:
            kpi_cards.kpi_card(
                title="Net Profit",
                value=f"{config.currency_symbol}{data['metrics']['net_profit']:,.0f}",
                help_text="Net profit"
            )

        with col3:
            kpi_cards.kpi_card(
                title="Risk Score",
                value=f"{data['metrics']['risk_score']:.2f}",
                help_text="Risk score"
            )

        with col4:
            kpi_cards.kpi_card(
                title="CLV",
                value=f"{config.currency_symbol}{data['metrics']['customer_lifetime_value']:,.0f}",
                help_text="Customer lifetime value"
            )
    
    st.markdown("---")
    
    # Risk Information
    st.markdown("### Risk Information")
    
    if data['risk']:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"**Risk Level**: {data['risk']['risk_level']}")
        
        with col2:
            st.markdown(f"**Exposure**: {config.currency_symbol}{data['risk']['exposure_amount']:,.0f}")
        
        with col3:
            st.markdown(f"**Delinquency Days**: {data['risk']['delinquency_days']}")
    
    st.markdown("---")

    # Recent Transactions
    st.markdown("### Recent Transactions")

    if data['recent_transactions']:
        transactions_df = pd.DataFrame(data['recent_transactions'])
        tables.data_table(transactions_df)

    st.markdown("---")

    # Customer Performance Charts
    st.markdown("### Customer Performance Analysis")

    if data['metrics']:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Revenue vs Profit")
            charts.bar_chart(
                pd.DataFrame({
                    'metric': ['Revenue', 'Profit'],
                    'value': [data['metrics']['total_revenue'], data['metrics']['net_profit']]
                }),
                x='metric',
                y='value',
                title='Revenue vs Profit'
            )

        with col2:
            st.markdown("#### Risk & CLV")
            charts.bar_chart(
                pd.DataFrame({
                    'metric': ['Risk Score', 'CLV'],
                    'value': [data['metrics']['risk_score'], data['metrics']['customer_lifetime_value']]
                }),
                x='metric',
                y='value',
                title='Risk & CLV'
            )