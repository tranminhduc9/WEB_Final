# Hướng Dẫn Sử Dụng Middleware v2.0

Hướng dẫn chi tiết sử dụng middleware layer cho WEB Final API.

## 📋 Tổng Quan

Middleware v2.0 cung cấp các tính năng bảo mật, xác thực và kiểm tra dữ liệu cho WEB Final API:
- Xác thực JWT với token blacklist
- Phân quyền Role-based (User/Mod/Admin)
- Giới hạn truy cập 3 cấp
- Kiểm tra dữ liệu với Pydantic schemas
- Xử lý lỗi tập trung
- Audit logging

## 🚀 Cài Đặt

### 1. Thêm Dependencies

```bash
pip install fastapi pydantic redis PyJWT python-multipart
```

### 2. Cấu Hình Environment Variables

```bash
# .env file
JWT_SECRET_KEY=your-super-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

REDIS_URL=redis://localhost:6379/0

DEBUG=false
LOG_LEVEL=INFO
```

### 3. Setup Middleware Stack

```python
from fastapi import FastAPI
from middleware.auth.jwt_middleware import JWTAuthMiddleware
from middleware.auth.role_guard import RoleGuardMiddleware
from middleware.security.rate_limiter import RateLimiterMiddleware
from middleware.validation.validator import ValidationMiddleware
from middleware.error.global_error_handler import ErrorHandlerMiddleware

app = FastAPI(title="WEB Final API v2.0")

# Thêm middleware (thứ tự quan trọng!)
app.add_middleware(ErrorHandlerMiddleware)           # Trong cùng
app.add_middleware(ValidationMiddleware)
app.add_middleware(RateLimiterMiddleware)
app.add_middleware(JWTAuthMiddleware,
                   excluded_paths=["/login", "/register", "/health"])
app.add_middleware(RoleGuardMiddleware)              # Ngoài cùng
```

## 🔐 Xác Thực JWT

### Cách Hoạt Động

- Trích xuất token từ `Authorization: Bearer <token>` header
- Xác thực signature và expiration
- Kiểm tra token blacklist
- Đính kèm user info vào `request.state.user`

### Response Headers

```http
Authorization: Bearer <jwt_token>
```

### Error Responses

```json
{
  "success": false,
  "message": "Token đã hết hạn",
  "error_code": "TOKEN_EXPIRED",
  "data": null,
  "pagination": null
}
```

## 👥 Phân Quyền (Role-based Access Control)

### Role Hierarchy

```
Guest (0) < User (1) < Moderator (2) < Admin (3)
```

### Sử Dụng Decorators

```python
from middleware.auth.role_guard import require_role, require_permission

# Yêu cầu role cụ thể
@app.get("/admin/dashboard")
@require_role("admin")
async def admin_dashboard(request: Request):
    return {"message": "Admin access granted"}

# Yêu cầu nhiều role
@app.get("/moderator/tools")
@require_role("admin", "moderator")
async def moderator_tools(request: Request):
    return {"message": "Moderator access granted"}

# Yêu cầu permission
@app.delete("/posts/{post_id}")
@require_permission("delete", "manage_posts")
async def delete_post(request: Request, post_id: str):
    return {"message": "Post deleted"}
```

### Truy Cập User Info

```python
@app.get("/api/v1/profile")
async def get_profile(request: Request):
    user = request.state.user
    return {
        "user_id": user["id"],
        "email": user["email"],
        "role": user["role"]
    }
```

## ⚡ Giới Hạn Truy Cập (Rate Limiting)

### 3 Cấp Rate Limiting

| Level | Requests | Thời gian | Endpoints |
|-------|----------|----------|-----------|
| **CAO** | 5 req/phút | 60s | `/auth/login`, `/auth/register`, `/auth/reset-password` |
| **TRUNG BÌNH** | 20 req/phút | 60s | `/upload`, `/posts`, `/comments`, `/reports` |
| **THẤP** | 100 req/phút | 60s | `/places`, `/places/suggest`, `/chatbot/message` |

### Response Headers

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995260
X-RateLimit-Level: 100req/60s
```

### Rate Limit Exceeded

```json
{
  "success": false,
  "message": "Quá nhiều yêu cầu, vui lòng thử lại sau",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "data": {
    "retry_after": 60
  }
}
```

## ✅ Kiểm Tra Dữ Liệu (Validation)

### Sử Dụng Decorators

```python
from middleware.validation.validator import validate_body, validate_query, validate_params

# Validate request body
@app.post("/api/v1/posts")
@validate_body(CreatePostSchema)
async def create_post(request: Request):
    data = request.state.validated_body
    return {"title": data["title"], "content": data["content"]}

# Validate query parameters
@app.get("/api/v1/places")
@validate_query(SearchPlacesSchema)
async def search_places(request: Request):
    query = request.state.validated_query
    return {"results": [], "query": query["q"]}

# Validate path parameters
@app.get("/api/v1/users/{user_id}")
@validate_params(UserIdSchema)
async def get_user(request: Request, user_id: str):
    return {"user_id": user_id}
```

### Validation Error Response

```json
{
  "success": false,
  "message": "Dữ liệu không hợp lệ",
  "error_code": "VALIDATION_ERROR",
  "data": {
    "errors": [
      {
        "field": "email",
        "message": "Email không hợp lệ",
        "value": "invalid-email"
      }
    ]
  }
}
```

## 🚨 Xử Lý Lỗi

### Error Types Handled

- **Authentication Errors**: JWT token invalid/expired
- **Authorization Errors**: Insufficient permissions
- **Validation Errors**: Pydantic validation failures
- **Rate Limiting Errors**: Too many requests
- **Database Errors**: MongoDB connection issues
- **Generic Errors**: Unhandled exceptions

### Standard Error Format

```json
{
  "success": false,
  "message": "Thông tin lỗi bằng tiếng Việt",
  "error_code": "ERROR_CODE",
  "data": {
    "details": "Chi tiết lỗi (nếu có)"
  },
  "pagination": null
}
```

## 📝 Audit Logging

### Features

- Tự động log tất cả user activities
- Sanitize sensitive data
- Metadata: action, endpoint, method, user_id, severity

### Audit Log Format

```json
{
  "timestamp": "2024-12-11T14:30:00Z",
  "action": "create_post",
  "method": "POST",
  "endpoint": "/api/v1/posts",
  "user_id": 123,
  "severity": "MEDIUM",
  "metadata": {
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0..."
  }
}
```

## 🔧 Configuration Chi Tiết

### Full Environment Variables

```bash
# JWT Configuration
JWT_SECRET_KEY=your-super-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Application Configuration
DEBUG=false
LOG_LEVEL=INFO
ENVIRONMENT=production

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
CORS_CREDENTIALS=true
```

### Custom Configuration

```python
from middleware.auth.jwt_middleware import JWTAuthMiddleware

app.add_middleware(
    JWTAuthMiddleware,
    excluded_paths=[
        "/health",
        "/docs",
        "/openapi.json",
        "/static/*",
        "/api/v1/public/*"
    ]
)
```

## 🐛 Troubleshooting

### Common Issues

1. **JWT Token Issues**
   ```bash
   # Check token validity
   python -c "import jwt; token='your-token'; key='your-secret'; print(jwt.decode(token, key, algorithms=['HS256']))"
   ```

2. **Redis Connection**
   ```bash
   # Test Redis connection
   redis-cli ping
   ```

3. **Import Errors**
   ```bash
   # Check Python path
   python -c "from middleware.auth.jwt_middleware import JWTAuthMiddleware; print('OK')"
   ```

4. **Rate Limiting Not Working**
   - Verify Redis connection
   - Check endpoint classification
   - Review rate limit headers

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Hoặc set environment variable
os.environ["DEBUG"] = "true"
```

## 📚 Examples

### Complete Protected Endpoint

```python
from fastapi import Request
from middleware.validation.validator import validate_body
from middleware.auth.role_guard import require_role

@app.post("/api/v1/posts")
@validate_body(CreatePostSchema)
@require_role("user", "moderator", "admin")
async def create_post(request: Request):
    # Get authenticated user info
    user = request.state.user

    # Get validated data
    post_data = request.state.validated_body

    # Create post logic here
    new_post = {
        "id": "post_123",
        "title": post_data["title"],
        "content": post_data["content"],
        "author_id": user["id"],
        "created_at": datetime.utcnow()
    }

    return {
        "success": True,
        "message": "Tạo bài viết thành công",
        "data": new_post
    }
```

### Public Endpoint with Rate Limiting

```python
@app.post("/api/v1/auth/login")
@validate_body(LoginSchema)
async def login(request: Request):
    # Public endpoint - không cần authentication
    # Nhưng vẫn bị rate limiting (CAO level: 5 req/phút)

    data = request.state.validated_body
    user = await authenticate_user(data["email"], data["password"])

    if not user:
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không đúng")

    # Generate JWT token
    token = create_jwt_token(user)

    return {
        "success": True,
        "message": "Đăng nhập thành công",
        "data": {
            "access_token": token,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "role": user["role"]
            }
        }
    }
```

## 🧪 Testing

### Run Tests

```bash
# Run all tests
python run_tests.py

# Run with coverage
python run_tests.py --coverage

# Run specific test types
python run_tests.py --type unit
python run_tests.py --type integration

# Run tests by component
python run_tests.py --component auth
python run_tests.py --component rate_limiting
```

---

**Version**: 2.0
**Framework**: FastAPI
**Python**: 3.9+
**Status**: Production Ready ✅

Cho thêm thông tin chi tiết, xem [Development Log](DEVELOPMENT_LOG.md) và [Test Documentation](tests/README.md).