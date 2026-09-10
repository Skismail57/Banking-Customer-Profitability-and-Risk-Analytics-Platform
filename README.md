
# 🏦 Banking Customer Profitability & Risk Analytics Platform
<div align="center">

<img src="assets/github-cover.svg" alt="Banking Customer Profitability and Risk Analytics Platform" width="100%"/>

</div>
<div align="center">

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white) ![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white) ![Kafka](https://img.shields.io/badge/Kafka%2FRedpanda-231F20?style=for-the-badge&logo=apachekafka&logoColor=white)

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white) ![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white) ![Scikit Learn](https://img.shields.io/badge/Scikit--Learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white) ![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white) ![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white) ![License](https://img.shields.io/badge/License-MIT-black?style=for-the-badge)

</div>
> A portfolio-grade banking analytics platform that combines customer 360 analytics, profitability, credit risk, churn, segmentation, predictive modeling, statistical analysis, decision intelligence, API services and streaming-style monitoring in one modular Python system.

## 📌 Project at a Glance

| Area | Implementation |
|---|---|
| **Primary interface** | Streamlit multi-page analytics dashboard |
| **API** | FastAPI REST API with OpenAPI / Swagger / ReDoc |
| **Database design** | PostgreSQL + SQLAlchemy + dimensional/star-schema style facts and dimensions |
| **Analytics** | Profitability, credit risk, churn, CLV, segmentation, transaction, customer intelligence and statistics |
| **ML** | Churn, default risk, profitability, CLV and transaction anomaly models |
| **Streaming** | Kafka/Redpanda, Redis feature store, event-time processing, alerts, replay and reconciliation modules |
| **Data quality** | Pandera-based validation, quality metrics, lineage and monitoring |
| **Decision layer** | Configurable business rules and prioritized recommendations |
| **Deployment** | Docker, Docker Compose and Kubernetes manifests |
| **Automation** | GitHub Actions CI/CD workflows |
| **Documentation** | 70+ Markdown documents plus architecture, security, testing and methodology material |
| **Test suite** | 57 test files / 181 collected tests at inspection time |
| **Included UI evidence** | **64 screenshots**, grouped below so every screenshot renders in the README |

## 🎯 What This Project Solves

Banks often have customer, account, transaction, credit, profitability and engagement data spread across different systems. This project turns those domains into a unified analytical workflow that answers questions such as:

- Which customers generate the most revenue and net profit?
- Where is credit exposure concentrated?
- Which customers show high risk or delinquency signals?
- Which customers are most likely to churn?
- Which products contribute revenue, balances and risk?
- How do customer segments differ in value and behavior?
- What actions should an executive or relationship manager consider?
- How can risk, churn and anomaly signals be monitored continuously?

## 🧩 Core Analytics Domains

### 1. Customer 360
Unified customer profile combining demographic attributes, balances, profitability, CLV, risk information and recent transactions.

### 2. Profitability Analytics
Revenue and cost decomposition, net profit, margin, ROA/ROE-oriented metrics, customer/product/account analysis, temporal analysis and profitability tiers.

### 3. Credit Risk Analytics
Credit utilization, debt burden, repayment behavior, delinquency, exposure, default indicators, risk scoring, risk bands and portfolio-level risk analysis.

### 4. Churn & Retention Analytics
Churn feature engineering, probability scoring, cohort/rate analysis, evaluation and identification of high-churn customers.

### 5. Customer Lifetime Value
Historical, estimated and predicted CLV, retention adjustments and sensitivity analysis around retention, revenue, costs and discount assumptions.

### 6. Customer Segmentation
Business-rule segmentation plus K-Means, hierarchical and DBSCAN clustering, cluster evaluation, profiling and stability analysis.

### 7. Transaction Analytics
Transaction KPIs, debit/credit flows, frequency, behavior, trends and anomaly detection.

### 8. Statistical Analytics
Descriptive statistics, correlation, confidence intervals, t-tests, chi-square, ANOVA, non-parametric tests and regression.

### 9. Predictive Analytics
Reusable preprocessing, splitting, baseline comparison, imbalance handling, cross-validation, hyperparameter tuning, evaluation and model persistence.

### 10. Decision Intelligence
Rule-driven recommendations that combine profitability, risk, churn, CLV, exposure and segment signals into prioritized actions.

### 11. Streaming Intelligence
Event-time processing, watermarks, late-event handling, schema validation, feature-store adapters, anomaly/risk engines, alerts, audit trails, replay and batch-stream reconciliation.

## 🏗️ Architecture

```mermaid
flowchart LR
    A[Source Data / Events] --> B[Ingestion]
    B --> C[Validation & Data Quality]
    C --> D[Transformation / Feature Engineering]
    D --> E[(PostgreSQL Data Warehouse)]
    D --> F[Analytics Engines]
    D --> G[Streaming Pipeline]
    G --> H[(Redis Feature Store)]
    G --> I[Risk / Anomaly / Alert Engines]
    F --> J[Predictive Models]
    J --> K[Decision Intelligence]
    E --> L[FastAPI]
    F --> L
    K --> L
    I --> L
    L --> M[Streamlit Dashboard]
    L --> N[External Consumers]
    E --> O[Power BI Template]
```

### Architectural layers

| Layer | Main responsibilities | Key modules |
|---|---|---|
| **Ingestion** | Extract, clean and load source data | `src/ingestion/` |
| **Data quality & governance** | Schema validation, quality metrics, lineage | `src/data_quality/`, `src/data_governance/` |
| **Data platform** | Load customer, transaction, product and analytical datasets | `src/data_platform/` |
| **Core analytics** | Business metrics and aggregations | `src/core_analytics/`, `src/analytics/` |
| **Risk & profitability** | Credit risk and value analysis | `src/credit_risk_analytics/`, `src/profitability_analytics/` |
| **Customer intelligence** | 360, segmentation, CLV and churn | `src/customer_intelligence/`, `src/customer_segmentation/`, `src/clv_analytics/`, `src/churn_analytics/` |
| **Predictive ML** | Training, evaluation and persistence | `src/predictive_analytics/`, `src/ml/` |
| **Decision layer** | Rule engine and recommendations | `src/decision_intelligence/` |
| **Streaming** | Event processing and real-time decision signals | `src/streaming/` |
| **API** | Authenticated service interface | `api/` |
| **Presentation** | Interactive dashboards | `frontend/` |
| **Deployment** | Containers, Kubernetes and CI/CD | `Dockerfile*`, `k8s/`, `.github/workflows/` |

## 🗃️ Data Model

The SQL schema defines dimension and fact tables including:

**Dimensions**
- `dim_date`
- `dim_customer`
- `dim_product`
- `dim_channel`
- customer/account/branch/segment dimensions in SQLAlchemy models

**Facts**
- `fact_customer_metrics`
- `fact_transactions`
- `fact_loan`
- `fact_account`
- `fact_payment`
- `fact_customer_profitability`
- `fact_recommendations`
- `fact_model_performance`
- `fact_data_quality`
- streaming/event, prediction, anomaly, alert, audit, reconciliation and replay facts

The repository also contains SQL analytical views for executive overview, customer 360, profitability trends, risk distribution, churn/retention, product analytics, transaction analytics, segmentation, decision intelligence and model monitoring.

## 🤖 Machine Learning & Predictive Analytics

The predictive layer is designed as a reusable framework rather than a single notebook. It contains:

- **Churn prediction** — binary classification
- **Default-risk prediction** — binary classification
- **Profitability prediction** — regression
- **CLV prediction** — regression
- **Transaction anomaly detection** — anomaly detection
- Baseline model comparison
- Time-aware and train/validation/test splitting
- Preprocessing pipelines
- Class-imbalance handling
- Cross-validation and hyperparameter tuning
- Model evaluation and feature importance
- Model persistence and metadata
- Model monitoring and drift detection

The repository documents these methods and their assumptions in `docs/PREDICTIVE_ANALYTICS_FRAMEWORK.md` and related methodology files.

## 📡 Streaming & Real-Time Design

The streaming subsystem is unusually broad for an analytics portfolio project. It includes:

- Kafka/Redpanda producers, consumers, topics and consumer groups
- Event schemas and schema-registry integration
- Event-time processing and watermarks
- Late-event handling
- Stateful processing
- Redis-backed feature-store components
- Online model registry/inference components
- Risk scoring and anomaly adapters
- Early-warning and alert engines
- Decision audit trail
- Dead-letter queues and retry/backoff
- Circuit-breaker/backpressure reliability components
- Historical replay
- Batch-stream reconciliation
- Performance/load/stress testing
- Chaos scenarios and recovery validation

The streaming configuration defines topics for raw/validated events, customer/account features, risk and churn predictions, fraud anomalies, risk alerts, replay input/output and a dead-letter queue.

## 🔐 API, Security & Governance

The FastAPI layer exposes health, authentication, customer, profitability, risk, segmentation, churn, portfolio and realtime routes. Authentication is implemented with JWT-based security, while middleware includes security headers and correlation IDs; rate limiting is provided through `slowapi`.

Security-oriented repository material also covers authentication, authorization, WebSocket security, attack-surface review, dependency scanning, audit trails and production security architecture.

### Representative API surface

| Route | Purpose |
|---|---|
| `GET /` | API root and service metadata |
| `GET /api/v1/health` | Health check |
| `GET /api/v1/health/ready` | Readiness check |
| `GET /api/v1/health/live` | Liveness check |
| `POST /api/v1/auth/login` | JWT login |
| `GET /api/v1/auth/me` | Current-user information |
| `GET /api/v1/customers` | Customer listing/search |
| `GET /api/v1/customers/{id}` | Customer detail |
| `GET /api/v1/profitability/aggregate` | Profitability KPIs |
| `GET /api/v1/risk/aggregate` | Risk KPIs |
| `GET /api/v1/churn/aggregate` | Churn KPIs |
| `GET /api/v1/segments` | Customer segments |
| `GET /api/v1/portfolio/summary` | Portfolio summary |
| `GET /api/v1/realtime/alerts` | Realtime alerts |
| `GET /api/v1/realtime/metrics` | Streaming metrics |

Swagger and ReDoc screenshots are included later in this README.

## 🖥️ Dashboard Experience

The Streamlit application is organized into business-facing pages:

1. Home
2. Executive Overview
3. Customer 360
4. Credit Risk Analytics
5. Profitability Analytics
6. Churn Analytics
7. Transaction Analytics
8. Product Analytics
9. Customer Segmentation
10. Decision Intelligence
11. Model Monitoring
12. Data Quality Monitoring
13. Live Monitor

The UI uses interactive filters, KPI cards, Plotly charts, tables, recommendation panels and real-time-style monitoring views.

## 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| **Language** | Python 3.11+ |
| **Data processing** | Pandas, Polars, NumPy |
| **Data validation** | Pandera |
| **Statistics** | SciPy, Statsmodels |
| **Machine learning** | Scikit-learn, imbalanced-learn |
| **Database** | PostgreSQL, SQLAlchemy, Alembic |
| **API** | FastAPI, Pydantic, Uvicorn |
| **Authentication/security** | JWT, python-jose, Passlib/Bcrypt, SlowAPI, Bandit, pip-audit |
| **Visualization** | Plotly |
| **Dashboard** | Streamlit |
| **Streaming** | Confluent Kafka client, Kafka/Redpanda |
| **Feature store/cache** | Redis |
| **Testing** | pytest, pytest-cov, pytest-mock, pytest-asyncio |
| **Containerization** | Docker, Docker Compose |
| **Orchestration** | Kubernetes |
| **CI/CD** | GitHub Actions |
| **BI** | Power BI template (`.pbit`) |

## 📁 Repository Structure

```text
.
├── api/                    # FastAPI application, auth, middleware and routers
├── frontend/               # Streamlit application and dashboard pages
├── src/                    # Analytics, ML, data platform and streaming modules
├── sql/                    # Schema, analytical SQL, views and migrations
├── config/                 # Environment and streaming configuration
├── data/                   # Data pipeline directories
├── models/                 # Model-related project assets
├── power_bi/               # Power BI template and setup documentation
├── k8s/                    # Kubernetes production manifests
├── docs/                   # Methodologies, architecture, security and deployment docs
├── tests/                  # Unit, integration, API, SQL, ML, security and load tests
├── Project Screenshots/    # Original 64 UI/API screenshots
├── Dockerfile*             # Container definitions
├── docker-compose*.yml     # Compose configurations
├── .github/workflows/      # CI/CD workflows
├── DATA_DICTIONARY.md      # Data definitions and business fields
├── ARCHITECTURE.md         # Architecture reference
└── PROJECT_CONSTITUTION.md # Engineering principles
```

## 📸 Complete Project Screenshots

**All 64 screenshots from the project archive are included below.** They have been copied to clean, GitHub-safe filenames under `assets/screenshots/` so filenames containing spaces or `#` characters do not break image rendering.

### 🏠 Home & Platform Introduction

The landing experience, onboarding guidance, platform scope, navigation and data-source architecture.

<div align="center">

<img src="assets/screenshots/01-home/home-tab-getting-started-guide-and-platform-statistics-kpi-cards-10-000-customers-1m-data-points.png" alt="Getting Started guide and platform-statistics cards" width="100%"/>

**1. Getting Started guide and platform-statistics cards**

</div>

<div align="center">

<img src="assets/screenshots/01-home/home-tab-quick-navigation-and-data-source-architecture-description.png" alt="Home tab Quick Navigation and Data Source architecture description." width="100%"/>

**2. Home tab Quick Navigation and Data Source architecture description.**

</div>

<div align="center">

<img src="assets/screenshots/01-home/home-tab-welcome-to-the-banking-customer-profitability-and-risk-analytics-platform-core-overview.png" alt="Platform welcome page and core overview" width="100%"/>

**3. Platform welcome page and core overview**

</div>

### 📊 Executive Overview

Executive-level KPIs, filters, recommendations, customer summaries and portfolio analytics.

<div align="center">

<img src="assets/screenshots/02-executive-overview/executive-overview-tab-customer-metrics-summary-data-table-view.png" alt="Executive Overview customer metrics summary table" width="100%"/>

**1. Executive Overview customer metrics summary table**

</div>

<div align="center">

<img src="assets/screenshots/02-executive-overview/executive-overview-tab-date-range-region-and-segment-filter-options.png" alt="Executive Overview date, region and segment filters" width="100%"/>

**2. Executive Overview date, region and segment filters**

</div>

<div align="center">

<img src="assets/screenshots/02-executive-overview/executive-overview-tab-expanded-executive-recommendations-profitability-risk-growth-action-items.png" alt="Expanded executive recommendations: profitability, risk and growth" width="100%"/>

**3. Expanded executive recommendations: profitability, risk and growth**

</div>

<div align="center">

<img src="assets/screenshots/02-executive-overview/executive-overview-tab-key-performance-indicators-total-customers-revenue-profit-high-risk-and-top-recommendations.png" alt="Executive Overview KPIs and top recommendations" width="100%"/>

**4. Executive Overview KPIs and top recommendations**

</div>

<div align="center">

<img src="assets/screenshots/02-executive-overview/executive-overview-tab-revenue-by-customer-line-chart-risk-score-by-level-bar-chart.png" alt="Revenue by customer and risk score by level charts" width="100%"/>

**5. Revenue by customer and risk score by level charts**

</div>

### 👤 Customer 360

Unified customer profile, profitability, risk, CLV and recent transaction views.

<div align="center">

<img src="assets/screenshots/03-customer-360/customer-360-revenue-vs-profit-risk-vs-clv-charts.png" alt="Customer 360 revenue vs profit and risk vs CLV charts" width="100%"/>

**1. Customer 360 revenue vs profit and risk vs CLV charts**

</div>

<div align="center">

<img src="assets/screenshots/03-customer-360/customer-360-risk-info-recent-transactions-table.png" alt="Customer 360 risk information and recent transactions" width="100%"/>

**2. Customer 360 risk information and recent transactions**

</div>

<div align="center">

<img src="assets/screenshots/03-customer-360/customer-360-tab-customer-metrics-cards-revenue-net-profit-risk-score-clv-and-risk-information.png" alt="Customer 360 metrics cards and risk information" width="100%"/>

**3. Customer 360 metrics cards and risk information**

</div>

<div align="center">

<img src="assets/screenshots/03-customer-360/customer-360-tab-customer-search-bar-and-initial-customer-profile-info-nasir-khan.png" alt="Customer search and initial customer profile" width="100%"/>

**4. Customer search and initial customer profile**

</div>

### ⚠️ Credit Risk Analytics

Risk KPIs, risk bands, exposure, delinquency and detailed customer risk analysis.

<div align="center">

<img src="assets/screenshots/04-credit-risk/credit-risk-detailed-risk-analysis-delinquency-table.png" alt="Detailed credit-risk analysis and delinquency table" width="100%"/>

**1. Detailed credit-risk analysis and delinquency table**

</div>

<div align="center">

<img src="assets/screenshots/04-credit-risk/credit-risk-header-filter-selection-panel.png" alt="Credit Risk header and filter selection panel" width="100%"/>

**2. Credit Risk header and filter selection panel**

</div>

<div align="center">

<img src="assets/screenshots/04-credit-risk/credit-risk-risk-kpis-high-risk-count-avg-score-total-exposure.png" alt="Credit Risk KPIs: high-risk count, average score and exposure" width="100%"/>

**3. Credit Risk KPIs: high-risk count, average score and exposure**

</div>

<div align="center">

<img src="assets/screenshots/04-credit-risk/credit-risk-risk-score-by-level-exposure-charts.png" alt="Risk score by level and exposure charts" width="100%"/>

**4. Risk score by level and exposure charts**

</div>

### 💰 Profitability Analytics

Revenue, profit, customer profitability metrics and profitability distributions.

<div align="center">

<img src="assets/screenshots/05-profitability/profitability-customer-profitability-metrics-data-table.png" alt="Customer profitability metrics table" width="100%"/>

**1. Customer profitability metrics table**

</div>

<div align="center">

<img src="assets/screenshots/05-profitability/profitability-header-filter-controls-top-layout.png" alt="Profitability header, filters and top layout" width="100%"/>

**2. Profitability header, filters and top layout**

</div>

<div align="center">

<img src="assets/screenshots/05-profitability/profitability-key-performance-indicators-revenue-profit-customers.png" alt="Profitability KPIs: revenue, profit and customers" width="100%"/>

**3. Profitability KPIs: revenue, profit and customers**

</div>

<div align="center">

<img src="assets/screenshots/05-profitability/profitability-revenue-profit-distribution-by-customer-charts.png" alt="Revenue and profit distributions by customer" width="100%"/>

**4. Revenue and profit distributions by customer**

</div>

### 🔄 Churn Analytics

Churn KPIs, probability distributions, customer predictions and high-risk retention lists.

<div align="center">

<img src="assets/screenshots/06-churn/churn-analytics-header-filter-options-kpi-preview.png" alt="Churn Analytics header, filters and KPI preview" width="100%"/>

**1. Churn Analytics header, filters and KPI preview**

</div>

<div align="center">

<img src="assets/screenshots/06-churn/churn-kpis-high-churn-risk-avg-churn-probability-total-customers.png" alt="Churn KPIs: high-risk count, average probability and customers" width="100%"/>

**2. Churn KPIs: high-risk count, average probability and customers**

</div>

<div align="center">

<img src="assets/screenshots/06-churn/churn-predictions-customer-probability-risk-table.png" alt="Customer churn predictions with probability and risk band" width="100%"/>

**3. Customer churn predictions with probability and risk band**

</div>

<div align="center">

<img src="assets/screenshots/06-churn/churn-risk-churn-probability-distribution-charts.png" alt="Churn-risk and churn-probability distributions" width="100%"/>

**4. Churn-risk and churn-probability distributions**

</div>

<div align="center">

<img src="assets/screenshots/06-churn/filtered-high-churn-risk-customers-table.png" alt="Filtered high-churn-risk customer table" width="100%"/>

**5. Filtered high-churn-risk customer table**

</div>

### 📦 Product Analytics

Product KPIs, revenue/customer distribution, balances and non-performing-loan monitoring.

<div align="center">

<img src="assets/screenshots/07-product-analytics/product-analytics-average-balance-chart-view.png" alt="Product Analytics average-balance chart" width="100%"/>

**1. Product Analytics average-balance chart**

</div>

<div align="center">

<img src="assets/screenshots/07-product-analytics/product-analytics-filters-key-performance-indicators.png" alt="Product Analytics filters and KPIs" width="100%"/>

**2. Product Analytics filters and KPIs**

</div>

<div align="center">

<img src="assets/screenshots/07-product-analytics/product-analytics-header-productsegment-filters.png" alt="Product Analytics header and product/segment filters" width="100%"/>

**3. Product Analytics header and product/segment filters**

</div>

<div align="center">

<img src="assets/screenshots/07-product-analytics/product-analytics-kpis-product-performance-breakdown-table.png" alt="Product KPIs and product-performance breakdown" width="100%"/>

**4. Product KPIs and product-performance breakdown**

</div>

<div align="center">

<img src="assets/screenshots/07-product-analytics/product-analytics-non-performing-loan-npl-rate-chart-view.png" alt="Product Analytics NPL-rate chart" width="100%"/>

**5. Product Analytics NPL-rate chart**

</div>

<div align="center">

<img src="assets/screenshots/07-product-analytics/product-analytics-total-revenue-customer-distribution-charts.png" alt="Product revenue and customer-distribution charts" width="100%"/>

**6. Product revenue and customer-distribution charts**

</div>

### 💳 Transaction Analytics

Transaction KPIs, transaction-type/product breakdowns, filters and recent transaction data.

<div align="center">

<img src="assets/screenshots/08-transaction-analytics/transaction-analytics-header-description-filter-controls.png" alt="Transaction Analytics header, description and filters" width="100%"/>

**1. Transaction Analytics header, description and filters**

</div>

<div align="center">

<img src="assets/screenshots/08-transaction-analytics/transaction-analytics-key-performance-indicators-kpi-cards.png" alt="Transaction Analytics KPI cards" width="100%"/>

**2. Transaction Analytics KPI cards**

</div>

<div align="center">

<img src="assets/screenshots/08-transaction-analytics/transaction-analytics-recent-transactions-data-table.png" alt="Recent transactions table" width="100%"/>

**3. Recent transactions table**

</div>

<div align="center">

<img src="assets/screenshots/08-transaction-analytics/transaction-analytics-volume-by-type-product-bar-charts.png" alt="Transaction volume by type and product" width="100%"/>

**4. Transaction volume by type and product**

</div>

### 🧠 Decision Intelligence

Decision KPIs, filtering and executive recommendations generated from business rules.

<div align="center">

<img src="assets/screenshots/09-decision-intelligence/decision-intelligence-u2013-executive-recommendations.png" alt="Decision Intelligence executive recommendations" width="100%"/>

**1. Decision Intelligence executive recommendations**

</div>

<div align="center">

<img src="assets/screenshots/09-decision-intelligence/decision-intelligence-u2013-header-filter-controls.png" alt="Decision Intelligence header and filter controls" width="100%"/>

**2. Decision Intelligence header and filter controls**

</div>

<div align="center">

<img src="assets/screenshots/09-decision-intelligence/decision-intelligence-u2013-kpi-metrics-overview.png" alt="Decision Intelligence KPI overview" width="100%"/>

**3. Decision Intelligence KPI overview**

</div>

### 📡 Live Monitor & Streaming Alerts

Streaming-style operational monitoring, metrics, watchlists and multiple alert severities.

<div align="center">

<img src="assets/screenshots/10-live-monitor/live-monitor-u2013-payment-failure-anomaly-alerts.png" alt="Payment-failure and anomaly alerts" width="100%"/>

**1. Payment-failure and anomaly alerts**

</div>

<div align="center">

<img src="assets/screenshots/10-live-monitor/live-monitor-u2013-real-time-streaming-analytics-metrics.png" alt="Real-time streaming analytics metrics" width="100%"/>

**2. Real-time streaming analytics metrics**

</div>

<div align="center">

<img src="assets/screenshots/10-live-monitor/live-monitor-u2013-recent-alerts-feed-highmedium.png" alt="Recent alerts feed with severity levels" width="100%"/>

**3. Recent alerts feed with severity levels**

</div>

<div align="center">

<img src="assets/screenshots/10-live-monitor/live-monitor-view-displaying-account-anomaly-low-high-and-high-transaction-volume-medium-alerts.png" alt="Account anomaly and high-transaction-volume alerts" width="100%"/>

**4. Account anomaly and high-transaction-volume alerts**

</div>

<div align="center">

<img src="assets/screenshots/10-live-monitor/live-monitor-view-displaying-risk-threshold-exceeded-high-medium-and-payment-failure-alerts.png" alt="Risk-threshold and payment-failure alerts" width="100%"/>

**5. Risk-threshold and payment-failure alerts**

</div>

<div align="center">

<img src="assets/screenshots/10-live-monitor/live-monitor-view-highlighting-payment-failure-critical-and-suspicious-activity-critical-alerts.png" alt="Critical payment-failure and suspicious-activity alerts" width="100%"/>

**6. Critical payment-failure and suspicious-activity alerts**

</div>

<div align="center">

<img src="assets/screenshots/10-live-monitor/live-monitor-view-showing-risk-threshold-exceeded-low-payment-failure-low-and-suspicious-activity-alerts.png" alt="Low-severity threshold, payment and suspicious-activity alerts" width="100%"/>

**7. Low-severity threshold, payment and suspicious-activity alerts**

</div>

<div align="center">

<img src="assets/screenshots/10-live-monitor/live-monitor-view-showing-risk-threshold-exceeded-high-transaction-volume-and-payment-failure-medium-alerts.png" alt="Mixed medium-severity streaming alerts" width="100%"/>

**8. Mixed medium-severity streaming alerts**

</div>

### 🤖 Model Monitoring

Model monitoring configuration, KPI summaries and model-performance tables.

<div align="center">

<img src="assets/screenshots/11-model-monitoring/model-monitoring-u2013-header-configuration.png" alt="Model Monitoring header and configuration" width="100%"/>

**1. Model Monitoring header and configuration**

</div>

<div align="center">

<img src="assets/screenshots/11-model-monitoring/model-monitoring-u2013-kpi-summary-cards.png" alt="Model Monitoring KPI summary cards" width="100%"/>

**2. Model Monitoring KPI summary cards**

</div>

<div align="center">

<img src="assets/screenshots/11-model-monitoring/model-monitoring-u2013-performance-metrics-table.png" alt="Model Monitoring performance metrics table" width="100%"/>

**3. Model Monitoring performance metrics table**

</div>

### ✅ Data Quality Monitoring

Data-quality dashboard and table-level quality metrics.

<div align="center">

<img src="assets/screenshots/12-data-quality/data-quality-monitoring-u2013-dashboard-metrics-table.png" alt="Data Quality Monitoring dashboard and metrics table" width="100%"/>

**1. Data Quality Monitoring dashboard and metrics table**

</div>

### 🎯 Customer Segmentation

Segment KPIs, customer segment tables, filters, distributions and balance analysis.

<div align="center">

<img src="assets/screenshots/13-segmentation/average-balance-by-segment-bar-chart.png" alt="Average balance by customer segment" width="100%"/>

**1. Average balance by customer segment**

</div>

<div align="center">

<img src="assets/screenshots/13-segmentation/customer-segments-data-table.png" alt="Customer segments data table" width="100%"/>

**2. Customer segments data table**

</div>

<div align="center">

<img src="assets/screenshots/13-segmentation/distribution-revenue-by-segment-bar-charts.png" alt="Segment distribution and revenue by segment" width="100%"/>

**3. Segment distribution and revenue by segment**

</div>

<div align="center">

<img src="assets/screenshots/13-segmentation/segmentation-kpis-total-segments-largest-segment-total-customers.png" alt="Segmentation KPIs: total segments, largest segment and customers" width="100%"/>

**4. Segmentation KPIs: total segments, largest segment and customers**

</div>

<div align="center">

<img src="assets/screenshots/13-segmentation/customer-segmentation-filters.png" alt="Customer segmentation filters" width="100%"/>

**5. Customer segmentation filters**

</div>

### 🔌 API Documentation

Swagger UI, ReDocly, OpenAPI schema, root response and health/readiness/liveness views.

<div align="center">

<img src="assets/screenshots/14-api-documentation/json-output-from-the-root-api-endpoint-listing-links-for-docs-health-auth-and-websocket-routes.png" alt="Root API JSON response and route links" width="100%"/>

**1. Root API JSON response and route links**

</div>

<div align="center">

<img src="assets/screenshots/14-api-documentation/json-response-from-the-health-endpoint-displaying-status-degraded-version-and-database-state.png" alt="Health endpoint JSON response" width="100%"/>

**2. Health endpoint JSON response**

</div>

<div align="center">

<img src="assets/screenshots/14-api-documentation/openapi-3-1-0-json-specification-schema-showing-api-info-and-health-check-paths.png" alt="OpenAPI 3.1 JSON specification view" width="100%"/>

**3. OpenAPI 3.1 JSON specification view**

</div>

<div align="center">

<img src="assets/screenshots/14-api-documentation/redocly-ui-showing-documentation-and-response-samples-for-apiv1healthready-and-apiv1healthlive.png" alt="ReDocly response samples for readiness and liveness endpoints" width="100%"/>

**4. ReDocly response samples for readiness and liveness endpoints**

</div>

<div align="center">

<img src="assets/screenshots/14-api-documentation/swagger-ui-documentation-page-showing-the-openapi-3-1-title-banner-authorize-button-and-endpoint-lists.png" alt="Swagger UI with OpenAPI title, authorization and endpoint lists" width="100%"/>

**5. Swagger UI with OpenAPI title, authorization and endpoint lists**

</div>

<div align="center">

<img src="assets/screenshots/14-api-documentation/top-level-redocly-documentation-interface-displaying-the-banking-analytics-api-title-version-and-initial-health-check-section.png" alt="Top-level ReDocly API documentation interface" width="100%"/>

**6. Top-level ReDocly API documentation interface**

</div>

### 🖨️ Export, Print & Recording

Dashboard print/export workflow and Streamlit/browser recording prompts.

<div align="center">

<img src="assets/screenshots/15-export-recording/shows-the-executive-overview-dashboard-page-inside-the-browser-s-save-as-pdf-print-preview-dialog.png" alt="Browser print preview / Save as PDF workflow" width="100%"/>

**1. Browser print preview / Save as PDF workflow**

</div>

<div align="center">

<img src="assets/screenshots/15-export-recording/shows-the-streamlit-record-a-screencast-overlay-modal-on-the-executive-overview-page.png" alt="Streamlit screencast recording overlay" width="100%"/>

**2. Streamlit screencast recording overlay**

</div>

<div align="center">

<img src="assets/screenshots/15-export-recording/shows-the-browser-prompt-asking-to-choose-and-share-the-screen.png" alt="Browser screen-sharing permission prompt" width="100%"/>

**3. Browser screen-sharing permission prompt**

</div>

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 15 recommended for the included Compose setup
- Redis 7 for streaming/feature-store functionality
- Kafka/Redpanda for streaming functionality
- Git
- Docker + Docker Compose (optional)

### 1. Clone and enter the project

```bash
git clone <your-repository-url>
cd "Banking Customer Profitability and Risk Analytics Platform"
```

### 2. Create a virtual environment

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

For API-focused installation:

```bash
pip install -r requirements-api.txt
```

### 4. Configure environment

```bash
cp .env.example .env
```

On Windows, copy `.env.example` to `.env` manually if `cp` is unavailable. Set database and JWT values before running production-like services.

### 5. Run the Streamlit dashboard

The current repository entry point is:

```bash
streamlit run frontend/app.py --server.port 8501
```

### 6. Run the FastAPI service

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Then open:

- Dashboard: `http://localhost:8501`
- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`
- Health: `http://localhost:8000/api/v1/health`

### 7. Database migrations

The repository includes Alembic configuration and migration scripts. Configure the target database first, then use:

```bash
alembic upgrade head
```

## 🧪 Testing

The archive contains **57 test files** spanning analytics, API, data quality, integration, load, ML, regression, security, SQL and extensive unit-test modules.

Run the full suite with:

```bash
pytest tests/ -v
```

### Inspection result for this archive

At the time this README was prepared, the test runner collected **181 tests but stopped during collection with 5 errors**. The observed blockers included:

- an `IndentationError` in `tests/api/test_api_endpoints.py`;
- a missing `Optional` import in `src/advanced_risk_analytics/trend_monitoring.py`;
- missing runtime dependencies in the inspection environment (`jose` and `pandera`).

Therefore, this README intentionally **does not claim that the current checkout has a fully passing test suite**. Fixing those blockers and rerunning CI should be part of the next hardening pass.

## ⚠️ Important Implementation Notes

This section is intentionally explicit so the README reflects the repository rather than overstating it.

### Synthetic/mock dashboard data

Most Streamlit analytics pages currently instantiate `MockDataLoader`. The mock generator creates approximately **1,000 customers and 10,000 transactions** for local/demo analytics. The UI screenshots contain labels such as “10,000+ customers” and “1M+ data points”; those labels should be treated as presentation/demo content rather than verified current dataset volume.

### Empty local SQLite artifact

The archived `banking_analytics.db` file is 0 bytes. The project itself is designed around PostgreSQL for the primary database layer, with SQLAlchemy and Alembic support.

### Docker/Compose alignment

The repository contains Docker and Compose configurations, but the current Compose/Streamlit paths should be reconciled before calling the containerized setup production-ready. In particular, the Compose configuration references `./streamlit` and `streamlit/home.py`, while the current dashboard implementation is under `frontend/app.py`; the Compose file also mounts `./sql/init`, which is not present in the archive.

### Production-readiness wording

The repository's internal remediation documentation reports a **9.0/10 production-readiness score**. That is an internal project assessment, not an independent certification. Because the current archive still has test-collection failures and deployment-path inconsistencies, the safer description is **“production-oriented / production-readiness work implemented”** rather than “verified production-ready.”

### Financial decision disclaimer

The analytics and ML components are intended for portfolio, educational and decision-support use. They should not be used as an automated lending, credit approval or financial-advice system without appropriate validation, governance, compliance review, bias testing, monitoring and human oversight.

## 📚 Documentation Map

The project contains a substantial documentation layer. Useful starting points include:

| Document | Purpose |
|---|---|
| `ARCHITECTURE.md` | System architecture and module responsibilities |
| `DATA_DICTIONARY.md` | Core fields, metrics, relationships and data-quality rules |
| `PROJECT_CONSTITUTION.md` | Engineering principles and project standards |
| `docs/PROFITABILITY_METHODOLOGY.md` | Profitability definitions and calculations |
| `docs/CREDIT_RISK_METHODOLOGY.md` | Credit-risk methodology |
| `docs/ADVANCED_RISK_ANALYTICS_METHODOLOGY.md` | Advanced risk, concentration, migration and early-warning analysis |
| `docs/CHURN_ANALYTICS_METHODOLOGY.md` | Churn methodology |
| `docs/CLV_METHODOLOGY.md` | CLV methodology |
| `docs/CUSTOMER_SEGMENTATION_METHODOLOGY.md` | Business rules, clustering and stability |
| `docs/PREDICTIVE_ANALYTICS_FRAMEWORK.md` | ML framework and evaluation |
| `docs/STATISTICAL_ANALYTICS_METHODOLOGY.md` | Statistical methods and business tests |
| `docs/DECISION_INTELLIGENCE_METHODOLOGY.md` | Recommendation rules and prioritization |
| `docs/STREAMING_ARCHITECTURE.md` | Streaming architecture and processing semantics |
| `docs/DATA_QUALITY_RULES.md` | Data quality controls |
| `docs/security/` | Security architecture and security reviews |
| `docs/PRODUCTION_READINESS_CHECKLIST.md` | Production-readiness checklist |
| `docs/DEPLOYMENT_GUIDE.md` | Deployment guidance |

## 🗺️ Recommended Next Hardening Steps

1. **Fix test collection errors** and establish a green CI baseline.
2. **Align Docker Compose paths** with `frontend/app.py` and the actual SQL initialization layout.
3. **Connect dashboard pages to the real PostgreSQL `DataLoader`** where production-like data is available, while retaining `MockDataLoader` as an explicit demo mode.
4. **Add a reproducible seed/load command** for a documented synthetic dataset.
5. **Verify every model with real train/validation/test artifacts** and store measured metrics rather than example values.
6. **Add observability dashboards** for API, streaming, database and model-health SLIs/SLOs.
7. **Harden secrets/configuration** and avoid shipping local `.env` files or credentials in repositories.
8. **Add database migrations/initialization verification** to CI.
9. **Validate Kubernetes manifests in CI** with schema/lint checks and environment-specific configuration.
10. **Document a single canonical deployment path** for local, staging and production environments.

## 📄 License

This project is released under the **MIT License**. See [`LICENSE`](LICENSE).

## 👨‍💻 Author

**S K Ismail**

Backend Developer | AI/ML Engineer | Cloud & DevOps Enthusiast

---

<div align="center">

**Banking Customer Profitability & Risk Analytics Platform**  
*From customer data → analytics → prediction → risk intelligence → business decisions*

</div>
