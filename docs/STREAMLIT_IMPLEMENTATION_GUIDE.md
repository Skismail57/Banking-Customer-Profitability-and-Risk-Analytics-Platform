# Streamlit Implementation Guide

## Overview

This guide provides comprehensive documentation for the Streamlit analytics application for the Banking Customer Profitability and Risk Analytics Platform. The application provides interactive dashboards for exploring customer analytics data.

---

## Architecture

### Single Source of Truth

**Principle**: All business logic resides in the Python analytics layer. The Streamlit application only visualizes pre-calculated metrics.

**Data Flow**:
1. Python analytics modules calculate metrics (profitability, risk, churn, CLV, etc.)
2. Metrics are stored in database tables
3. SQL views aggregate and format the data
4. Streamlit queries the views and displays the data
5. No business logic in Streamlit UI components

### Application Structure

```
streamlit/
├── app.py                      # Main application entry point
├── config.py                   # Application configuration
├── __init__.py
├── components/                 # Reusable UI components
│   ├── __init__.py
│   ├── filters.py              # Filter components
│   ├── kpi_cards.py            # KPI card components
│   ├── charts.py               # Plotly chart components
│   └── tables.py               # Table components
└── pages/                      # Page implementations
    ├── __init__.py
    ├── home.py                 # Home page
    ├── executive_overview.py    # Executive Overview
    ├── customer_360.py         # Customer 360
    ├── profitability.py        # Profitability
    ├── risk.py                 # Risk
    ├── segmentation.py         # Segmentation
    ├── churn.py                # Churn
    ├── transactions.py         # Transactions
    ├── products.py             # Products
    ├── decision_intelligence.py # Decision Intelligence
    ├── model_monitoring.py     # Model Monitoring
    └── data_quality.py         # Data Quality
```

---

## Installation

### Prerequisites

- Python 3.9+
- pip
- Virtual environment (recommended)

### Setup

1. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install streamlit pandas plotly
```

3. **Set environment variables**:
```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=banking_analytics
export DB_USER=postgres
export DB_PASSWORD=your_password
```

4. **Run the application**:
```bash
streamlit run streamlit/app.py
```

---

## Configuration

### Application Configuration (`config.py`)

The application uses a centralized configuration system:

```python
@dataclass
class AppConfig:
    # Database configuration
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "5432"))
    db_name: str = os.getenv("DB_NAME", "banking_analytics")
    db_user: str = os.getenv("DB_USER", "postgres")
    db_password: str = os.getenv("DB_PASSWORD", "")
    
    # Cache configuration
    cache_ttl: int = 3600  # 1 hour
    cache_max_entries: int = 100
    
    # Pagination
    default_page_size: int = 50
    max_page_size: int = 500
    
    # Chart configuration
    default_chart_height: int = 400
    default_chart_width: int = 800
    
    # Theme colors
    primary_color: str = "#1f77b4"
    secondary_color: str = "#ff7f0e"
    success_color: str = "#2ca02c"
    warning_color: str = "#ff7f0e"
    danger_color: str = "#d62728"
    
    # Risk levels and colors
    risk_levels: list = ["low", "medium", "high", "critical"]
    risk_colors: dict = {
        "low": "#2ca02c",
        "medium": "#ff7f0e",
        "high": "#d62728",
        "critical": "#9467bd",
    }
```

---

## Reusable Components

### Filter Components (`components/filters.py`)

#### Date Range Filter
```python
start_date, end_date = filters.date_range_filter(
    key="date_range",
    default_days=30
)
```

#### Segment Filter
```python
segments = filters.segment_filter(
    segments=["premium", "standard", "basic"],
    key="segment",
    default=None
)
```

#### Risk Filter
```python
risk_levels = filters.risk_filter(
    key="risk",
    default=None
)
```

#### Customer Search
```python
search_query = filters.customer_search(
    key="customer_search"
)
```

#### Region Filter
```python
regions = filters.region_filter(
    regions=["North", "South", "East", "West"],
    key="region",
    default=None
)
```

#### Apply Filters
```python
filtered_df = filters.apply_filters(
    df=df,
    filters={
        "date_column": "as_of_date",
        "start_date": start_date,
        "end_date": end_date,
        "segment": segments,
        "risk_level": risk_levels,
        "region": regions,
        "customer_search": search_query
    }
)
```

### KPI Card Components (`components/kpi_cards.py`)

#### Basic KPI Card
```python
kpi_cards.kpi_card(
    title="Total Customers",
    value=10000,
    delta=0.05,
    delta_color="normal",
    help_text="Total active customers",
    color="blue"
)
```

#### KPI Row
```python
kpi_cards.kpi_row({
    "Total Customers": {
        "value": 10000,
        "delta": 0.05,
        "help_text": "Total active customers"
    },
    "Total Profit": {
        "value": 5000000,
        "help_text": "Total net profit"
    }
}, columns=4)
```

#### Risk KPI Card
```python
kpi_cards.risk_kpi_card(
    title="High Risk Customers",
    value=500,
    risk_level="high",
    help_text="Customers with high risk level"
)
```

#### Profitability KPI Card
```python
kpi_cards.profitability_kpi_card(
    title="Net Profit",
    value=15000,
    is_positive=True,
    help_text="Current net profit"
)
```

#### Percentage KPI Card
```python
kpi_cards.percentage_kpi_card(
    title="Churn Probability",
    value=0.15,
    threshold=0.3,
    help_text="Predicted churn probability"
)
```

### Chart Components (`components/charts.py`)

#### Line Chart
```python
charts.line_chart(
    df=df,
    x="month",
    y="net_profit",
    title="Profit Trend",
    color="segment",
    height=400
)
```

#### Bar Chart
```python
charts.bar_chart(
    df=df,
    x="segment",
    y="total_profit",
    title="Profit by Segment",
    color="risk_level",
    orientation="v",
    height=400
)
```

#### Pie/Donut Chart
```python
charts.donut_chart(
    df=df,
    names="risk_level",
    values="count",
    title="Risk Distribution",
    height=400
)
```

#### Scatter Plot
```python
charts.scatter_plot(
    df=df,
    x="clv",
    y="churn_probability",
    color="risk_level",
    size="exposure",
    title="Churn vs CLV",
    height=400
)
```

#### Histogram
```python
charts.histogram(
    df=df,
    x="net_profit",
    title="Profit Distribution",
    color="segment",
    nbins=30,
    height=400
)
```

#### Box Plot
```python
charts.box_plot(
    df=df,
    x="segment",
    y="net_profit",
    title="Profit Distribution by Segment",
    height=400
)
```

#### Heatmap
```python
charts.heatmap(
    df=correlation_matrix,
    title="Correlation Heatmap",
    height=400
)
```

#### Risk Distribution Chart
```python
charts.risk_distribution_chart(
    df=df,
    risk_column="risk_level",
    title="Risk Distribution",
    height=400
)
```

### Table Components (`components/tables.py`)

#### Data Table
```python
tables.data_table(
    df=df,
    key="table",
    page_size=50,
    use_container_width=True,
    height=400
)
```

#### Interactive Table
```python
selected_df = tables.interactive_table(
    df=df,
    key="interactive_table",
    page_size=50
)
```

#### Summary Table
```python
tables.summary_table(
    df=df,
    group_by="segment",
    agg_columns=["net_profit", "clv"],
    agg_functions=["sum", "mean", "count"],
    key="summary_table"
)
```

#### Export Button
```python
tables.export_button(
    df=df,
    filename="data.csv",
    key="export"
)
```

---

## Pages

### Home Page

**Purpose**: Landing page with platform overview and navigation

**Features**:
- Welcome message
- Platform statistics
- Quick navigation guide
- Data source information

**Usage**:
```python
from src.streamlit.pages import home
home.render()
```

### Executive Overview Page

**Purpose**: High-level KPIs for executives

**Features**:
- KPI cards (customers, profit, exposure, churn)
- Risk distribution chart
- Profit trend chart
- Segment performance charts

**Filters**:
- Date range
- Segment
- Region

### Customer 360 Page

**Purpose**: Comprehensive customer view

**Features**:
- Customer search
- Customer profile display
- KPI cards (profit, CLV, churn, exposure)
- Profitability trend chart
- Risk trajectory chart
- Transaction history table
- Recommendations table

**Filters**:
- Customer search

### Profitability Page

**Purpose**: Profitability analysis

**Features**:
- KPI cards (total profit, avg profit, margin, risk-adjusted profit)
- Profit trend chart
- Risk-adjusted profit trend chart
- Segment profitability charts
- Profitability distribution histogram

**Filters**:
- Date range
- Segment
- Region

### Risk Page

**Purpose**: Credit risk analytics

**Features**:
- KPI cards (high risk, critical risk, exposure, delinquency)
- Risk distribution chart
- Risk trend chart
- Delinquency funnel chart
- Exposure by risk level chart

**Filters**:
- Date range
- Segment
- Risk level

### Segmentation Page

**Purpose**: Customer segment analysis

**Features**:
- KPI cards (segments, largest segment, profitability, churn rate)
- Segment size pie chart
- Segment profitability bar chart
- Segment risk profile stacked bar chart
- Segment churn charts

**Filters**:
- Date range
- Segment
- Region

### Churn Page

**Purpose**: Churn and retention analytics

**Features**:
- KPI cards (churn probability, high churn customers, retention rate)
- Churn probability distribution histogram
- Churn by segment chart
- Churn vs risk level chart
- Churn vs CLV scatter plot
- Retention trend chart

**Filters**:
- Date range
- Segment
- Region

### Transactions Page

**Purpose**: Transaction analytics

**Features**:
- KPI cards (volume, value, avg amount, unique customers)
- Transaction volume trend chart
- Transaction value trend chart
- Transaction by type donut chart
- Transaction by channel bar chart
- Transaction value distribution histogram

**Filters**:
- Date range
- Product
- Channel

### Products Page

**Purpose**: Product performance analytics

**Features**:
- KPI cards (revenue, adoption rate, avg transaction, volume)
- Product revenue bar chart
- Product adoption bar chart
- Product risk scatter plot
- Product revenue trend line chart

**Filters**:
- Date range
- Product
- Segment

### Decision Intelligence Page

**Purpose**: Recommendations display

**Features**:
- Disclaimer (not banking decisions)
- KPI cards (critical recommendations, high confidence, total, completion rate)
- Recommendations by priority donut chart
- Recommendations by type bar chart
- Recommendation trend chart
- Recommendations table with export

**Filters**:
- Date range
- Segment
- Priority
- Confidence

### Model Monitoring Page

**Purpose**: Model performance tracking

**Features**:
- KPI cards (accuracy, precision, recall, drift)
- Model performance trend line chart
- Model comparison bar chart
- Model drift status table
- Model performance comparison table

**Filters**:
- Date range
- Model name
- Model type

### Data Quality Page

**Purpose**: Data quality monitoring

**Features**:
- KPI cards (total records, null %, duplicate %, freshness)
- Data quality by table
- Null percentage trend chart
- Duplicate percentage trend chart
- Column quality table
- Data quality summary with status indicators

---

## Caching

### Data Caching

The application uses Streamlit's `@st.cache_data` decorator to cache data fetching functions:

```python
@st.cache_data(ttl=config.cache_ttl)
def get_executive_data(start_date, end_date, segments, regions):
    """Get executive overview data from analytics layer."""
    # Data fetching logic
    return data
```

**Benefits**:
- Reduces database queries
- Improves page load performance
- Configurable TTL (default: 1 hour)

**Cache Invalidation**:
- Cache invalidates after TTL expires
- Manual cache clearing: Streamlit → Clear Cache

---

## Error Handling

### Graceful Error Handling

All data fetching functions include try-except blocks:

```python
try:
    data = get_executive_data(start_date, end_date, segments, regions)
except Exception as e:
    st.error(f"Error loading data: {e}")
    return
```

**Best Practices**:
- Always wrap data fetching in try-except
- Display user-friendly error messages
- Log errors for debugging
- Provide fallback options when possible

---

## Analytics Layer Integration

### Data Fetching Pattern

Each page follows this pattern:

1. **Get user filters** from UI components
2. **Call analytics layer** via cached function
3. **Handle errors** gracefully
4. **Display data** using reusable components

**Example**:
```python
def render() -> None:
    # Get filters
    start_date, end_date = filters.date_range_filter()
    segments = filters.segment_filter(["premium", "standard", "basic"])
    
    # Get data from analytics layer
    try:
        data = get_profitability_data(start_date, end_date, segments, regions)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return
    
    # Display using components
    kpi_cards.kpi_row({...})
    charts.line_chart(...)
```

### Analytics Layer Calls

The application calls the Python analytics layer to get pre-calculated metrics:

```python
@st.cache_data(ttl=config.cache_ttl)
def get_profitability_data(start_date, end_date, segments, regions):
    """Get profitability data from analytics layer."""
    
    # This would call the actual analytics modules:
    # from src.profitability_analytics import ProfitabilityAnalytics
    # analytics = ProfitabilityAnalytics()
    # data = analytics.calculate_profitability(...)
    
    # For now, return placeholder data
    return {...}
```

**Important**: Do not implement business logic in Streamlit pages. All calculations should be done in the Python analytics layer.

---

## Customization

### Adding New Pages

1. Create new page file in `streamlit/pages/`:
```python
# streamlit/pages/new_page.py
import streamlit as st
from src.streamlit.components import filters, kpi_cards, charts

def render() -> None:
    st.markdown('<h1 class="main-title">New Page</h1>', unsafe_allow_html=True)
    # Page implementation
```

2. Add to `streamlit/app.py`:
```python
from src.streamlit.pages import new_page

# Add to page radio
page = st.sidebar.radio(
    "Navigate",
    [..., "New Page"]
)

# Add to routing
elif page == "New Page":
    new_page.render()
```

### Adding New Components

1. Create component in `streamlit/components/`:
```python
# streamlit/components/new_component.py
def new_component(param1, param2):
    """New reusable component."""
    # Component implementation
```

2. Import and use in pages:
```python
from src.streamlit.components import new_component

new_component(param1, param2)
```

### Modifying Theme

Edit `streamlit/config.py`:
```python
@dataclass
class AppConfig:
    primary_color: str = "#your_color"
    secondary_color: str = "#your_color"
    # ...
```

---

## Deployment

### Local Deployment

```bash
streamlit run streamlit/app.py
```

### Cloud Deployment

#### Streamlit Cloud

1. Push code to GitHub
2. Connect to Streamlit Cloud
3. Deploy from repository
4. Set environment variables in Streamlit Cloud settings

#### Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["streamlit", "run", "streamlit/app.py"]
```

Build and run:
```bash
docker build -t banking-analytics .
docker run -p 8501:8501 banking-analytics
```

---

## Performance Optimization

### Caching Strategy

- Cache data fetching functions with appropriate TTL
- Use `@st.cache_data` for data that doesn't change frequently
- Clear cache manually when data is updated

### Component Optimization

- Limit chart complexity
- Use appropriate chart types
- Paginate large tables
- Lazy load data when possible

### Database Optimization

- Use SQL views for complex queries
- Add indexes to frequently queried columns
- Consider materialized views for heavy aggregations

---

## Security

### Environment Variables

Store sensitive configuration in environment variables:
```bash
export DB_PASSWORD=your_secure_password
export API_KEY=your_api_key
```

### Row-Level Security

Implement RLS in the database layer, not in Streamlit.

### Data Masking

Mask sensitive customer data in the analytics layer before displaying in Streamlit.

---

## Troubleshooting

### Common Issues

**Cache Issues**:
- Clear cache: Streamlit → Clear Cache
- Adjust TTL in `config.py`

**Data Loading Errors**:
- Check database connection
- Verify SQL views exist
- Check analytics layer output

**Performance Issues**:
- Reduce data volume
- Optimize SQL queries
- Increase cache TTL

**Chart Rendering Issues**:
- Check data format
- Verify column names
- Reduce chart complexity

---

## Best Practices

### Development

1. **Use reusable components**: Avoid duplicating UI code
2. **Cache data fetching**: Improve performance with caching
3. **Handle errors gracefully**: Always use try-except
4. **Separate concerns**: UI in Streamlit, logic in analytics layer
5. **Document code**: Add docstrings and comments

### UI/UX

1. **Consistent styling**: Use theme colors consistently
2. **Responsive design**: Test on different screen sizes
3. **Clear labels**: Label all filters and charts clearly
4. **Loading indicators**: Show loading state for slow operations
5. **User feedback**: Provide feedback on user actions

### Data

1. **Single source of truth**: All calculations in analytics layer
2. **No business logic in UI**: Streamlit only displays data
3. **Validate inputs**: Validate filter values
4. **Handle edge cases**: Handle empty data, null values
5. **Log errors**: Log errors for debugging

---

## Support

For issues or questions:
1. Check this guide
2. Review analytics layer documentation
3. Check Streamlit documentation
4. Contact development team
