"""
Security middleware package for handling rate limiting, CORS, security headers, and input validation.
"""

# Safe imports with fallbacks
__all__ = []

try:
    from .rate_limiter import RateLimiterMiddleware
    __all__.append("RateLimiterMiddleware")
except ImportError as e:
    print(f"Warning: Could not import rate_limiter: {e}")

try:
    from .cors_enhanced import EnhancedCORSMiddleware
    __all__.append("EnhancedCORSMiddleware")
except ImportError as e:
    print(f"Warning: Could not import cors_enhanced: {e}")

try:
    from .security_headers import SecurityHeadersMiddleware
    __all__.append("SecurityHeadersMiddleware")
except ImportError as e:
    print(f"Warning: Could not import security_headers: {e}")

try:
    from .input_validation import InputValidationMiddleware
    __all__.append("InputValidationMiddleware")
except ImportError as e:
    print(f"Warning: Could not import input_validation: {e}")

# Initialize __all__ if empty
if not __all__:
    __all__ = []
