"""
Gemini Chat Service

Core service xử lý AI chatbot với Google Gemini.
Hỗ trợ place context injection để gợi ý địa điểm chính xác.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any

from .config import ChatbotConfig, get_config
from .prompts import build_prompt_with_places, is_greeting, GREETING_RESPONSES

logger = logging.getLogger(__name__)


class GeminiChatService:
    """
    Service xử lý AI chatbot với Gemini.
    
    Features:
    - Singleton pattern để tái sử dụng client
    - Place context injection cho gợi ý chính xác
    - Rate limiting đơn giản
    - Error handling với fallback response
    - Conversation history support
    
    Usage:
        service = GeminiChatService()
        response = await service.chat("Quán phở ngon ở Hoàn Kiếm?", places=[...])
    """
    
    def __init__(self, config: ChatbotConfig = None):
        """
        Initialize Gemini chat service.
        
        Args:
            config: ChatbotConfig instance, uses default if None
        """
        self.config = config or get_config()
        self._client = None
        self._last_request_time = 0.0
        self._initialized = False
        self._use_new_sdk = False
        
    def _init_client(self) -> bool:
        """
        Lazy initialize Gemini client.
        
        Returns:
            True if initialization successful, False otherwise
        """
        if self._initialized:
            return self._client is not None
            
        if not self.config.is_configured:
            logger.warning("Chatbot API key not configured or disabled")
            self._initialized = True
            return False
        
        try:
            # Try new google-genai SDK first (v1.0+)
            try:
                from google import genai
                self._client = genai.Client(api_key=self.config.api_key)
                self._use_new_sdk = True
                logger.info(f"Initialized Gemini client with new SDK, model: {self.config.model}")
            except ImportError:
                # Fallback to google-generativeai SDK
                import google.generativeai as genai
                genai.configure(api_key=self.config.api_key)
                self._client = genai.GenerativeModel(self.config.model)
                self._use_new_sdk = False
                logger.info(f"Initialized Gemini client with legacy SDK, model: {self.config.model}")
            
            self._initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            self._initialized = True
            return False
    
    async def _check_rate_limit(self) -> None:
        """Simple rate limiting - wait if needed."""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        
        if time_since_last < self.config.min_request_interval:
            await asyncio.sleep(self.config.min_request_interval - time_since_last)
        
        self._last_request_time = time.time()
    
    async def chat(
        self, 
        message: str, 
        conversation_history: List[Dict] = None,
        places: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Gửi tin nhắn và nhận response từ AI.
        
        Args:
            message: Tin nhắn từ người dùng
            conversation_history: Lịch sử hội thoại (optional)
            places: Danh sách địa điểm liên quan từ database (optional)
            
        Returns:
            Dict với keys: response, entities, suggested_place_ids
        """
        # Validate input
        if not message or not message.strip():
            return self._error_response("Tin nhắn không được để trống")
        
        # Check for greeting - respond without AI call
        if is_greeting(message):
            import random
            return {
                "response": random.choice(GREETING_RESPONSES),
                "entities": {},
                "suggested_place_ids": [p["id"] for p in (places or [])[:3]]
            }
        
        # Initialize client if needed
        if not self._init_client():
            return self._fallback_response()
        
        # Rate limiting
        await self._check_rate_limit()
        
        try:
            # Build prompt with places context
            full_prompt = build_prompt_with_places(
                message=message,
                places=places or [],
                history=conversation_history
            )
            
            # Generate response
            response_text = await self._generate_response(full_prompt)
            
            if not response_text:
                return self._fallback_response()
            
            if self.config.enable_logging:
                logger.info(f"Generated response for: {message[:50]}...")
            
            # Extract suggested place IDs from places context
            suggested_ids = [p["id"] for p in (places or [])[:3]]
            
            return {
                "response": response_text,
                "entities": {},
                "suggested_place_ids": suggested_ids
            }
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return self._error_response(str(e))
    
    async def _generate_response(self, prompt: str) -> Optional[str]:
        """
        Generate response using Gemini API.
        
        Args:
            prompt: Full prompt with system instructions and history
            
        Returns:
            Generated text or None on error
        """
        try:
            if self._use_new_sdk:
                # New google-genai SDK
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        self._client.models.generate_content,
                        model=self.config.model,
                        contents=prompt
                    ),
                    timeout=self.config.timeout
                )
                return response.text if response.text else None
            else:
                # Legacy google-generativeai SDK
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        self._client.generate_content,
                        prompt
                    ),
                    timeout=self.config.timeout
                )
                return response.text if response.text else None
                
        except asyncio.TimeoutError:
            logger.error(f"Request timed out after {self.config.timeout}s")
            return None
        except Exception as e:
            logger.error(f"Generate response error: {e}")
            return None
    
    def _fallback_response(self) -> Dict[str, Any]:
        """Return fallback response when AI is unavailable."""
        return {
            "response": "Xin lỗi, hệ thống AI đang bảo trì. Vui lòng thử lại sau hoặc liên hệ hỗ trợ.",
            "entities": {},
            "suggested_place_ids": []
        }
    
    def _error_response(self, error_msg: str) -> Dict[str, Any]:
        """Return error response."""
        logger.warning(f"Returning error response: {error_msg}")
        return {
            "response": "Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại sau.",
            "entities": {},
            "suggested_place_ids": []
        }
    
    @property
    def is_healthy(self) -> bool:
        """Check if service is ready."""
        return self._init_client()


# Singleton service instance
_service: Optional[GeminiChatService] = None


def get_chat_service() -> GeminiChatService:
    """Get singleton chat service instance."""
    global _service
    if _service is None:
        _service = GeminiChatService()
    return _service


def reset_chat_service() -> GeminiChatService:
    """Reset and get new service instance."""
    global _service
    _service = GeminiChatService()
    return _service
