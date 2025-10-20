"""
Main middleware configuration and setup.

This module provides centralized configuration for all middleware components
and handles their registration with FastAPI application.
"""

from typing import List, Type, Dict, Any, Optional
from fastapi import FastAPI, Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware

from .settings import MiddlewareSettings


class MiddlewareConfig:
    """Central configuration for all middleware components."""

    def __init__(self, settings: Optional[MiddlewareSettings] = None):
        self.settings = settings or MiddlewareSettings()

    def setup_middleware(self, app: FastAPI) -> List[Type[BaseHTTPMiddleware]]:
        """
        Setup and register all middleware with the FastAPI application.

        Args:
            app: FastAPI application instance

        Returns:
            List of registered middleware classes
        """
        # Setup CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=self.settings.allowed_origins,
            allow_credentials=True,
            allow_methods=self.settings.allowed_methods,
            allow_headers=self.settings.allowed_headers,
        )

        # TODO: Add other middleware when they are implemented
        # - Rate limiting middleware
        # - Authentication middleware
        # - Logging middleware
        # - Security headers middleware
        # - Caching middleware

        return []

    def get_middleware_order(self) -> List[str]:
        """
        Define the order in which middleware should be applied.

        Returns:
            List of middleware names in execution order
        """
        return [
            "cors",
            "security_headers",
            "rate_limiter",
            "authentication",
            "logging",
            "input_validation",
            "caching",
            "response_formatter",
            "compression",
        ]

    def get_enabled_middlewares(self) -> Dict[str, bool]:
        """
        Get configuration for which middlewares are enabled.

        Returns:
            Dictionary mapping middleware names to enabled status
        """
        return {
            "cors": True,
            "security_headers": True,
            "rate_limiter": self.settings.environment == "production",
            "authentication": True,
            "logging": True,
            "input_validation": True,
            "caching": self.settings.environment != "development",
            "response_formatter": True,
            "compression": self.settings.environment == "production",
        }