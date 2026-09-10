"""Security event auditing module."""

from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum
import logging
import uuid

logger = logging.getLogger(__name__)


class SecurityEventType(str, Enum):
    """Security event types."""
    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_FAILURE = "LOGIN_FAILURE"
    TOKEN_REFRESH = "TOKEN_REFRESH"
    LOGOUT = "LOGOUT"
    ACCESS_DENIED = "ACCESS_DENIED"
    ROLE_CHANGE = "ROLE_CHANGE"
    USER_CREATED = "USER_CREATED"
    USER_DISABLED = "USER_DISABLED"
    MODEL_ACTIVATED = "MODEL_ACTIVATED"
    MODEL_RETIRED = "MODEL_RETIRED"
    CONFIG_CHANGED = "CONFIG_CHANGED"
    SECURITY_CONFIG_CHANGED = "SECURITY_CONFIG_CHANGED"


class SecurityEvent:
    """Security event record."""
    
    def __init__(
        self,
        event_type: SecurityEventType,
        actor: str,
        resource: Optional[str] = None,
        action: Optional[str] = None,
        result: str = "success",
        reason: Optional[str] = None,
        source: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """Initialize security event.
        
        Args:
            event_type: Type of security event
            actor: User or service ID
            resource: Resource being accessed
            action: Action being performed
            result: Result of the action (success/failure)
            reason: Reason for failure or denial
            source: Source IP or service name
            context: Additional context data
        """
        self.event_id = str(uuid.uuid4())
        self.timestamp = datetime.utcnow()
        self.event_type = event_type
        self.actor = actor
        self.resource = resource
        self.action = action
        self.result = result
        self.reason = reason
        self.source = source
        self.correlation_id = context.get("correlation_id") if context else None
        self.context = context or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary.
        
        Returns:
            Dictionary representation of event
        """
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type.value,
            "actor": self.actor,
            "resource": self.resource,
            "action": self.action,
            "result": self.result,
            "reason": self.reason,
            "source": self.source,
            "correlation_id": self.correlation_id,
            "context": self.context
        }


class SecurityAuditor:
    """Security event auditor."""
    
    def __init__(self):
        """Initialize security auditor."""
        # TODO: Integrate with Redis for short-term storage
        # TODO: Integrate with PostgreSQL for long-term storage
        pass
    
    def log_event(self, event: SecurityEvent) -> None:
        """Log a security event.
        
        Args:
            event: Security event to log
        """
        logger.info(
            f"Security Event: {event.event_type.value} | "
            f"Actor: {event.actor} | "
            f"Resource: {event.resource} | "
            f"Action: {event.action} | "
            f"Result: {event.result} | "
            f"Source: {event.source} | "
            f"Correlation ID: {event.correlation_id}"
        )
        
        # TODO: Store in Redis for immediate access
        # TODO: Store in PostgreSQL for long-term retention
    
    def log_login_success(
        self,
        username: str,
        source: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> None:
        """Log successful login.
        
        Args:
            username: Username
            source: Source IP
            correlation_id: Correlation ID
        """
        event = SecurityEvent(
            event_type=SecurityEventType.LOGIN_SUCCESS,
            actor=username,
            resource="auth",
            action="login",
            result="success",
            source=source,
            context={"correlation_id": correlation_id}
        )
        self.log_event(event)
    
    def log_login_failure(
        self,
        username: str,
        reason: str,
        source: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> None:
        """Log failed login.
        
        Args:
            username: Username
            reason: Failure reason
            source: Source IP
            correlation_id: Correlation ID
        """
        event = SecurityEvent(
            event_type=SecurityEventType.LOGIN_FAILURE,
            actor=username,
            resource="auth",
            action="login",
            result="failure",
            reason=reason,
            source=source,
            context={"correlation_id": correlation_id}
        )
        self.log_event(event)
    
    def log_access_denied(
        self,
        user_id: str,
        resource: str,
        action: str,
        reason: str,
        correlation_id: Optional[str] = None
    ) -> None:
        """Log access denial.
        
        Args:
            user_id: User ID
            resource: Resource being accessed
            action: Action being attempted
            reason: Denial reason
            correlation_id: Correlation ID
        """
        event = SecurityEvent(
            event_type=SecurityEventType.ACCESS_DENIED,
            actor=user_id,
            resource=resource,
            action=action,
            result="denied",
            reason=reason,
            context={"correlation_id": correlation_id}
        )
        self.log_event(event)
    
    def log_token_refresh(
        self,
        user_id: str,
        correlation_id: Optional[str] = None
    ) -> None:
        """Log token refresh.
        
        Args:
            user_id: User ID
            correlation_id: Correlation ID
        """
        event = SecurityEvent(
            event_type=SecurityEventType.TOKEN_REFRESH,
            actor=user_id,
            resource="auth",
            action="refresh_token",
            result="success",
            context={"correlation_id": correlation_id}
        )
        self.log_event(event)
    
    def log_logout(
        self,
        user_id: str,
        correlation_id: Optional[str] = None
    ) -> None:
        """Log logout.
        
        Args:
            user_id: User ID
            correlation_id: Correlation ID
        """
        event = SecurityEvent(
            event_type=SecurityEventType.LOGOUT,
            actor=user_id,
            resource="auth",
            action="logout",
            result="success",
            context={"correlation_id": correlation_id}
        )
        self.log_event(event)


# Global security auditor instance
security_auditor = SecurityAuditor()
