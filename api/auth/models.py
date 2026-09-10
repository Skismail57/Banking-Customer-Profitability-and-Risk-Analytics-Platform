"""Authentication models."""

from enum import Enum
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class UserRole(str, Enum):
    """User roles for RBAC."""
    ADMIN = "admin"
    ANALYST = "analyst"
    RISK_MANAGER = "risk_manager"
    AUDITOR = "auditor"
    SERVICE = "service"


class Permission(str, Enum):
    """Permissions for authorization."""
    # Analytics
    ANALYTICS_READ = "analytics:read"
    ANALYTICS_EXECUTE = "analytics:execute"
    
    # Customers
    CUSTOMERS_READ = "customers:read"
    CUSTOMERS_MODIFY = "customers:modify"
    
    # Risk
    RISK_READ = "risk:read"
    RISK_EXECUTE = "risk:execute"
    
    # Models
    MODELS_VIEW = "models:view"
    MODELS_REGISTER = "models:register"
    MODELS_ACTIVATE = "models:activate"
    MODELS_RETIRE = "models:retire"
    
    # Alerts
    ALERTS_VIEW = "alerts:view"
    ALERTS_ACKNOWLEDGE = "alerts:acknowledge"
    ALERTS_RESOLVE = "alerts:resolve"
    
    # Audit
    AUDIT_READ = "audit:read"
    AUDIT_EXPORT = "audit:export"
    
    # Administration
    USERS_MANAGE = "users:manage"
    ROLES_MANAGE = "roles:manage"
    CONFIGURATION_MANAGE = "configuration:manage"


# Role to permission mapping
ROLE_PERMISSIONS: dict[UserRole, List[Permission]] = {
    UserRole.ADMIN: [perm for perm in Permission],  # All permissions
    UserRole.ANALYST: [
        Permission.ANALYTICS_READ,
        Permission.ANALYTICS_EXECUTE,
        Permission.CUSTOMERS_READ,
        Permission.RISK_READ,
        Permission.MODELS_VIEW,
        Permission.ALERTS_VIEW,
        Permission.ALERTS_ACKNOWLEDGE,
        Permission.ALERTS_RESOLVE,
    ],
    UserRole.RISK_MANAGER: [
        Permission.ANALYTICS_READ,
        Permission.CUSTOMERS_READ,
        Permission.RISK_READ,
        Permission.RISK_EXECUTE,
        Permission.MODELS_VIEW,
        Permission.ALERTS_VIEW,
        Permission.ALERTS_ACKNOWLEDGE,
        Permission.ALERTS_RESOLVE,
    ],
    UserRole.AUDITOR: [
        Permission.ANALYTICS_READ,
        Permission.CUSTOMERS_READ,
        Permission.RISK_READ,
        Permission.MODELS_VIEW,
        Permission.ALERTS_VIEW,
        Permission.AUDIT_READ,
        Permission.AUDIT_EXPORT,
    ],
    UserRole.SERVICE: [
        Permission.ANALYTICS_READ,
        Permission.ANALYTICS_EXECUTE,
        Permission.CUSTOMERS_READ,
        Permission.CUSTOMERS_MODIFY,
        Permission.RISK_READ,
        Permission.RISK_EXECUTE,
        Permission.MODELS_VIEW,
        Permission.MODELS_REGISTER,
        Permission.MODELS_ACTIVATE,
        Permission.MODELS_RETIRE,
        Permission.ALERTS_VIEW,
    ],
}


class User(BaseModel):
    """User model."""
    user_id: str = Field(..., description="Unique user identifier")
    username: str = Field(..., description="Username")
    email: Optional[str] = Field(None, description="Email address")
    roles: List[UserRole] = Field(default_factory=list, description="User roles")
    is_active: bool = Field(default=True, description="Whether user is active")
    is_service: bool = Field(default=False, description="Whether this is a service account")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    @property
    def permissions(self) -> set[Permission]:
        """Get all permissions for this user based on roles."""
        perms = set()
        for role in self.roles:
            perms.update(ROLE_PERMISSIONS.get(role, []))
        return perms
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if user has a specific permission.
        
        Args:
            permission: Permission to check
            
        Returns:
            True if user has permission, False otherwise
        """
        return permission in self.permissions
    
    def has_role(self, role: UserRole) -> bool:
        """Check if user has a specific role.
        
        Args:
            role: Role to check
            
        Returns:
            True if user has role, False otherwise
        """
        return role in self.roles
    
    def is_admin(self) -> bool:
        """Check if user is an admin.
        
        Returns:
            True if user has admin role, False otherwise
        """
        return UserRole.ADMIN in self.roles


class UserCreate(BaseModel):
    """User creation model."""
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[str] = Field(None, max_length=100)
    password: str = Field(..., min_length=8)
    roles: List[UserRole] = Field(default_factory=list)


class UserUpdate(BaseModel):
    """User update model."""
    email: Optional[str] = Field(None, max_length=100)
    roles: Optional[List[UserRole]] = None
    is_active: Optional[bool] = None


class UserInDB(User):
    """User model with password hash (for internal use only)."""
    password_hash: str = Field(..., description="Hashed password")
