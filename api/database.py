"""Database connection management.

This module provides database connection management with connection pooling,
query optimization, and backup strategy for the banking analytics platform.

Assumptions:
- PostgreSQL is the primary database
- Connection pooling is managed by SQLAlchemy
- Backups are managed by external tools (pg_dump, WAL archiving)

Limitations:
- Connection pool size may need tuning based on load
- Query optimization requires manual index management
- Backup strategy requires external orchestration

Fairness Considerations:
- Ensure database access controls prevent unauthorized data access
- Monitor query performance for bias in data access patterns
- Implement audit logging for sensitive queries
"""

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import Optional, Dict, Any, List
import logging
import uuid
from datetime import datetime

from api.config import settings

logger = logging.getLogger(__name__)

# Enhanced connection pool configuration
POOL_SIZE = 20
MAX_OVERFLOW = 10
POOL_TIMEOUT = 30
POOL_RECYCLE = 3600  # Recycle connections after 1 hour

# Sync engine for simple queries with enhanced pooling
engine = create_engine(
    settings.db_url_sync,
    poolclass=QueuePool,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_timeout=POOL_TIMEOUT,
    pool_recycle=POOL_RECYCLE,
    pool_pre_ping=True,
    echo=False  # Set to True for SQL query logging
)

# Async engine for async operations with enhanced pooling (commented out if asyncpg not available)
try:
    # Skip async engine for SQLite since it doesn't support async
    if settings.db_url_async.startswith("sqlite"):
        logger.warning("SQLite does not support async operations, async engine disabled")
        async_engine = None
    else:
        async_engine = create_async_engine(
            settings.db_url_async,
            poolclass=QueuePool,
            pool_size=POOL_SIZE,
            max_overflow=MAX_OVERFLOW,
            pool_timeout=POOL_TIMEOUT,
            pool_recycle=POOL_RECYCLE,
            pool_pre_ping=True,
            echo=False
        )
except ImportError:
    logger.warning("asyncpg not installed, async engine disabled")
    async_engine = None

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Async session factory (only if async engine is available)
if async_engine:
    AsyncSessionLocal = sessionmaker(
        async_engine,
        class_=AsyncSession,
        autocommit=False,
        autoflush=False
    )
else:
    AsyncSessionLocal = None


def get_db():
    """Get database session for FastAPI dependency injection.
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db():
    """Get async database session.
    
    Yields:
        Async database session
    """
    async with AsyncSessionLocal() as session:
        yield session


class QueryOptimizer:
    """Query optimization utilities."""
    
    def __init__(self, engine):
        """Initialize query optimizer.
        
        Args:
            engine: SQLAlchemy engine
        """
        self.engine = engine
    
    def analyze_query_performance(self, query: str) -> Dict[str, Any]:
        """Analyze query performance using EXPLAIN ANALYZE.
        
        Args:
            query: SQL query to analyze
        
        Returns:
            Query performance metrics
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(f"EXPLAIN ANALYZE {query}")
                plan = result.fetchall()
                
                return {
                    'query': query,
                    'execution_plan': plan,
                    'analyzed_at': datetime.utcnow().isoformat()
                }
        except Exception as e:
            logger.error(f"Error analyzing query: {e}")
            return {'error': str(e)}
    
    def get_table_indexes(self, table_name: str) -> List[Dict[str, Any]]:
        """Get indexes for a table.
        
        Args:
            table_name: Table name
        
        Returns:
            List of index information
        """
        try:
            with self.engine.connect() as conn:
                # Validate table name to prevent SQL injection
                if not table_name.replace('_', '').replace('-', '').isalnum():
                    raise ValueError(f"Invalid table name: {table_name}")
                
                result = conn.execute(text("""
                    SELECT 
                        indexname, 
                        indexdef 
                    FROM pg_indexes 
                    WHERE tablename = :table_name
                """), {"table_name": table_name})
                indexes = result.fetchall()
                
                return [
                    {'name': row[0], 'definition': row[1]}
                    for row in indexes
                ]
        except Exception as e:
            logger.error(f"Error getting indexes: {e}")
            return []
    
    def suggest_indexes(self, table_name: str) -> List[str]:
        """Suggest potential indexes based on query patterns.
        
        Args:
            table_name: Table name
        
        Returns:
            List of index suggestions
        """
        # This is a simplified implementation
        # In production, this would analyze query logs
        suggestions = []
        
        # Get existing indexes
        existing_indexes = self.get_table_indexes(table_name)
        existing_names = {idx['name'] for idx in existing_indexes}
        
        # Common index suggestions
        common_suggestions = [
            f"CREATE INDEX idx_{table_name}_customer_key ON {table_name}(customer_key)",
            f"CREATE INDEX idx_{table_name}_created_at ON {table_name}(created_at)",
            f"CREATE INDEX idx_{table_name}_event_timestamp ON {table_name}(event_timestamp)"
        ]
        
        for suggestion in common_suggestions:
            idx_name = suggestion.split()[2]
            if idx_name not in existing_names:
                suggestions.append(suggestion)
        
        return suggestions


class BackupManager:
    """Database backup management utilities."""
    
    def __init__(self, engine):
        """Initialize backup manager.
        
        Args:
            engine: SQLAlchemy engine
        """
        self.engine = engine
        self.backup_history = []
    
    def create_backup(
        self,
        backup_name: str,
        backup_type: str = "full"
    ) -> Dict[str, Any]:
        """Create a database backup.
        
        Args:
            backup_name: Name for the backup
            backup_type: Type of backup (full, incremental)
        
        Returns:
            Backup information
        """
        logger.info(f"Creating {backup_type} backup: {backup_name}")
        
        # In production, this would use pg_dump or similar tools
        # This is a placeholder implementation
        backup_info = {
            'backup_id': str(uuid.uuid4()),
            'backup_name': backup_name,
            'backup_type': backup_type,
            'created_at': datetime.utcnow().isoformat(),
            'status': 'created',
            'note': 'Backup requires external tool (pg_dump)'
        }
        
        self.backup_history.append(backup_info)
        
        return backup_info
    
    def restore_backup(self, backup_id: str) -> Dict[str, Any]:
        """Restore a database backup.
        
        Args:
            backup_id: Backup identifier
        
        Returns:
            Restore information
        """
        logger.info(f"Restoring backup: {backup_id}")
        
        # Find backup
        backup = None
        for b in self.backup_history:
            if b['backup_id'] == backup_id:
                backup = b
                break
        
        if not backup:
            return {'error': 'Backup not found'}
        
        # In production, this would use pg_restore or similar tools
        return {
            'backup_id': backup_id,
            'restored_at': datetime.utcnow().isoformat(),
            'status': 'restored',
            'note': 'Restore requires external tool (pg_restore)'
        }
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List all backups.
        
        Returns:
            List of backup information
        """
        return self.backup_history
    
    def get_backup_schedule(self) -> Dict[str, Any]:
        """Get recommended backup schedule.
        
        Returns:
            Backup schedule recommendations
        """
        return {
            'full_backup': 'Daily at 2:00 AM UTC',
            'incremental_backup': 'Every 4 hours',
            'wal_archiving': 'Continuous',
            'retention_period': '90 days',
            'offsite_backup': 'Weekly'
        }


# Initialize optimizer and backup manager
query_optimizer = QueryOptimizer(engine)
backup_manager = BackupManager(engine)
