"""Authentication router for login, logout, token refresh."""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
import logging

from api.auth.service import (
    authenticate_user,
    create_tokens,
    refresh_access_token,
    change_password,
    create_user,
    update_user,
    list_users
)
from api.auth.schemas import LoginRequest, RefreshTokenRequest, Token, PasswordChangeRequest
from api.auth.dependencies import get_current_active_user, require_admin
from api.auth.models import User
from api.auth.exceptions import (
    InvalidCredentialsError,
    UserNotFoundError,
    UserDisabledError,
    PasswordValidationError
)
# from api.rate_limit import conditional_rate_limit  # Temporarily disabled due to missing slowapi

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/login", response_model=Token, tags=["Authentication"])
# @conditional_rate_limit("5/minute")  # Temporarily disabled due to missing slowapi
async def login(login_data: LoginRequest, request: Request) -> Token:
    """Authenticate user and return tokens.
    
    Args:
        login_data: Login credentials
        request: FastAPI request
        
    Returns:
        Access and refresh tokens
        
    Raises:
        HTTPException: If authentication fails
    """
    correlation_id = request.state.correlation_id if hasattr(request.state, 'correlation_id') else None
    source = request.client.host if request.client else None
    
    try:
        user = authenticate_user(login_data.username, login_data.password)
        tokens = create_tokens(user)
        logger.info(f"User logged in successfully - {user.username}")
        
        # Log security event
        from api.audit import security_auditor
        security_auditor.log_login_success(
            username=user.username,
            source=source,
            correlation_id=correlation_id
        )
        
        return tokens
    except UserNotFoundError:
        from api.audit import security_auditor
        security_auditor.log_login_failure(
            username=login_data.username,
            reason="User not found",
            source=source,
            correlation_id=correlation_id
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    except InvalidCredentialsError:
        from api.audit import security_auditor
        security_auditor.log_login_failure(
            username=login_data.username,
            reason="Invalid password",
            source=source,
            correlation_id=correlation_id
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    except UserDisabledError:
        from api.audit import security_auditor
        security_auditor.log_login_failure(
            username=login_data.username,
            reason="User account disabled",
            source=source,
            correlation_id=correlation_id
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )


@router.post("/refresh", response_model=Token, tags=["Authentication"])
# @conditional_rate_limit("10/minute")  # Temporarily disabled due to missing slowapi
async def refresh_token(refresh_data: RefreshTokenRequest, request: Request) -> Token:
    """Refresh access token using refresh token.
    
    Args:
        refresh_data: Refresh token
        request: FastAPI request
        
    Returns:
        New access and refresh tokens
        
    Raises:
        HTTPException: If refresh fails
    """
    correlation_id = request.state.correlation_id if hasattr(request.state, 'correlation_id') else None
    
    try:
        tokens = refresh_access_token(refresh_data.refresh_token)
        logger.info("Token refreshed successfully")
        
        # Log security event
        from api.audit import security_auditor
        security_auditor.log_token_refresh(
            user_id="user",  # Will be extracted from token in production
            correlation_id=correlation_id
        )
        
        return tokens
    except (InvalidCredentialsError, UserNotFoundError, UserDisabledError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )


@router.post("/logout", tags=["Authentication"])
async def logout(
    current_user: Annotated[User, Depends(get_current_active_user)],
    request: Request
) -> dict:
    """Logout user (client-side token invalidation).
    
    Args:
        current_user: Current authenticated user
        request: FastAPI request
        
    Returns:
        Logout confirmation
    """
    correlation_id = request.state.correlation_id if hasattr(request.state, 'correlation_id') else None
    
    # TODO: Implement token revocation/blacklist in Redis
    logger.info(f"User logged out - {current_user.username}")
    
    # Log security event
    from api.audit import security_auditor
    security_auditor.log_logout(
        user_id=current_user.user_id,
        correlation_id=correlation_id
    )
    
    return {"message": "Logged out successfully"}


@router.post("/change-password", tags=["Authentication"])
async def change_user_password(
    password_data: PasswordChangeRequest,
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> dict:
    """Change current user's password.
    
    Args:
        password_data: Password change data
        current_user: Current authenticated user
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If password change fails
    """
    try:
        change_password(
            current_user.user_id,
            password_data.current_password,
            password_data.new_password
        )
        logger.info(f"Password changed successfully - {current_user.username}")
        return {"message": "Password changed successfully"}
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    except PasswordValidationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password does not meet strength requirements",
        )


@router.get("/me", response_model=User, tags=["Authentication"])
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    """Get current user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user information
    """
    return current_user


@router.get("/users", response_model=list[User], tags=["Authentication"])
async def get_all_users(
    current_user: Annotated[User, Depends(require_admin)]
) -> list[User]:
    """Get all users (admin only).
    
    Args:
        current_user: Current authenticated user (must be admin)
        
    Returns:
        List of all users
    """
    return list_users()


@router.post("/users", response_model=User, tags=["Authentication"])
async def create_new_user(
    user_data: dict,
    current_user: Annotated[User, Depends(require_admin)]
) -> User:
    """Create a new user (admin only).
    
    Args:
        user_data: User creation data
        current_user: Current authenticated user (must be admin)
        
    Returns:
        Created user
        
    Raises:
        HTTPException: If user creation fails
    """
    try:
        user = create_user(user_data)
        logger.info(f"User created by admin - {current_user.username} created {user.username}")
        return user
    except PasswordValidationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password does not meet strength requirements",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
