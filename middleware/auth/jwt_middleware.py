"""
JWT Authentication Middleware v2.0 cho WEB Final API

Triển khai JWT Authentication Guard cho API v1:
- Kiểm tra Access Token trong Authorization header
- Validate token format và signature
- Attach user information vào request.state
- Support refresh token mechanism
- Token blacklist support
"""


import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

import jwt
import redis
from fastapi import Request, Response, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

# Safe import with fallback
try:
    from ..config.settings import MiddlewareSettings
except ImportError:
    # Fallback for standalone usage
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config.settings import MiddlewareSettings


logger = logging.getLogger(__name__)


class AuthException(HTTPException):
    """Custom exception cho Authentication"""

    def __init__(self, error_code: str, message: str, status_code: int = status.HTTP_401_UNAUTHORIZED):
        headers = {}
        super().__init__(
            status_code=status_code,
            headers=headers
        )

        # Format theo chuẩn response mới
        self.detail = {
            "success": False,
            "message": message,
            "error_code": error_code,
            "data": None
        }


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """
    JWT Authentication Middleware v2.0 cho WEB Final API

    Validates JWT tokens từ Authorization header và đính kèm thông tin user
    vào request.state cho downstream processing.

    Features:
    - Extract JWT token từ Authorization header (Bearer <token>)
    - Verify token signature và expiration
    - Check token trong blacklist (cho logout)
    - Decode token và attach user info vào request.state.user
    - Handle errors: MISSING_TOKEN, INVALID_TOKEN, TOKEN_EXPIRED, TOKEN_REVOKED
    - Support cả Access Token và Refresh Token validation
    """

    def __init__(
        self,
        app,
        settings: MiddlewareSettings = None,
        excluded_paths: Optional[list] = None,
        redis_client: Optional[redis.Redis] = None,
        verify_token_type: str = "access",  # "access" hoặc "refresh"
    ):
        """
        Initialize JWT Authentication Middleware v2.0

        Args:
            app: FastAPI application instance
            settings: Middleware settings object
            excluded_paths: Paths excluded from authentication
            redis_client: Redis client for token blacklist
            verify_token_type: Type of token to verify ("access" or "refresh")
        """
        super().__init__(app)
        self.settings = settings or MiddlewareSettings()
        self.redis_client = redis_client
        self.verify_token_type = verify_token_type

        # Excluded paths cho API v1
        self.excluded_paths = excluded_paths or [
            "/health",
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/forgot-password",
            "/api/v1/auth/reset-password",
            "/api/v1/auth/refresh-token",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/favicon.ico",
            "/static",
        ]

        # Security settings
        self.secret_key = self.settings.secret_key
        self.algorithm = self.settings.algorithm
        self.access_token_expire_minutes = self.settings.access_token_expire_minutes

    async def dispatch(self, request: Request, call_next):
        """
        Xử lý incoming request và validate JWT token

        Args:
            request: HTTP request cần xử lý
            call_next: Middleware tiếp theo trong chuỗi

        Returns:
            HTTP response với user information hoặc error response
        """
        # Bỏ qua authentication cho excluded paths
        if self._is_excluded_path(request.url.path):
            return await call_next(request)

        try:
            # Extract token từ Authorization header
            token = self._extract_token(request)
            if not token:
                raise AuthException("AUTH_001", "Thiếu Access Token trong header Authorization: Bearer <token>")

            # Check nếu token bị blacklist
            if await self._is_token_blacklisted(token):
                raise AuthException("AUTH_002", "Token đã bị thu hồi (logout)")

            # Validate và decode token
            payload = self._validate_token(token)

            # Attach user info vào request state
            self._attach_user_info(request, payload, token)

            # Log successful authentication
            logger.debug(f"User authenticated: {payload.get('email', 'unknown')} for {request.url.path}")

            # Tiếp tục middleware chain
            return await call_next(request)

        except AuthException:
            # Re-raise custom auth exceptions
            raise
        except jwt.ExpiredSignatureError:
            logger.warning(f"Token expired cho request: {request.url.path}")
            raise AuthException("AUTH_003", "Access Token đã hết hạn")
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token cho request: {request.url.path}, error: {str(e)}")
            raise AuthException("AUTH_004", "Access Token không hợp lệ")
        except Exception as e:
            logger.error(f"Lỗi không mong đợi trong JWT middleware: {str(e)}")
            raise AuthException("AUTH_005", "Lỗi server nội bộ", status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _is_excluded_path(self, path: str) -> bool:
        """
        Kiểm tra path có nên được loại trừ khỏi authentication không

        Args:
            path: Request path

        Returns:
            True nếu path nên được loại trừ
        """
        # Kiểm tra exact matches
        if path in self.excluded_paths:
            return True

        # Kiểm tra prefix matches cho static files, etc.
        for excluded_path in self.excluded_paths:
            if excluded_path.endswith('/') and path.startswith(excluded_path):
                return True
            if excluded_path.endswith('*') and path.startswith(excluded_path[:-1]):
                return True

        return False

    def _extract_token(self, request: Request) -> Optional[str]:
        """
        Extract JWT token từ Authorization header

        Expected format: Authorization: Bearer <token>

        Args:
            request: FastAPI request object

        Returns:
            JWT token string hoặc None nếu không tìm thấy
        """
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return None

        # Kiểm tra header format
        if not auth_header.startswith("Bearer "):
            logger.warning(f"Invalid Authorization header format: {auth_header[:20]}...")
            return None

        # Extract token sau "Bearer "
        token = auth_header[7:].strip()  # Remove "Bearer " và trim spaces

        if not token:
            logger.warning("Empty token trong Authorization header")
            return None

        return token

    def _validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate JWT token và return payload

        Args:
            token: JWT token string

        Returns:
            Token payload dictionary

        Raises:
            jwt.ExpiredSignatureError: Token đã hết hạn
            jwt.InvalidTokenError: Token không hợp lệ
        """
        try:
            # Decode và verify token
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iat": True,
                    "require": ["exp", "iat", "sub"]
                }
            )

            # Validate required payload fields cho API v1
            required_fields = ["user_id", "email", "role_id"]
            for field in required_fields:
                if field not in payload:
                    logger.error(f"Token missing required field: {field}")
                    raise jwt.InvalidTokenError(f"Token missing required field: {field}")

            # Validate token type
            if self.verify_token_type == "access" and payload.get("token_type") != "access":
                raise jwt.InvalidTokenError("Invalid token type. Expected access token.")
            elif self.verify_token_type == "refresh" and payload.get("token_type") != "refresh":
                raise jwt.InvalidTokenError("Invalid token type. Expected refresh token.")

            return payload

        except jwt.ExpiredSignatureError:
            # Let caller handle this
            raise
        except jwt.InvalidTokenError as e:
            logger.warning(f"Token validation failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Lỗi không mong đợi trong token validation: {str(e)}")
            raise jwt.InvalidTokenError("Token validation failed")

    async def _is_token_blacklisted(self, token: str) -> bool:
        """
        Kiểm tra token có trong blacklist không (cho logout feature)

        Args:
            token: JWT token cần kiểm tra

        Returns:
            True nếu token trong blacklist, False ngược lại
        """
        if not self.redis_client:
            # Nếu Redis không available, skip blacklist check (fail-open)
            return False

        try:
            blacklist_key = f"blacklist:{token}"
            is_blacklisted = self.redis_client.exists(blacklist_key)
            return bool(is_blacklisted)
        except Exception as e:
            logger.error(f"Lỗi khi kiểm tra token blacklist: {str(e)}")
            # Nếu Redis fails, allow request (fail-open strategy)
            return False

    def _attach_user_info(self, request: Request, payload: Dict[str, Any], token: str):
        """
        Đính kèm thông tin user vào request state

        Args:
            request: FastAPI request object
            payload: Decoded JWT token payload
            token: Raw JWT token string
        """
        # Extract user info từ payload theo API v1 format
        user_info = {
            "id": payload.get("user_id"),
            "email": payload.get("email"),
            "role_id": payload.get("role_id", "user"),
            "full_name": payload.get("full_name"),
            "avatar": payload.get("avatar"),
            "iat": payload.get("iat"),
            "exp": payload.get("exp"),
            "jti": payload.get("jti"),
            "token_type": payload.get("token_type", "access")
        }

        # Đính kèm user info vào request.state
        request.state.user = user_info
        request.state.token = token

        logger.debug(f"User authenticated: {user_info['email']} (ID: {user_info['id']}, Role: {user_info['role_id']})")

    def get_current_user(self, request: Request) -> Optional[Dict[str, Any]]:
        """
        Helper để lấy current user từ request state

        Args:
            request: FastAPI request object

        Returns:
            User information dictionary hoặc None
        """
        return getattr(request.state, "user", None)

    def is_authenticated(self, request: Request) -> bool:
        """
        Kiểm tra request có được authenticated không

        Args:
            request: FastAPI request object

        Returns:
            True nếu authenticated, False ngược lại
        """
        return hasattr(request.state, "user") and request.state.user is not None


# Decorators cho convenience

def require_auth(func):
    """
    Decorator để yêu cầu authentication cho route

    Usage:
        @require_auth
        async def protected_route(request: Request):
            user = request.state.user
            return {"message": "Hello, authenticated user!"}
    """
    def wrapper(*args, **kwargs):
        request = None
        for arg in args:
            if isinstance(arg, Request):
                request = arg
                break

        if request and not hasattr(request.state, 'user'):
            raise AuthException("AUTH_001", "Yêu cầu xác thực")

        return func(*args, **kwargs)
    return wrapper


def require_role(*allowed_roles: str):
    """
    Decorator để yêu cầu specific user roles cho route

    Usage:
        @require_role("admin", "moderator")
        async def admin_route(request: Request):
            return {"message": "Admin access granted"}
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if not request or not hasattr(request.state, 'user'):
                raise AuthException("AUTH_001", "Yêu cầu xác thực")

            user_role = request.state.user.get("role_id", "user")
            if user_role not in allowed_roles:
                raise AuthException("AUTH_006", "Bạn không có quyền truy cập", status.HTTP_403_FORBIDDEN)

            return func(*args, **kwargs)
        return wrapper
    return decorator


# Factory function cho việc tạo JWT middleware instances
def create_jwt_middleware(**kwargs):
    """
    Factory function để tạo JWT authentication middleware

    Args:
        **kwargs: Additional arguments cho JWTAuthMiddleware

    Returns:
        JWTAuthMiddleware instance
    """
    return lambda app: JWTAuthMiddleware(app, **kwargs)


# Helper functions cho convenience
def get_current_user(request: Request) -> Optional[Dict[str, Any]]:
    """
    Helper function để lấy current user từ request

    Args:
        request: FastAPI request object

    Returns:
        User information dictionary hoặc None
    """
    return getattr(request.state, "user", None)


def get_current_user_id(request: Request) -> Optional[int]:
    """
    Helper function để lấy current user ID

    Args:
        request: FastAPI request object

    Returns:
        User ID hoặc None
    """
    user = get_current_user(request)
    return user.get("id") if user else None