"""Neon UI components for Streamlit."""

from .kpi import neon_kpi_card, neon_kpi_grid, neon_metric_card
from .charts import (
    apply_neon_chart_theme,
    get_neon_color_sequence,
    neon_line_chart,
    neon_bar_chart,
    neon_donut_chart,
    neon_scatter_plot,
    neon_histogram,
    neon_gauge_chart,
    neon_risk_distribution_chart
)
from .panels import neon_panel, neon_status_panel, neon_recommendation_panel, neon_what_if_panel
from .alerts import neon_alert, neon_business_alert, neon_anomaly_alert
from .header import neon_page_header, neon_section_header, neon_breadcrumb
from .filters import (
    neon_filter_container,
    neon_date_range_filter,
    neon_multiselect_filter,
    neon_select_filter,
    neon_text_filter,
    neon_filter_bar,
    close_filter_container
)

__all__ = [
    # KPI components
    'neon_kpi_card',
    'neon_kpi_grid',
    'neon_metric_card',
    # Chart components
    'apply_neon_chart_theme',
    'get_neon_color_sequence',
    'neon_line_chart',
    'neon_bar_chart',
    'neon_donut_chart',
    'neon_scatter_plot',
    'neon_histogram',
    'neon_gauge_chart',
    'neon_risk_distribution_chart',
    # Panel components
    'neon_panel',
    'neon_status_panel',
    'neon_recommendation_panel',
    'neon_what_if_panel',
    # Alert components
    'neon_alert',
    'neon_business_alert',
    'neon_anomaly_alert',
    # Header components
    'neon_page_header',
    'neon_section_header',
    'neon_breadcrumb',
    # Filter components
    'neon_filter_container',
    'neon_date_range_filter',
    'neon_multiselect_filter',
    'neon_select_filter',
    'neon_text_filter',
    'neon_filter_bar',
    'close_filter_container',
]
