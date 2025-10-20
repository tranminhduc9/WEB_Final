"""
Middleware package for WEB_Final application.

This package contains various middleware components for handling authentication,
security, logging, caching, and other cross-cutting concerns.
"""

__version__ = "1.0.0"
__author__ = "WEB Final Team"

from .config import MiddlewareConfig
from .utils import MiddlewareChain

__all__ = [
    "MiddlewareConfig",
    "MiddlewareChain",
]