"""
Global middleware settings configuration.

This module contains base settings that will be used across all middleware components.
"""

from typing import Dict, Any, Optional, List
from pydantic import Field
try:
    # For Pydantic v2+
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for older Pydantic versions
    from pydantic import BaseSettings


class MiddlewareSettings(BaseSettings):
    """Base settings for middleware configuration."""

    # General settings
    debug: bool = Field(default=False, description="Enable debug mode")
    environment: str = Field(default="development", description="Environment name")

    # Security settings
    secret_key: str = Field(default="your-secret-key-change-in-production", description="JWT secret key")
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="Token expiration in minutes")

    # Rate limiting
    rate_limit_requests: int = Field(default=100, description="Max requests per window")
    rate_limit_window: int = Field(default=60, description="Rate limit window in seconds")

    # CORS settings
    allowed_origins: List[str] = Field(default=["*"], description="Allowed CORS origins")
    allowed_methods: List[str] = Field(default=["*"], description="Allowed HTTP methods")
    allowed_headers: List[str] = Field(default=["*"], description="Allowed HTTP headers")

    # Logging settings
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format")

    # Caching settings
    cache_ttl: int = Field(default=300, description="Cache TTL in seconds")
    cache_max_size: int = Field(default=1000, description="Maximum cache size")

    # Redis settings
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    redis_enabled: bool = Field(default=True, description="Enable Redis functionality")

    # For Pydantic v2+
    if hasattr(BaseSettings, 'model_config'):
        model_config = {
            "env_prefix": "MIDDLEWARE_",
            "env_file": ".env",
            "case_sensitive": False,
            "extra": "ignore"
        }
    else:
        # For Pydantic v1.x
        class Config:
            env_prefix = "MIDDLEWARE_"
            env_file = ".env"
            case_sensitive = False