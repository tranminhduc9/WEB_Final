# Test Suite cho WEB Final Middleware v2.0

Test suite comprehensive cho middleware layer của WEB Final API v1 với đầy đủ các test cases cho authentication, authorization, rate limiting, validation, và error handling.

## 🧪 Cấu Trúc Test Suite

```
tests/
├── conftest.py                 # Pytest configuration và shared fixtures
├── pytest.ini                 # Pytest settings
├── requirements.txt            # Test dependencies
├── test_rate_limiting.py       # Rate Limiting tests
├── test_authentication.py      # JWT Auth tests
├── test_authorization.py       # Role Guard tests
├── test_validation.py          # Request Validation tests
├── test_error_handling.py      # Error Handler tests
├── test_audit_logging.py       # Audit Log tests
├── test_integration.py         # Integration tests
└── mocks/
    ├── __init__.py
    ├── mock_redis.py           # Mock Redis implementation
    ├── mock_jwt.py             # Mock JWT service
    └── mock_database.py        # Mock database services
```

## 🚀 Chạy Tests

### Quick Start
```bash
# Install test dependencies
pip install -r requirements.txt

# Chạy tất cả tests
pytest -v

# Chạy với coverage
pytest --cov=../middleware --cov-report=html

# Chạy chỉ một module test
pytest test_rate_limiting.py -v
```

### Chạy Tests theo Component
```bash
# Rate limiting tests
pytest test_rate_limiting.py -v

# Authentication tests
pytest test_authentication.py -v

# Authorization tests
pytest test_authorization.py -v

# Validation tests
pytest test_validation.py -v

# Error handling tests
pytest test_error_handling.py -v

# Audit logging tests
pytest test_audit_logging.py -v
```

### Test Markers
```bash
# Chạy chỉ unit tests
pytest -m "unit" -v

# Chạy chỉ integration tests
pytest -m "integration" -v

# Chạy tests cần Redis
pytest -m "redis" -v

# Chạy performance tests
pytest -m "performance" -v
```

## 📊 Test Coverage Mục Tiêu

- **Unit Tests**: 95%+ coverage
- **Integration Tests**: 80%+ coverage
- **Overall**: 90%+ coverage

## 🎯 Test Categories

### 1. Unit Tests
- Test individual middleware components
- Mock external dependencies
- Fast execution (< 1s per test)

### 2. Integration Tests
- Test middleware interactions
- Real Redis connection
- End-to-end request flow

### 3. Performance Tests
- Rate limiting performance under load
- Memory usage validation
- Concurrent request handling

## 🛠️ Test Configuration

### Environment Variables
```bash
# Test environment
export TESTING=true
export LOG_LEVEL=DEBUG

# Test Redis (optional)
export REDIS_URL=redis://localhost:6379/15

# Test secrets
export JWT_SECRET_KEY=test-jwt-secret-for-testing-only
```

### Pytest Configuration
Xem `pytest.ini` và `conftest.py` cho detailed configuration.

## 🧩 Mock Objects

### MockRedis
- Full Redis functionality simulation
- Pipeline support
- TTL and expiration handling
- Error simulation capabilities

### MockJWTService
- JWT token generation and validation
- Custom claims support
- Token expiration simulation
- Token blacklist support

### MockDatabase
- SQLAlchemy operations simulation
- Query building support
- Transaction handling
- Error simulation

## 📝 Test Patterns

### Async Test Pattern
```python
@pytest.mark.asyncio
async def test_middleware_functionality():
    # Arrange
    middleware = YourMiddleware()
    request = create_mock_request("GET", "/api/test")

    # Act
    result = await middleware.process_request(request)

    # Assert
    assert result is not None
```

### Mock Service Pattern
```python
@pytest.fixture
def mock_redis():
    return MockRedis()

@pytest.mark.asyncio
async def test_with_redis(mock_redis):
    # Use mock Redis in tests
    await mock_redis.set("key", "value")
    result = await mock_redis.get("key")
    assert result == "value"
```

### Error Simulation Pattern
```python
@pytest.mark.asyncio
async def test_error_handling():
    mock_redis = MockRedis()
    mock_redis.simulate_connection_error(True)

    middleware = RateLimitMiddleware(redis_client=mock_redis)

    with pytest.raises(ConnectionError):
        await middleware.check_rate_limit(request)
```

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Check Python path
   python -c "import sys; print(sys.path)"

   # Test imports
   python -c "from tests.mocks import MockRedis; print('OK')"
   ```

2. **Async Test Issues**
   ```bash
   # Ensure pytest-asyncio installed
   pip install pytest-asyncio

   # Check pytest version
   pytest --version
   ```

3. **Redis Connection Issues**
   ```bash
   # Test Redis connection
   redis-cli ping

   # Use mock Redis if Redis not available
   pytest -m "unit"  # Uses mock by default
   ```

### Debug Mode
```bash
# Chạy tests với debug logging
LOG_LEVEL=DEBUG pytest -v -s test_file.py

# Chạy specific test method
pytest -v -s test_file.py::TestClass::test_method

# Chạy tests với debugger
pytest --pdb test_file.py
```

## 📈 Performance Testing

### Performance Test Example
```python
@pytest.mark.performance
@pytest.mark.asyncio
async def test_rate_limiting_performance():
    middleware = RateLimitMiddleware()

    start_time = time.time()

    # Measure 100 requests
    for i in range(100):
        request = create_mock_request("GET", "/api/test")
        await middleware.check_rate_limit(request)

    duration = time.time() - start_time

    # Assert < 1 second total, < 10ms average
    assert duration < 1.0
    assert duration / 100 < 0.01
```

## 🔄 CI/CD Integration

### GitHub Actions Example
```yaml
name: Middleware Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: "3.9"

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-cov

    - name: Run tests
      run: |
        pytest --cov=../middleware --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## 📚 Best Practices

### Test Writing Guidelines

1. **Descriptive Test Names**
   ```python
   def test_rate_limiter_blocks_requests_after_limit():
       # Good: Specific and descriptive
       pass

   def test_rate_limiter():
       # Bad: Too generic
       pass
   ```

2. **Arrange-Act-Assert Pattern**
   ```python
   def test_user_authentication():
       # Arrange
       user_data = create_test_user()
       token = create_jwt_token(user_data)

       # Act
       result = authenticate_token(token)

       # Assert
       assert result["user_id"] == user_data["id"]
   ```

3. **Test Independence**
   ```python
   @pytest.fixture
   def clean_middleware():
       middleware = RateLimitMiddleware()
       middleware.reset_stats()
       return middleware
   ```

4. **Comprehensive Error Testing**
   ```python
   @pytest.mark.parametrize("error_type,expected_status", [
       ("missing_token", 401),
       ("invalid_token", 401),
       ("expired_token", 401),
   ])
   async def test_auth_errors(error_type, expected_status):
       # Test multiple error scenarios
       pass
   ```

---

**Framework**: FastAPI, Pytest
**Python**: 3.9+
**Coverage Target**: 90%+
**Test Style**: AAA (Arrange, Act, Assert)