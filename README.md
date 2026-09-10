# 🏦 Banking Customer Profitability & Risk Analytics Platform

![Production Ready](https://img.shields.io/badge/Production-Ready-green)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey)

<div align="center">
  <img src="Project Screenshots/Home tab Welcome to the Banking Customer Profitability and Risk Analytics Platform & core overview.png" alt="Platform Overview" width="1000"/>
</div>

---

## 📖 Overview

A comprehensive, production-grade **Banking Customer Profitability & Risk Analytics Platform** designed for financial institutions to gain deep insights into customer behavior, assess risk exposure, optimize profitability, and make data-driven decisions. This platform combines real-time streaming analytics, machine learning models, and interactive dashboards to provide a 360-degree view of customer relationships.

### 🎯 Key Capabilities

- **Real-time Risk Scoring**: Continuous monitoring of customer risk levels with early warning systems
- **Customer 360 Analytics**: Unified view of customer profiles, transactions, and relationships
- **Profitability Analysis**: Detailed customer and product-level profitability metrics
- **Churn Prediction**: ML-powered churn risk identification and retention strategies
- **Decision Intelligence**: Automated recommendations for business actions
- **Live Monitoring**: Real-time alerts for anomalies, fraud, and threshold breaches
- **Model Monitoring**: Continuous tracking of ML model performance and drift

### 📊 Production Readiness Score

**9.0/10** - This platform is production-ready with complete API layer, security features, containerization, and CI/CD pipeline.

---

## ✨ Features

### 🎯 Core Analytics Modules

#### **Customer 360**
- Unified customer profiles with comprehensive metrics
- Customer lifetime value (CLV) calculations
- Revenue vs. Profit analysis
- Risk score visualization
- Recent transaction tracking

#### **Credit Risk Analytics**
- Real-time risk scoring with multiple risk levels
- Risk migration matrix tracking
- Early warning system for deteriorating customers
- Exposure analysis by risk level
- Delinquency monitoring

#### **Profitability Analytics**
- Customer-level profitability decomposition
- Product profitability analysis
- Revenue and profit distribution charts
- Cost allocation tracking
- Net interest margin calculations

#### **Churn Analytics**
- ML-powered churn probability prediction
- High churn risk customer identification
- Churn risk distribution analysis
- Retention strategy recommendations
- Customer behavior change detection

#### **Product Analytics**
- Product performance metrics
- Non-performing loan (NPL) rate tracking
- Average balance analysis
- Customer distribution by product
- Revenue contribution by product

#### **Transaction Analytics**
- Real-time transaction monitoring
- Transaction volume analysis by type
- Recent transaction feeds
- Anomaly detection in transaction patterns
- Product-wise transaction breakdown

#### **Decision Intelligence**
- Automated executive recommendations
- Actionable insights for growth
- Risk mitigation suggestions
- Profitability optimization strategies
- What-if scenario analysis

#### **Live Monitor**
- Real-time streaming analytics dashboard
- Alert management (Critical, High, Medium, Low)
- Payment failure monitoring
- Suspicious activity detection
- Risk threshold breach alerts

#### **Model Monitoring**
- ML model performance tracking
- Feature distribution monitoring
- Prediction accuracy metrics
- Model drift detection
- Performance degradation alerts

#### **Data Quality Monitoring**
- Data quality scoring
- Completeness metrics
- Freshness monitoring
- Validation rule tracking
- Quality trend analysis

### 🔧 Technical Features

- **RESTful API**: FastAPI-based REST API with OpenAPI/Swagger documentation
- **Real-time Streaming**: Apache Kafka integration for real-time data processing
- **Caching**: Redis-based feature store for high-performance queries
- **Security**: JWT authentication, rate limiting, security headers
- **Containerization**: Docker and Kubernetes deployment ready
- **CI/CD**: Automated testing and deployment pipelines
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Testing**: Comprehensive test suite with pytest

---

## 🛠️ Technology Stack

### Backend
- **Python 3.11+** - Core programming language
- **FastAPI 0.109.0** - High-performance REST API framework
- **SQLAlchemy 2.0.23** - SQL ORM and database toolkit
- **Alembic 1.13.0** - Database migration tool

### Data Processing
- **Pandas 2.1.4** - Data manipulation and analysis
- **Polars 0.20.6** - High-performance DataFrame library
- **NumPy 1.26.2** - Numerical computing
- **Pydantic 2.5.3** - Data validation using Python type annotations

### Machine Learning
- **scikit-learn 1.3.2** - Machine learning algorithms
- **imbalanced-learn 0.11.0** - Handling imbalanced datasets
- **SciPy 1.11.4** - Scientific computing
- **Statsmodels 0.14.0** - Statistical modeling

### Streaming & Caching
- **Apache Kafka 2.0.2** - Distributed event streaming
- **Redis 4.3.4** - In-memory data store and cache

### Visualization & Dashboards
- **Streamlit 1.31.0** - Interactive web applications
- **Plotly 5.18.0** - Interactive visualization library

### Security
- **python-jose 3.3.0** - JWT token handling
- **passlib 1.7.4** - Password hashing
- **slowapi 0.1.9** - Rate limiting
- **bandit 1.7.5** - Security linting

### Testing
- **pytest 7.4.4** - Testing framework
- **pytest-cov 4.1.0** - Code coverage
- **pytest-mock 3.12.0** - Mocking support
- **pytest-asyncio 0.23.3** - Async testing

### Deployment
- **Docker** - Containerization
- **Kubernetes** - Container orchestration
- **GitHub Actions** - CI/CD automation

---

## 🏗️ Architecture

<div align="center">
  <img src="Project Screenshots/Home tab Quick Navigation and Data Source architecture description.png" alt="Architecture Overview" width="800"/>
</div>

### System Architecture

The platform follows a **layered architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Streamlit   │  │  FastAPI     │  │  Power BI    │     │
│  │  Dashboards  │  │  REST API    │  │  Reports     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Analytics Layer                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐  │
│  │  Risk    │ │Profit    │ │ Churn    │ │ Customer     │  │
│  │ Analytics│ │Analytics │ │Prediction│ │ Intelligence │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Processing Layer                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐  │
│  │ Feature  │ │   ML     │ │ Streaming│ │ Data Quality │  │
│  │ Engine   │ │ Models   │ │ Pipeline │ │ Validation   │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐  │
│  │PostgreSQL│ │  Kafka   │ │  Redis   │ │ File Storage │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

- **Streaming Infrastructure**: Real-time event processing with Kafka and Redis
- **Feature Store**: High-performance feature serving for ML models
- **Model Registry**: Centralized model versioning and deployment
- **Alert Engine**: Real-time alert generation and notification
- **Reconciliation**: Batch-stream data consistency validation
- **Security Layer**: Authentication, authorization, and rate limiting

---

## 📸 Project Screenshots

### 🏠 Home & Getting Started

<div align="center">
  <img src="Project Screenshots/Home tab Welcome to the Banking Customer Profitability and Risk Analytics Platform & core overview.png" alt="Home Page" width="800"/>
  <p><em>Welcome to the Platform</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Home tab Getting Started guide and Platform Statistics KPI cards (10,000+ customers, 1M+ data points)..png" alt="Getting Started" width="800"/>
  <p><em>Getting Started Guide & Platform Statistics</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Home tab Quick Navigation and Data Source architecture description.png" alt="Quick Navigation" width="800"/>
  <p><em>Quick Navigation & Architecture Overview</em></p>
</div>

### 📊 Executive Overview

<div align="center">
  <img src="Project Screenshots/Executive Overview tab Key Performance Indicators (Total Customers, Revenue, Profit, High Risk) and top recommendations.png" alt="Executive Overview KPIs" width="800"/>
  <p><em>Executive Overview - Key Performance Indicators</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Executive Overview tab Revenue by Customer line chart & Risk Score by Level bar chart..png" alt="Executive Overview Charts" width="800"/>
  <p><em>Revenue & Risk Analytics</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Executive Overview tab Expanded Executive Recommendations (Profitability, Risk, Growth action items)..png" alt="Executive Recommendations" width="800"/>
  <p><em>Executive Recommendations</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Executive Overview tab Date range, Region, and Segment filter options..png" alt="Executive Overview Filters" width="800"/>
  <p><em>Executive Overview - Filter Options</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Executive Overview tab Customer Metrics Summary data table view..png" alt="Executive Overview Table" width="800"/>
  <p><em>Executive Overview - Customer Metrics Summary</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Distribution & Revenue by Segment bar charts.png" alt="Distribution Charts" width="800"/>
  <p><em>Executive Overview - Distribution & Revenue by Segment</em></p>
</div>

### 👤 Customer 360

<div align="center">
  <img src="Project Screenshots/Customer 360 tab Customer metrics cards (Revenue, Net Profit, Risk Score, CLV) and Risk Information..png" alt="Customer 360 Metrics" width="800"/>
  <p><em>Customer 360 - Metrics & Risk Information</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Customer 360 Revenue vs Profit & Risk vs CLV Charts.png" alt="Customer 360 Charts" width="800"/>
  <p><em>Customer 360 - Revenue, Profit, Risk & CLV Analysis</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Customer 360 Risk Info & Recent Transactions Table.png" alt="Customer 360 Transactions" width="800"/>
  <p><em>Customer 360 - Recent Transactions</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Customer 360 tab Customer search bar and initial customer profile info (Nasir Khan)..png" alt="Customer 360 Search" width="800"/>
  <p><em>Customer 360 - Customer Search & Profile</em></p>
</div>

### ⚠️ Credit Risk Analytics

<div align="center">
  <img src="Project Screenshots/Credit Risk Risk KPIs (High Risk Count, Avg Score, Total Exposure).png" alt="Credit Risk KPIs" width="800"/>
  <p><em>Credit Risk - Key Performance Indicators</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Credit Risk Risk Score by Level & Exposure Charts.png" alt="Credit Risk Charts" width="800"/>
  <p><em>Credit Risk - Score Distribution & Exposure Analysis</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Credit Risk Detailed Risk Analysis & Delinquency Table.png" alt="Credit Risk Table" width="800"/>
  <p><em>Credit Risk - Detailed Analysis & Delinquency</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Credit Risk Header & Filter Selection Panel.png" alt="Credit Risk Header" width="800"/>
  <p><em>Credit Risk - Header & Filter Selection</em></p>
</div>

### 📈 Profitability Analytics

<div align="center">
  <img src="Project Screenshots/Profitability Key Performance Indicators (Revenue, Profit, Customers).png" alt="Profitability KPIs" width="800"/>
  <p><em>Profitability - Key Performance Indicators</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Profitability Revenue & Profit Distribution by Customer Charts.png" alt="Profitability Charts" width="800"/>
  <p><em>Profitability - Revenue & Profit Distribution</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Profitability Customer Profitability Metrics Data Table.png" alt="Profitability Table" width="800"/>
  <p><em>Profitability - Customer Metrics Table</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Profitability Header, Filter Controls & Top Layout.png" alt="Profitability Header" width="800"/>
  <p><em>Profitability - Header & Filter Controls</em></p>
</div>

### 🔄 Churn Analytics

<div align="center">
  <img src="Project Screenshots/Churn KPIs (High Churn Risk, Avg Churn Probability, Total Customers).png" alt="Churn KPIs" width="800"/>
  <p><em>Churn Analytics - Key Performance Indicators</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Churn Risk & Churn Probability distribution charts.png" alt="Churn Charts" width="800"/>
  <p><em>Churn Analytics - Risk & Probability Distribution</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Churn Predictions customer probability & risk table.png" alt="Churn Table" width="800"/>
  <p><em>Churn Analytics - Customer Predictions</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Churn Analytics header, filter options, KPI preview.png" alt="Churn Header" width="800"/>
  <p><em>Churn Analytics - Header & Filter Options</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Filtered High Churn Risk Customers table.png" alt="Churn Filtered" width="800"/>
  <p><em>Churn Analytics - High Churn Risk Customers</em></p>
</div>

### 📦 Product Analytics

<div align="center">
  <img src="Project Screenshots/Product Analytics KPIs & Product Performance breakdown table.png" alt="Product Analytics KPIs" width="800"/>
  <p><em>Product Analytics - Performance Metrics</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Product Analytics Total Revenue & Customer Distribution charts.png" alt="Product Analytics Charts" width="800"/>
  <p><em>Product Analytics - Revenue & Distribution</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Product Analytics Non-Performing Loan (NPL) Rate chart view.png" alt="Product Analytics NPL" width="800"/>
  <p><em>Product Analytics - NPL Rate Tracking</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Product Analytics Header & productsegment filters.png" alt="Product Analytics Header" width="800"/>
  <p><em>Product Analytics - Header & Filters</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Product Analytics Average Balance chart view.png" alt="Product Analytics Balance" width="800"/>
  <p><em>Product Analytics - Average Balance Analysis</em></p>
</div>

### 💳 Transaction Analytics

<div align="center">
  <img src="Project Screenshots/Transaction Analytics Key Performance Indicators (KPI cards).png" alt="Transaction Analytics KPIs" width="800"/>
  <p><em>Transaction Analytics - Key Performance Indicators</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Transaction Analytics Volume by type & product bar charts.png" alt="Transaction Analytics Charts" width="800"/>
  <p><em>Transaction Analytics - Volume Analysis</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Transaction Analytics Recent Transactions data table.png" alt="Transaction Analytics Table" width="800"/>
  <p><em>Transaction Analytics - Recent Transactions</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Transaction Analytics Header, description & filter controls.png" alt="Transaction Analytics Header" width="800"/>
  <p><em>Transaction Analytics - Header & Filter Controls</em></p>
</div>

### 🧠 Decision Intelligence

<div align="center">
  <img src="Project Screenshots/Decision Intelligence – KPI Metrics Overview.png" alt="Decision Intelligence KPIs" width="800"/>
  <p><em>Decision Intelligence - Metrics Overview</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Decision Intelligence – Executive Recommendations.png" alt="Decision Intelligence Recommendations" width="800"/>
  <p><em>Decision Intelligence - Executive Recommendations</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Decision Intelligence – Header & Filter Controls.png" alt="Decision Intelligence Header" width="800"/>
  <p><em>Decision Intelligence - Header & Filter Controls</em></p>
</div>

### 🔴 Live Monitor

<div align="center">
  <img src="Project Screenshots/Live Monitor – Real-time Streaming Analytics & Metrics.png" alt="Live Monitor Dashboard" width="800"/>
  <p><em>Live Monitor - Real-time Streaming Analytics</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Live Monitor view displaying Risk Threshold Exceeded (High & Medium) and Payment Failure alerts..png" alt="Live Monitor Alerts" width="800"/>
  <p><em>Live Monitor - Alert Management</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Live Monitor – Recent Alerts Feed (HighMedium).png" alt="Live Monitor Feed" width="800"/>
  <p><em>Live Monitor - Recent Alerts Feed</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Live Monitor view displaying Account Anomaly (Low & High) and High Transaction Volume (Medium) alerts..png" alt="Live Monitor Anomaly" width="800"/>
  <p><em>Live Monitor - Account Anomaly Alerts</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Live Monitor view highlighting Payment Failure (Critical) and Suspicious Activity (Critical) alerts..png" alt="Live Monitor Critical" width="800"/>
  <p><em>Live Monitor - Critical Alerts</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Live Monitor view showing Risk Threshold Exceeded (Low), Payment Failure (Low), and Suspicious Activity alerts..png" alt="Live Monitor Low" width="800"/>
  <p><em>Live Monitor - Low Priority Alerts</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Live Monitor view showing Risk Threshold Exceeded, High Transaction Volume, and Payment Failure (Medium) alerts..png" alt="Live Monitor Mixed" width="800"/>
  <p><em>Live Monitor - Mixed Alert Types</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Live Monitor – Payment Failure & Anomaly Alerts.png" alt="Live Monitor Payment" width="800"/>
  <p><em>Live Monitor - Payment Failure & Anomaly</em></p>
</div>

### 🤖 Model Monitoring

<div align="center">
  <img src="Project Screenshots/Model Monitoring – KPI Summary Cards.png" alt="Model Monitoring KPIs" width="800"/>
  <p><em>Model Monitoring - Performance Metrics</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Model Monitoring – Performance Metrics Table.png" alt="Model Monitoring Table" width="800"/>
  <p><em>Model Monitoring - Detailed Performance</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Model Monitoring – Header & Configuration.png" alt="Model Monitoring Header" width="800"/>
  <p><em>Model Monitoring - Header & Configuration</em></p>
</div>

### ✅ Data Quality Monitoring

<div align="center">
  <img src="Project Screenshots/Data Quality Monitoring – Dashboard & Metrics Table.png" alt="Data Quality Dashboard" width="800"/>
  <p><em>Data Quality Monitoring - Dashboard & Metrics</em></p>
</div>

### � Customer Segmentation

<div align="center">
  <img src="Project Screenshots/Segmentation KPIs (Total Segments, Largest Segment, Total Customers).png" alt="Segmentation KPIs" width="800"/>
  <p><em>Customer Segmentation - Key Performance Indicators</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Customer Segments data table.png" alt="Segmentation Table" width="800"/>
  <p><em>Customer Segmentation - Data Table</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/customer-segmentation-filters.png" alt="Segmentation Filters" width="800"/>
  <p><em>Customer Segmentation - Filter Options</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Average Balance by Segment bar chart.png" alt="Segmentation Balance" width="800"/>
  <p><em>Customer Segmentation - Average Balance by Segment</em></p>
</div>

### �🔌 API Documentation

<div align="center">
  <img src="Project Screenshots/Swagger UI documentation page showing the OpenAPI 3.1 title banner, authorize button, and endpoint lists..png" alt="Swagger UI" width="800"/>
  <p><em>API Documentation - Swagger UI</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Top-level Redocly documentation interface displaying the Banking Analytics API title, version, and initial health check section..png" alt="ReDoc" width="800"/>
  <p><em>API Documentation - ReDoc</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Redocly UI showing documentation and response samples for apiv1healthready and apiv1healthlive.png" alt="ReDoc Health" width="800"/>
  <p><em>API Documentation - ReDoc Health Endpoints</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/OpenAPI 3.1.0 JSON specification schema showing API info and health check paths..png" alt="OpenAPI Schema" width="800"/>
  <p><em>API Documentation - OpenAPI Schema</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/JSON output from the root API endpoint listing links for docs, health, auth, and websocket routes..png" alt="API Root" width="800"/>
  <p><em>API Documentation - Root Endpoint Response</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/JSON response from the health endpoint displaying status (degraded), version, and database state..png" alt="API Health" width="800"/>
  <p><em>API Documentation - Health Endpoint Response</em></p>
</div>

### 🖨️ Export & Print

<div align="center">
  <img src="Project Screenshots/Shows the Executive Overview dashboard page inside the browser's Save as PDF  print preview dialog..png" alt="Print Preview" width="800"/>
  <p><em>Export - Print Preview / Save as PDF</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Shows the Streamlit Record a screencast overlay modal on the Executive Overview page..png" alt="Screencast" width="800"/>
  <p><em>Export - Record Screencast</em></p>
</div>

<div align="center">
  <img src="Project Screenshots/Shows the browser prompt asking to choose and share the screen..png" alt="Screen Share" width="800"/>
  <p><em>Export - Screen Share Prompt</em></p>
</div>

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 14 or higher
- Apache Kafka 2.8 or higher
- Redis 7 or higher
- Docker and Docker Compose (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Skismail57/Banking-Customer-Profitability-and-Risk-Analytics-Platform.git
   cd Banking-Customer-Profitability-and-Risk-Analytics-Platform
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-api.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   alembic upgrade head
   ```

### Running the Application

#### Option 1: Using Docker Compose (Recommended)

```bash
docker-compose up -d
```

This will start:
- FastAPI backend on port 8000
- Streamlit dashboard on port 8501
- PostgreSQL database
- Apache Kafka
- Redis

#### Option 2: Manual Setup

**Start the API server:**
```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Start the Streamlit dashboard:**
```bash
streamlit run frontend/streamlit_app.py --server.port 8501
```

**Start the streaming pipeline:**
```bash
python -m src.streaming.orchestrator
```

### Access Points

- **Streamlit Dashboard**: http://localhost:8501
- **API Documentation (Swagger)**: http://localhost:8000/api/docs
- **API Documentation (ReDoc)**: http://localhost:8000/api/redoc
- **Health Check**: http://localhost:8000/api/v1/health

---

## 📚 API Documentation

### Authentication

The API uses JWT authentication. Obtain a token by:

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'
```

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/customers` | GET | List customers with pagination and search |
| `/api/v1/customers/{customer_id}` | GET | Get customer by ID |
| `/api/v1/profitability/aggregate` | GET | Profitability metrics |
| `/api/v1/risk/aggregate` | GET | Risk metrics |
| `/api/v1/churn/aggregate` | GET | Churn metrics |
| `/api/v1/segments` | GET | List customer segments |
| `/api/v1/portfolio/summary` | GET | Portfolio summary |
| `/api/v1/health` | GET | Health check |

### Example Request

```bash
curl -X GET "http://localhost:8000/api/v1/customers?limit=10&offset=0" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 🧪 Testing

### Run all tests
```bash
pytest tests/ -v
```

### Run with coverage
```bash
pytest tests/ --cov=src --cov-report=html
```

### Run specific test suites
```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# API tests
pytest tests/api/ -v

# Security tests
pytest tests/security/ -v
```

---

## 🚢 Deployment

### Docker Deployment

Build the Docker image:
```bash
docker build -t banking-analytics-platform .
```

Run the container:
```bash
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e JWT_SECRET_KEY=your-secret-key \
  banking-analytics-platform
```

### Kubernetes Deployment

The platform includes Kubernetes manifests in the `k8s/production/` directory:

```bash
kubectl apply -f k8s/production/configmap.yaml
kubectl apply -f k8s/production/secret.yaml
kubectl apply -f k8s/production/deployment.yaml
kubectl apply -f k8s/production/service.yaml
```

### CI/CD Pipeline

The platform uses GitHub Actions for CI/CD:
- **CI Pipeline**: Runs on every push (lint, test, security scan, build)
- **CD Pipeline**: Automated deployment to staging/production with canary releases

---

## 📖 Documentation

- [Architecture Documentation](ARCHITECTURE.md) - Detailed system architecture
- [Data Dictionary](DATA_DICTIONARY.md) - Data model definitions
- [Assumptions & Limitations](docs/ASSUMPTIONS_AND_LIMITATIONS.md) - Platform constraints
- [Remediation Summary](REMEDIATION_SUMMARY.md) - Production readiness improvements
- [Project Constitution](PROJECT_CONSTITUTION.md) - Development principles

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow the [Project Constitution](PROJECT_CONSTITUTION.md)
- Write tests for new features
- Ensure code passes linting and security checks
- Update documentation as needed
- Use conventional commit messages

---

## ⚠️ Disclaimer

**This platform is an analytical and educational model for decision support only.** It does not make actual lending decisions, approve or reject loan applications, or replace human judgment in credit decisions. All risk scores, churn predictions, and recommendations are analytical outputs intended to support decision-making, not replace it.

For detailed assumptions and limitations, please refer to [Assumptions and Limitations](docs/ASSUMPTIONS_AND_LIMITATIONS.md).

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Sk Ismail**

- GitHub: [@Skismail57](https://github.com/Skismail57)
- LinkedIn: [Sk Ismail](https://linkedin.com/in/sk-ismail)

---

## 🙏 Acknowledgments

- Built with modern data engineering best practices
- Inspired by industry-leading banking analytics platforms
- Designed for scalability and production use
- Community-driven open-source development

---

## 📞 Support

For questions, issues, or contributions:
- Open an issue on GitHub
- Contact: [skismail57@gmail.com](mailto:skismail57@gmail.com)

---

<div align="center">
  <b>⭐ Star this repository if you find it useful! ⭐</b>
</div>
