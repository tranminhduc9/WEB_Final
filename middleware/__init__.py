"""
Middleware package for WEB_Final application.

This package contains various middleware components for handling authentication,
security, logging, caching, and other cross-cutting concerns.
"""

__version__ = "1.0.0"
__author__ = "WEB Final Team"

# Initialize __all__ list
__all__ = []

# Try to import available modules
try:
    from .config.settings import MiddlewareSettings
    __all__.append("MiddlewareSettings")
except ImportError:
    pass

try:
    from .utils import MiddlewareChain
    __all__.append("MiddlewareChain")
except ImportError:
    pass