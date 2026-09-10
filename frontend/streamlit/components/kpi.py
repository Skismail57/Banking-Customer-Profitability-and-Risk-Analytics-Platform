"""Neon KPI card components with advanced styling."""

import streamlit as st
from typing import Optional, Any, Dict
from frontend.streamlit.theme import neon_theme


def neon_kpi_card(
    title: str,
    value: Any,
    delta: Optional[float] = None,
    delta_color: str = "normal",
    description: Optional[str] = None,
    icon: Optional[str] = None,
    variant: str = "default",
    sparkline: Optional[list] = None,
    help_text: Optional[str] = None
) -> None:
    """Create a neon-styled KPI card with advanced features.

    Args:
        title: KPI title
        value: KPI value
        delta: Optional delta value
        delta_color: Color for delta (normal, inverse, off)
        description: Optional description text
        icon: Optional icon (emoji or character)
        variant: Card variant (default, cyan, purple, green, orange, red)
        sparkline: Optional list of values for sparkline
        help_text: Optional help tooltip
    """
    # Determine color class
    color_class = f"{variant}" if variant != "default" else ""

    # Format delta
    delta_html = ""
    if delta is not None:
        delta_sign = "↑" if delta >= 0 else "↓"
        delta_class = "positive" if delta >= 0 else "negative"
        delta_html = f'<div class="kpi-card-delta {delta_class}">{delta_sign} {abs(delta):.1f}%</div>'

    # Icon HTML
    icon_html = f'<div style="font-size: 1.5rem; margin-bottom: 0.5rem;">{icon}</div>' if icon else ""

    # Sparkline (simplified - would need Plotly for full implementation)
    sparkline_html = ""
    if sparkline:
        sparkline_html = f'<div style="height: 30px; margin-top: 0.5rem; opacity: 0.7;">[Sparkline: {len(sparkline)} points]</div>'

    card_html = f"""
    <div class="kpi-card {color_class}">
        {icon_html}
        <div class="kpi-card-label">{title}</div>
        <div class="kpi-card-value">{value}</div>
        {delta_html}
        {sparkline_html}
        {f'<div class="kpi-card-description">{description}</div>' if description else ''}
    </div>
    """

    st.markdown(card_html, unsafe_allow_html=True)

    if help_text:
        st.caption(help_text)


def neon_kpi_grid(
    kpis: Dict[str, Dict[str, Any]],
    columns: int = 4
) -> None:
    """Create a grid of neon KPI cards with staggered animation.

    Args:
        kpis: Dictionary of KPIs with keys as titles and values as config dicts
        columns: Number of columns in the grid
    """
    cols = st.columns(columns)

    for i, (title, config) in enumerate(kpis.items()):
        with cols[i % columns]:
            # Add staggered animation delay
            delay = i * 0.1
            st.markdown(f'<div style="animation: fadeInUp 0.6s ease-out {delay}s both;">', unsafe_allow_html=True)

            neon_kpi_card(
                title=title,
                value=config.get("value"),
                delta=config.get("delta"),
                delta_color=config.get("delta_color", "normal"),
                description=config.get("description"),
                icon=config.get("icon"),
                variant=config.get("variant", "default"),
                sparkline=config.get("sparkline"),
                help_text=config.get("help_text")
            )

            st.markdown('</div>', unsafe_allow_html=True)


def neon_metric_card(
    label: str,
    value: Any,
    delta: Optional[float] = None,
    delta_color: str = "normal",
    color: str = "cyan"
) -> None:
    """Create a simple neon metric card similar to st.metric but styled.

    Args:
        label: Metric label
        value: Metric value
        delta: Optional delta value
        delta_color: Color for delta
        color: Accent color (cyan, purple, green, orange, red)
    """
    # Get color from theme
    color_map = {
        "cyan": neon_theme.colors.cyan,
        "purple": neon_theme.colors.purple,
        "green": neon_theme.colors.green,
        "orange": neon_theme.colors.orange,
        "red": neon_theme.colors.red
    }
    accent_color = color_map.get(color, neon_theme.colors.cyan)

    # Format delta
    delta_html = ""
    if delta is not None:
        delta_sign = "↑" if delta >= 0 else "↓"
        delta_color_style = neon_theme.colors.green if delta >= 0 else neon_theme.colors.red
        delta_html = f'<span style="color: {delta_color_style}; font-weight: 600;">{delta_sign} {abs(delta):.1f}%</span>'

    metric_html = f"""
    <div style="
        background: linear-gradient(135deg, rgba(12, 18, 24, 0.8) 0%, rgba(16, 24, 32, 0.8) 100%);
        border: 1px solid rgba({accent_color}, 0.2);
        border-radius: {neon_theme.borders.radius_lg};
        padding: 1.25rem;
        margin: 0.5rem 0;
        backdrop-filter: blur(20px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        transition: all {neon_theme.animation.duration_base} {neon_theme.animation.ease_in_out};
    ">
        <div style="
            font-size: 0.875rem;
            color: {neon_theme.colors.muted};
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        ">{label}</div>
        <div style="
            font-size: 1.75rem;
            font-weight: 700;
            color: {neon_theme.colors.white};
            margin: 0.5rem 0;
        ">{value}</div>
        {f'<div style="font-size: 0.875rem; margin-top: 0.25rem;">{delta_html}</div>' if delta_html else ''}
    </div>
    """

    st.markdown(metric_html, unsafe_allow_html=True)
