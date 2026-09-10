"""Security utilities for authentication and authorization."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets
import logging
import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from api.config import settings
except ImportError:
    # Fallback for testing
    from dotenv import load_dotenv
    load_dotenv()
    from pydantic_settings import BaseSettings
    from pydantic import Field

    class Settings(BaseSettings):
        jwt_algorithm: str = "HS256"
        jwt_secret_key: str = Field(default_factory=lambda: os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production"))
        jwt_access_token_expire_minutes: int = 30
        jwt_refresh_token_expire_days: int = 7

    settings = Settings()

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
ALGORITHM = settings.jwt_algorithm
SECRET_KEY = settings.jwt_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES = settings.jwt_access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = settings.jwt_refresh_token_expire_days


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token.
    
    Args:
        data: Payload data to include in token
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create a JWT refresh token.
    
    Args:
        data: Payload data to include in token
        
    Returns:
        Encoded JWT refresh token
    """
    to_encode = data.copy()
    
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh",
        "jti": secrets.token_hex(16)  # Unique token ID for revocation
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
    """Verify and decode a JWT token.

    Args:
        token: JWT token to verify
        token_type: Expected token type (access or refresh)

    Returns:
        Decoded token payload

    Raises:
        InvalidTokenError: If token is invalid
        ExpiredTokenError: If token is expired
    """
    from api.auth.exceptions import InvalidTokenError, ExpiredTokenError

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Verify token type
        if payload.get("type") != token_type:
            raise InvalidTokenError(f"Invalid token type: expected {token_type}")

        return payload

    except jwt.ExpiredSignatureError:
        raise ExpiredTokenError("Token has expired")
    except jwt.JWTError as e:
        raise InvalidTokenError(f"Invalid token: {str(e)}")


def generate_secret_key(length: int = 32) -> str:
    """Generate a cryptographically secure random secret key.

    Args:
        length: Length of the secret key

    Returns:
        Secure random secret key
    """
    return secrets.token_urlsafe(length)
