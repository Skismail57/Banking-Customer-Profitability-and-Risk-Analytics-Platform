# Security Guide

This guide provides comprehensive information about the security features and best practices for the Banking Customer Profitability & Risk Analytics Platform.

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Authorization](#authorization)
4. [API Security](#api-security)
5. [WebSocket Security](#websocket-security)
6. [Database Security](#database-security)
7. [Redis Security](#redis-security)
8. [Kafka Security](#kafka-security)
9. [Security Headers](#security-headers)
10. [Rate Limiting](#rate-limiting)
11. [Audit Logging](#audit-logging)
12. [Error Handling](#error-handling)
13. [Docker Security](#docker-security)
14. [Dependency Security](#dependency-security)
15. [Security Testing](#security-testing)

## Overview

The platform implements a layered security architecture following defense-in-depth principles. All security controls are designed to be backward compatible with existing functionality while providing production-grade security.

### Security Principles

- **Defense in Depth**: Multiple layers of security controls
- **Least Privilege**: Users and services have minimum required permissions
- **Secure by Default**: Production-ready security configurations
- **Audit Everything**: All security events are logged
- **Fail Securely**: Errors do not compromise security

## Authentication

### JWT-Based Authentication

The platform uses JWT (JSON Web Tokens) for authentication with the following features:

- **Access Tokens**: Short-lived tokens (configurable, default 30 minutes)
- **Refresh Tokens**: Long-lived tokens (configurable, default 7 days)
- **Token Revocation**: Planned Redis-based token blacklist
- **Secure Storage**: Tokens stored in memory or secure HTTP-only cookies

### Authentication Flow

1. **Login**: User submits credentials to `/api/v1/auth/login`
2. **Token Generation**: Server generates access and refresh tokens
3. **Token Storage**: Client stores tokens securely
4. **API Access**: Client includes access token in Authorization header
5. **Token Refresh**: Client uses refresh token to get new access token
6. **Logout**: Client invalidates tokens (server-side revocation planned)

### Default Users

For development, the following default users are configured:

| Username | Password | Role | Purpose |
|----------|----------|------|---------|
| admin | admin123 | admin | Full system access |
| analyst | analyst123 | analyst | Analytics and reporting |
| service | service123 | service | Service account for automation |

**IMPORTANT**: Change default passwords before production deployment.

### Password Requirements

- Minimum length: 8 characters (configurable)
- Uppercase letters: Required (configurable)
- Lowercase letters: Required (configurable)
- Digits: Required (configurable)
- Special characters: Required (configurable)

## Authorization

### Role-Based Access Control (RBAC)

The platform implements RBAC with the following roles:

#### Roles

- **admin**: Full system access, user management, configuration
- **analyst**: Analytics execution, reporting, customer data access
- **risk_manager**: Risk analysis, model monitoring, alert management
- **auditor**: Read-only access, audit log export, compliance
- **service**: Service account for automated processes

#### Permissions

Permissions are organized by functional area:

- **Analytics**: `analytics:read`, `analytics:execute`
- **Customers**: `customers:read`, `customers:modify`
- **Risk**: `risk:read`, `risk:execute`
- **Models**: `models:view`, `models:register`, `models:activate`, `models:retire`
- **Alerts**: `alerts:view`, `alerts:acknowledge`, `alerts:resolve`
- **Audit**: `audit:read`, `audit:export`
- **Administration**: `users:manage`, `roles:manage`, `configuration:manage`

### Using Authorization

To protect API endpoints, use the provided FastAPI dependencies:

```python
from api.auth.dependencies import get_current_user, require_permission, require_role
from api.auth.models import Permission, UserRole

# Require authentication
@router.get("/protected")
async def protected_endpoint(current_user: User = Depends(get_current_user)):
    return {"message": "Authenticated"}

# Require specific permission
@router.post("/analytics")
async def run_analytics(current_user: User = Depends(require_permission(Permission.ANALYTICS_EXECUTE))):
    return {"message": "Analytics executed"}

# Require specific role
@router.delete("/users/{user_id}")
async def delete_user(current_user: User = Depends(require_role(UserRole.ADMIN))):
    return {"message": "User deleted"}
```

## API Security

### Security Headers

The API automatically adds security headers to all responses:

- **Strict-Transport-Security**: Enforces HTTPS in production
- **X-Content-Type-Options**: Prevents MIME type sniffing
- **X-Frame-Options**: Prevents clickjacking
- **Content-Security-Policy**: Controls resource loading
- **Referrer-Policy**: Controls referrer information
- **Permissions-Policy**: Controls browser features
- **X-XSS-Protection**: Enables XSS filtering

### Rate Limiting

Rate limiting is implemented using slowapi:

- **Default**: 100 requests per minute per IP
- **Login**: 5 requests per minute
- **Token Refresh**: 10 requests per minute
- **Configurable**: All limits can be adjusted via environment variables

### Request Size Limits

Maximum request body size: 10 MB

### Correlation IDs

All requests include a correlation ID header (`X-Correlation-ID`) for tracing and debugging.

## WebSocket Security

### Authentication

WebSocket connections support optional JWT authentication:

```javascript
// Connect with token
const ws = new WebSocket(`ws://localhost:8000/ws?token=${accessToken}`);
```

### Connection Management

- **User Mapping**: Tracks user-to-connection mapping
- **Targeted Messaging**: Send messages to specific users
- **Broadcasting**: Send messages to all connected clients

## Database Security

### Connection Security

- **SSL Mode**: Required in production
- **Connection Pooling**: Secure connection pooling
- **Credential Protection**: Passwords hidden in logs

### Configuration

Database security is configured via environment variables:

```bash
DB_SSL_MODE=require  # Require SSL in production
DB_HOST=localhost
DB_PASSWORD=your_secure_password
```

## Redis Security

### Authentication

Redis supports password authentication:

```bash
REDIS_PASSWORD=your_redis_password
```

### Connection Security

- **Password Protection**: All connections require password
- **TLS Support**: Planned for production

## Kafka Security

### Current Configuration

- **Development**: No authentication (for local development)
- **Production**: SASL authentication planned

### Schema Registry

Schema registry credentials are configured via environment variables:

```bash
SCHEMA_REGISTRY_USERNAME=registry_user
SCHEMA_REGISTRY_PASSWORD=registry_password
```

## Security Headers

### Production Headers

In production mode, the following strict security headers are applied:

```http
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self'; object-src 'none';
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

### Development Headers

In development mode, CSP is relaxed to allow Swagger UI:

```http
Content-Security-Policy: default-src 'self' 'unsafe-inline' 'unsafe-eval';
```

## Rate Limiting

### Configuration

Rate limiting is configured via environment variables:

```bash
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=100
```

### Implementation

Rate limiting uses slowapi with in-memory storage. For production, Redis-based distributed rate limiting is recommended.

## Audit Logging

### Security Events

The following security events are automatically logged:

- **Login Success/Failure**: With source IP and correlation ID
- **Token Refresh**: With user ID and correlation ID
- **Logout**: With user ID and correlation ID
- **Access Denied**: With resource, action, and reason
- **Role Changes**: With actor and target user
- **User Creation/Deletion**: With actor and user details

### Event Structure

```json
{
  "event_id": "uuid",
  "timestamp": "ISO-8601",
  "event_type": "LOGIN_SUCCESS",
  "actor": "username",
  "resource": "auth",
  "action": "login",
  "result": "success",
  "source": "IP address",
  "correlation_id": "correlation-id",
  "context": {}
}
```

## Error Handling

### Secure Error Responses

All errors return safe, generic messages to clients:

```json
{
  "detail": "Error message",
  "correlation_id": "correlation-id"
}
```

### Logging

Full error details (including stack traces) are logged server-side for debugging but never exposed to clients.

## Docker Security

### Image Security

- **Base Image**: Python 3.11 slim (minimal attack surface)
- **Non-Root User**: Application runs as non-root user
- **Minimal Packages**: Only required system packages installed
- **No Cache**: Build cache disabled to prevent sensitive data

### .dockerignore

Sensitive files are excluded from Docker builds:

- `.env` files
- SSH keys
- Certificates
- Secrets directory

## Dependency Security

### Vulnerability Scanning

Use the provided script to check for known vulnerabilities:

```bash
python scripts/check_dependencies.py
```

This runs:
- **pip-audit**: Checks for known vulnerabilities in dependencies
- **safety**: Checks for security issues in installed packages

### Static Analysis

Use bandit for Python security static analysis:

```bash
bandit -r api/ -c .bandit
```

## Security Testing

### Running Security Tests

```bash
pytest tests/security/
```

### Test Coverage

Security tests cover:
- Password hashing and verification
- JWT token creation and verification
- User permissions and roles
- API authentication requirements
- Security headers
- Input validation

### Test Files

- `tests/security/test_authentication.py`: Authentication tests
- `tests/security/test_authorization.py`: Authorization tests
- `tests/security/test_api_security.py`: API security tests

## Production Deployment Checklist

Before deploying to production:

- [ ] Change all default passwords
- [ ] Set strong JWT secret key (32+ characters)
- [ ] Enable SSL/TLS for all connections
- [ ] Configure Redis password
- [ ] Enable Kafka SASL authentication
- [ ] Set environment to `production`
- [ ] Configure CORS to specific origins
- [ ] Enable rate limiting
- [ ] Configure secure CSP headers
- [ ] Set up log aggregation
- [ ] Configure audit log retention
- [ ] Run security tests
- [ ] Run dependency vulnerability scan
- [ ] Run static code analysis
- [ ] Review and rotate all secrets
- [ ] Enable database SSL mode
- [ ] Configure backup and recovery
- [ ] Set up monitoring and alerting

## Security Incident Response

If a security incident is suspected:

1. **Isolate**: If possible, isolate affected systems
2. **Preserve**: Preserve logs and evidence
3. **Investigate**: Review audit logs for suspicious activity
4. **Contain**: Rotate compromised credentials
5. **Notify**: Follow incident response procedures
6. **Document**: Document all actions taken
7. **Review**: Conduct post-incident review

## Additional Resources

- [Security Architecture](security_architecture.md)
- [Security Reconciliation](../audit/phase1_security_reconciliation.md)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
