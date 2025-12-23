"""
Middleware giới hạn tốc độ truy cập - Rate Limiting

Module này cung cấp các thuật toán rate limiting để ngăn chặn abuse,
bảo vệ API khỏi requests quá nhiều trong một khoảng thời gian.
Thuật toán giữ ổn định qua các phiên bản.
"""

import time
import asyncio
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status
from collections import defaultdict, deque
import logging
import hashlib
import os

logger = logging.getLogger(__name__)


class RateLimitConfig:
    """
    Cấu hình rate limit cho các endpoint khác nhau
    """

    # Mức độ rate limit (requests/minute) theo API contract
    RATE_LIMITS = {
        "high": 5,      # 5 req/phút - Login, Register, OTP
        "medium": 20,   # 20 req/phút - Write actions: Post, Comment
        "low": 100,     # 100 req/phút - Read actions: Search, Get Details
        "suggest": 200, # 200 req/phút - Places suggest endpoint
        "none": 1000    # Gần như không giới hạn
    }

    # Default limits cho các endpoint theo API contract
    DEFAULT_LIMITS = {
        # Authentication endpoints - High: 5 req/phút
        "POST:/api/v1/auth/register": ("high", 60),
        "POST:/api/v1/auth/login": ("high", 60),
        "POST:/api/v1/auth/forgot-password": ("high", 60),
        "POST:/api/v1/auth/reset-password": ("high", 60),
        "POST:/api/v1/auth/refresh-token": ("medium", 60),

        # Upload endpoints - Medium: 20 req/phút
        "POST:/api/v1/upload": ("medium", 60),

        # Places endpoints - Low: 100 req/phút, Suggest: 200 req/phút
        "GET:/api/v1/places/suggest": ("suggest", 60),  # Special: 200 req/phút
        "GET:/api/v1/places": ("low", 60),
        "GET:/api/v1/places/": ("low", 60),  # GET /places/{id}
        "GET:/api/v1/places/*/reviews": ("low", 60),  # GET /places/{id}/reviews

        # Posts endpoints - Read: Low, Write: Medium
        "GET:/api/v1/posts": ("low", 60),
        "POST:/api/v1/posts": ("medium", 20),  # 5 posts/giờ = ~20 req/phút
        "POST:/api/v1/posts/*/comments": ("medium", 60),
        "POST:/api/v1/posts/*/likes": ("medium", 60),

        # User endpoints - Medium: 20 req/phút
        "GET:/api/v1/users/me": ("medium", 60),
        "PUT:/api/v1/users/me": ("medium", 60),
        "PUT:/api/v1/users/me/password": ("medium", 60),
        "GET:/api/v1/users/me/favorites": ("medium", 60),
        "POST:/api/v1/favorites/places": ("medium", 60),
        "GET:/api/v1/users/*/profile": ("low", 60),

        # Report endpoints - Medium: 20 req/phút
        "POST:/api/v1/reports": ("medium", 60),

        # Chatbot endpoints - Medium: 20 req/phút
        "POST:/api/v1/chatbot/message": ("medium", 60),
        "GET:/api/v1/chatbot/history": ("medium", 60),

        # Admin endpoints - Medium: 20 req/phút (more restrictive)
        "GET:/api/v1/admin/users": ("medium", 60),
        "PATCH:/api/v1/admin/users/*/status": ("medium", 60),
        "GET:/api/v1/admin/posts/pending": ("medium", 60),
        "DELETE:/api/v1/admin/posts/*": ("medium", 60),
        "DELETE:/api/v1/admin/reviews/*": ("medium", 60),
        "GET:/api/v1/admin/dashboard/stats": ("medium", 60),
        "POST:/api/v1/admin/places": ("medium", 60),
        "PUT:/api/v1/admin/places/*": ("medium", 60),
        "DELETE:/api/v1/admin/places/*": ("medium", 60),
    }


class MemoryRateLimiter:
    """
    Rate Limiter sử dụng thuật toán Sliding Window với bộ nhớ RAM

    Thuật toán sliding window cho phép control chính xác hơn
    so với fixed window và hiệu quả cho distributed systems.
    """

    def __init__(self):
        """Khởi tạo rate limiter với bộ nhớ trong"""
        # Structure: {key: deque of timestamps}
        self._requests: Dict[str, deque] = defaultdict(deque)
        # Structure: {key: last_cleanup_time}
        self._last_cleanup: Dict[str, float] = defaultdict(float)

    def _get_key(self, identifier: str, endpoint: str = "") -> str:
        """
        Tạo key duy nhất cho rate limit

        Args:
            identifier: IP address hoặc user ID
            endpoint: Endpoint đang truy cập

        Returns:
            str: Key duy nhất
        """
        # Tạo key hash để tránh collision
        key_string = f"{identifier}:{endpoint}"
        return hashlib.md5(key_string.encode()).hexdigest()

    def _cleanup_old_requests(self, key: str, window_size: int) -> None:
        """
        Xóa các requests cũ ngoài sliding window

        Args:
            key: Rate limit key
            window_size: Kích thước window (giây)
        """
        current_time = time.time()

        # Chỉ cleanup mỗi 10 giây để tránh performance impact
        if current_time - self._last_cleanup[key] < 10:
            return

        cutoff_time = current_time - window_size
        while self._requests[key] and self._requests[key][0] <= cutoff_time:
            self._requests[key].popleft()

        self._last_cleanup[key] = current_time

    async def is_allowed(self, identifier: str, limit: int, window_size: int = 60, endpoint: str = "") -> Tuple[bool, Dict[str, Any]]:
        """
        Kiểm tra request có được phép không

        Args:
            identifier: IP address hoặc user ID
            limit: Số requests tối đa
            window_size: Kích thước window (giây)
            endpoint: Endpoint đang truy cập

        Returns:
            Tuple[bool, Dict]: (allowed, metadata)
        """
        key = self._get_key(identifier, endpoint)
        current_time = time.time()

        # Cleanup requests cũ
        self._cleanup_old_requests(key, window_size)

        # Thêm request hiện tại
        self._requests[key].append(current_time)

        # Kiểm tra số requests trong window
        request_count = len(self._requests[key])

        # Tính toán metadata
        oldest_request = self._requests[key][0] if self._requests[key] else current_time
        time_until_reset = window_size - (current_time - oldest_request)
        remaining_requests = max(0, limit - request_count)

        metadata = {
            "limit": limit,
            "remaining": remaining_requests,
            "reset_time": int(oldest_request + window_size),
            "retry_after": int(time_until_reset) if time_until_reset > 0 else 0,
            "current_requests": request_count
        }

        return request_count <= limit, metadata

    def reset_limit(self, identifier: str, endpoint: str = "") -> None:
        """
        Reset rate limit cho một identifier cụ thể

        Args:
            identifier: IP address hoặc user ID
            endpoint: Endpoint cần reset
        """
        key = self._get_key(identifier, endpoint)
        if key in self._requests:
            del self._requests[key]


class RedisRateLimiter:
    """
    Rate Limiter sử dụng Redis cho distributed systems

    Dùng khi có nhiều server instances cần chia sẻ state.
    """

    def __init__(self, redis_client=None):
        """
        Khởi tạo Redis rate limiter

        Args:
            redis_client: Redis client instance
        """
        self.redis = redis_client

    def _get_key(self, identifier: str, endpoint: str = "") -> str:
        """Tạo key cho Redis"""
        return f"rate_limit:{endpoint}:{identifier}"

    async def is_allowed(self, identifier: str, limit: int, window_size: int = 60, endpoint: str = "") -> Tuple[bool, Dict[str, Any]]:
        """
        Kiểm tra request với Redis sliding window

        Args:
            identifier: IP address hoặc user ID
            limit: Số requests tối đa
            window_size: Kích thước window (giây)
            endpoint: Endpoint đang truy cập

        Returns:
            Tuple[bool, Dict]: (allowed, metadata)
        """
        if not self.redis:
            # Fallback to memory limiter
            fallback = MemoryRateLimiter()
            return fallback.is_allowed(identifier, limit, window_size, endpoint)

        key = self._get_key(identifier, endpoint)
        current_time = time.time()

        try:
            # Sử dụng Redis sorted set để implement sliding window
            # Xóa các requests cũ
            cutoff_time = current_time - window_size
            await self.redis.zremrangebyscore(key, 0, cutoff_time)

            # Đếm số requests hiện tại
            request_count = await self.redis.zcard(key)

            # Nếu vượt quá limit
            if request_count >= limit:
                # Lấy thời gian request cũ nhất để tính retry_after
                oldest_request = await self.redis.zrange(key, 0, 0, withscores=True)
                if oldest_request:
                    retry_after = int(window_size - (current_time - oldest_request[0][1]))
                else:
                    retry_after = window_size

                return False, {
                    "limit": limit,
                    "remaining": 0,
                    "retry_after": max(0, retry_after),
                    "current_requests": request_count
                }

            # Thêm request hiện tại
            await self.redis.zadd(key, {str(current_time): current_time})
            await self.redis.expire(key, window_size)

            return True, {
                "limit": limit,
                "remaining": limit - request_count - 1,
                "retry_after": 0,
                "current_requests": request_count + 1
            }

        except Exception as e:
            logger.error(f"Redis rate limit error: {str(e)}")
            # Fallback to allow request if Redis fails
            return True, {"limit": limit, "remaining": limit - 1}


class RateLimitMiddleware:
    """
    Middleware chính cho rate limiting

    Tự động detect endpoint và áp dụng rate limit phù hợp.
    """

    def __init__(self, use_redis: bool = False, redis_client=None):
        """
        Khởi tạo middleware

        Args:
            use_redis: Có dùng Redis không
            redis_client: Redis client instance
        """
        if use_redis and redis_client:
            self.limiter = RedisRateLimiter(redis_client)
        else:
            self.limiter = MemoryRateLimiter()

        self.config = RateLimitConfig()

    def get_rate_limit_for_endpoint(self, path: str, method: str = "GET") -> Tuple[str, int]:
        """
        Lấy cấu hình rate limit cho endpoint

        Args:
            path: Endpoint path
            method: HTTP method

        Returns:
            Tuple[str, int]: (limit_type, window_size)
        """
        # Normalize path (remove leading slash for matching)
        normalized_path = path.lstrip('/')

        # Ưu tiên match chính xác với full path
        exact_key = f"{method.upper()}:{path}"
        if exact_key in self.config.DEFAULT_LIMITS:
            return self.config.DEFAULT_LIMITS[exact_key]

        # Thử match chính xác với path đã normalize
        exact_key_normalized = f"{method.upper()}:{normalized_path}"
        if exact_key_normalized in self.config.DEFAULT_LIMITS:
            return self.config.DEFAULT_LIMITS[exact_key_normalized]

        # Pattern matching cho các endpoints với ID parameters
        for key, (limit_type, window) in self.config.DEFAULT_LIMITS.items():
            if "*" in key:
                # Convert pattern to regex for matching
                pattern = key.replace("*", "[^/]+")
                import re
                if re.match(f"^{pattern}$", f"{method.upper()}:{path}"):
                    return (limit_type, window)

        # Match theo prefix
        for key, (limit_type, window) in self.config.DEFAULT_LIMITS.items():
            if not key.startswith("/") and not key.startswith("*") and (path.startswith(key) or normalized_path.startswith(key)):
                return (limit_type, window)

        # Mặc định cho GET requests là low limit
        if method.upper() == "GET":
            return ("low", 60)

        # Mặc định cho other requests là medium limit
        return ("medium", 60)

    def get_identifier(self, request: Request) -> str:
        """
        Lấy identifier cho rate limiting

        Ưu tiên: User ID > IP Address

        Args:
            request: FastAPI request

        Returns:
            str: Identifier
        """
        # Thử lấy user ID từ request state (nếu đã auth)
        if hasattr(request.state, 'user') and request.state.user:
            user_id = request.state.user.get('user_id')
            if user_id:
                return f"user:{user_id}"

        # Fallback: IP address
        client_ip = self._get_client_ip(request)
        return f"ip:{client_ip}"

    def _get_client_ip(self, request: Request) -> str:
        """
        Lấy IP address của client

        Args:
            request: FastAPI request

        Returns:
            str: IP address
        """
        # Kiểm tra các header phổ biến
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()

        # Fallback đến client host
        return request.client.host if request.client else "unknown"

    async def check_rate_limit(self, request: Request) -> None:
        """
        Kiểm tra rate limit cho request

        Args:
            request: FastAPI request

        Raises:
            HTTPException: Nếu vượt rate limit
        """
        path = request.url.path
        method = request.method

        # Bỏ qua các path không cần rate limit
        if self._should_skip_path(path):
            return

        # Lấy cấu hình rate limit
        limit_type, window_size = self.get_rate_limit_for_endpoint(path, method)
        limit = self.config.RATE_LIMITS.get(limit_type, self.config.RATE_LIMITS["medium"])

        # Lấy identifier
        identifier = self.get_identifier(request)

        # Kiểm tra rate limit
        allowed, metadata = await self.limiter.is_allowed(
            identifier=identifier,
            limit=limit,
            window_size=window_size,
            endpoint=f"{method}:{path}"
        )

        if not allowed:
            logger.warning(f"Rate limit exceeded for {identifier} on {method}:{path}")

            # Use standard error response format theo API contract
            from .response import rate_limit_response
            response = rate_limit_response(metadata["retry_after"])

            # Add rate limit headers
            response.headers.update({
                "X-RateLimit-Limit": str(metadata["limit"]),
                "X-RateLimit-Remaining": str(metadata["remaining"]),
                "X-RateLimit-Reset": str(metadata["reset_time"]),
                "Retry-After": str(metadata["retry_after"])
            })

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "success": False,
                    "message": "Vượt quá giới hạn request cho phép",
                    "data": None,
                    "error_code": "RATE_001",
                    "retry_after": metadata["retry_after"],
                    "limit": metadata["limit"],
                    "remaining": metadata["remaining"]
                },
                headers={
                    "X-RateLimit-Limit": str(metadata["limit"]),
                    "X-RateLimit-Remaining": str(metadata["remaining"]),
                    "X-RateLimit-Reset": str(metadata["reset_time"]),
                    "Retry-After": str(metadata["retry_after"])
                }
            )

    def _should_skip_path(self, path: str) -> bool:
        """
        Kiểm tra có bỏ qua path không

        Args:
            path: Request path

        Returns:
            bool: True nếu bỏ qua
        """
        skip_paths = [
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json",
            "/favicon.ico",
            "/static/"
        ]

        return any(path.startswith(skip_path) for skip_path in skip_paths)


# Instance toàn cục
rate_limiter = RateLimitMiddleware()


# Decorator cho rate limit
def rate_limit(limit_type: str = "medium", window_size: int = 60):
    """
    Decorator để áp dụng rate limit cho endpoint

    Args:
        limit_type: Loại limit (high, medium, low, none)
        window_size: Kích thước window (giây)
    """
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            # Lấy cấu hình
            limit = RateLimitConfig.RATE_LIMITS.get(limit_type, 20)
            identifier = rate_limiter.get_identifier(request)

            # Kiểm tra limit
            allowed, metadata = await rate_limiter.limiter.is_allowed(
                identifier=identifier,
                limit=limit,
                window_size=window_size
            )

            if not allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "Rate limit exceeded",
                        "limit": limit,
                        "retry_after": metadata["retry_after"]
                    }
                )

            return await func(request, *args, **kwargs)

        return wrapper
    return decorator


# FastAPI dependency
async def check_rate_limit_dependency(request: Request):
    """
    FastAPI dependency để kiểm tra rate limit
    """
    await rate_limiter.check_rate_limit(request)
    return True


# Utility functions
def get_rate_limit_status(identifier: str, endpoint: str = "") -> Dict[str, Any]:
    """
    Lấy status hiện tại của rate limit

    Args:
        identifier: IP hoặc user ID
        endpoint: Endpoint name

    Returns:
        Dict: Rate limit status
    """
    if isinstance(rate_limiter.limiter, MemoryRateLimiter):
        key = rate_limiter.limiter._get_key(identifier, endpoint)
        if key in rate_limiter.limiter._requests:
            return {
                "current_requests": len(rate_limiter.limiter._requests[key]),
                "requests": list(rate_limiter.limiter._requests[key])
            }

    return {"current_requests": 0, "requests": []}


def reset_rate_limit(identifier: str, endpoint: str = ""):
    """
    Reset rate limit cho identifier

    Args:
        identifier: IP hoặc user ID
        endpoint: Endpoint name
    """
    if isinstance(rate_limiter.limiter, MemoryRateLimiter):
        rate_limiter.limiter.reset_limit(identifier, endpoint)