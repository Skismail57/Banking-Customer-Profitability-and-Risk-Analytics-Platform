"""Reusable chart components using Plotly."""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, List, Dict, Any
import pandas as pd

from frontend.config import config


def line_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    color: Optional[str] = None,
    height: Optional[int] = None
) -> None:
    """Create a modern line chart with gradient styling and animations.

    Args:
        df: DataFrame with data
        x: Column name for x-axis
        y: Column name for y-axis
        title: Chart title
        color: Optional column name for color coding
        height: Chart height
    """
    if height is None:
        height = config.default_chart_height

    # Only include title if provided
    chart_title = title if title else None

    fig = px.line(
        df,
        x=x,
        y=y,
        color=color,
        title=chart_title,
        template="plotly_dark"
    )

    fig.update_traces(
        line=dict(width=4),
        selector=dict(mode='lines+markers'),
        hovertemplate='<b>%{x}</b><br>%{y}<extra></extra>'
    )

    fig.update_layout(
        height=height,
        plot_bgcolor='rgba(15, 23, 42, 0.8)',
        paper_bgcolor='rgba(15, 23, 42, 0.95)',
        font=dict(color='#f8fafc', family='Inter, system-ui, sans-serif'),
        title_font=dict(size=20, color='#f8fafc', family='Inter, system-ui, sans-serif'),
        xaxis=dict(
            gridcolor='rgba(99, 102, 241, 0.15)',
            showgrid=True,
            zeroline=False,
            tickfont=dict(color='#94a3b8')
        ),
        yaxis=dict(
            gridcolor='rgba(99, 102, 241, 0.15)',
            showgrid=True,
            zeroline=False,
            tickfont=dict(color='#94a3b8')
        ),
        hovermode='x unified',
        transition=dict(duration=500, easing='cubic-in-out'),
        margin=dict(l=50, r=50, t=60, b=50)
    )

    st.plotly_chart(fig, width="stretch")


def bar_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    color: Optional[str] = None,
    orientation: str = "v",
    height: Optional[int] = None,
    show_title: bool = True
) -> None:
    """Create a modern bar chart with gradient styling and animations.

    Args:
        df: DataFrame with data
        x: Column name for x-axis
        y: Column name for y-axis
        title: Chart title
        color: Optional column name for color coding
        orientation: Chart orientation (v or h)
        height: Chart height
        show_title: Whether to show chart title
    """
    if height is None:
        height = config.default_chart_height

    # Only include title if provided and show_title is True
    chart_title = title if title and show_title else None

    if orientation == "h":
        fig = px.bar(
            df,
            x=y,
            y=x,
            color=color,
            title=chart_title,
            orientation="h",
            template="plotly_dark",
            color_discrete_sequence=['#06b6d4', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444']
        )
    else:
        fig = px.bar(
            df,
            x=x,
            y=y,
            color=color,
            title=chart_title,
            template="plotly_dark",
            color_discrete_sequence=['#06b6d4', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444']
        )

    fig.update_traces(
        marker=dict(
            line=dict(width=0),
            pattern=dict(shape="")),
        selector=dict(type='bar'),
        hovertemplate='<b>%{x}</b><br>%{y}<extra></extra>'
    )

    fig.update_layout(
        height=height,
        plot_bgcolor='rgba(15, 23, 42, 0.8)',
        paper_bgcolor='rgba(15, 23, 42, 0.95)',
        font=dict(color='#f8fafc', family='Inter, system-ui, sans-serif'),
        title_font=dict(size=20, color='#f8fafc', family='Inter, system-ui, sans-serif'),
        xaxis=dict(
            gridcolor='rgba(99, 102, 241, 0.15)',
            showgrid=True,
            zeroline=False,
            tickfont=dict(color='#94a3b8')
        ),
        yaxis=dict(
            gridcolor='rgba(99, 102, 241, 0.15)',
            showgrid=True,
            zeroline=False,
            tickfont=dict(color='#94a3b8')
        ),
        hovermode='closest',
        transition=dict(duration=500, easing='cubic-in-out'),
        margin=dict(l=50, r=50, t=60, b=50),
        bargap=0.2
    )

    st.plotly_chart(fig, width="stretch")


def pie_chart(
    df: pd.DataFrame,
    names: str,
    values: str,
    title: str,
    height: Optional[int] = None
) -> None:
    """Create a modern pie chart with gradient styling and animations.

    Args:
        df: DataFrame with data
        names: Column name for pie slices
        values: Column name for slice values
        title: Chart title
        height: Chart height
    """
    if height is None:
        height = config.default_chart_height

    # Only include title if provided
    chart_title = title if title else None

    fig = px.pie(
        df,
        names=names,
        values=values,
        title=chart_title,
        template="plotly_dark",
        color_discrete_sequence=['#06b6d4', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#ec4899'],
        hole=0
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>%{value}<br>%{percent}<extra></extra>',
        marker=dict(line=dict(color='#1e293b', width=2))
    )

    fig.update_layout(
        height=height,
        plot_bgcolor='rgba(15, 23, 42, 0.8)',
        paper_bgcolor='rgba(15, 23, 42, 0.95)',
        font=dict(color='#f8fafc', family='Inter, system-ui, sans-serif'),
        title_font=dict(size=20, color='#f8fafc', family='Inter, system-ui, sans-serif'),
        transition=dict(duration=500, easing='cubic-in-out'),
        margin=dict(l=50, r=50, t=60, b=50),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02,
            font=dict(color='#94a3b8')
        )
    )

    st.plotly_chart(fig, width="stretch")


def donut_chart(
    df: pd.DataFrame,
    names: str,
    values: str,
    title: str,
    height: Optional[int] = None,
    show_title: bool = True
) -> None:
    """Create a modern donut chart with gradient styling and animations.

    Args:
        df: DataFrame with data
        names: Column name for donut slices
        values: Column name for slice values
        title: Chart title
        height: Chart height
        show_title: Whether to show chart title
    """
    if height is None:
        height = config.default_chart_height

    # Only include title if provided and show_title is True
    chart_title = title if title and show_title else None

    fig = px.pie(
        df,
        names=names,
        values=values,
        title=chart_title,
        hole=0.5,
        template="plotly_dark",
        color_discrete_sequence=['#06b6d4', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#ec4899']
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>%{value}<br>%{percent}<extra></extra>',
        marker=dict(line=dict(color='#1e293b', width=2))
    )

    fig.update_layout(
        height=height,
        plot_bgcolor='rgba(15, 23, 42, 0.8)',
        paper_bgcolor='rgba(15, 23, 42, 0.95)',
        font=dict(color='#f8fafc', family='Inter, system-ui, sans-serif'),
        title_font=dict(size=20, color='#f8fafc', family='Inter, system-ui, sans-serif'),
        transition=dict(duration=500, easing='cubic-in-out'),
        margin=dict(l=50, r=50, t=60, b=50),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02,
            font=dict(color='#94a3b8')
        )
    )

    st.plotly_chart(fig, width="stretch")


def scatter_plot(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    color: Optional[str] = None,
    size: Optional[str] = None,
    height: Optional[int] = None
) -> None:
    """Create a modern scatter plot with gradient styling and animations.

    Args:
        df: DataFrame with data
        x: Column name for x-axis
        y: Column name for y-axis
        title: Chart title
        color: Optional column name for color coding
        size: Optional column name for bubble size
        height: Chart height
    """
    if height is None:
        height = config.default_chart_height

    # Only include title if provided
    chart_title = title if title else None

    fig = px.scatter(
        df,
        x=x,
        y=y,
        color=color,
        size=size,
        title=chart_title,
        template="plotly_dark",
        color_discrete_sequence=['#06b6d4', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444']
    )

    fig.update_traces(
        marker=dict(
            line=dict(color='#1e293b', width=1),
            opacity=0.8
        ),
        selector=dict(mode='markers'),
        hovertemplate='<b>%{x}</b><br>%{y}<extra></extra>'
    )

    fig.update_layout(
        height=height,
        plot_bgcolor='rgba(15, 23, 42, 0.8)',
        paper_bgcolor='rgba(15, 23, 42, 0.95)',
        font=dict(color='#f8fafc', family='Inter, system-ui, sans-serif'),
        title_font=dict(size=20, color='#f8fafc', family='Inter, system-ui, sans-serif'),
        xaxis=dict(
            gridcolor='rgba(99, 102, 241, 0.15)',
            showgrid=True,
            zeroline=False,
            tickfont=dict(color='#94a3b8')
        ),
        yaxis=dict(
            gridcolor='rgba(99, 102, 241, 0.15)',
            showgrid=True,
            zeroline=False,
            tickfont=dict(color='#94a3b8')
        ),
        hovermode='closest',
        transition=dict(duration=500, easing='cubic-in-out'),
        margin=dict(l=50, r=50, t=60, b=50)
    )

    st.plotly_chart(fig, width="stretch")


def histogram(
    df: pd.DataFrame,
    x: str,
    title: str,
    color: Optional[str] = None,
    nbins: int = 30,
    height: Optional[int] = None
) -> None:
    """Create a modern histogram with gradient styling and animations.

    Args:
        df: DataFrame with data
        x: Column name for histogram
        title: Chart title
        color: Optional column name for color coding
        nbins: Number of bins
        height: Chart height
    """
    if height is None:
        height = config.default_chart_height

    # Only include title if provided
    chart_title = title if title else None

    fig = px.histogram(
        df,
        x=x,
        color=color,
        title=chart_title,
        nbins=nbins,
        template="plotly_dark",
        color_discrete_sequence=['#06b6d4', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444']
    )

    fig.update_traces(
        marker=dict(
            line=dict(color='#1e293b', width=1),
            pattern=dict(shape="")),
        selector=dict(type='histogram'),
        hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>',
        opacity=0.8
    )

    fig.update_layout(
        height=height,
        plot_bgcolor='rgba(15, 23, 42, 0.8)',
        paper_bgcolor='rgba(15, 23, 42, 0.95)',
        font=dict(color='#f8fafc', family='Inter, system-ui, sans-serif'),
        title_font=dict(size=20, color='#f8fafc', family='Inter, system-ui, sans-serif'),
        xaxis=dict(
            gridcolor='rgba(99, 102, 241, 0.15)',
            showgrid=True,
            zeroline=False,
            tickfont=dict(color='#94a3b8')
        ),
        yaxis=dict(
            gridcolor='rgba(99, 102, 241, 0.15)',
            showgrid=True,
            zeroline=False,
            tickfont=dict(color='#94a3b8')
        ),
        hovermode='closest',
        transition=dict(duration=500, easing='cubic-in-out'),
        margin=dict(l=50, r=50, t=60, b=50),
        bargap=0.1
    )

    st.plotly_chart(fig, width="stretch")


def box_plot(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    height: Optional[int] = None
) -> None:
    """Create a modern box plot with gradient styling and animations.

    Args:
        df: DataFrame with data
        x: Column name for x-axis (categories)
        y: Column name for y-axis (values)
        title: Chart title
        height: Chart height
    """
    if height is None:
        height = config.default_chart_height

    fig = px.box(
        df,
        x=x,
        y=y,
        title=title,
        template="plotly_dark",
        color_discrete_sequence=['#06b6d4', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444']
    )

    fig.update_traces(
        marker=dict(color='#06b6d4'),
        line=dict(color='#06b6d4'),
        hovertemplate='<b>%{x}</b><br>Median: %{median}<br>Q1: %{q1}<br>Q3: %{q3}<extra></extra>'
    )

    fig.update_layout(
        height=height,
        plot_bgcolor='rgba(15, 23, 42, 0.8)',
        paper_bgcolor='rgba(15, 23, 42, 0.95)',
        font=dict(color='#f8fafc', family='Inter, system-ui, sans-serif'),
        title_font=dict(size=20, color='#f8fafc', family='Inter, system-ui, sans-serif'),
        xaxis=dict(
            gridcolor='rgba(99, 102, 241, 0.15)',
            showgrid=True,
            zeroline=False,
            tickfont=dict(color='#94a3b8')
        ),
        yaxis=dict(
            gridcolor='rgba(99, 102, 241, 0.15)',
            showgrid=True,
            zeroline=False,
            tickfont=dict(color='#94a3b8')
        ),
        hovermode='closest',
        transition=dict(duration=500, easing='cubic-in-out'),
        margin=dict(l=50, r=50, t=60, b=50)
    )

    st.plotly_chart(fig, width="stretch")


def heatmap(
    df: pd.DataFrame,
    title: str,
    height: Optional[int] = None
) -> None:
    """Create a modern heatmap with gradient styling and animations.

    Args:
        df: DataFrame with correlation matrix
        title: Chart title
        height: Chart height
    """
    if height is None:
        height = config.default_chart_height

    fig = px.imshow(
        df,
        text_auto=True,
        aspect="auto",
        title=title,
        template="plotly_dark",
        color_continuous_scale='Cividis'
    )

    fig.update_traces(
        hovertemplate='<b>%{x}</b> vs <b>%{y}</b><br>Value: %{z}<extra></extra>',
        textfont=dict(color='#f8fafc', size=11)
    )

    fig.update_layout(
        height=height,
        plot_bgcolor='rgba(15, 23, 42, 0.8)',
        paper_bgcolor='rgba(15, 23, 42, 0.95)',
        font=dict(color='#f8fafc', family='Inter, system-ui, sans-serif'),
        title_font=dict(size=20, color='#f8fafc', family='Inter, system-ui, sans-serif'),
        xaxis=dict(
            tickfont=dict(color='#94a3b8'),
            showgrid=False
        ),
        yaxis=dict(
            tickfont=dict(color='#94a3b8'),
            showgrid=False
        ),
        transition=dict(duration=500, easing='cubic-in-out'),
        margin=dict(l=50, r=50, t=60, b=50)
    )

    st.plotly_chart(fig, width="stretch")


def funnel_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    height: Optional[int] = None
) -> None:
    """Create a modern funnel chart with gradient styling and animations.

    Args:
        df: DataFrame with data
        x: Column name for funnel stages
        y: Column name for values
        title: Chart title
        height: Chart height
    """
    if height is None:
        height = config.default_chart_height

    fig = px.funnel(
        df,
        x=x,
        y=y,
        title=title,
        template="plotly_dark",
        color_discrete_sequence=['#06b6d4', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444']
    )

    fig.update_traces(
        hovertemplate='<b>%{y}</b><br>Value: %{x}<extra></extra>',
        marker=dict(line=dict(color='#1e293b', width=1))
    )

    fig.update_layout(
        height=height,
        plot_bgcolor='rgba(15, 23, 42, 0.8)',
        paper_bgcolor='rgba(15, 23, 42, 0.95)',
        font=dict(color='#f8fafc', family='Inter, system-ui, sans-serif'),
        title_font=dict(size=20, color='#f8fafc', family='Inter, system-ui, sans-serif'),
        transition=dict(duration=500, easing='cubic-in-out'),
        margin=dict(l=50, r=50, t=60, b=50)
    )

    st.plotly_chart(fig, width="stretch")


def gauge_chart(
    value: float,
    title: str,
    min_value: float = 0,
    max_value: float = 100,
    height: Optional[int] = None
) -> None:
    """Create a modern gauge chart with gradient styling and animations.

    Args:
        value: Gauge value
        title: Chart title
        min_value: Minimum value
        max_value: Maximum value
        height: Chart height
    """
    if height is None:
        height = config.default_chart_height

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        title={"text": title, "font": {"color": "#f8fafc", "size": 16, "family": "Inter, system-ui, sans-serif"}},
        delta={"reference": max_value * 0.5},
        gauge={
            "axis": {"range": [min_value, max_value], "tickcolor": "#94a3b8", "tickwidth": 1},
            "bar": {"color": "#06b6d4", "thickness": 0.3},
            "steps": [
                {"range": [min_value, max_value * 0.33], "color": "rgba(239, 68, 68, 0.2)"},
                {"range": [max_value * 0.33, max_value * 0.66], "color": "rgba(245, 158, 11, 0.2)"},
                {"range": [max_value * 0.66, max_value], "color": "rgba(16, 185, 129, 0.2)"},
            ],
            "threshold": {
                "line": {"color": "#ef4444", "width": 4},
                "thickness": 0.75,
                "value": max_value * 0.9
            }
        }
    ))

    fig.update_layout(
        height=height,
        plot_bgcolor='rgba(15, 23, 42, 0.8)',
        paper_bgcolor='rgba(15, 23, 42, 0.95)',
        font=dict(color='#f8fafc', family='Inter, system-ui, sans-serif'),
        margin=dict(l=50, r=50, t=60, b=50),
        transition=dict(duration=500, easing='cubic-in-out')
    )

    st.plotly_chart(fig, width="stretch")


def risk_distribution_chart(
    df: pd.DataFrame,
    risk_column: str = "risk_level",
    title: str = "Risk Distribution",
    height: Optional[int] = None
) -> None:
    """Create a modern risk distribution donut chart with risk colors and animations.

    Args:
        df: DataFrame with risk data
        risk_column: Column name for risk levels
        title: Chart title
        height: Chart height
    """
    if height is None:
        height = config.default_chart_height

    risk_counts = df[risk_column].value_counts().reset_index()
    risk_counts.columns = ["Risk Level", "Count"]

    # Risk-specific colors
    risk_colors_map = {
        "Low": "#10b981",
        "Medium": "#f59e0b",
        "High": "#ef4444",
        "Critical": "#7c3aed"
    }
    colors = [risk_colors_map.get(level, "#64748b") for level in risk_counts["Risk Level"]]

    # Only include title if provided
    chart_title = title if title else None

    fig = px.pie(
        risk_counts,
        names="Risk Level",
        values="Count",
        title=chart_title,
        hole=0.5,
        template="plotly_dark"
    )

    fig.update_traces(
        marker=dict(colors=colors, line=dict(color='#1e293b', width=2)),
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>'
    )

    fig.update_layout(
        height=height,
        plot_bgcolor='rgba(15, 23, 42, 0.8)',
        paper_bgcolor='rgba(15, 23, 42, 0.95)',
        font=dict(color='#f8fafc', family='Inter, system-ui, sans-serif'),
        title_font=dict(size=20, color='#f8fafc', family='Inter, system-ui, sans-serif'),
        transition=dict(duration=500, easing='cubic-in-out'),
        margin=dict(l=50, r=50, t=60, b=50),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02,
            font=dict(color='#94a3b8')
        )
    )

    st.plotly_chart(fig, width="stretch")


def area_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    color: Optional[str] = None,
    height: Optional[int] = None
) -> None:
    """Create a modern area chart with gradient styling and animations.

    Args:
        df: DataFrame with data
        x: Column name for x-axis
        y: Column name for y-axis
        title: Chart title
        color: Optional column name for color coding
        height: Chart height
    """
    if height is None:
        height = config.default_chart_height

    chart_title = title if title else None

    fig = px.area(
        df,
        x=x,
        y=y,
        color=color,
        title=chart_title,
        template="plotly_dark",
        color_discrete_sequence=['#06b6d4', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444']
    )

    fig.update_traces(
        fill='tozeroy',
        line=dict(width=3),
        hovertemplate='<b>%{x}</b><br>%{y}<extra></extra>',
        opacity=0.7
    )

    fig.update_layout(
        height=height,
        plot_bgcolor='rgba(15, 23, 42, 0.8)',
        paper_bgcolor='rgba(15, 23, 42, 0.95)',
        font=dict(color='#f8fafc', family='Inter, system-ui, sans-serif'),
        title_font=dict(size=20, color='#f8fafc', family='Inter, system-ui, sans-serif'),
        xaxis=dict(
            gridcolor='rgba(99, 102, 241, 0.15)',
            showgrid=True,
            zeroline=False,
            tickfont=dict(color='#94a3b8')
        ),
        yaxis=dict(
            gridcolor='rgba(99, 102, 241, 0.15)',
            showgrid=True,
            zeroline=False,
            tickfont=dict(color='#94a3b8')
        ),
        hovermode='x unified',
        transition=dict(duration=500, easing='cubic-in-out'),
        margin=dict(l=50, r=50, t=60, b=50)
    )

    st.plotly_chart(fig, width="stretch")


def radar_chart(
    df: pd.DataFrame,
    categories: list,
    values: str,
    title: str,
    group: Optional[str] = None,
    height: Optional[int] = None
) -> None:
    """Create a modern radar/spider chart for multi-dimensional comparison.

    Args:
        df: DataFrame with data
        categories: List of category columns for radar axes
        values: Column name for values
        title: Chart title
        group: Optional column name for grouping
        height: Chart height
    """
    if height is None:
        height = config.default_chart_height

    chart_title = title if title else None

    fig = go.Figure()

    if group:
        for group_val in df[group].unique():
            group_df = df[df[group] == group_val]
            fig.add_trace(go.Scatterpolar(
                r=group_df[values].values,
                theta=categories,
                fill='toself',
                name=str(group_val),
                line=dict(color='#06b6d4' if group_val == df[group].unique()[0] else '#8b5cf6',
                         width=2),
                opacity=0.6
            ))
    else:
        fig.add_trace(go.Scatterpolar(
            r=df[values].values,
            theta=categories,
            fill='toself',
            name='Values',
            line=dict(color='#06b6d4', width=2),
            opacity=0.6
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                gridcolor='rgba(99, 102, 241, 0.15)',
                tickfont=dict(color='#94a3b8')
            ),
            angularaxis=dict(
                gridcolor='rgba(99, 102, 241, 0.15)',
                tickfont=dict(color='#94a3b8')
            ),
            bgcolor='rgba(15, 23, 42, 0.8)'
        ),
        height=height,
        title=chart_title,
        title_font=dict(size=20, color='#f8fafc', family='Inter, system-ui, sans-serif'),
        paper_bgcolor='rgba(15, 23, 42, 0.95)',
        font=dict(color='#f8fafc', family='Inter, system-ui, sans-serif'),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02,
            font=dict(color='#94a3b8')
        ),
        transition=dict(duration=500, easing='cubic-in-out'),
        margin=dict(l=50, r=50, t=60, b=50)
    )

    st.plotly_chart(fig, width="stretch")


def waterfall_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    measure: Optional[str] = None,
    height: Optional[int] = None
) -> None:
    """Create a modern waterfall chart for profit/revenue breakdown.

    Args:
        df: DataFrame with data
        x: Column name for x-axis (categories)
        y: Column name for y-axis (values)
        title: Chart title
        measure: Optional column for measure type (relative, absolute, total)
        height: Chart height
    """
    if height is None:
        height = config.default_chart_height

    chart_title = title if title else None

    if measure:
        fig = go.Figure(go.Waterfall(
            name="Waterfall",
            orientation="v",
            x=df[x],
            y=df[y],
            measure=df[measure],
            text=df[y],
            textposition="outside",
            textfont=dict(color='#f8fafc'),
            decreasing=dict(marker=dict(color='#ef4444')),
            increasing=dict(marker=dict(color='#10b981')),
            totals=dict(marker=dict(color='#06b6d4'))
        ))
    else:
        fig = go.Figure(go.Waterfall(
            name="Waterfall",
            orientation="v",
            x=df[x],
            y=df[y],
            text=df[y],
            textposition="outside",
            textfont=dict(color='#f8fafc'),
            decreasing=dict(marker=dict(color='#ef4444')),
            increasing=dict(marker=dict(color='#10b981')),
            totals=dict(marker=dict(color='#06b6d4'))
        ))

    fig.update_layout(
        height=height,
        title=chart_title,
        title_font=dict(size=20, color='#f8fafc', family='Inter, system-ui, sans-serif'),
        plot_bgcolor='rgba(15, 23, 42, 0.8)',
        paper_bgcolor='rgba(15, 23, 42, 0.95)',
        font=dict(color='#f8fafc', family='Inter, system-ui, sans-serif'),
        xaxis=dict(
            gridcolor='rgba(99, 102, 241, 0.15)',
            showgrid=True,
            tickfont=dict(color='#94a3b8')
        ),
        yaxis=dict(
            gridcolor='rgba(99, 102, 241, 0.15)',
            showgrid=True,
            tickfont=dict(color='#94a3b8')
        ),
        transition=dict(duration=500, easing='cubic-in-out'),
        margin=dict(l=50, r=50, t=60, b=50)
    )

    st.plotly_chart(fig, width="stretch")


def bullet_chart(
    value: float,
    target: float,
    ranges: list,
    title: str,
    height: Optional[int] = None
) -> None:
    """Create a modern bullet chart for KPI performance against targets.

    Args:
        value: Current value
        target: Target value
        ranges: List of range values [low, medium, high]
        title: Chart title
        height: Chart height
    """
    if height is None:
        height = 250

    fig = go.Figure(go.Indicator(
        mode="number+gauge+delta",
        value=value,
        delta={"reference": target},
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, "font": {"color": "#f8fafc", "size": 16, "family": "Inter, system-ui, sans-serif"}},
        gauge={
            'axis': {'range': [None, max(ranges) * 1.2], 'tickcolor': '#94a3b8'},
            'bar': {'color': '#06b6d4'},
            'steps': [
                {'range': [0, ranges[0]], 'color': 'rgba(239, 68, 68, 0.2)'},
                {'range': [ranges[0], ranges[1]], 'color': 'rgba(245, 158, 11, 0.2)'},
                {'range': [ranges[1], ranges[2]], 'color': 'rgba(16, 185, 129, 0.2)'},
            ],
            'threshold': {
                'line': {'color': '#ef4444', 'width': 4},
                'thickness': 0.75,
                'value': target
            }
        }
    ))

    fig.update_layout(
        height=height,
        plot_bgcolor='rgba(15, 23, 42, 0.8)',
        paper_bgcolor='rgba(15, 23, 42, 0.95)',
        font=dict(color='#f8fafc', family='Inter, system-ui, sans-serif'),
        margin=dict(l=50, r=50, t=60, b=50),
        transition=dict(duration=500, easing='cubic-in-out')
    )

    st.plotly_chart(fig, width="stretch")


def sparkline(
    values: list,
    height: int = 100,
    color: str = '#06b6d4'
) -> None:
    """Create a sparkline for trend indicators in KPI cards.

    Args:
        values: List of values
        height: Chart height
        color: Line color
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        y=values,
        mode='lines',
        line=dict(color=color, width=2),
        fill='tozeroy',
        fillcolor=f'{color}33',
        hoverinfo='skip'
    ))

    fig.update_layout(
        height=height,
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor='transparent',
        paper_bgcolor='transparent',
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        showlegend=False
    )

    st.plotly_chart(fig, width="stretch")


def treemap(
    df: pd.DataFrame,
    path: list,
    values: str,
    title: str,
    color: Optional[str] = None,
    height: Optional[int] = None
) -> None:
    """Create a modern treemap for hierarchical data visualization.

    Args:
        df: DataFrame with data
        path: List of column names for hierarchy
        values: Column name for values
        title: Chart title
        color: Optional column name for color coding
        height: Chart height
    """
    if height is None:
        height = config.default_chart_height

    chart_title = title if title else None

    fig = px.treemap(
        df,
        path=path,
        values=values,
        title=chart_title,
        color=color,
        color_continuous_scale='Cividis',
        template="plotly_dark"
    )

    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>Value: %{value}<extra></extra>',
        textfont=dict(color='#f8fafc', size=12)
    )

    fig.update_layout(
        height=height,
        plot_bgcolor='rgba(15, 23, 42, 0.8)',
        paper_bgcolor='rgba(15, 23, 42, 0.95)',
        font=dict(color='#f8fafc', family='Inter, system-ui, sans-serif'),
        title_font=dict(size=20, color='#f8fafc', family='Inter, system-ui, sans-serif'),
        transition=dict(duration=500, easing='cubic-in-out'),
        margin=dict(l=50, r=50, t=60, b=50)
    )

    st.plotly_chart(fig, width="stretch")


def sunburst_chart(
    df: pd.DataFrame,
    path: list,
    values: str,
    title: str,
    height: Optional[int] = None
) -> None:
    """Create a modern sunburst chart for hierarchical customer segmentation.

    Args:
        df: DataFrame with data
        path: List of column names for hierarchy
        values: Column name for values
        title: Chart title
        height: Chart height
    """
    if height is None:
        height = config.default_chart_height

    chart_title = title if title else None

    fig = px.sunburst(
        df,
        path=path,
        values=values,
        title=chart_title,
        template="plotly_dark",
        color_discrete_sequence=['#06b6d4', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#ec4899']
    )

    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>Value: %{value}<extra></extra>',
        textfont=dict(color='#f8fafc', size=11)
    )

    fig.update_layout(
        height=height,
        plot_bgcolor='rgba(15, 23, 42, 0.8)',
        paper_bgcolor='rgba(15, 23, 42, 0.95)',
        font=dict(color='#f8fafc', family='Inter, system-ui, sans-serif'),
        title_font=dict(size=20, color='#f8fafc', family='Inter, system-ui, sans-serif'),
        transition=dict(duration=500, easing='cubic-in-out'),
        margin=dict(l=50, r=50, t=60, b=50)
    )

    st.plotly_chart(fig, width="stretch")


def violin_plot(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    height: Optional[int] = None
) -> None:
    """Create a modern violin plot for distribution analysis.

    Args:
        df: DataFrame with data
        x: Column name for x-axis (categories)
        y: Column name for y-axis (values)
        title: Chart title
        height: Chart height
    """
    if height is None:
        height = config.default_chart_height

    fig = px.violin(
        df,
        x=x,
        y=y,
        title=title,
        template="plotly_dark",
        color_discrete_sequence=['#06b6d4', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444']
    )

    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>Median: %{median}<extra></extra>',
        marker=dict(line=dict(color='#1e293b', width=1)),
        opacity=0.8
    )

    fig.update_layout(
        height=height,
        plot_bgcolor='rgba(15, 23, 42, 0.8)',
        paper_bgcolor='rgba(15, 23, 42, 0.95)',
        font=dict(color='#f8fafc', family='Inter, system-ui, sans-serif'),
        title_font=dict(size=20, color='#f8fafc', family='Inter, system-ui, sans-serif'),
        xaxis=dict(
            gridcolor='rgba(99, 102, 241, 0.15)',
            showgrid=True,
            tickfont=dict(color='#94a3b8')
        ),
        yaxis=dict(
            gridcolor='rgba(99, 102, 241, 0.15)',
            showgrid=True,
            tickfont=dict(color='#94a3b8')
        ),
        hovermode='closest',
        transition=dict(duration=500, easing='cubic-in-out'),
        margin=dict(l=50, r=50, t=60, b=50)
    )

    st.plotly_chart(fig, width="stretch")


def dual_axis_chart(
    df: pd.DataFrame,
    x: str,
    y1: str,
    y2: str,
    title: str,
    y1_name: str = "Left Axis",
    y2_name: str = "Right Axis",
    height: Optional[int] = None
) -> None:
    """Create a dual-axis chart for comparing two metrics.

    Args:
        df: DataFrame with data
        x: Column name for x-axis
        y1: Column name for left y-axis
        y2: Column name for right y-axis
        title: Chart title
        y1_name: Name for left axis
        y2_name: Name for right axis
        height: Chart height
    """
    if height is None:
        height = config.default_chart_height

    chart_title = title if title else None

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df[x],
        y=df[y1],
        name=y1_name,
        line=dict(color='#06b6d4', width=3),
        yaxis='y'
    ))

    fig.add_trace(go.Scatter(
        x=df[x],
        y=df[y2],
        name=y2_name,
        line=dict(color='#8b5cf6', width=3),
        yaxis='y2'
    ))

    fig.update_layout(
        height=height,
        title=chart_title,
        title_font=dict(size=20, color='#f8fafc', family='Inter, system-ui, sans-serif'),
        plot_bgcolor='rgba(15, 23, 42, 0.8)',
        paper_bgcolor='rgba(15, 23, 42, 0.95)',
        font=dict(color='#f8fafc', family='Inter, system-ui, sans-serif'),
        xaxis=dict(
            gridcolor='rgba(99, 102, 241, 0.15)',
            showgrid=True,
            tickfont=dict(color='#94a3b8')
        ),
        yaxis=dict(
            title=y1_name,
            gridcolor='rgba(99, 102, 241, 0.15)',
            showgrid=True,
            tickfont=dict(color='#94a3b8'),
            titlefont=dict(color='#06b6d4')
        ),
        yaxis2=dict(
            title=y2_name,
            gridcolor='rgba(99, 102, 241, 0.15)',
            showgrid=False,
            tickfont=dict(color='#94a3b8'),
            titlefont=dict(color='#8b5cf6'),
            overlaying='y',
            side='right'
        ),
        hovermode='x unified',
        transition=dict(duration=500, easing='cubic-in-out'),
        margin=dict(l=50, r=50, t=60, b=50),
        legend=dict(
            orientation="top",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(color='#94a3b8')
        )
    )

    st.plotly_chart(fig, width="stretch")


def stacked_bar_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    color: str,
    title: str,
    orientation: str = "v",
    height: Optional[int] = None
) -> None:
    """Create a stacked bar chart for component analysis.

    Args:
        df: DataFrame with data
        x: Column name for x-axis
        y: Column name for y-axis
        color: Column name for color stacking
        title: Chart title
        orientation: Chart orientation (v or h)
        height: Chart height
    """
    if height is None:
        height = config.default_chart_height

    chart_title = title if title else None

    if orientation == "h":
        fig = px.bar(
            df,
            x=y,
            y=x,
            color=color,
            title=chart_title,
            orientation="h",
            template="plotly_dark",
            color_discrete_sequence=['#06b6d4', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444']
        )
    else:
        fig = px.bar(
            df,
            x=x,
            y=y,
            color=color,
            title=chart_title,
            template="plotly_dark",
            color_discrete_sequence=['#06b6d4', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444']
        )

    fig.update_traces(
        marker=dict(line=dict(width=0)),
        hovertemplate='<b>%{x}</b><br>%{y}<extra></extra>'
    )

    fig.update_layout(
        barmode='stack',
        height=height,
        plot_bgcolor='rgba(15, 23, 42, 0.8)',
        paper_bgcolor='rgba(15, 23, 42, 0.95)',
        font=dict(color='#f8fafc', family='Inter, system-ui, sans-serif'),
        title_font=dict(size=20, color='#f8fafc', family='Inter, system-ui, sans-serif'),
        xaxis=dict(
            gridcolor='rgba(99, 102, 241, 0.15)',
            showgrid=True,
            tickfont=dict(color='#94a3b8')
        ),
        yaxis=dict(
            gridcolor='rgba(99, 102, 241, 0.15)',
            showgrid=True,
            tickfont=dict(color='#94a3b8')
        ),
        hovermode='closest',
        transition=dict(duration=500, easing='cubic-in-out'),
        margin=dict(l=50, r=50, t=60, b=50),
        bargap=0.2
    )

    st.plotly_chart(fig, width="stretch")
