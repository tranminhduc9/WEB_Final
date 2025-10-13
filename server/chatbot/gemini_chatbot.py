"""
Gemini AI chatbot implementation.

This module provides a concrete implementation of the ChatbotInterface
using Google's Gemini AI API for generating responses.
"""

import asyncio
import logging
import time
from typing import List, Optional, Dict, Any
from google import genai

from .interfaces import ChatbotInterface, ChatMessage, ChatResponse
from .config import ChatbotConfig
from .exceptions import APIError, AuthenticationError, RateLimitError, ValidationError


class GeminiChatbot(ChatbotInterface):
    """
    Gemini AI-powered chatbot implementation.
    
    This class provides a complete chatbot implementation using Google's
    Gemini AI API, with proper error handling, rate limiting, and conversation
    management.
    """
    
    def __init__(self, config: ChatbotConfig):
        """
        Initialize the Gemini chatbot.
        
        Args:
            config: ChatbotConfig instance with all necessary settings
            
        Raises:
            ConfigurationError: If configuration is invalid
            AuthenticationError: If API key is invalid
        """
        self.config = config
        self.config.validate()
        
        # Initialize Gemini AI client
        self.client = genai.Client(api_key=config.api_key)
        
        # Conversation state
        self._conversation_history: List[ChatMessage] = []
        self._last_request_time = 0.0
        
        # Setup logging
        self._setup_logging()
        
    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        if not self.config.enable_logging:
            return
            
        logging.basicConfig(
            level=getattr(logging, self.config.log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    async def chat(self, message: str, conversation_history: Optional[List[ChatMessage]] = None) -> ChatResponse:
        """
        Process a user message and return a response.
        
        Args:
            message: The user's input message
            conversation_history: Optional list of previous messages
            
        Returns:
            ChatResponse containing the assistant's response
            
        Raises:
            ValidationError: If input validation fails
            RateLimitError: If rate limit is exceeded
            APIError: If there's an error with the API
        """
        # Input validation
        if not message or not message.strip():
            raise ValidationError("Message cannot be empty")
        
        # Rate limiting check
        await self._check_rate_limit()
        
        # Use provided history or current conversation
        history = conversation_history or self._conversation_history
        
        try:
            # Add user message to history
            user_message = ChatMessage(
                role="user",
                content=message.strip(),
                timestamp=time.time()
            )
            history.append(user_message)
            
            # Prepare conversation for Gemini
            conversation_text = self._format_conversation_for_gemini(history)
            
            # Generate response
            response = await self._generate_response(conversation_text)
            
            # Create response object
            chat_response = ChatResponse(
                content=response.text,
                metadata={
                    "model": self.config.model,
                    "temperature": self.config.temperature,
                    "timestamp": time.time()
                },
                usage={
                    "prompt_tokens": len(conversation_text.split()),
                    "completion_tokens": len(response.text.split()),
                    "total_tokens": len(conversation_text.split()) + len(response.text.split())
                },
                model=self.config.model
            )
            
            # Add assistant response to history
            assistant_message = ChatMessage(
                role="assistant",
                content=response.text,
                timestamp=time.time()
            )
            history.append(assistant_message)
            
            # Update conversation history
            self._conversation_history = history[-self.config.max_conversation_length:]
            
            if self.config.enable_logging:
                self.logger.info(f"Generated response for message: {message[:50]}...")
            
            return chat_response
            
        except Exception as e:
            if self.config.enable_logging:
                self.logger.error(f"Error generating response: {str(e)}")
            raise APIError(f"Failed to generate response: {str(e)}")
    
    async def _generate_response(self, conversation_text: str) -> Any:
        """Generate response using Gemini API."""
        try:
            # Add system prompt if not already present
            if not conversation_text.startswith("System:"):
                conversation_text = f"System: {self.config.system_prompt}\n\n{conversation_text}"
            
            # Generate response with timeout
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.client.models.generate_content,
                    model=self.config.model,
                    contents=conversation_text
                ),
                timeout=self.config.timeout
            )
            
            if not response.text:
                raise APIError("Empty response from Gemini API")
            
            return response
            
        except asyncio.TimeoutError:
            raise APIError(f"Request timed out after {self.config.timeout} seconds")
        except Exception as e:
            if "API_KEY" in str(e) or "authentication" in str(e).lower():
                raise AuthenticationError(f"Authentication failed: {str(e)}")
            elif "quota" in str(e).lower() or "rate" in str(e).lower():
                raise RateLimitError(f"Rate limit exceeded: {str(e)}")
            else:
                raise APIError(f"API error: {str(e)}")
    
    def _format_conversation_for_gemini(self, history: List[ChatMessage]) -> str:
        """Format conversation history for Gemini API."""
        formatted_parts = []
        
        for message in history:
            if message.role == "system":
                formatted_parts.append(f"System: {message.content}")
            elif message.role == "user":
                formatted_parts.append(f"User: {message.content}")
            elif message.role == "assistant":
                formatted_parts.append(f"Assistant: {message.content}")
        
        return "\n\n".join(formatted_parts)
    
    async def _check_rate_limit(self) -> None:
        """Simple rate limiting check."""
        current_time = time.time()
        
        # Simple rate limiting - just check minimum interval between requests
        time_since_last = current_time - self._last_request_time
        min_interval = 1.0  # 1 second between requests
        if time_since_last < min_interval:
            await asyncio.sleep(min_interval - time_since_last)
        
        self._last_request_time = time.time()
    
    async def reset_conversation(self) -> None:
        """Reset the conversation state."""
        self._conversation_history.clear()
        if self.config.enable_logging:
            self.logger.info("Conversation reset")
    
    def get_conversation_history(self) -> List[ChatMessage]:
        """Get the current conversation history."""
        return self._conversation_history.copy()
    
    def is_healthy(self) -> bool:
        """Check if the chatbot is ready to process requests."""
        return bool(self.config.api_key)
