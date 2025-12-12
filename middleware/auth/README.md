# Authentication Middleware

This directory contains JWT authentication and authorization middleware for the WEB_Final project, implementing the Auth Guard functionality from Task #1.

## 📁 Files

- **`jwt_middleware.py`** - Main JWT Auth Guard middleware
- **`token_blacklist.py`** - Token blacklist service for logout functionality
- **`test_auth_guard.py`** - Comprehensive test suite and examples
- **`rbac_middleware.py`** - Role-based access control (placeholder)
- **`session_middleware.py`** - Session management (placeholder)

## 🚀 Quick Start

### 1. Basic Setup

```python
from fastapi import FastAPI
from middleware.auth.jwt_middleware import JWTAuthMiddleware
from middleware.config.settings import MiddlewareSettings

app = FastAPI()

# Configure settings
settings = MiddlewareSettings()
settings.secret_key = "your-secret-key-here"  # Use environment variable in production

# Add JWT Auth middleware
app.add_middleware(
    JWTAuthMiddleware,
    settings=settings,
    excluded_paths=[
        "/health",
        "/login",
        "/register",
        "/docs",
        "/static"
    ]
)
```

### 2. Protected Routes

Access authenticated user information via `request.state.user`:

```python
from fastapi import Request

@app.get("/api/v1/profile")
async def get_profile(request: Request):
    user = request.state.user
    return {
        "user_id": user["id"],
        "email": user["email"],
        "role": user["role"],
        "name": user["name"]
    }
```

### 3. Decorator-based Protection

```python
from middleware.auth.jwt_middleware import require_auth, require_role

# Require authentication only
@require_auth
async def protected_route(request: Request):
    return {"message": "Hello authenticated user!"}

# Require specific role
@require_role("admin", "moderator")
async def admin_route(request: Request):
    return {"message": "Hello admin!"}
```

## 📋 Features Implemented

### ✅ Auth Guard - JWT Verification (Task #1)

- **Token Extraction**: Extracts JWT from `Authorization: Bearer <token>` header
- **Token Verification**: Validates signature, expiration, and required fields
- **Token Blacklist**: Checks Redis for revoked tokens (logout functionality)
- **User Attachment**: Attaches decoded user info to `request.state.user`
- **Error Handling**: Comprehensive error responses with proper HTTP status codes
- **Path Exclusion**: Configurable excluded paths for public endpoints

### 🛡️ Security Features

- **Secure Token Validation**: Uses PyJWT with RS256/HS256 algorithms
- **Fail-Open Strategy**: Allows requests if Redis is unavailable
- **Comprehensive Logging**: Detailed security event logging
- **Rate Limiting Ready**: Integrated with existing rate limiting middleware
- **Input Sanitization**: Protected against injection attacks

### 🔧 Token Blacklist Service (Task #13)

- **Redis Integration**: Store blacklisted tokens with TTL
- **Auto-Expiration**: Tokens expire automatically based on JWT expiration time
- **Performance Optimized**: Uses Redis key expiration for efficient cleanup
- **Error Resilience**: Graceful fallback when Redis is unavailable

## 📊 Error Responses

All authentication errors return consistent JSON responses:

### Missing Token
```json
{
  "success": false,
  "error": {
    "code": "MISSING_TOKEN",
    "message": "Thiếu token xác thực"
  }
}
```
HTTP Status: 401

### Invalid Token
```json
{
  "success": false,
  "error": {
    "code": "INVALID_TOKEN",
    "message": "Token không hợp lệ"
  }
}
```
HTTP Status: 401

### Token Expired
```json
{
  "success": false,
  "error": {
    "code": "TOKEN_EXPIRED",
    "message": "Token đã hết hạn"
  }
}
```
HTTP Status: 401

### Token Revoked
```json
{
  "success": false,
  "error": {
    "code": "TOKEN_REVOKED",
    "message": "Token đã bị thu hồi"
  }
}
```
HTTP Status: 401

## 🧪 Testing

### Run Test Suite

```bash
cd middleware/auth/
python test_auth_guard.py
```

### Test Cases Covered

1. **Request without Authorization header** → 401 MISSING_TOKEN
2. **Request with invalid token format** → 401 MISSING_TOKEN
3. **Request with invalid JWT token** → 401 INVALID_TOKEN
4. **Request with expired token** → 401 TOKEN_EXPIRED
5. **Request with valid token** → Success, attach user to request.state.user
6. **Request with blacklisted token** → 401 TOKEN_REVOKED
7. **Admin endpoint with user role** → 403 FORBIDDEN
8. **Admin endpoint with admin role** → Success
9. **Public endpoint access** → Success (no auth required)
10. **Token generation and validation** → Success

## 🔧 Configuration

### Environment Variables

```bash
# Required
MIDDLEWARE_SECRET_KEY=your-super-secret-jwt-key-here
MIDDLEWARE_ALGORITHM=HS256
MIDDLEWARE_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Optional
MIDDLEWARE_DEBUG=false
MIDDLEWARE_ENVIRONMENT=production
REDIS_URL=redis://localhost:6379/0
```

### Settings Object

```python
from middleware.config.settings import MiddlewareSettings

settings = MiddlewareSettings(
    secret_key="your-secret-key",
    algorithm="HS256",
    access_token_expire_minutes=30,
    debug=False
)
```

## 📝 Usage Examples

### Basic Protected Route

```python
from fastapi import FastAPI, Request, Depends
from fastapi.security import HTTPBearer
from middleware.auth.jwt_middleware import JWTAuthMiddleware
from middleware.config.settings import MiddlewareSettings

app = FastAPI()

# Add auth middleware
app.add_middleware(
    JWTAuthMiddleware,
    settings=MiddlewareSettings(),
    excluded_paths=["/login", "/register"]
)

@app.get("/api/v1/profile")
async def get_profile(request: Request):
    user = request.state.user
    return {
        "id": user["id"],
        "email": user["email"],
        "role": user["role"]
    }
```

### Role-based Access Control

```python
from middleware.auth.jwt_middleware import require_role

@app.get("/api/v1/admin/users")
@require_role("admin")
async def get_admin_users(request: Request):
    user = request.state.user
    # Admin-only logic here
    return {"message": f"Admin {user['email']} accessed admin endpoint"}
```

### Token Blacklist for Logout

```python
from middleware.auth.token_blacklist import TokenBlacklistService

@app.post("/api/v1/auth/logout")
async def logout(request: Request):
    user = request.state.user
    token = request.state.token

    # Add token to blacklist
    blacklist_service = TokenBlacklistService()
    await blacklist_service.add_to_blacklist(token)

    return {"message": "Successfully logged out"}
```

### Custom Auth Middleware Configuration

```python
app.add_middleware(
    JWTAuthMiddleware,
    settings=settings,
    excluded_paths=[
        "/health",
        "/chatbot/health",
        "/docs",
        "/openapi.json",
        "/static",
        "/login",
        "/register",
        "/api/v1/public/*"
    ],
    redis_client=redis.Redis.from_url("redis://localhost:6379/0")
)
```

## 🔄 Integration with Server

To integrate with the existing FastAPI server:

```python
# server/app.py

from fastapi import FastAPI
from middleware.auth.jwt_middleware import JWTAuthMiddleware
from middleware.config.settings import MiddlewareSettings

app = FastAPI(title="WEB_Final API")

# Add auth middleware
app.add_middleware(
    JWTAuthMiddleware,
    settings=MiddlewareSettings(),
    excluded_paths=[
        "/health",
        "/chatbot/health",
        "/docs",
        "/login",
        "/register"
    ]
)

# Import and include chatbot routes
from chatbot import chatbot_routes
app.include_router(chatbot_routes, prefix="/chatbot")

# Auth-protected routes
@app.get("/api/v1/user/profile")
async def get_profile(request: Request):
    user = request.state.user
    return {"user": user}
```

## 🚨 Security Considerations

1. **Secret Key Management**: Use environment variables for JWT secret
2. **Token Expiration**: Set appropriate token expiration times
3. **HTTPS Only**: Always use HTTPS in production
4. **Input Validation**: Validate all user inputs
5. **Rate Limiting**: Implement rate limiting on auth endpoints
6. **Logging**: Monitor authentication failures and suspicious activities

## 🐛 Troubleshooting

### Common Issues

1. **JWT Secret Key Mismatch**: Ensure same secret key is used for generation and verification
2. **Token Format**: Ensure token is sent as `Authorization: Bearer <token>`
3. **Redis Connection**: Check Redis connection for blacklist functionality
4. **Clock Skew**: Ensure server time is synchronized for token expiration checks

### Debug Mode

Enable debug mode for detailed error information:

```python
settings = MiddlewareSettings(debug=True)
```

## 📚 Additional Documentation

- [FastAPI Security Documentation](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT Best Practices](https://auth0.com/blog/a-look-at-the-latest-draft-for-jwt-bcp/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

## 🤝 Contributing

When modifying authentication middleware:

1. Run the full test suite
2. Test all error scenarios
3. Update documentation
4. Ensure backward compatibility
5. Follow security best practices

---

**Note**: This implementation follows the requirements from Task #1 of the JSON prompt, adapted for the FastAPI framework used in the WEB_Final project.
