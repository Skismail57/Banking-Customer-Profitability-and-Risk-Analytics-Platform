# Deployment Guide

This guide provides comprehensive instructions for deploying the Banking Customer Profitability and Risk Analytics Platform to production environments.

---

## Deployment Options

### 1. Docker Deployment (Recommended)

Docker deployment provides containerized, reproducible deployments.

#### Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 20GB disk space minimum

#### Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: banking_analytics_db_prod
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./sql/init:/docker-entrypoint-initdb.d:ro
    networks:
      - banking_network
    restart: always
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    image: your-registry/banking-analytics-api:latest
    container_name: banking_analytics_api_prod
    environment:
      DB_HOST: postgres
      DB_PORT: 5432
      DB_NAME: ${DB_NAME}
      DB_USER: ${DB_USER}
      DB_PASSWORD: ${DB_PASSWORD}
      CORS_ORIGINS: ${CORS_ORIGINS}
      LOG_LEVEL: INFO
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - banking_network
    restart: always
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/api/v1/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

  streamlit:
    image: your-registry/banking-analytics-streamlit:latest
    container_name: banking_analytics_streamlit_prod
    environment:
      DB_HOST: postgres
      DB_PORT: 5432
      DB_NAME: ${DB_NAME}
      DB_USER: ${DB_USER}
      DB_PASSWORD: ${DB_PASSWORD}
    ports:
      - "8501:8501"
    depends_on:
      postgres:
        condition: service_healthy
      api:
        condition: service_healthy
    networks:
      - banking_network
    restart: always
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8501')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 15s

networks:
  banking_network:
    driver: bridge

volumes:
  postgres_data:
    driver: local
```

#### Deployment Steps

1. **Build Images**
```bash
docker build -t banking-analytics-api:latest -f Dockerfile .
docker build -t banking-analytics-streamlit:latest -f Dockerfile.streamlit .
```

2. **Push to Registry**
```bash
docker tag banking-analytics-api:latest your-registry/banking-analytics-api:latest
docker tag banking-analytics-streamlit:latest your-registry/banking-analytics-streamlit:latest
docker push your-registry/banking-analytics-api:latest
docker push your-registry/banking-analytics-streamlit:latest
```

3. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with production values
```

4. **Deploy**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

5. **Verify Deployment**
```bash
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs -f
```

---

### 2. Kubernetes Deployment

For larger deployments, Kubernetes provides scalability and orchestration.

#### Prerequisites

- Kubernetes cluster 1.20+
- kubectl configured
- Container registry access

#### Kubernetes Manifests

Create `k8s/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: banking-analytics-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: banking-analytics-api
  template:
    metadata:
      labels:
        app: banking-analytics-api
    spec:
      containers:
      - name: api
        image: your-registry/banking-analytics-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DB_HOST
          value: "postgres-service"
        - name: DB_PORT
          value: "5432"
        - name: DB_NAME
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: db-name
        - name: DB_USER
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: db-user
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: db-password
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: banking-analytics-api
spec:
  selector:
    app: banking-analytics-api
  ports:
  - port: 8000
    targetPort: 8000
  type: LoadBalancer
```

#### Deployment Steps

1. **Create Secrets**
```bash
kubectl create secret generic db-secret \
  --from-literal=db-name=banking_analytics \
  --from-literal=db-user=postgres \
  --from-literal=db-password=your-password
```

2. **Deploy**
```bash
kubectl apply -f k8s/deployment.yaml
```

3. **Verify**
```bash
kubectl get pods
kubectl logs -f deployment/banking-analytics-api
```

---

### 3. Cloud Deployment

#### AWS Deployment

**Using AWS ECS**

1. **Push to ECR**
```bash
aws ecr create-repository --repository-name banking-analytics-api
docker tag banking-analytics-api:latest <account-id>.dkr.ecr.<region>.amazonaws.com/banking-analytics-api
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/banking-analytics-api:latest
```

2. **Create ECS Task Definition**
```json
{
  "family": "banking-analytics-api",
  "containerDefinitions": [
    {
      "name": "api",
      "image": "<account-id>.dkr.ecr.<region>.amazonaws.com/banking-analytics-api:latest",
      "memory": 1024,
      "cpu": 512,
      "portMappings": [
        {
          "containerPort": 8000
        }
      ],
      "environment": [
        {
          "name": "DB_HOST",
          "value": "postgres.rds.amazonaws.com"
        }
      ],
      "secrets": [
        {
          "name": "DB_PASSWORD",
          "valueFrom": "arn:aws:secretsmanager:<region>:<account-id>:secret:db-password"
        }
      ]
    }
  ]
}
```

3. **Create ECS Service**
```bash
aws ecs create-service \
  --cluster banking-analytics \
  --service-name api \
  --task-definition banking-analytics-api \
  --desired-count 3 \
  --launch-type FARGATE
```

**Using AWS RDS for PostgreSQL**

```bash
aws rds create-db-instance \
  --db-instance-identifier banking-analytics-db \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --engine-version 15 \
  --allocated-storage 20 \
  --master-username admin \
  --master-user-password your-password \
  --vpc-security-group-ids sg-xxxxx
```

#### Azure Deployment

**Using Azure Container Instances**

```bash
az container create \
  --resource-group banking-analytics-rg \
  --name banking-analytics-api \
  --image your-registry/banking-analytics-api:latest \
  --cpu 1 \
  --memory 2 \
  --ports 8000 \
  --environment-variables DB_HOST=postgres.database.azure.net \
  --secure-environment-variables DB_PASSWORD=your-password
```

**Using Azure Database for PostgreSQL**

```bash
az postgres server create \
  --resource-group banking-analytics-rg \
  --name banking-analytics-db \
  --location eastus \
  --admin-user admin \
  --admin-password your-password \
  --sku-name GP_Gen5_2
```

#### GCP Deployment

**Using Cloud Run**

```bash
gcloud run deploy banking-analytics-api \
  --image gcr.io/your-project/banking-analytics-api:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DB_HOST=cloudsql
```

**Using Cloud SQL for PostgreSQL**

```bash
gcloud sql instances create banking-analytics-db \
  --tier db-f1-micro \
  --region us-central1 \
  --database-version POSTGRES_15
```

---

## Database Setup

### Production Database Configuration

#### PostgreSQL Configuration

Edit `postgresql.conf` for production:

```ini
# Connection Settings
max_connections = 200
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 2621kB
min_wal_size = 1GB
max_wal_size = 4GB

# Logging
logging_collector = on
log_directory = 'pg_log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_statement = 'all'
log_duration = on
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '

# Performance
shared_preload_libraries = 'pg_stat_statements'
```

#### Database Initialization

```bash
# Connect to database
psql -h localhost -U postgres -d banking_analytics

# Run schema
\i sql/schema/schema.sql

# Run data loading
\i sql/data/load_data.sql

# Create views
\i sql/views/vw_executive_overview_kpi.sql
\i sql/views/vw_customer_360_detail.sql
\i sql/views/vw_profitability_trend.sql
\i sql/views/vw_risk_distribution.sql
\i sql/views/vw_segment_analysis.sql
\i sql/views/vw_churn_retention.sql
\i sql/views/vw_product_analytics.sql
\i sql/views/vw_transaction_analytics.sql
\i sql/views/vw_decision_intelligence.sql
\i sql/views/vw_model_monitoring.sql
```

---

## Pipeline Deployment

### Scheduled Pipeline Execution

#### Using Cron

```bash
# Edit crontab
crontab -e

# Add daily pipeline at 2 AM
0 2 * * * cd /opt/banking-analytics && /opt/banking-analytics/venv/bin/python -m src.pipeline.orchestrator >> /var/log/banking-analytics/pipeline.log 2>&1
```

#### Using Systemd Timer

Create `/etc/systemd/system/banking-analytics-pipeline.service`:

```ini
[Unit]
Description=Banking Analytics Pipeline
After=network.target postgresql.service

[Service]
Type=oneshot
User=analytics
WorkingDirectory=/opt/banking-analytics
Environment="PATH=/opt/banking-analytics/venv/bin"
ExecStart=/opt/banking-analytics/venv/bin/python -m src.pipeline.orchestrator
```

Create `/etc/systemd/system/banking-analytics-pipeline.timer`:

```ini
[Unit]
Description=Run Banking Analytics Pipeline Daily

[Timer]
OnCalendar=*-*-* 02:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable and start:

```bash
systemctl enable banking-analytics-pipeline.timer
systemctl start banking-analytics-pipeline.timer
```

---

## Monitoring

### Application Monitoring

#### Health Checks

API health check endpoint: `GET /api/v1/health`

Response:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2026-09-07T20:30:00Z"
}
```

#### Logging

Logs are stored in:
- Application logs: `/var/log/banking-analytics/`
- Database logs: PostgreSQL log directory
- Container logs: `docker-compose logs` or Kubernetes logs

#### Metrics

Consider implementing:
- Prometheus for metrics collection
- Grafana for visualization
- ELK stack for log aggregation

### Database Monitoring

#### PostgreSQL Monitoring

```sql
-- Check active connections
SELECT count(*) FROM pg_stat_activity;

-- Check slow queries
SELECT query, mean_exec_time, calls 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;

-- Check table sizes
SELECT relname, pg_size_pretty(pg_total_relation_size(relid)) 
FROM pg_catalog.pg_statio_user_tables 
ORDER BY pg_total_relation_size(relid) DESC;
```

---

## Security

### Environment Variables

Store sensitive data in environment variables or secrets management:

- Database credentials
- API keys
- Encryption keys

Never commit secrets to version control.

### SSL/TLS

Enable SSL for production:

#### PostgreSQL SSL

```yaml
# docker-compose.prod.yml
postgres:
  environment:
    POSTGRES_SSL_MODE: require
```

#### API SSL

Use reverse proxy (nginx) with SSL:

```nginx
server {
    listen 443 ssl;
    server_name api.banking-analytics.com;

    ssl_certificate /etc/ssl/certs/api.crt;
    ssl_certificate_key /etc/ssl/private/api.key;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Firewall Rules

Restrict access:
- Database: Only accessible from application servers
- API: Restrict by IP or use authentication
- Streamlit: Use authentication in production

---

## Backup and Recovery

### Database Backup

#### Automated Backup

```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
BACKUP_DIR=/backups/postgres
docker-compose exec -T postgres pg_dump -U postgres banking_analytics > $BACKUP_DIR/backup_$DATE.sql

# Keep last 30 days
find $BACKUP_DIR -name "backup_*.sql" -mtime +30 -delete
```

#### Restore

```bash
docker-compose exec -T postgres psql -U postgres banking_analytics < backup_20260907.sql
```

### Application Backup

Backup configuration and code:
```bash
tar czf backup_$(date +%Y%m%d).tar.gz \
  config/ \
  src/ \
  api/ \
  streamlit/ \
  requirements.txt
```

---

## Scaling

### Horizontal Scaling

#### API Scaling

Increase replicas in Docker Compose:

```yaml
api:
  deploy:
    replicas: 3
```

Or in Kubernetes:

```yaml
replicas: 5
```

#### Database Scaling

- Read replicas for read-heavy workloads
- Connection pooling (PgBouncer)
- Database sharding for very large datasets

### Vertical Scaling

Increase resources:

```yaml
api:
  deploy:
    resources:
      limits:
        memory: 2Gi
        cpu: 2000m
```

---

## Troubleshooting

### Common Issues

**Service Won't Start**
```bash
# Check logs
docker-compose logs api

# Check environment variables
docker-compose config

# Restart service
docker-compose restart api
```

**Database Connection Failed**
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Test connection
docker-compose exec postgres pg_isready -U postgres

# Check credentials
docker-compose exec api env | grep DB_
```

**High Memory Usage**
```bash
# Check resource usage
docker stats

# Increase memory limits
# Edit docker-compose.prod.yml
```

---

## Rollback

### Docker Rollback

```bash
# Stop current version
docker-compose down

# Start previous version
docker-compose -f docker-compose.prod.yml up -d
```

### Database Rollback

```bash
# Restore from backup
docker-compose exec -T postgres psql -U postgres banking_analytics < backup_20260906.sql
```

---

## Performance Optimization

### Application Optimization

- Enable caching (Redis)
- Use connection pooling
- Optimize database queries
- Implement pagination
- Use async operations where appropriate

### Database Optimization

- Add indexes to frequently queried columns
- Partition large tables
- Use materialized views
- Optimize PostgreSQL configuration
- Regular vacuum and analyze

---

## Compliance

### Regulatory Considerations

- **GDPR**: Data privacy and right to be forgotten
- **CCPA**: California Consumer Privacy Act
- **PCI DSS**: Payment Card Industry compliance
- **SOX**: Sarbanes-Oxley Act for financial reporting

### Audit Logging

Enable audit logging for:
- Data access
- Configuration changes
- User actions
- API calls

---

## Support

For deployment issues, contact:
- Technical support: support@banking-analytics.com
- Documentation: docs/
- Issue tracking: GitHub Issues
