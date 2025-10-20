"""
Global middleware settings configuration.

This module contains base settings that will be used across all middleware components.
"""

from typing import Dict, Any, Optional
from pydantic import BaseSettings


class MiddlewareSettings(BaseSettings):
    """Base settings for middleware configuration."""

    # General settings
    debug: bool = False
    environment: str = "development"

    # Security settings
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Rate limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds

    # CORS settings
    allowed_origins: list = ["*"]
    allowed_methods: list = ["*"]
    allowed_headers: list = ["*"]

    # Logging settings
    log_level: str = "INFO"
    log_format: str = "json"

    # Caching settings
    cache_ttl: int = 300  # seconds
    cache_max_size: int = 1000

    class Config:
        env_prefix = "MIDDLEWARE_"
        env_file = ".env"