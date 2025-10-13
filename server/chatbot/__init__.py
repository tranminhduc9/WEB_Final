"""
Chatbot module for AI-powered conversation system.

This module provides a flexible chatbot architecture that supports multiple
AI providers and is designed for easy extension with RAG capabilities.
"""

from .interfaces import ChatbotInterface
from .gemini_chatbot import GeminiChatbot
from .config import ChatbotConfig
from .exceptions import ChatbotError, APIError, ConfigurationError

__version__ = "1.0.0"
__all__ = [
    "ChatbotInterface",
    "GeminiChatbot", 
    "ChatbotConfig",
    "ChatbotError",
    "APIError",
    "ConfigurationError"
]
