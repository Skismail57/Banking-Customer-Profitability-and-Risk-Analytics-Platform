"""Neon alert and notification components."""

import streamlit as st
from typing import Optional, List
from frontend.streamlit.theme import neon_theme


def neon_alert(
    message: str,
    alert_type: str = "info",
    title: Optional[str] = None,
    dismissible: bool = False,
    icon: Optional[str] = None
) -> None:
    """Create a neon-styled alert with glow effects.

    Args:
        message: Alert message
        alert_type: Alert type (info, success, warning, error, critical, anomaly, risk, ai_insight)
        title: Optional alert title
        dismissible: Whether the alert is dismissible
        icon: Optional custom icon
    """
    alert_colors = {
        "info": neon_theme.colors.cyan,
        "success": neon_theme.colors.green,
        "warning": neon_theme.colors.orange,
        "error": neon_theme.colors.red,
        "critical": neon_theme.colors.red,
        "anomaly": neon_theme.colors.magenta,
        "risk": neon_theme.colors.orange,
        "ai_insight": neon_theme.colors.purple
    }

    alert_icons = {
        "info": "ℹ",
        "success": "✓",
        "warning": "⚠",
        "error": "✕",
        "critical": "⚡",
        "anomaly": "◉",
        "risk": "⚠",
        "ai_insight": "✦"
    }

    color = alert_colors.get(alert_type, neon_theme.colors.cyan)
    default_icon = alert_icons.get(alert_type, "ℹ")
    display_icon = icon if icon else default_icon

    # Add animation for critical alerts
    animation_class = "critical" if alert_type == "critical" else alert_type

    title_html = f'<div style="font-weight: 600; color: {neon_theme.colors.white}; margin-bottom: 0.5rem;">{title}</div>' if title else ""

    alert_html = f"""
    <div class="neon-alert {animation_class}">
        <div style="display: flex; align-items: flex-start; gap: 1rem;">
            <div style="
                font-size: 1.5rem;
                color: {color};
                line-height: 1;
                flex-shrink: 0;
            ">{display_icon}</div>
            <div style="flex: 1;">
                {title_html}
                <div style="
                    color: {neon_theme.colors.white_dim};
                    line-height: 1.6;
                ">{message}</div>
            </div>
            {f'<div style="cursor: pointer; color: {neon_theme.colors.muted}; font-size: 1.25rem;">✕</div>' if dismissible else ''}
        </div>
    </div>
    """

    st.markdown(alert_html, unsafe_allow_html=True)


def neon_business_alert(
    alert_type: str,
    title: str,
    description: str,
    severity: str,
    timestamp: Optional[str] = None,
    affected_entities: Optional[List[str]] = None,
    recommended_actions: Optional[List[str]] = None
) -> None:
    """Create a neon-styled business alert for Decision Center.

    Args:
        alert_type: Type of business alert
        title: Alert title
        description: Alert description
        severity: Severity level (low, medium, high, critical)
        timestamp: Optional timestamp
        affected_entities: Optional list of affected entities
        recommended_actions: Optional list of recommended actions
    """
    severity_colors = {
        "low": neon_theme.colors.green,
        "medium": neon_theme.colors.yellow,
        "high": neon_theme.colors.orange,
        "critical": neon_theme.colors.red
    }

    severity_color = severity_colors.get(severity.lower(), neon_theme.colors.cyan)

    entities_html = ""
    if affected_entities:
        entities_html = f'''
        <div style="margin-top: 0.75rem;">
            <div style="font-size: 0.75rem; color: {neon_theme.colors.muted}; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem;">Affected Entities</div>
            <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                {"".join([f'<span style="background: rgba(0, 245, 255, 0.1); border: 1px solid rgba(0, 245, 255, 0.2); color: {neon_theme.colors.cyan}; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem;">{entity}</span>' for entity in affected_entities])}
            </div>
        </div>
        '''

    actions_html = ""
    if recommended_actions:
        actions_html = f'''
        <div style="margin-top: 0.75rem;">
            <div style="font-size: 0.75rem; color: {neon_theme.colors.muted}; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem;">Recommended Actions</div>
            <ul style="margin: 0.25rem 0 0 1.5rem; padding: 0;">
                {"".join([f'<li style="color: {neon_theme.colors.white_dim}; margin: 0.25rem 0;">{action}</li>' for action in recommended_actions])}
            </ul>
        </div>
        '''

    alert_html = f'''
    <div class="glass-panel warning" style="
        border-color: rgba({severity_color}, 0.3);
        background: linear-gradient(135deg, rgba({severity_color}, 0.05) 0%, rgba(12, 18, 24, 0.8) 100%);
    ">
        <div style="display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 0.75rem;">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <div style="
                    font-size: 1.25rem;
                    color: {severity_color};
                ">⚠</div>
                <div>
                    <div style="
                        font-size: 0.75rem;
                        color: {neon_theme.colors.muted};
                        text-transform: uppercase;
                        letter-spacing: 0.05em;
                    ">{alert_type}</div>
                    <div style="
                        font-size: 1rem;
                        font-weight: 600;
                        color: {neon_theme.colors.white};
                    ">{title}</div>
                </div>
            </div>
            <div style="
                background: rgba({severity_color}, 0.15);
                border: 1px solid rgba({severity_color}, 0.3);
                color: {severity_color};
                padding: 0.25rem 0.75rem;
                border-radius: 9999px;
                font-size: 0.75rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            ">{severity}</div>
        </div>

        <div style="
            color: {neon_theme.colors.white_dim};
            line-height: 1.6;
            margin-bottom: 0.75rem;
        ">{description}</div>

        {f'<div style="font-size: 0.75rem; color: {neon_theme.colors.muted_dim};">{timestamp}</div>' if timestamp else ''}

        {entities_html}

        {actions_html}
    </div>
    '''

    st.markdown(alert_html, unsafe_allow_html=True)


def neon_anomaly_alert(
    anomaly_type: str,
    value: float,
    threshold: float,
    severity: str,
    context: Optional[str] = None,
    explanation: Optional[str] = None
) -> None:
    """Create a neon-styled anomaly detection alert.

    Args:
        anomaly_type: Type of anomaly detected
        value: Detected value
        threshold: Threshold value
        severity: Severity level
        context: Optional context information
        explanation: Optional explanation of the anomaly
    """
    severity_colors = {
        "low": neon_theme.colors.green,
        "medium": neon_theme.colors.yellow,
        "high": neon_theme.colors.orange,
        "critical": neon_theme.colors.red
    }

    severity_color = severity_colors.get(severity.lower(), neon_theme.colors.magenta)

    deviation = ((value - threshold) / threshold * 100) if threshold != 0 else 0
    deviation_sign = "+" if deviation >= 0 else ""

    alert_html = f'''
    <div class="glass-panel danger" style="
        border-color: rgba({neon_theme.colors.magenta}, 0.3);
        background: linear-gradient(135deg, rgba({neon_theme.colors.magenta}, 0.1) 0%, rgba(12, 18, 24, 0.8) 100%);
    ">
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
            <div style="
                font-size: 1.5rem;
                color: {neon_theme.colors.magenta};
                animation: pulse 2s ease-in-out infinite;
            ">◉</div>
            <div>
                <div style="
                    font-size: 0.75rem;
                    color: {neon_theme.colors.muted};
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                ">Anomaly Detected</div>
                <div style="
                    font-size: 1rem;
                    font-weight: 600;
                    color: {neon_theme.colors.white};
                ">{anomaly_type}</div>
            </div>
        </div>

        <div style="
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.75rem;
            margin-bottom: 0.75rem;
        ">
            <div style="
                background: rgba(12, 18, 24, 0.6);
                border: 1px solid rgba(0, 245, 255, 0.1);
                border-radius: 0.5rem;
                padding: 0.75rem;
            ">
                <div style="font-size: 0.75rem; color: {neon_theme.colors.muted}; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem;">Value</div>
                <div style="font-size: 1.125rem; color: {neon_theme.colors.white}; font-weight: 600;">{value:,.2f}</div>
            </div>

            <div style="
                background: rgba(12, 18, 24, 0.6);
                border: 1px solid rgba(0, 245, 255, 0.1);
                border-radius: 0.5rem;
                padding: 0.75rem;
            ">
                <div style="font-size: 0.75rem; color: {neon_theme.colors.muted}; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem;">Threshold</div>
                <div style="font-size: 1.125rem; color: {neon_theme.colors.white}; font-weight: 600;">{threshold:,.2f}</div>
            </div>

            <div style="
                background: rgba({severity_color}, 0.15);
                border: 1px solid rgba({severity_color}, 0.3);
                border-radius: 0.5rem;
                padding: 0.75rem;
            ">
                <div style="font-size: 0.75rem; color: {neon_theme.colors.muted}; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem;">Deviation</div>
                <div style="font-size: 1.125rem; color: {severity_color}; font-weight: 600;">{deviation_sign}{deviation:.1f}%</div>
            </div>
        </div>

        {f'<div style="color: {neon_theme.colors.white_dim}; line-height: 1.6; margin-bottom: 0.5rem;">{context}</div>' if context else ''}

        {f'<div style="font-size: 0.875rem; color: {neon_theme.colors.muted_dim}; font-style: italic;">{explanation}</div>' if explanation else ''}
    </div>
    '''

    st.markdown(alert_html, unsafe_allow_html=True)
