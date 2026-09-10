"""Neon header component for page titles and navigation."""

import streamlit as st
from datetime import datetime
from typing import Optional
from frontend.streamlit.theme import neon_theme


def neon_page_header(
    title: str,
    subtitle: Optional[str] = None,
    icon: Optional[str] = None,
    show_status: bool = True,
    show_timestamp: bool = False
) -> None:
    """Create a neon-styled page header.

    Args:
        title: Page title
        subtitle: Optional page subtitle
        icon: Optional page icon (emoji or character)
        show_status: Whether to show system status indicator
        show_timestamp: Whether to show current timestamp
    """
    # Build title with icon
    icon_html = f'<span style="margin-right: 0.5rem;">{icon}</span>' if icon else ""

    # Status indicator
    status_html = ""
    if show_status:
        status_html = f'''
        <div style="
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-top: 0.75rem;
        ">
            <div style="
                width: 8px;
                height: 8px;
                background: {neon_theme.colors.green};
                border-radius: 50%;
                box-shadow: 0 0 10px rgba(0, 255, 156, 0.5);
                animation: pulse 2s ease-in-out infinite;
            "></div>
            <div style="
                font-size: 0.875rem;
                color: {neon_theme.colors.muted};
                font-weight: 500;
            ">System Online</div>
        </div>
        '''

    # Timestamp
    timestamp_html = ""
    if show_timestamp:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        timestamp_html = f'''
        <div style="
            font-size: 0.75rem;
            color: {neon_theme.colors.muted_dim};
            margin-top: 0.5rem;
        ">{current_time}</div>
        '''

    header_html = f'''
    <div style="animation: fadeInDown 0.6s ease-out;">
        <h1 class="main-title">{icon_html}{title}</h1>
        {f'<p class="page-subtitle">{subtitle}</p>' if subtitle else ''}
        {status_html}
        {timestamp_html}
    </div>
    '''

    st.markdown(header_html, unsafe_allow_html=True)


def neon_section_header(
    title: str,
    description: Optional[str] = None,
    icon: Optional[str] = None,
    variant: str = "default"
) -> None:
    """Create a neon-styled section header.

    Args:
        title: Section title
        description: Optional section description
        icon: Optional section icon
        variant: Header variant (default, cyan, purple, green, orange, red)
    """
    variant_colors = {
        "default": neon_theme.colors.cyan,
        "cyan": neon_theme.colors.cyan,
        "purple": neon_theme.colors.purple,
        "green": neon_theme.colors.green,
        "orange": neon_theme.colors.orange,
        "red": neon_theme.colors.red
    }

    accent_color = variant_colors.get(variant, neon_theme.colors.cyan)

    icon_html = f'<span style="margin-right: 0.5rem;">{icon}</span>' if icon else ""

    description_html = f'<p style="color: {neon_theme.colors.muted}; font-size: 0.875rem; margin-top: 0.5rem;">{description}</p>' if description else ""

    header_html = f'''
    <div class="section-header" style="
        border-bottom-color: rgba({accent_color}, 0.2);
        animation: fadeIn 0.6s ease-out;
    ">
        <div style="
            width: 4px;
            height: 1.5rem;
            background: linear-gradient(180deg, {accent_color} 0%, rgba({accent_color}, 0.5) 100%);
            border-radius: 2px;
            margin-right: 0.75rem;
        "></div>
        <div style="flex: 1;">
            <div style="
                font-size: 1.25rem;
                font-weight: 600;
                color: {neon_theme.colors.white};
            ">{icon_html}{title}</div>
            {description_html}
        </div>
    </div>
    '''

    st.markdown(header_html, unsafe_allow_html=True)


def neon_breadcrumb(
    items: list,
    separator: str = "›"
) -> None:
    """Create a neon-styled breadcrumb navigation.

    Args:
        items: List of breadcrumb items (text, optional link)
        separator: Separator character
    """
    breadcrumb_html = '<div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem; font-size: 0.875rem;">'

    for i, item in enumerate(items):
        if isinstance(item, tuple):
            text, link = item
            breadcrumb_html += f'<a href="{link}" style="color: {neon_theme.colors.cyan}; text-decoration: none;">{text}</a>'
        else:
            if i == len(items) - 1:
                breadcrumb_html += f'<span style="color: {neon_theme.colors.white}; font-weight: 500;">{item}</span>'
            else:
                breadcrumb_html += f'<span style="color: {neon_theme.colors.muted};">{item}</span>'

        if i < len(items) - 1:
            breadcrumb_html += f'<span style="color: {neon_theme.colors.muted_dim}; margin: 0 0.25rem;">{separator}</span>'

    breadcrumb_html += '</div>'

    st.markdown(breadcrumb_html, unsafe_allow_html=True)
