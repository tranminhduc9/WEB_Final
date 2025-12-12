"""
Validation middleware package.

This package contains request validation middleware for input sanitization
and data validation using Pydantic schemas.
"""

import logging

# Safe imports with fallbacks
__all__ = []

logger = logging.getLogger(__name__)

try:
    from .validator import ValidationMiddleware
    __all__.append("ValidationMiddleware")
except ImportError as e:
    logger.warning(f"Could not import validator: {e}")

try:
    from .schemas import auth_schemas, post_schemas
    __all__.extend([
        "auth_schemas",
        "post_schemas"
    ])
except ImportError as e:
    logger.warning(f"Could not import schemas: {e}")

# Initialize __all__ if empty
if not __all__:
    __all__ = []