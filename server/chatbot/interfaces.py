"""
Abstract interfaces for chatbot implementations.

This module defines the contract that all chatbot implementations must follow,
ensuring consistency and enabling easy swapping of different AI providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class ChatMessage:
    """Represents a single message in a conversation."""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ChatResponse:
    """Represents the response from a chatbot."""
    content: str
    metadata: Optional[Dict[str, Any]] = None
    usage: Optional[Dict[str, Any]] = None
    model: Optional[str] = None


class ChatbotInterface(ABC):
    """
    Abstract base class for all chatbot implementations.
    
    This interface ensures that all chatbot implementations provide
    consistent methods for conversation management and response generation.
    """
    
    @abstractmethod
    async def chat(self, message: str, conversation_history: Optional[List[ChatMessage]] = None) -> ChatResponse:
        """
        Process a user message and return a response.
        
        Args:
            message: The user's input message
            conversation_history: Optional list of previous messages in the conversation
            
        Returns:
            ChatResponse containing the assistant's response
            
        Raises:
            ChatbotError: If there's an error processing the message
        """
        pass
    
    @abstractmethod
    async def reset_conversation(self) -> None:
        """Reset the conversation state."""
        pass
    
    @abstractmethod
    def get_conversation_history(self) -> List[ChatMessage]:
        """Get the current conversation history."""
        pass
    
    @abstractmethod
    def is_healthy(self) -> bool:
        """Check if the chatbot is ready to process requests."""
        pass
