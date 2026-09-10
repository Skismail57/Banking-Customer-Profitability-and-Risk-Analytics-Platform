# FastAPI Implementation Guide

## Overview

This guide provides comprehensive documentation for the FastAPI service that exposes analytical capabilities for the Banking Customer Profitability and Risk Analytics Platform. The API provides RESTful endpoints for customer data, profitability, risk, churn, segments, and portfolio analytics.

---

## Architecture

### Single Source of Truth

**Principle**: All business logic resides in the Python analytics layer. The FastAPI service only exposes pre-calculated metrics from the database.

**Data Flow**:
1. Python analytics modules calculate metrics (profitability, risk, churn, CLV, etc.)
2. Metrics are stored in database tables
3. FastAPI queries the database via SQL
4. Responses are validated with Pydantic schemas
5. No business logic in API endpoints

### Application Structure

```
api/
├── main.py                      # FastAPI application entry point
├── config.py                   # Application configuration
├── database.py                 # Database connection management
├── __init__.py
├── routers/                    # API route handlers
│   ├── __init__.py
│   ├── health.py               # Health check endpoint
│   ├── customers.py            # Customer endpoints
│   ├── profitability.py         # Profitability endpoints
│   ├── risk.py                 # Risk endpoints
│   ├── segments.py             # Segment endpoints
│   ├── churn.py                # Churn endpoints
│   └── portfolio.py            # Portfolio endpoints
└── schemas/                    # Pydantic schemas
    ├── __init__.py
    ├── common.py               # Common schemas (pagination, health, error)
    ├── customer.py             # Customer schemas
    ├── profitability.py         # Profitability schemas
    ├── risk.py                 # Risk schemas
    ├── churn.py                # Churn schemas
    ├── transaction.py           # Transaction schemas
    ├── recommendation.py        # Recommendation schemas
    ├── segment.py              # Segment schemas
    └── portfolio.py            # Portfolio schemas
```

---

## Installation

### Prerequisites

- Python 3.9+
- pip
- Virtual environment (recommended)
- PostgreSQL database

### Setup

1. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install fastapi uvicorn sqlalchemy pydantic-settings psycopg2-binary asyncpg
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
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Configuration

### Application Configuration (`config.py`)

The application uses Pydantic Settings for configuration:

```python
class Settings(BaseSettings):
    # Application
    app_name: str = "Banking Analytics API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "5432"))
    db_name: str = os.getenv("DB_NAME", "banking_analytics")
    db_user: str = os.getenv("DB_USER", "postgres")
    db_password: str = os.getenv("DB_PASSWORD", "")
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8501"]
    
    # Logging
    log_level: str = "INFO"
    
    # Pagination
    default_page_size: int = 50
    max_page_size: int = 500
```

---

## API Endpoints

### Health Check

**GET** `/api/v1/health`

Health check endpoint to verify API and database status.

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-09-07T12:00:00Z",
  "database": "healthy"
}
```

---

### Customer Endpoints

#### Get Customers

**GET** `/api/v1/customers`

Get list of customers with pagination and filters.

**Query Parameters**:
- `page` (int): Page number (default: 1)
- `page_size` (int): Items per page (default: 50, max: 500)
- `segment` (str, optional): Filter by segment
- `region` (str, optional): Filter by region

**Response**:
```json
{
  "customers": [
    {
      "customer_key": "CUST_001",
      "customer_name": "John Doe",
      "segment": "premium",
      "region": "North",
      "acquisition_date": "2020-01-15",
      "customer_age": 45,
      "income_level": "High"
    }
  ],
  "total": 10000
}
```

#### Get Customer Detail

**GET** `/api/v1/customers/{customer_id}`

Get detailed customer information including metrics.

**Path Parameters**:
- `customer_id` (str): Customer identifier

**Response**:
```json
{
  "customer_key": "CUST_001",
  "customer_name": "John Doe",
  "segment": "premium",
  "region": "North",
  "acquisition_date": "2020-01-15",
  "customer_age": 45,
  "income_level": "High",
  "net_profit": 15000.00,
  "clv": 50000.00,
  "risk_level": "low",
  "churn_probability": 0.12,
  "exposure_amount": 75000.00
}
```

#### Get Customer Profitability

**GET** `/api/v1/customers/{customer_id}/profitability`

Get customer profitability history.

**Path Parameters**:
- `customer_id` (str): Customer identifier

**Response**:
```json
{
  "profitability_history": [
    {
      "customer_key": "CUST_001",
      "net_profit": 15000.00,
      "risk_adjusted_profit": 13500.00,
      "as_of_date": "2026-09-01"
    }
  ]
}
```

#### Get Customer Risk

**GET** `/api/v1/customers/{customer_id}/risk`

Get customer risk history.

**Path Parameters**:
- `customer_id` (str): Customer identifier

**Response**:
```json
{
  "risk_history": [
    {
      "customer_key": "CUST_001",
      "risk_level": "low",
      "risk_trend": "stable",
      "exposure_amount": 75000.00,
      "credit_utilization": 0.35,
      "days_past_due": 0,
      "credit_score": 750,
      "balance_to_income_ratio": 0.25,
      "as_of_date": "2026-09-01"
    }
  ]
}
```

#### Get Customer Transactions

**GET** `/api/v1/customers/{customer_id}/transactions`

Get customer transactions with pagination.

**Path Parameters**:
- `customer_id` (str): Customer identifier

**Query Parameters**:
- `page` (int): Page number (default: 1)
- `page_size` (int): Items per page (default: 50, max: 500)

**Response**:
```json
{
  "transactions": [
    {
      "transaction_key": "TXN_001",
      "customer_key": "CUST_001",
      "transaction_date": "2026-09-01",
      "amount": 100.00,
      "product_type": "Credit Card",
      "transaction_type": "purchase",
      "channel": "online"
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 50
}
```

#### Get Customer Churn

**GET** `/api/v1/customers/{customer_id}/churn`

Get customer churn history.

**Path Parameters**:
- `customer_id` (str): Customer identifier

**Response**:
```json
{
  "churn_history": [
    {
      "customer_key": "CUST_001",
      "churn_probability": 0.12,
      "clv": 50000.00,
      "as_of_date": "2026-09-01"
    }
  ]
}
```

#### Get Customer Recommendations

**GET** `/api/v1/customers/{customer_id}/recommendations`

Get customer recommendations from decision intelligence.

**Path Parameters**:
- `customer_id` (str): Customer identifier

**Response**:
```json
{
  "recommendations": [
    {
      "recommendation_key": "REC_001",
      "customer_key": "CUST_001",
      "segment": "premium",
      "priority": "high",
      "confidence": "high",
      "recommended_action": "Offer premium product",
      "reason": "High profitability, low risk",
      "generated_at": "2026-09-01"
    }
  ]
}
```

---

### Aggregate Endpoints

#### Profitability Aggregate

**GET** `/api/v1/profitability/aggregate`

Get aggregate profitability metrics.

**Query Parameters**:
- `start_date` (date, optional): Start date
- `end_date` (date, optional): End date

**Response**:
```json
{
  "total_net_profit": 5000000.00,
  "avg_profit_per_customer": 500.00,
  "total_risk_adjusted_profit": 4500000.00,
  "profit_margin": 0.25,
  "customer_count": 10000,
  "as_of_date": "2026-09-01"
}
```

#### Profitability by Segment

**GET** `/api/v1/profitability/by-segment`

Get profitability metrics by segment.

**Query Parameters**:
- `start_date` (date, optional): Start date
- `end_date` (date, optional): End date

**Response**:
```json
[
  {
    "segment": "premium",
    "total_profit": 3000000.00,
    "avg_profit": 1500.00,
    "customer_count": 2000
  }
]
```

#### Risk Aggregate

**GET** `/api/v1/risk/aggregate`

Get aggregate risk metrics.

**Query Parameters**:
- `start_date` (date, optional): Start date
- `end_date` (date, optional): End date

**Response**:
```json
{
  "total_customers": 10000,
  "low_risk_count": 7000,
  "medium_risk_count": 2000,
  "high_risk_count": 500,
  "critical_risk_count": 150,
  "total_exposure": 100000000.00,
  "delinquency_rate": 0.05,
  "avg_utilization": 0.45,
  "as_of_date": "2026-09-01"
}
```

#### Risk Distribution

**GET** `/api/v1/risk/distribution`

Get risk distribution by risk level.

**Query Parameters**:
- `start_date` (date, optional): Start date
- `end_date` (date, optional): End date

**Response**:
```json
[
  {
    "risk_level": "low",
    "count": 7000,
    "exposure": 30000000.00
  }
]
```

#### Segments

**GET** `/api/v1/segments`

Get all segments with metrics.

**Response**:
```json
{
  "segments": [
    {
      "segment": "premium",
      "customer_count": 2000,
      "avg_profit": 1500.00,
      "avg_risk_score": 1.5,
      "avg_churn_probability": 0.10
    }
  ],
  "total": 3
}
```

#### Churn Aggregate

**GET** `/api/v1/churn/aggregate`

Get aggregate churn metrics.

**Query Parameters**:
- `start_date` (date, optional): Start date
- `end_date` (date, optional): End date

**Response**:
```json
{
  "avg_churn_probability": 0.15,
  "high_churn_risk_customers": 1550,
  "retention_rate": 0.85,
  "high_churn_high_clv_count": 300,
  "customer_count": 10000,
  "as_of_date": "2026-09-01"
}
```

#### Churn by Segment

**GET** `/api/v1/churn/by-segment`

Get churn metrics by segment.

**Query Parameters**:
- `start_date` (date, optional): Start date
- `end_date` (date, optional): End date

**Response**:
```json
[
  {
    "segment": "premium",
    "avg_churn_probability": 0.10,
    "high_churn_count": 200
  }
]
```

#### Portfolio Summary

**GET** `/api/v1/portfolio/summary`

Get portfolio summary metrics.

**Response**:
```json
{
  "total_customers": 10000,
  "total_exposure": 100000000.00,
  "total_profit": 5000000.00,
  "avg_risk_score": 1.5,
  "high_risk_exposure": 30000000.00,
  "concentration_hhi": 0.025,
  "as_of_date": "2026-09-01"
}
```

---

## Pydantic Schemas

### Common Schemas

#### PaginationParams
```python
class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(50, ge=1, le=500)
```

#### HealthResponse
```python
class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime
    database: str
```

#### ErrorResponse
```python
class ErrorResponse(BaseModel):
    error: str
    message: str
    detail: Optional[str] = None
```

### Customer Schemas

#### Customer
```python
class Customer(BaseModel):
    customer_key: str
    customer_name: Optional[str]
    segment: Optional[str]
    region: Optional[str]
    acquisition_date: Optional[date]
    customer_age: Optional[int]
    income_level: Optional[str]
```

#### CustomerDetail
```python
class CustomerDetail(Customer):
    net_profit: Optional[float]
    clv: Optional[float]
    risk_level: Optional[str]
    churn_probability: Optional[float]
    exposure_amount: Optional[float]
```

### Other Schemas

Similar schemas exist for:
- Profitability (`CustomerProfitability`, `ProfitabilityAggregate`, `ProfitabilityBySegment`)
- Risk (`CustomerRisk`, `RiskAggregate`, `RiskDistribution`)
- Churn (`CustomerChurn`, `ChurnAggregate`, `ChurnBySegment`)
- Transaction (`Transaction`)
- Recommendation (`Recommendation`)
- Segment (`Segment`)
- Portfolio (`PortfolioSummary`)

---

## Error Handling

### HTTP Status Codes

- `200 OK`: Successful request
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

### Error Response Format

```json
{
  "detail": "Error message"
}
```

### Error Handling Pattern

All endpoints include try-except blocks:

```python
try:
    # Database query
    result = db.execute(text(query), params).fetchall()
    
    if not result:
        raise HTTPException(status_code=404, detail="Data not found")
    
    return schema(**result._asdict())
except HTTPException:
    raise
except Exception as e:
    logger.error(f"Error: {e}")
    raise HTTPException(status_code=500, detail="Error processing request")
```

---

## Logging

### Configuration

Logging is configured in `main.py`:

```python
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
```

### Log Levels

- `INFO`: Normal operations
- `WARNING`: Non-critical issues
- `ERROR`: Errors requiring attention

### Log Messages

All endpoints log errors:

```python
logger.error(f"Error fetching customers: {e}")
```

---

## Database Connection Management

### Connection Pool

The application uses SQLAlchemy connection pooling:

```python
engine = create_engine(settings.db_url, pool_pre_ping=True)
```

### Session Management

Use dependency injection for database sessions:

```python
@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Async Support

Async engine and session factory are also available:

```python
async_engine = create_async_engine(
    settings.db_url.replace("postgresql://", "postgresql+asyncpg://"),
    pool_pre_ping=True
)
```

---

## Pagination

### Pagination Parameters

Pagination is handled via `PaginationParams` schema:

```python
class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(50, ge=1, le=500)
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size
```

### Usage in Endpoints

```python
@router.get("/customers")
async def get_customers(
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db)
):
    # Use pagination.offset and pagination.page_size
    query += f" LIMIT :limit OFFSET :offset"
    params["limit"] = pagination.page_size
    params["offset"] = pagination.offset
```

---

## Security

### Environment Variables

Store sensitive configuration in environment variables:

```bash
export DB_PASSWORD=your_secure_password
```

### Data Masking

Sensitive customer data is not exposed in API responses. Only necessary fields are included in schemas.

### CORS

CORS is configured to allow specific origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## API Documentation

### Interactive Documentation

FastAPI provides interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### OpenAPI Schema

The OpenAPI schema is available at:
- `http://localhost:8000/openapi.json`

---

## Deployment

### Local Development

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Production

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t banking-api .
docker run -p 8000:8000 banking-api
```

---

## Testing

### Example Requests

#### Health Check
```bash
curl http://localhost:8000/api/v1/health
```

#### Get Customers
```bash
curl http://localhost:8000/api/v1/customers?page=1&page_size=10
```

#### Get Customer Detail
```bash
curl http://localhost:8000/api/v1/customers/CUST_001
```

#### Get Profitability Aggregate
```bash
curl http://localhost:8000/api/v1/profitability/aggregate
```

---

## Best Practices

### Development

1. **Use Pydantic schemas**: Validate all inputs and outputs
2. **Dependency injection**: Use `Depends()` for database sessions
3. **Error handling**: Always include try-except blocks
4. **Logging**: Log errors for debugging
5. **Documentation**: Add docstrings to all endpoints

### Security

1. **Environment variables**: Never hardcode credentials
2. **Data masking**: Don't expose sensitive data
3. **CORS**: Configure CORS appropriately
4. **Validation**: Use Pydantic for input validation
5. **Rate limiting**: Consider adding rate limiting for production

### Performance

1. **Connection pooling**: Use SQLAlchemy connection pooling
2. **Pagination**: Always paginate large result sets
3. **Caching**: Consider caching frequently accessed data
4. **Async**: Use async endpoints for I/O-bound operations
5. **Indexes**: Ensure database has proper indexes

---

## Troubleshooting

### Common Issues

**Database Connection Errors**:
- Check database credentials
- Verify database is running
- Check network connectivity

**Import Errors**:
- Ensure all dependencies are installed
- Check Python version compatibility
- Verify virtual environment is activated

**Validation Errors**:
- Check Pydantic schema definitions
- Verify input data types
- Review error messages for details

---

## Support

For issues or questions:
1. Check this guide
2. Review API documentation at `/docs`
3. Check database schema
4. Contact development team
