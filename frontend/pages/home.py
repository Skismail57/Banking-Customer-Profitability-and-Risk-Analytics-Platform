"""Home page for Streamlit application."""

import streamlit as st
from frontend.components import kpi_cards


def render() -> None:
    """Render the home page."""
    st.markdown('<h1 class="main-title">🏦 Banking Analytics Platform</h1>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Welcome message
    st.markdown("""
    ## Welcome to the Banking Customer Profitability and Risk Analytics Platform
    
    This platform provides comprehensive analytics for banking customer data, including:
    
    - **Customer Profitability**: Analyze customer profitability and risk-adjusted returns
    - **Credit Risk**: Monitor risk levels, exposure, and delinquency
    - **Customer Segmentation**: Understand customer segments and their characteristics
    - **Churn & Retention**: Predict churn and identify retention opportunities
    - **Transaction Analytics**: Analyze transaction patterns and trends
    - **Product Analytics**: Evaluate product performance and adoption
    - **Decision Intelligence**: Get actionable recommendations based on analytics
    - **Model Monitoring**: Track model performance and drift
    
    ---
    
    ### Quick Navigation
    
    Use the sidebar to navigate to different analytics pages. Each page provides:
    
    - Interactive filters for data exploration
    - KPI cards for key metrics
    - Interactive charts for visualization
    - Drill-down capabilities for detailed analysis
    - Export options for data extraction
    
    ---
    
    ### Data Source
    
    All analytics are powered by the Python analytics layer, which processes raw data and generates:
    
    - Customer metrics (profitability, risk, churn, CLV)
    - Risk analytics (risk levels, exposure, concentration)
    - Predictive models (churn, default risk, profitability)
    - Decision intelligence recommendations
    
    The Streamlit application visualizes these pre-calculated metrics without duplicating business logic.
    
    ---
    
    ### Getting Started
    
    1. **Executive Overview**: Start here for high-level KPIs and trends
    2. **Customer 360**: Drill down into individual customer details
    3. **Profitability**: Analyze profitability trends and distribution
    4. **Risk**: Monitor risk levels and exposure
    5. **Segmentation**: Understand customer segments
    6. **Churn**: Analyze churn risk and retention opportunities
    7. **Transactions**: Explore transaction patterns
    8. **Products**: Evaluate product performance
    9. **Decision Intelligence**: Review actionable recommendations
    10. **Model Monitoring**: Track model performance
    11. **Data Quality**: Monitor data quality metrics
    """)
    
    st.markdown("---")
    
    # Platform stats (placeholder - would come from analytics layer)
    st.markdown("### Platform Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        kpi_cards.kpi_card(
            title="Total Customers",
            value="10,000+",
            help_text="Active customers in the database"
        )
    
    with col2:
        kpi_cards.kpi_card(
            title="Data Points",
            value="1M+",
            help_text="Total data points processed"
        )
    
    with col3:
        kpi_cards.kpi_card(
            title="Analytics Models",
            value="5",
            help_text="Active predictive models"
        )
    
    with col4:
        kpi_cards.kpi_card(
            title="Daily Updates",
            value="Yes",
            help_text="Data refreshed daily"
        )
