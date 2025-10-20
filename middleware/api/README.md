# API Middleware

This package provides API-specific middleware components.

## 📁 Components

### APIVersioningMiddleware
- URL path, header, or query parameter versioning
- Automatic version detection
- Backward compatibility support

### APIThrottlingMiddleware
- API-specific rate limiting
- Quota management per user/API key
- Throttling rule configuration

### ResponseFormatterMiddleware
- Standardized API response format
- Consistent error responses
- Content negotiation support

## 🔧 Usage

```python
from middleware.api import (
    APIVersioningMiddleware,
    APIThrottlingMiddleware,
    ResponseFormatterMiddleware
)

app.add_middleware(APIVersioningMiddleware, default_version="v1")
app.add_middleware(APIThrottlingMiddleware, default_quota=1000)
app.add_middleware(ResponseFormatterMiddleware, format="json")
```

## 📋 TODO

- [ ] Implement semantic versioning support
- [ ] Add API key-based throttling
- [ ] Implement response template system
- [ ] Add API documentation integration
- [ ] Support for GraphQL-specific middleware