"""Authentication schemas for request/response validation."""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class Token(BaseModel):
    """Token response schema."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration in seconds")


class TokenData(BaseModel):
    """Token payload data."""
    user_id: str
    username: str
    roles: list[str]
    exp: datetime
    iat: datetime
    type: str
    jti: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request schema."""
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=1, description="Password")


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""
    refresh_token: str = Field(..., description="Refresh token")


class LogoutRequest(BaseModel):
    """Logout request schema."""
    refresh_token: Optional[str] = Field(None, description="Refresh token to invalidate")


class PasswordChangeRequest(BaseModel):
    """Password change request schema."""
    current_password: str = Field(..., min_length=1, description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")


class PasswordResetRequest(BaseModel):
    """Password reset request schema (admin only)."""
    user_id: str = Field(..., description="User ID")
    new_password: str = Field(..., min_length=8, description="New password")
