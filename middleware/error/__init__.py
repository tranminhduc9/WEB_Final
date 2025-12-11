"""
Error handling middleware package.
"""

# Safe imports with fallbacks
__all__ = []

try:
    from .auth_error_handler import AuthErrorHandler, auth_exception_handler
    __all__.extend([
        "AuthErrorHandler",
        "auth_exception_handler"
    ])
except ImportError as e:
    print(f"Warning: Could not import auth_error_handler: {e}")

# Initialize __all__ if empty
if not __all__:
    __all__ = []
