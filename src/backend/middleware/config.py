"""
Middleware Configuration Loader
Load và cấu hình middleware từ environment variables
"""

import os
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class MiddlewareConfig:
    """
    Cấu hình chung cho tất cả middleware
    Load từ environment variables
    """

    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    API_VERSION = os.getenv("API_VERSION", "v1")

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/hanoi_travel")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "hanoi_travel_mongo")
    MONGO_TIMEOUT = int(os.getenv("MONGO_TIMEOUT", "5000"))

    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "hanoi-travel-super-secret-key-change-in-production-2024")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION = int(os.getenv("JWT_EXPIRATION", "3600"))
    REFRESH_TOKEN_EXPIRATION = int(os.getenv("REFRESH_TOKEN_EXPIRATION", "604800"))

    # Rate Limiting
    RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_STORAGE = os.getenv("RATE_LIMIT_STORAGE", "redis")
    RATE_LIMIT_DEFAULT_WINDOW = int(os.getenv("RATE_LIMIT_DEFAULT_WINDOW", "60"))

    # Cloudinary
    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "")
    CLOUDINARY_FOLDER = os.getenv("CLOUDINARY_FOLDER", "hanoi-travel")

    # Email (SendGrid)
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
    FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@hanoi-travel.com")
    FROM_NAME = os.getenv("FROM_NAME", "Hanoi Travel")

    # CORS - Include all localhost variants (IPv4, IPv6, localhost alias)
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173,http://[::1]:3000,http://[::1]:5173").split(",")
    CORS_METHODS = os.getenv("CORS_METHODS", "GET,POST,PUT,DELETE,OPTIONS").split(",")
    CORS_HEADERS = os.getenv("CORS_HEADERS", "*").split(",")
    CORS_CREDENTIALS = os.getenv("CORS_CREDENTIALS", "true").lower() == "true"
    CORS_MAX_AGE = int(os.getenv("CORS_MAX_AGE", "86400"))



    # Security
    BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", "12"))
    SESSION_SECRET = os.getenv("SESSION_SECRET", "session-secret-change-in-production")
    ENABLE_AUDIT_LOG = os.getenv("ENABLE_AUDIT_LOG", "true").lower() == "true"
    AUDIT_LOG_FILE = os.getenv("AUDIT_LOG_FILE", "logs/audit.log")

    # File Upload
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "5242880"))  # 5MB
    ALLOWED_FILE_TYPES = os.getenv("ALLOWED_FILE_TYPES", "jpg,jpeg,png,gif,webp").split(",")
    UPLOAD_PATH = os.getenv("UPLOAD_PATH", "uploads")

    # Search Logging
    ENABLE_SEARCH_LOGGING = os.getenv("ENABLE_SEARCH_LOGGING", "true").lower() == "true"
    SEARCH_LOG_RETENTION_DAYS = int(os.getenv("SEARCH_LOG_RETENTION_DAYS", "30"))

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = os.getenv("LOG_FORMAT", "json")
    ENABLE_REQUEST_LOGGING = os.getenv("ENABLE_REQUEST_LOGGING", "true").lower() == "true"

    # Performance
    ENABLE_COMPRESSION = os.getenv("ENABLE_COMPRESSION", "true").lower() == "true"
    ENABLE_CACHING = os.getenv("ENABLE_CACHING", "true").lower() == "true"
    CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))

    # Chatbot
    CHATBOT_ENABLED = os.getenv("CHATBOT_ENABLED", "true").lower() == "true"
    CHATBOT_MODEL = os.getenv("CHATBOT_MODEL", "gpt-3.5-turbo")
    CHATBOT_MAX_TOKENS = int(os.getenv("CHATBOT_MAX_TOKENS", "1000"))
    CHATBOT_TEMPERATURE = float(os.getenv("CHATBOT_TEMPERATURE", "0.7"))
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

    # Feature Flags
    ENABLE_REGISTRATION = os.getenv("ENABLE_REGISTRATION", "true").lower() == "true"
    ENABLE_EMAIL_VERIFICATION = os.getenv("ENABLE_EMAIL_VERIFICATION", "false").lower() == "true"
    ENABLE_SOCIAL_LOGIN = os.getenv("ENABLE_SOCIAL_LOGIN", "false").lower() == "true"
    ENABLE_CONTENT_MODERATION = os.getenv("ENABLE_CONTENT_MODERATION", "true").lower() == "true"

    @classmethod
    def validate_config(cls) -> List[str]:
        """
        Validate configuration và trả về warnings

        Returns:
            List[str]: Danh sách warnings
        """
        warnings = []

        # Check required configs
        if cls.ENVIRONMENT == "production":
            if cls.JWT_SECRET_KEY == "hanoi-travel-super-secret-key-change-in-production-2024":
                warnings.append("[WARN] Production: Please change JWT_SECRET_KEY")



            if cls.SESSION_SECRET == "session-secret-change-in-production":
                warnings.append("[WARN] Production: Please change SESSION_SECRET")

            if "localhost" in cls.CORS_ORIGINS[0]:
                warnings.append("[WARN] Production: CORS_ORIGINS contains localhost")

        # Check optional but recommended configs
        if not cls.CLOUDINARY_CLOUD_NAME:
            warnings.append("[WARN] Cloudinary not configured - file upload will use local storage")

        if not cls.SENDGRID_API_KEY:
            warnings.append("[WARN] SendGrid not configured - email features will be disabled")

        if cls.REDIS_HOST == "localhost" and cls.ENVIRONMENT == "production":
            warnings.append("[WARN] Production: Consider using external Redis service")

        # Check database connections
        if not cls.DATABASE_URL or "username:password" in cls.DATABASE_URL:
            warnings.append("[WARN] Please configure DATABASE_URL with proper credentials")

        if not cls.MONGO_URI or "localhost" in cls.MONGO_URI and cls.ENVIRONMENT == "production":
            warnings.append("[WARN] Production: Consider using external MongoDB service")

        return warnings

    @classmethod
    def get_cors_config(cls) -> Dict[str, Any]:
        """
        Get CORS configuration cho FastAPI

        Returns:
            Dict: CORS configuration
        """
        return {
            "allow_origins": cls.CORS_ORIGINS,
            "allow_credentials": cls.CORS_CREDENTIALS,
            "allow_methods": cls.CORS_METHODS,
            "allow_headers": cls.CORS_HEADERS,
            "max_age": cls.CORS_MAX_AGE
        }

    @classmethod
    def get_rate_limit_config(cls) -> Dict[str, int]:
        """
        Get rate limit configuration theo API contract

        Returns:
            Dict: Rate limit tiers
        """
        return {
            "high": 5,      # Login, Register, OTP
            "medium": 20,   # Write actions: Post, Comment
            "low": 100,     # Read actions: Search, Get Details
            "suggest": 200, # Places suggest endpoint
            "none": 1000    # Gần như không giới hạn
        }

    @classmethod
    def get_endpoint_rate_limits(cls) -> Dict[str, tuple]:
        """
        Get rate limit mapping cho các endpoints theo API contract

        Returns:
            Dict: Endpoint -> (limit_type, window_size)
        """
        return {
            # Authentication endpoints
            "/api/v1/auth/register": ("high", 60),
            "/api/v1/auth/login": ("high", 60),
            "/api/v1/auth/forgot-password": ("high", 60),
            "/api/v1/auth/reset-password": ("high", 60),
            "/api/v1/auth/refresh-token": ("medium", 60),

            # Upload endpoints
            "/api/v1/upload": ("medium", 60),

            # Places endpoints
            "/api/v1/places/suggest": ("suggest", 60),  # 200 req/phút theo yêu cầu
            "/api/v1/places": ("low", 60),
            "/api/v1/places/": ("low", 60),

            # Posts endpoints
            "/api/v1/posts": ("low", 60),
            "/api/v1/posts/": ("medium", 60),  # For POST (create), PUT, DELETE

            # User endpoints
            "/api/v1/users/me": ("medium", 60),
            "/api/v1/favorites/places": ("medium", 60),

            # Admin endpoints (lower limits for security)
            "/api/v1/admin/": ("medium", 60),

            # Chatbot endpoints
            "/api/v1/chatbot/": ("medium", 60),
        }

    @classmethod
    def get_redis_config(cls) -> Dict[str, Any]:
        """
        Get Redis configuration

        Returns:
            Dict: Redis config
        """
        return {
            "host": cls.REDIS_HOST,
            "port": cls.REDIS_PORT,
            "db": cls.REDIS_DB,
            "password": cls.REDIS_PASSWORD,
            "decode_responses": True,
            "socket_connect_timeout": 5,
            "socket_timeout": 5,
            "retry_on_timeout": True
        }

    @classmethod
    def get_mongodb_config(cls) -> Dict[str, Any]:
        """
        Get MongoDB configuration

        Returns:
            Dict: MongoDB config
        """
        return {
            "uri": cls.MONGO_URI,
            "db_name": cls.MONGO_DB_NAME,
            "timeout": cls.MONGO_TIMEOUT,
            "max_pool_size": 10,
            "min_pool_size": 1
        }

    @classmethod
    def get_cloudinary_config(cls) -> Dict[str, str]:
        """
        Get Cloudinary configuration

        Returns:
            Dict: Cloudinary config
        """
        return {
            "cloud_name": cls.CLOUDINARY_CLOUD_NAME,
            "api_key": cls.CLOUDINARY_API_KEY,
            "api_secret": cls.CLOUDINARY_API_SECRET,
            "folder": cls.CLOUDINARY_FOLDER
        }

    @classmethod
    def get_email_config(cls) -> Dict[str, Any]:
        """
        Get Email (SendGrid) configuration

        Returns:
            Dict: Email config
        """
        return {
            "api_key": cls.SENDGRID_API_KEY,
            "from_email": cls.FROM_EMAIL,
            "from_name": cls.FROM_NAME
        }


def load_config() -> MiddlewareConfig:
    """
    Load và validate configuration

    Returns:
        MiddlewareConfig: Loaded configuration
    """
    config = MiddlewareConfig()
    warnings = config.validate_config()

    if warnings:
        logger.warning("Configuration warnings:")
        for warning in warnings:
            logger.warning(warning)

    logger.info(f"Environment: {config.ENVIRONMENT}")
    logger.info(f"Rate Limiting: {'Enabled' if config.RATE_LIMIT_ENABLED else 'Disabled'}")
    logger.info(f"Audit Logging: {'Enabled' if config.ENABLE_AUDIT_LOG else 'Disabled'}")
    logger.info(f"Search Logging: {'Enabled' if config.ENABLE_SEARCH_LOGGING else 'Disabled'}")

    return config


# Global config instance
config = load_config()