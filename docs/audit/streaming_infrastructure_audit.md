# Streaming Infrastructure Audit

**Generated:** 2026-09-08
**Repository:** Banking Customer Profitability and Risk Analytics Platform

## Executive Summary

This audit examines the streaming infrastructure including Kafka/Redpanda, Redis, schema registry, topic configuration, consumer groups, and Docker deployment setup.

## Infrastructure Components

### Redpanda (Kafka-compatible Event Broker)

**Location:** `docker-compose.streaming.yml`

**Configuration:**
- Image: `vectorized/redpanda:v23.2.15`
- Kafka API Port: 9092
- Admin API Port: 9644
- Schema Registry Port: 8081
- Partitions: 6 (default)
- Replication: 1 (default)
- Auto-create topics: disabled
- Health check: `rpk cluster health`

**Assessment:** ✅ GOOD
- Appropriate version for production use
- Health check configured
- Auto-create topics disabled (good practice)
- Default partitions and replication configured
- Volume persistence configured

**Recommendations:**
- Consider increasing replication factor to 3 for production
- Add resource limits (CPU, memory) for production
- Consider adding monitoring endpoint exposure

---

### Redis (Feature Store and Caching)

**Location:** `docker-compose.streaming.yml`

**Configuration:**
- Image: `redis:7-alpine`
- Port: 6379
- Persistence: AOF enabled
- AOF fsync: everysec
- Max memory: 256mb (configurable)
- Eviction policy: allkeys-lru
- Save intervals: 900/1, 300/10, 60/10000
- Health check: `redis-cli ping`

**Assessment:** ⚠️ NEEDS REVIEW
- AOF persistence configured correctly
- LRU eviction policy appropriate for feature store
- Max memory of 256mb may be insufficient for production
- Save intervals are reasonable
- Health check configured

**Issues:**

### INFRA-001 Low Redis Memory Limit

**Problem:** Default Redis memory limit of 256mb is too low for production feature store.

**Impact:** Redis may evict features prematurely, causing cache misses and degraded performance.

**Recommendation:** Increase to at least 2GB for production, make configurable per environment.

**Severity:** MEDIUM

---

### INFRA-002 Missing Redis Authentication

**Problem:** Redis is configured without password authentication in Docker.

**Evidence:**
- `docker-compose.streaming.yml` no password environment variable
- `config/base.yaml` password is null
- `config/environments/development.yaml` password is null

**Impact:** Security vulnerability - unauthorized access to feature store.

**Recommendation:** Enable Redis authentication with strong password in production.

**Severity:** HIGH

---

### INFRA-003 Missing Redis SSL/TLS

**Problem:** No SSL/TLS configuration for Redis connections.

**Impact:** Data in transit is unencrypted.

**Recommendation:** Enable SSL/TLS for Redis in production environments.

**Severity:** MEDIUM

---

### Schema Registry

**Configuration:**
- URL: http://localhost:8081
- Enabled: true
- Compatibility level: backward (from streaming.yaml)

**Assessment:** ⚠️ PARTIAL
- Schema registry is configured in Redpanda
- Compatibility level defined in streaming.yaml
- No actual schema validation implementation found in code

**Issues:**

### INFRA-004 Schema Registry Not Used

**Problem:** Schema registry is configured but not actually used by serialization layer.

**Evidence:**
- `src/streaming/kafka/serialization.py` uses JSON serialization only
- No Avro or Protobuf schema integration
- No schema validation in MessageDeserializer

**Impact:** No schema enforcement, potential data quality issues.

**Recommendation:** Implement Avro/Protobuf schema validation or remove schema registry dependency.

**Severity:** LOW

---

## Topic Configuration

**Location:** `config/streaming.yaml`

**Topics Defined:**

| Topic Name | Partitions | Replication | Retention | Purpose |
|------------|------------|-------------|-----------|---------|
| banking.events.raw | 12 | 1 | 7 days | Raw banking events |
| banking.events.validated | 12 | 1 | 7 days | Validated events |
| banking.features.customer | 6 | 1 | 2 days | Customer features |
| banking.features.account | 6 | 1 | 2 days | Account features |
| banking.predictions.risk | 3 | 1 | 30 days | Risk predictions |
| banking.predictions.churn | 3 | 1 | 30 days | Churn predictions |
| banking.anomalies.fraud | 3 | 1 | 2 years | Fraud anomalies |
| banking.alerts.risk | 3 | 1 | 90 days | Risk alerts |
| banking.dlq | 1 | 1 | 30 days | Dead-letter queue |
| banking.replay.input | 6 | 1 | 7 days | Replay input |
| banking.replay.output | 6 | 1 | 7 days | Replay output |

**Assessment:** ✅ GOOD
- Logical topic naming convention
- Appropriate partition counts based on expected throughput
- Retention periods aligned with data importance
- Compression enabled (snappy)
- DLQ configured

**Issues:**

### INFRA-005 Low Replication Factor

**Problem:** All topics have replication factor of 1.

**Impact:** No fault tolerance - broker failure causes data loss.

**Recommendation:** Increase to 3 for production environments.

**Severity:** HIGH

---

### INFRA-006 Missing Topic Creation

**Problem:** No code found to automatically create topics on startup.

**Evidence:**
- No topic creation logic in streaming initialization
- Redpanda auto-create is disabled
- Manual topic creation required

**Impact:** System will fail if topics don't exist.

**Recommendation:** Add topic creation script or enable auto-create for development.

**Severity:** HIGH

---

## Consumer Group Configuration

**Location:** `config/streaming.yaml`

**Consumer Groups Defined:**

| Group Name | Topics | Auto Offset Reset | Auto Commit | Purpose |
|------------|--------|-------------------|-------------|---------|
| banking.feature.processor | banking.events.raw | earliest | false | Feature computation |
| banking.prediction.processor | banking.features.customer, banking.features.account | latest | false | ML predictions |
| banking.anomaly.processor | banking.events.validated, banking.features.customer | latest | false | Anomaly detection |
| banking.alert.processor | banking.predictions.risk, banking.predictions.churn, banking.anomalies.fraud | latest | false | Alert generation |
| banking.replay.processor | banking.replay.input | earliest | false | Historical replay |

**Assessment:** ✅ GOOD
- Logical consumer group naming
- Appropriate offset reset strategies
- Manual offset commit configured (correct for exactly-once semantics)
- Reasonable session and heartbeat timeouts

**Issues:** None identified

---

## Event Type Configuration

**Location:** `config/streaming.yaml`

**Event Types Defined:**
- transaction
- account_update
- customer_update
- loan_application
- payment

**Assessment:** ✅ GOOD
- Event types mapped to topics
- Schema version tracking configured
- Validation required flag set

**Issues:** None identified

---

## Docker Configuration

### Docker Compose Structure

**Files:**
- `docker-compose.yml` - Core services (Postgres, API, Streamlit, Pipeline)
- `docker-compose.streaming.yml` - Streaming infrastructure (Redpanda, Redis)
- `docker-compose.dev.yml` - Development overrides

**Assessment:** ✅ GOOD
- Modular compose file structure
- Separation of concerns (core vs streaming)
- Health checks configured for all services
- Volume persistence for data
- Network isolation with banking_network

**Issues:**

### INFRA-007 Missing Streaming Service

**Problem:** No streaming orchestrator service defined in Docker compose.

**Evidence:**
- `docker-compose.yml` has api, streamlit, pipeline services
- `docker-compose.streaming.yml` has redpanda, redis only
- No service to run the streaming pipeline

**Impact:** Streaming pipeline must be run manually outside Docker.

**Recommendation:** Add streaming orchestrator service to docker-compose.streaming.yml.

**Severity:** MEDIUM

---

### INFRA-008 Missing Environment File

**Problem:** No .env file found for configuration.

**Evidence:**
- Docker compose uses environment variables (${VAR:-default})
- No .env file in repository
- Hard to manage different environments

**Impact:** Configuration management is manual and error-prone.

**Recommendation:** Add .env.example and .env files for different environments.

**Severity:** LOW

---

### INFRA-009 Missing Resource Limits

**Problem:** No CPU or memory limits defined for any services.

**Impact:** Services can consume unlimited resources, potentially causing system instability.

**Recommendation:** Add resource limits to all services for production.

**Severity:** MEDIUM

---

## Configuration Management

### Configuration Files

**Files:**
- `config/base.yaml` - Base configuration
- `config/streaming.yaml` - Streaming-specific configuration
- `config/replay.yaml` - Replay configuration
- `config/logging.yaml` - Logging configuration
- `config/environments/development.yaml` - Development overrides
- Missing: `config/environments/production.yaml`

**Assessment:** ⚠️ INCOMPLETE
- Good separation of concerns
- Environment-specific overrides
- Missing production configuration

**Issues:**

### INFRA-010 Missing Production Configuration

**Problem:** No production environment configuration file.

**Impact:** No production-specific settings (higher resource limits, security settings, etc.).

**Recommendation:** Add `config/environments/production.yaml` with production settings.

**Severity:** MEDIUM

---

## Network Configuration

**Network:** banking_network (bridge driver)

**Assessment:** ✅ GOOD
- Services isolated on dedicated network
- Bridge driver appropriate for single-host deployment
- All services on same network for inter-service communication

**Issues:** None identified

---

## Volume Configuration

**Volumes:**
- `postgres_data` - PostgreSQL data
- `redpanda_data` - Redpanda data
- `redis_data` - Redis data

**Assessment:** ✅ GOOD
- All stateful services have persistent volumes
- Named volumes for easy backup/restore
- Appropriate for single-host deployment

**Issues:** None identified

---

## Health Checks

**Services with Health Checks:**
- PostgreSQL: `pg_isready`
- API: HTTP health endpoint
- Streamlit: HTTP check
- Redpanda: `rpk cluster health`
- Redis: `redis-cli ping`

**Assessment:** ✅ EXCELLENT
- All services have health checks
- Appropriate intervals and timeouts
- Retry logic configured
- Start periods configured

**Issues:** None identified

---

## Dependency Management

**Service Dependencies:**
- API depends on postgres (healthy)
- Streamlit depends on postgres (healthy) and api (healthy)
- Pipeline depends on postgres (healthy)
- No streaming service dependencies defined

**Assessment:** ⚠️ INCOMPLETE
- Core services have proper dependencies
- Streaming services have no dependency management
- No wait-for scripts for Redpanda/Redis readiness

**Issues:**

### INFRA-011 Missing Streaming Service Dependencies

**Problem:** If streaming service is added, it lacks dependency definitions.

**Recommendation:** Add streaming service with dependencies on redpanda and redis.

**Severity:** LOW

---

## Security Assessment

### Authentication

**PostgreSQL:** Trust authentication (development only)
**Redis:** No authentication
**Redpanda:** No authentication configured
**API:** No authentication middleware found

**Assessment:** ❌ INSECURE
- No authentication for any service
- Trust authentication for Postgres is insecure
- No encryption for inter-service communication

**Issues:**

### INFRA-012 No Authentication Configured

**Problem:** No authentication configured for any service.

**Impact:** Unauthorized access to all services.

**Recommendation:** Implement authentication for all services in production.

**Severity:** CRITICAL

---

### INFRA-013 No SSL/TLS

**Problem:** No SSL/TLS configured for any service.

**Impact:** All data in transit is unencrypted.

**Recommendation:** Enable SSL/TLS for all services in production.

**Severity:** HIGH

---

## Monitoring and Observability

**Current State:**
- Health checks configured
- No metrics endpoints exposed
- No logging aggregation
- No distributed tracing

**Assessment:** ❌ INSUFFICIENT
- Basic health checks only
- No metrics collection
- No centralized logging
- No tracing

**Issues:**

### INFRA-014 No Metrics Collection

**Problem:** No Prometheus or other metrics collection configured.

**Impact:** No visibility into system performance.

**Recommendation:** Add Prometheus exporter and Grafana for monitoring.

**Severity:** MEDIUM

---

### INFRA-015 No Centralized Logging

**Problem:** No centralized logging configured.

**Impact:** Difficult to debug issues across services.

**Recommendation:** Add ELK stack or similar for log aggregation.

**Severity:** MEDIUM

---

## Backup and Recovery

**Current State:**
- Volume persistence configured
- No backup strategy
- No disaster recovery plan

**Assessment:** ❌ INSUFFICIENT
- Data persists locally only
- No automated backups
- No recovery procedures

**Issues:**

### INFRA-016 No Backup Strategy

**Problem:** No automated backup configuration.

**Impact:** Data loss risk from disk failure or corruption.

**Recommendation:** Implement automated backup strategy with off-site storage.

**Severity:** HIGH

---

## Summary

**Total Issues Found:** 16
- CRITICAL: 1
- HIGH: 4
- MEDIUM: 7
- LOW: 4

**Overall Assessment:** The streaming infrastructure has a solid foundation with good Docker Compose structure, health checks, and topic configuration. However, critical security issues (no authentication) and production readiness gaps (backup strategy, monitoring, resource limits) must be addressed before production deployment.

## Recommendations

### Immediate Actions (P0)

1. Add authentication to all services (INFRA-012)
2. Increase replication factor to 3 for production (INFRA-005)
3. Add topic creation logic (INFRA-006)

### Short-term Actions (P1)

4. Enable SSL/TLS for all services (INFRA-013)
5. Implement backup strategy (INFRA-016)
6. Add streaming service to Docker compose (INFRA-007)
7. Increase Redis memory limit (INFRA-001)

### Medium-term Actions (P2)

8. Add resource limits to all services (INFRA-009)
9. Add production configuration file (INFRA-010)
10. Add metrics collection (INFRA-014)
11. Add centralized logging (INFRA-015)

### Long-term Actions (P3)

12. Enable Redis authentication (INFRA-002)
13. Enable Redis SSL/TLS (INFRA-003)
14. Implement schema registry validation or remove dependency (INFRA-004)
15. Add environment file management (INFRA-008)
16. Add streaming service dependencies (INFRA-011)
