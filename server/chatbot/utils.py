"""
Utility helpers for the chatbot API layer.
"""

from __future__ import annotations

import os
from typing import List, Optional

from .interfaces import ChatMessage, ChatResponse
from .config import ChatbotConfig
from .exceptions import (
    ConfigurationError,
    ValidationError,
    RateLimitError,
    APIError,
    AuthenticationError,
    ChatbotError,
)
from .gemini_chatbot import GeminiChatbot


def build_chatbot_from_env() -> GeminiChatbot:
    """Create a GeminiChatbot using environment variables.

    Prefers GEMINI_API_KEY, falls back to CHATBOT_API_KEY.
    """
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("CHATBOT_API_KEY")
    if not api_key:
        raise ConfigurationError("Missing GEMINI_API_KEY/CHATBOT_API_KEY")

    # Create config manually to avoid prefix issues
    model = os.getenv("CHATBOT_MODEL", "gemini-2.5-flash")
    temperature = float(os.getenv("CHATBOT_TEMPERATURE", "0.7"))
    max_tokens = int(os.getenv("CHATBOT_MAX_TOKENS", "1024"))
    system_prompt = os.getenv("CHATBOT_SYSTEM_PROMPT", "You are a helpful AI assistant.")
    enable_logging = os.getenv("CHATBOT_ENABLE_LOGGING", "true").lower() == "true"
    log_level = os.getenv("CHATBOT_LOG_LEVEL", "INFO")

    cfg = ChatbotConfig(
        api_key=api_key,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        system_prompt=system_prompt,
        enable_logging=enable_logging,
        log_level=log_level,
    )
    cfg.validate()
    return GeminiChatbot(cfg)


def to_domain_history(history: Optional[List[dict]]) -> Optional[List[ChatMessage]]:
    """Convert list of dict (role, content, timestamp, metadata) to ChatMessage list."""
    if history is None:
        return None
    return [
        ChatMessage(
            role=m.get("role", "user"),
            content=str(m.get("content", "")),
            timestamp=m.get("timestamp"),
            metadata=m.get("metadata"),
        )
        for m in history
    ]


def to_response_dict(resp: ChatResponse) -> dict:
    """Convert ChatResponse to a serializable dict."""
    return {
        "content": resp.content,
        "metadata": resp.metadata,
        "usage": resp.usage,
        "model": resp.model,
    }


def map_exception(exc: Exception) -> tuple[int, str]:
    """Map domain exceptions to HTTP status code and message."""
    if isinstance(exc, ValidationError):
        return 400, str(exc)
    if isinstance(exc, RateLimitError):
        return 429, str(exc)
    if isinstance(exc, (AuthenticationError, )):
        return 401, str(exc)
    if isinstance(exc, (ConfigurationError, )):
        return 500, str(exc)
    if isinstance(exc, (APIError, ChatbotError)):
        return 502, str(exc)
    return 500, "Internal server error"


