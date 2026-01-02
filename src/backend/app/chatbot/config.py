"""
Chatbot Configuration

Quản lý cấu hình cho chatbot từ environment variables.
Tất cả cấu hình được đọc từ file .env

Environment Variables (src/.env):
- CHATBOT_API_KEY: API key cho Google Gemini
- CHATBOT_MODEL: Model name (default: gemini-1.5-flash)
- CHATBOT_TEMPERATURE: Temperature (default: 0.7)
- CHATBOT_MAX_TOKENS: Max output tokens (default: 2048)
- CHATBOT_TIMEOUT: Timeout in seconds (default: 30.0)
- CHATBOT_REQUESTS_PER_MINUTE: Rate limit (default: 60)
- CHATBOT_MAX_CONVERSATION_LENGTH: Max history (default: 50)
- CHATBOT_ENABLE_LOGGING: Enable logging (default: true)
- CHATBOT_LOG_LEVEL: Log level (default: INFO)
"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ChatbotConfig:
    """
    Configuration class for Gemini chatbot settings.
    
    Loads settings from environment variables defined in src/.env
    """
    
    # API Configuration - đọc từ .env
    api_key: str = field(default_factory=lambda: os.getenv("CHATBOT_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY", ""))
    model: str = field(default_factory=lambda: os.getenv("CHATBOT_MODEL", "gemini-1.5-flash"))
    
    # Generation settings
    temperature: float = field(default_factory=lambda: float(os.getenv("CHATBOT_TEMPERATURE", "0.7")))
    max_output_tokens: int = field(default_factory=lambda: int(os.getenv("CHATBOT_MAX_TOKENS", "2048")))
    
    # Rate limiting
    requests_per_minute: int = field(default_factory=lambda: int(os.getenv("CHATBOT_REQUESTS_PER_MINUTE", "60")))
    max_retries: int = field(default_factory=lambda: int(os.getenv("CHATBOT_MAX_RETRIES", "3")))
    min_request_interval: float = 1.0  # seconds between requests
    
    # Timeouts
    timeout: float = field(default_factory=lambda: float(os.getenv("CHATBOT_TIMEOUT", "30.0")))
    
    # Conversation settings
    max_history_length: int = field(default_factory=lambda: int(os.getenv("CHATBOT_MAX_CONVERSATION_LENGTH", "50")))
    
    # Logging
    enable_logging: bool = field(default_factory=lambda: os.getenv("CHATBOT_ENABLE_LOGGING", "true").lower() == "true")
    log_level: str = field(default_factory=lambda: os.getenv("CHATBOT_LOG_LEVEL", "INFO"))
    
    # Feature flags
    enabled: bool = field(default_factory=lambda: os.getenv("CHATBOT_ENABLED", "true").lower() == "true")
    enable_rag: bool = field(default_factory=lambda: os.getenv("CHATBOT_ENABLE_RAG", "false").lower() == "true")
    
    def validate(self) -> bool:
        """Validate configuration."""
        if not self.api_key:
            return False
        if self.temperature < 0 or self.temperature > 2:
            return False
        if self.max_output_tokens <= 0:
            return False
        return True
    
    @property
    def is_configured(self) -> bool:
        """Check if API key is configured."""
        return bool(self.api_key) and self.enabled


# Singleton config instance
_config: Optional[ChatbotConfig] = None


def get_config() -> ChatbotConfig:
    """Get singleton config instance."""
    global _config
    if _config is None:
        _config = ChatbotConfig()
    return _config


def reload_config() -> ChatbotConfig:
    """Force reload config from environment."""
    global _config
    _config = ChatbotConfig()
    return _config
