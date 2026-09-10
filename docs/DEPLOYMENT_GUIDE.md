# Deployment Guide

This guide provides comprehensive instructions for deploying the Banking Customer Profitability and Risk Analytics Platform to production environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [CI/CD Pipeline](#cicd-pipeline)
- [Monitoring and Observability](#monitoring-and-observability)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **CPU**: 4+ cores recommended
- **Memory**: 8GB+ RAM minimum, 16GB+ recommended
- **Storage**: 50GB+ available space
- **Network**: Stable internet connection for external dependencies

### Software Requirements

- Docker 20.10+
- Docker Compose 2.0+
- Kubernetes 1.24+ (for K8s deployment)
- kubectl 1.24+
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Kafka/Redpanda (for streaming)

### External Services

- Container registry (Docker Hub, ECR, GCR, etc.)
- PostgreSQL database (managed or self-hosted)
- Redis instance (managed or self-hosted)
- Kafka cluster (managed or self-hosted)
- Monitoring system (Prometheus, Grafana, CloudWatch, etc.)
- Log aggregation (ELK, CloudWatch Logs, etc.)

## Environment Setup

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Database Configuration
DB_HOST=your-db-host
DB_PORT=5432
DB_NAME=banking_analytics
DB_USER=banking_analytics_user
DB_PASSWORD=your-secure-password

# Redis Configuration
REDIS_HOST=your-redis-host
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password

# Kafka Configuration
KAFKA_BROKER=your-kafka-broker:9092
KAFKA_GROUP_ID=banking-analytics-production

# Security
JWT_SECRET_KEY=your-secure-jwt-secret-key-min-32-chars
ENVIRONMENT=production

# CORS
CORS_ORIGINS=https://your-frontend-domain.com

# Logging
LOG_LEVEL=INFO
```

### Secret Management

For production, use a proper secret management system:

- **Kubernetes Secrets**: Use Kubernetes secrets for sensitive data
- **AWS Secrets Manager**: For AWS deployments
- **Azure Key Vault**: For Azure deployments
- **HashiCorp Vault**: For on-premises deployments

## Docker Deployment

### Local Development

```bash
# Start all services
docker-compose up -d

# Start with streaming infrastructure
docker-compose -f docker-compose.yml -f docker-compose.streaming.yml up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Deployment

#### Build and Push Images

```bash
# Build image
docker build -t your-registry/banking-analytics:latest .

# Tag image
docker tag banking-analytics:latest your-registry/banking-analytics:v1.0.0

# Push to registry
docker push your-registry/banking-analytics:v1.0.0
```

#### Run with Docker Compose

```bash
# Copy production compose file
cp docker-compose.yml docker-compose.prod.yml

# Edit for production settings
# - Update image tags
# - Configure resource limits
# - Set environment variables
# - Configure volumes

# Start production services
docker-compose -f docker-compose.prod.yml up -d
```

#### Health Checks

```bash
# Check API health
curl http://localhost:8000/api/v1/health

# Check service status
docker-compose ps
```

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster configured
- kubectl configured
- Container registry access configured
- Namespace created

### Create Namespace

```bash
kubectl create namespace production
```

### Configure Secrets

```bash
# Create secret from file
kubectl create secret generic banking-analytics-secrets \
  --from-env-file=.env \
  --namespace=production

# Or create secret manually
kubectl apply -f k8s/production/secret.yaml
```

### Apply ConfigMap

```bash
kubectl apply -f k8s/production/configmap.yaml
```

### Deploy Application

```bash
# Apply deployment
kubectl apply -f k8s/production/deployment.yaml

# Apply service
kubectl apply -f k8s/production/service.yaml

# Check deployment status
kubectl rollout status deployment/banking-analytics -n production
```

### Scale Deployment

```bash
# Scale to 3 replicas
kubectl scale deployment banking-analytics --replicas=3 -n production

# Check pods
kubectl get pods -n production
```

### Update Deployment

```bash
# Update image
kubectl set image deployment/banking-analytics \
  banking-analytics=your-registry/banking-analytics:v1.1.0 \
  -n production

# Watch rollout
kubectl rollout status deployment/banking-analytics -n production
```

### Rollback

```bash
# Rollback to previous version
kubectl rollout undo deployment/banking-analytics -n production

# Rollback to specific revision
kubectl rollout undo deployment/banking-analytics --to-revision=2 -n production
```

## CI/CD Pipeline

### GitHub Actions

The project includes GitHub Actions workflows for CI/CD:

- **CI Pipeline** (`.github/workflows/ci.yml`): Runs on every push/PR
  - Code linting
  - Unit tests
  - Integration tests
  - Security scanning
  - Docker image build

- **CD Pipeline** (`.github/workflows/cd.yml`): Runs on main branch
  - Deploy to staging
  - Deploy to production (manual trigger)
  - Canary deployments
  - Rollback support

### Manual Deployment

```bash
# Trigger staging deployment
gh workflow run cd.yml -f environment=staging

# Trigger production deployment
gh workflow run cd.yml -f environment=production
```

### Pipeline Status

```bash
# List workflow runs
gh run list

# View specific run
gh run view <run-id>
```

## Monitoring and Observability

### Metrics Collection

The platform exposes metrics in Prometheus format:

```bash
# Access metrics endpoint
curl http://localhost:8000/metrics
```

### Logging

Logs are structured JSON for easy parsing:

```json
{
  "service": "streaming-pipeline",
  "timestamp": "2024-01-01T00:00:00Z",
  "level": "info",
  "message": "Event processed",
  "trace_id": "abc123",
  "context": {}
}
```

### Distributed Tracing

Trace IDs are included in logs for request tracking:

```python
# Trace context is automatically propagated
with observability.observe_operation("process_event"):
    # Your code here
```

### Health Checks

```bash
# API health check
curl http://localhost:8000/api/v1/health

# Streaming pipeline health check
curl http://localhost:8080/health
```

## Security Considerations

### Network Security

- Use TLS/SSL for all external connections
- Configure firewall rules to restrict access
- Use VPCs or private networks for internal services

### Authentication

- JWT tokens for API authentication
- Rotate JWT secrets regularly
- Use strong, randomly generated secrets

### Authorization

- Role-based access control (RBAC)
- Principle of least privilege
- Regular access reviews

### Data Encryption

- Encrypt data at rest (database, Redis)
- Encrypt data in transit (TLS)
- Use managed encryption services (KMS)

### Secrets Management

- Never commit secrets to version control
- Use environment-specific secrets
- Rotate secrets regularly
- Audit secret access

## Troubleshooting

### Common Issues

#### Database Connection Failed

```bash
# Check database connectivity
kubectl exec -it <pod-name> -n production -- python -c "
import psycopg2
conn = psycopg2.connect('host=postgres user=postgres password=password')
print('Connected')
"
```

#### Redis Connection Failed

```bash
# Check Redis connectivity
kubectl exec -it <pod-name> -n production -- redis-cli -h redis ping
```

#### Kafka Connection Failed

```bash
# Check Kafka connectivity
kubectl exec -it <pod-name> -n production -- rpk cluster health
```

#### Pod Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n production

# Check pod logs
kubectl logs <pod-name> -n production

# Check previous logs if crashed
kubectl logs <pod-name> -n production --previous
```

#### High Memory Usage

```bash
# Check resource usage
kubectl top pods -n production

# Check pod limits
kubectl describe pod <pod-name> -n production | grep -A 5 Limits
```

### Debug Mode

Enable debug logging:

```bash
# Set log level to DEBUG
kubectl set env deployment/banking-analytics LOG_LEVEL=DEBUG -n production
```

### Performance Issues

```bash
# Check resource quotas
kubectl describe namespace production

# Check node resources
kubectl top nodes
```

## Backup and Recovery

### Database Backup

```bash
# Backup PostgreSQL
kubectl exec postgres-0 -n production -- pg_dump banking_analytics > backup.sql

# Restore PostgreSQL
kubectl exec -i postgres-0 -n production -- psql banking_analytics < backup.sql
```

### Redis Backup

```bash
# Backup Redis
kubectl exec redis-0 -n production -- redis-cli SAVE

# Copy RDB file
kubectl cp redis-0:/data/dump.rdb ./redis-backup.rdb -n production
```

### Application State Backup

```bash
# Export Kubernetes resources
kubectl get all -n production -o yaml > backup.yaml
```

## Upgrade Procedure

### Pre-Upgrade Checklist

- [ ] Backup database
- [ ] Backup Redis
- [ ] Export Kubernetes resources
- [ ] Review release notes
- [ ] Test in staging environment

### Upgrade Steps

1. **Build new image**
   ```bash
   docker build -t banking-analytics:new-version .
   ```

2. **Test in staging**
   ```bash
   kubectl set image deployment/banking-analytics \
     banking-analytics=banking-analytics:new-version \
     -n staging
   ```

3. **Verify staging deployment**
   ```bash
   kubectl rollout status deployment/banking-analytics -n staging
   ```

4. **Deploy to production**
   ```bash
   kubectl set image deployment/banking-analytics \
     banking-analytics=banking-analytics:new-version \
     -n production
   ```

5. **Monitor production deployment**
   ```bash
   kubectl rollout status deployment/banking-analytics -n production
   ```

6. **Verify application health**
   ```bash
   curl https://api.banking-analytics.com/api/v1/health
   ```

### Rollback Procedure

If issues occur:

```bash
# Rollback deployment
kubectl rollout undo deployment/banking-analytics -n production

# Verify rollback
kubectl rollout status deployment/banking-analytics -n production
```

## Support

For deployment issues, contact:
- DevOps team: devops@company.com
- Platform team: platform@company.com
- On-call rotation: oncall@company.com
