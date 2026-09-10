# Repository Inventory

**Generated:** 2026-09-08
**Repository:** Banking Customer Profitability and Risk Analytics Platform

## Executive Summary

This inventory provides a structural overview of the entire repository to establish a baseline for the production-grade technical audit.

## Directory Structure

```
Banking Customer Profitability and Risk Analytics Platform/
├── api/                          # FastAPI application
├── config/                       # Configuration files
├── data/                         # Data directory (empty)
├── deployment/                   # Deployment scripts (empty)
├── docs/                         # Documentation
├── power_bi/                     # Power BI assets
├── sql/                          # SQL scripts and migrations
├── src/                          # Source code
├── streamlit/                    # Streamlit dashboard
├── tests/                        # Test suite
├── .dockerignore
├── .env
├── .env.example
├── .gitignore
├── .pytest_cache/
├── ARCHITECTURE.md
├── DATA_DICTIONARY.md
├── Dockerfile
├── Dockerfile.streamlit
├── PROJECT_CONSTITUTION.md
├── README.md
├── alembic.ini
├── docker-compose.dev.yml
├── docker-compose.streaming.yml
├── docker-compose.yml
├── pytest.ini
└── requirements.txt
```

## File Counts

### By Type

| File Type | Count | Notes |
|------------|-------|-------|
| Python Files (.py) | ~150+ | Estimated from directory listings |
| SQL Files (.sql) | 15 | Includes migrations, views, analytics |
| YAML/YML Files | 7 | Configuration files |
| Markdown Files (.md) | 30 | Documentation |
| Dockerfile Files | 2 | Main and Streamlit |
| Docker Compose Files | 3 | Main, dev, streaming |
| Test Files | 33+ | test_*.py and *_test.py patterns |
| Configuration Files | 10+ | .env, .ini, YAML |
| Total Files | ~250+ | Estimated |

### By Directory

| Directory | Python Files | SQL Files | Config Files | Test Files | Total |
|-----------|--------------|-----------|--------------|------------|-------|
| api/ | 25 | 0 | 1 | 2 | 28 |
| src/ | ~120+ | 0 | 0 | 0 | ~120+ |
| sql/ | 1 | 15 | 0 | 1 | 17 |
| tests/ | 33+ | 0 | 1 | 33+ | ~35 |
| streamlit/ | 14 | 0 | 1 | 0 | 15 |
| config/ | 0 | 0 | 7 | 0 | 7 |
| docs/ | 0 | 0 | 0 | 0 | 30 |
| power_bi/ | 0 | 0 | 0 | 0 | 3 |
| Root | 0 | 0 | 5 | 0 | 15 |

## Detailed Component Breakdown

### API Layer (`api/`)

**Routers:**
- `churn.py` - Churn analytics endpoints
- `customers.py` - Customer management endpoints
- `health.py` - Health check endpoints
- `portfolio.py` - Portfolio analytics endpoints
- `profitability.py` - Profitability analytics endpoints
- `realtime.py` - Real-time streaming endpoints
- `recommendations.py` - Recommendation endpoints
- `risk.py` - Risk analytics endpoints
- `segments.py` - Customer segmentation endpoints

**Schemas:**
- Pydantic schemas for all routers
- Common schemas (HealthResponse, etc.)

**Other:**
- `main.py` - FastAPI application entry point
- `config.py` - API configuration
- `database.py` - Database session management
- `websocket.py` - WebSocket support

### Source Code (`src/`)

**Analytics Modules:**
- `advanced_analytics/` - Scenario analysis
- `advanced_risk_analytics/` - Advanced risk analytics (12 files)
- `behavioral_analytics/` - Behavioral analytics
- `churn_analytics/` - Churn analytics (9 files)
- `clv_analytics/` - Customer lifetime value (8 files)
- `credit_risk_analytics/` - Credit risk analytics (11 files)
- `customer_intelligence/` - Customer intelligence
- `customer_segmentation/` - Customer segmentation (9 files)
- `decision_intelligence/` - Decision intelligence (9 files)
- `predictive_analytics/` - Predictive analytics (16 files)
- `profitability_analytics/` - Profitability analytics (10 files)
- `statistical_analytics/` - Statistical analytics (13 files)
- `transaction_analytics/` - Transaction analytics (8 files)

**Streaming Modules (NEW):**
- `streaming/` - Streaming infrastructure (47 files)
  - `alerts/` - Alert engine
  - `anomaly/` - Anomaly detection
  - `audit/` - Decision audit
  - `early_warning/` - Early warning system
  - `features/` - Feature store
  - `kafka/` - Kafka integration
  - `model_registry/` - Model registry
  - `observability/` - Metrics and monitoring
  - `orchestrator/` - Pipeline orchestrator
  - `parity/` - Feature parity validation
  - `processor/` - Stream processor
  - `reconciliation/` - Batch-stream reconciliation
  - `replay/` - Historical replay
  - `risk/` - Risk engine
  - `schemas/` - Event schemas

**Supporting Modules:**
- `core_analytics/` - Core analytics utilities
- `data_governance/` - Data governance
- `data_platform/` - Data platform utilities
- `data_quality/` - Data quality validation (7 files)
- `feature_engineering/` - Feature engineering
- `ingestion/` - Data ingestion (7 files)
- `ml/` - ML utilities (3 files)
- `models/` - SQLAlchemy models (5 files)
- `pipeline/` - Pipeline utilities
- `utils/` - Utilities (2 files)

### Database Layer (`sql/`)

**Migrations:**
- `migrations/env.py` - Alembic environment
- `migrations/versions/001_add_streaming_tables.py` - Streaming tables
- `migrations/versions/002_add_realtime_columns.py` - Real-time columns

**Schema:**
- `schema/schema.sql` - Base schema definition

**Analytics SQL:**
- `credit_risk_analytics.sql`
- `customer_360_views.sql`
- `profitability_analytics.sql`
- `transaction_analytics.sql`

**Views:**
- `views/vw_churn_retention.sql`
- `views/vw_customer_360_detail.sql`
- `views/vw_decision_intelligence.sql`
- `views/vw_executive_overview_kpi.sql`
- `views/vw_model_monitoring.sql`
- `views/vw_product_analytics.sql`
- `views/vw_profitability_trend.sql`
- `views/vw_risk_distribution.sql`
- `views/vw_segment_analysis.sql`
- `views/vw_transaction_analytics.sql`

### Test Suite (`tests/`)

**Unit Tests:**
- `unit/advanced_risk_analytics/`
- `unit/churn_analytics/`
- `unit/clv_analytics/`
- `unit/credit_risk_analytics/`
- `unit/customer_intelligence/`
- `unit/customer_segmentation/`
- `unit/data_quality/`
- `unit/decision_intelligence/`
- `unit/ingestion/`
- (and more - 56 total unit test files)

**Integration Tests:**
- `integration/test_analytics_orchestrator.py`
- `integration/test_infrastructure.py`

**Regression Tests:**
- `regression/test_critical_metrics.py`

**Data Quality Tests:**
- `data_quality/test_duplicate_handling.py`
- `data_quality/test_edge_cases.py`
- `data_quality/test_null_handling.py`

**API Tests:**
- `api/test_api_endpoints.py`

**ML Tests:**
- `ml/test_model_pipeline.py`

**SQL Tests:**
- `sql/test_view_syntax.py`

### Configuration (`config/`)

- `base.yaml` - Base configuration
- `environments/development.yaml` - Development environment
- `environments/production.yaml` - Production environment
- `ingestion.yaml` - Ingestion configuration
- `logging.yaml` - Logging configuration
- `replay.yaml` - Replay configuration
- `streaming.yaml` - Streaming configuration

### Documentation (`docs/`)

**Methodology Documents:**
- `ADVANCED_RISK_ANALYTICS_METHODOLOGY.md`
- `CHURN_ANALYTICS_METHODOLOGY.md`
- `CLV_METHODOLOGY.md`
- `CREDIT_RISK_METHODOLOGY.md`
- `CUSTOMER_SEGMENTATION_METHODOLOGY.md`
- `DECISION_INTELLIGENCE_METHODOLOGY.md`
- `PREDICTIVE_ANALYTICS_FRAMEWORK.md`
- `PROFITABILITY_METHODOLOGY.md`
- `STATISTICAL_ANALYTICS_METHODOLOGY.md`

**Technical Guides:**
- `DOCKER_SETUP_GUIDE.md`
- `ETL.md`
- `FASTAPI_IMPLEMENTATION_GUIDE.md`
- `STREAMING_INTEGRATION.md`
- `STREAMLIT_IMPLEMENTATION_GUIDE.md`
- `TESTING_GUIDE.md`

**Reference Documents:**
- `ARCHITECTURE.md` (root)
- `DATA_DICTIONARY.md` (root)
- `DATA_MODEL.md`
- `DATA_QUALITY_RULES.md`
- `CUSTOMER_360_METRICS.md`
- `TRANSACTION_KPIS.md`
- `POWER_BI_DATA_MODEL.md`
- `POWER_BI_IMPLEMENTATION_GUIDE.md`

**Other:**
- `ASSUMPTIONS_AND_LIMITATIONS.md`
- `deployment.md`
- `limitations.md`
- `streaming_database_schema.md`

### Streamlit Dashboard (`streamlit/`)

**Pages:**
- `pages/home.py`
- `pages/executive_overview.py`
- `pages/customer_360.py`
- `pages/profitability.py`
- `pages/risk.py`
- `pages/segmentation.py`
- `pages/churn.py`
- `pages/transactions.py`
- `pages/products.py`
- `pages/decision_intelligence.py`
- `pages/model_monitoring.py`
- `pages/data_quality.py`
- `pages/live_monitor.py` (NEW)

**Components:**
- `components/` - Reusable UI components

**Configuration:**
- `config.py` - Streamlit configuration

**Entry Point:**
- `app.py` - Main application

### Docker Configuration

**Dockerfiles:**
- `Dockerfile` - Main application
- `Dockerfile.streamlit` - Streamlit dashboard

**Compose Files:**
- `docker-compose.yml` - Main services
- `docker-compose.dev.yml` - Development overrides
- `docker-compose.streaming.yml` - Streaming services (Redpanda, Redis)

### Root Level Files

- `.dockerignore`
- `.env` (contains actual environment variables)
- `.env.example` (template)
- `.gitignore`
- `ARCHITECTURE.md`
- `DATA_DICTIONARY.md`
- `PROJECT_CONSTITUTION.md`
- `README.md`
- `alembic.ini` - Alembic configuration
- `pytest.ini` - Pytest configuration
- `requirements.txt` - Python dependencies

## Key Observations

1. **Streaming Infrastructure**: Recently added with 47 files in `src/streaming/`
2. **Test Coverage**: Extensive test suite with 56 unit test files
3. **Documentation**: Comprehensive documentation with 30+ markdown files
4. **Database**: Well-structured with migrations, views, and analytics SQL
5. **API**: Complete FastAPI application with 10 routers
6. **Dashboard**: Streamlit dashboard with 13 pages including new live monitor

## Next Steps

Proceed to PHASE 1: Architecture Audit to examine imports, dependencies, and architectural patterns.
