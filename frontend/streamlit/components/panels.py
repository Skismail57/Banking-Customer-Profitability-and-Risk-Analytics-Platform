"""Neon glass panel components for content containers."""

import streamlit as st
from typing import Optional
from frontend.streamlit.theme import neon_theme


def neon_panel(
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
    icon: Optional[str] = None,
    variant: str = "default",
    collapsible: bool = False,
    expanded: bool = True
) -> None:
    """Create a neon-styled glass panel container.

    Args:
        title: Optional panel title
        subtitle: Optional panel subtitle
        icon: Optional icon (emoji or character)
        variant: Panel variant (default, cyan, purple, green, warning, danger)
        collapsible: Whether the panel is collapsible
        expanded: Initial expanded state if collapsible
    """
    variant_class = f"{variant}" if variant != "default" else ""

    # Build header HTML
    header_html = ""
    if title or icon:
        icon_html = f'<span style="margin-right: 0.5rem;">{icon}</span>' if icon else ""
        title_html = f'<div class="panel-header">{icon_html}{title}</div>'
        if subtitle:
            title_html += f'<div style="font-size: 0.875rem; color: {neon_theme.colors.muted}; margin-top: 0.25rem;">{subtitle}</div>'
        header_html = title_html

    if collapsible:
        with st.expander(title or "Panel", expanded=expanded):
            if header_html:
                st.markdown(header_html, unsafe_allow_html=True)
    else:
        if header_html:
            st.markdown(header_html, unsafe_allow_html=True)


def neon_status_panel(
    status: str,
    message: str,
    details: Optional[str] = None
) -> None:
    """Create a neon status panel for alerts and notifications.

    Args:
        status: Status type (info, success, warning, error, critical)
        message: Status message
        details: Optional details text
    """
    status_colors = {
        "info": neon_theme.colors.cyan,
        "success": neon_theme.colors.green,
        "warning": neon_theme.colors.orange,
        "error": neon_theme.colors.red,
        "critical": neon_theme.colors.red
    }

    status_icons = {
        "info": "ℹ",
        "success": "✓",
        "warning": "⚠",
        "error": "✕",
        "critical": "⚡"
    }

    color = status_colors.get(status, neon_theme.colors.cyan)
    icon = status_icons.get(status, "ℹ")

    panel_html = f"""
    <div class="neon-alert {status}">
        <div style="display: flex; align-items: flex-start; gap: 1rem;">
            <div style="
                font-size: 1.5rem;
                color: {color};
                line-height: 1;
            ">{icon}</div>
            <div style="flex: 1;">
                <div style="
                    font-weight: 600;
                    color: {neon_theme.colors.white};
                    margin-bottom: 0.25rem;
                ">{status.upper()}</div>
                <div style="
                    color: {neon_theme.colors.white_dim};
                    line-height: 1.5;
                ">{message}</div>
                {f'<div style="font-size: 0.875rem; color: {neon_theme.colors.muted_dim}; margin-top: 0.5rem;">{details}</div>' if details else ''}
            </div>
        </div>
    </div>
    """

    st.markdown(panel_html, unsafe_allow_html=True)


def neon_recommendation_panel(
    title: str,
    recommendation: str,
    expected_impact: str,
    confidence: str,
    priority: str,
    action_items: Optional[list] = None
) -> None:
    """Create a neon-styled recommendation panel for Decision Center.

    Args:
        title: Recommendation title
        recommendation: Main recommendation text
        expected_impact: Expected impact description
        confidence: Confidence level
        priority: Priority level
        action_items: Optional list of action items
    """
    priority_colors = {
        "critical": neon_theme.colors.red,
        "high": neon_theme.colors.orange,
        "medium": neon_theme.colors.yellow,
        "low": neon_theme.colors.green
    }

    priority_color = priority_colors.get(priority.lower(), neon_theme.colors.cyan)

    action_items_html = ""
    if action_items:
        action_items_html = '<div style="margin-top: 1rem;"><strong>Action Items:</strong><ul style="margin: 0.5rem 0 0 1.5rem; padding: 0;">'
        for item in action_items:
            action_items_html += f'<li style="color: {neon_theme.colors.white_dim}; margin: 0.25rem 0;">{item}</li>'
        action_items_html += '</ul></div>'

    panel_html = f"""
    <div class="glass-panel purple" style="
        border-color: rgba(157, 0, 255, 0.3);
        background: linear-gradient(135deg, rgba(157, 0, 255, 0.1) 0%, rgba(12, 18, 24, 0.8) 100%);
    ">
        <div style="
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 1rem;
        ">
            <div style="
                font-size: 1.25rem;
                color: {neon_theme.colors.purple};
            ">✦</div>
            <div style="
                font-size: 1.125rem;
                font-weight: 600;
                color: {neon_theme.colors.white};
            ">{title}</div>
        </div>

        <div style="
            color: {neon_theme.colors.white_dim};
            line-height: 1.6;
            margin-bottom: 1rem;
        ">{recommendation}</div>

        <div style="
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 0.75rem;
            margin-bottom: 1rem;
        ">
            <div style="
                background: rgba(0, 255, 156, 0.1);
                border: 1px solid rgba(0, 255, 156, 0.2);
                border-radius: 0.5rem;
                padding: 0.75rem;
            ">
                <div style="
                    font-size: 0.75rem;
                    color: {neon_theme.colors.muted};
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                    margin-bottom: 0.25rem;
                ">Expected Impact</div>
                <div style="
                    font-size: 0.875rem;
                    color: {neon_theme.colors.green};
                    font-weight: 600;
                ">{expected_impact}</div>
            </div>

            <div style="
                background: rgba(0, 245, 255, 0.1);
                border: 1px solid rgba(0, 245, 255, 0.2);
                border-radius: 0.5rem;
                padding: 0.75rem;
            ">
                <div style="
                    font-size: 0.75rem;
                    color: {neon_theme.colors.muted};
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                    margin-bottom: 0.25rem;
                ">Confidence</div>
                <div style="
                    font-size: 0.875rem;
                    color: {neon_theme.colors.cyan};
                    font-weight: 600;
                ">{confidence}</div>
            </div>
        </div>

        <div style="
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 1rem;
        ">
            <div style="
                font-size: 0.75rem;
                color: {neon_theme.colors.muted};
                text-transform: uppercase;
                letter-spacing: 0.05em;
            ">Priority:</div>
            <div style="
                background: rgba({priority_color}, 0.15);
                border: 1px solid rgba({priority_color}, 0.3);
                color: {priority_color};
                padding: 0.25rem 0.75rem;
                border-radius: 9999px;
                font-size: 0.75rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            ">{priority}</div>
        </div>

        {action_items_html}
    </div>
    """

    st.markdown(panel_html, unsafe_allow_html=True)


def neon_what_if_panel(
    scenario: str,
    metrics: dict,
    comparison: Optional[dict] = None
) -> None:
    """Create a neon-styled what-if analysis panel.

    Args:
        scenario: Scenario name (Baseline, Optimistic, Pessimistic, Custom)
        metrics: Dictionary of metric values
        comparison: Optional comparison to baseline
    """
    scenario_colors = {
        "Baseline": neon_theme.colors.cyan,
        "Optimistic": neon_theme.colors.green,
        "Pessimistic": neon_theme.colors.red,
        "Custom": neon_theme.colors.purple
    }

    scenario_color = scenario_colors.get(scenario, neon_theme.colors.cyan)

    metrics_html = ""
    for metric_name, metric_value in metrics.items():
        diff_html = ""
        if comparison and metric_name in comparison:
            baseline_value = comparison[metric_name]
            diff = metric_value - baseline_value
            diff_pct = (diff / baseline_value * 100) if baseline_value != 0 else 0
            diff_color = neon_theme.colors.green if diff >= 0 else neon_theme.colors.red
            diff_sign = "+" if diff >= 0 else ""
            diff_html = f'''
            <div style="
                font-size: 0.75rem;
                color: {diff_color};
                margin-top: 0.25rem;
            ">{diff_sign}{diff:,.0f} ({diff_sign}{diff_pct:.1f}%)</div>
            '''

        metrics_html += f'''
        <div style="
            background: rgba(12, 18, 24, 0.6);
            border: 1px solid rgba(0, 245, 255, 0.1);
            border-radius: 0.5rem;
            padding: 0.75rem;
        ">
            <div style="
                font-size: 0.75rem;
                color: {neon_theme.colors.muted};
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: 0.25rem;
            ">{metric_name}</div>
            <div style="
                font-size: 1.125rem;
                color: {neon_theme.colors.white};
                font-weight: 600;
            ">{metric_value:,.0f}</div>
            {diff_html}
        </div>
        '''

    panel_html = f"""
    <div class="glass-panel cyan" style="
        border-color: rgba(0, 245, 255, 0.3);
        background: linear-gradient(135deg, rgba(0, 245, 255, 0.1) 0%, rgba(12, 18, 24, 0.8) 100%);
    ">
        <div style="
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1rem;
        ">
            <div style="
                font-size: 1.125rem;
                font-weight: 600;
                color: {neon_theme.colors.white};
            ">{scenario}</div>
            <div style="
                background: rgba({scenario_color}, 0.15);
                border: 1px solid rgba({scenario_color}, 0.3);
                color: {scenario_color};
                padding: 0.25rem 0.75rem;
                border-radius: 9999px;
                font-size: 0.75rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            ">Scenario</div>
        </div>

        <div style="
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 0.75rem;
        ">
            {metrics_html}
        </div>
    </div>
    """

    st.markdown(panel_html, unsafe_allow_html=True)
