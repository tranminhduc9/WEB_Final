"""
Chatbot Package - AI-Powered Travel Assistant for Hanoivivu

This package provides the core chatbot functionality using Google's Gemini AI
with dynamic place context injection.

Usage:
    from app.chatbot import get_chat_service, get_place_context_service
    
    # Get relevant places from database
    place_service = get_place_context_service()
    places = await place_service.search_relevant_places(message, db)
    
    # Chat with places context
    chat_service = get_chat_service()
    response = await chat_service.chat(message, places=places)
"""

from .gemini_service import GeminiChatService, get_chat_service, reset_chat_service
from .config import ChatbotConfig, get_config, reload_config
from .prompts import HANOI_TRAVEL_PROMPT, build_prompt_with_places
from .place_context import PlaceContextService, get_place_context_service

__all__ = [
    # Services
    "GeminiChatService",
    "get_chat_service",
    "reset_chat_service",
    "PlaceContextService",
    "get_place_context_service",
    
    # Config
    "ChatbotConfig",
    "get_config",
    "reload_config",
    
    # Prompts
    "HANOI_TRAVEL_PROMPT",
    "build_prompt_with_places",
]

__version__ = "1.1.0"
