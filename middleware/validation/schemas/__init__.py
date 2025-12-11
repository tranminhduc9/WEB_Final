"""
Validation schemas package.

This package contains Pydantic schemas for request validation.
"""

try:
    from .auth import RegisterSchema, LoginSchema
    from .post import CreatePostSchema, UpdatePostSchema
    __all__ = [
        "RegisterSchema",
        "LoginSchema",
        "CreatePostSchema",
        "UpdatePostSchema"
    ]
except ImportError as e:
    print(f"Warning: Could not import schemas: {e}")
    __all__ = []