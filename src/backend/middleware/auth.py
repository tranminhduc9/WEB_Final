"""
Middleware xác thực người dùng - JWT Authentication

Module này cung cấp các chức năng xác thực JWT token,
quản lý phiên đăng nhập và phân quyền người dùng.
Logic giữ ổn định qua các phiên bản.
"""

import jwt
import bcrypt
import hashlib
import time
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
import os
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

# Cấu hình JWT - Lấy từ environment variables
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "hanoi-travel-default-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION = 3600  # 1 giờ
REFRESH_TOKEN_EXPIRATION = 7 * 24 * 3600  # 7 ngày

# Enhanced Security Configuration
MAX_LOGIN_ATTEMPTS = 5
ACCOUNT_LOCKOUT_DURATION = 900  # 15 minutes
PASSWORD_MIN_LENGTH = 8
PASSWORD_REQUIRE_UPPERCASE = True
PASSWORD_REQUIRE_LOWERCASE = True
PASSWORD_REQUIRE_DIGIT = True
PASSWORD_REQUIRE_SPECIAL = True
SESSION_TIMEOUT = 1800  # 30 minutes

# Rate limiting configuration
AUTH_RATE_LIMIT = 10  # requests per minute
AUTH_RATE_WINDOW = 60  # seconds

security = HTTPBearer()


class FailedAttemptTracker:
    """Track failed login attempts with memory storage"""

    def __init__(self):
        self.failed_attempts = defaultdict(list)
        self.locked_accounts = {}

    def add_failed_attempt(self, identifier: str, ip_address: str = None):
        """Add a failed attempt"""
        key = f"{identifier}:{ip_address}" if ip_address else identifier
        self.failed_attempts[key].append(time.time())

        # Clean old attempts (older than 1 hour)
        cutoff = time.time() - 3600
        self.failed_attempts[key] = [
            attempt for attempt in self.failed_attempts[key]
            if attempt > cutoff
        ]

    def get_failed_attempts(self, identifier: str, ip_address: str = None) -> int:
        """Get number of failed attempts"""
        key = f"{identifier}:{ip_address}" if ip_address else identifier
        cutoff = time.time() - ACCOUNT_LOCKOUT_DURATION
        return len([
            attempt for attempt in self.failed_attempts[key]
            if attempt > cutoff
        ])

    def is_account_locked(self, identifier: str) -> Tuple[bool, Optional[int]]:
        """Check if account is locked and return remaining time"""
        if identifier in self.locked_accounts:
            lock_expiry = self.locked_accounts[identifier]
            if time.time() < lock_expiry:
                remaining = int(lock_expiry - time.time())
                return True, remaining
            else:
                # Lock expired, remove it
                del self.locked_accounts[identifier]
        return False, None

    def lock_account(self, identifier: str):
        """Lock an account"""
        self.locked_accounts[identifier] = time.time() + ACCOUNT_LOCKOUT_DURATION
        logger.warning(f"Account {identifier} locked due to too many failed attempts")

    def clear_failed_attempts(self, identifier: str, ip_address: str = None):
        """Clear failed attempts after successful login"""
        key = f"{identifier}:{ip_address}" if ip_address else identifier
        if key in self.failed_attempts:
            del self.failed_attempts[key]


class PasswordValidator:
    """Enhanced password validation"""

    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, List[str]]:
        """
        Validate password strength

        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_errors)
        """
        errors = []

        # Length check
        if len(password) < PASSWORD_MIN_LENGTH:
            errors.append(f"Password must be at least {PASSWORD_MIN_LENGTH} characters long")

        # Uppercase check
        if PASSWORD_REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")

        # Lowercase check
        if PASSWORD_REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")

        # Digit check
        if PASSWORD_REQUIRE_DIGIT and not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")

        # Special character check
        if PASSWORD_REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")

        # Common password check
        common_passwords = [
            'password', '123456', '123456789', 'qwerty', 'abc123',
            'password123', 'admin', 'letmein', 'welcome', 'monkey'
        ]
        if password.lower() in common_passwords:
            errors.append("Password is too common. Please choose a stronger password")

        return len(errors) == 0, errors


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
        self.failed_tracker = FailedAttemptTracker()
        self.rate_limiter = defaultdict(deque)  # Simple in-memory rate limiter

    def hash_password(self, password: str) -> str:
        """
        Mã hóa mật khẩu người dùng với enhanced security

        Args:
            password: Mật khẩu gốc

        Returns:
            str: Mật khẩu đã mã hóa bằng bcrypt với increased rounds
        """
        # bcrypt has a 72-byte limit, truncate long passwords but maintain security
        if len(password.encode('utf-8')) > 72:
            # Use SHA-256 hash of long password, then take first 72 bytes
            import hashlib
            password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
            password = password_hash[:72]  # Take first 72 chars of hash

        # Increased rounds for better security
        salt = bcrypt.gensalt(rounds=12)
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
        # Apply same truncation logic as hash_password for consistency
        if len(password.encode('utf-8')) > 72:
            import hashlib
            password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
            password = password_hash[:72]

        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

    async def check_rate_limit(self, identifier: str) -> bool:
        """Check if identifier has exceeded rate limit"""
        now = time.time()
        cutoff = now - AUTH_RATE_WINDOW

        # Clean old requests
        while self.rate_limiter[identifier] and self.rate_limiter[identifier][0] < cutoff:
            self.rate_limiter[identifier].popleft()

        # Check if under limit
        if len(self.rate_limiter[identifier]) >= AUTH_RATE_LIMIT:
            return False

        # Add current request
        self.rate_limiter[identifier].append(now)
        return True

    async def authenticate_user(
        self,
        email: str,
        password: str,
        request: Request,
        user_lookup_func: callable
    ) -> Dict[str, Any]:
        """
        Enhanced user authentication with security checks

        Args:
            email: User email
            password: User password
            request: FastAPI request object
            user_lookup_func: Function to lookup user and verify password

        Returns:
            Dict: Authentication result with tokens and user info

        Raises:
            HTTPException: For various authentication failures
        """
        ip_address = request.client.host if request.client else "unknown"

        # Rate limiting check
        if not await self.check_rate_limit(f"auth:{ip_address}"):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many authentication attempts. Please try again later."
            )

        # Account lockout check
        is_locked, remaining_time = self.failed_tracker.is_account_locked(email)
        if is_locked:
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"Account locked due to too many failed attempts. Try again in {remaining_time} seconds."
            )

        try:
            # Lookup user and verify password
            user = await user_lookup_func(email, password)
            if not user:
                # Add failed attempt
                self.failed_tracker.add_failed_attempt(email, ip_address)
                failed_count = self.failed_tracker.get_failed_attempts(email, ip_address)

                if failed_count >= MAX_LOGIN_ATTEMPTS:
                    self.failed_tracker.lock_account(email)

                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )

            # Clear failed attempts on successful login
            self.failed_tracker.clear_failed_attempts(email, ip_address)

            # Create tokens
            access_token = self.create_access_token(user)
            refresh_token = self.create_refresh_token(user)

            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": JWT_EXPIRATION,
                "user": user
            }

        except Exception as e:
            logger.error(f"Authentication error for {email}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service unavailable"
            )

    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token"""
        try:
            # Verify refresh token
            payload = await self.verify_token(refresh_token, "refresh")

            # Create new access token
            user_data = {
                "id": payload["sub"],
                "email": payload["email"],
                "role": payload["role"]
            }

            new_access_token = self.create_access_token(user_data)

            return {
                "access_token": new_access_token,
                "token_type": "bearer",
                "expires_in": JWT_EXPIRATION
            }

        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

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
            "type": "access",
            "iss": "hanoi-travel",
            "aud": "hanoi-travel-users"
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
            "type": "refresh",
            "iss": "hanoi-travel",
            "aud": "hanoi-travel-users"
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
                algorithms=[self.algorithm],
                audience="hanoi-travel-users",
                issuer="hanoi-travel"
            )

            # Validate token type
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Token type mismatch. Expected {token_type}"
                )

            # Check expiration
            if datetime.utcnow() > datetime.fromtimestamp(payload.get("exp", 0)):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token đã hết hạn"
                )

            # Validate subject
            if not payload.get("sub"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing subject"
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
        except HTTPException:
            # Re-raise existing HTTPExceptions
            raise
        except Exception as e:
            logger.error(f"Unexpected error during token verification: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token verification failed"
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
    Enhanced dependency để lấy user hiện tại (bắt buộc phải đăng nhập)
    """
    # Rate limiting check for auth endpoints
    ip_address = request.client.host if request.client else "unknown"
    if not await auth_middleware.check_rate_limit(f"auth_check:{ip_address}"):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many authentication checks. Please try again later."
        )

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


async def require_active_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Require user to be active
    """
    if current_user.get("status") == "inactive":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not active"
        )
    return current_user


def validate_user_password(password: str) -> Tuple[bool, List[str]]:
    """
    Validate user password strength

    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_errors)
    """
    return PasswordValidator.validate_password_strength(password)


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


# Enhanced role decorators using FastAPI dependencies
def require_role(required_roles: List[str]):
    """Enhanced role requirement decorator using FastAPI dependencies"""
    def role_checker(current_user: Dict[str, Any] = Depends(require_active_user)):
        user_role = current_user.get("role", "user")
        if user_role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(required_roles)}"
            )
        return current_user
    return role_checker


# Enhanced role decorators
require_admin = require_role(["admin"])
require_moderator = require_role(["admin", "moderator"])
require_user = require_role(["admin", "moderator", "user"])


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


# Security Headers Middleware
async def add_security_headers(request: Request, call_next):
    """
    Add security headers to responses for enhanced security
    """
    response = await call_next(request)

    security_headers = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }

    for header, value in security_headers.items():
        response.headers[header] = value

    return response