# Docker Setup Guide

## Overview

This guide provides comprehensive documentation for containerizing the Banking Customer Profitability and Risk Analytics Platform using Docker and Docker Compose. The platform includes FastAPI, Streamlit, and PostgreSQL services.

---

## Prerequisites

- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Docker Compose
- At least 4GB RAM available for Docker
- At least 10GB disk space

---

## Architecture

### Services

The Docker Compose setup includes the following services:

1. **PostgreSQL Database** (`postgres`)
   - PostgreSQL 15 Alpine
   - Persistent volume for data
   - Health check for readiness
   - Port: 5432

2. **FastAPI Application** (`api`)
   - Python 3.9 slim image
   - Exposes REST API endpoints
   - Health check for monitoring
   - Port: 8000
   - Depends on PostgreSQL

3. **Streamlit Application** (`streamlit`)
   - Python 3.9 slim image
   - Web UI for analytics
   - Health check for monitoring
   - Port: 8501
   - Depends on PostgreSQL and API

4. **Analytics Pipeline** (`pipeline`)
   - Optional service for ETL/analytics jobs
   - Runs in batch mode
   - Depends on PostgreSQL
   - Profile-based activation

---

## File Structure

```
.
├── Dockerfile                  # FastAPI application Dockerfile
├── Dockerfile.streamlit        # Streamlit application Dockerfile
├── docker-compose.yml          # Production Docker Compose configuration
├── docker-compose.dev.yml      # Development override configuration
├── .dockerignore               # Docker ignore patterns
├── .env.example               # Environment variables template
└── .env                      # Actual environment variables (not committed)
```

---

## Local Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd "Banking Customer Profitability and Risk Analytics Platform"
```

### 2. Configure Environment Variables

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=banking_analytics
DB_USER=your_database_user
DB_PASSWORD=your_secure_password_here

# Application Configuration
APP_ENV=development
LOG_LEVEL=INFO
DEBUG=false

# API Configuration
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:8501

# Streamlit Configuration
STREAMLIT_PORT=8501
CACHE_TTL=3600
```

**Security Note**: Never commit `.env` to version control. It contains sensitive credentials.

### 3. Build and Start Services

#### Production Mode

```bash
docker-compose up -d
```

This starts all services in detached mode:
- PostgreSQL on port 5432
- FastAPI on port 8000
- Streamlit on port 8501

#### Development Mode

For development with hot reload:

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

This enables:
- FastAPI auto-reload on code changes
- Streamlit auto-reload on code changes
- Debug logging
- Volume mounts for live code editing

### 4. Verify Services

Check service status:

```bash
docker-compose ps
```

Expected output:
```
NAME                        STATUS
banking_analytics_api        Up (healthy)
banking_analytics_db         Up (healthy)
banking_analytics_streamlit  Up (healthy)
```

View logs:

```bash
docker-compose logs -f
```

View specific service logs:

```bash
docker-compose logs -f api
docker-compose logs -f streamlit
docker-compose logs -f postgres
```

---

## Database Setup

### Automatic Initialization

The PostgreSQL service includes automatic initialization:

1. **Database Creation**: Database is created based on `DB_NAME` environment variable
2. **Volume Persistence**: Data persists in Docker volume `postgres_data`
3. **Init Scripts**: SQL scripts in `sql/init/` run automatically on first startup

### Manual Database Setup

If you need to set up the database manually:

#### Connect to PostgreSQL

```bash
docker-compose exec postgres psql -U postgres -d banking_analytics
```

#### Run SQL Scripts

```bash
# Run schema creation
docker-compose exec postgres psql -U postgres -d banking_analytics -f sql/schema/schema.sql

# Run data loading
docker-compose exec postgres psql -U postgres -d banking_analytics -f sql/data/load_data.sql

# Create views
docker-compose exec postgres psql -U postgres -d banking_analytics -f sql/views/vw_executive_overview_kpi.sql
```

#### Backup Database

```bash
docker-compose exec postgres pg_dump -U postgres banking_analytics > backup.sql
```

#### Restore Database

```bash
docker-compose exec -T postgres psql -U postgres banking_analytics < backup.sql
```

---

## Pipeline Execution

### Run Analytics Pipeline

The analytics pipeline service runs ETL and analytics jobs:

#### Start Pipeline Service

```bash
docker-compose --profile pipeline up pipeline
```

This starts the pipeline service which:
- Connects to PostgreSQL
- Runs data ingestion
- Executes analytics calculations
- Stores results in database

#### Run Pipeline Once

```bash
docker-compose run --rm pipeline
```

This runs the pipeline once and removes the container after completion.

#### Schedule Pipeline

For scheduled execution, use cron or a job scheduler:

```bash
# Add to crontab
0 2 * * * cd /path/to/project && docker-compose --profile pipeline run --rm pipeline
```

---

## API Startup

### Start FastAPI Service

The FastAPI service starts automatically with Docker Compose.

#### Manual Start

```bash
docker-compose up -d api
```

#### Access API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/api/v1/health

#### Test API Endpoints

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Get customers
curl http://localhost:8000/api/v1/customers

# Get profitability aggregate
curl http://localhost:8000/api/v1/profitability/aggregate
```

#### API Configuration

The API configuration is in `api/config.py`:

```python
class Settings(BaseSettings):
    app_name: str = "Banking Analytics API"
    app_version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "5432"))
    db_name: str = os.getenv("DB_NAME", "banking_analytics")
    db_user: str = os.getenv("DB_USER", "postgres")
    db_password: str = os.getenv("DB_PASSWORD", "")
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8501"]
    log_level: str = "INFO"
```

---

## Streamlit Startup

### Start Streamlit Service

The Streamlit service starts automatically with Docker Compose.

#### Manual Start

```bash
docker-compose up -d streamlit
```

#### Access Streamlit UI

Open browser: http://localhost:8501

#### Streamlit Configuration

The Streamlit configuration is in `streamlit/.streamlit/config.toml`:

```toml
[theme]
base = "light"
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"

[client]
showErrorDetails = true
maxUploadSize = 200

[logger]
level = "info"
```

#### Streamlit Pages

The Streamlit application includes pages for:
- Home
- Executive Overview
- Customer 360
- Profitability
- Risk
- Segmentation
- Churn
- Transactions
- Products
- Decision Intelligence
- Model Monitoring
- Data Quality

---

## Power BI Connection Approach

### Direct Database Connection

Power BI can connect directly to the PostgreSQL database:

#### Connection String

```
postgresql://DB_USER:DB_PASSWORD@localhost:5432/DB_NAME
```

#### Steps in Power BI Desktop

1. Open Power BI Desktop
2. Click "Get Data" → "Database" → "PostgreSQL database"
3. Enter connection details:
   - Server: `localhost`
   - Database: `banking_analytics`
   - Username: `DB_USER`
   - Password: `DB_PASSWORD`
4. Click "Connect"
5. Select tables/views to import

#### Using Docker Network

If Power BI is running in a different network:

1. Find PostgreSQL container IP:
```bash
docker inspect banking_analytics_db | grep IPAddress
```

2. Use the IP in connection string

### API-Based Connection

Power BI can connect via the FastAPI API:

#### Steps in Power BI Desktop

1. Open Power BI Desktop
2. Click "Get Data" → "Web"
3. Enter API URL: `http://localhost:8000/api/v1/profitability/aggregate`
4. Click "Connect"
5. Transform data as needed

### Data Refresh

#### Direct Database Refresh

Power BI can refresh data directly from PostgreSQL:
- Configure scheduled refresh in Power BI Service
- Ensure PostgreSQL is accessible from Power BI Service

#### API-Based Refresh

For API-based connections:
- Use Power Automate to trigger refresh
- Call API endpoints to get latest data

---

## Development Workflow

### Hot Reload

In development mode, code changes trigger automatic reload:

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

Changes to:
- `src/` directory → API reloads
- `streamlit/` directory → Streamlit reloads
- `api/` directory → API reloads

### Running Tests

Run tests inside containers:

```bash
# Run all tests
docker-compose exec api pytest tests/

# Run specific test
docker-compose exec api pytest tests/unit/decision_intelligence/test_base.py

# Run with coverage
docker-compose exec api pytest --cov=src tests/
```

### Debugging

#### Attach Debugger

For VS Code debugging:
1. Install Python extension
2. Create `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Remote Attach",
      "type": "python",
      "request": "attach",
      "connect": {
        "host": "localhost",
        "port": 5678
      }
    }
  ]
}
```

#### View Logs

```bash
docker-compose logs -f api
docker-compose logs -f streamlit
```

---

## Production Deployment

### Build Images

```bash
docker-compose build
```

### Push to Registry

```bash
# Tag images
docker tag banking_analytics_api your-registry/banking-analytics-api:latest
docker tag banking_analytics_streamlit your-registry/banking-analytics-streamlit:latest

# Push images
docker push your-registry/banking-analytics-api:latest
docker push your-registry/banking-analytics-streamlit:latest
```

### Production Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

  api:
    image: your-registry/banking-analytics-api:latest
    environment:
      DB_HOST: postgres
      DB_PORT: 5432
      DB_NAME: ${DB_NAME}
      DB_USER: ${DB_USER}
      DB_PASSWORD: ${DB_PASSWORD}
    depends_on:
      - postgres
    restart: always

  streamlit:
    image: your-registry/banking-analytics-streamlit:latest
    environment:
      DB_HOST: postgres
      DB_PORT: 5432
      DB_NAME: ${DB_NAME}
      DB_USER: ${DB_USER}
      DB_PASSWORD: ${DB_PASSWORD}
    depends_on:
      - postgres
      - api
    restart: always

volumes:
  postgres_data:
```

### Deploy

```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## Health Checks

### Service Health Status

Check health of all services:

```bash
docker-compose ps
```

Expected output shows `(healthy)` status for all services.

### Manual Health Checks

```bash
# PostgreSQL
docker-compose exec postgres pg_isready -U postgres

# FastAPI
curl http://localhost:8000/api/v1/health

# Streamlit
curl http://localhost:8501
```

### Health Check Configuration

Health checks are configured in `docker-compose.yml`:

```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/api/v1/health')"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 10s
```

---

## Troubleshooting

### Common Issues

**Port Already in Use**:
```bash
# Check what's using the port
netstat -ano | findstr :8000

# Change port in .env
API_PORT=8001
```

**Database Connection Failed**:
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

**Container Won't Start**:
```bash
# View logs
docker-compose logs <service-name>

# Rebuild container
docker-compose up -d --build <service-name>
```

**Volume Issues**:
```bash
# Remove volume (WARNING: deletes data)
docker-compose down -v

# Recreate volume
docker-compose up -d
```

### Reset Environment

To completely reset the environment:

```bash
# Stop all services
docker-compose down

# Remove volumes
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Rebuild and start
docker-compose up -d --build
```

---

## Security Best Practices

### Environment Variables

- Never commit `.env` file
- Use strong passwords in production
- Rotate credentials regularly
- Use secrets management in production (e.g., AWS Secrets Manager, HashiCorp Vault)

### Network Security

- Use Docker networks for service isolation
- Don't expose PostgreSQL port in production
- Use HTTPS/TLS for API in production
- Implement authentication for API endpoints

### Container Security

- Use non-root user in containers (already configured)
- Keep images updated
- Scan images for vulnerabilities
- Use minimal base images (alpine/slim)

### Data Security

- Encrypt data at rest
- Encrypt data in transit
- Implement backup strategy
- Regular security audits

---

## Performance Optimization

### Resource Limits

Add resource limits to `docker-compose.yml`:

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### Database Optimization

- Tune PostgreSQL configuration
- Add indexes to frequently queried columns
- Use connection pooling
- Monitor query performance

### Caching

- Enable Streamlit caching
- Use Redis for distributed caching
- Cache API responses

---

## Monitoring

### Logs

View logs in real-time:

```bash
docker-compose logs -f
```

### Metrics

Consider adding monitoring:
- Prometheus for metrics collection
- Grafana for visualization
- ELK stack for log aggregation

### Alerts

Set up alerts for:
- Service health failures
- High resource usage
- Database connection issues

---

## Backup and Recovery

### Database Backup

```bash
# Backup
docker-compose exec postgres pg_dump -U postgres banking_analytics > backup_$(date +%Y%m%d).sql

# Restore
docker-compose exec -T postgres psql -U postgres banking_analytics < backup_20260907.sql
```

### Volume Backup

```bash
# Backup volume
docker run --rm -v banking_analytics_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data

# Restore volume
docker run --rm -v banking_analytics_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_backup.tar.gz -C /
```

---

## Summary

The Docker setup provides:

- **Containerized Services**: FastAPI, Streamlit, PostgreSQL
- **Health Checks**: Automated health monitoring
- **Persistent Storage**: Database volume for data persistence
- **Development Mode**: Hot reload for development
- **Production Mode**: Optimized for production deployment
- **Security**: Environment variables, non-root users, network isolation
- **Scalability**: Easy to scale services
- **Portability**: Runs anywhere Docker is available
