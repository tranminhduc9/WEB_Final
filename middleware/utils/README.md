# Utility Middleware

This package provides utility middleware components for common tasks.

## 📁 Components

### CompressionMiddleware
- Compresses response bodies (gzip, deflate)
- Configurable compression thresholds
- Bandwidth optimization

### MiddlewareChain
- Manages middleware execution order
- Dynamic middleware registration
- Chain validation and debugging

### HealthCheckMiddleware
- Health check endpoint management
- Dependency health monitoring
- Application status reporting

## 🔧 Usage

```python
from middleware.utils import (
    CompressionMiddleware,
    MiddlewareChain,
    HealthCheckMiddleware
)

app.add_middleware(CompressionMiddleware, min_size=1024)
app.add_middleware(HealthCheckMiddleware, health_endpoint="/health")

# Using middleware chain
chain = MiddlewareChain(app)
chain.add_middleware(CompressionMiddleware, position=0)
```

## 📋 TODO

- [ ] Implement Brotli compression support
- [ ] Add middleware dependency resolution
- [ ] Implement detailed health checks
- [ ] Add middleware performance profiling
- [ ] Support for dynamic middleware reloading