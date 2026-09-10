"""API configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, Field
from typing import List, Optional, Union
import os
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = "Banking Analytics API"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = Field(default="development", description="Environment: development, test, production")
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database
    db_host: str = Field(default="localhost", description="Database host")
    db_port: int = Field(default=5432, description="Database port")
    db_name: str = Field(default="banking_analytics", description="Database name")
    db_user: str = Field(default="postgres", description="Database user")
    db_password: str = Field(default="", description="Database password")
    db_ssl_mode: str = Field(default="prefer", description="Database SSL mode: disable, allow, prefer, require, verify-ca, verify-full")
    
    @property
    def db_url(self) -> str:
        """Construct database URL without exposing password in logs."""
        # Use SQLite for demo if USE_SQLITE is set
        if os.getenv("USE_SQLITE", "false").lower() == "true":
            return "sqlite:///banking_analytics.db"
        return f"postgresql://{self.db_user}:***@{self.db_host}:{self.db_port}/{self.db_name}?sslmode={self.db_ssl_mode}"
    
    @property
    def db_url_sync(self) -> str:
        """Construct synchronous database URL for SQLAlchemy."""
        # Use SQLite for demo if USE_SQLITE is set
        if os.getenv("USE_SQLITE", "false").lower() == "true":
            return "sqlite:///banking_analytics.db"
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}?sslmode={self.db_ssl_mode}"
    
    @property
    def db_url_async(self) -> str:
        """Construct asynchronous database URL for SQLAlchemy."""
        # Use SQLite for demo if USE_SQLITE is set (SQLite doesn't support async)
        if os.getenv("USE_SQLITE", "false").lower() == "true":
            return "sqlite:///banking_analytics.db"
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}?sslmode={self.db_ssl_mode}"
    
    # CORS
    cors_origins: Union[str, List[str]] = Field(
        default="http://localhost:3000,http://localhost:8501",
        description="CORS allowed origins (comma-separated string or list)"
    )
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = Field(default=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    cors_allow_headers: List[str] = Field(default=["*"])
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    # Logging
    log_level: str = "INFO"
    
    # Pagination
    default_page_size: int = 50
    max_page_size: int = 500
    
    # Cache
    cache_ttl: int = 3600  # 1 hour
    
    # Security - JWT
    jwt_secret_key: str = Field(
        default_factory=lambda: os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production"),
        description="JWT secret key for token signing"
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_access_token_expire_minutes: int = Field(default=15, description="JWT access token expiration in minutes")
    jwt_refresh_token_expire_days: int = Field(default=7, description="JWT refresh token expiration in days")
    
    # Security - Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests_per_minute: int = 100
    rate_limit_burst: int = 10
    
    # Security - Password (if local authentication)
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_digit: bool = True
    password_require_special: bool = True
    
    # Redis
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_db: int = Field(default=0, description="Redis database number")
    redis_password: Optional[str] = Field(default=None, description="Redis password")
    redis_ssl: bool = Field(default=False, description="Redis SSL/TLS")
    
    # Kafka/Redpanda
    kafka_bootstrap_servers: str = Field(default="localhost:9092", description="Kafka bootstrap servers")
    kafka_security_protocol: str = Field(default="PLAINTEXT", description="Kafka security protocol: PLAINTEXT, SSL, SASL_SSL")
    kafka_sasl_mechanism: Optional[str] = Field(default=None, description="Kafka SASL mechanism")
    kafka_sasl_username: Optional[str] = Field(default=None, description="Kafka SASL username")
    kafka_sasl_password: Optional[str] = Field(default=None, description="Kafka SASL password")
    
    # Schema Registry
    schema_registry_url: str = Field(default="http://localhost:8081", description="Schema registry URL")
    schema_registry_api_key: Optional[str] = Field(default=None, description="Schema registry API key")
    schema_registry_api_secret: Optional[str] = Field(default=None, description="Schema registry API secret")
    
    @field_validator('environment')
    @classmethod
    def validate_environment(cls, v):
        """Validate environment value."""
        valid_environments = ['development', 'test', 'production']
        if v not in valid_environments:
            raise ValueError(f"Environment must be one of {valid_environments}, got {v}")
        return v
    
    @field_validator('jwt_secret_key')
    @classmethod
    def validate_jwt_secret(cls, v, info):
        """Validate JWT secret key is strong enough for production."""
        # Get environment from the field values
        environment = info.data.get('environment', 'development')
        if environment == 'production' and v == 'dev-secret-key-change-in-production':
            raise ValueError("JWT_SECRET_KEY must be set in production environment")
        if environment == 'production' and len(v) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters in production")
        return v
    
    @field_validator('db_password')
    @classmethod
    def validate_db_password(cls, v, info):
        """Validate database password is set in production."""
        environment = info.data.get('environment', 'development')
        if environment == 'production' and not v:
            raise ValueError("DB_PASSWORD must be set in production environment")
        return v
    
    @field_validator('redis_password')
    @classmethod
    def validate_redis_password(cls, v, info):
        """Validate Redis password is set in production."""
        environment = info.data.get('environment', 'development')
        if environment == 'production' and not v:
            logger.warning("REDIS_PASSWORD not set in production - Redis will be unauthenticated")
        return v
    
    @field_validator('kafka_sasl_password')
    @classmethod
    def validate_kafka_password(cls, v, info):
        """Validate Kafka password if SASL is enabled."""
        security_protocol = info.data.get('kafka_security_protocol', 'PLAINTEXT')
        environment = info.data.get('environment', 'development')
        if environment == 'production' and 'SASL' in security_protocol and not v:
            raise ValueError("KAFKA_SASL_PASSWORD must be set when using SASL in production")
        return v
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_prefix=""
    )
    
    def validate_production_secrets(self) -> List[str]:
        """Validate all required secrets are set for production.
        
        Returns:
            List of validation errors (empty if all valid)
        """
        errors = []
        
        if self.environment == 'production':
            if self.jwt_secret_key == 'dev-secret-key-change-in-production':
                errors.append("JWT_SECRET_KEY must be changed from default in production")
            if not self.db_password:
                errors.append("DB_PASSWORD must be set in production")
            if self.kafka_security_protocol == 'PLAINTEXT':
                errors.append("KAFKA_SECURITY_PROTOCOL should be SSL or SASL_SSL in production")
            if not self.redis_ssl:
                errors.append("REDIS_SSL should be enabled in production")
        
        return errors


# Global settings instance
settings = Settings()

# Validate production secrets on startup
validation_errors = settings.validate_production_secrets()
if validation_errors:
    logger.warning(f"Configuration validation warnings: {', '.join(validation_errors)}")
    if settings.environment == 'production':
        logger.error("Production configuration validation failed")
        for error in validation_errors:
            logger.error(f"  - {error}")
