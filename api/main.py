"""FastAPI application entry point."""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from typing import Optional
from datetime import datetime
import logging

from api.config import settings
from api.database import engine
from api.routers import (
    health,
    customers,
    profitability,
    risk,
    segments,
    churn,
    portfolio,
    realtime,
    # recommendations,  # Temporarily disabled due to missing imblearn dependency
    auth,
)
from api.errors import security_exception_handler, generic_exception_handler
from api.websocket import manager, authenticate_websocket

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info(f"Starting Banking Analytics API in {settings.environment} environment")
    if settings.environment == "development":
        logger.warning("Running in development mode - security features may be relaxed")
    # Database connection is established on first use via engine
    yield
    # Shutdown
    logger.info("Shutting down Banking Analytics API")
    try:
        if hasattr(engine, 'dispose'):
            if callable(engine.dispose):
                engine.dispose()
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

# Create FastAPI application without security middleware for now
app = FastAPI(
    title="Banking Analytics API",
    description="API for Banking Customer Profitability and Risk Analytics Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    swagger_ui_parameters={"defaultModelsExpandDepth": 1},
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Add exception handlers
app.add_exception_handler(HTTPException, security_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(customers.router, prefix="/api/v1", tags=["Customers"])
app.include_router(profitability.router, prefix="/api/v1", tags=["Profitability"])
app.include_router(risk.router, prefix="/api/v1", tags=["Risk"])
app.include_router(segments.router, prefix="/api/v1", tags=["Segments"])
app.include_router(churn.router, prefix="/api/v1", tags=["Churn"])
app.include_router(portfolio.router, prefix="/api/v1", tags=["Portfolio"])
app.include_router(realtime.router, tags=["Realtime"])
# app.include_router(recommendations.router, prefix="/api/v1", tags=["Recommendations"])  # Temporarily disabled

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Banking Analytics API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
        "auth": "/api/v1/auth/login",
        "websocket": "/api/v1/ws"
    }


# WebSocket endpoint for real-time updates
@app.websocket("/api/v1/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None, description="JWT access token for authentication")
):
    """WebSocket endpoint for real-time updates.
    
    Authentication is optional for public streams but required for personalized streams.
    
    Args:
        websocket: WebSocket connection
        token: Optional JWT access token
    """
    # Authenticate user if token provided
    user = await authenticate_websocket(token)
    
    # Generate client ID
    import uuid
    client_id = str(uuid.uuid4())
    
    # Accept connection
    await manager.connect(websocket, client_id, user)
    
    try:
        if user:
            await websocket.send_json({
                "type": "connected",
                "message": f"Connected as {user.username}",
                "user_id": user.user_id,
                "roles": [role.value for role in user.roles]
            })
        else:
            await websocket.send_json({
                "type": "connected",
                "message": "Connected as anonymous (public stream only)",
                "user_id": None
            })
        
        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_json()
            
            # Handle different message types
            if data.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                })
            elif data.get("type") == "subscribe":
                # Handle subscription to specific channels
                channel = data.get("channel")
                if channel:
                    await websocket.send_json({
                        "type": "subscribed",
                        "channel": channel,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
    except WebSocketDisconnect:
        manager.disconnect(client_id, user)
        logger.info(f"WebSocket client {client_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
        manager.disconnect(client_id, user)
