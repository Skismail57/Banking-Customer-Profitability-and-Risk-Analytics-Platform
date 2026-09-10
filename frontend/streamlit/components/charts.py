"""Neon Plotly chart theme system."""

import plotly.graph_objects as go
import plotly.express as px
from typing import Optional, List, Dict, Any
import pandas as pd
from frontend.streamlit.theme import neon_theme


def apply_neon_chart_theme(fig: go.Figure, height: Optional[int] = None) -> go.Figure:
    """Apply centralized neon theme to a Plotly figure.

    Args:
        fig: Plotly figure to theme
        height: Optional chart height

    Returns:
        Themed Plotly figure
    """
    if height is None:
        height = neon_theme.layout.chart_height_base

    # Apply dark neon theme
    fig.update_layout(
        # Backgrounds
        plot_bgcolor='rgba(12, 18, 24, 0.8)',
        paper_bgcolor='rgba(12, 18, 24, 0.6)',

        # Typography
        font=dict(
            family=neon_theme.typography.font_family_base,
            color=neon_theme.colors.white,
            size=14
        ),

        # Title styling
        title_font=dict(
            size=18,
            color=neon_theme.colors.white,
            weight=600
        ),

        # Axes
        xaxis=dict(
            gridcolor='rgba(0, 245, 255, 0.1)',
            zerolinecolor='rgba(0, 245, 255, 0.2)',
            tickcolor=neon_theme.colors.muted,
            tickfont=dict(color=neon_theme.colors.muted),
            titlefont=dict(color=neon_theme.colors.white_dim)
        ),
        yaxis=dict(
            gridcolor='rgba(0, 245, 255, 0.1)',
            zerolinecolor='rgba(0, 245, 255, 0.2)',
            tickcolor=neon_theme.colors.muted,
            tickfont=dict(color=neon_theme.colors.muted),
            titlefont=dict(color=neon_theme.colors.white_dim)
        ),

        # Legend
        legend=dict(
            bgcolor='rgba(12, 18, 24, 0.8)',
            bordercolor='rgba(0, 245, 255, 0.2)',
            borderwidth=1,
            font=dict(color=neon_theme.colors.white),
            orientation='v',
            yanchor='top',
            y=0.99,
            xanchor='left',
            x=0.01
        ),

        # Margins
        margin=dict(l=60, r=30, t=60, b=60),

        # Height
        height=height,

        # Hover
        hovermode='x unified'
    )

    return fig


def get_neon_color_sequence() -> List[str]:
    """Get the neon color sequence for charts."""
    return [
        neon_theme.colors.cyan,
        neon_theme.colors.purple,
        neon_theme.colors.magenta,
        neon_theme.colors.green,
        neon_theme.colors.orange,
        neon_theme.colors.yellow,
        neon_theme.colors.red
    ]


def neon_line_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    color: Optional[str] = None,
    height: Optional[int] = None,
    show_area: bool = False
) -> go.Figure:
    """Create a neon-styled line chart.

    Args:
        df: DataFrame with data
        x: Column name for x-axis
        y: Column name for y-axis
        title: Chart title
        color: Optional column name for color coding
        height: Chart height
        show_area: Whether to show area fill

    Returns:
        Plotly figure
    """
    fig = px.line(
        df,
        x=x,
        y=y,
        color=color,
        title=title,
        color_discrete_sequence=get_neon_color_sequence()
    )

    # Update traces for neon effect
    fig.update_traces(
        line=dict(width=3),
        selector=dict(mode='lines')
    )

    if show_area:
        fig.update_traces(
            fill='tozeroy',
            fillcolor=f'rgba(0, 245, 255, 0.1)',
            selector=dict(mode='lines')
        )

    return apply_neon_chart_theme(fig, height)


def neon_bar_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    color: Optional[str] = None,
    orientation: str = "v",
    height: Optional[int] = None
) -> go.Figure:
    """Create a neon-styled bar chart.

    Args:
        df: DataFrame with data
        x: Column name for x-axis
        y: Column name for y-axis
        title: Chart title
        color: Optional column name for color coding
        orientation: Chart orientation (v or h)
        height: Chart height

    Returns:
        Plotly figure
    """
    if orientation == "h":
        fig = px.bar(
            df,
            x=y,
            y=x,
            color=color,
            title=title,
            orientation="h",
            color_discrete_sequence=get_neon_color_sequence()
        )
    else:
        fig = px.bar(
            df,
            x=x,
            y=y,
            color=color,
            title=title,
            color_discrete_sequence=get_neon_color_sequence()
        )

    # Update traces for neon effect
    fig.update_traces(
        marker=dict(
            line=dict(width=0),
            cornerradius=4
        ),
        selector=dict(type='bar')
    )

    return apply_neon_chart_theme(fig, height)


def neon_donut_chart(
    df: pd.DataFrame,
    names: str,
    values: str,
    title: str,
    height: Optional[int] = None
) -> go.Figure:
    """Create a neon-styled donut chart.

    Args:
        df: DataFrame with data
        names: Column name for donut slices
        values: Column name for slice values
        title: Chart title
        height: Chart height

    Returns:
        Plotly figure
    """
    fig = px.pie(
        df,
        names=names,
        values=values,
        title=title,
        hole=0.4,
        color_discrete_sequence=get_neon_color_sequence()
    )

    # Update traces for neon effect
    fig.update_traces(
        marker=dict(
            line=dict(color='rgba(12, 18, 24, 0.8)', width=2),
            cornerradius=4
        ),
        textposition='inside',
        textinfo='percent+label'
    )

    return apply_neon_chart_theme(fig, height)


def neon_scatter_plot(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    color: Optional[str] = None,
    size: Optional[str] = None,
    height: Optional[int] = None
) -> go.Figure:
    """Create a neon-styled scatter plot.

    Args:
        df: DataFrame with data
        x: Column name for x-axis
        y: Column name for y-axis
        title: Chart title
        color: Optional column name for color coding
        size: Optional column name for bubble size
        height: Chart height

    Returns:
        Plotly figure
    """
    fig = px.scatter(
        df,
        x=x,
        y=y,
        color=color,
        size=size,
        title=title,
        color_discrete_sequence=get_neon_color_sequence()
    )

    # Update traces for neon effect
    fig.update_traces(
        marker=dict(
            line=dict(color='rgba(12, 18, 24, 0.8)', width=1),
            opacity=0.8
        ),
        selector=dict(mode='markers')
    )

    return apply_neon_chart_theme(fig, height)


def neon_histogram(
    df: pd.DataFrame,
    x: str,
    title: str,
    color: Optional[str] = None,
    nbins: int = 30,
    height: Optional[int] = None
) -> go.Figure:
    """Create a neon-styled histogram.

    Args:
        df: DataFrame with data
        x: Column name for histogram
        title: Chart title
        color: Optional column name for color coding
        nbins: Number of bins
        height: Chart height

    Returns:
        Plotly figure
    """
    fig = px.histogram(
        df,
        x=x,
        color=color,
        title=title,
        nbins=nbins,
        color_discrete_sequence=get_neon_color_sequence()
    )

    # Update traces for neon effect
    fig.update_traces(
        marker=dict(
            line=dict(color='rgba(12, 18, 24, 0.8)', width=1),
            cornerradius=4
        ),
        opacity=0.8,
        selector=dict(type='histogram')
    )

    return apply_neon_chart_theme(fig, height)


def neon_gauge_chart(
    value: float,
    title: str,
    min_value: float = 0,
    max_value: float = 100,
    height: Optional[int] = None
) -> go.Figure:
    """Create a neon-styled gauge chart.

    Args:
        value: Gauge value
        title: Chart title
        min_value: Minimum value
        max_value: Maximum value
        height: Chart height

    Returns:
        Plotly figure
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title, "font": {"color": neon_theme.colors.white}},
        gauge={
            "axis": {
                "range": [min_value, max_value],
                "tickcolor": neon_theme.colors.muted,
                "tickfont": {"color": neon_theme.colors.muted}
            },
            "bar": {"color": neon_theme.colors.cyan},
            "steps": [
                {"range": [min_value, max_value * 0.33], "color": "rgba(0, 255, 156, 0.1)"},
                {"range": [max_value * 0.33, max_value * 0.66], "color": "rgba(255, 138, 0, 0.1)"},
                {"range": [max_value * 0.66, max_value], "color": "rgba(255, 49, 88, 0.1)"},
            ],
            "threshold": {
                "line": {"color": neon_theme.colors.red, "width": 4},
                "thickness": 0.75,
                "value": max_value * 0.8
            }
        }
    ))

    return apply_neon_chart_theme(fig, height)


def neon_risk_distribution_chart(
    df: pd.DataFrame,
    risk_column: str = "risk_level",
    title: str = "Risk Distribution",
    height: Optional[int] = None
) -> go.Figure:
    """Create a neon-styled risk distribution donut chart with semantic colors.

    Args:
        df: DataFrame with risk data
        risk_column: Column name for risk levels
        title: Chart title
        height: Chart height

    Returns:
        Plotly figure
    """
    risk_counts = df[risk_column].value_counts().reset_index()
    risk_counts.columns = ["Risk Level", "Count"]

    # Semantic risk colors
    risk_colors = {
        "low": neon_theme.colors.green,
        "medium": neon_theme.colors.orange,
        "high": neon_theme.colors.red,
        "critical": neon_theme.colors.red
    }

    colors = [risk_colors.get(level.lower(), neon_theme.colors.cyan) for level in risk_counts["Risk Level"]]

    fig = px.pie(
        risk_counts,
        names="Risk Level",
        values="Count",
        title=title,
        hole=0.4
    )

    fig.update_traces(
        marker=dict(colors=colors, line=dict(color='rgba(12, 18, 24, 0.8)', width=2)),
        textposition='inside',
        textinfo='percent+label'
    )

    return apply_neon_chart_theme(fig, height)
