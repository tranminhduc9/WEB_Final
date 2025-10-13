"""
Unit tests for ChatbotConfig class.

This module contains tests for configuration management,
validation, and environment variable loading.
"""

import pytest
import os
from unittest.mock import patch

from ..config import ChatbotConfig
from ..exceptions import ConfigurationError


class TestChatbotConfig:
    """Test cases for ChatbotConfig class."""
    
    def test_valid_config(self):
        """Test creating a valid configuration."""
        config = ChatbotConfig(
            api_key="test-key",
            model="gemini-1.5-flash",
            temperature=0.7,
            max_tokens=1000
        )
        
        assert config.api_key == "test-key"
        assert config.model == "gemini-1.5-flash"
        assert config.temperature == 0.7
        assert config.max_tokens == 1000
    
    def test_config_validation_success(self):
        """Test successful configuration validation."""
        config = ChatbotConfig(
            api_key="test-key",
            temperature=1.0,
            max_tokens=1000,
            max_conversation_length=50,
            requests_per_minute=60,
            max_retries=3,
            timeout=30.0,
            log_level="INFO"
        )
        
        # Should not raise any exception
        config.validate()
    
    def test_config_validation_empty_api_key(self):
        """Test validation with empty API key."""
        config = ChatbotConfig(api_key="")
        
        with pytest.raises(ConfigurationError, match="API key cannot be empty"):
            config.validate()
    
    def test_config_validation_invalid_temperature(self):
        """Test validation with invalid temperature."""
        config = ChatbotConfig(api_key="test-key", temperature=3.0)
        
        with pytest.raises(ConfigurationError, match="Temperature must be between 0.0 and 2.0"):
            config.validate()
        
        config = ChatbotConfig(api_key="test-key", temperature=-1.0)
        
        with pytest.raises(ConfigurationError, match="Temperature must be between 0.0 and 2.0"):
            config.validate()
    
    def test_config_validation_invalid_max_tokens(self):
        """Test validation with invalid max tokens."""
        config = ChatbotConfig(api_key="test-key", max_tokens=0)
        
        with pytest.raises(ConfigurationError, match="Max tokens must be positive"):
            config.validate()
        
        config = ChatbotConfig(api_key="test-key", max_tokens=-100)
        
        with pytest.raises(ConfigurationError, match="Max tokens must be positive"):
            config.validate()
    
    def test_config_validation_invalid_conversation_length(self):
        """Test validation with invalid conversation length."""
        config = ChatbotConfig(api_key="test-key", max_conversation_length=0)
        
        with pytest.raises(ConfigurationError, match="Max conversation length must be positive"):
            config.validate()
    
    def test_config_validation_invalid_requests_per_minute(self):
        """Test validation with invalid requests per minute."""
        config = ChatbotConfig(api_key="test-key", requests_per_minute=0)
        
        with pytest.raises(ConfigurationError, match="Requests per minute must be positive"):
            config.validate()
    
    def test_config_validation_invalid_max_retries(self):
        """Test validation with invalid max retries."""
        config = ChatbotConfig(api_key="test-key", max_retries=-1)
        
        with pytest.raises(ConfigurationError, match="Max retries cannot be negative"):
            config.validate()
    
    def test_config_validation_invalid_timeout(self):
        """Test validation with invalid timeout."""
        config = ChatbotConfig(api_key="test-key", timeout=0)
        
        with pytest.raises(ConfigurationError, match="Timeout must be positive"):
            config.validate()
    
    def test_config_validation_invalid_log_level(self):
        """Test validation with invalid log level."""
        config = ChatbotConfig(api_key="test-key", log_level="INVALID")
        
        with pytest.raises(ConfigurationError, match="Log level must be one of"):
            config.validate()
    
    @patch.dict(os.environ, {
        'CHATBOT_API_KEY': 'env-api-key',
        'CHATBOT_MODEL': 'gemini-1.5-pro',
        'CHATBOT_TEMPERATURE': '0.5',
        'CHATBOT_MAX_TOKENS': '2000'
    })
    def test_from_env_success(self):
        """Test loading configuration from environment variables."""
        config = ChatbotConfig.from_env()
        
        assert config.api_key == "env-api-key"
        assert config.model == "gemini-1.5-pro"
        assert config.temperature == 0.5
        assert config.max_tokens == 2000
    
    @patch.dict(os.environ, {}, clear=True)
    def test_from_env_missing_api_key(self):
        """Test loading configuration with missing API key."""
        with pytest.raises(ConfigurationError, match="Missing required environment variable"):
            ChatbotConfig.from_env()
    
    @patch.dict(os.environ, {
        'CHATBOT_API_KEY': 'test-key',
        'CHATBOT_TEMPERATURE': 'invalid'
    })
    def test_from_env_invalid_values(self):
        """Test loading configuration with invalid values."""
        with pytest.raises(ValueError):
            ChatbotConfig.from_env()
    
    @patch.dict(os.environ, {
        'CHATBOT_API_KEY': 'test-key',
        'CHATBOT_ENABLE_RAG': 'true'
    })
    def test_from_env_with_rag(self):
        """Test loading configuration with RAG enabled."""
        config = ChatbotConfig.from_env()
        
        assert config.enable_rag is True
    
    def test_default_values(self):
        """Test default configuration values."""
        config = ChatbotConfig(api_key="test-key")
        
        assert config.model == "gemini-1.5-flash"
        assert config.temperature == 0.7
        assert config.max_tokens == 2048
        assert config.system_prompt == "You are a helpful AI assistant."
        assert config.max_conversation_length == 50
        assert config.requests_per_minute == 60
        assert config.max_retries == 3
        assert config.timeout == 30.0
        assert config.enable_logging is True
        assert config.log_level == "INFO"
        assert config.enable_rag is False
