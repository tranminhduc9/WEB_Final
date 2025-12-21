"""
Pytest configuration and fixtures for middleware tests.

This file sets up the proper Python path and provides common fixtures
for all middleware test modules.
"""

import pytest
import os
import sys
import tempfile
import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock

# Get the current test directory
test_dir = Path(__file__).parent

# Add the backend src directory to Python path
backend_src_dir = test_dir.parent.parent
middleware_dir = backend_src_dir / "middleware"

if str(backend_src_dir) not in sys.path:
    sys.path.insert(0, str(backend_src_dir))

if str(middleware_dir) not in sys.path:
    sys.path.insert(0, str(middleware_dir))

# Set environment variables for testing
os.environ["TESTING"] = "true"
os.environ["DEBUG"] = "false"
os.environ["LOG_DIR"] = str(test_dir / "logs")
os.environ["AUDIT_LOG_FILE"] = str(test_dir / "logs" / "audit.log")

# Import check to ensure middleware modules can be found
try:
    import auth
    import validator
    import rate_limit
    print(f"[OK] Middleware modules found in: {middleware_dir}")
except ImportError as e:
    print(f"[ERROR] Cannot import middleware modules from {middleware_dir}")
    print(f"Available files: {list(middleware_dir.glob('*.py'))}")
    raise e


# ============================================================================
# PYTEST FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop cho async tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_redis():
    """Mock Redis client fixture"""
    mock_redis = Mock()
    # Mock Redis methods
    mock_redis.get = AsyncMock()
    mock_redis.set = AsyncMock()
    mock_redis.setex = AsyncMock()
    mock_redis.delete = AsyncMock()
    mock_redis.exists = AsyncMock()
    mock_redis.incr = AsyncMock()
    mock_redis.expire = AsyncMock()
    mock_redis.ttl = AsyncMock()
    mock_redis.zadd = AsyncMock()
    mock_redis.zremrangebyscore = AsyncMock()
    mock_redis.zcard = AsyncMock()
    mock_redis.zrange = AsyncMock()
    return mock_redis


@pytest.fixture
def mock_request():
    """Mock FastAPI Request fixture"""
    request = Mock()
    request.method = "GET"
    request.url = Mock()
    request.url.path = "/api/test"
    request.url.query_params = ""
    request.headers = {
        "User-Agent": "TestClient/1.0",
        "Content-Type": "application/json"
    }
    request.state = Mock()
    request.client = Mock()
    request.client.host = "192.168.1.1"
    return request


@pytest.fixture
def mock_response():
    """Mock FastAPI Response fixture"""
    response = Mock()
    response.status_code = 200
    response.headers = {}
    response.body = b'{"success": true}'
    return response


@pytest.fixture
def mock_upload_file():
    """Mock UploadFile fixture"""
    file = Mock()
    file.filename = "test.jpg"
    file.content_type = "image/jpeg"
    file.size = 1024
    file.read = AsyncMock(return_value=b"test file content")
    file.seek = Mock()
    file.file = Mock()
    return file


@pytest.fixture
def temp_file():
    """Create temporary file cho tests"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.tmp') as temp:
        temp_path = temp.name

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def temp_directory():
    """Create temporary directory cho tests"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment variables"""
    # Set test environment variables
    test_env = {
        "JWT_SECRET_KEY": "test-secret-key-for-testing-only",
        "SMTP_HOST": "smtp.test.com",
        "SMTP_PORT": "587",
        "SMTP_USE_TLS": "true",
        "SMTP_USERNAME": "test@test.com",
        "SMTP_PASSWORD": "test-password",
        "FROM_EMAIL": "noreply@test.com",
        "FROM_NAME": "Test Service",
        "FRONTEND_URL": "http://localhost:3000",
        "MONGO_URI": "mongodb://localhost:27017/test",
        "MONGO_DB_NAME": "test_mongo",
        "CLOUDINARY_CLOUD_NAME": "test-cloud",
        "CLOUDINARY_API_KEY": "test-key",
        "CLOUDINARY_API_SECRET": "test-secret",
        "OTP_ENCRYPTION_KEY": "test-encryption-key"
    }

    # Backup original environment
    original_env = {}
    for key, value in test_env.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value

    yield

    # Restore original environment
    for key, original_value in original_env.items():
        if original_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original_value


# ============================================================================
# SAMPLE DATA FIXTURES
# ============================================================================

@pytest.fixture
def sample_user_data():
    """Sample user data cho tests"""
    return {
        "id": 123,
        "email": "test@example.com",
        "password": "SecurePassword123!",
        "full_name": "Test User",
        "role": "user",
        "is_verified": True,
        "created_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def sample_admin_data():
    """Sample admin data cho tests"""
    return {
        "id": 456,
        "email": "admin@example.com",
        "password": "AdminPassword123!",
        "full_name": "Admin User",
        "role": "admin",
        "is_verified": True,
        "created_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def sample_post_data():
    """Sample post data cho tests"""
    return {
        "id": "post123",
        "title": "Bài viết test",
        "content": "<p>Nội dung bài viết test</p>",
        "author_id": 123,
        "related_place_id": 50,
        "tags": ["test", "blog"],
        "status": "approved",
        "created_at": "2024-01-01T00:00:00Z"
    }


# ============================================================================
# CUSTOM MARKS AND CONFIGURATION
# ============================================================================

def pytest_configure(config):
    """Configure custom marks"""
    config.addinivalue_line(
        "markers", "unit: Mark test as unit test (fast, isolated)"
    )
    config.addinivalue_line(
        "markers", "integration: Mark test as integration test (requires dependencies)"
    )
    config.addinivalue_line(
        "markers", "middleware: Mark test as middleware-specific"
    )
    config.addinivalue_line(
        "markers", "slow: Mark test as slow (may take longer to run)"
    )
    config.addinivalue_line(
        "markers", "performance: Mark test as performance benchmark"
    )
    config.addinivalue_line(
        "markers", "security: Mark test as security-focused"
    )


# ============================================================================
# TEST UTILITIES
# ============================================================================

class TestDataFactory:
    """Factory class cho tạo test data"""

    @staticmethod
    def create_user(overrides=None):
        """Create test user data với optional overrides"""
        base_data = {
            "id": 123,
            "email": "test@example.com",
            "password": "SecurePassword123!",
            "full_name": "Test User",
            "role": "user",
            "is_verified": True,
            "created_at": "2024-01-01T00:00:00Z"
        }

        if overrides:
            base_data.update(overrides)

        return base_data

    @staticmethod
    def create_request(method="GET", path="/api/test", headers=None):
        """Create mock request với custom parameters"""
        request = Mock()
        request.method = method
        request.url = Mock()
        request.url.path = path
        request.url.query_params = ""
        request.headers = headers or {"User-Agent": "TestClient/1.0"}
        request.state = Mock()
        request.client = Mock()
        request.client.host = "192.168.1.1"

        return request

    @staticmethod
    def create_upload_file(filename="test.jpg", content_type="image/jpeg", size=1024):
        """Create mock upload file"""
        file = Mock()
        file.filename = filename
        file.content_type = content_type
        file.size = size
        file.read = AsyncMock(return_value=b"test content")
        file.seek = Mock()

        return file


class AsyncTestHelper:
    """Helper class cho async tests"""

    @staticmethod
    async def run_with_timeout(coro, timeout=5.0):
        """Run coroutine với timeout"""
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            pytest.fail(f"Test timed out after {timeout} seconds")

    @staticmethod
    def assert_awaited_with(mock_func, *args, **kwargs):
        """Assert async mock was called với specific arguments"""
        assert mock_func.awaited
        assert mock_func.await_count >= 1

        if args or kwargs:
            mock_func.assert_awaited_with(*args, **kwargs)


class MiddlewareTestHelper:
    """Helper utilities cho middleware tests"""

    @staticmethod
    def create_jwt_payload(user_data, expiry_minutes=60):
        """Create JWT payload cho test"""
        import time
        current_time = int(time.time())

        payload = {
            "sub": str(user_data["id"]),
            "email": user_data["email"],
            "role": user_data.get("role", "user"),
            "iat": current_time,
            "exp": current_time + (expiry_minutes * 60),
            "type": "access"
        }

        return payload

    @staticmethod
    def mock_mongo_client():
        """Mock MongoDB client"""
        mock_client = Mock()
        mock_db = Mock()
        mock_collection = Mock()

        mock_client.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection

        # Mock common methods
        mock_collection.insert_one = AsyncMock(return_value=Mock(inserted_id="test_id"))
        mock_collection.find_one = AsyncMock(return_value={"_id": "test_id", "data": "test"})
        mock_collection.update_one = AsyncMock(return_value=Mock(modified_count=1))
        mock_collection.delete_one = AsyncMock(return_value=Mock(deleted_count=1))

        return mock_client