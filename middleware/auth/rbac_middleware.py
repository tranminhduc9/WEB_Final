"""
Role-Based Access Control (RBAC) Middleware.

This middleware handles role-based authorization for protected endpoints.
Implementation following Task #2 requirements - Role Guard functionality.
"""

import logging
from typing import List, Dict, Set, Optional, Union
from functools import wraps

from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

# Safe import with fallback
try:
    from ..config.settings import MiddlewareSettings
except ImportError:
    # Fallback for standalone usage
    import sys, os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config.settings import MiddlewareSettings

from .jwt_middleware import AuthException


logger = logging.getLogger(__name__)


class RoleException(HTTPException):
    """Custom role-based access exception."""

    def __init__(self, error_code: str, message: str, status_code: int = status.HTTP_403_FORBIDDEN):
        super().__init__(
            status_code=status_code,
            detail={
                "success": False,
                "error": {
                    "code": error_code,
                    "message": message
                }
            }
        )


class RoleGuardMiddleware(BaseHTTPMiddleware):
    """
    Role Guard Middleware for FastAPI.

    Enforces role-based access control for protected endpoints.
    Must be used after JWT authentication middleware.
    """

    def __init__(
        self,
        app,
        allowed_roles: Optional[List[str]] = None,
        role_permissions: Optional[Dict[str, Set[str]]] = None,
        endpoint_permissions: Optional[Dict[str, List[str]]] = None,
        default_role: str = "guest",
        require_auth: bool = True,
    ):
        """
        Initialize Role Guard Middleware.

        Args:
            app: FastAPI application instance
            allowed_roles: List of allowed roles for all endpoints
            role_permissions: Role to permissions mapping
            endpoint_permissions: Endpoint to required permissions mapping
            default_role: Default role for unauthenticated users
            require_auth: Whether authentication is required
        """
        super().__init__(app)

        self.allowed_roles = allowed_roles or []
        self.require_auth = require_auth

        # Default role hierarchy (higher number = higher privilege)
        self.role_hierarchy = {
            "guest": 0,
            "user": 1,
            "moderator": 2,
            "admin": 3
        }

        # Default role permissions
        self.role_permissions = role_permissions or {
            "admin": {"read", "write", "delete", "manage_users", "manage_content"},
            "moderator": {"read", "write", "manage_content"},
            "user": {"read", "write"},
            "guest": {"read"}
        }

        # Endpoint-specific permissions (method:endpoint: required_roles)
        self.endpoint_permissions = endpoint_permissions or {
            "GET:/api/v1/admin": ["admin"],
            "POST:/api/v1/admin": ["admin"],
            "PUT:/api/v1/admin": ["admin"],
            "DELETE:/api/v1/admin": ["admin"],
            "GET:/api/v1/moderator": ["admin", "moderator"],
            "POST:/api/v1/moderator": ["admin", "moderator"],
            "PUT:/api/v1/moderator": ["admin", "moderator"],
            "POST:/api/v1/posts": ["admin", "moderator", "user"],
            "PUT:/api/v1/posts": ["admin", "moderator"],
            "DELETE:/api/v1/posts": ["admin", "moderator"],
            "GET:/api/v1/places": ["admin", "moderator", "user", "guest"],
            "POST:/api/v1/places": ["admin", "moderator"],
        }

        self.default_role = default_role

    async def dispatch(self, request: Request, call_next):
        """
        Process request and enforce role-based access control.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware in chain

        Returns:
            HTTP response if authorized, otherwise raises RoleException
        """
        try:
            # Get endpoint key for permission checking
            endpoint_key = f"{request.method}:{request.url.path}"

            # Check if this endpoint requires role checking
            if not self._requires_role_check(request, endpoint_key):
                return await call_next(request)

            # Extract user from request state (set by JWT middleware)
            user = self._get_user_from_request(request)

            # Check if authentication is required
            if self.require_auth and not user:
                logger.warning(f"Authentication required for {endpoint_key} but no user found")
                raise RoleException("UNAUTHORIZED", "Yêu cầu xác thực", status.HTTP_401_UNAUTHORIZED)

            # Get user role
            user_role = user.get("role", self.default_role) if user else self.default_role

            # Check role-based access
            if not self._check_role_access(request, endpoint_key, user_role):
                user_info = f"User {user['id']}" if user else "Anonymous"
                logger.warning(f"Access denied for {user_info} with role '{user_role}' to {endpoint_key}")
                raise RoleException("FORBIDDEN", "Bạn không có quyền truy cập")

            # Log successful access
            if user:
                logger.debug(f"Access granted for user {user['id']} ({user_role}) to {endpoint_key}")

            return await call_next(request)

        except RoleException:
            # Re-raise role exceptions
            raise
        except Exception as e:
            logger.error(f"Unexpected error in role guard middleware: {str(e)}")
            raise RoleException("INTERNAL_SERVER_ERROR", "Lỗi server nội bộ", status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _requires_role_check(self, request: Request, endpoint_key: str) -> bool:
        """
        Check if the endpoint requires role-based access control.

        Args:
            request: FastAPI request object
            endpoint_key: Formatted endpoint key (METHOD:path)

        Returns:
            True if role check is required, False otherwise
        """
        # Skip for excluded paths
        excluded_paths = [
            "/health",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/favicon.ico",
            "/static/",
            "/api/v1/auth/login",
            "/api/v1/auth/register",
        ]

        # Check if path starts with any excluded path
        for excluded_path in excluded_paths:
            if excluded_path.endswith('/') and request.url.path.startswith(excluded_path):
                return False
            if request.url.path == excluded_path:
                return False

        # Check if endpoint has specific permissions
        if endpoint_key in self.endpoint_permissions:
            return True

        # If no specific endpoint permissions but allowed_roles is set, check
        if self.allowed_roles:
            return True

        return False

    def _get_user_from_request(self, request: Request) -> Optional[Dict[str, any]]:
        """
        Extract user information from request state.

        Args:
            request: FastAPI request object

        Returns:
            User dictionary or None if not authenticated
        """
        return getattr(request.state, "user", None)

    def _check_role_access(self, request: Request, endpoint_key: str, user_role: str) -> bool:
        """
        Check if user role has access to the endpoint.

        Args:
            request: FastAPI request object
            endpoint_key: Formatted endpoint key (METHOD:path)
            user_role: User role string

        Returns:
            True if access is granted, False otherwise
        """
        # Check specific endpoint permissions first
        if endpoint_key in self.endpoint_permissions:
            allowed_roles = self.endpoint_permissions[endpoint_key]
            if user_role in allowed_roles:
                return True
            return False

        # Check global allowed roles if set
        if self.allowed_roles:
            return user_role in self.allowed_roles

        # Default: allow access for all authenticated users
        return True

    def _get_role_hierarchy_level(self, role: str) -> int:
        """
        Get hierarchy level for a role.

        Args:
            role: Role string

        Returns:
            Hierarchy level (higher number = higher privilege)
        """
        return self.role_hierarchy.get(role, 0)

    def _has_higher_privilege(self, user_role: str, required_role: str) -> bool:
        """
        Check if user role has higher or equal privilege than required role.

        Args:
            user_role: User's current role
            required_role: Required role for access

        Returns:
            True if user has sufficient privilege
        """
        user_level = self._get_role_hierarchy_level(user_role)
        required_level = self._get_role_hierarchy_level(required_role)
        return user_level >= required_level


def require_role(*allowed_roles: str):
    """
    Decorator for role-based access control on individual endpoints.

    Usage:
        @require_role('admin')
        async def admin_endpoint(request: Request):
            return {"message": "Admin only"}

        @require_role('admin', 'moderator')
        async def moderator_endpoint(request: Request):
            return {"message": "Admin or Moderator"}

    Args:
        *allowed_roles: List of allowed roles

    Returns:
        Decorator function
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request from arguments
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if not request:
                raise RoleException("INTERNAL_SERVER_ERROR", "Request object not found")

            # Check if user is authenticated
            user = getattr(request.state, "user", None)
            if not user:
                raise RoleException("UNAUTHORIZED", "Yêu cầu xác thực", status.HTTP_401_UNAUTHORIZED)

            # Check user role
            user_role = user.get("role", "user")
            if user_role not in allowed_roles:
                logger.warning(f"Access denied for user {user.get('id')} with role '{user_role}'")
                raise RoleException("FORBIDDEN", "Bạn không có quyền truy cập")

            # Log successful access
            logger.debug(f"Access granted for user {user.get('id')} ({user_role}) to {func.__name__}")

            # Call the original function
            return await func(*args, **kwargs)

        return wrapper
    return decorator


def require_permission(*required_permissions: str):
    """
    Decorator for permission-based access control.

    Usage:
        @require_permission('delete', 'manage_users')
        async def delete_user(request: Request):
            return {"message": "User deleted"}

    Args:
        *required_permissions: List of required permissions

    Returns:
        Decorator function
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request from arguments
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if not request:
                raise RoleException("INTERNAL_SERVER_ERROR", "Request object not found")

            # Check if user is authenticated
            user = getattr(request.state, "user", None)
            if not user:
                raise RoleException("UNAUTHORIZED", "Yêu cầu xác thực", status.HTTP_401_UNAUTHORIZED)

            # Check user permissions
            user_role = user.get("role", "user")

            # Create a temporary role guard instance to check permissions
            role_guard = RoleGuardMiddleware(None)
            user_permissions = role_guard.role_permissions.get(user_role, set())

            # Check if user has all required permissions
            for permission in required_permissions:
                if permission not in user_permissions:
                    logger.warning(f"Access denied for user {user.get('id')} - missing permission '{permission}'")
                    raise RoleException("FORBIDDEN", f"Thiếu quyền truy cập: {permission}")

            # Log successful access
            logger.debug(f"Permission access granted for user {user.get('id')} ({user_role}) to {func.__name__}")

            # Call the original function
            return await func(*args, **kwargs)

        return wrapper
    return decorator


# Factory function for easy role guard creation
def create_role_guard(*allowed_roles: str, **kwargs):
    """
    Factory function to create RoleGuardMiddleware instances.

    Args:
        *allowed_roles: Allowed roles
        **kwargs: Additional keyword arguments for RoleGuardMiddleware

    Returns:
        RoleGuardMiddleware instance
    """
    return lambda app: RoleGuardMiddleware(
        app,
        allowed_roles=list(allowed_roles),
        **kwargs
    )


# Usage examples:
#
# # Global role guard middleware
# app.add_middleware(RoleGuardMiddleware, allowed_roles=["user", "admin"])
#
# # Decorator-based role checking
# @app.get("/admin")
# @require_role("admin")
# async def admin_only(request: Request):
#     return {"message": "Admin access granted"}
#
# # Permission-based decorator
# @app.delete("/users/{user_id}")
# @require_permission("delete", "manage_users")
# async def delete_user(request: Request, user_id: int):
#     return {"message": f"User {user_id} deleted"}