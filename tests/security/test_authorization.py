"""Tests for authorization system."""

import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi import HTTPException, status
from api.auth.models import UserRole, Permission
from api.auth.dependencies import require_permission, require_role, require_admin
from api.auth.service import authenticate_user, create_tokens


class TestAuthorizationDependencies:
    """Test authorization dependencies."""
    
    @pytest.mark.asyncio
    async def test_require_permission_granted(self):
        """Test permission check when user has permission."""
        from api.auth.models import User
        
        user = User(
            user_id="analyst1",
            username="analyst",
            roles=[UserRole.ANALYST]
        )
        
        # Analyst has analytics read permission
        dependency = require_permission(Permission.ANALYTICS_READ)
        result = await dependency(current_user=user)
        
        assert result == user
    
    @pytest.mark.asyncio
    async def test_require_permission_denied(self):
        """Test permission check when user lacks permission."""
        from api.auth.models import User
        
        user = User(
            user_id="analyst1",
            username="analyst",
            roles=[UserRole.ANALYST]
        )
        
        # Analyst does not have user management permission
        dependency = require_permission(Permission.USERS_MANAGE)
        
        with pytest.raises(HTTPException) as exc_info:
            await dependency(current_user=user)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_require_role_granted(self):
        """Test role check when user has role."""
        from api.auth.models import User
        
        user = User(
            user_id="analyst1",
            username="analyst",
            roles=[UserRole.ANALYST]
        )
        
        dependency = require_role(UserRole.ANALYST)
        result = await dependency(current_user=user)
        
        assert result == user
    
    @pytest.mark.asyncio
    async def test_require_role_denied(self):
        """Test role check when user lacks role."""
        from api.auth.models import User
        
        user = User(
            user_id="analyst1",
            username="analyst",
            roles=[UserRole.ANALYST]
        )
        
        dependency = require_role(UserRole.ADMIN)
        
        with pytest.raises(HTTPException) as exc_info:
            await dependency(current_user=user)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_require_admin_granted(self):
        """Test admin check when user is admin."""
        from api.auth.models import User
        
        user = User(
            user_id="admin1",
            username="admin",
            roles=[UserRole.ADMIN]
        )
        
        result = await require_admin(current_user=user)
        
        assert result == user
    
    @pytest.mark.asyncio
    async def test_require_admin_denied(self):
        """Test admin check when user is not admin."""
        from api.auth.models import User
        
        user = User(
            user_id="analyst1",
            username="analyst",
            roles=[UserRole.ANALYST]
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await require_admin(current_user=user)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN


class TestPermissionMatrix:
    """Test role-permission matrix."""
    
    def test_analyst_permissions(self):
        """Test analyst has correct permissions."""
        from api.auth.models import User, ROLE_PERMISSIONS
        
        expected_perms = ROLE_PERMISSIONS[UserRole.ANALYST]
        
        user = User(
            user_id="analyst1",
            username="analyst",
            roles=[UserRole.ANALYST]
        )
        
        for perm in expected_perms:
            assert user.has_permission(perm)
        
        # Should not have admin permissions
        assert not user.has_permission(Permission.USERS_MANAGE)
        assert not user.has_permission(Permission.ROLES_MANAGE)
    
    def test_risk_manager_permissions(self):
        """Test risk manager has correct permissions."""
        from api.auth.models import User, ROLE_PERMISSIONS
        
        expected_perms = ROLE_PERMISSIONS[UserRole.RISK_MANAGER]
        
        user = User(
            user_id="risk1",
            username="risk_manager",
            roles=[UserRole.RISK_MANAGER]
        )
        
        for perm in expected_perms:
            assert user.has_permission(perm)
        
        # Should have risk execute permission
        assert user.has_permission(Permission.RISK_EXECUTE)
    
    def test_auditor_permissions(self):
        """Test auditor has correct permissions."""
        from api.auth.models import User, ROLE_PERMISSIONS
        
        expected_perms = ROLE_PERMISSIONS[UserRole.AUDITOR]
        
        user = User(
            user_id="auditor1",
            username="auditor",
            roles=[UserRole.AUDITOR]
        )
        
        for perm in expected_perms:
            assert user.has_permission(perm)
        
        # Should have audit export permission
        assert user.has_permission(Permission.AUDIT_EXPORT)
        
        # Should not have write permissions
        assert not user.has_permission(Permission.CUSTOMERS_MODIFY)
        assert not user.has_permission(Permission.ALERTS_ACKNOWLEDGE)
    
    def test_service_permissions(self):
        """Test service account has correct permissions."""
        from api.auth.models import User, ROLE_PERMISSIONS
        
        expected_perms = ROLE_PERMISSIONS[UserRole.SERVICE]
        
        user = User(
            user_id="service1",
            username="service",
            roles=[UserRole.SERVICE],
            is_service=True
        )
        
        for perm in expected_perms:
            assert user.has_permission(perm)
        
        # Should have model lifecycle permissions
        assert user.has_permission(Permission.MODELS_REGISTER)
        assert user.has_permission(Permission.MODELS_ACTIVATE)
