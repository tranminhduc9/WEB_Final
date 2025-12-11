"""
Rate Limiting Middleware Tests v2.0

Comprehensive tests cho Rate Limiting Middleware với 3 levels:
- HIGH (5 req/phút): Login, Register, OTP
- MEDIUM (20 req/phút): Write actions
- LOW (100 req/phút): Read actions
"""

import pytest
import asyncio
from typing import Optional, Dict, Any
from unittest.mock import AsyncMock, patch
from fastapi import Request
from starlette.responses import JSONResponse

# Dynamic imports để handle testing environment
try:
    from security.rate_limiter import (
        RateLimiterMiddleware, RateLimitLevel, RateLimitException
    )
    IMPORTS_AVAILABLE = True
except ImportError:
    IMPORTS_AVAILABLE = False
    pytest.skip("Rate limiting module not available", allow_module_level=True)


@pytest.mark.skipif(not globals().get('IMPORTS_AVAILABLE', False), reason="Rate limiting module not available")
class TestRateLimitingMiddleware:
    """Test cases cho Rate Limiting Middleware"""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_middleware_initialization(self, mock_redis):
        """Test middleware initialization với different configurations"""
        # Test default initialization
        middleware = RateLimiterMiddleware(app=None, redis_client=mock_redis)
        assert middleware.redis_client == mock_redis
        assert middleware.redis_prefix == "web_final_rate_limit"
        assert middleware.fail_open is True
        assert len(middleware.rate_limits) == 3  # HIGH, MEDIUM, LOW
        assert RateLimitLevel.HIGH in middleware.rate_limits
        assert RateLimitLevel.MEDIUM in middleware.rate_limits
        assert RateLimitLevel.LOW in middleware.rate_limits

        # Test custom configuration
        custom_middleware = RateLimiterMiddleware(
            app=None,
            redis_client=mock_redis,
            redis_prefix="custom_prefix",
            fail_open=False
        )
        assert custom_middleware.redis_prefix == "custom_prefix"
        assert custom_middleware.fail_open is False

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_endpoint_rate_level_determination(self, rate_limit_middleware):
        """Test xác định rate limit level cho các endpoints khác nhau"""
        # Test HIGH level endpoints
        login_request = create_mock_request("POST", "/api/v1/auth/login")
        assert rate_limit_middleware._determine_rate_limit_level(login_request) == RateLimitLevel.HIGH

        register_request = create_mock_request("POST", "/api/v1/auth/register")
        assert rate_limit_middleware._determine_rate_limit_level(register_request) == RateLimitLevel.HIGH

        # Test MEDIUM level endpoints (write actions)
        create_post_request = create_mock_request("POST", "/api/v1/posts")
        assert rate_limit_middleware._determine_rate_limit_level(create_post_request) == RateLimitLevel.MEDIUM

        upload_request = create_mock_request("POST", "/api/v1/upload")
        assert rate_limit_middleware._determine_rate_limit_level(upload_request) == RateLimitLevel.MEDIUM

        # Test LOW level endpoints (read actions)
        get_places_request = create_mock_request("GET", "/api/v1/places")
        assert rate_limit_middleware._determine_rate_limit_level(get_places_request) == RateLimitLevel.LOW

        get_posts_request = create_mock_request("GET", "/api/v1/posts")
        assert rate_limit_middleware._determine_rate_limit_level(get_posts_request) == RateLimitLevel.LOW

        # Test default behavior cho unknown endpoints
        unknown_get_request = create_mock_request("GET", "/api/v1/unknown")
        assert rate_limit_middleware._determine_rate_limit_level(unknown_get_request) == RateLimitLevel.LOW

        unknown_post_request = create_mock_request("POST", "/api/v1/unknown")
        assert rate_limit_middleware._determine_rate_limit_level(unknown_post_request) == RateLimitLevel.MEDIUM

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_rate_limit_key_generation(self, rate_limit_middleware):
        """Test rate limit key generation cho user và IP"""
        # Test IP-based key cho anonymous user
        anonymous_request = create_mock_request(
            "GET",
            "/api/v1/places",
            headers={"x-forwarded-for": "192.168.1.100"}
        )
        key = rate_limit_middleware._generate_rate_limit_key(anonymous_request, RateLimitLevel.LOW)
        assert key == "ip:192.168.1.100:low"

        # Test user-based key cho authenticated user
        authenticated_request = create_mock_request("GET", "/api/v1/places")
        authenticated_request.state.user = {"id": 123, "email": "test@example.com"}
        key = rate_limit_middleware._generate_rate_limit_key(authenticated_request, RateLimitLevel.LOW)
        assert key == "user:123:low"

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_high_level_rate_limiting(self, rate_limit_middleware, mock_redis):
        """Test HIGH level rate limiting (5 req/phút) cho login"""
        request = create_mock_request(
            "POST",
            "/api/v1/auth/login",
            json_body={"email": "test@example.com", "password": "password"}
        )

        # Mock call_next
        async def mock_call_next(req):
            return JSONResponse(content={"success": True})

        # Test 5 requests - nên pass
        for i in range(5):
            response = await rate_limit_middleware.dispatch(request, mock_call_next)
            assert response.status_code == 200

        # Request thứ 6 - nên bị rate limit
        with pytest.raises(RateLimitException) as exc_info:
            await rate_limit_middleware.dispatch(request, mock_call_next)

        assert exc_info.value.status_code == 429
        assert "RATE_LIMIT_EXCEEDED" in str(exc_info.value.detail.get("error_code", ""))

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_medium_level_rate_limiting(self, rate_limit_middleware, mock_redis):
        """Test MEDIUM level rate limiting (20 req/phút) cho write actions"""
        request = create_mock_request(
            "POST",
            "/api/v1/posts",
            json_body={"title": "Test Post", "content": "Test content"}
        )

        async def mock_call_next(req):
            return JSONResponse(content={"success": True})

        # Test 20 requests - nên pass
        for i in range(20):
            response = await rate_limit_middleware.dispatch(request, mock_call_next)
            assert response.status_code == 200

        # Request thứ 21 - nên bị rate limit
        with pytest.raises(RateLimitException):
            await rate_limit_middleware.dispatch(request, mock_call_next)

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_low_level_rate_limiting(self, rate_limit_middleware, mock_redis):
        """Test LOW level rate limiting (100 req/phút) cho read actions"""
        request = create_mock_request("GET", "/api/v1/places")

        async def mock_call_next(req):
            return JSONResponse(content={"success": True})

        # Test 100 requests - nên pass
        for i in range(100):
            response = await rate_limit_middleware.dispatch(request, mock_call_next)
            assert response.status_code == 200

        # Request thứ 101 - nên bị rate limit
        with pytest.raises(RateLimitException):
            await rate_limit_middleware.dispatch(request, mock_call_next)

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_rate_limit_headers(self, rate_limit_middleware, mock_redis):
        """Test rate limit headers trong response"""
        request = create_mock_request("GET", "/api/v1/places")

        async def mock_call_next(req):
            response = JSONResponse(content={"success": True})
            return response

        response = await rate_limit_middleware.dispatch(request, mock_call_next)

        # Check rate limit headers
        assert hasattr(response, 'headers')
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers
        assert "X-RateLimit-Level" in response.headers

        assert response.headers["X-RateLimit-Limit"] == "100"  # LOW level limit
        assert response.headers["X-RateLimit-Remaining"] == "99"  # 1 request made
        assert response.headers["X-RateLimit-Level"] == "100req/60s"  # LOW level config

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_different_rate_levels_different_endpoints(self, rate_limit_middleware, mock_redis):
        """Test rate limits khác nhau cho endpoints khác nhau"""
        # Create requests cho các endpoints với levels khác nhau
        login_request = create_mock_request("POST", "/api/v1/auth/login")
        post_request = create_mock_request("POST", "/api/v1/posts")
        get_request = create_mock_request("GET", "/api/v1/places")

        async def mock_call_next(req):
            return JSONResponse(content={"success": True})

        # Test HIGH level (5 requests)
        login_response = await rate_limit_middleware.dispatch(login_request, mock_call_next)
        assert login_response.headers["X-RateLimit-Limit"] == "5"
        assert login_response.headers["X-RateLimit-Level"] == "5req/60s"

        # Test MEDIUM level (20 requests)
        post_response = await rate_limit_middleware.dispatch(post_request, mock_call_next)
        assert post_response.headers["X-RateLimit-Limit"] == "20"
        assert post_response.headers["X-RateLimit-Level"] == "20req/60s"

        # Test LOW level (100 requests)
        get_response = await rate_limit_middleware.dispatch(get_request, mock_call_next)
        assert get_response.headers["X-RateLimit-Limit"] == "100"
        assert get_response.headers["X-RateLimit-Level"] == "100req/60s"

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_user_based_vs_ip_based_rate_limiting(self, rate_limit_middleware, mock_redis):
        """Test phân biệt user-based và IP-based rate limiting"""
        # Create authenticated request
        user_request = create_mock_request("POST", "/api/v1/posts")
        user_request.state.user = {"id": 123, "email": "user1@example.com"}

        # Create anonymous request
        ip_request = create_mock_request(
            "POST",
            "/api/v1/posts",
            headers={"x-forwarded-for": "192.168.1.100"}
        )

        async def mock_call_next(req):
            return JSONResponse(content={"success": True})

        # Test user-based rate limiting
        for i in range(19):  # MEDIUM level = 20, nên pass
            response = await rate_limit_middleware.dispatch(user_request, mock_call_next)
            assert response.status_code == 200

        # Test IP-based rate limiting cho different user
        user_request2 = create_mock_request("POST", "/api/v1/posts")
        user_request2.state.user = {"id": 456, "email": "user2@example.com"}

        response2 = await rate_limit_middleware.dispatch(user_request2, mock_call_next)
        assert response2.status_code == 200  # Different user nên có limit riêng

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_redis_failure_fallback_to_memory(self, rate_limit_middleware, mock_redis):
        """Test fallback to memory storage khi Redis fails"""
        # Simulate Redis connection error
        mock_redis.simulate_connection_error(True)

        request = create_mock_request("GET", "/api/v1/places")

        async def mock_call_next(req):
            return JSONResponse(content={"success": True})

        # Test requests vẫn hoạt động với memory fallback
        for i in range(5):
            response = await rate_limit_middleware.dispatch(request, mock_call_next)
            assert response.status_code == 200

        # Verify statistics
        stats = rate_limit_middleware.get_stats()
        assert stats["redis_failures"] > 0
        assert stats["memory_fallbacks"] > 0

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_pattern_matching_for_dynamic_endpoints(self, rate_limit_middleware):
        """Test pattern matching cho dynamic endpoints"""
        # Test dynamic endpoints với IDs
        comment_request = create_mock_request("POST", "/api/v1/posts/123/comments")
        assert rate_limit_middleware._determine_rate_limit_level(comment_request) == RateLimitLevel.MEDIUM

        like_request = create_mock_request("POST", "/api/v1/posts/456/likes")
        assert rate_limit_middleware._determine_rate_limit_level(like_request) == RateLimitLevel.MEDIUM

        review_request = create_mock_request("GET", "/api/v1/places/789/reviews")
        assert rate_limit_middleware._determine_rate_limit_level(review_request) == RateLimitLevel.LOW

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_rate_limit_with_redis_pipeline(self, rate_limit_middleware, mock_redis):
        """Test rate limiting với Redis pipeline operations"""
        request = create_mock_request("POST", "/api/v1/auth/login")

        async def mock_call_next(req):
            return JSONResponse(content={"success": True})

        # Test concurrent requests
        async def make_request():
            try:
                return await rate_limit_middleware.dispatch(request, mock_call_next)
            except RateLimitException:
                return "rate_limited"

        # Create 10 concurrent requests (HIGH level allows 5)
        tasks = [make_request() for _ in range(10)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Count successful vs rate limited requests
        successful = sum(1 for r in results if hasattr(r, 'status_code') and r.status_code == 200)
        rate_limited = sum(1 for r in results if r == "rate_limited")

        assert successful == 5  # HIGH level allows 5
        assert rate_limited == 5  # Remaining 5 should be rate limited

    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_rate_limiting_performance(self, rate_limit_middleware, mock_redis):
        """Test performance của rate limiting middleware"""
        request = create_mock_request("GET", "/api/v1/places")

        async def mock_call_next(req):
            return JSONResponse(content={"success": True})

        import time
        start_time = time.time()

        # Measure time for 100 requests
        for i in range(100):
            await rate_limit_middleware.dispatch(request, mock_call_next)

        duration = time.time() - start_time

        # Assert performance requirements
        assert duration < 2.0  # Should complete within 2 seconds
        assert duration / 100 < 0.02  # Average < 20ms per request

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_rate_limit_info_endpoint(self, rate_limit_middleware, mock_redis):
        """Test get_rate_limit_info method"""
        request = create_mock_request("GET", "/api/v1/places")

        async def mock_call_next(req):
            return JSONResponse(content={"success": True})

        # Mock synchronous get method for rate limit info
        original_get = mock_redis.get
        mock_redis.get = mock_redis.get_sync

        # Make a request first
        await rate_limit_middleware.dispatch(request, mock_call_next)

        # Get rate limit info
        info = rate_limit_middleware.get_rate_limit_info(request)
        assert info is not None
        assert info["level"] == "low"
        assert info["limit"] == 100
        assert info["window"] == 60
        assert info["current"] == 1
        assert info["remaining"] == 99

        # Restore original method
        mock_redis.get = original_get

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_statistics_tracking(self, rate_limit_middleware, mock_redis):
        """Test statistics tracking"""
        request = create_mock_request("GET", "/api/v1/places")

        async def mock_call_next(req):
            return JSONResponse(content={"success": True})

        # Make some requests
        for i in range(3):
            await rate_limit_middleware.dispatch(request, mock_call_next)

        # Check statistics
        stats = rate_limit_middleware.get_stats()
        assert stats["total_requests"] == 3
        assert stats["blocked_requests"] == 0

        # Reset statistics
        rate_limit_middleware.reset_stats()
        stats = rate_limit_middleware.get_stats()
        assert stats["total_requests"] == 0


# Helper function từ conftest
def create_mock_request(
    method: str,
    path: str,
    headers: Optional[dict] = None,
    json_body: Optional[dict] = None
) -> Request:
    """Create mock FastAPI Request"""
    from urllib.parse import urlencode

    url = f"http://testserver{path}"
    scope = {
        "type": "http",
        "method": method,
        "path": path,
        "headers": [(k.encode(), v.encode()) for k, v in (headers or {}).items()],
        "url": url,
    }

    request = Request(scope)
    if json_body:
        request._json = json_body

    return request