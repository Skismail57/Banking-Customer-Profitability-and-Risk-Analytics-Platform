"""WebSocket support for real-time updates.

This module provides WebSocket endpoints for pushing real-time
updates to connected clients (alerts, metrics, etc.).
"""

from datetime import datetime
from typing import Dict, Any, Optional
import json
import logging
from fastapi import WebSocket, WebSocketDisconnect, status, Query
from fastapi.security.utils import get_authorization_scheme_param
from api.auth.security import verify_token
from api.auth.models import User
from api.auth.exceptions import InvalidTokenError, ExpiredTokenError

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time updates with authentication."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[str, str] = {}  # user_id -> client_id mapping
    
    async def connect(self, websocket: WebSocket, client_id: str, user: Optional[User] = None):
        """Accept a WebSocket connection with optional authentication.
        
        Args:
            websocket: WebSocket connection
            client_id: Unique client identifier
            user: Authenticated user (optional for public streams)
        """
        await websocket.accept()
        self.active_connections[client_id] = websocket
        
        if user:
            self.user_connections[user.user_id] = client_id
            logger.info(f"User {user.username} connected as client {client_id}. Total connections: {len(self.active_connections)}")
        else:
            logger.info(f"Anonymous client {client_id} connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, client_id: str, user: Optional[User] = None):
        """Remove a WebSocket connection.
        
        Args:
            client_id: Client identifier
            user: Authenticated user (optional)
        """
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        
        if user and user.user_id in self.user_connections:
            del self.user_connections[user.user_id]
        
        if user:
            logger.info(f"User {user.username} disconnected. Total connections: {len(self.active_connections)}")
        else:
            logger.info(f"Anonymous client {client_id} disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: Dict[str, Any], client_id: str):
        """Send a message to a specific client.
        
        Args:
            message: Message to send
            client_id: Client identifier
        """
        if client_id in self.active_connections:
            try:
                websocket = self.active_connections[client_id]
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to client {client_id}: {e}")
                self.disconnect(client_id)
    
    async def send_user_message(self, message: Dict[str, Any], user_id: str):
        """Send a message to a specific user.
        
        Args:
            message: Message to send
            user_id: User identifier
        """
        client_id = self.user_connections.get(user_id)
        if client_id:
            await self.send_personal_message(message, client_id)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast a message to all connected clients.
        
        Args:
            message: Message to broadcast
        """
        disconnected_clients = []
        
        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # Remove disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    async def broadcast_alert(self, alert: Dict[str, Any]):
        """Broadcast an alert to all connected clients.
        
        Args:
            alert: Alert data
        """
        message = {
            'type': 'alert',
            'data': alert,
            'timestamp': datetime.utcnow().isoformat()
        }
        await self.broadcast(message)
    
    async def broadcast_metrics(self, metrics: Dict[str, Any]):
        """Broadcast streaming metrics to all connected clients.
        
        Args:
            metrics: Metrics data
        """
        message = {
            'type': 'metrics',
            'data': metrics,
            'timestamp': datetime.utcnow().isoformat()
        }
        await self.broadcast(message)
    
    async def broadcast_risk_update(self, customer_key: str, risk_data: Dict[str, Any]):
        """Broadcast a risk update to all connected clients.
        
        Args:
            customer_key: Customer identifier
            risk_data: Risk score data
        """
        message = {
            'type': 'risk_update',
            'customer_key': customer_key,
            'data': risk_data,
            'timestamp': datetime.utcnow().isoformat()
        }
        await self.broadcast(message)
    
    def get_connection_count(self) -> int:
        """Get the number of active connections.
        
        Returns:
            Number of active connections
        """
        return len(self.active_connections)


# Global connection manager instance
manager = ConnectionManager()


async def authenticate_websocket(token: Optional[str]) -> Optional[User]:
    """Authenticate WebSocket connection using JWT token.
    
    Args:
        token: JWT token from query parameter or header
        
    Returns:
        User if authenticated, None otherwise
    """
    if not token:
        return None
    
    try:
        payload = verify_token(token, token_type="access")
        
        user_id = payload.get("sub")
        username = payload.get("username")
        roles = payload.get("roles", [])
        
        if user_id is None or username is None:
            return None
        
        from api.auth.models import UserRole
        user = User(
            user_id=user_id,
            username=username,
            roles=[UserRole(role) for role in roles],
            is_active=payload.get("is_active", True),
            is_service=payload.get("is_service", False),
        )
        
        return user
        
    except (InvalidTokenError, ExpiredTokenError):
        return None
