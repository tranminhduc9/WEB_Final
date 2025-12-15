"""
Middleware xác thực người dùng - JWT Authentication

Module này cung cấp các chức năng xác thực JWT token,
quản lý phiên đăng nhập và phân quyền người dùng.
Logic giữ ổn định qua các phiên bản.
"""

import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
import os

logger = logging.getLogger(__name__)

# Cấu hình JWT - Lấy từ environment variables
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "hanoi-travel-default-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION = 3600  # 1 giờ
REFRESH_TOKEN_EXPIRATION = 7 * 24 * 3600  # 7 ngày

security = HTTPBearer()


class JWTAuthMiddleware:
    """
    Middleware xác thực JWT token

    Cung cấp các chức năng:
    - Xác thực JWT token
    - Tạo access token và refresh token
    - Quản lý phiên người dùng
    - Xử lý lỗi xác thực thống nhất
    """

    def __init__(self, secret_key: str = None, algorithm: str = "HS256"):
        """
        Khởi tạo middleware xác thực

        Args:
            secret_key: Khóa bí mật cho JWT
            algorithm: Thuật toán mã hóa JWT
        """
        self.secret_key = secret_key or JWT_SECRET_KEY
        self.algorithm = algorithm

    def hash_password(self, password: str) -> str:
        """
        Mã hóa mật khẩu người dùng

        Args:
            password: Mật khẩu gốc

        Returns:
            str: Mật khẩu đã mã hóa bằng bcrypt
        """
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Kiểm tra mật khẩu

        Args:
            password: Mật khẩu người dùng nhập
            hashed_password: Mật khẩu đã hash trong database

        Returns:
            bool: True nếu mật khẩu đúng
        """
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

    def create_access_token(self, user_data: Dict[str, Any], expires_delta: int = None) -> str:
        """
        Tạo JWT access token

        Args:
            user_data: Thông tin người dùng
            expires_delta: Thời gian hết hạn tùy chỉnh

        Returns:
            str: JWT access token
        """
        now = datetime.utcnow()
        exp = expires_delta or JWT_EXPIRATION

        payload = {
            "sub": str(user_data.get("id")),
            "email": user_data.get("email"),
            "role": user_data.get("role", "user"),
            "iat": now,
            "exp": now + timedelta(seconds=exp),
            "type": "access"
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, user_data: Dict[str, Any]) -> str:
        """
        Tạo refresh token

        Args:
            user_data: Thông tin người dùng

        Returns:
            str: JWT refresh token
        """
        now = datetime.utcnow()
        payload = {
            "sub": str(user_data.get("id")),
            "email": user_data.get("email"),
            "role": user_data.get("role", "user"),
            "iat": now,
            "exp": now + timedelta(seconds=REFRESH_TOKEN_EXPIRATION),
            "type": "refresh"
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    async def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """
        Xác thực JWT token

        Args:
            token: JWT token cần xác thực
            token_type: Loại token ("access" hoặc "refresh")

        Returns:
            Dict: Payload của token

        Raises:
            HTTPException: Nếu token không hợp lệ
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )

            # Kiểm tra loại token
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Token type mismatch. Expected {token_type}"
                )

            # Kiểm tra token có hết hạn không
            if datetime.utcnow() > datetime.fromtimestamp(payload.get("exp", 0)):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token đã hết hạn"
                )

            return payload

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token đã hết hạn"
            )
        except jwt.InvalidTokenError as e:
            logger.warning(f"Token không hợp lệ: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token không hợp lệ"
            )

    async def get_current_user_from_request(self, request: Request) -> Optional[Dict[str, Any]]:
        """
        Lấy thông tin người dùng hiện tại từ request

        Args:
            request: FastAPI Request object

        Returns:
            Dict: Thông tin người dùng hoặc None nếu chưa đăng nhập
        """
        try:
            # Lấy token từ Authorization header
            authorization = request.headers.get("Authorization")
            if not authorization:
                return None

            # Tách token từ "Bearer <token>"
            if not authorization.startswith("Bearer "):
                return None

            token = authorization[7:]
            payload = await self.verify_token(token, "access")

            return {
                "user_id": payload.get("sub"),
                "email": payload.get("email"),
                "role": payload.get("role"),
                "exp": payload.get("exp")
            }

        except Exception as e:
            logger.warning(f"Lỗi khi xác thực người dùng: {str(e)}")
            return None


# Instance toàn cục
auth_middleware = JWTAuthMiddleware()


# FastAPI Dependencies
async def get_current_user(request: Request) -> Dict[str, Any]:
    """
    Dependency để lấy user hiện tại (bắt buộc phải đăng nhập)
    """
    user = await auth_middleware.get_current_user_from_request(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Vui lòng đăng nhập để tiếp tục",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user


async def get_optional_user(request: Request) -> Optional[Dict[str, Any]]:
    """
    Dependency để lấy user hiện tại (tùy chọn - không báo lỗi nếu chưa đăng nhập)
    """
    return await auth_middleware.get_current_user_from_request(request)


def require_roles(required_roles: List[str]):
    """
    Decorator yêu cầu người dùng có vai trò cụ thể

    Args:
        required_roles: Danh sách các vai trò được phép
    """
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            user = await auth_middleware.get_current_user_from_request(request)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Vui lòng đăng nhập để tiếp tục"
                )

            user_role = user.get("role", "user")
            if user_role not in required_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Không đủ quyền truy cập. Vai trò yêu cầu: {required_roles}"
                )

            # Thêm thông tin user vào request state
            request.state.user = user
            return await func(request, *args, **kwargs)

        return wrapper
    return decorator


# Decorators thông dụng
require_admin = require_roles(["admin"])
require_moderator = require_roles(["admin", "moderator"])
require_user = require_roles(["admin", "moderator", "user"])


class RoleGuard:
    """
    Lớp kiểm tra quyền truy cập dựa trên vai trò
    """

    @staticmethod
    def has_permission(user_role: str, required_roles: List[str]) -> bool:
        """
        Kiểm tra user có quyền truy cập không

        Args:
            user_role: Vai trò của user
            required_roles: Danh sách vai trò yêu cầu

        Returns:
            bool: True nếu có quyền
        """
        return user_role in required_roles

    @staticmethod
    def can_access_resource(user_role: str, resource_owner_id: str, current_user_id: str) -> bool:
        """
        Kiểm tra user có thể truy cập resource không (chủ sở hữu hoặc admin)

        Args:
            user_role: Vai trò của user
            resource_owner_id: ID chủ sở hữu resource
            current_user_id: ID user hiện tại

        Returns:
            bool: True nếu có quyền
        """
        return user_role == "admin" or str(resource_owner_id) == str(current_user_id)


# Hàm tiện ích
def is_token_expired(payload: Dict[str, Any]) -> bool:
    """
    Kiểm tra token có hết hạn không

    Args:
        payload: Payload của JWT token

    Returns:
        bool: True nếu hết hạn
    """
    exp_timestamp = payload.get("exp")
    if not exp_timestamp:
        return True

    # Handle both timestamp (int) and datetime objects
    if isinstance(exp_timestamp, (int, float)):
        exp_datetime = datetime.fromtimestamp(exp_timestamp)
    else:
        exp_datetime = exp_timestamp

    return datetime.utcnow() > exp_datetime


def extract_user_info(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Trích xuất thông tin user từ JWT payload

    Args:
        payload: JWT payload

    Returns:
        Dict: Thông tin user
    """
    return {
        "user_id": payload.get("sub"),
        "email": payload.get("email"),
        "role": payload.get("role", "user"),
        "exp": payload.get("exp"),
        "iat": payload.get("iat")
    }