"""
Configuration management for chatbot module.

This module handles loading and validation of chatbot configuration,
including API keys, model settings, and other parameters.
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from .exceptions import ConfigurationError


@dataclass
class ChatbotConfig:
    """
    Configuration class for chatbot settings.
    
    This class manages all configuration parameters needed for chatbot
    operation, with proper validation and environment variable support.
    """
    
    # API Configuration
    api_key: str = "AIzaSyBwGc5TQ14IpygA8FeJaKdGoIFC2sM238k"
    model: str = "gemini-1.5-flash"
    temperature: float = 0.7
    max_tokens: int = 2048
    
    # System Configuration
    system_prompt: str = "You are a helpful AI assistant."
    max_conversation_length: int = 50
    
    # Rate Limiting
    requests_per_minute: int = 60
    max_retries: int = 3
    
    # Additional settings
    timeout: float = 30.0
    enable_logging: bool = True
    log_level: str = "INFO"
    
    # RAG Configuration (for future extension)
    enable_rag: bool = False
    rag_config: Optional[Dict[str, Any]] = field(default_factory=dict)
    
    @classmethod
    def from_env(cls, prefix: str = "CHATBOT_") -> "ChatbotConfig":
        """
        Create configuration from environment variables.
        
        Args:
            prefix: Prefix for environment variable names
            
        Returns:
            ChatbotConfig instance loaded from environment
            
        Raises:
            ConfigurationError: If required environment variables are missing
        """
        api_key = os.getenv(f"{prefix}API_KEY")
        if not api_key:
            raise ConfigurationError(f"Missing required environment variable: {prefix}API_KEY")
        
        return cls(
            api_key=api_key,
            model=os.getenv(f"{prefix}MODEL", "gemini-2.5-flash"),
            temperature=float(os.getenv(f"{prefix}TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv(f"{prefix}MAX_TOKENS", "2048")),
            system_prompt=os.getenv(f"{prefix}SYSTEM_PROMPT", "You are a helpful AI assistant."),
            max_conversation_length=int(os.getenv(f"{prefix}MAX_CONVERSATION_LENGTH", "50")),
            requests_per_minute=int(os.getenv(f"{prefix}REQUESTS_PER_MINUTE", "60")),
            max_retries=int(os.getenv(f"{prefix}MAX_RETRIES", "3")),
            timeout=float(os.getenv(f"{prefix}TIMEOUT", "30.0")),
            enable_logging=os.getenv(f"{prefix}ENABLE_LOGGING", "true").lower() == "true",
            log_level=os.getenv(f"{prefix}LOG_LEVEL", "INFO"),
            enable_rag=os.getenv(f"{prefix}ENABLE_RAG", "false").lower() == "true"
        )
    
    def validate(self) -> None:
        """
        Validate the configuration parameters.
        
        Raises:
            ConfigurationError: If any configuration parameter is invalid
        """
        if not self.api_key:
            raise ConfigurationError("API key cannot be empty")
        
        if not (0.0 <= self.temperature <= 2.0):
            raise ConfigurationError("Temperature must be between 0.0 and 2.0")
        
        if self.max_tokens <= 0:
            raise ConfigurationError("Max tokens must be positive")
        
        if self.max_conversation_length <= 0:
            raise ConfigurationError("Max conversation length must be positive")
        
        if self.requests_per_minute <= 0:
            raise ConfigurationError("Requests per minute must be positive")
        
        if self.max_retries < 0:
            raise ConfigurationError("Max retries cannot be negative")
        
        if self.timeout <= 0:
            raise ConfigurationError("Timeout must be positive")
        
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level.upper() not in valid_log_levels:
            raise ConfigurationError(f"Log level must be one of: {valid_log_levels}")
