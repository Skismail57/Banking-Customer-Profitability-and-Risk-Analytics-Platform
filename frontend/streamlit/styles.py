"""Centralized CSS styling system for Neon Enterprise UI.

This module provides all CSS styles for the banking analytics platform,
organized by component type for maintainability.
"""

from frontend.streamlit.theme import neon_theme


def get_global_styles() -> str:
    """Get global CSS styles for the application."""
    return f"""
    {neon_theme.get_global_css()}

    /* Streamlit-specific overrides */
    .stApp {{
        background: linear-gradient(180deg, #05070A 0%, #0A1117 50%, #0D161D 100%);
    }}

    /* Main container */
    .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }}

    /* Typography */
    h1, h2, h3, h4, h5, h6 {{
        color: var(--text-white);
        font-weight: 600;
        margin-bottom: 0.5rem;
    }}

    p {{
        color: var(--text-muted);
        line-height: 1.6;
    }}

    /* Links */
    a {{
        color: var(--color-cyan);
        text-decoration: none;
        transition: color var(--duration-base) var(--ease-in-out);
    }}

    a:hover {{
        color: var(--color-purple);
    }}
    """


def get_sidebar_styles() -> str:
    """Get sidebar styling for dark neon navigation."""
    return """
    /* Sidebar base */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0C1218 0%, #080D12 100%);
        border-right: 1px solid rgba(0, 245, 255, 0.1);
        box-shadow: 2px 0 20px rgba(0, 0, 0, 0.3);
    }

    /* Sidebar navigation items */
    [data-testid="stSidebar"] > div:nth-child(2) > div > div {
        background: transparent;
    }

    /* Navigation radio buttons */
    [data-testid="stSidebar"] label {
        color: var(--text-muted);
        font-weight: 500;
        padding: 0.75rem 1rem;
        margin: 0.25rem 0;
        border-radius: var(--radius-base);
        transition: all var(--duration-base) var(--ease-in-out);
        border: 1px solid transparent;
    }

    [data-testid="stSidebar"] label:hover {
        background: rgba(0, 245, 255, 0.05);
        border-color: rgba(0, 245, 255, 0.2);
        color: var(--text-white);
        transform: translateX(4px);
    }

    [data-testid="stSidebar"] label[data-selected="true"] {
        background: linear-gradient(90deg, rgba(0, 245, 255, 0.15) 0%, transparent 100%);
        border-left: 3px solid var(--color-cyan);
        color: var(--color-cyan);
        font-weight: 600;
    }

    /* Sidebar title */
    [data-testid="stSidebar"] h1 {
        color: var(--text-white);
        font-size: 1.25rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--color-cyan) 0%, var(--color-purple) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* Sidebar dividers */
    [data-testid="stSidebar"] hr {
        border-color: rgba(0, 245, 255, 0.1);
        margin: 1rem 0;
    }
    """


def get_header_styles() -> str:
    """Get header styling for page titles and navigation."""
    return """
    /* Main title styling */
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--color-cyan) 0%, var(--color-purple) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        animation: fadeInDown 0.6s ease-out;
    }

    /* Page subtitle */
    .page-subtitle {
        font-size: 1.1rem;
        color: var(--text-muted);
        margin-bottom: 1.5rem;
        animation: fadeIn 0.8s ease-out;
    }

    /* Section headers */
    .section-header {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-white);
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(0, 245, 255, 0.2);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .section-header::before {
        content: '';
        width: 4px;
        height: 1.5rem;
        background: linear-gradient(180deg, var(--color-cyan) 0%, var(--color-purple) 100%);
        border-radius: 2px;
    }
    """


def get_kpi_card_styles() -> str:
    """Get KPI card styling with neon effects."""
    return """
    /* KPI card base */
    .kpi-card {
        background: linear-gradient(135deg, rgba(12, 18, 24, 0.8) 0%, rgba(16, 24, 32, 0.8) 100%);
        border: 1px solid rgba(0, 245, 255, 0.2);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        margin: 0.5rem 0;
        backdrop-filter: blur(20px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3), inset 0 0 30px rgba(0, 0, 0, 0.1);
        transition: all var(--duration-base) var(--ease-in-out);
        position: relative;
        overflow: hidden;
        min-height: var(--kpi-card-height);
    }

    /* KPI card hover effect */
    .kpi-card:hover {
        transform: translateY(-4px);
        border-color: rgba(0, 245, 255, 0.4);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4), 0 0 30px rgba(0, 245, 255, 0.1);
    }

    /* KPI card glow effect */
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--color-cyan), transparent);
        opacity: 0;
        transition: opacity var(--duration-base) var(--ease-in-out);
    }

    .kpi-card:hover::before {
        opacity: 1;
    }

    /* KPI card variants */
    .kpi-card.cyan {
        border-color: rgba(0, 245, 255, 0.3);
    }

    .kpi-card.cyan:hover {
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4), var(--glow-cyan);
    }

    .kpi-card.purple {
        border-color: rgba(157, 0, 255, 0.3);
    }

    .kpi-card.purple:hover {
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4), var(--glow-purple);
    }

    .kpi-card.green {
        border-color: rgba(0, 255, 156, 0.3);
    }

    .kpi-card.green:hover {
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4), var(--glow-green);
    }

    .kpi-card.orange {
        border-color: rgba(255, 138, 0, 0.3);
    }

    .kpi-card.orange:hover {
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4), var(--glow-orange);
    }

    .kpi-card.red {
        border-color: rgba(255, 49, 88, 0.3);
    }

    .kpi-card.red:hover {
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4), var(--glow-red);
    }

    /* KPI card content */
    .kpi-card-label {
        font-size: 0.875rem;
        color: var(--text-muted);
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }

    .kpi-card-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-white);
        margin: 0.5rem 0;
    }

    .kpi-card-delta {
        font-size: 0.875rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }

    .kpi-card-delta.positive {
        color: var(--color-green);
    }

    .kpi-card-delta.negative {
        color: var(--color-red);
    }

    .kpi-card-description {
        font-size: 0.75rem;
        color: var(--text-muted-dim);
        margin-top: 0.5rem;
    }
    """


def get_panel_styles() -> str:
    """Get glass panel styling for content containers."""
    return """
    /* Panel base */
    .glass-panel {
        background: linear-gradient(135deg, rgba(12, 18, 24, 0.6) 0%, rgba(16, 24, 32, 0.6) 100%);
        border: 1px solid rgba(0, 245, 255, 0.15);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        backdrop-filter: blur(20px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        transition: all var(--duration-base) var(--ease-in-out);
    }

    .glass-panel:hover {
        border-color: rgba(0, 245, 255, 0.3);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
    }

    /* Panel variants */
    .glass-panel.cyan {
        border-color: rgba(0, 245, 255, 0.2);
        background: linear-gradient(135deg, rgba(0, 245, 255, 0.05) 0%, rgba(12, 18, 24, 0.6) 100%);
    }

    .glass-panel.purple {
        border-color: rgba(157, 0, 255, 0.2);
        background: linear-gradient(135deg, rgba(157, 0, 255, 0.05) 0%, rgba(12, 18, 24, 0.6) 100%);
    }

    .glass-panel.green {
        border-color: rgba(0, 255, 156, 0.2);
        background: linear-gradient(135deg, rgba(0, 255, 156, 0.05) 0%, rgba(12, 18, 24, 0.6) 100%);
    }

    .glass-panel.warning {
        border-color: rgba(255, 138, 0, 0.2);
        background: linear-gradient(135deg, rgba(255, 138, 0, 0.05) 0%, rgba(12, 18, 24, 0.6) 100%);
    }

    .glass-panel.danger {
        border-color: rgba(255, 49, 88, 0.2);
        background: linear-gradient(135deg, rgba(255, 49, 88, 0.05) 0%, rgba(12, 18, 24, 0.6) 100%);
    }

    /* Panel header */
    .panel-header {
        font-size: 1.125rem;
        font-weight: 600;
        color: var(--text-white);
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid rgba(0, 245, 255, 0.1);
    }
    """


def get_table_styles() -> str:
    """Get table styling with dark neon aesthetic."""
    return """
    /* Data frame base */
    .stDataFrame {
        border-radius: var(--radius-lg);
        overflow: hidden;
        border: 1px solid rgba(0, 245, 255, 0.15);
        background: rgba(12, 18, 24, 0.8);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
    }

    /* Table header */
    .stDataFrame thead th {
        background: linear-gradient(180deg, rgba(0, 245, 255, 0.1) 0%, rgba(157, 0, 255, 0.05) 100%);
        color: var(--color-cyan);
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 0.05em;
        padding: 1rem;
        border-bottom: 2px solid rgba(0, 245, 255, 0.3);
    }

    /* Table cells */
    .stDataFrame tbody td {
        color: var(--text-white);
        padding: 0.875rem 1rem;
        border-bottom: 1px solid rgba(0, 245, 255, 0.05);
        font-size: 0.875rem;
    }

    /* Table row hover */
    .stDataFrame tbody tr:hover {
        background: rgba(0, 245, 255, 0.05);
    }

    /* Table status badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .status-badge.success {
        background: rgba(0, 255, 156, 0.15);
        color: var(--color-green);
        border: 1px solid rgba(0, 255, 156, 0.3);
    }

    .status-badge.warning {
        background: rgba(255, 138, 0, 0.15);
        color: var(--color-orange);
        border: 1px solid rgba(255, 138, 0, 0.3);
    }

    .status-badge.danger {
        background: rgba(255, 49, 88, 0.15);
        color: var(--color-red);
        border: 1px solid rgba(255, 49, 88, 0.3);
    }

    .status-badge.info {
        background: rgba(0, 245, 255, 0.15);
        color: var(--color-cyan);
        border: 1px solid rgba(0, 245, 255, 0.3);
    }
    """


def get_button_styles() -> str:
    """Get button styling with neon effects."""
    return """
    /* Primary button */
    .stButton > button {
        background: linear-gradient(135deg, var(--color-cyan) 0%, var(--color-purple) 100%);
        border: none;
        border-radius: var(--radius-base);
        color: var(--bg-base);
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        transition: all var(--duration-base) var(--ease-in-out);
        box-shadow: 0 4px 12px rgba(0, 245, 255, 0.3);
        position: relative;
        overflow: hidden;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 245, 255, 0.5);
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    /* Button shine effect */
    .stButton > button::after {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.5s;
    }

    .stButton > button:hover::after {
        left: 100%;
    }

    /* Secondary button */
    .stButton > button[kind="secondary"] {
        background: transparent;
        border: 1px solid var(--color-cyan);
        color: var(--color-cyan);
        box-shadow: none;
    }

    .stButton > button[kind="secondary"]:hover {
        background: rgba(0, 245, 255, 0.1);
        box-shadow: 0 0 20px rgba(0, 245, 255, 0.3);
    }
    """


def get_input_styles() -> str:
    """Get input and filter styling."""
    return """
    /* Text input */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(12, 18, 24, 0.8);
        border: 1px solid rgba(0, 245, 255, 0.2);
        border-radius: var(--radius-base);
        color: var(--text-white);
        padding: 0.75rem 1rem;
        transition: all var(--duration-base) var(--ease-in-out);
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--color-cyan);
        box-shadow: 0 0 20px rgba(0, 245, 255, 0.2);
        outline: none;
    }

    /* Select box */
    .stSelectbox > div > div > select,
    .stMultiselect > div > div > select {
        background: rgba(12, 18, 24, 0.8);
        border: 1px solid rgba(0, 245, 255, 0.2);
        border-radius: var(--radius-base);
        color: var(--text-white);
        padding: 0.75rem 1rem;
    }

    .stSelectbox > div > div > select:focus,
    .stMultiselect > div > div > select:focus {
        border-color: var(--color-cyan);
        box-shadow: 0 0 20px rgba(0, 245, 255, 0.2);
        outline: none;
    }

    /* Date input */
    .stDateInput > div > div > input {
        background: rgba(12, 18, 24, 0.8);
        border: 1px solid rgba(0, 245, 255, 0.2);
        border-radius: var(--radius-base);
        color: var(--text-white);
    }

    /* Number input */
    .stNumberInput > div > div > input {
        background: rgba(12, 18, 24, 0.8);
        border: 1px solid rgba(0, 245, 255, 0.2);
        border-radius: var(--radius-base);
        color: var(--text-white);
    }
    """


def get_chart_styles() -> str:
    """Get Plotly chart container styling."""
    return """
    /* Chart container */
    .plotly-graph-wrapper {
        border-radius: var(--radius-lg);
        overflow: hidden;
        border: 1px solid rgba(0, 245, 255, 0.15);
        background: rgba(12, 18, 24, 0.8);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        transition: all var(--duration-base) var(--ease-in-out);
    }

    .plotly-graph-wrapper:hover {
        border-color: rgba(0, 245, 255, 0.3);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
    }

    /* Chart title */
    .js-plotly-plot .plotly .main-svg .title {
        color: var(--text-white) !important;
        font-weight: 600;
    }
    """


def get_alert_styles() -> str:
    """Get alert and notification styling."""
    return """
    /* Alert containers */
    .stAlert {
        border-radius: var(--radius-lg);
        border: 1px solid;
        backdrop-filter: blur(20px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
    }

    /* Info alert */
    .stAlert[data-testid="stInfo"] {
        background: rgba(0, 245, 255, 0.1);
        border-color: rgba(0, 245, 255, 0.3);
        color: var(--color-cyan);
    }

    /* Success alert */
    .stAlert[data-testid="stSuccess"] {
        background: rgba(0, 255, 156, 0.1);
        border-color: rgba(0, 255, 156, 0.3);
        color: var(--color-green);
    }

    /* Warning alert */
    .stAlert[data-testid="stWarning"] {
        background: rgba(255, 138, 0, 0.1);
        border-color: rgba(255, 138, 0, 0.3);
        color: var(--color-orange);
    }

    /* Error alert */
    .stAlert[data-testid="stError"] {
        background: rgba(255, 49, 88, 0.1);
        border-color: rgba(255, 49, 88, 0.3);
        color: var(--color-red);
    }

    /* Custom alert component */
    .neon-alert {
        background: linear-gradient(135deg, rgba(12, 18, 24, 0.8) 0%, rgba(16, 24, 32, 0.8) 100%);
        border: 1px solid;
        border-radius: var(--radius-lg);
        padding: 1.25rem;
        margin: 1rem 0;
        backdrop-filter: blur(20px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
    }

    .neon-alert.info {
        border-color: rgba(0, 245, 255, 0.3);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2), 0 0 20px rgba(0, 245, 255, 0.1);
    }

    .neon-alert.success {
        border-color: rgba(0, 255, 156, 0.3);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2), 0 0 20px rgba(0, 255, 156, 0.1);
    }

    .neon-alert.warning {
        border-color: rgba(255, 138, 0, 0.3);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2), 0 0 20px rgba(255, 138, 0, 0.1);
    }

    .neon-alert.danger {
        border-color: rgba(255, 49, 88, 0.3);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2), 0 0 20px rgba(255, 49, 88, 0.1);
    }

    .neon-alert.critical {
        border-color: rgba(255, 49, 88, 0.5);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2), 0 0 30px rgba(255, 49, 88, 0.3);
        animation: glowPulse 2s ease-in-out infinite;
    }
    """


def get_expander_styles() -> str:
    """Get expander/accordion styling."""
    return """
    /* Expander header */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(0, 245, 255, 0.05) 0%, rgba(157, 0, 255, 0.05) 100%);
        border: 1px solid rgba(0, 245, 255, 0.15);
        border-radius: var(--radius-base);
        padding: 1rem;
        color: var(--text-white);
        font-weight: 600;
        transition: all var(--duration-base) var(--ease-in-out);
    }

    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, rgba(0, 245, 255, 0.1) 0%, rgba(157, 0, 255, 0.1) 100%);
        border-color: rgba(0, 245, 255, 0.3);
    }

    /* Expander content */
    .streamlit-expanderContent {
        background: rgba(12, 18, 24, 0.4);
        border: 1px solid rgba(0, 245, 255, 0.1);
        border-top: none;
        border-radius: 0 0 var(--radius-base) var(--radius-base);
        padding: 1rem;
    }
    """


def get_complete_css() -> str:
    """Get complete CSS for the application."""
    return f"""
    <style>
    {get_global_styles()}
    {get_sidebar_styles()}
    {get_header_styles()}
    {get_kpi_card_styles()}
    {get_panel_styles()}
    {get_table_styles()}
    {get_button_styles()}
    {get_input_styles()}
    {get_chart_styles()}
    {get_alert_styles()}
    {get_expander_styles()}
    </style>
    """
