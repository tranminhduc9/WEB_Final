# Authentication & Authorization Middleware

This package handles authentication and authorization for the application.

## 📁 Components

### JWTMiddleware
- Validates JWT tokens from Authorization header
- Extracts user information and attaches to request state
- Supports configurable excluded paths

### RBACMiddleware
- Enforces role-based access control
- Configurable role-permission mapping
- Protects endpoints based on user roles

### SessionMiddleware
- Manages user sessions lifecycle
- Handles session cookies
- Supports session timeout configuration

## 🔧 Usage

```python
from middleware.auth import JWTMiddleware, RBACMiddleware, SessionMiddleware

# Add JWT middleware
app.add_middleware(
    JWTMiddleware,
    secret_key="your-secret-key",
    excluded_paths=["/health", "/docs"]
)

# Add RBAC middleware
app.add_middleware(
    RBACMiddleware,
    role_permissions={
        "admin": {"read", "write", "delete"},
        "user": {"read", "write"}
    }
)

# Add session middleware
app.add_middleware(
    SessionMiddleware,
    session_timeout=3600,
    cookie_name="session_id"
)
```

## 📋 TODO

- [ ] Implement JWT token validation logic
- [ ] Implement RBAC permission checking
- [ ] Implement session storage and validation
- [ ] Add token refresh mechanism
- [ ] Add session cleanup job
- [ ] Add comprehensive error handling