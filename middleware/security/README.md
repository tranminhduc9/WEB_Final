# Security Middleware

This package provides security-related middleware components for protecting the application.

## 📁 Components

### RateLimiterMiddleware
- Implements rate limiting to prevent abuse and DDoS attacks
- Configurable request limits per time window
- Support for custom key functions (IP, user ID, etc.)

### EnhancedCORSMiddleware
- Enhanced CORS configuration with granular control
- Support for dynamic origin validation
- Better handling of preflight requests

### SecurityHeadersMiddleware
- Adds security headers to HTTP responses
- Configurable HSTS, CSP, XSS protection, etc.
- Support for custom security headers

### InputValidationMiddleware
- Validates and sanitizes incoming request data
- Prevents injection attacks
- Configurable validation rules

## 🔧 Usage

```python
from middleware.security import (
    RateLimiterMiddleware,
    EnhancedCORSMiddleware,
    SecurityHeadersMiddleware,
    InputValidationMiddleware
)

# Rate limiting
app.add_middleware(
    RateLimiterMiddleware,
    requests=100,
    window=60
)

# Enhanced CORS
app.add_middleware(
    EnhancedCORSMiddleware,
    allow_origins=["https://example.com"],
    allow_credentials=True
)

# Security headers
app.add_middleware(
    SecurityHeadersMiddleware,
    hsts_max_age=31536000,
    content_security_policy="default-src 'self'"
)

# Input validation
app.add_middleware(
    InputValidationMiddleware,
    max_request_size=10485760,
    sanitize_html=True
)
```

## 📋 TODO

- [ ] Implement rate limiting storage (Redis/memory)
- [ ] Implement enhanced CORS validation logic
- [ ] Implement all security headers
- [ ] Implement comprehensive input validation
- [ ] Add IP whitelisting/blacklisting
- [ ] Add bot detection
- [ ] Add request fingerprinting