"""
Caching middleware package.
"""

# Safe imports with fallbacks
__all__ = []

try:
    from .redis_cache import RedisCacheMiddleware
    __all__.append("RedisCacheMiddleware")
except ImportError as e:
    print(f"Warning: Could not import redis_cache: {e}")

try:
    from .memory_cache import MemoryCacheMiddleware
    __all__.append("MemoryCacheMiddleware")
except ImportError as e:
    print(f"Warning: Could not import memory_cache: {e}")

try:
    from .cache_manager import CacheManagerMiddleware
    __all__.append("CacheManagerMiddleware")
except ImportError as e:
    print(f"Warning: Could not import cache_manager: {e}")

# Initialize __all__ if empty
if not __all__:
    __all__ = []
