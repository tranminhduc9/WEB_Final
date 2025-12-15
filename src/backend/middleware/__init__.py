"""
Middleware package for WEB Final application.

This package contains middleware components organized into:
- v3/: Modern middleware components (60% existing libraries + 40% custom logic)
- api_config.py: Unified API configuration for all modules

v2/ has been removed due to architectural issues and replaced with v3.
"""

__version__ = "3.0.0"
__author__ = "WEB Final Team"

# Initialize __all__ list
__all__ = []

# Import unified API configuration (thay thế cho các module config riêng lẻ)
try:
    from .api_config import (
        UnifiedAPIConfig,
        get_unified_api_config,
        get_endpoint_url,
        get_rate_limit,
        get_error_code,
        APIEndpointConfig,
        RateLimitTier
    )
    __all__.extend([
        "UnifiedAPIConfig",
        "get_unified_api_config",
        "get_endpoint_url",
        "get_rate_limit",
        "get_error_code",
        "APIEndpointConfig",
        "RateLimitTier"
    ])
except ImportError:
    pass

# Import functional components (configuration)
try:
    from .config.settings import MiddlewareSettings
    __all__.append("MiddlewareSettings")
except ImportError:
    pass

# Import v3 enhanced components
try:
    from .v3 import (
        V3Config,
        V3MiddlewareConfig,
        APIMiddlewareManager,
        create_api_middleware,
        api_middleware,
        setup_middleware,
        RateLimiterV3,
        AuthGuardV3,
        RoleGuardV3,
        ResponseFormatterV3,
        RequestValidatorV3,
        ErrorHandlerV3,
        AuditLoggerV3,
        CORSHandlerV3
    )
    __all__.extend([
        "V3Config",
        "V3MiddlewareConfig",
        "APIMiddlewareManager",
        "create_api_middleware",
        "api_middleware",
        "setup_middleware",
        "RateLimiterV3",
        "AuthGuardV3",
        "RoleGuardV3",
        "ResponseFormatterV3",
        "RequestValidatorV3",
        "ErrorHandlerV3",
        "AuditLoggerV3",
        "CORSHandlerV3"
    ])
except ImportError:
    pass

# Convenience imports for quick setup
try:
    from .v3.api_middleware import (
        get_middleware_manager,
        require_auth,
        require_roles,
        rate_limit,
        audit_action
    )
    __all__.extend([
        "get_middleware_manager",
        "require_auth",
        "require_roles",
        "rate_limit",
        "audit_action"
    ])
except ImportError:
    pass

# Response formatter utilities
try:
    from .v3.components.response_formatter import (
        create_success_response,
        create_error_response,
        create_paginated_response,
        ErrorCodes
    )
    __all__.extend([
        "create_success_response",
        "create_error_response",
        "create_paginated_response",
        "ErrorCodes"
    ])
except ImportError:
    pass

# Authentication utilities
try:
    from .v3.components.auth import (
        get_current_user,
        get_optional_user,
        JWTTokenManager
    )
    __all__.extend([
        "get_current_user",
        "get_optional_user",
        "JWTTokenManager"
    ])
except ImportError:
    pass

# Role-based access control utilities
try:
    from .v3.components.roles import (
        UserRole,
        ResourceOwnerChecker,
        require_admin,
        require_moderator
    )
    __all__.extend([
        "UserRole",
        "ResourceOwnerChecker",
        "require_admin",
        "require_moderator"
    ])
except ImportError:
    pass