# Caching Middleware

This package provides caching middleware components for improved performance.

## 📁 Components

### MemoryCacheMiddleware
- In-memory caching with LRU eviction
- Configurable TTL and cache size
- Fast response times for repeated requests

### RedisCacheMiddleware
- Distributed Redis caching
- Multiple application instances support
- Advanced caching strategies

### CacheManagerMiddleware
- Manages multiple caching strategies
- Cache invalidation and warming
- Intelligent cache key generation

## 🔧 Usage

```python
from middleware.caching import (
    MemoryCacheMiddleware,
    RedisCacheMiddleware,
    CacheManagerMiddleware
)

app.add_middleware(MemoryCacheMiddleware, ttl=300, max_size=1000)
app.add_middleware(RedisCacheMiddleware, redis_url="redis://localhost:6379")
app.add_middleware(CacheManagerMiddleware, strategy="redis")
```

## 📋 TODO

- [ ] Implement Redis connection pooling
- [ ] Add cache warming strategies
- [ ] Implement cache invalidation patterns
- [ ] Add cache statistics and monitoring
- [ ] Support for cache tagging and bulk invalidation