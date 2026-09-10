"""Tests for authentication system."""

import pytest
import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from api.auth.security import (
    create_access_token,
    create_refresh_token,
    verify_token,
    get_password_hash,
    verify_password
)
from api.auth.exceptions import InvalidTokenError, ExpiredTokenError
from api.auth.models import UserRole, Permission


class TestPasswordHashing:
    """Test password hashing and verification."""
    
    def test_password_hashing(self):
        """Test password hashing produces different hashes for same password."""
        password = "test_password_123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Hashes should be different (salt)
        assert hash1 != hash2
        
        # But both should verify correctly
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)
    
    def test_password_verification(self):
        """Test password verification."""
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed)
        assert not verify_password(wrong_password, hashed)
    
    def test_password_strength_validation(self):
        """Test password strength validation."""
        from api.auth.service import validate_password_strength
        
        # Weak passwords
        assert not validate_password_strength("short")
        assert not validate_password_strength("nouppercase123")
        assert not validate_password_strength("NOLOWERCASE123")
        assert not validate_password_strength("NoDigits!")
        
        # Strong password
        assert validate_password_strength("StrongPassword123!")


class TestTokenCreation:
    """Test JWT token creation."""
    
    def test_create_access_token(self):
        """Test access token creation."""
        data = {"sub": "user123", "username": "testuser"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_refresh_token(self):
        """Test refresh token creation."""
        data = {"sub": "user123", "username": "testuser"}
        token = create_refresh_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0


class TestTokenVerification:
    """Test JWT token verification."""
    
    def test_verify_valid_access_token(self):
        """Test verification of valid access token."""
        data = {"sub": "user123", "username": "testuser"}
        token = create_access_token(data)
        
        payload = verify_token(token, token_type="access")
        
        assert payload["sub"] == "user123"
        assert payload["username"] == "testuser"
        assert payload["type"] == "access"
    
    def test_verify_valid_refresh_token(self):
        """Test verification of valid refresh token."""
        data = {"sub": "user123", "username": "testuser"}
        token = create_refresh_token(data)
        
        payload = verify_token(token, token_type="refresh")
        
        assert payload["sub"] == "user123"
        assert payload["username"] == "testuser"
        assert payload["type"] == "refresh"
        assert "jti" in payload  # Refresh tokens have jti
    
    def test_verify_invalid_token(self):
        """Test verification of invalid token."""
        invalid_token = "invalid.token.here"
        
        with pytest.raises(InvalidTokenError):
            verify_token(invalid_token, token_type="access")
    
    def test_verify_wrong_token_type(self):
        """Test verification fails with wrong token type."""
        data = {"sub": "user123", "username": "testuser"}
        token = create_access_token(data)
        
        with pytest.raises(InvalidTokenError):
            verify_token(token, token_type="refresh")


class TestUserModel:
    """Test User model and permissions."""
    
    def test_user_permissions(self):
        """Test user permission calculation."""
        from api.auth.models import User
        
        user = User(
            user_id="user1",
            username="analyst",
            roles=[UserRole.ANALYST]
        )
        
        # Analyst should have analytics permissions
        assert user.has_permission(Permission.ANALYTICS_READ)
        assert user.has_permission(Permission.ANALYTICS_EXECUTE)
        
        # But not admin permissions
        assert not user.has_permission(Permission.USERS_MANAGE)
        assert not user.has_permission(Permission.ROLES_MANAGE)
    
    def test_admin_permissions(self):
        """Test admin has all permissions."""
        from api.auth.models import User
        
        user = User(
            user_id="admin1",
            username="admin",
            roles=[UserRole.ADMIN]
        )
        
        # Admin should have all permissions
        for perm in Permission:
            assert user.has_permission(perm)
    
    def test_is_admin(self):
        """Test is_admin method."""
        from api.auth.models import User
        
        admin_user = User(
            user_id="admin1",
            username="admin",
            roles=[UserRole.ADMIN]
        )
        
        analyst_user = User(
            user_id="analyst1",
            username="analyst",
            roles=[UserRole.ANALYST]
        )
        
        assert admin_user.is_admin()
        assert not analyst_user.is_admin()
    
    def test_has_role(self):
        """Test has_role method."""
        from api.auth.models import User
        
        user = User(
            user_id="user1",
            username="analyst",
            roles=[UserRole.ANALYST, UserRole.AUDITOR]
        )
        
        assert user.has_role(UserRole.ANALYST)
        assert user.has_role(UserRole.AUDITOR)
        assert not user.has_role(UserRole.ADMIN)


class TestAuthenticationService:
    """Test authentication service."""
    
    def test_authenticate_valid_user(self):
        """Test authentication with valid credentials."""
        from api.auth.service import authenticate_user
        
        # Default admin user: admin / admin123
        user = authenticate_user("admin", "admin123")
        
        assert user.username == "admin"
        assert UserRole.ADMIN in user.roles
    
    def test_authenticate_invalid_user(self):
        """Test authentication with invalid username."""
        from api.auth.service import authenticate_user
        from api.auth.exceptions import UserNotFoundError
        
        with pytest.raises(UserNotFoundError):
            authenticate_user("nonexistent", "password")
    
    def test_authenticate_invalid_password(self):
        """Test authentication with invalid password."""
        from api.auth.service import authenticate_user
        from api.auth.exceptions import InvalidCredentialsError
        
        with pytest.raises(InvalidCredentialsError):
            authenticate_user("admin", "wrongpassword")
    
    def test_create_tokens_for_user(self):
        """Test token creation for user."""
        from api.auth.service import create_tokens, authenticate_user
        
        user = authenticate_user("admin", "admin123")
        tokens = create_tokens(user)
        
        assert tokens.access_token is not None
        assert tokens.refresh_token is not None
        assert tokens.token_type == "bearer"
        assert tokens.expires_in > 0
