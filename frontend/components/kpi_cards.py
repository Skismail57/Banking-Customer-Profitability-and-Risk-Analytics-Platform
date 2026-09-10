"""Reusable KPI card components."""

import streamlit as st
from typing import Optional, Any


def kpi_card(
    title: str,
    value: Any,
    delta: Optional[float] = None,
    delta_color: str = "normal",
    help_text: Optional[str] = None,
    color: str = "blue"
) -> None:
    """Create a KPI card with neon box around the value.

    Args:
        title: KPI title
        value: KPI value
        delta: Optional delta value (percentage or absolute)
        delta_color: Color for delta (normal, inverse, off)
        help_text: Optional help text
        color: Card color theme
    """
    # Build delta HTML if provided
    delta_html = ""
    if delta is not None:
        delta_display = f"{delta:+.1%}" if abs(delta) < 1 else f"{delta:+,.0f}"
        delta_color_code = "#10b981" if delta > 0 else "#ef4444" if delta < 0 else "#64748b"
        delta_html = f"""
        <div style="font-size: 0.875rem; color: {delta_color_code}; font-weight: 600; margin-top: 0.5rem;">
            {delta_display}
        </div>
        """

    # Build help text HTML if provided
    help_html = ""
    if help_text:
        help_html = f"""
        <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 0.5rem;">
            {help_text}
        </div>
        """

    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(30, 41, 59, 0.9) 100%);
                border: 2px solid rgba(0, 255, 255, 0.3);
                border-radius: 0.75rem;
                padding: 1.5rem;
                box-shadow: 0 0 20px rgba(0, 255, 255, 0.2), inset 0 0 20px rgba(0, 255, 255, 0.05);
                margin-bottom: 1rem;">
            <div style="font-size: 0.875rem; color: #94a3b8; font-weight: 500; margin-bottom: 0.75rem;">
                {title}
            </div>
            <div style="
                background: linear-gradient(135deg, rgba(0, 255, 255, 0.1) 0%, rgba(0, 200, 255, 0.15) 100%);
                border: 2px solid #00ffff;
                border-radius: 0.5rem;
                padding: 1rem 1.5rem;
                box-shadow: 0 0 15px rgba(0, 255, 255, 0.5), 0 0 30px rgba(0, 255, 255, 0.3), inset 0 0 10px rgba(0, 255, 255, 0.1);
                text-align: center;
                margin: 0.5rem 0;">
                <div style="font-size: 2rem; font-weight: 700; color: #ffffff; text-shadow: 0 0 10px rgba(0, 255, 255, 0.8), 0 0 20px rgba(0, 255, 255, 0.5);">
                    {value}
                </div>
            </div>
            {delta_html}
            {help_html}
        </div>
        """,
        unsafe_allow_html=True
    )
