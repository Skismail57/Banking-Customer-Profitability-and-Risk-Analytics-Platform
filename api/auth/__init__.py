"""Authentication module for Banking Analytics API."""

from api.auth.security import (
    create_access_token,
    create_refresh_token,
    verify_token,
    get_password_hash,
    verify_password
)
from api.auth.models import User, UserRole
from api.auth.schemas import Token, TokenData, LoginRequest, RefreshTokenRequest
from api.auth.dependencies import get_current_user, get_current_active_user, require_role
from api.auth.exceptions import (
    AuthenticationError,
    InvalidTokenError,
    ExpiredTokenError,
    InsufficientPermissionError
)

__all__ = [
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "get_password_hash",
    "verify_password",
    "User",
    "UserRole",
    "Token",
    "TokenData",
    "LoginRequest",
    "RefreshTokenRequest",
    "get_current_user",
    "get_current_active_user",
    "require_role",
    "AuthenticationError",
    "InvalidTokenError",
    "ExpiredTokenError",
    "InsufficientPermissionError",
]
