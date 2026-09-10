"""Model Monitoring page for Streamlit application."""

import streamlit as st
import pandas as pd
import numpy as np
from frontend.components import filters, kpi_cards, charts, tables
from frontend.config import config


@st.cache_data(ttl=config.cache_ttl)
def get_model_monitoring_data(start_date, end_date, model_names, model_types):
    """Get model monitoring data from analytics layer.
    
    Args:
        start_date: Start date for data
        end_date: End date for data
        model_names: Selected model names
        model_types: Selected model types
    
    Returns:
        Dictionary with model monitoring data
    """
    # Generate mock model monitoring data
    np.random.seed(42)
    models = ['Churn Model', 'Risk Model', 'Profitability Model', 'Default Model']
    model_types_list = ['Classification', 'Classification', 'Regression', 'Classification']
    
    model_data = pd.DataFrame({
        'model_name': models,
        'model_type': model_types_list,
        'accuracy': np.random.uniform(0.7, 0.95, len(models)),
        'precision': np.random.uniform(0.65, 0.92, len(models)),
        'recall': np.random.uniform(0.68, 0.90, len(models)),
        'f1_score': np.random.uniform(0.67, 0.91, len(models)),
        'drift_score': np.random.uniform(0.0, 0.3, len(models)),
        'last_updated': pd.Timestamp.now()
    })
    
    if model_names:
        model_data = model_data[model_data['model_name'].isin(model_names)]
    
    if model_types:
        model_data = model_data[model_data['model_type'].isin(model_types)]
    
    return {
        'model_data': model_data,
        'total_models': len(model_data),
        'avg_accuracy': model_data['accuracy'].mean()
    }


def render() -> None:
    """Render the model monitoring page with advanced animations."""
    st.markdown('<h1 class="main-title">Model Monitoring</h1>', unsafe_allow_html=True)

    # Intro section
    st.markdown("""
    <p style="color: #94a3b8; font-size: 1.1rem;">
        Real-time model performance monitoring with drift detection and accuracy tracking.
    </p>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Filters
    st.markdown("### Filters")
    with st.expander("Filter Options", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            start_date, end_date = filters.date_range_filter()

        with col2:
            model_names = st.multiselect(
                "Select Models",
                options=["Churn Model", "Risk Model", "Profitability Model", "Default Model"],
                default=["Churn Model", "Risk Model", "Profitability Model", "Default Model"]
            )
            model_types = st.multiselect(
                "Select Model Types",
                options=["Classification", "Regression"],
                default=["Classification", "Regression"]
            )
    
    # Get data
    try:
        data = get_model_monitoring_data(start_date, end_date, model_names, model_types)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return
    
    st.markdown("---")
    
    # KPI Cards
    st.markdown("### Key Performance Indicators")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        kpi_cards.kpi_card(
            title="Total Models",
            value=f"{data['total_models']}",
            help_text="Number of monitored models"
        )
    
    with col2:
        kpi_cards.kpi_card(
            title="Avg Accuracy",
            value=f"{data['avg_accuracy']:.2%}",
            help_text="Average model accuracy"
        )
    
    with col3:
        kpi_cards.kpi_card(
            title="Model Types",
            value=f"{data['model_data']['model_type'].nunique()}",
            help_text="Number of model types"
        )
    
    st.markdown("---")
    
    # Model Data Table
    st.markdown("### Model Performance Metrics")
    tables.data_table(data['model_data'])