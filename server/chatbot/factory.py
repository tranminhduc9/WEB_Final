"""
Factory for creating chatbot instances.

This module provides a factory pattern implementation for creating
different types of chatbot instances based on configuration.
"""

from typing import Type, Dict, Any
from .interfaces import ChatbotInterface
from .gemini_chatbot import GeminiChatbot
from .config import ChatbotConfig
from .exceptions import ConfigurationError


class ChatbotFactory:
    """
    Factory class for creating chatbot instances.
    
    This class provides a centralized way to create different types
    of chatbot implementations based on configuration.
    """
    
    # Registry of available chatbot implementations
    _registry: Dict[str, Type[ChatbotInterface]] = {
        "gemini": GeminiChatbot,
    }
    
    @classmethod
    def create_chatbot(cls, config: ChatbotConfig, 
                      chatbot_type: str = "gemini") -> ChatbotInterface:
        """
        Create a chatbot instance based on the specified type.
        
        Args:
            config: ChatbotConfig instance
            chatbot_type: Type of chatbot to create ("gemini", etc.)
            
        Returns:
            ChatbotInterface instance
            
        Raises:
            ConfigurationError: If chatbot type is not supported
        """
        if chatbot_type not in cls._registry:
            available_types = ", ".join(cls._registry.keys())
            raise ConfigurationError(
                f"Unsupported chatbot type: {chatbot_type}. "
                f"Available types: {available_types}"
            )
        
        chatbot_class = cls._registry[chatbot_type]
        return chatbot_class(config)
    
    @classmethod
    def register_chatbot(cls, name: str, chatbot_class: Type[ChatbotInterface]) -> None:
        """
        Register a new chatbot implementation.
        
        Args:
            name: Name to register the chatbot under
            chatbot_class: ChatbotInterface implementation class
        """
        if not issubclass(chatbot_class, ChatbotInterface):
            raise ConfigurationError(
                f"Chatbot class must implement ChatbotInterface"
            )
        
        cls._registry[name] = chatbot_class
    
    @classmethod
    def get_available_types(cls) -> list[str]:
        """Get list of available chatbot types."""
        return list(cls._registry.keys())
