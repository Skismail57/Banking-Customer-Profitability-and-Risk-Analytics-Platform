"""Decision Intelligence page for Streamlit application."""

import streamlit as st
import pandas as pd
from frontend.components import filters, kpi_cards, charts, tables
from frontend.config import config

# Use mock data loader for development
from src.data_platform.mock_data_loader import MockDataLoader as DataLoader
from src.decision_intelligence.mock_decision_engine import MockDecisionEngine as DecisionEngine


@st.cache_data(ttl=config.cache_ttl)
def get_decision_intelligence_data(start_date, end_date, segments, priorities, confidence):
    """Get decision intelligence data from analytics layer.
    
    Args:
        start_date: Start date for data
        end_date: End date for data
        segments: Selected segments
        priorities: Selected priorities
        confidence: Selected confidence levels
    
    Returns:
        Dictionary with decision intelligence data
    """
    decision_engine = DecisionEngine(as_of_date=end_date, data_loader=DataLoader())
    recommendations = decision_engine.get_executive_recommendations(start_date, end_date, segments)
    
    if priorities:
        # Case-insensitive priority filtering
        priorities_lower = [p.lower() for p in priorities]
        recommendations = [r for r in recommendations if r['priority'].lower() in priorities_lower]
    
    return {
        'recommendations': recommendations,
        'total_recommendations': len(recommendations)
    }


def render() -> None:
    """Render the decision intelligence page with advanced animations."""
    st.markdown('<h1 class="main-title">Decision Intelligence</h1>', unsafe_allow_html=True)

    # Intro section
    st.markdown("""
    <p style="color: #94a3b8; font-size: 1.1rem;">
        This platform provides analytical insights and recommendations for decision support purposes. All recommendations should be reviewed by qualified personnel before implementation.
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
            priorities = filters.priority_filter()
            confidence = filters.confidence_filter()
    
    # Get data
    try:
        data = get_decision_intelligence_data(start_date, end_date, segments, priorities, confidence)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return
    
    st.markdown("---")
    
    # KPI Cards
    st.markdown("### Key Performance Indicators")
    
    col1, col2 = st.columns(2)
    
    with col1:
        kpi_cards.kpi_card(
            title="Total Recommendations",
            value=f"{data['total_recommendations']}",
            help_text="Total number of recommendations"
        )
    
    with col2:
        kpi_cards.kpi_card(
            title="Categories",
            value=f"{len(set(r['category'] for r in data['recommendations']))}",
            help_text="Number of recommendation categories"
        )
    
    st.markdown("---")
    
    # Recommendations List
    st.markdown("### Executive Recommendations")
    
    for i, rec in enumerate(data['recommendations'], 1):
        with st.expander(f"{i}. {rec['category']} - {rec['priority'].capitalize()} Priority", expanded=i==1):
            st.markdown(f"**Recommendation:** {rec['recommendation']}")
            st.markdown(f"**Expected Impact:** {rec['expected_impact']}")
            st.markdown("**Action Items:**")
            for action in rec['action_items']:
                st.markdown(f"- {action}")