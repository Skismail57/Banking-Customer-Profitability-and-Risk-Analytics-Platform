# Security Architecture

**Project:** Banking Customer Profitability and Risk Analytics Platform  
**Date:** 2025-01-09  
**Purpose:** Define security architecture for production deployment

---

## Architecture Overview

The security architecture wraps the existing batch + streaming intelligence platform with production-grade security controls without replacing the core analytics functionality.

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                              │
│  (Web UI, API Clients, Streamlit Dashboard, WebSocket Clients) │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ↓ HTTPS/TLS
┌─────────────────────────────────────────────────────────────────┐
│                    Authentication Layer                          │
│  (JWT Token Validation, OAuth2, Token Lifecycle Management)     │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Authorization Layer                           │
│  (RBAC, Permission Checks, Role-Based Access Control)           │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                    API Middleware Layer                           │
│  (Security Headers, Rate Limiting, Input Validation, CORS)      │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                  Application Services Layer                       │
│  (REST API, WebSocket, Batch Analytics, Streaming Pipeline)     │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ↓ TLS/SSL
┌─────────────────────────────────────────────────────────────────┐
│                    Data Storage Layer                            │
│  (PostgreSQL, Redis, Redpanda/Kafka)                            │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Audit Trail Layer                             │
│  (Security Events, Decision Audit, Access Logs)                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Security Boundaries

### Boundary 1: External to Application
- **Protection:** TLS/SSL encryption, authentication, rate limiting
- **Assets:** API endpoints, WebSocket endpoints
- **Threats:** Unauthorized access, DoS, MITM attacks

### Boundary 2: Application to Database
- **Protection:** TLS/SSL, connection pooling, parameterized queries
- **Assets:** PostgreSQL database
- **Threats:** SQL injection, data exfiltration, unauthorized access

### Boundary 3: Application to Redis
- **Protection:** Redis AUTH, TLS where available
- **Assets:** Redis feature store
- **Threats:** Unauthorized access, data exfiltration

### Boundary 4: Application to Broker
- **Protection:** SASL authentication, TLS encryption
- **Assets:** Redpanda/Kafka topics
- **Threats:** Unauthorized access, data tampering

### Boundary 5: Service to Service
- **Protection:** Service tokens, mutual TLS (future)
- **Assets:** Internal service communication
- **Threats:** Lateral movement, unauthorized service access

---

## Authentication

### Authentication Strategy: JWT (JSON Web Tokens)

**Rationale:**
- Stateless authentication suitable for microservices
- Compatible with FastAPI ecosystem
- Supports token expiration and refresh
- No session management overhead
- Works well with WebSocket connections

### Token Lifecycle

```
Login → Token Issuance (Access Token + Refresh Token) →
Token Validation → Token Refresh → Token Expiration → Re-authentication
```

### Token Specifications

**Access Token:**
- **Algorithm:** RS256 (asymmetric) or HS256 (symmetric for development)
- **Expiration:** 15 minutes (short-lived)
- **Claims:** 
  - `sub`: User ID
  - `roles`: User roles
  - `permissions`: User permissions
  - `iat`: Issued at
  - `exp`: Expiration
  - `jti`: Token ID (for revocation)
  - `iss`: Issuer

**Refresh Token:**
- **Expiration:** 7 days
- **Storage:** HTTP-only secure cookie (web) or secure storage (API clients)
- **Rotation:** On every refresh

### Authentication Flow

```
1. Client sends credentials (username/password or API key)
2. Server validates credentials
3. Server issues JWT access token and refresh token
4. Client includes access token in Authorization header
5. Server validates token on each request
6. When access token expires, client uses refresh token
7. Server issues new access token
```

### Token Validation

- **Signature verification** using secret or public key
- **Expiration check** (exp claim)
- **Issuer validation** (iss claim)
- **Token revocation check** (using jti in Redis blacklist)
- **Algorithm check** (prevent alg=none attacks)

### Password Handling (if local authentication)

- **Hashing:** bcrypt with cost factor 12
- **Salt:** Automatically generated by bcrypt
- **Storage:** Only hashed passwords stored
- **Validation:** Constant-time comparison

---

## Authorization / RBAC

### Role-Based Access Control (RBAC)

**Roles:**

| Role | Description | Permissions |
|------|-------------|-------------|
| ADMIN | Full system access | All permissions |
| ANALYST | Analytics access | read analytics, execute analytics |
| RISK_MANAGER | Risk management access | read risk scores, execute risk analysis |
| AUDITOR | Read-only audit access | read audit events, export audit events |
| SERVICE | Service account | Service-to-service access |

### Permission Matrix

| Resource | ADMIN | ANALYST | RISK_MANAGER | AUDITOR | SERVICE |
|----------|-------|---------|-------------|---------|---------|
| Analytics (read) | ✓ | ✓ | ✓ | ✓ | ✓ |
| Analytics (execute) | ✓ | ✓ | ✓ | ✗ | ✓ |
| Customers (read) | ✓ | ✓ | ✓ | ✓ | ✓ |
| Customers (modify) | ✓ | ✗ | ✗ | ✗ | ✓ |
| Risk (read) | ✓ | ✓ | ✓ | ✓ | ✓ |
| Risk (execute) | ✓ | ✗ | ✓ | ✗ | ✓ |
| Models (view) | ✓ | ✓ | ✓ | ✓ | ✓ |
| Models (register) | ✓ | ✗ | ✗ | ✗ | ✓ |
| Models (activate) | ✓ | ✗ | ✗ | ✗ | ✓ |
| Models (retire) | ✓ | ✗ | ✗ | ✗ | ✓ |
| Alerts (view) | ✓ | ✓ | ✓ | ✓ | ✓ |
| Alerts (acknowledge) | ✓ | ✓ | ✓ | ✗ | ✓ |
| Alerts (resolve) | ✓ | ✓ | ✓ | ✗ | ✓ |
| Audit (read) | ✓ | ✗ | ✗ | ✓ | ✓ |
| Audit (export) | ✓ | ✗ | ✗ | ✓ | ✓ |
| Users (manage) | ✓ | ✗ | ✗ | ✗ | ✗ |
| Roles (manage) | ✓ | ✗ | ✗ | ✗ | ✗ |
| Configuration (manage) | ✓ | ✗ | ✗ | ✗ | ✗ |

### Authorization Enforcement

- **API Level:** FastAPI dependencies for route protection
- **WebSocket Level:** Token validation on connection
- **Service Level:** Permission checks in business logic
- **Database Level:** Row-level security (future enhancement)

### Permission Check Flow

```
1. Extract user roles from JWT token
2. Load user permissions based on roles
3. Check if required permission is in user's permission set
4. Allow or deny access based on permission check
5. Log authorization decision
```

---

## Service-to-Service Authentication

### Strategy: API Keys / Service Tokens

**Rationale:**
- Simpler than mutual TLS for initial implementation
- Compatible with existing architecture
- Can be upgraded to mutual TLS in future

### Service Token Format

- **Format:** Bearer token (similar to JWT but simpler)
- **Storage:** Environment variables (development), secrets manager (production)
- **Validation:** Token lookup in Redis or database

### Service Accounts

| Service | Token Purpose |
|---------|--------------|
| streaming-orchestrator | Kafka consumer access |
| feature-store | Redis write access |
| alert-engine | Alert generation access |
| model-registry | Model lifecycle access |

---

## Secrets Management

### Current State: Environment Variables

### Target State: Environment Variables + Secrets Manager (Phase 1)

**Phase 1 Approach:**
- Continue using environment variables for simplicity
- Add validation and fail-fast for missing secrets
- Add secrets redaction in logs
- Document secrets manager integration for future phase

### Secrets Categories

| Category | Examples | Storage |
|----------|----------|---------|
| Database | DB_PASSWORD, DB_URL | Environment variable |
| Redis | REDIS_PASSWORD | Environment variable |
| Kafka | KAFKA_SASL_PASSWORD | Environment variable |
| API | JWT_SECRET, API_KEYS | Environment variable |
| Encryption | ENCRYPTION_KEY | Environment variable |
| External | SCHEMA_REGISTRY_API_SECRET | Environment variable |

### Secrets Validation

- **Startup Validation:** Fail-fast if required secrets missing in production
- **Environment Validation:** Validate environment type (dev/test/prod)
- **Secret Format Validation:** Validate secret strength where applicable

### Secrets Redaction

- **Log Redaction:** Automatically redact secrets from logs
- **Error Redaction:** Redact secrets from error messages
- **API Response Redaction:** Never return secrets in API responses

---

## Encryption

### In Transit Encryption

**HTTPS/TLS:**
- **API:** TLS 1.2+ required for production
- **WebSocket:** WSS (WebSocket Secure) required for production
- **Development:** HTTP allowed with warning
- **Certificates:** Let's Encrypt or corporate CA

**Database TLS:**
- **PostgreSQL:** SSL mode `require` for production
- **Connection String:** `postgresql://user:pass@host:port/db?sslmode=require`
- **Certificate Validation:** Full certificate validation in production

**Redis TLS:**
- **Redis:** SSL/TLS where supported by deployment
- **Configuration:** `ssl: true` in production config
- **Certificate Validation:** Full certificate validation

**Broker TLS:**
- **Redpanda/Kafka:** TLS encryption for production
- **Configuration:** `security_protocol: SSL` or `SASL_SSL`
- **Certificate Validation:** Full certificate validation

### At Rest Encryption

**Strategy:** Rely on infrastructure encryption

**Rationale:**
- Application-level encryption adds complexity
- Infrastructure encryption (disk encryption, managed database encryption) is sufficient
- Focus on access control rather than encryption

**Implementation:**
- **PostgreSQL:** Use managed database encryption (AWS RDS, etc.)
- **Redis:** Use Redis Enterprise or managed Redis with encryption
- **File Storage:** Encrypt sensitive files if any (not applicable currently)

### Data Classification

| Classification | Example | Encryption Required |
|---------------|---------|---------------------|
| PUBLIC | API documentation, public metrics | No |
| INTERNAL | System metrics, operational data | No |
| CONFIDENTIAL | Customer data, risk scores, financial metrics | In transit only |
| SENSITIVE | Authentication tokens, secrets, encryption keys | In transit + at rest |

---

## TLS Configuration

### API TLS Configuration

**Development:**
```yaml
# No TLS for development
# Warning logged on startup
```

**Production:**
```yaml
# TLS 1.2+ required
# Certificate validation enabled
# HSTS enabled
```

### Database TLS Configuration

**Development:**
```python
# SSL mode: prefer (allow non-SSL)
sslmode="prefer"
```

**Production:**
```python
# SSL mode: require (enforce SSL)
sslmode="require"
sslcert="/path/to/client-cert.pem"
sslkey="/path/to/client-key.pem"
sslrootcert="/path/to/ca-cert.pem"
```

### Redis TLS Configuration

**Development:**
```yaml
# No TLS for development
redis:
  ssl: false
```

**Production:**
```yaml
# TLS enabled
redis:
  ssl: true
  ssl_cert_reqs: required
```

### Broker TLS Configuration

**Development:**
```yaml
# No TLS for development
security_protocol: PLAINTEXT
```

**Production:**
```yaml
# TLS enabled
security_protocol: SSL
# or SASL_SSL for authentication + encryption
```

---

## Database Security

### Connection Security

- **Connection Pooling:** SQLAlchemy with pool_pre_ping
- **SSL Mode:** `require` for production
- **Credential Storage:** Environment variables
- **Connection String:** Never logged, constructed securely

### Query Security

- **ORM Usage:** SQLAlchemy ORM for all queries (no raw SQL)
- **Parameterization:** Automatic parameter binding via ORM
- **SQL Injection Prevention:** ORM provides protection
- **Query Validation:** Pydantic schemas for input validation

### Database User Privileges

**Development:**
- Single user with full privileges (simpler setup)

**Production:**
- Application user with limited privileges (SELECT, INSERT, UPDATE on specific tables)
- Separate admin user for migrations
- Least privilege principle

---

## Redis Security

### Authentication

**Development:**
```yaml
# No password for development
redis:
  password: null
```

**Production:**
```yaml
# Password required
redis:
  password: ${REDIS_PASSWORD}
```

### TLS Configuration

**Development:**
```yaml
# No TLS for development
redis:
  ssl: false
```

**Production:**
```yaml
# TLS enabled where supported
redis:
  ssl: ${REDIS_SSL:-true}
```

### Sensitive Data Handling

- **Feature Store:** Customer features stored in Redis
- **Classification:** CONFIDENTIAL (in transit encryption required)
- **Access Control:** Redis AUTH + network isolation
- **Logging:** Redact sensitive feature values from logs

---

## Broker Security (Redpanda/Kafka)

### Authentication

**Development:**
```yaml
# No authentication for development
security_protocol: PLAINTEXT
```

**Production:**
```yaml
# SASL authentication
security_protocol: SASL_SSL
sasl_mechanism: PLAIN
sasl_username: ${KAFKA_SASL_USERNAME}
sasl_password: ${KAFKA_SASL_PASSWORD}
```

### Authorization

**Topic Permissions:**
- **Feature Processor:** Read from raw topics, write to feature topics
- **Prediction Processor:** Read from feature topics, write to prediction topics
- **Alert Processor:** Read from prediction/anomaly topics, write to alert topics
- **Replay Processor:** Read from replay topics, write to replay output

### TLS Configuration

**Development:**
```yaml
# No TLS for development
security_protocol: PLAINTEXT
```

**Production:**
```yaml
# TLS encryption
security_protocol: SSL
# or SASL_SSL for authentication + encryption
```

### Sensitive Data Handling

- **Event Data:** Customer transaction data in events
- **Classification:** CONFIDENTIAL (in transit encryption required)
- **Access Control:** SASL authentication + topic ACLs
- **Logging:** Redact sensitive event data from logs

---

## Audit Logging

### Security Events to Log

| Event Type | Description | Context |
|------------|-------------|---------|
| LOGIN_SUCCESS | Successful login | user_id, ip_address, timestamp |
| LOGIN_FAILURE | Failed login attempt | username, ip_address, reason, timestamp |
| TOKEN_REFRESH | Token refresh | user_id, old_jti, new_jti, timestamp |
| LOGOUT | User logout | user_id, timestamp |
| ACCESS_DENIED | Authorization denied | user_id, resource, action, reason, timestamp |
| ROLE_CHANGE | Role modification | admin_id, target_user_id, old_role, new_role, timestamp |
| USER_CREATED | User creation | admin_id, new_user_id, timestamp |
| USER_DISABLED | User disabled | admin_id, target_user_id, reason, timestamp |
| MODEL_ACTIVATED | Model activation | user_id, model_id, model_version, timestamp |
| MODEL_RETIRED | Model retirement | user_id, model_id, model_version, timestamp |
| CONFIG_CHANGED | Configuration change | user_id, config_key, timestamp |
| SECURITY_CONFIGURATION_CHANGED | Security config change | user_id, config_key, timestamp |

### Audit Record Structure

```python
{
    "event_id": str,
    "timestamp": datetime,
    "event_type": str,
    "actor": str,  # user_id or service_id
    "role": str,
    "resource": str,
    "action": str,
    "result": str,  # success/failure
    "correlation_id": str,
    "source": str,  # ip_address or service_name
    "reason": str,  # optional
    "context": dict  # additional context
}
```

### Audit Trail Storage

- **Short-term:** Redis for immediate access (7 days)
- **Long-term:** PostgreSQL for compliance (7 years)
- **Tamper Resistance:** Append-only table, no updates/deletes

### Integration with Existing Decision Audit Trail

- **Extend:** Add security event types to existing `DecisionAuditor`
- **Separate:** Keep security events separate from decision events
- **Unified:** Provide unified query interface for both types

---

## Security Headers

### HTTP Security Headers

| Header | Value | Purpose |
|--------|-------|---------|
| Strict-Transport-Security | max-age=31536000; includeSubDomains | Enforce HTTPS |
| X-Content-Type-Options | nosniff | Prevent MIME sniffing |
| X-Frame-Options | DENY | Prevent clickjacking |
| Content-Security-Policy | default-src 'self' | Prevent XSS |
| Referrer-Policy | strict-origin-when-cross-origin | Control referrer info |
| Permissions-Policy | geolocation=(), microphone=() | Disable browser features |

### CSP Policy

**Development:**
```python
# Relaxed CSP for development
Content-Security-Policy: default-src 'self' 'unsafe-inline' 'unsafe-eval'
```

**Production:**
```python
# Strict CSP for production
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self'
```

### WebSocket Compatibility

- **CSP:** Allow WebSocket connections from trusted origins
- **Frame Options:** May need SAMEORIGIN for WebSocket if embedded
- **Testing:** Verify headers don't break WebSocket functionality

---

## Rate Limiting

### Rate Limiting Strategy

**Implementation:** SlowAPI or custom rate limiter

**Storage:** Redis for distributed rate limiting

**Scope:**
- Per-IP rate limiting (anonymous requests)
- Per-user rate limiting (authenticated requests)
- Per-endpoint rate limiting (expensive operations)

### Rate Limits by Endpoint

| Endpoint | Limit | Window | Scope |
|----------|-------|--------|-------|
| /auth/login | 5 requests | 1 minute | per-IP |
| /auth/refresh | 10 requests | 1 minute | per-user |
| /api/v1/analytics/* | 100 requests | 1 minute | per-user |
| /api/v1/models/activate | 10 requests | 1 hour | per-user |
| /api/v1/replay/* | 5 requests | 1 hour | per-user |
| WebSocket connect | 10 connections | 1 minute | per-IP |

### Rate Limit Response

```python
HTTP 429 Too Many Requests
{
    "detail": "Rate limit exceeded",
    "retry_after": 60
}
```

---

## Input Validation

### Validation Strategy

**Layers:**
1. **Pydantic Schemas:** Type validation and constraints
2. **Custom Validators:** Business logic validation
3. **Sanitization:** Input sanitization where needed

### Validation Categories

| Category | Validation | Sanitization |
|----------|------------|--------------|
| String input | Length, format, allowed characters | HTML encoding |
| Numeric input | Range, type | Integer/float conversion |
| Date input | Format, range | Date parsing |
| JSON input | Schema validation | JSON parsing |
| File input | Size, type | Virus scanning (future) |

### SQL Injection Prevention

- **ORM Only:** Use SQLAlchemy ORM exclusively
- **No Raw SQL:** Avoid raw SQL queries
- **Parameter Binding:** Automatic via ORM
- **Validation:** Pydantic schemas before database operations

### XSS Prevention

- **Output Encoding:** Automatic in FastAPI
- **CSP:** Content-Security-Policy header
- **Input Sanitization:** HTML encoding for user input

---

## Error Handling

### Secure Error Handling Principles

**Never Expose:**
- Stack traces
- Database errors
- Internal paths
- Secret values
- Authentication implementation details
- Detailed error messages for security failures

**Always Return:**
- Generic error messages for security failures
- HTTP status codes appropriate for error type
- Correlation ID for debugging
- Safe error details in logs (not exposed to client)

### Error Response Format

```python
# Security errors (401, 403)
{
    "detail": "Authentication failed",
    "correlation_id": "abc123"
}

# Validation errors (422)
{
    "detail": [
        {
            "loc": ["body", "email"],
            "msg": "field required",
            "type": "value_error.missing"
        }
    ],
    "correlation_id": "abc123"
}

# Server errors (500)
{
    "detail": "Internal server error",
    "correlation_id": "abc123"
}
```

### Exception Handling

- **Authentication Errors:** Return 401, log details
- **Authorization Errors:** Return 403, log details
- **Validation Errors:** Return 422 with details
- **Database Errors:** Return 500, log details (not exposed)
- **System Errors:** Return 500, log details (not exposed)

---

## Security Monitoring

### Metrics to Track

| Metric | Type | Purpose |
|--------|------|---------|
| auth_login_success | Counter | Successful logins |
| auth_login_failure | Counter | Failed login attempts |
| auth_token_refresh | Counter | Token refreshes |
| auth_access_denied | Counter | Authorization denials |
| rate_limit_exceeded | Counter | Rate limit violations |
| security_event_total | Counter | Total security events |

### Alerting Thresholds

| Metric | Threshold | Action |
|--------|-----------|--------|
| auth_login_failure | > 10 per minute per IP | Alert, possible block |
| auth_access_denied | > 100 per minute per user | Alert, investigate |
| rate_limit_exceeded | > 1000 per minute | Alert, possible DDoS |

---

## Security Testing

### Test Categories

1. **Authentication Tests:** Valid/invalid credentials, expired tokens, malformed tokens
2. **Authorization Tests:** Permitted/denied roles, cross-user access, admin operations
3. **API Security Tests:** Unauthenticated access, authorization bypass, input validation
4. **WebSocket Security Tests:** Unauthorized connection, invalid token, message validation
5. **Secrets Tests:** Secrets not logged, configuration validation
6. **SQL Injection Tests:** Injection attempts, parameterization verification
7. **Rate Limit Tests:** Repeated requests, protected endpoints

### Security Tools

- **Static Analysis:** Bandit for Python security issues
- **Dependency Scanning:** pip-audit for vulnerable dependencies
- **Secret Scanning:** git-secrets or similar (future)

---

## Implementation Phases

### Phase 1 (Current): Foundation
- JWT authentication
- RBAC authorization
- Secrets validation
- Security headers
- Basic rate limiting
- Security event logging
- Error handling security

### Phase 2 (Future): Enhanced Security
- Secrets manager integration
- Mutual TLS for service-to-service
- Row-level security in database
- Advanced rate limiting
- Security monitoring and alerting

### Phase 3 (Future): Advanced Security
- Hardware security modules (HSM)
- Key management service (KMS)
- Advanced threat detection
- Security information and event management (SIEM)

---

## Architecture Impact

### Integration with Existing Architecture

**Batch Analytics:**
- No changes required
- Security wraps batch pipeline
- Batch jobs use service tokens

**Streaming Pipeline:**
- No changes to streaming logic
- Service tokens for Kafka/Redis access
- Security events logged to audit trail

**Feature Store:**
- Redis authentication added
- TLS where supported
- No changes to feature logic

**API Layer:**
- Authentication middleware added
- Authorization dependencies added
- Security headers added
- Rate limiting added

**WebSocket:**
- Token validation on connection
- Authorization checks on subscription
- No changes to message handling

---

## Security Principles

1. **Defense in Depth:** Multiple layers of security
2. **Least Privilege:** Minimum required access
3. **Fail Securely:** Default deny, not default allow
4. **Secure by Default:** Security enabled by default
5. **Transparency:** Security decisions auditable
6. **Simplicity:** Avoid unnecessary complexity
7. **Verification:** All security controls tested
8. **Monitoring:** Security events logged and monitored

---

**Document Status:** Complete  
**Next Step:** STEP 3 - Configuration & Secrets Foundation
