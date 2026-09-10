"""Database connection and session management utilities."""

import os
from typing import Optional
from urllib.parse import urlunparse

import yaml
from dotenv import load_dotenv
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import QueuePool

# Load environment variables from .env file
load_dotenv()

Base = declarative_base()


class DatabaseConfig:
    """Database configuration loaded from YAML and environment variables."""
    
    def __init__(self, environment: str = "development"):
        """Initialize database configuration.
        
        Args:
            environment: Environment name (development, staging, production)
        """
        self.environment = environment
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """Load configuration from YAML files."""
        # Load base configuration
        base_config_path = "config/base.yaml"
        try:
            with open(base_config_path, "r") as f:
                config = yaml.safe_load(f)
        except FileNotFoundError:
            config = {"database": {"host": "localhost", "port": 5432, "name": "banking_analytics"}}
        
        # Load environment-specific overrides
        env_config_path = f"config/environments/{self.environment}.yaml"
        try:
            with open(env_config_path, "r") as f:
                env_config = yaml.safe_load(f)
                # Deep merge environment config
                config = self._deep_merge(config, env_config)
        except FileNotFoundError:
            pass
        
        # Substitute environment variables
        config = self._substitute_env_vars(config)
        
        return config
    
    def _deep_merge(self, base: dict, override: dict) -> dict:
        """Deep merge override dictionary into base dictionary."""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    def _substitute_env_vars(self, config: dict) -> dict:
        """Substitute environment variables in configuration."""
        if isinstance(config, dict):
            return {k: self._substitute_env_vars(v) for k, v in config.items()}
        elif isinstance(config, str) and config.startswith("${") and config.endswith("}"):
            env_var = config[2:-1]
            return os.getenv(env_var, config)
        else:
            return config
    
    @property
    def database_url(self) -> str:
        """Construct database URL from configuration."""
        db_config = self.config["database"]
        
        # Get credentials from environment variables for security
        user = os.getenv("DATABASE_USER", "postgres")
        password = os.getenv("DATABASE_PASSWORD", "")
        host = db_config["host"]
        port = db_config["port"]
        database = db_config["name"]
        
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    @property
    def pool_size(self) -> int:
        """Get connection pool size."""
        return self.config["database"].get("pool_size", 10)
    
    @property
    def max_overflow(self) -> int:
        """Get maximum overflow connections."""
        return self.config["database"].get("max_overflow", 20)
    
    @property
    def pool_timeout(self) -> int:
        """Get pool timeout in seconds."""
        return self.config["database"].get("pool_timeout", 30)
    
    @property
    def pool_recycle(self) -> int:
        """Get pool recycle time in seconds."""
        return self.config["database"].get("pool_recycle", 3600)
    
    @property
    def echo(self) -> bool:
        """Get SQL echo setting."""
        return self.config["database"].get("echo", False)


class DatabaseManager:
    """Database connection and session manager."""
    
    _instance: Optional["DatabaseManager"] = None
    _engine: Optional[Engine] = None
    _session_factory: Optional[sessionmaker] = None
    
    def __new__(cls, config: Optional[DatabaseConfig] = None):
        """Singleton pattern to ensure single engine instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        """Initialize database manager.
        
        Args:
            config: Database configuration. If None, loads from environment.
        """
        if self._initialized:
            return
        
        self.config = config or DatabaseConfig()
        self._initialized = True
    
    def get_engine(self) -> Engine:
        """Get or create SQLAlchemy engine."""
        if self._engine is None:
            self._engine = create_engine(
                self.config.database_url,
                poolclass=QueuePool,
                pool_size=self.config.pool_size,
                max_overflow=self.config.max_overflow,
                pool_timeout=self.config.pool_timeout,
                pool_recycle=self.config.pool_recycle,
                echo=self.config.echo,
                pool_pre_ping=True,  # Verify connections before using
            )
        return self._engine
    
    def get_session_factory(self) -> sessionmaker:
        """Get or create session factory."""
        if self._session_factory is None:
            self._session_factory = sessionmaker(
                bind=self.get_engine(),
                expire_on_commit=False
            )
        return self._session_factory
    
    def get_session(self) -> Session:
        """Get a new database session."""
        return self.get_session_factory()()
    
    def create_tables(self) -> None:
        """Create all tables in the database."""
        Base.metadata.create_all(self.get_engine())
    
    def drop_tables(self) -> None:
        """Drop all tables from the database."""
        Base.metadata.drop_all(self.get_engine())
    
    def dispose(self) -> None:
        """Dispose of the engine and close all connections."""
        if self._engine is not None:
            self._engine.dispose()
            self._engine = None
            self._session_factory = None


def get_db_manager(config: Optional[DatabaseConfig] = None) -> DatabaseManager:
    """Get database manager instance.
    
    Args:
        config: Database configuration. If None, loads from environment.
    
    Returns:
        DatabaseManager instance
    """
    return DatabaseManager(config)


def get_db_session(config: Optional[DatabaseConfig] = None) -> Session:
    """Get a database session.
    
    Args:
        config: Database configuration. If None, loads from environment.
    
    Returns:
        SQLAlchemy Session
    """
    return get_db_manager(config).get_session()
