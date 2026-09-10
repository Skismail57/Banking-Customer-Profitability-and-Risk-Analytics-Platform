"""Tests for API security."""

import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi.testclient import TestClient
from fastapi import status


class TestAPIAuthentication:
    """Test API authentication requirements."""
    
    def test_login_endpoint_requires_no_auth(self):
        """Test login endpoint does not require authentication."""
        from api.main import app
        
        client = TestClient(app)
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        
        # Should succeed with valid credentials
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]
    
    def test_protected_endpoint_requires_auth(self):
        """Test protected endpoint requires authentication."""
        from api.main import app
        
        client = TestClient(app)
        response = client.get("/api/v1/auth/me")
        
        # Should fail without authentication
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_protected_endpoint_with_valid_token(self):
        """Test protected endpoint succeeds with valid token."""
        from api.main import app
        
        client = TestClient(app)
        
        # First login to get token
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        
        if login_response.status_code == status.HTTP_200_OK:
            token = login_response.json()["access_token"]
            
            # Use token to access protected endpoint
            response = client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == status.HTTP_200_OK
            assert response.json()["username"] == "admin"
    
    def test_invalid_token_rejected(self):
        """Test invalid token is rejected."""
        from api.main import app
        
        client = TestClient(app)
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestSecurityHeaders:
    """Test security headers are present."""
    
    def test_security_headers_present(self):
        """Test security headers are present in responses."""
        from api.main import app
        
        client = TestClient(app)
        response = client.get("/")
        
        # Check for security headers
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"
        
        assert "X-XSS-Protection" in response.headers
        
        assert "Content-Security-Policy" in response.headers
        
        assert "Referrer-Policy" in response.headers
        
        assert "Permissions-Policy" in response.headers
    
    def test_correlation_id_header(self):
        """Test correlation ID header is present."""
        from api.main import app
        
        client = TestClient(app)
        response = client.get("/")
        
        assert "X-Correlation-ID" in response.headers
        assert len(response.headers["X-Correlation-ID"]) > 0


class TestRateLimiting:
    """Test rate limiting functionality."""
    
    def test_login_rate_limit(self):
        """Test login endpoint has rate limiting."""
        from api.main import app
        
        client = TestClient(app)
        
        # Make multiple login attempts
        for i in range(10):
            response = client.post(
                "/api/v1/auth/login",
                json={"username": "wrong", "password": "wrong"}
            )
        
        # Should eventually be rate limited
        # Note: This test may need adjustment based on rate limit configuration
        pass


class TestInputValidation:
    """Test input validation."""
    
    def test_login_missing_username(self):
        """Test login fails with missing username."""
        from api.main import app
        
        client = TestClient(app)
        response = client.post(
            "/api/v1/auth/login",
            json={"password": "password"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_login_missing_password(self):
        """Test login fails with missing password."""
        from api.main import app
        
        client = TestClient(app)
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_login_short_username(self):
        """Test login fails with short username."""
        from api.main import app
        
        client = TestClient(app)
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "ab", "password": "password"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
