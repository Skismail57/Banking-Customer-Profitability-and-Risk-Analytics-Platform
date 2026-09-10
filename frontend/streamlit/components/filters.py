"""Neon filter components with enterprise control panel styling."""

import streamlit as st
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from frontend.streamlit.theme import neon_theme


def neon_filter_container(
    title: str = "Filters",
    expanded: bool = True,
    collapsible: bool = True
) -> None:
    """Create a neon-styled filter container.

    Args:
        title: Container title
        expanded: Initial expanded state
        collapsible: Whether the container is collapsible
    """
    if collapsible:
        with st.expander(title, expanded=expanded):
            st.markdown('<div style="animation: fadeIn 0.4s ease-out;">', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="glass-panel cyan" style="padding: 1.5rem; margin-bottom: 1rem;"><div class="panel-header">{title}</div>', unsafe_allow_html=True)


def neon_date_range_filter(
    key: str = "date_range",
    default_days: int = 30,
    label: str = "Date Range"
) -> Tuple[datetime.date, datetime.date]:
    """Create a neon-styled date range filter.

    Args:
        key: Unique key for the filter
        default_days: Default number of days to show
        label: Filter label

    Returns:
        Tuple of (start_date, end_date)
    """
    col1, col2 = st.columns(2)

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=default_days)

    with col1:
        st.markdown(f'<label style="font-size: 0.875rem; color: {neon_theme.colors.muted}; font-weight: 500;">{label} - Start</label>', unsafe_allow_html=True)
        start_date = st.date_input(
            "",
            value=start_date,
            key=f"{key}_start",
            label_visibility="collapsed"
        )

    with col2:
        st.markdown(f'<label style="font-size: 0.875rem; color: {neon_theme.colors.muted}; font-weight: 500;">{label} - End</label>', unsafe_allow_html=True)
        end_date = st.date_input(
            "",
            value=end_date,
            key=f"{key}_end",
            label_visibility="collapsed"
        )

    return start_date, end_date


def neon_multiselect_filter(
    label: str,
    options: List[str],
    default: Optional[List[str]] = None,
    key: str = "multiselect",
    help_text: Optional[str] = None
) -> List[str]:
    """Create a neon-styled multiselect filter.

    Args:
        label: Filter label
        options: Available options
        default: Default selected options
        key: Unique key for the filter
        help_text: Optional help text

    Returns:
        List of selected options
    """
    if default is None:
        default = options

    st.markdown(f'<label style="font-size: 0.875rem; color: {neon_theme.colors.muted}; font-weight: 500;">{label}</label>', unsafe_allow_html=True)

    selected = st.multiselect(
        "",
        options=options,
        default=default,
        key=key,
        label_visibility="collapsed",
        help=help_text
    )

    return selected if selected else options


def neon_select_filter(
    label: str,
    options: List[str],
    default: Optional[str] = None,
    key: str = "select",
    help_text: Optional[str] = None
) -> str:
    """Create a neon-styled select filter.

    Args:
        label: Filter label
        options: Available options
        default: Default selected option
        key: Unique key for the filter
        help_text: Optional help text

    Returns:
        Selected option
    """
    if default is None:
        default = options[0]

    st.markdown(f'<label style="font-size: 0.875rem; color: {neon_theme.colors.muted}; font-weight: 500;">{label}</label>', unsafe_allow_html=True)

    selected = st.selectbox(
        "",
        options=options,
        index=options.index(default) if default in options else 0,
        key=key,
        label_visibility="collapsed",
        help=help_text
    )

    return selected


def neon_text_filter(
    label: str,
    placeholder: str = "Search...",
    key: str = "text_filter",
    help_text: Optional[str] = None
) -> str:
    """Create a neon-styled text filter.

    Args:
        label: Filter label
        placeholder: Input placeholder
        key: Unique key for the filter
        help_text: Optional help text

    Returns:
        Search query string
    """
    st.markdown(f'<label style="font-size: 0.875rem; color: {neon_theme.colors.muted}; font-weight: 500;">{label}</label>', unsafe_allow_html=True)

    search_query = st.text_input(
        "",
        placeholder=placeholder,
        key=key,
        label_visibility="collapsed",
        help=help_text
    )

    return search_query


def neon_filter_bar(
    filters: dict,
    apply_button: bool = True,
    reset_button: bool = True
) -> None:
    """Create a neon-styled filter bar with action buttons.

    Args:
        filters: Dictionary of filter configurations
        apply_button: Whether to show apply button
        reset_button: Whether to show reset button
    """
    cols = st.columns(len(filters) + (1 if apply_button else 0) + (1 if reset_button else 0))

    for i, (filter_name, filter_config) in enumerate(filters.items()):
        with cols[i]:
            filter_type = filter_config.get("type", "select")

            if filter_type == "select":
                neon_select_filter(
                    label=filter_config.get("label", filter_name),
                    options=filter_config.get("options", []),
                    default=filter_config.get("default"),
                    key=f"filter_{filter_name}"
                )
            elif filter_type == "multiselect":
                neon_multiselect_filter(
                    label=filter_config.get("label", filter_name),
                    options=filter_config.get("options", []),
                    default=filter_config.get("default"),
                    key=f"filter_{filter_name}"
                )
            elif filter_type == "text":
                neon_text_filter(
                    label=filter_config.get("label", filter_name),
                    placeholder=filter_config.get("placeholder", "Search..."),
                    key=f"filter_{filter_name}"
                )

    button_col = len(filters)
    if apply_button:
        with cols[button_col]:
            st.markdown('<div style="padding-top: 1.75rem;">', unsafe_allow_html=True)
            st.button("Apply Filters", key="apply_filters")
            st.markdown('</div>', unsafe_allow_html=True)
        button_col += 1

    if reset_button:
        with cols[button_col]:
            st.markdown('<div style="padding-top: 1.75rem;">', unsafe_allow_html=True)
            st.button("Reset", key="reset_filters")
            st.markdown('</div>', unsafe_allow_html=True)


def close_filter_container(collapsible: bool = True) -> None:
    """Close a neon filter container.

    Args:
        collapsible: Whether the container was collapsible
    """
    if collapsible:
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('</div></div>', unsafe_allow_html=True)
