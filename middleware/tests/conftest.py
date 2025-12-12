"""
Pytest configuration và shared fixtures cho WEB Final Middleware v2.0 tests.

Cung cấp common fixtures, mock objects, và test utilities
cho tất cả middleware test modules.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from urllib.parse import urlencode

import pytest
from fastapi import Request, HTTPException
from starlette.responses import JSONResponse

# Configure logging cho tests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class TestConfig:
    """Configuration constants cho tests"""
    TEST_SECRET_KEY = "test-jwt-secret-key-for-middleware-testing-only"
    TEST_ALGORITHM = "HS256"
    TEST_REDIS_URL = "redis://localhost:6379/15"
    TEST_ACCESS_TOKEN_EXPIRE = 3600  # 1 hour


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop cho async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Mock Objects Fixtures

@pytest.fixture
def mock_redis():
    """Mock Redis instance cho testing"""
    from mocks.mock_redis import MockRedis
    redis = MockRedis()
    yield redis
    redis.reset()


@pytest.fixture
def mock_jwt_service():
    """Mock JWT service cho testing"""
    from mocks.mock_jwt import MockJWTService
    jwt_service = MockJWTService(
        secret_key=TestConfig.TEST_SECRET_KEY,
        algorithm=TestConfig.TEST_ALGORITHM
    )
    yield jwt_service
    jwt_service.reset()


@pytest.fixture
def mock_database():
    """Mock database service cho testing"""
    from mocks.mock_database import MockDatabase
    db = MockDatabase()
    yield db
    db.reset()


@pytest.fixture
def rate_limit_middleware(mock_redis):
    """Mock rate limit middleware instance cho testing"""
    try:
        from security.rate_limiter import RateLimiterMiddleware
        middleware = RateLimiterMiddleware(app=None, redis_client=mock_redis)
        yield middleware
    except ImportError:
        # Skip if rate limiter not available
        pytest.skip("Rate limiting module not available")


# Request Fixtures

@pytest.fixture
def sample_headers():
    """Sample request headers"""
    return {
        "user-agent": "Mozilla/5.0 (Test Browser)",
        "content-type": "application/json",
        "x-forwarded-for": "192.168.1.100"
    }


@pytest.fixture
def sample_user():
    """Sample user data cho JWT tokens"""
    return {
        "user_id": 123,
        "email": "test@example.com",
        "full_name": "Test User",
        "role_id": "user",
        "avatar": "https://example.com/avatar.jpg",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=1)
    }


@pytest.fixture
def sample_admin_user():
    """Sample admin user data cho JWT tokens"""
    return {
        "user_id": 456,
        "email": "admin@example.com",
        "full_name": "Admin User",
        "role_id": "admin",
        "avatar": "https://example.com/admin-avatar.jpg",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=1)
    }


@pytest.fixture
def sample_jwt_token(mock_jwt_service, sample_user):
    """Sample valid JWT token"""
    return mock_jwt_service.create_access_token(
        user_id=sample_user["user_id"],
        email=sample_user["email"],
        full_name=sample_user["full_name"],
        role_id=sample_user["role_id"]
    )


@pytest.fixture
def sample_admin_token(mock_jwt_service, sample_admin_user):
    """Sample admin JWT token"""
    return mock_jwt_service.create_access_token(
        user_id=sample_admin_user["user_id"],
        email=sample_admin_user["email"],
        full_name=sample_admin_user["full_name"],
        role_id=sample_admin_user["role_id"]
    )


@pytest.fixture
def expired_jwt_token(mock_jwt_service):
    """Sample expired JWT token"""
    return mock_jwt_service.create_expired_token("test_user_123")


# Request Builder Functions

def create_mock_request(
    method: str,
    path: str,
    headers: Optional[Dict[str, str]] = None,
    query_params: Optional[Dict[str, str]] = None,
    json_body: Optional[Dict[str, Any]] = None
) -> Request:
    """
    Tạo mock FastAPI Request object cho testing

    Args:
        method: HTTP method
        path: Request path
        headers: Request headers
        query_params: Query parameters
        json_body: JSON body data

    Returns:
        Mock FastAPI Request object
    """
    # Build URL
    url = f"http://testserver{path}"
    if query_params:
        url += f"?{urlencode(query_params)}"

    # Create mock request
    scope = {
        "type": "http",
        "method": method,
        "path": path,
        "query_string": urlencode(query_params or {}).encode(),
        "headers": [(k.encode(), v.encode()) for k, v in (headers or {}).items()],
        "url": url,
    }

    request = Request(scope)

    # Attach JSON body nếu có
    if json_body:
        request._json = json_body

    return request


def create_auth_request(
    token: str,
    path: str,
    method: str = "GET",
    **kwargs
) -> Request:
    """
    Tạo mock authenticated request

    Args:
        token: JWT token
        path: Request path
        method: HTTP method
        **kwargs: Additional arguments cho create_mock_request

    Returns:
        Mock authenticated request
    """
    headers = kwargs.get("headers", {})
    headers["authorization"] = f"Bearer {token}"
    kwargs["headers"] = headers
    return create_mock_request(method, path, **kwargs)


def create_admin_request(
    token: str,
    path: str,
    method: str = "GET",
    **kwargs
) -> Request:
    """
    Tạo mock admin authenticated request

    Args:
        token: Admin JWT token
        path: Request path
        method: HTTP method
        **kwargs: Additional arguments

    Returns:
        Mock admin request
    """
    headers = kwargs.get("headers", {})
    headers["authorization"] = f"Bearer {token}"
    headers["x-admin-token"] = "true"
    kwargs["headers"] = headers
    return create_mock_request(method, path, **kwargs)


# Common Request Fixtures

@pytest.fixture
def public_get_request():
    """Mock public GET request"""
    return create_mock_request("GET", "/api/v1/places")


@pytest.fixture
def authenticated_get_request(sample_jwt_token):
    """Mock authenticated GET request"""
    return create_auth_request(sample_jwt_token, "/api/v1/users/me")


@pytest.fixture
def authenticated_post_request(sample_jwt_token):
    """Mock authenticated POST request"""
    return create_auth_request(
        sample_jwt_token,
        "/api/v1/posts",
        method="POST",
        json_body={
            "title": "Test Post Title",
            "content": "Test post content here",
            "tags": ["test", "post"]
        }
    )


@pytest.fixture
def admin_get_request(sample_admin_token):
    """Mock admin GET request"""
    return create_admin_request(sample_admin_token, "/api/v1/admin/users")


# Test Utility Functions

def assert_error_response_format(response_data: Dict[str, Any], expected_status_code: int = 400):
    """
    Assert response follows error format theo API contract v1

    Args:
        response_data: Response data dictionary
        expected_status_code: Expected HTTP status code
    """
    assert isinstance(response_data, dict)
    assert response_data["success"] is False
    assert "message" in response_data
    assert "error_code" in response_data
    assert "data" in response_data
    assert "pagination" in response_data
    assert response_data["pagination"] is None


def assert_validation_error_details(details: List[Dict[str, Any]], field_name: str):
    """
    Assert validation error details contain specific field error

    Args:
        details: Validation error details list
        field_name: Expected field name with error
    """
    assert isinstance(details, list)
    assert len(details) > 0

    field_errors = [d for d in details if d.get("field") == field_name]
    assert len(field_errors) > 0
    assert "message" in field_errors[0]


def create_mock_call_next(response_data: Any = None):
    """
    Tạo mock call_next function cho middleware testing

    Args:
        response_data: Response data to return

    Returns:
        Mock call_next function
    """
    async def mock_call_next(request):
        if response_data is not None:
            if isinstance(response_data, dict):
                return JSONResponse(content=response_data)
            return response_data
        return JSONResponse(content={"success": True, "message": "OK"})
    return mock_call_next


# Test Data Fixtures

@pytest.fixture
def test_user_data():
    """Test user registration data"""
    return {
        "full_name": "Nguyễn Văn A",
        "email": "test@example.com",
        "password": "SecurePass123!"
    }


@pytest.fixture
def test_login_data():
    """Test user login data"""
    return {
        "email": "test@example.com",
        "password": "SecurePass123!"
    }


@pytest.fixture
def test_post_data():
    """Test post creation data"""
    return {
        "title": "Bài viết test về Hà Nội",
        "content": "Đây là nội dung bài viết test về Hà Nội với đủ 100 ký tự để validate content length requirements của middleware.",
        "cover_image": "https://example.com/hanoi-cover.jpg",
        "related_place_id": 1,
        "tags": ["Hà Nội", "Du lịch", "Văn hóa", "Lịch sử", "Ẩm thực"]
    }


@pytest.fixture
def test_place_data():
    """Test place creation data"""
    return {
        "name": "Văn Miếu - Quốc Tử Giám",
        "description": "Văn Miếu - Quốc Tử Giám là quần thể kiến trúc văn hóa lịch sử tọa lạc tại Hà Nội, Việt Nam. Đây là nơi thờ Khổng Tử và các vị hiền triết Nho giáo.",
        "address": "Quốc Tử Giám, Đống Đa, Hà Nội",
        "district_id": 1,
        "category_id": 1,
        "price_min": 0,
        "price_max": 50000,
        "opening_hours": "8:00 - 17:00",
        "lat": 21.0278,
        "long": 105.8342,
        "images": [
            "https://example.com/van-mieu-1.jpg",
            "https://example.com/van-mieu-2.jpg"
        ]
    }


# Markers cho pytest configuration

def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line(
        "markers", "unit: Unit tests (fast, isolated)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (require external services)"
    )
    config.addinivalue_line(
        "markers", "redis: Tests requiring Redis connection"
    )
    config.addinivalue_line(
        "markers", "performance: Performance tests"
    )
    config.addinivalue_line(
        "markers", "slow: Slow-running tests"
    )


# Cleanup fixtures

@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Auto cleanup after each test"""
    yield
    # Cleanup code sẽ chạy sau mỗi test
    pass