"""
Rate Limiting Middleware v2.0

Triển khai rate limiting theo 3 levels cho WEB Final API v1:
- High: 5 req/phút (Login, Register, OTP)
- Medium: 20 req/phút (Write actions: Post, Comment, Report, Upload)
- Low: 100 req/phút (Read actions: Search, Get Details)
"""

import time
import logging
import asyncio
from typing import Dict, Optional, Tuple, Union, Callable, List
from datetime import datetime
from enum import Enum

import redis
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

# Safe import with fallback
try:
    from ..config.settings import MiddlewareSettings
except ImportError:
    # Fallback for standalone usage
    import sys, os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config.settings import MiddlewareSettings


logger = logging.getLogger(__name__)


class RateLimitLevel(Enum):
    """Enum định nghĩa các mức rate limiting"""
    HIGH = "high"      # 5 requests/phút
    MEDIUM = "medium"  # 20 requests/phút
    LOW = "low"        # 100 requests/phút


class RateLimitException(HTTPException):
    """Custom exception cho rate limiting"""

    def __init__(self, error_code: str, message: str, retry_after: Optional[int] = None):
        headers = {"Retry-After": str(retry_after)} if retry_after else {}
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            headers=headers
        )

        # Format theo chuẩn response mới
        self.detail = {
            "success": False,
            "message": message,
            "error_code": error_code,
            "data": {
                "retry_after": retry_after
            } if retry_after else None
        }


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Rate Limiting Middleware v2.0 cho WEB Final API

    Triển khai rate limiting theo 3 levels:
    - HIGH (5 req/phút): Login, Register, OTP
    - MEDIUM (20 req/phút): Write actions (Post, Comment, Report, Upload)
    - LOW (100 req/phút): Read actions (Search, Get Details)

    Support cả IP-based và user-based rate limiting với Redis backend.
    """

    def __init__(
        self,
        app,
        redis_client: Optional[redis.Redis] = None,
        redis_prefix: str = "web_final_rate_limit",
        fail_open: bool = True,
    ):
        """
        Initialize Rate Limiter Middleware v2.0.

        Args:
            app: FastAPI application instance
            redis_client: Redis client instance
            redis_prefix: Redis key prefix
            fail_open: Allow requests if Redis fails (fail-open strategy)
        """
        super().__init__(app)

        self.redis_client = redis_client
        self.redis_prefix = redis_prefix
        self.fail_open = fail_open

        # Định nghĩa rate limits theo level
        self.rate_limits = {
            RateLimitLevel.HIGH: {"requests": 5, "window": 60},      # 5 req/phút
            RateLimitLevel.MEDIUM: {"requests": 20, "window": 60},   # 20 req/phút
            RateLimitLevel.LOW: {"requests": 100, "window": 60},     # 100 req/phút
        }

        # Mapping endpoint → rate limit level
        self.endpoint_rate_limits = self._build_endpoint_mapping()

        # In-memory storage fallback
        self.memory_storage: Dict[str, Dict[str, int]] = {}

        # Statistics tracking
        self.stats = {
            "total_requests": 0,
            "blocked_requests": 0,
            "redis_failures": 0,
            "memory_fallbacks": 0
        }

    def _build_endpoint_mapping(self) -> Dict[str, RateLimitLevel]:
        """
        Xây dựng mapping từ endpoint đến rate limit level
        Dựa trên API contract v1
        """
        mapping = {}

        # HIGH level endpoints (5 req/phút)
        high_endpoints = [
            "POST:/api/v1/auth/login",
            "POST:/api/v1/auth/register",
            "POST:/api/v1/auth/forgot-password",
            "POST:/api/v1/auth/reset-password",
            "POST:/api/v1/auth/refresh-token",
        ]

        # MEDIUM level endpoints (20 req/phút) - Write actions
        medium_endpoints = [
            "POST:/api/v1/upload",
            "POST:/api/v1/posts",
            "POST:/api/v1/posts/",  # với comments
            "POST:/api/v1/posts/",  # với likes
            "POST:/api/v1/reports",
            "PUT:/api/v1/users/me",
            "PUT:/api/v1/users/me/password",
            "POST:/api/v1/favorites/places",
            "POST:/api/v1/admin/places",
            "PUT:/api/v1/admin/places/",
            "PATCH:/api/v1/admin/users/",
            "DELETE:/api/v1/admin/posts/",
            "DELETE:/api/v1/admin/reviews/",
        ]

        # LOW level endpoints (100 req/phút) - Read actions
        low_endpoints = [
            "GET:/api/v1/places/suggest",
            "GET:/api/v1/places",
            "GET:/api/v1/places/",
            "GET:/api/v1/places/",  # reviews
            "GET:/api/v1/posts",
            "GET:/api/v1/users/me",
            "GET:/api/v1/users/me/favorites",
            "GET:/api/v1/users/",
            "GET:/api/v1/chatbot/message",
            "GET:/api/v1/chatbot/history",
            "GET:/api/v1/admin/users",
            "GET:/api/v1/admin/posts/pending",
            "GET:/api/v1/admin/dashboard/stats",
        ]

        # Gán level cho các endpoint
        for endpoint in high_endpoints:
            mapping[endpoint] = RateLimitLevel.HIGH

        for endpoint in medium_endpoints:
            mapping[endpoint] = RateLimitLevel.MEDIUM

        for endpoint in low_endpoints:
            mapping[endpoint] = RateLimitLevel.LOW

        return mapping

    def _determine_rate_limit_level(self, request: Request) -> RateLimitLevel:
        """
        Xác định rate limit level cho request
        """
        endpoint_key = f"{request.method}:{request.url.path}"

        # Kiểm tra exact match
        if endpoint_key in self.endpoint_rate_limits:
            return self.endpoint_rate_limits[endpoint_key]

        # Kiểm tra pattern match cho dynamic endpoints ( với params)
        for pattern_key, level in self.endpoint_rate_limits.items():
            if self._pattern_match(endpoint_key, pattern_key):
                return level

        # Default: MEDIUM cho write actions, LOW cho read actions
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            return RateLimitLevel.MEDIUM
        else:
            return RateLimitLevel.LOW

    def _pattern_match(self, endpoint: str, pattern: str) -> bool:
        """
        Kiểm tra xem endpoint có match với pattern không
        Ví dụ: "POST:/api/v1/posts/123/comments" match "POST:/api/v1/posts/"
        """
        if pattern.endswith("/"):
            return endpoint.startswith(pattern)
        return endpoint == pattern

    async def dispatch(self, request: Request, call_next):
        """
        Xử lý request và áp dụng rate limiting theo level.

        Args:
            request: HTTP request cần xử lý
            call_next: Middleware tiếp theo trong chuỗi

        Returns:
            HTTP response nếu trong rate limit, ngược lại raise RateLimitException
        """
        try:
            self.stats["total_requests"] += 1

            # Xác định rate limit level cho endpoint
            rate_limit_level = self._determine_rate_limit_level(request)
            rate_config = self.rate_limits[rate_limit_level]

            # Generate rate limit key
            key = self._generate_rate_limit_key(request, rate_limit_level)

            # Kiểm tra rate limit
            rate_limit_info = await self._check_rate_limit(
                key,
                rate_config["requests"],
                rate_config["window"]
            )

            # Log request for debugging
            logger.debug(f"Rate limit check: {key} - Level: {rate_limit_level.value} - "
                        f"Current: {rate_limit_info['current']}/{rate_config['requests']}")

            # Set rate limit headers
            response = await self._set_rate_limit_headers(
                await call_next(request),
                rate_limit_info,
                rate_config
            )

            # Log rate limiting events
            self._log_rate_limit_event(key, rate_limit_info, request, rate_limit_level)

            return response

        except RateLimitException:
            # Re-raise rate limit exceptions
            raise
        except Exception as e:
            logger.error(f"Lỗi không mong đợi trong rate limiter: {str(e)}")
            # Fail-open strategy: cho phép request nếu có lỗi
            if self.fail_open:
                return await call_next(request)
            raise RateLimitException(
                "RATE_LIMIT_ERROR",
                "Lỗi server nội bộ",
                retry_after=60
            )

    def _generate_rate_limit_key(self, request: Request, level: RateLimitLevel) -> str:
        """
        Tạo rate limit key dựa trên user ID hoặc IP address

        Args:
            request: FastAPI request object
            level: Rate limit level

        Returns:
            Rate limit key string
        """
        # Ưu tiên user ID nếu đã authenticated
        if hasattr(request.state, 'user') and request.state.user:
            user_id = request.state.user.get("id")
            if user_id:
                return f"user:{user_id}:{level.value}"

        # Fallback đến IP address
        client_ip = self._get_client_ip(request)
        return f"ip:{client_ip}:{level.value}"

    def _get_client_ip(self, request: Request) -> str:
        """
        Lấy client IP address từ request

        Args:
            request: FastAPI request object

        Returns:
            Client IP address
        """
        # Kiểm tra headers từ load balancer/proxy
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fallback đến request client
        if request.client:
            return request.client.host

        return "unknown"

    async def _check_rate_limit(self, key: str, max_requests: int, window_seconds: int) -> Dict[str, int]:
        """
        Kiểm tra rate limit sử dụng Redis hoặc memory fallback

        Args:
            key: Rate limit key
            max_requests: Số request tối đa
            window_seconds: Thời gian window (giây)

        Returns:
            Dictionary thông tin rate limit
        """
        try:
            # Ưu tiên Redis
            if self.redis_client:
                return await self._check_redis_rate_limit(key, max_requests, window_seconds)
            else:
                return self._check_memory_rate_limit(key, max_requests, window_seconds)
        except Exception as e:
            logger.warning(f"Redis rate limit check failed: {str(e)}")
            self.stats["redis_failures"] += 1

            # Fallback to memory storage
            self.stats["memory_fallbacks"] += 1
            return self._check_memory_rate_limit(key, max_requests, window_seconds)

    async def _check_redis_rate_limit(self, key: str, max_requests: int, window_seconds: int) -> Dict[str, int]:
        """
        Kiểm tra rate limit sử dụng Redis với atomic operations

        Args:
            key: Rate limit key
            max_requests: Số request tối đa
            window_seconds: Thời gian window (giây)

        Returns:
            Rate limit information
        """
        redis_key = f"{self.redis_prefix}:{key}"

        try:
            # Sử dụng Redis pipeline cho atomic operations
            pipeline = self.redis_client.pipeline()
            pipeline.incr(redis_key)
            pipeline.expire(redis_key, window_seconds)
            results = pipeline.execute()

            current_count = results[0]
            remaining_requests = max(0, max_requests - current_count)
            reset_time = int(time.time() + window_seconds)

            return {
                "current": current_count,
                "remaining": remaining_requests,
                "limit": max_requests,
                "reset_time": reset_time,
                "is_limited": current_count > max_requests
            }

        except Exception as e:
            logger.error(f"Redis rate limit check error: {str(e)}")
            raise

    def _check_memory_rate_limit(self, key: str, max_requests: int, window_seconds: int) -> Dict[str, int]:
        """
        Kiểm tra rate limit sử dụng memory storage (fallback)

        Args:
            key: Rate limit key
            max_requests: Số request tối đa
            window_seconds: Thời gian window (giây)

        Returns:
            Rate limit information
        """
        now = int(time.time())

        # Initialize nếu key chưa tồn tại
        if key not in self.memory_storage:
            self.memory_storage[key] = {
                "count": 0,
                "reset_time": now + window_seconds
            }

        # Reset nếu window đã hết hạn
        if now >= self.memory_storage[key]["reset_time"]:
            self.memory_storage[key] = {
                "count": 1,
                "reset_time": now + window_seconds
            }
        else:
            self.memory_storage[key]["count"] += 1

        current_count = self.memory_storage[key]["count"]
        remaining_requests = max(0, max_requests - current_count)

        return {
            "current": current_count,
            "remaining": remaining_requests,
            "limit": max_requests,
            "reset_time": self.memory_storage[key]["reset_time"],
            "is_limited": current_count > max_requests
        }

    async def _set_rate_limit_headers(
        self,
        response: Response,
        rate_limit_info: Dict[str, int],
        rate_config: Dict[str, int]
    ) -> Response:
        """
        Set rate limit headers cho response

        Args:
            response: HTTP response object
            rate_limit_info: Thông tin rate limit
            rate_config: Rate limit configuration

        Returns:
            Response với rate limit headers
        """
        if hasattr(response, 'headers'):
            response.headers["X-RateLimit-Limit"] = str(rate_limit_info["limit"])
            response.headers["X-RateLimit-Remaining"] = str(rate_limit_info["remaining"])
            response.headers["X-RateLimit-Reset"] = str(rate_limit_info["reset_time"])
            # Custom header cho level
            response.headers["X-RateLimit-Level"] = f"{rate_config['requests']}req/{rate_config['window']}s"

        return response

    def _log_rate_limit_event(
        self,
        key: str,
        rate_limit_info: Dict[str, int],
        request: Request,
        level: RateLimitLevel
    ):
        """
        Log rate limiting events

        Args:
            key: Rate limit key
            rate_limit_info: Rate limit information
            request: HTTP request
            level: Rate limit level
        """
        if rate_limit_info["is_limited"]:
            self.stats["blocked_requests"] += 1
            retry_after = max(1, rate_limit_info["reset_time"] - int(time.time()))
            rate_config = self.rate_limits[level]

            logger.warning(
                f"Rate limit exceeded for {key} on {request.method} {request.url.path}. "
                f"Level: {level.value}, Current: {rate_limit_info['current']}, "
                f"Limit: {rate_limit_info['limit']}, Retry after: {retry_after}s"
            )

            # Raise exception với format mới
            raise RateLimitException(
                "RATE_LIMIT_EXCEEDED",
                f"Vượt quá giới hạn yêu cầu cho phép ({rate_limit_info['limit']} req/{rate_config['window']}s). "
                f"Vui lòng thử lại sau {retry_after} giây.",
                retry_after=retry_after
            )

        logger.debug(
            f"Rate limit check passed for {key}: {rate_limit_info['remaining']}/"
            f"{rate_limit_info['limit']} remaining (Level: {level.value})"
        )

    def get_stats(self) -> Dict[str, int]:
        """
        Lấy thống kê rate limiting

        Returns:
            Statistics dictionary
        """
        return self.stats.copy()

    def reset_stats(self):
        """Reset thống kê rate limiting"""
        self.stats = {
            "total_requests": 0,
            "blocked_requests": 0,
            "redis_failures": 0,
            "memory_fallbacks": 0
        }

    def clear_memory_storage(self):
        """Xóa memory storage"""
        self.memory_storage.clear()

    def get_rate_limit_info(self, request: Request) -> Optional[Dict[str, any]]:
        """
        Lấy thông tin rate limit hiện tại cho một request

        Args:
            request: FastAPI request object

        Returns:
            Rate limit information hoặc None
        """
        try:
            level = self._determine_rate_limit_level(request)
            rate_config = self.rate_limits[level]
            key = self._generate_rate_limit_key(request, level)

            if self.redis_client:
                redis_key = f"{self.redis_prefix}:{key}"
                current = self.redis_client.get(redis_key)
                current_count = int(current) if current else 0
            else:
                current_count = self.memory_storage.get(key, {}).get("count", 0)

            return {
                "level": level.value,
                "limit": rate_config["requests"],
                "window": rate_config["window"],
                "current": current_count,
                "remaining": max(0, rate_config["requests"] - current_count)
            }
        except Exception as e:
            logger.error(f"Lỗi khi lấy rate limit info: {str(e)}")
            return None


# Factory functions cho các rate limiting strategies

def create_rate_limiter(**kwargs):
    """
    Factory function để tạo RateLimiterMiddleware instance

    Args:
        **kwargs: Additional arguments cho RateLimiterMiddleware

    Returns:
        RateLimiterMiddleware instance
    """
    return lambda app: RateLimiterMiddleware(app, **kwargs)


# Alias cho backwards compatibility
RateLimitMiddleware = RateLimiterMiddleware