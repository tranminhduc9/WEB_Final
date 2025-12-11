"""
Mock objects package cho WEB Final Middleware tests.

Cung cấp mock implementations cho Redis, JWT, Database và các external services.
"""

from .mock_redis import MockRedis
from .mock_jwt import MockJWTService
from .mock_database import MockDatabase

__all__ = [
    'MockRedis',
    'MockJWTService',
    'MockDatabase'
]