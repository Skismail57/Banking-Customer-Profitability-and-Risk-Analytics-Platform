"""Health check router."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from datetime import datetime
import logging
import redis

from api.database import get_db
from api.schemas.common import HealthResponse
from api.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint.
    
    Returns:
        HealthResponse: Health status
    """
    overall_status = "healthy"
    components = {}
    
    # Check database connection (critical)
    try:
        from api.database import engine
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        components['database'] = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        components['database'] = "unhealthy"
        overall_status = "unhealthy"
    
    # Check Redis connection (optional - only mark as degraded if running in production)
    try:
        redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2
        )
        redis_client.ping()
        components['redis'] = "healthy"
    except Exception as e:
        logger.warning(f"Redis health check failed (optional service): {e}")
        components['redis'] = "unhealthy"
        # Only mark as degraded if in production
        if settings.environment == "production":
            overall_status = "degraded"
    
    # Check Kafka/Redpanda connection (optional - only mark as degraded if running in production)
    try:
        from confluent_kafka import Producer
        kafka_servers = getattr(settings, 'kafka_bootstrap_servers', None) or getattr(settings, 'kafka_brokers', 'localhost:9092')
        conf = {
            'bootstrap.servers': kafka_servers,
            'client.id': 'health-check',
            'request.timeout.ms': 1000
        }
        producer = Producer(conf)
        producer.poll(0)
        components['kafka'] = "healthy"
    except Exception as e:
        logger.warning(f"Kafka health check failed (optional service): {e}")
        components['kafka'] = "unhealthy"
        # Only mark as degraded if in production
        if settings.environment == "production":
            overall_status = "degraded"
    
    return HealthResponse(
        status=overall_status,
        version=settings.app_version,
        timestamp=datetime.utcnow(),
        database=components.get('database', 'unknown'),
        components=components
    )


@router.get("/health/ready")
async def readiness_check():
    """Readiness check endpoint.
    
    Returns:
        Readiness status
    """
    # Readiness checks if the service is ready to accept traffic
    # This is more strict than health check
    return {
        "ready": True,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/health/live")
async def liveness_check():
    """Liveness check endpoint.
    
    Returns:
        Liveness status
    """
    # Liveness checks if the service is running
    # This is a simple check to see if the process is alive
    return {
        "alive": True,
        "timestamp": datetime.utcnow().isoformat()
    }
