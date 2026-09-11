# Banking Customer Profitability and Risk Analytics Platform

[![CI Pipeline](https://github.com/Skismail57/Banking-Customer-Profitability-and-Risk-Analytics-Platform/actions/workflows/ci.yml/badge.svg)](https://github.com/Skismail57/Banking-Customer-Profitability-and-Risk-Analytics-Platform/actions/workflows/ci.yml)
[![CD Pipeline](https://github.com/Skismail57/Banking-Customer-Profitability-and-Risk-Analytics-Platform/actions/workflows/cd.yml/badge.svg)](https://github.com/Skismail57/Banking-Customer-Profitability-and-Risk-Analytics-Platform/actions/workflows/cd.yml)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.14-blue)](#)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141-teal)](#)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.63-FF4B4B)](#)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)](#)
[![Pandera](https://img.shields.io/badge/Pandera-0.33-E94E5C)](#)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](#)

![Banking Customer Profitability and Risk Analytics Platform - Cover](Screenshots/Github%20Image.png)

> **Production-grade, end-to-end banking analytics platform** that unifies customer profitability measurement, credit risk scoring, churn prediction, customer segmentation, real-time transaction monitoring, executive decision intelligence, and model observability into one cohesive FastAPI + Streamlit + PostgreSQL data warehouse application.

---

## Table of Contents

| # | Section | # | Section |
|---|---------|---|---------|
| 1 | [Project Overview](#1-project-overview)  | 19 | [Database Setup](#19-database-setup) |
| 2 | [Business Problem](#2-business-problem) | 20 | [Running the Backend](#20-running-the-backend) |
| 3 | [Solution](#3-solution) | 21 | [Running the Frontend](#21-running-the-frontend) |
| 4 | [Key Highlights](#4-key-highlights) | 22 | [Docker Setup](#22-docker-setup) |
| 5 | [Features](#5-features) | 23 | [Testing](#23-testing) |
| 6 | [Architecture](#6-architecture) | 24 | [Code Quality](#24-code-quality) |
| 7 | [Technology Stack](#7-technology-stack) | 25 | [CI/CD](#25-cicd) |
| 8 | [Project Structure](#8-project-structure) | 26 | [Deployment](#26-deployment) |
| 9 | [Data Architecture](#9-data-architecture) | 27 | [Security](#27-security) |
| 10 | [Database](#10-database) | 28 | [Performance & Scalability](#28-performance--scalability) |
| 11 | [Analytics](#11-analytics) | 29 | [Advantages](#29-advantages) |
| 12 | [Data Quality](#12-data-quality) | 30 | [Use Cases](#30-use-cases) |
| 13 | [API Documentation](#13-api-documentation) | 31 | [Troubleshooting](#31-troubleshooting) |
| 14 | [Installation](#14-installation) | 32 | [Future Enhancements](#32-future-enhancements) |
| 15 | [Prerequisites](#15-prerequisites) | 33 | [Contributing](#33-contributing) |
| 16 | [Environment Variables](#16-environment-variables) | 34 | [License](#34-license) |
| 17 | [—](#17-prerequisites) | 35 | [Project Status](#35-project-status) |
| 18 | [—](#18-environment-variables) | 36 | [Screenshots](#36-complete-screenshots) |

---

## 1. Project Overview

The **Banking Customer Profitability and Risk Analytics Platform** is a modular, domain-driven data analytics application built for retail and SME banking teams. It ingests, validates, models, and visualizes every layer of a bank's customer relationship lifecycle — from origination and product holding through daily transactions, lending exposure, fee income, operating costs, credit delinquency, churn signals, fraud suspicion, and executive-level decision intelligence.

The platform ships with:

- A **FastAPI** REST and WebSocket backend exposing 15+ analytics, monitoring, health, and real-time routes.
- A **Streamlit** interactive analytics frontend with 13 themed dashboards.
- A **PostgreSQL 15** data warehouse with star-schema dimensional models (5 dimensions, 8 fact tables) and 10 pre-built analytical SQL views.
- A **Pandera-based data-quality layer** with 13 strict schema contracts, 50+ per-column business-rule validators, and 10+ cross-field referential checks.
- A **Kafka + Redis** streaming tier for real-time alerts, anomaly detection, and feature-serving materialization.
- **GitHub Actions** CI/CD pipelines for lint, unit, API, integration, security-scan, SQLite-mode, Docker-build, and deploy-to-staging/production-with-rollback jobs.

### 1.1 Project Identity

| Item | Value |
|------|-------|
| Official Name | Banking Customer Profitability and Risk Analytics Platform |
| Short Name | Banking Analytics Platform |
| Primary Audience | Retail / SME Banking — CFO, CRO, Head of Retail, Analytics Office |
| Data Model Class | Star-schema, banking customer analytics (Kimball-style) |
| Deployment Tier | Self-hosted (Postgres + FastAPI + Streamlit + Kafka/Redis) or Kubernetes |

---

## 2. Business Problem

Banking leadership teams typically operate with fragmented, Excel-based reporting across risk, finance, marketing, and operations silos. The consequences are costly:

1. **Profitability opacity.** No single source of truth for *customer-level* net profit after funds-transfer-pricing (FTP), cost-to-serve, risk costs, and capital charges.
2. **Risk blind spots.** Credit, fraud, and early-warning signals are computed on disjoint schedules; by the time a delinquency is reported, the loss is already realized.
3. **Churn discovered too late.** Attrition analytics remain descriptive rather than predictive.
4. **No feedback loop.** Models in production drift silently without automated monitoring.
5. **Data quality debt.** Hand-written ETL silently accepts invalid business data (fraud scores > 1, future-dated originations, zero-amount transactions, negative credit limits), corrupting every downstream report.

The platform solves this by unifying these concerns under one versioned, testable, observable codebase with schema-enforced contracts at every ingestion boundary.

---

## 3. Solution

The platform delivers a **single cohesive analytics product** covering the full decision stack:

```
 ┌────────────────────────────────────────────────────────────────────┐
 │                      Streamlit Frontend (13 Pages)                 │
 │  Home  Executive  Customer360  Profitability  Risk  Churn  Segments │
 │  Products  Transactions  Decision  DQ  Models  Live Monitor        │
 └────────────────────────────┬───────────────────────────────────────┘
                              │ HTTP / HTTPS
 ┌────────────────────────────▼───────────────────────────────────────┐
 │                      FastAPI Backend (15+ Routes)                  │
 │   Health  Auth  Customers  Profitability  Risk  Churn  Segments    │
 │   Portfolio  Realtime(WSS)  Recommendations  OpenAPI/Redoc/Swagger │
 └──────────────────────┬───────────────────────────┬─────────────────┘
                        │ SQLAlchemy 2.x            │ WebSocket + Kafka
 ┌──────────────────────▼─────────────────────┐  ┌─▼──────────────────────┐
 │         PostgreSQL 15 Data Warehouse       │  │ Redis + Kafka Streaming │
 │  5 Dims · 8 Facts · 10 Analytical Views    │  │  Feature Store · Alerts │
 └────────────────────────────────────────────┘  └────────────────────────┘
```

Key differentiators:

- **Pandera schema contracts on every table.** No data ever enters the warehouse without passing a strict validation report that includes per-column range checks, cross-field date ordering, non-negativity on financial fields, and domain-specific interval rules (e.g., `0 ≤ fraud_score ≤ 1`, `300 ≤ credit_score ≤ 850`, `maturity_date ≥ origination_date`, `amount ≠ 0`).
- **15 analytics modules in a consistent orchestrator pattern.** Each domain (`profitability`, `credit_risk`, `churn`, `clv`, `customer_segmentation`, `customer_intelligence`, `advanced_risk_analytics`, `behavioral`, `core_analytics`, `data_governance`) exposes the same `base.py → features/models → orchestrator.py` shape for predictable extension.
- **Genuine two-sided risk normalization.** The `ON_TIME_PAYMENT_RATE` scoring rule has been explicitly verified against the double-inversion bug: 100% on-time yields 0 risk (correct), not 100 (the buggy baseline).
- **Real-time streaming.** An independent `streaming/` module integrates Kafka (event bus) and Redis (feature store / live alert cache) with a live-monitor dashboard visualizing severity-tiered alerts (Critical / High / Medium / Low).

---

## 4. Key Highlights

- ✅ **400+ passing tests** covering units, API contracts, and end-to-end analytics pipelines.
- ✅ **13 Pandera schemas** with restored business-rule validators on every column.
- ✅ **5 financial star-schema dimensions** and **8 fact tables** covering the full customer relationship.
- ✅ **10 pre-built analytical SQL views** (executive KPI, customer 360, profitability trend, risk distribution, churn retention, segment analysis, product analytics, transaction analytics, decision intelligence, model monitoring).
- ✅ **2 GitHub Actions pipelines** (CI + CD) with modern action versions, hardened secrets expressions, no `|| true` masking of genuine failures, and a manual rollback input on CD.
- ✅ **3 Docker images** (FastAPI API, Streamlit UI, Streaming worker) with a 4-service compose topology plus an optional pipeline and Kafka/Redis overlay.
- ✅ **13 Streamlit dashboards** with 64 in-app screenshots captured and documented.
- ✅ **OpenAPI 3.1 / Swagger UI / Redoc** interactive API documentation endpoints.
- ✅ **JWT-based authentication** in the API with secure dependencies and schema-level rate limiting.

---

## 5. Features

### 5.1 Executive & Strategic
- **Executive Overview** — aggregate KPIs, region/segment filters, revenue trend, risk distribution, and prioritized recommendation feed.
- **Decision Intelligence** — profitability/risk/growth action items, KPI overview panel, filterable recommendation engine.

### 5.2 Customer Intelligence
- **Customer 360** — individual customer search, profile, metrics cards (Revenue / Net Profit / Risk Score / CLV), Risk Information pane, Revenue-vs-Profit and Risk-vs-CLV charts, and recent transactions table.
- **Customer Segmentation** — unsupervised clustering + rule-based segments, KPI cards, segment data table, average balance / distribution / revenue charts.
- **Churn Analytics** — churn KPI cards (High Churn Risk / Avg Churn Probability / Total Customers), churn risk & probability distributions, prediction table, filtered high-risk cohort view.

### 5.3 Financial & Risk
- **Profitability Analytics** — customer-level profitability KPIs, revenue/profit distribution charts, full profitability metrics table.
- **Credit Risk Analytics** — risk KPI cards (High Risk Count / Avg Score / Total Exposure), risk score bands, exposure charts, detailed delinquency table.
- **Advanced Risk** — concentration analysis, delinquency buckets, early-warning signals, exposure concentration, RAROC (risk-adjusted profitability), risk migration, transition matrices, trend monitoring.
- **CLV Analytics** — historical CLV, estimated CLV, predicted CLV, adjustments, sensitivity analysis.

### 5.4 Product & Transaction
- **Product Analytics** — header/filters, KPIs, product performance breakdown, Average Balance view, NPL Rate view, Total Revenue / Customer distribution charts.
- **Transaction Analytics** — header/description/filters, KPI cards, Recent Transactions table, Volume by Type & Product bar charts.

### 5.5 Operations & Observability
- **Data Quality Monitoring** — live dashboard with validation metrics table.
- **Model Monitoring** — model KPI summary cards, configuration panel, performance metrics table.
- **Live Monitor / Real-Time Streaming** — real-time streaming analytics & metrics, account anomalies, risk-threshold exceedances, payment failures (Critical / High / Medium / Low severity), suspicious activity alerts, recent alerts feed.

### 5.6 Backend & Platform
- REST API with 15+ routes (health, auth, customers, profitability, risk, churn, segments, portfolio, realtime WebSocket, recommendations).
- **Swagger UI**, **Redoc**, and raw **OpenAPI 3.1 JSON** auto-documentation.
- **Pandera data-quality layer** (13 schemas, per-column + cross-field validators) with `validate_with_report()` returning pass/fail plus a per-rule report DataFrame.
- **Rate limiting**, **audit middleware**, and **structured JWT auth dependencies**.
- **Alembic migrations**, **SQL scripts**, and **PostgreSQL views** for every analytical domain.

---

## 6. Architecture

The platform follows a **layered, domain-driven architecture** with clear ownership boundaries:

### 6.1 Layered Model

```
┌───────────────────────────────────────────────────────────────────┐
│ L1  Presentation           Streamlit (13 pages / 4 component mods)│
├───────────────────────────────────────────────────────────────────┤
│ L2  Interface/API          FastAPI routes · Pydantic schemas      │
│                            REST + WebSocket + OpenAPI docs        │
├───────────────────────────────────────────────────────────────────┤
│ L3  Application/Orchestrators 10 analytics modules                │
│           profitability · credit_risk · churn · clv · segments    │
│           customer_intelligence · advanced_risk · behavioral      │
│           core_analytics · data_governance                        │
├───────────────────────────────────────────────────────────────────┤
│ L4  Domain / Data Quality   Pandera schemas · 13 contracts        │
│                            BaseSchema + _field_validators         │
│                            + _cross_field_validators              │
├───────────────────────────────────────────────────────────────────┤
│ L5  Infrastructure         SQLAlchemy 2.x ORM · PostgreSQL 15     │
│                            Redis · Kafka · Alembic · Docker       │
└───────────────────────────────────────────────────────────────────┘
```

### 6.2 Data Flow

1. **Batch or streaming input** → Pandera `BaseSchema.validate_with_report()`
2. **Validation pass** → Pandas DataFrame with type coercion + nullable column auto-injection
3. **Validation fail** → Report DataFrame returned with per-rule failures; no write
4. **Validated data** → `SQLAlchemy` write into star schema
5. **Analytical SQL views** maintained in `sql/views/` and materialized on demand
6. **API layer** reads via SQLAlchemy, serializes via Pydantic, returns JSON
7. **Frontend layer** composes Plotly charts / KPI cards / tables from API
8. **Streaming layer** writes alerts into Redis + Kafka; Live Monitor page subscribes via WebSocket

### 6.3 Key Architectural Choices

| Concern | Choice | Rationale |
|---------|--------|-----------|
| ORM | SQLAlchemy 2.x (type-safe queries) | Mature, type-aware, Alembic migrations native. |
| Schema validation | Pandera 0.33 + custom `_field_validators` / `_cross_field_validators` dispatch layer | Pandera dropped `Field(checks=...)` kwarg; explicit registries preserve every business rule without touching Field kwargs. |
| Missing nullable columns in strict mode | `_ensure_nullable_columns_present()` auto-injects NaN for `nullable=True` cols before `strict=True` Pandera validate | Lets legitimately-optional dates (`churn_date`, `closed_date`) be absent from input DataFrames for active customers / open accounts. |
| Classmethod dispatch in cross-field rules | `isinstance(ref, classmethod)` branch calling `ref.__func__(cls, df)` | Classmethods stored at class-eval time are not auto-bound to dict values; explicit branch resolves correctly. |
| API transport | FastAPI (REST) + Starlette WebSocket | REST for domain endpoints, WSS for live streaming alert fan-out. |
| Auth | JWT via `passlib` + `bcrypt` + dependency injection | Stateless bearer tokens without tight coupling. |
| Frontend | Streamlit 1.x multi-page app | Fastest path from DataFrame to dashboard; supports Plotly, pandas-native rendering. |
| Jobs / CI | GitHub Actions matrix 3.11/3.12 + service containers (Postgres / Redis / Kafka / ZK) | Reproducible on every push; externalized infra in services. |

---


## 7. Project  Screenshots


---

### 7.1 Home / Platform Overview

![Welcome Overview](Screenshots/Home%20tab%20Welcome%20to%20the%20Banking%20Customer%20Profitability%20and%20Risk%20Analytics%20Platform%20%26%20core%20overview.png)

*Welcome screen — platform mission statement, core capabilities overview, and entry-point navigation.*

![Getting Started & Platform Statistics](Screenshots/Home%20tab%20Getting%20Started%20guide%20and%20Platform%20Statistics%20KPI%20cards%20(10%2C000%2B%20customers%2C%201M%2B%20data%20points)..png)

*Getting Started guide plus Platform Statistics KPI cards confirming 10,000+ customers and 1M+ data points processed.*

![Quick Navigation & Data Source Architecture](Screenshots/Home%20tab%20Quick%20Navigation%20and%20Data%20Source%20architecture%20description..png)

*Quick Navigation panel plus high-level Data Source architecture describing the warehouse and streaming data flow.*

---

### 7.2 Executive Overview Dashboard

![Executive KPIs & Top Recommendations](Screenshots/Executive%20Overview%20tab%20Key%20Performance%20Indicators%20(Total%20Customers%2C%20Revenue%2C%20Profit%2C%20High%20Risk)%20and%20top%20recommendations.png)

*Executive Overview headline KPI row (Total Customers, Revenue, Profit, High Risk) and prioritized top recommendations feed.*

![Executive Date, Region, Segment Filters](Screenshots/Executive%20Overview%20tab%20Date%20range%2C%20Region%2C%20and%20Segment%20filter%20options..png)

*Date-range picker, Region multi-select, and Segment multi-select filters drive every downstream KPI and chart on the Executive Overview page.*

![Executive Revenue Trend & Risk Distribution](Screenshots/Executive%20Overview%20tab%20Revenue%20by%20Customer%20line%20chart%20%26%20Risk%20Score%20by%20Level%20bar%20chart..png)

*Revenue-by-Customer line chart over the reporting period alongside Risk-Score-by-Level bar chart summarizing the credit portfolio composition.*

![Expanded Executive Recommendations](Screenshots/Executive%20Overview%20tab%20Expanded%20Executive%20Recommendations%20(Profitability%2C%20Risk%2C%20Growth%20action%20items)..png)

*Expanded Executive Recommendations panel with categorized action items for Profitability, Risk, and Growth initiatives.*

![Customer Metrics Summary Table](Screenshots/Executive%20Overview%20tab%20Customer%20Metrics%20Summary%20data%20table%20view..png)

*Customer Metrics Summary data table view — executive-accessible drill-down of the headline KPIs with per-row detail.*

![PDF Print Preview of Executive Overview](Screenshots/Shows%20the%20Executive%20Overview%20dashboard%20page%20inside%20the%20browser%27s%20Save%20as%20PDF%20%20print%20preview%20dialog..png)

*Browser print-preview dialog exporting the Executive Overview dashboard directly to PDF for board meetings.*

![Streamlit Screencast Overlay](Screenshots/Shows%20the%20Streamlit%20Record%20a%20screencast%20overlay%20modal%20on%20the%20Executive%20Overview%20page..png)

*Streamlit's built-in "Record a screencast" overlay shown over the Executive Overview page for walkthrough capture.*

---

### 7.3 Customer 360 Profile

![Customer 360 — Search & Profile Card](Screenshots/Customer%20360%20tab%20Customer%20search%20bar%20and%20initial%20customer%20profile%20info%20(Nasir%20Khan)..png)

*Customer search bar and initial profile header for customer "Nasir Khan" — the starting point for any 360 investigation.*

![Customer 360 — Metrics Cards & Risk Information](Screenshots/Customer%20360%20tab%20Customer%20metrics%20cards%20(Revenue%2C%20Net%20Profit%2C%20Risk%20Score%2C%20CLV)%20and%20Risk%20Information..png)

*Customer metrics cards (Revenue, Net Profit, Risk Score, CLV) paired with a structured Risk Information pane capturing the risk profile at a glance.*

![Customer 360 — Revenue vs Profit & Risk vs CLV Charts](Screenshots/Customer%20360%20Revenue%20vs%20Profit%20%26%20Risk%20vs%20CLV%20Charts.png)

*Quadrant view combining Revenue-vs-Profit (financial) and Risk-vs-CLV (strategic) to identify the most valuable retention and upsell targets.*

![Customer 360 — Risk Info & Recent Transactions Table](Screenshots/Customer%20360%20Risk%20Info%20%26%20Recent%20Transactions%20Table.png)

*Risk Information pane plus a paginated Recent Transactions table showing latest customer-level activity and flagged behavior.*

---

### 7.4 Profitability Analytics

![Profitability — Header, Filter Controls & Top Layout](Screenshots/Profitability%20Header%2C%20Filter%20Controls%20%26%20Top%20Layout.png)

*Profitability Analytics page header, filter controls (date range, segment, region), and introductory description text.*

![Profitability — KPI Cards (Revenue, Profit, Customers)](Screenshots/Profitability%20Key%20Performance%20Indicators%20(Revenue%2C%20Profit%2C%20Customers).png)

*Profitability KPI cards at the top of the page: Revenue, Profit, and Total Customers in the filtered cohort.*

![Profitability — Revenue & Profit Distribution by Customer Charts](Screenshots/Profitability%20Revenue%20%26%20Profit%20Distribution%20by%20Customer%20Charts.png)

*Two distribution charts showing customer-level Revenue and Profit spreads across the current cohort.*

![Profitability — Customer Profitability Metrics Data Table](Screenshots/Profitability%20Customer%20Profitability%20Metrics%20Data%20Table.png)

*Customer Profitability Metrics Data Table — per-customer granularity with all profitability inputs (interest income, fee income, operating costs, risk costs) plus net profit rank.*

---

### 7.5 Credit Risk Analytics

![Credit Risk — Header & Filter Selection Panel](Screenshots/Credit%20Risk%20Header%20%26%20Filter%20Selection%20Panel.png)

*Credit Risk Analytics header with page description and the filter selection panel driving the downstream KPI, chart, and table views.*

![Credit Risk — Risk KPIs](Screenshots/Credit%20Risk%20Risk%20KPIs%20(High%20Risk%20Count%2C%20Avg%20Score%2C%20Total%20Exposure).png)

*Credit Risk KPI cards: High Risk Count, Average Risk Score, and Total Exposure.*

![Credit Risk — Risk Score by Level & Exposure Charts](Screenshots/Credit%20Risk%20Risk%20Score%20by%20Level%20%26%20Exposure%20Charts.png)

*Risk Score by Level distribution (bar chart) plus Exposure (aggregate bar chart) combining volume and severity analysis.*

![Credit Risk — Detailed Risk Analysis & Delinquency Table](Screenshots/Credit%20Risk%20Detailed%20Risk%20Analysis%20%26%20Delinquency%20Table.png)

*Detailed Risk Analysis and Delinquency Table — analyst view with risk bands, delinquency bucket counters, and exposure per customer/account.*

---

### 7.6 Churn Analytics

![Churn — Header, Filter Options, KPI Preview](Screenshots/Churn%20Analytics%20header%2C%20filter%20options%2C%20KPI%20preview.png)

*Churn Analytics page header, filter options (region, segment, model threshold), and compact KPI preview at the top of the page.*

![Churn — KPI Cards](Screenshots/Churn%20KPIs%20(High%20Churn%20Risk%2C%20Avg%20Churn%20Probability%2C%20Total%20Customers).png)

*Churn KPI cards: High Churn Risk count, Average Churn Probability, and Total Customers in scope.*

![Churn — Risk & Probability Distribution Charts](Screenshots/Churn%20Risk%20%26%20Churn%20Probability%20distribution%20charts.png)

*Churn Risk distribution and Churn Probability distribution — side-by-side charts describing the shape of attrition risk in the portfolio.*

![Churn — Predictions Probability & Risk Table](Screenshots/Churn%20Predictions%20customer%20probability%20%26%20risk%20table.png)

*Churn Predictions table: per-customer probability, risk tier, and key risk drivers for analyst review.*

![Churn — Filtered High-Risk Customers Table](Screenshots/Filtered%20High%20Churn%20Risk%20Customers%20table.png)

*Filtered High Churn Risk Customers table — pre-filtered view of only the high-priority retention list for marketing action.*

---

### 7.7 Customer Segmentation

![Segmentation Filters](Screenshots/customer-segmentation-filters.png)

*Segmentation filters UI — parameters governing business-rule and clustering-based segmentation logic.*

![Segmentation KPIs](Screenshots/Segmentation%20KPIs%20(Total%20Segments%2C%20Largest%20Segment%2C%20Total%20Customers).png)

*Segmentation KPI cards: Total Segments, Largest Segment by membership, and Total Customers segmented.*

![Segment Data Table](Screenshots/Customer%20Segments%20data%20table.png)

*Customer Segments data table — per-segment row with profile metrics and counts.*

![Average Balance by Segment Bar Chart](Screenshots/Average%20Balance%20by%20Segment%20bar%20chart.png)

*Average Balance by Segment bar chart — size comparison across segments by the deposits metric.*

![Distribution & Revenue by Segment Bar Charts](Screenshots/Distribution%20%26%20Revenue%20by%20Segment%20bar%20charts.png)

*Dual bar charts: customer Distribution by Segment and Revenue by Segment — comparing volume and financial contribution.*

---

### 7.8 Product Analytics

![Product Analytics — Header & Filters](Screenshots/Product%20Analytics%20Header%20%26%20productsegment%20filters.png)

*Product Analytics page header and product/segment filter controls.*

![Product Analytics — Filters & KPIs](Screenshots/Product%20Analytics%20Filters%20%26%20Key%20Performance%20Indicators.png)

*Expanded filters layout plus the row of Product Analytics Key Performance Indicators.*

![Product Analytics — KPIs & Performance Table](Screenshots/Product%20Analytics%20KPIs%20%26%20Product%20Performance%20breakdown%20table.png)

*Product KPIs (cards) directly above the Product Performance breakdown table for cross-reference.*

![Product Analytics — Average Balance Chart](Screenshots/Product%20Analytics%20Average%20Balance%20chart%20view.png)

*Average Balance view by product — deposit depth per product line.*

![Product Analytics — NPL Rate Chart](Screenshots/Product%20Analytics%20Non-Performing%20Loan%20(NPL)%20Rate%20chart%20view.png)

*Non-Performing Loan (NPL) Rate chart view by product — risk contribution per product line.*

![Product Analytics — Total Revenue & Customer Distribution Charts](Screenshots/Product%20Analytics%20Total%20Revenue%20%26%20Customer%20Distribution%20charts.png)

*Dual charts: Total Revenue by product and Customer Distribution by product for portfolio balance.*

---

### 7.9 Transaction Analytics

![Transaction Analytics — Header & Filters](Screenshots/Transaction%20Analytics%20Header%2C%20description%20%26%20filter%20controls.png)

*Transaction Analytics page header, description paragraph, and filter controls (date range, account type, product).*

![Transaction Analytics — KPI Cards](Screenshots/Transaction%20Analytics%20Key%20Performance%20Indicators%20(KPI%20cards).png)

*Transaction Analytics KPI cards — total volume, total amount, average size, fraud-related counters.*

![Transaction Analytics — Recent Transactions Table](Screenshots/Transaction%20Analytics%20Recent%20Transactions%20data%20table.png)

*Recent Transactions data table with pagination, filters, and per-row status and fraud-suspicion flags.*

![Transaction Analytics — Volume by Type & Product Bars](Screenshots/Transaction%20Analytics%20Volume%20by%20type%20%26%20product%20bar%20charts.png)

*Volume by Type bar chart and Volume by Product bar chart — compositional analysis of transaction streams.*

---

### 7.10 Decision Intelligence

![Decision Intelligence — Header & Filter Controls](Screenshots/Decision%20Intelligence%20%E2%80%93%20Header%20%26%20Filter%20Controls.png)

*Decision Intelligence page header, introductory description, and filter controls.*

![Decision Intelligence — KPI Metrics Overview](Screenshots/Decision%20Intelligence%20%E2%80%93%20KPI%20Metrics%20Overview.png)

*Decision Intelligence KPI Metrics Overview — aggregated scores for the current recommendation batch.*

![Decision Intelligence — Executive Recommendations](Screenshots/Decision%20Intelligence%20%E2%80%93%20Executive%20Recommendations.png)

*Executive Recommendations list — prioritized, categorized, and tagged with the owning domain (Profitability, Risk, Growth).*

---

### 7.11 Data Quality Monitoring

![Data Quality Monitoring Dashboard & Metrics Table](Screenshots/Data%20Quality%20Monitoring%20%E2%80%93%20Dashboard%20%26%20Metrics%20Table.png)

*Data Quality Monitoring dashboard and accompanying Metrics Table — per-schema pass/fail, failure counts, and trend indicators.*

---

### 7.12 Model Monitoring

![Model Monitoring — Header & Configuration](Screenshots/Model%20Monitoring%20%E2%80%93%20Header%20%26%20Configuration.png)

*Model Monitoring header plus Configuration pane — current tracked model, train/production window, alert thresholds.*

![Model Monitoring — KPI Summary Cards](Screenshots/Model%20Monitoring%20%E2%80%93%20KPI%20Summary%20Cards.png)

*Model Monitoring KPI Summary Cards: production data volume, prediction count, accuracy proxy, drift score.*

![Model Monitoring — Performance Metrics Table](Screenshots/Model%20Monitoring%20%E2%80%93%20Performance%20Metrics%20Table.png)

*Model Monitoring Performance Metrics Table — per-model-version tracking of AUC, precision, recall, F1, calibration, and drift versus baseline.*

---

### 7.13 Live Monitor / Real-Time Streaming Analytics

![Live Monitor — Real-time Streaming Analytics & Metrics](Screenshots/Live%20Monitor%20%E2%80%93%20Real-time%20Streaming%20Analytics%20%26%20Metrics.png)

*Live Monitor streaming overview header, throughput metrics, and general streaming health panel.*

![Live Monitor — Payment Failure & Anomaly Alerts](Screenshots/Live%20Monitor%20%E2%80%93%20Payment%20Failure%20%26%20Anomaly%20Alerts.png)

*Dedicated panel view showing Payment Failure and Account Anomaly alert streams.*

![Live Monitor — Recent Alerts Feed (High/Medium)](Screenshots/Live%20Monitor%20%E2%80%93%20Recent%20Alerts%20Feed%20(HighMedium).png)

*Recent Alerts Feed view prioritized for High and Medium severity for rapid NOC triage.*

![Live Monitor — Account Anomalies (Low/High) & High Transaction Volume](Screenshots/Live%20Monitor%20view%20displaying%20Account%20Anomaly%20(Low%20%26%20High)%20and%20High%20Transaction%20Volume%20(Medium)%20alerts..png)

*Account Anomaly alerts spanning Low and High severity alongside a High Transaction Volume (Medium) alert.*

![Live Monitor — Risk Threshold Exceeded (High/Medium) & Payment Failures](Screenshots/Live%20Monitor%20view%20displaying%20Risk%20Threshold%20Exceeded%20(High%20%26%20Medium)%20and%20Payment%20Failure%20alerts..png)

*Risk Threshold Exceeded (High and Medium) alerts interspersed with Payment Failure events.*

![Live Monitor — Critical: Payment Failure & Suspicious Activity](Screenshots/Live%20Monitor%20view%20highlighting%20Payment%20Failure%20(Critical)%20and%20Suspicious%20Activity%20(Critical)%20alerts..png)

*Critical severity tile view highlighting Payment Failure (Critical) and Suspicious Activity (Critical) events — the highest priority for operations.*

![Live Monitor — Low Severity: Risk Thresholds / Payment Failures / Suspicious](Screenshots/Live%20Monitor%20view%20showing%20Risk%20Threshold%20Exceeded%20(Low)%2C%20Payment%20Failure%20(Low)%2C%20and%20Suspicious%20Activity%20alerts..png)

*Low-severity alert view: Risk Threshold Exceeded (Low), Payment Failure (Low), and Suspicious Activity for tracking/audit.*

![Live Monitor — Medium: Risk Thresholds / High Volume / Payment Failures](Screenshots/Live%20Monitor%20view%20showing%20Risk%20Threshold%20Exceeded%2C%20High%20Transaction%20Volume%2C%20and%20Payment%20Failure%20(Medium)%20alerts..png)

*Medium-severity aggregation view: Risk Threshold, High Transaction Volume, and Payment Failure medium-tier alerts.*

---

### 7.14 API & Backend Documentation

![Root API Endpoint (Links)](Screenshots/JSON%20output%20from%20the%20root%20API%20endpoint%20listing%20links%20for%20docs%2C%20health%2C%20auth%2C%20and%20websocket%20routes..png)

*JSON response from the root API endpoint (`/`) exposing the HATEOAS-style link collection (docs, health, auth, websocket, etc.).*

![Health Endpoint (Status, Version, DB State)](Screenshots/JSON%20response%20from%20the%20health%20endpoint%20displaying%20status%20(degraded)%2C%20version%2C%20and%20database%20state..png)

*JSON response from the health endpoint showing operational status (`degraded` sample), version, and database connectivity state.*

![OpenAPI 3.1 JSON Schema (API Info & health paths)](Screenshots/OpenAPI%203.1.0%20JSON%20specification%20schema%20showing%20API%20info%20and%20health%20check%20paths..png)

*Raw `openapi.json` response — OpenAPI 3.1.0 schema root with API info block and `/health*` paths enumerated.*

![Swagger UI — API Banner, Authorize, Endpoint List](Screenshots/Swagger%20UI%20documentation%20page%20showing%20the%20OpenAPI%203.1%20title%20banner%2C%20authorize%20button%2C%20and%20endpoint%20lists..png)

*Swagger UI page: OpenAPI 3.1 banner, Authorize button for JWT, and full endpoint list — the default interactive console at `/docs`.*

![Redoc UI — Banking Analytics API Title & Health Section](Screenshots/Top-level%20Redocly%20documentation%20interface%20displaying%20the%20Banking%20Analytics%20API%20title%2C%20version%2C%20and%20initial%20health%20check%20section..png)

*Top-level Redoc UI (`/redoc`) — Banking Analytics API title, semantic version, and the introductory Health Check section layout.*

![Redoc — Sample Responses for Health Ready & Live](Screenshots/Redocly%20UI%20showing%20documentation%20and%20response%20samples%20for%20apiv1healthready%20and%20apiv1healthlive.png)

*Redoc UI detail view showing sample request/response bodies for `/api/v1/health/ready` and `/api/v1/health/live`.*

---

### 7.15 Miscellaneous UI Artifact

![Share Screen Browser Prompt](Screenshots/Shows%20the%20browser%20prompt%20asking%20to%20choose%20and%20share%20the%20screen..png)

*Browser share-screen prompt triggered when starting the Streamlit screencast recorder — captured for completeness in documentation around walkthrough capture flows.*



## 8. Technology Stack

### 8.1 Languages & Runtime
- **Python** 3.11, 3.12, 3.14 (verified)
- **YAML** for config & GitHub Actions
- **Templating:** Alembic Mako
- **SQL** (PostgreSQL 15 dialect + views)

### 8.2 Backend
- **FastAPI** 0.141.x — REST + WebSocket
- **Uvicorn** — ASGI server
- **Pydantic v2** — API request/response validation
- **SQLAlchemy 2.x** — ORM + Core
- **Alembic** — migrations
- **Psycopg2 / psycopg2-binary** — PostgreSQL driver
- **Passlib + bcrypt** — password hashing
- **python-jose[cryptography]** — JWT signing
- **httpx** — test client / outbound HTTP

### 8.3 Analytics & ML
- **Pandas 3.x** — DataFrames & ETL
- **NumPy 2.x** — numerics
- **scikit-learn** — churn models, clustering, scoring pipelines
- **Plotly** — all frontend charting
- **Pandera 0.33.x** — data-quality contracts with custom dispatch layer
- **Pydantic-settings** — typed configuration loading

### 8.4 Streaming & Live Ops
- **Apache Kafka** (Confluent 7.4 images) — event bus
- **Redis 7** — feature store + alert cache
- **confluent-kafka** Python client

### 8.5 Frontend
- **Streamlit 1.63** — multi-page UI framework
- **Plotly Express / Figure Factory** — charts
- **pandas** Styler — table rendering

### 8.6 Testing & Quality
- **pytest 9.x**
- **pytest-cov**, **pytest-mock**, **pytest-asyncio**
- **Bandit** — SAST
- **pip-audit** — SCA on requirements
- **flake8**, **black**, **isort**, **mypy**, **pylint**

### 8.7 DevOps
- **Docker** (3 Dockerfiles) + **docker-compose** 3.8 (core + streaming overlays)
- **Kubernetes 1.x** manifests under `k8s/production/` (Deployment, Service, ConfigMap, Secret)
- **GitHub Actions** (checkout@v4, setup-python@v5, setup-buildx@v3, login-action@v3, build-push-action@v5, upload-artifact@v4, codecov@v4)

---

## 9. Project Structure

```
Banking Customer Profitability and Risk Analytics Platform/
├── Screenshots/                         # 65 PNG screenshots documented in §36
├── .github/workflows/
│   ├── ci.yml                           # Lint · Unit · API · Integration · Security · Build · SQLite
│   └── cd.yml                           # Staging / Production deploy + Rollback input
├── api/                                 # FastAPI backend
│   ├── main.py                          # App factory, 15 routes, CORS, middleware
│   ├── auth/                            # JWT auth models, schemas, security, service, deps
│   ├── routers/                         # 9 endpoint modules (health, auth, customers, …)
│   ├── schemas/                         # Pydantic v2 request/response schemas per domain
│   ├── audit.py · middleware.py · rate_limit.py · errors.py
│   ├── config.py · database.py · websocket.py
├── config/
│   ├── base.yaml · logging.yaml · ingestion.yaml · replay.yaml · streaming.yaml
│   └── environments/{development,production}.yaml
├── docs/
│   ├── security/                        # SECURITY_GUIDE + 5 phased security reports
│   ├── audit/                           # 35 end-to-end audit documents & reports
│   ├── streaming/                       # phase4 streaming reliability report
│   └── *.md                             # 28 methodology / deployment / implementation guides
├── frontend/                            # Streamlit application
│   ├── app.py                           # Main multi-page entry point
│   ├── pages/                           # 13 dashboard pages (home, executive_overview, …)
│   ├── components/                      # charts, filters, kpi_cards, tables (shared)
│   ├── streamlit/                       # styles, theme, advanced streamlit components
│   └── config.py
├── k8s/production/                      # Deployment, Service, ConfigMap, Secret
├── power_bi/                            # Power_BI_Data_Model.pbit + setup guide
├── scripts/
│   └── check_dependencies.py
├── sql/
│   ├── migrations/                      # Alembic + versions (001 streaming, 002 realtime cols)
│   ├── schema/schema.sql                # Full DDL for star schema
│   ├── views/*.sql                      # 10 analytical views
│   ├── credit_risk_analytics.sql · customer_360_views.sql
│   ├── profitability_analytics.sql · transaction_analytics.sql
├── src/                                 # Domain analytics modules
│   ├── advanced_analytics/scenario_analysis.py
│   ├── advanced_risk_analytics/         # 11 modules (base, concentration, RAROC, …)
│   ├── behavioral_analytics/change_detection.py
│   ├── churn_analytics/                 # features, models, evaluation, signals, rates, cohorts
│   ├── clv_analytics/                   # historical, estimated, predicted, adjustments, sensitivity
│   ├── core_analytics/
│   ├── credit_risk_analytics/           # scoring, repayment, delinquency, default, exposure, …
│   ├── customer_intelligence/
│   ├── customer_segmentation/           # clustering, business_rules, profiling, stability, …
│   ├── data_governance/{lineage, quality_scoring}.py
│   └── data_quality/
│       ├── base.py                      # BaseSchema (validate_with_report, field+cross dispatch)
│       └── schemas.py                   # 13 Pandera DataFrameModels with validator registries
├── tests/
│   ├── unit/                            # analytics, API, data_quality, models, streaming, …
│   ├── api/                             # FastAPI API contract tests
│   └── integration/                     # end-to-end + infrastructure tests
├── .dockerignore · .env.example · .gitignore
├── alembic.ini · pytest.ini
├── ARCHITECTURE.md · DATA_DICTIONARY.md
├── Dockerfile  Dockerfile.streaming  Dockerfile.streamlit
├── docker-compose.yml · docker-compose.dev.yml · docker-compose.streaming.yml
├── LICENSE · PROJECT_CONSTITUTION.md · REMEDIATION_SUMMARY.md
├── requirements.txt · requirements-api.txt
└── README.md                            # This file
```

---

## 10. Data Architecture

The warehouse follows a **classic Kimball star schema** anchored on customer, account, product, branch, and date dimensions.

### 10.1 Dimensional Model — Inventory

| Table | Kind | Grain | Key |
|-------|------|-------|-----|
| `dim_customer` | Dimension | One row per customer | `customer_id` |
| `dim_account` | Dimension | One row per account | `account_id` |
| `dim_product` | Dimension | One row per product | `product_id` |
| `dim_branch` | Dimension | One row per branch | `branch_id` |
| `dim_date` | Dimension | One row per calendar date | `date_id` |
| `dim_customer_segment` | Dimension | One row per segment definition | `segment_id` |
| `fact_transaction` | Fact | One row per transaction event | `transaction_id` |
| `fact_loan` | Fact | One row per loan origination | `loan_id` |
| `fact_loan_payment` | Fact | One row per loan payment | `payment_id` |
| `fact_card_transaction` | Fact | One row per card transaction event | `card_tx_id` |
| `fact_customer_interaction` | Fact | One row per customer interaction event | `interaction_id` |
| `fact_customer_profitability` | Fact | One row per customer × period | `profitability_id` |
| `fact_customer_risk` | Fact | One row per customer × period | `risk_id` |

### 10.2 Data Flow Layers

1. **Landing / Raw.** Batches or stream events arrive as raw DataFrames.
2. **Staging with schema validation.** Raw → Pandera `BaseSchema.validate_with_report()`.
   - Coerce types per schema (`coerce=True`).
   - Enforce strict columns; auto-inject missing nullable columns as NaN.
   - Run per-column validators (ranges, non-neg, domain rules).
   - Run cross-field validators (date orderings, min ≤ max, amount ≠ 0 rules).
   - If any validator fails, report is returned and data is NOT written to warehouse.
3. **Warehouse load.** Validated DataFrame → SQLAlchemy ORM into fact/dim tables.
4. **Analytical presentation.** SQL views under `sql/views/` compute domain outputs.
5. **API consumption.** FastAPI routers serve the views or equivalent ORM queries.

### 10.3 Domain-to-Table Mapping

| Domain | Source Tables | Key Views |
|--------|---------------|-----------|
| Executive | `fact_customer_profitability`, `fact_customer_risk`, … | `vw_executive_overview_kpi`, `vw_decision_intelligence` |
| Customer 360 | `dim_customer`, `fact_transaction`, `fact_loan`, `fact_card_transaction`, … | `vw_customer_360_detail` |
| Profitability | `fact_customer_profitability`, `dim_customer`, `dim_account` | `vw_profitability_trend` |
| Credit Risk | `fact_customer_risk`, `fact_loan`, `fact_loan_payment` | `vw_risk_distribution` |
| Churn | `dim_customer`, `fact_customer_interaction`, `fact_transaction` | `vw_churn_retention` |
| Segmentation | `dim_customer_segment`, `dim_customer` | `vw_segment_analysis` |
| Product | `dim_product`, `fact_transaction`, `fact_loan` | `vw_product_analytics` |
| Transactions | `fact_transaction`, `fact_card_transaction`, `dim_account`, `dim_product` | `vw_transaction_analytics` |
| Model Monitoring | model-run metadata tables | `vw_model_monitoring` |

---

## 11. Database

### 10.1 Engine
- **PostgreSQL 15** (Alpine image in docker-compose).
- **Alembic** migrations under `sql/migrations/versions/` (001 streaming tables, 002 realtime cols).
- Full DDL snapshot provided in `sql/schema/schema.sql` for standalone provisioning.

### 11.2 Connection
Default (override via env):

```
host     = localhost / postgres (compose)
port     = 5432
database = banking_analytics
user     = postgres
password = from env
```

### 11.3 Highlights
- All tables owned by the application user.
- Proper foreign keys from fact tables to dimensions.
- Coverage indexes on `customer_id`, `account_id`, `transaction_date`, `segment_id`, `period_start/end`.
- JSONB columns for flexible payloads in alerting and interaction facts.
- Alembic `env.py` configured for async-compatible migration runs.

---

## 12. Analytics

Every analytics module in `src/` follows a consistent **Orchestrator** pattern. Each ships a base mixin, a feature-engineering module, one or more model/statistic modules, and an orchestrator composing them end-to-end.

### 12.1 Module Inventory

| Module | Location | Produces |
|--------|----------|----------|
| Core Analytics | `src/core_analytics/` | Orchestrates full ETL. |
| Profitability | `src/…/credit_risk_analytics/` (plus `src/data_quality/*`) | Net profit per customer × period, distribution, rankings. |
| Credit Risk | `src/credit_risk_analytics/scoring.py` + 9 siblings | Risk score, bands, debt burden, default probability, exposure at default, loss given default, utilization, repayment behavior, delinquency buckets, payment behavior, portfolio concentration. |
| Advanced Risk | `src/advanced_risk_analytics/` | RAROC, transition matrices, risk migration, trend monitoring, early warning, exposure concentration, concentration analysis, delinquency buckets, portfolio distribution, orchestrator. |
| CLV | `src/clv_analytics/` | Historical / Estimated / Predicted CLV, adjustments, sensitivity. |
| Churn | `src/churn_analytics/` | Churn features, sklearn model, evaluation, cohort rates, signals. |
| Segmentation | `src/customer_segmentation/` | Business-rule + clustering (KMeans/HDBSCAN) segments, profiling, stability evaluation. |
| Customer Intelligence | `src/customer_intelligence/` | Customer-level feature rollup. |
| Behavioral Analytics | `src/behavioral_analytics/change_detection.py` | Statistical regime change detection on behavior streams. |
| Scenario Analysis | `src/advanced_analytics/scenario_analysis.py` | Stress scenarios against risk & profitability. |
| Data Governance | `src/data_governance/` | Lineage, quality scoring. |

### 12.2 Credit Risk Scoring Normalization (Verified Bug Fix)
In `src/credit_risk_analytics/scoring.py`, the `ON_TIME_PAYMENT_RATE` metric:
- Values are clamped to `[0, 100]` (percent).
- No pre-inversion by `100 - value`.
- Direction inversion (`100 - normalized`) is applied **once** iff direction is `higher_is_better`.

This guarantees the intended semantics:
| On-time rate | Normalized | Inversion (higher_is_better) | **Risk** |
|--------------|-----------:|-----------------------------:|---------:|
| 100%         | 100        | 100 - 100                    | **0** ✓ |
| 0%           | 0          | 100 - 0                      | **100** ✓ |

All 15 tests in `tests/unit/credit_risk_analytics/test_scoring.py` pass, including `test_normalize_on_time_payment_rate`.

---

## 13. Data Quality

### 13.1 Principles
1. **Schema-on-read, strictly.** Every analytical input DataFrame passes a Pandera `DataFrameModel` with `strict=True`, `coerce=True`.
2. **No silent pass.** If any business rule fails, `validate_with_report()` returns `is_valid=False` plus a report DataFrame naming every violated row × rule.
3. **Every rule from the original `checks=` kwarg is preserved.** When the Pandera 0.33 upgrade removed `Field(checks=[...])` support, every rule was re-expressed as entries in per-schema `_field_validators` or `_cross_field_validators` registries. A total of 50+ range/non-neg/domain rules plus 10+ cross-field rules are active.
4. **Legitimately optional data is tolerated.** `nullable=True` columns missing from an input frame are auto-populated with NaN for active-customer, open-account scenarios.

### 13.2 BaseSchema Pipeline (`src/data_quality/base.py`)

```
DataFrame
  → _ensure_nullable_columns_present()   # auto-inject NaN into any absent nullable=True col
  → cls.validate()                       # Pandera strict type + coercion
  → _run_field_validations()             # per-col: range, non-neg, domain intervals, date ranges
  → _run_cross_field_validations()       # date ordering, min ≤ max, amount ≠ 0
  → (is_valid, report_df)
```

### 13.3 Rules Implemented (by Schema)

| Schema | Per-Column Validators | Cross-Field Validators |
|--------|----------------------|------------------------|
| `DimCustomerSchema` | birth_date past, annual_income ≥ 0, customer_since valid, churn_date valid | `churn_date ≥ customer_since` |
| `DimAccountSchema` | credit_limit ≥ 0, overdraft_limit ≥ 0, opened_date valid, closed_date valid | `closed_date ≥ opened_date` |
| `DimProductSchema` | interest_rate ≥ 0, annual_fee ≥ 0, minimum_balance ≥ 0, term_months ≥ 0 | |
| `DimBranchSchema` | lat ∈ [−90,90], lon ∈ [−180,180], atm_count ≥ 0, employee_count ≥ 0 | |
| `DimDateSchema` | day 1..31, weekday 1..7, month 1..12, quarter 1..4, year 1900..2200 | |
| `DimCustomerSegmentSchema` | min/max_balance ≥ 0, credit_min/max ∈ [300, 850] | `expiry_date ≥ effective_date`, `min_balance ≤ max_balance`, `credit_min ≤ credit_max` |
| `FactTransactionSchema` | fraud_score ∈ [0, 1] | `amount != 0` (zero-amount transactions rejected) |
| `FactLoanSchema` | principal ≥ 0, interest ≥ 0, term > 0, credit_score ∈ [300,850], dpd ≥ 0 | `maturity_date ≥ origination_date` |
| `FactLoanPaymentSchema` | payment_amount > 0, principal ≥ 0, interest ≥ 0, days_late ≥ 0 | |
| `FactCardTransactionSchema` | fraud_score ∈ [0,1], rewards_points ≥ 0 | `transaction_amount != 0` |
| `FactCustomerInteractionSchema` | duration ≥ 0, satisfaction ∈ [1,5] | |
| `FactCustomerProfitabilitySchema` | interest, fee, cost, operating_costs, account_count, tx_count all ≥ 0 | `period_end ≥ period_start` |
| `FactCustomerRiskSchema` | credit_score ∈ [300,850], exposure ≥ 0, dpd ≥ 0, delinquent ≥ 0, PD ∈ [0,1], LGD ∈ [0,1] | `period_end ≥ period_start` |

### 13.4 Testing
All 40 tests in `tests/unit/data_quality/` pass, including the four originally-named failing tests and the additional `test_zero_transaction_amount` rule regression:

- `test_non_negative_with_negative` — semantic assertion after NumPy boolean singleton fix.
- `test_valid_customer_data` — valid DataFrame without `churn_date` passes (auto-injected NaN).
- `test_valid_account_data` — valid DataFrame without `closed_date` passes (auto-injected NaN).
- `test_invalid_fraud_score` — `fraud_score = 1.5` correctly rejected per [0, 1] rule.
- `test_zero_transaction_amount` — `amount = 0` correctly rejected per cross-field amount ≠ 0 rule.

---

## 14. API Documentation

### 14.1 Route Inventory

| Prefix | Router | Purpose |
|--------|--------|---------|
| `/api/v1/health` | `health` | liveness, readiness, degraded state, version, DB status |
| `/api/v1/auth` | `auth` | JWT login / register flows |
| `/api/v1/customers` | `customers` | customer list, customer 360, filter endpoints |
| `/api/v1/profitability` | `profitability` | profitability summary, distribution, customer-level detail |
| `/api/v1/risk` | `risk` | credit risk scores, bands, exposure, delinquency tables |
| `/api/v1/churn` | `churn` | churn KPIs, probability distributions, prediction table, high-risk filter |
| `/api/v1/segments` | `segments` | segment definitions, segment averages, segment tables |
| `/api/v1/portfolio` | `portfolio` | aggregate portfolio views, concentrations |
| `/ws/realtime` | WebSocket (`realtime`) | push channel for streaming Live Monitor alerts |
| `/api/v1/recommendations` | `recommendations` | decision-intelligence recommendations |
| `/api/v1/products` | `portfolio` / products | KPIs, NPL, average balance, product performance table |
| `/api/v1/transactions` | transaction router | KPIs, recent transactions, volume by type/product |
| `/docs` | built-in Swagger UI | interactive OpenAPI console |
| `/redoc` | built-in Redoc | polished OpenAPI documentation |
| `/openapi.json` | raw schema | OpenAPI 3.1 JSON |

### 14.2 Auto-Generated Docs Served Natively
- **Swagger UI:** `<host>/docs`
- **Redoc UI:** `<host>/redoc`
- **Raw OpenAPI 3.1 JSON:** `<host>/openapi.json`

### 14.3 Response Contracts
All responses are Pydantic v2-schematized. Field types are strictly enforced. Every non-trivial router exposes request validation schemas in `api/schemas/*.py`.

---

## 15. Installation

### 14.1 Option A — Local Python (dev mode)

```powershell
git clone <your-repo-url>
cd "Banking Customer Profitability and Risk Analytics Platform"

python -m venv .venv
.venv\Scripts\Activate.ps1       # Windows PowerShell
# source .venv/bin/activate      # bash/zsh

python -m pip install --upgrade pip
pip install -r requirements.txt
# API-only minimal footprint:
# pip install -r requirements-api.txt

Copy-Item .env.example .env
# Edit .env and fill DB_PASSWORD, JWT_SECRET_KEY, etc.
```

Proceed to §19 (Database Setup).

### 15.2 Option B — Docker Compose (quickest full stack)

See §22.

---

## 16. Prerequisites

| Prerequisite | Minimum Version | Notes |
|--------------|----------------:|-------|
| Python | 3.11 | 3.12 or 3.14 recommended. |
| PostgreSQL | 15 | Included in Docker Compose. |
| Redis | 7 | Optional, only for streaming / live monitor. |
| Kafka | 3.4+ (cp-kafka 7.4) | Optional, only for streaming ingest. |
| Docker Engine | 24 | Required only for container runs. |
| Docker Compose | v2 | Required only for compose runs. |
| pip | 23 | Upgrade via `python -m pip install --upgrade pip`. |

---

## 17. Environment Variables

See [`.env.example`](.env.example) for a complete template. Every sensitive variable is read via env; nothing is hardcoded.

| Name | Purpose | Default | Required? |
|------|---------|---------|-----------|
| `DB_HOST` | PostgreSQL hostname | `localhost` | Yes |
| `DB_PORT` | PostgreSQL port | `5432` | Yes |
| `DB_NAME` | Database name | `banking_analytics` | Yes |
| `DB_USER` | Database user | — | Yes |
| `DB_PASSWORD` | Database password | — | **Yes (never commit)** |
| `APP_ENV` | `development` / `production` / `staging` | `development` | |
| `LOG_LEVEL` | Python log level | `INFO` | |
| `DEBUG` | FastAPI debug mode | `false` | |
| `API_PORT` | FastAPI listen port | `8000` | |
| `CORS_ORIGINS` | Comma-separated CORS origins | `http://localhost:3000,http://localhost:8501` | |
| `STREAMLIT_PORT` | Streamlit listen port | `8501` | |
| `CACHE_TTL` | Frontend cache TTL (s) | `3600` | |
| `PIPELINE_MODE` | `batch` | `batch` | |
| `JWT_SECRET_KEY` | HS256 signing key for JWT | — | **Yes (never commit)** |
| `USE_SQLITE` | Fallback to SQLite (no Postgres needed) | `false` | |
| `REDIS_HOST` | Redis host for streaming | — | Streaming only |
| `KAFKA_BROKER` | Kafka bootstrap | — | Streaming only |
| `DOCKER_REGISTRY` / `DOCKER_USERNAME` / `DOCKER_PASSWORD` | CD registry creds | — | CD only, in GitHub secrets |
| `CODECOV_TOKEN` | Coverage upload | — | CI only, in GitHub secrets |

---

## 18. [Duplicate placeholder retained for numbering parity]

(This entry preserved to match the 36-section index published by the platform charter. See §18 through §36 for substantive content.)

---

## 19. [Duplicate placeholder retained for numbering parity]

(This entry preserved to match the 36-section index published by the platform charter. See §19 onward.)

---

## 20. Database Setup

### 20.1 Provision Postgres (native)

```sql
CREATE USER banking_app WITH PASSWORD '<DB_PASSWORD from .env>';
CREATE DATABASE banking_analytics OWNER banking_app;
GRANT ALL PRIVILEGES ON DATABASE banking_analytics TO banking_app;
```

Then run:

```powershell
# Load full schema DDL
psql -U banking_app -d banking_analytics -f sql/schema/schema.sql

# Optional: seed test data (project-specific scripts, if added)
# python scripts/seed_data.py
```

### 20.2 Alembic Migrations

```powershell
alembic upgrade head          # Runs versions 001 → 002
```

### 20.3 Views

All views under `sql/views/*.sql` must be applied after the schema:

```powershell
Get-ChildItem sql/views/*.sql | Sort-Object Name | ForEach-Object {
    psql -U banking_app -d banking_analytics -f $_.FullName
}
```

---

## 21. Running the Backend

### 21.1 Local Dev Mode

```powershell
$env:PYTHONPATH = "."
uvicorn api.main:app --host 0.0.0.0 --port $env:API_PORT --reload
```

Verify the API is live:

- Health: `http://localhost:8000/api/v1/health/ready` and `/live`
- Swagger UI: `http://localhost:8000/docs`
- Redoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`
- Root link collection: `http://localhost:8000/`

### 21.2 Local Unit Test Mode (SQLite)

Useful for lightweight runs without Postgres:

```powershell
$env:USE_SQLITE = "true"
pytest tests/unit -v --ignore=tests/unit/streaming/kafka --ignore=tests/unit/models
```

---

## 22. Running the Frontend

Ensure the backend is running first (frontend calls API endpoints for most tabs).

```powershell
$env:PYTHONPATH = "."
streamlit run frontend/app.py --server.port $env:STREAMLIT_PORT --server.address 0.0.0.0
```

Then open `http://localhost:8501`. The sidebar exposes 13 pages.

---

## 23. Docker Setup

### 22.1 Images Provided

| Image | Dockerfile | Entry |
|-------|-----------|-------|
| API + Pipeline | `Dockerfile` | FastAPI `uvicorn api.main:app` / pipeline orchestrator |
| Streamlit UI | `Dockerfile.streamlit` | `streamlit run frontend/app.py` |
| Streaming Worker | `Dockerfile.streaming` | Standalone streaming consumer |

### 23.2 Core Stack (Postgres + API + Streamlit + optional Pipeline)

```powershell
Copy-Item .env.example .env     # set DB_PASSWORD at minimum
docker compose up -d --build
```

Services exposed:

| Service | URL | Notes |
|---------|-----|-------|
| API | `http://localhost:8000/` | Depends on postgres healthy |
| UI | `http://localhost:8501/` | Depends on postgres + API healthy |
| Postgres | `localhost:5432` | Named volume persists data |

### 23.3 Add Streaming Stack

```powershell
docker compose -f docker-compose.yml -f docker-compose.streaming.yml up -d --build
```

Provisions Redis, Kafka, Zookeeper, and the streaming worker.

### 23.4 Pipeline Only

```powershell
docker compose --profile pipeline up -d --build pipeline
```

### 23.5 Verified Correctness (Docker Paths)
Audited during the platform audit:

- `Dockerfile.streamlit` → `CMD streamlit run frontend/app.py` (correct)
- `docker-compose.yml` streamlit service → `./frontend:/app/frontend:ro` (correct)
- `docker-compose.yml` api service → `./src:/app/src:ro`, `./api:/app/api:ro` (correct)

---

## 24. Testing

### 24.1 Framework

- **pytest** with plugins: `pytest-cov`, `pytest-mock`, `pytest-asyncio`.
- Configured in `pytest.ini`.

### 24.2 Core Test Run

```powershell
# Unit + API tests (no external infra):
python -m pytest tests/unit tests/api `
    --ignore=tests/unit/streaming/kafka `
    --ignore=tests/unit/models `
    -q
```

Verified result (current audit): **400 passed, 3 skipped** (excludes streaming/kafka and models collection issues).

### 24.3 Domain-Focused Runs

```powershell
# Data quality (all 40 tests):
python -m pytest tests/unit/data_quality/ -q

# Credit risk scoring (all 15 tests, validates scoring bug fix):
python -m pytest tests/unit/credit_risk_analytics/test_scoring.py -q

# FastAPI routes:
python -m pytest tests/api/ -q
```

### 24.4 Full Integration Run (requires services)

```powershell
docker compose -f docker-compose.yml -f docker-compose.streaming.yml up -d postgres redis kafka zookeeper
$env:DB_HOST=localhost; $env:REDIS_HOST=localhost; $env:KAFKA_BROKER=localhost:9092
python -m pytest tests/integration -v
```

### 24.5 Known External-Dependency Failures (Documented, Not Masked)

Three categories of known issues surface on a fresh Python 3.14 sandbox. None are masked by `|| true` anywhere in code, CI, or this README:

1. **`tests/unit/streaming/kafka/*` — 3 collection errors.** `ModuleNotFoundError: No module named 'confluent_kafka'`. Install `confluent-kafka` via pip if Kafka tests are needed. CI applies `--ignore=tests/unit/streaming/kafka`.
2. **`tests/unit/models/test_streaming.py` — 1 collection error.** Python 3.14 + SQLAlchemy 2.0.36 typing edge case in `de_stringify_union_elements` → `TypeError: descriptor '__getitem__' requires a 'typing.Union' object but received a 'tuple'`. Mitigated by `--ignore=tests/unit/models` pending a SQLAlchemy release targeting Python 3.14 typing internals.
3. **`datetime.utcnow()` deprecation warnings (non-blocking).** Python 3.12+ emits `DeprecationWarning: datetime.utcnow() is deprecated and scheduled for removal in a future version` across the source tree. Affected files (100+ call sites, 15 files):
   - `src/data_quality/metrics.py`, `src/data_quality/base.py`, `src/data_quality/schemas.py` (`CustomCheck._past_date`, `CustomCheck._age_at_least`)
   - `api/routers/health.py`, `api/routers/realtime.py`
   - `api/main.py`, `api/database.py`, `api/websocket.py`, `api/audit.py`
   - `api/auth/security.py`, `api/auth/models.py`
   - `tests/api/test_api_endpoints.py`, `tests/unit/data_quality/test_schemas.py::test_invalid_birth_date_future`
   - `tests/unit/streaming/schemas/{test_validation,test_event_schemas}.py`, `tests/unit/streaming/{test_alert_engine,test_warning_adapter,processor/test_processor}.py`
   Clean semantic-upgrade path is a future PR replacing each call with `datetime.now(datetime.UTC)` (and `.replace(tzinfo=None)` for naive-timestamp consumers) — no behaviour change required. GitHub-dependent CD operations (Docker registry push, Codecov upload, GitHub Environments protection rules, kubectl rollback) require GitHub secrets / live cluster — correct in YAML, not reproducible locally, catalogued explicitly in §25.3.

---

## 25. Code Quality

The CI lint job runs the following tools. Each lint step uses `continue-on-error: true` with an in-YAML rationale comment. **Lint output is advisory-only and must never silently mask a functionally-correct commit;** style regressions are surfaced to the author for out-of-band remediation:

| Tool | Purpose | Command |
|------|---------|---------|
| `flake8` (E9/F63/F7/F82) | Syntax/semantic errors | `flake8 src/ api/ frontend/ --count --select=E9,F63,F7,F82 --show-source --statistics` |
| `flake8` (complexity/style) | McCabe, line length | `flake8 src/ api/ frontend/ --count --max-complexity=10 --max-line-length=127 --statistics` |
| `black` | Formatting | `black --check src/ api/ frontend/` |
| `isort` | Import order | `isort --check-only src/ api/ frontend/` |
| `mypy` | Static typing | `mypy src/ api/ --ignore-missing-imports` |
| `pylint` | Installed, configurable in CI config | |

**Security scanning** runs in the `security-scan` job (also `continue-on-error: true`):

| Tool | Purpose |
|------|---------|
| `bandit -r src/ api/` | SAST |
| `pip-audit` | SCA on installed dependencies |
| Artifacts uploaded to GitHub Actions run for 30 days | |

---

## 26. CI/CD

### 26.1 CI Pipeline (`.github/workflows/ci.yml`)

Runs on every push/PR to `main` and `develop`:

| Job | Matrix | Services | Hard Fail? |
|-----|--------|----------|------------|
| lint | single (py 3.12) | — | Per-step advisory-only |
| test | 3.11, 3.12 | Postgres 15, Redis 7 | ✅ Genuine fail |
| api-test | 3.11, 3.12 | Postgres 15 | ✅ Genuine fail |
| integration-test | 3.11, 3.12 | Postgres 15, Redis 7, cp-kafka 7.4, cp-zookeeper 7.4 | Job-level best-effort, step-level genuine |
| security-scan | single | — | Job-level advisory-only |
| build | single | Docker Buildx | ✅ `docker build` genuine fail; save artifact non-critical |
| sqlite-test | single (py 3.12) | — | Job-level best-effort |

**CI hardening applied:**
- All GitHub Actions on modern stable versions (`checkout@v4`, `setup-python@v5`, `setup-buildx-action@v3`, `login-action@v3`, `build-push-action@v5`, `upload-artifact@v4`, `codecov@v4`).
- No `|| true` or `|| echo …` hiding in any test/build step. Precisely one ignore-path list per unit-test job for the two known external-dependency collection errors (Kafka Python client, SQLAlchemy Py3.14 typing).
- Codecov upload gated on step success and `fail_ci_if_error: false` (token optional).

### 26.2 CD Pipeline (`.github/workflows/cd.yml`)

Trigger on push to `main` **or** manual `workflow_dispatch` with two inputs:

| Input | Type | Values | Default |
|-------|------|--------|---------|
| `environment` | choice (required) | `staging`, `production` | `staging` |
| `rollback` | choice (optional) | `false`, `true` | `false` |

Jobs:

| Job | Activation | Hard Fail? |
|-----|-----------:|------------|
| `deploy-staging` | push-to-main OR `environment == staging` | ✅ Genuine fail |
| `deploy-production` | `environment == production AND rollback != 'true'` | ✅ Genuine fail |
| `rollback` | `workflow_dispatch AND rollback == 'true'` | ✅ Genuine fail |

**CD hardening applied:**
- All three `continue-on-error: true` at job level were **removed**; deployments now genuinely fail when broken.
- Login/push/push steps all guarded by `secrets.DOCKER_REGISTRY != '' && DOCKER_USERNAME != '' && DOCKER_PASSWORD != ''` (added the missing `DOCKER_PASSWORD` conjunct).
- `docker build` / `docker push` steps no longer swallow failures with `|| echo`.
- Rollback input was already defined as a `workflow_dispatch` input; an inline comment documents that `github.event.inputs.rollback` is guaranteed to resolve for `workflow_dispatch` events.
- Rollback step prints clear operator guidance: `Note: Manual kubectl rollout undo required if Kubernetes cluster is configured`.

### 26.3 CI/CD Items That Require GitHub Secrets

These cannot be reproduced locally and will only resolve under actual GitHub execution:

| GitHub Secret | Used In | Purpose |
|---------------|---------|---------|
| `DOCKER_REGISTRY`, `DOCKER_USERNAME`, `DOCKER_PASSWORD` | CD deploy jobs | Push images. Optional; CD jobs are fully skipped when empty. |
| `CODECOV_TOKEN` | CI test job | Upload coverage to Codecov. Optional. |
| GitHub Environments (`staging`, `production`) | CD | Required for GitHub Environments deployment tracking / protection rules. |

---

## 27. Deployment

### 26.1 Paths
1. **Docker Compose** (§22) — quickest for single-node / on-prem.
2. **Kubernetes** — manifests under `k8s/production/`:
   - `configmap.yaml` — non-sensitive config
   - `secret.yaml` — sealed-secrets pattern; never commit actual secrets
   - `deployment.yaml` — API + UI replicas, probes, resources
   - `service.yaml` — ClusterIP / LoadBalancer

### 28.2 CD Deployment
```
Push to main → deploy-staging → manual dispatch with environment=production → deploy-production
```

Rollback via manual dispatch with `rollback=true` (operator must also run `kubectl rollout undo` against any deployed ReplicaSets).

---

## 29. Security

See [`docs/security/SECURITY_GUIDE.md`](docs/security/SECURITY_GUIDE.md) for the full multi-phase security report. Highlights:

- **Secrets-only config.** No DB password, JWT key, or registry credential committed in code. `.env.example` only documents names, never values.
- **JWT auth + FastAPI Depends.** Every protected router reuses typed dependencies in `api/auth/dependencies.py`.
- **Audit middleware.** `api/audit.py` records route access.
- **Rate limiting.** `api/rate_limit.py` (token-bucket / sliding window per endpoint).
- **Error handling.** `api/errors.py` maps Pydantic validation errors, business rule errors, auth errors, SQL errors to consistent status codes with no stack trace leakage.
- **CORS.** Allowlist in `CORS_ORIGINS` env; no wildcard in production.
- **HTTPS / TLS.** Terminate at reverse proxy (nginx, ingress controller) for production.
- **Bandit + pip-audit.** Scanned in CI. Artifacts uploaded to run.
- **Attack-surface review, phase 1-3 implementation reports, and architecture diagrams** provided in `docs/security/`.

---

## 30. Performance & Scalability

### 30.1 Horizontal Scaling Targets
- **API.** Stateless behind any load balancer; horizontally scalable to N replicas. Sessionless JWT.
- **Streamlit UI.** Stateless per tab render; deploy N replicas and sticky sessions if desired.
- **Postgres.** Primary with read replicas for read-heavy dashboard loads.
- **Redis.** Cluster mode shards the live alert cache + feature store.
- **Kafka.** 3+ broker cluster for high-volume streaming ingest.

### 30.2 Performance Guardrails
- `sql/views/` SQL tuned with coverage indexes on dimension keys and dates.
- FastAPI responses are Pydantic v2 — ~10× faster parse than v1 for large lists.
- Pandera strict validation happens once at ingest, not per API call.
- Streamlit frontend has `CACHE_TTL` env (default 3600 s) on heavy aggregations.
- Docker healthchecks in every compose service (Postgres, API, UI) prevent traffic from hitting cold pods.

### 30.3 Proven Scales
- Static datasets of 10,000+ customers and 1M+ data points (as shown on the Home tab) are handled without issues in the test harness.

---

## 31. Advantages

| # | Advantage | Details |
|---|-----------|---------|
| 1 | **One codebase, one source of truth** | Profitability + Risk + Churn + Segments + Products + Transactions + DQ + Models + Streaming share a schema-enforced warehouse and API. |
| 2 | **50+ restored validations** | Pandera upgrade did not reduce validation coverage; each rule was re-expressed in explicit registries. |
| 3 | **Production-grade CI/CD** | No `|| true` masking; genuine failures surface; registry secrets gated with the missing-password conjunct; rollback input properly wired to `workflow_dispatch`. |
| 4 | **Documented 36-section README + 64 screenshots** | Portfolio-ready, fully audited. |
| 5 | **Multi-page Streamlit frontend over Plotly** | Analyst-friendly authoring; rich visualizations without a frontend framework build step. |
| 6 | **SQLAlchemy 2.x & Alembic** | Type-safe, migration-tracked schema. |
| 7 | **Docker Compose + Kubernetes** | Works out of the box on a laptop and scales cleanly to clusters. |
| 8 | **Security reports in-repo** | Phased security implementation reports guide hardening. |
| 9 | **Verified double-inversion bug fix** | ON_TIME_PAYMENT_RATE risk is 0 when on-time rate is 100%. |
| 10 | **Streaming tier present end-to-end** | Kafka ingest → Redis feature store → WebSocket push → Live Monitor dashboard. |

---

## 32. Use Cases

1. **Quarterly profitability review** — Finance team downloads the executive overview and customer-level profitability table, filtered by region/segment.
2. **Risk committee** — Risk team slices by risk band and exposure in Credit Risk; drills into Detailed Risk Analysis & Delinquency Table.
3. **Campaign planning** — Marketing uses Segmentation + Churn high-risk cohort to design targeted retention campaigns.
4. **Fraud / BSO operations** — Live Monitor page is the NOC pane of glass for Critical/High alerts: suspicious activity, payment failures, risk-threshold exceedances.
5. **Model governance** — Model Monitoring tab tracks drift, performance, KPIs, and configuration across every promoted model version.
6. **Data Quality council** — DQ dashboard shows per-table, per-rule failure counts over time and flags regression after ETL changes.
7. **M&A / portfolio transfer** — Product and portfolio views slice by product, segment, and NPL to value a book.
8. **Regulatory reporting** — Pre-built analytical views feed a BI export layer (see `power_bi/` Power BI `.pbit` template) that can be reconciled against regulatory feeds.

---

## 33. Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| `ModuleNotFoundError: No module named 'confluent_kafka'` | confluent-kafka not installed | `pip install confluent-kafka` |
| `TypeError: descriptor '__getitem__' requires a 'typing.Union' object …` in SQLAlchemy typing helpers | Python 3.14 + SQLAlchemy 2.0.36 edge case | Run tests with `--ignore=tests/unit/models` pending upstream SQLAlchemy release. |
| Postgres: "password authentication failed" | `DB_PASSWORD` empty or mismatch | Re-check `.env`. |
| Streamlit frontend shows empty charts | API unreachable | Visit `http://localhost:8000/api/v1/health/ready`; confirm API service started after Postgres health. |
| Docker build fails behind proxy | No proxy vars in build | Pass `--build-arg HTTP_PROXY=… HTTPS_PROXY=…`. |
| CD login step skipped | DOCKER_* secrets not populated in repo | Add `DOCKER_REGISTRY`, `DOCKER_USERNAME`, `DOCKER_PASSWORD` as GitHub repo/environment secrets. |
| Rolling back with `rollback=true` appears to do nothing | Kubernetes rollback requires operator action | Follow the kubectl guidance echoed in the rollback step. |
| Bandit finds `B101:assert_used` | Assertions in non-test code | Review each hit. DQ module uses exceptions, not asserts, for genuine business validation. |
| Pandera `SchemaError: column 'churn_date' not in dataframe` | Old schema code missing auto-inject | Current `BaseSchema` auto-injects; confirm schema class inherits from `src.data_quality.base.BaseSchema`. |
| `fraud_score = 1.5` passed validation | Old `checks=` removals without `_field_validators` restoration | Current `FactTransactionSchema` and `FactCardTransactionSchema` both install `CustomCheck.valid_rate` on `fraud_score`. |
| `amount = 0` passed validation | Cross-field rule not dispatched | Current schemas register `_amount_not_zero` classmethods; cross-field dispatch handles classmethod refs via `ref.__func__(cls, df)`. |
| `DeprecationWarning: datetime.utcnow() is deprecated` on Python 3.12+ | `datetime.utcnow()` scheduled for removal in future Python release | Non-blocking; clean upgrade path is `datetime.now(datetime.UTC)` (strip `tzinfo` for naive consumers). See §23.5 item 3 for affected file inventory. |

---

## 34. Future Enhancements

1. **Feature Store hardening.** Promote Redis feature store to Feast or equivalent for online/offline consistency.
2. **MLflow integration.** Track model version, dataset, and metrics per promoted model for ML governance.
3. **Reverse ETL sync to CRM / marketing automation.** Write churn-risk and segment outputs back to campaign tools.
4. **Kubernetes HPA + PDB.** Add Horizontal Pod Autoscaler for API and UI, Pod Disruption Budgets for stateful services.
5. **IAC:** Terraform / Pulumi modules alongside current Kubernetes manifests.
6. **ABAC / RBAC model.** Extend JWT auth with scoped roles (analyst / risk / finance / admin). Field-level redaction for PII on need-to-know.
7. **Column-level encryption / masking.** Encrypt PII columns (phone, email, address) at rest with KMS-wrapped DEKs.
8. **Power BI / Tableau DirectQuery.** Ship DirectQuery definitions alongside the `.pbit` template.
9. **Full streaming replay.** `config/replay.yaml` and `docs/streaming/phase4…` already exist; wire replay UI into Live Monitor.
10. **Data contracts as API.** Expose Pandera report schemas as a `/api/v1/data-quality/schemas` route for external validators.

---

## 35. Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feat/<name>` or `fix/<issue-id>-<slug>`).
3. Install dev deps (§14, `pip install -r requirements.txt && pip install flake8 black isort mypy pylint bandit pip-audit pytest pytest-cov pytest-mock pytest-asyncio`).
4. Implement.
5. Run the full test suite locally (§23).
6. Run lint and security scans (§24).
7. Update docs and screenshots if UI changes touch any dashboard page.
8. Open a PR against `develop`. The CI pipeline (§25) will run.

Branch model:
- `develop` — integration. All PRs land here.
- `main` — release line. Deployed to staging / production via CD.

---


## 36. Project Status

| Capability | Status |
|------------|--------|
| Dimensional data warehouse (5 dims, 8 facts) | ✅ Shipped |
| 10 analytical SQL views | ✅ Shipped |
| 13 Pandera schemas + restored business validators (50+ rules) | ✅ Shipped |
| FastAPI backend, 15+ routes, JWT auth, rate limit, audit | ✅ Shipped |
| 13 Streamlit dashboards | ✅ Shipped |
| 8-severity Live Monitor + streaming architecture | ✅ Shipped |
| Power BI data model template | ✅ Shipped |
| Kubernetes manifests | ✅ Shipped |
| Docker Compose (core + streaming) | ✅ Shipped |
| CI pipeline (7 jobs, 6 with hard-fail) | ✅ Shipped |
| CD pipeline (staging / production / rollback) | ✅ Shipped |
| 400+ passing tests, no `|| true` hiding | ✅ Verified in audit |
| 64 in-app screenshots + 1 cover image + full README | ✅ Shipped |
| Security audits, phased implementation reports, architecture guides | ✅ Shipped (35 files under `docs/`) |


---


## Repository

- **Charter:** [PROJECT_CONSTITUTION.md](PROJECT_CONSTITUTION.md)
- **Architecture:** [ARCHITECTURE.md](ARCHITECTURE.md)
- **Data Dictionary:** [DATA_DICTIONARY.md](DATA_DICTIONARY.md)
- **Security Guide:** [SECURITY_GUIDE.md](docs/security/SECURITY_GUIDE.md)
- **Audit Inventory:** `docs/audit/`
- **Methodologies:** `docs/*.md` (profitability, credit risk, churn, CLV, segmentation, decision intelligence, data quality rules, streaming architecture, etc.)

- ## 37. License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for the full text.

S K Ismail
