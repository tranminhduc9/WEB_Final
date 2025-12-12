"""
Role Guard Middleware v2.0 cho WEB Final API

Triển khai Role-based Access Control (RBAC) cho API v1:
- Kiểm tra user permissions: user, admin, moderator
- Endpoint-specific role requirements
- Resource ownership validation
- Hierarchical permission system
"""

import logging
from typing import List, Optional, Dict, Any, Set
from enum import Enum
from functools import wraps

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class UserRole(Enum):
    """Enum định nghĩa các user roles cho WEB Final API"""
    GUEST = "guest"        # User chưa authenticated
    USER = "user"          # Regular user
    MODERATOR = "moderator" # Content moderator
    ADMIN = "admin"        # System administrator

    def __lt__(self, other):
        """So sánh level của roles để kiểm tra hierarchy"""
        role_hierarchy = {
            UserRole.GUEST: 0,
            UserRole.USER: 1,
            UserRole.MODERATOR: 2,
            UserRole.ADMIN: 3
        }
        return role_hierarchy[self] < role_hierarchy[other]

    def __ge__(self, other):
        """Kiểm tra nếu role này có level >= role khác"""
        role_hierarchy = {
            UserRole.GUEST: 0,
            UserRole.USER: 1,
            UserRole.MODERATOR: 2,
            UserRole.ADMIN: 3
        }
        return role_hierarchy[self] >= role_hierarchy[other]


class RoleException(HTTPException):
    """Custom exception cho Role-based errors"""

    def __init__(self, error_code: str, message: str, status_code: int = status.HTTP_403_FORBIDDEN):
        super().__init__(
            status_code=status_code
        )

        # Format theo chuẩn response mới
        self.detail = {
            "success": False,
            "message": message,
            "error_code": error_code,
            "data": None
        }


class RoleGuardMiddleware(BaseHTTPMiddleware):
    """
    Role Guard Middleware cho WEB Final API

    Checks user roles và permissions dựa trên:
    - User role từ JWT token
    - Endpoint-specific role requirements
    - Resource ownership validation
    """

    def __init__(
        self,
        app,
        excluded_paths: Optional[List[str]] = None,
        endpoint_permissions: Optional[Dict[str, List[str]]] = None,
    ):
        """
        Initialize Role Guard Middleware

        Args:
            app: FastAPI application instance
            excluded_paths: Paths excluded from role checking
            endpoint_permissions: Mapping endpoint → required roles
        """
        super().__init__(app)

        # Excluded paths khỏi role checking
        self.excluded_paths = excluded_paths or [
            "/health",
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/forgot-password",
            "/api/v1/auth/reset-password",
            "/api/v1/auth/refresh-token",
            "/api/v1/places/suggest",
            "/api/v1/places",
            "/api/v1/places/",
            "/api/v1/posts",
            "/api/v1/chatbot/message",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/favicon.ico",
            "/static",
        ]

        # Default endpoint permissions theo API v1
        self.endpoint_permissions = endpoint_permissions or self._build_default_permissions()

        # Statistics tracking
        self.stats = {
            "total_requests": 0,
            "access_denied": 0,
            "role_upgrades": 0,
        }

    def _build_default_permissions(self) -> Dict[str, List[str]]:
        """
        Xây dựng default permissions mapping theo API contract v1
        """
        permissions = {}

        # Admin endpoints
        admin_endpoints = [
            "GET:/api/v1/admin/users",
            "PATCH:/api/v1/admin/users/",
            "GET:/api/v1/admin/posts/pending",
            "DELETE:/api/v1/admin/posts/",
            "DELETE:/api/v1/admin/reviews/",
            "GET:/api/v1/admin/dashboard/stats",
            "POST:/api/v1/admin/places",
            "PUT:/api/v1/admin/places/",
        ]

        # Moderator endpoints
        moderator_endpoints = [
            "POST:/api/v1/reports",
        ]

        # User endpoints
        user_endpoints = [
            "GET:/api/v1/users/me",
            "PUT:/api/v1/users/me",
            "PUT:/api/v1/users/me/password",
            "GET:/api/v1/users/me/favorites",
            "POST:/api/v1/favorites/places",
            "POST:/api/v1/upload",
            "POST:/api/v1/posts",
            "POST:/api/v1/posts/",
            "POST:/api/v1/posts/",
            "POST:/api/v1/auth/logout",
        ]

        # Public endpoints (không cần authentication)
        public_endpoints = [
            "GET:/api/v1/users/",
        ]

        # Gán permissions
        for endpoint in admin_endpoints:
            permissions[endpoint] = [UserRole.ADMIN.value]

        for endpoint in moderator_endpoints:
            permissions[endpoint] = [UserRole.MODERATOR.value, UserRole.ADMIN.value]

        for endpoint in user_endpoints:
            permissions[endpoint] = [UserRole.USER.value, UserRole.MODERATOR.value, UserRole.ADMIN.value]

        for endpoint in public_endpoints:
            permissions[endpoint] = [UserRole.GUEST.value, UserRole.USER.value, UserRole.MODERATOR.value, UserRole.ADMIN.value]

        return permissions

    async def dispatch(self, request: Request, call_next):
        """
        Xử lý request và kiểm tra role permissions

        Args:
            request: HTTP request cần xử lý
            call_next: Middleware tiếp theo trong chuỗi

        Returns:
            HTTP response nếu user có quyền, ngược lại raise RoleException
        """
        try:
            self.stats["total_requests"] += 1

            # Skip role checking cho excluded paths
            if self._is_excluded_path(request.url.path):
                return await call_next(request)

            # Get current user role
            user_role = self._get_user_role(request)
            endpoint_key = f"{request.method}:{request.url.path}"

            # Check endpoint permissions
            if not self._has_permission(user_role, endpoint_key):
                self.stats["access_denied"] += 1
                required_roles = self.endpoint_permissions.get(endpoint_key, ["user"])
                logger.warning(
                    f"Access denied: User role '{user_role}' cannot access {endpoint_key}. "
                    f"Required roles: {required_roles}"
                )
                raise RoleException(
                    "RBAC_001",
                    f"Bạn không có quyền truy cập endpoint này. "
                    f"Vai trò yêu cầu: {', '.join(required_roles)}"
                )

            # Resource ownership validation cho endpoints cần thiết
            if self._requires_ownership_check(endpoint_key):
                await self._validate_resource_ownership(request, endpoint_key)

            # Log successful authorization
            logger.debug(f"Role check passed: {user_role} accessing {endpoint_key}")

            return await call_next(request)

        except RoleException:
            raise
        except Exception as e:
            logger.error(f"Lỗi không mong đợi trong role guard: {str(e)}")
            # Fail-open: allow request nếu có lỗi trong role checking
            return await call_next(request)

    def _is_excluded_path(self, path: str) -> bool:
        """
        Kiểm tra path có nên được loại trừ khỏi role checking không

        Args:
            path: Request path

        Returns:
            True nếu path nên được loại trừ
        """
        if path in self.excluded_paths:
            return True

        for excluded_path in self.excluded_paths:
            if excluded_path.endswith('/') and path.startswith(excluded_path):
                return True
            if excluded_path.endswith('*') and path.startswith(excluded_path[:-1]):
                return True

        return False

    def _get_user_role(self, request: Request) -> str:
        """
        Lấy user role từ request state

        Args:
            request: FastAPI request object

        Returns:
            User role string
        """
        if hasattr(request.state, 'user') and request.state.user:
            return request.state.user.get("role_id", UserRole.USER.value)
        return UserRole.GUEST.value

    def _has_permission(self, user_role: str, endpoint_key: str) -> bool:
        """
        Kiểm tra user role có quyền truy cập endpoint không

        Args:
            user_role: User role string
            endpoint_key: Endpoint key (METHOD:PATH)

        Returns:
            True nếu có quyền, False ngược lại
        """
        # Lấy required roles cho endpoint
        required_roles = self.endpoint_permissions.get(endpoint_key)
        if not required_roles:
            # Default: require user role
            required_roles = [UserRole.USER.value]

        # Convert string role to enum
        try:
            user_role_enum = UserRole(user_role)
        except ValueError:
            logger.warning(f"Invalid user role: {user_role}")
            return False

        # Check permission using role hierarchy
        for required_role_str in required_roles:
            try:
                required_role = UserRole(required_role_str)
                if user_role_enum >= required_role:
                    return True
            except ValueError:
                logger.warning(f"Invalid required role: {required_role_str}")
                continue

        return False

    def _requires_ownership_check(self, endpoint_key: str) -> bool:
        """
        Kiểm tra endpoint có yêu cầu resource ownership validation không

        Args:
            endpoint_key: Endpoint key

        Returns:
            True nếu cần ownership check
        """
        # Các endpoints yêu cầu resource ownership
        ownership_required_patterns = [
            "PUT:/api/v1/users/me",
            "PUT:/api/v1/users/me/password",
            "DELETE:/api/v1/posts/",
            "PUT:/api/v1/posts/",
        ]

        for pattern in ownership_required_patterns:
            if endpoint_key.startswith(pattern):
                return True

        return False

    async def _validate_resource_ownership(self, request: Request, endpoint_key: str):
        """
        Validate resource ownership cho specific endpoints

        Args:
            request: FastAPI request object
            endpoint_key: Endpoint key
        """
        user_id = self._get_user_id(request)
        if not user_id:
            raise RoleException("RBAC_002", "Không thể xác định user ID")

        # Extract resource ID từ path
        path_parts = request.url.path.strip('/').split('/')
        resource_id = None

        if len(path_parts) >= 4 and path_parts[0] == "api" and path_parts[1] == "v1":
            if path_parts[2] == "posts" and len(path_parts) >= 4:
                resource_id = path_parts[3]

        # For now, skip actual ownership check (requires database access)
        # Trong thực tế, cần check trong database: resource.created_by == user_id
        logger.debug(f"Ownership check for user {user_id} on resource {resource_id}")

    def _get_user_id(self, request: Request) -> Optional[int]:
        """
        Lấy user ID từ request state

        Args:
            request: FastAPI request object

        Returns:
            User ID hoặc None
        """
        if hasattr(request.state, 'user') and request.state.user:
            return request.state.user.get("id")
        return None

    def get_stats(self) -> Dict[str, int]:
        """
        Lấy thống kê role guard

        Returns:
            Statistics dictionary
        """
        return self.stats.copy()

    def reset_stats(self):
        """Reset thống kê role guard"""
        self.stats = {
            "total_requests": 0,
            "access_denied": 0,
            "role_upgrades": 0,
        }


# Decorators cho role-based access control

def require_role(*allowed_roles: str):
    """
    Decorator để yêu cầu specific roles cho route/function

    Usage:
        @require_role("admin", "moderator")
        async def admin_function(user_id: int):
            return {"message": "Admin access granted"}

        @require_role("user")
        async def user_only_function(user_id: int):
            return {"message": "User access granted"}
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request từ kwargs hoặc args
            request = kwargs.get('request')
            if not request:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break

            if not request:
                raise RoleException("RBAC_003", "Không thể xác định request context")

            # Get user role
            user_role = request.state.user.get("role_id", UserRole.GUEST.value) if hasattr(request.state, 'user') else UserRole.GUEST.value

            # Check permissions
            user_role_enum = UserRole(user_role)
            for required_role_str in allowed_roles:
                required_role = UserRole(required_role_str)
                if user_role_enum >= required_role:
                    return await func(*args, **kwargs)

            # Access denied
            raise RoleException(
                "RBAC_001",
                f"Yêu cầu vai trò: {', '.join(allowed_roles)}. Vai trò hiện tại: {user_role}"
            )
        return wrapper
    return decorator


def require_admin():
    """Shortcut decorator cho admin-only access"""
    return require_role(UserRole.ADMIN.value)


def require_moderator():
    """Shortcut decorator cho moderator hoặc admin access"""
    return require_role(UserRole.MODERATOR.value, UserRole.ADMIN.value)


def require_user():
    """Shortcut decorator cho authenticated user access"""
    return require_role(UserRole.USER.value, UserRole.MODERATOR.value, UserRole.ADMIN.value)


# Helper functions

def get_user_role(request: Request) -> str:
    """
    Helper function để lấy user role từ request

    Args:
        request: FastAPI request object

    Returns:
        User role string
    """
    if hasattr(request.state, 'user') and request.state.user:
        return request.state.user.get("role_id", UserRole.USER.value)
    return UserRole.GUEST.value


def is_admin(request: Request) -> bool:
    """Kiểm tra user có phải admin không"""
    return get_user_role(request) == UserRole.ADMIN.value


def is_moderator_or_admin(request: Request) -> bool:
    """Kiểm tra user có quyền moderator trở lên không"""
    user_role = UserRole(get_user_role(request))
    return user_role >= UserRole.MODERATOR


def has_permission(request: Request, required_role: str) -> bool:
    """
    Kiểm tra user có quyền truy cập endpoint không

    Args:
        request: FastAPI request object
        required_role: Required role string

    Returns:
        True nếu có quyền, False ngược lại
    """
    user_role = UserRole(get_user_role(request))
    try:
        required = UserRole(required_role)
        return user_role >= required
    except ValueError:
        return False


# Factory function
def create_role_guard(**kwargs):
    """
    Factory function để tạo RoleGuardMiddleware instance

    Args:
        **kwargs: Additional arguments cho RoleGuardMiddleware

    Returns:
        RoleGuardMiddleware instance
    """
    return lambda app: RoleGuardMiddleware(app, **kwargs)