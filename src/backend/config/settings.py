"""
Application Settings

Cấu hình ứng dụng với 1 PostgreSQL database duy nhất:
- Database Docker (localhost:5433): Tất cả data (users, places, posts, comments, etc.)
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application Settings"""

    # ==================== APP INFO ====================
    APP_NAME: str = "Hanoi Travel API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # ==================== DATABASE (UNIFIED) ====================
    # Database Docker chứa TẤT CẢ data
    # Port 5433 (host) -> 5432 (container)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://admin:123456@localhost:5433/travel_db"
    )

    # Database Pool Settings
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "10"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "3600"))

    # ==================== MONGODB ====================
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "hanoi_travel_mongo")
    MONGO_TIMEOUT: int = int(os.getenv("MONGO_TIMEOUT", "5000"))
    MONGO_MAX_POOL_SIZE: int = int(os.getenv("MONGO_MAX_POOL_SIZE", "10"))
    MONGO_MIN_POOL_SIZE: int = int(os.getenv("MONGO_MIN_POOL_SIZE", "1"))

    # ==================== REDIS ====================
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    REDIS_SOCKET_TIMEOUT: int = int(os.getenv("REDIS_SOCKET_TIMEOUT", "5"))
    REDIS_SOCKET_CONNECT_TIMEOUT: int = int(os.getenv("REDIS_SOCKET_CONNECT_TIMEOUT", "5"))

    # ==================== JWT ====================
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "hanoi-travel-super-secret-key-change-in-production-2024")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION: int = int(os.getenv("JWT_EXPIRATION", "3600"))  # 1 hour
    REFRESH_TOKEN_EXPIRATION: int = int(os.getenv("REFRESH_TOKEN_EXPIRATION", "604800"))  # 7 days

    # ==================== PASSWORD HASHING ====================
    BCRYPT_ROUNDS: int = int(os.getenv("BCRYPT_ROUNDS", "12"))

    # ==================== RATE LIMITING ====================
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_STORAGE: str = os.getenv("RATE_LIMIT_STORAGE", "redis")
    RATE_LIMIT_DEFAULT_WINDOW: int = int(os.getenv("RATE_LIMIT_DEFAULT_WINDOW", "60"))

    # ==================== EMAIL (SENDGRID) ====================
    SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY", "")
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", "noreply@hanoi-travel.com")
    FROM_NAME: str = os.getenv("FROM_NAME", "Hanoi Travel")


    # ==================== FILE UPLOAD ====================
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "5242880"))  # 5MB
    ALLOWED_FILE_TYPES: list = os.getenv("ALLOWED_FILE_TYPES", "jpg,jpeg,png,gif,webp").split(",")
    UPLOAD_PATH: str = os.getenv("UPLOAD_PATH", "uploads")

    # ==================== CLOUDINARY ====================
    CLOUDINARY_CLOUD_NAME: Optional[str] = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY: Optional[str] = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET: Optional[str] = os.getenv("CLOUDINARY_API_SECRET")
    CLOUDINARY_FOLDER: str = os.getenv("CLOUDINARY_FOLDER", "hanoi-travel")

    # ==================== CHATBOT (GEMINI AI) ====================
    CHATBOT_ENABLED: bool = os.getenv("CHATBOT_ENABLED", "true").lower() == "true"
    CHATBOT_API_KEY: str = os.getenv("CHATBOT_API_KEY", "")
    CHATBOT_MODEL: str = os.getenv("CHATBOT_MODEL", "gemini-1.5-flash")
    CHATBOT_TEMPERATURE: float = float(os.getenv("CHATBOT_TEMPERATURE", "0.7"))
    CHATBOT_MAX_TOKENS: int = int(os.getenv("CHATBOT_MAX_TOKENS", "2048"))
    CHATBOT_TIMEOUT: float = float(os.getenv("CHATBOT_TIMEOUT", "30.0"))

    # ==================== HUNTER.IO (Email Validation) ====================
    # Get free API key from: https://hunter.io/api-key
    # Free tier: 50 requests/month
    HUNTER_IO_API_KEY: str = os.getenv("HUNTER_IO_API_KEY", "")

    # ==================== CORS ====================
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
    CORS_CREDENTIALS: bool = os.getenv("CORS_CREDENTIALS", "true").lower() == "true"
    CORS_MAX_AGE: int = int(os.getenv("CORS_MAX_AGE", "86400"))

    # ==================== SECURITY ====================
    ENABLE_CONTENT_MODERATION: bool = os.getenv("ENABLE_CONTENT_MODERATION", "true").lower() == "true"

    # ==================== LOGGING ====================
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    ENABLE_REQUEST_LOGGING: bool = os.getenv("ENABLE_REQUEST_LOGGING", "true").lower() == "true"
    ENABLE_AUDIT_LOG: bool = os.getenv("ENABLE_AUDIT_LOG", "true").lower() == "true"

    # ==================== FEATURES ====================
    ENABLE_REGISTRATION: bool = os.getenv("ENABLE_REGISTRATION", "true").lower() == "true"
    ENABLE_EMAIL_VERIFICATION: bool = os.getenv("ENABLE_EMAIL_VERIFICATION", "false").lower() == "true"

    class Config:
        case_sensitive = True
        # Không sử dụng env_file vì đã load trong app/main.py
        # Pydantic sẽ đọc từ environment variables đã được load


# ==================== SETTINGS INSTANCE ====================
settings = Settings()
