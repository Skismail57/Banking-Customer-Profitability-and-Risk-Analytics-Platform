"""Authentication service for user management and authentication."""

from typing import Optional, Dict, Any
from datetime import timedelta
import logging

from api.auth.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password
)
from api.auth.models import User, UserInDB, UserRole, Permission
from api.auth.schemas import Token
from api.auth.exceptions import (
    InvalidCredentialsError,
    UserNotFoundError,
    UserDisabledError,
    PasswordValidationError,
    InvalidTokenError
)
from api.config import settings

logger = logging.getLogger(__name__)


# In-memory user store for development
# TODO: Replace with database in production
_users_db: Dict[str, UserInDB] = {}


def _initialize_default_users():
    """Initialize default users for development."""
    # Default admin user
    admin_user = UserInDB(
        user_id="admin",
        username="admin",
        email="admin@banking.local",
        password_hash=get_password_hash("admin123"),  # Change in production!
        roles=[UserRole.ADMIN],
        is_active=True,
        is_service=False,
    )
    _users_db["admin"] = admin_user
    
    # Default analyst user
    analyst_user = UserInDB(
        user_id="analyst",
        username="analyst",
        email="analyst@banking.local",
        password_hash=get_password_hash("analyst123"),
        roles=[UserRole.ANALYST],
        is_active=True,
        is_service=False,
    )
    _users_db["analyst"] = analyst_user
    
    # Default service account
    service_user = UserInDB(
        user_id="service",
        username="service",
        email=None,
        password_hash=get_password_hash("service123"),
        roles=[UserRole.SERVICE],
        is_active=True,
        is_service=True,
    )
    _users_db["service"] = service_user
    
    logger.info("Initialized default users for development")


# Initialize default users on module load
_initialize_default_users()


def get_user_by_username(username: str) -> Optional[User]:
    """Get user by username.
    
    Args:
        username: Username to look up
        
    Returns:
        User if found, None otherwise
    """
    user_in_db = _users_db.get(username)
    if user_in_db:
        return User(**user_in_db.dict())
    return None


def get_user_by_id(user_id: str) -> Optional[User]:
    """Get user by ID.
    
    Args:
        user_id: User ID to look up
        
    Returns:
        User if found, None otherwise
    """
    for user_in_db in _users_db.values():
        if user_in_db.user_id == user_id:
            return User(**user_in_db.dict())
    return None


def authenticate_user(username: str, password: str) -> User:
    """Authenticate user with username and password.
    
    Args:
        username: Username
        password: Plain text password
        
    Returns:
        Authenticated user
        
    Raises:
        InvalidCredentialsError: If credentials are invalid
        UserNotFoundError: If user not found
        UserDisabledError: If user account is disabled
    """
    user_in_db = _users_db.get(username)
    
    if not user_in_db:
        logger.warning(f"Authentication failed: user not found - {username}")
        raise UserNotFoundError(f"User not found: {username}")
    
    if not verify_password(password, user_in_db.password_hash):
        logger.warning(f"Authentication failed: invalid password - {username}")
        raise InvalidCredentialsError("Invalid username or password")
    
    if not user_in_db.is_active:
        logger.warning(f"Authentication failed: user disabled - {username}")
        raise UserDisabledError("User account is disabled")
    
    user = User(**user_in_db.dict())
    logger.info(f"User authenticated successfully - {username}")
    return user


def create_tokens(user: User) -> Token:
    """Create access and refresh tokens for user.
    
    Args:
        user: User to create tokens for
        
    Returns:
        Token object with access and refresh tokens
    """
    # Create access token
    access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    access_token = create_access_token(
        data={
            "sub": user.user_id,
            "username": user.username,
            "roles": [role.value for role in user.roles],
            "is_active": user.is_active,
            "is_service": user.is_service,
        },
        expires_delta=access_token_expires
    )
    
    # Create refresh token
    refresh_token = create_refresh_token(
        data={
            "sub": user.user_id,
            "username": user.username,
        }
    )
    
    token = Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.jwt_access_token_expire_minutes * 60
    )
    
    logger.info(f"Tokens created for user - {user.username}")
    return token


def refresh_access_token(refresh_token: str) -> Token:
    """Refresh access token using refresh token.
    
    Args:
        refresh_token: Refresh token
        
    Returns:
        New token object with fresh access and refresh tokens
        
    Raises:
        InvalidTokenError: If refresh token is invalid
        UserNotFoundError: If user not found
        UserDisabledError: If user account is disabled
    """
    from api.auth.security import verify_token
    
    payload = verify_token(refresh_token, token_type="refresh")
    
    user_id = payload.get("sub")
    username = payload.get("username")
    
    if user_id is None or username is None:
        raise InvalidTokenError("Invalid refresh token payload")
    
    user = get_user_by_id(user_id)
    if not user:
        raise UserNotFoundError("User not found")
    
    if not user.is_active:
        raise UserDisabledError("User account is disabled")
    
    # Create new tokens
    return create_tokens(user)


def validate_password_strength(password: str) -> bool:
    """Validate password strength against requirements.
    
    Args:
        password: Password to validate
        
    Returns:
        True if password meets requirements, False otherwise
    """
    if len(password) < settings.password_min_length:
        return False
    
    if settings.password_require_uppercase and not any(c.isupper() for c in password):
        return False
    
    if settings.password_require_lowercase and not any(c.islower() for c in password):
        return False
    
    if settings.password_require_digit and not any(c.isdigit() for c in password):
        return False
    
    if settings.password_require_special and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        return False
    
    return True


def create_user(user_data: Dict[str, Any]) -> User:
    """Create a new user.
    
    Args:
        user_data: User creation data
        
    Returns:
        Created user
        
    Raises:
        PasswordValidationError: If password doesn't meet requirements
    """
    username = user_data["username"]
    password = user_data["password"]
    
    if not validate_password_strength(password):
        raise PasswordValidationError("Password does not meet strength requirements")
    
    # Check if user already exists
    if username in _users_db:
        raise ValueError(f"User already exists: {username}")
    
    # Create user
    user_in_db = UserInDB(
        user_id=username,  # Use username as ID for simplicity
        username=username,
        email=user_data.get("email"),
        password_hash=get_password_hash(password),
        roles=user_data.get("roles", [UserRole.ANALYST]),
        is_active=True,
        is_service=False,
    )
    
    _users_db[username] = user_in_db
    
    user = User(**user_in_db.dict())
    logger.info(f"User created - {username}")
    return user


def update_user(user_id: str, updates: Dict[str, Any]) -> User:
    """Update user information.
    
    Args:
        user_id: User ID to update
        updates: Fields to update
        
    Returns:
        Updated user
        
    Raises:
        UserNotFoundError: If user not found
    """
    for username, user_in_db in _users_db.items():
        if user_in_db.user_id == user_id:
            # Update fields
            if "email" in updates:
                user_in_db.email = updates["email"]
            if "roles" in updates:
                user_in_db.roles = updates["roles"]
            if "is_active" in updates:
                user_in_db.is_active = updates["is_active"]
            
            user = User(**user_in_db.dict())
            logger.info(f"User updated - {username}")
            return user
    
    raise UserNotFoundError(f"User not found: {user_id}")


def change_password(user_id: str, current_password: str, new_password: str) -> None:
    """Change user password.
    
    Args:
        user_id: User ID
        current_password: Current password for verification
        new_password: New password
        
    Raises:
        UserNotFoundError: If user not found
        InvalidCredentialsError: If current password is incorrect
        PasswordValidationError: If new password doesn't meet requirements
    """
    for user_in_db in _users_db.values():
        if user_in_db.user_id == user_id:
            # Verify current password
            if not verify_password(current_password, user_in_db.password_hash):
                raise InvalidCredentialsError("Current password is incorrect")
            
            # Validate new password
            if not validate_password_strength(new_password):
                raise PasswordValidationError("New password does not meet strength requirements")
            
            # Update password
            user_in_db.password_hash = get_password_hash(new_password)
            logger.info(f"Password changed for user - {user_in_db.username}")
            return
    
    raise UserNotFoundError(f"User not found: {user_id}")


def list_users() -> list[User]:
    """List all users.
    
    Returns:
        List of all users
    """
    return [User(**user_in_db.dict()) for user_in_db in _users_db.values()]
