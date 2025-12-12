"""
Authentication and Authorization middleware package.

This package contains middleware for handling JWT authentication,
role-based access control, and session management.
"""

import logging

# Safe imports with fallbacks
__all__ = []

logger = logging.getLogger(__name__)

try:
    from .jwt_middleware import JWTAuthMiddleware, AuthException, require_auth, require_role
    __all__.extend([
        "JWTAuthMiddleware",
        "AuthException",
        "require_auth",
        "require_role"
    ])
except ImportError as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"Could not import jwt_middleware: {e}")

try:
    from .rbac_middleware import RoleGuardMiddleware
    __all__.append("RoleGuardMiddleware")
except ImportError as e:
    logger.warning(f"Could not import rbac_middleware: {e}")

try:
    from .session_middleware import SessionMiddleware
    __all__.append("SessionMiddleware")
except ImportError as e:
    logger.warning(f"Could not import session_middleware: {e}")

try:
    from .token_blacklist import TokenBlacklist
    __all__.append("TokenBlacklist")
except ImportError as e:
    logger.warning(f"Could not import token_blacklist: {e}")

# Initialize __all__ if empty
if not __all__:
    __all__ = []