"""
Custom exceptions for the chatbot module.

This module defines specific exception types for different error scenarios
in the chatbot system, enabling better error handling and debugging.
"""

from typing import Optional, Dict, Any


class ChatbotError(Exception):
    """Base exception for all chatbot-related errors."""
    pass


class APIError(ChatbotError):
    """Raised when there's an error communicating with external AI APIs."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class ConfigurationError(ChatbotError):
    """Raised when there's an error in chatbot configuration."""
    pass


class ValidationError(ChatbotError):
    """Raised when input validation fails."""
    pass


class RateLimitError(APIError):
    """Raised when API rate limits are exceeded."""
    pass


class AuthenticationError(APIError):
    """Raised when API authentication fails."""
    pass
