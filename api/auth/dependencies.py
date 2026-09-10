"""FastAPI dependencies for authentication and authorization."""

from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

from api.auth.security import verify_token
from api.auth.models import User, UserRole, Permission
from api.auth.exceptions import (
    InvalidTokenError,
    ExpiredTokenError,
    InsufficientPermissionError
)

logger = logging.getLogger(__name__)

# HTTP Bearer token scheme
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> User:
    """Get current user from JWT token.
    
    Args:
        credentials: HTTP Bearer credentials
        
    Returns:
        Current user
        
    Raises:
        HTTPException: If authentication fails
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    try:
        payload = verify_token(token, token_type="access")
        
        # Extract user information from token
        user_id = payload.get("sub")
        username = payload.get("username")
        roles = payload.get("roles", [])
        
        if user_id is None or username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
        
        # Create user object from token data
        user = User(
            user_id=user_id,
            username=username,
            roles=[UserRole(role) for role in roles],
            is_active=payload.get("is_active", True),
            is_service=payload.get("is_service", False),
        )
        
        return user
        
    except ExpiredTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidTokenError as e:
        logger.warning(f"Invalid token attempt: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user.
    
    Args:
        current_user: Current user from token
        
    Returns:
        Current active user
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )
    
    return current_user


def require_permission(permission: Permission):
    """Dependency factory to require a specific permission.
    
    Args:
        permission: Required permission
        
    Returns:
        Dependency function
    """
    async def check_permission(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        """Check if user has required permission.
        
        Args:
            current_user: Current user
            
        Returns:
            Current user if permission granted
            
        Raises:
            HTTPException: If permission denied
        """
        if not current_user.has_permission(permission):
            logger.warning(
                f"Permission denied: user={current_user.username}, "
                f"required_permission={permission.value}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission required: {permission.value}",
            )
        
        return current_user
    
    return check_permission


def require_role(role: UserRole):
    """Dependency factory to require a specific role.
    
    Args:
        role: Required role
        
    Returns:
        Dependency function
    """
    async def check_role(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        """Check if user has required role.
        
        Args:
            current_user: Current user
            
        Returns:
            Current user if role granted
            
        Raises:
            HTTPException: If role denied
        """
        if not current_user.has_role(role):
            logger.warning(
                f"Role denied: user={current_user.username}, "
                f"required_role={role.value}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role required: {role.value}",
            )
        
        return current_user
    
    return check_role


def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Require admin role.
    
    Args:
        current_user: Current user
        
    Returns:
        Current user if admin
        
    Raises:
        HTTPException: If not admin
    """
    if not current_user.is_admin():
        logger.warning(f"Admin access denied: user={current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
    
    return current_user


def optional_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """Optional authentication - returns None if no token provided.
    
    Args:
        credentials: HTTP Bearer credentials
        
    Returns:
        User if authenticated, None otherwise
    """
    if credentials is None:
        return None
    
    try:
        return get_current_user(credentials)
    except HTTPException:
        return None
