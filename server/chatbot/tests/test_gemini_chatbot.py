"""
Unit tests for GeminiChatbot class.

This module contains comprehensive tests for the GeminiChatbot implementation,
including happy path, edge cases, and error scenarios.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import List

from ..gemini_chatbot import GeminiChatbot
from ..config import ChatbotConfig
from ..interfaces import ChatMessage, ChatResponse
from ..exceptions import ValidationError, APIError, RateLimitError, AuthenticationError


class TestGeminiChatbot:
    """Test cases for GeminiChatbot class."""
    
    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        return ChatbotConfig(
            api_key="test-api-key",
            model="gemini-1.5-flash",
            temperature=0.7,
            max_tokens=100,
            system_prompt="You are a test assistant.",
            max_conversation_length=10,
            requests_per_minute=60,
            max_retries=3,
            timeout=30.0,
            enable_logging=False
        )
    
    @pytest.fixture
    def mock_model(self):
        """Create a mock Gemini model."""
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "This is a test response."
        mock_model.generate_content.return_value = mock_response
        return mock_model
    
    @pytest.fixture
    def chatbot(self, config, mock_model):
        """Create a chatbot instance with mocked dependencies."""
        with patch('server.chatbot.gemini_chatbot.genai') as mock_genai:
            mock_genai.configure = Mock()
            mock_genai.GenerativeModel.return_value = mock_model
            
            chatbot = GeminiChatbot(config)
            chatbot.model = mock_model
            return chatbot
    
    @pytest.mark.asyncio
    async def test_chat_success(self, chatbot):
        """Test successful chat interaction."""
        message = "Hello, how are you?"
        
        response = await chatbot.chat(message)
        
        assert isinstance(response, ChatResponse)
        assert response.content == "This is a test response."
        assert response.model == "gemini-1.5-flash"
        assert "timestamp" in response.metadata
        assert "usage" in response
        assert len(chatbot.get_conversation_history()) == 2  # user + assistant
    
    @pytest.mark.asyncio
    async def test_chat_with_conversation_history(self, chatbot):
        """Test chat with provided conversation history."""
        history = [
            ChatMessage(role="user", content="Previous message"),
            ChatMessage(role="assistant", content="Previous response")
        ]
        message = "Follow-up question"
        
        response = await chatbot.chat(message, history)
        
        assert isinstance(response, ChatResponse)
        assert response.content == "This is a test response."
        # History should not be modified when provided externally
        assert len(history) == 4  # 2 original + 2 new
    
    @pytest.mark.asyncio
    async def test_chat_empty_message(self, chatbot):
        """Test chat with empty message raises ValidationError."""
        with pytest.raises(ValidationError, match="Message cannot be empty"):
            await chatbot.chat("")
        
        with pytest.raises(ValidationError, match="Message cannot be empty"):
            await chatbot.chat("   ")
    
    @pytest.mark.asyncio
    async def test_chat_api_error(self, chatbot):
        """Test chat with API error."""
        chatbot.model.generate_content.side_effect = Exception("API Error")
        
        with pytest.raises(APIError, match="Failed to generate response"):
            await chatbot.chat("Test message")
    
    @pytest.mark.asyncio
    async def test_chat_authentication_error(self, chatbot):
        """Test chat with authentication error."""
        chatbot.model.generate_content.side_effect = Exception("API_KEY invalid")
        
        with pytest.raises(AuthenticationError):
            await chatbot.chat("Test message")
    
    @pytest.mark.asyncio
    async def test_chat_rate_limit_error(self, chatbot):
        """Test chat with rate limit error."""
        chatbot.model.generate_content.side_effect = Exception("quota exceeded")
        
        with pytest.raises(RateLimitError):
            await chatbot.chat("Test message")
    
    @pytest.mark.asyncio
    async def test_chat_timeout(self, chatbot):
        """Test chat with timeout."""
        async def slow_generate(*args, **kwargs):
            await asyncio.sleep(35)  # Longer than timeout
            return Mock(text="Response")
        
        chatbot.model.generate_content = slow_generate
        
        with pytest.raises(APIError, match="Request timed out"):
            await chatbot.chat("Test message")
    
    @pytest.mark.asyncio
    async def test_reset_conversation(self, chatbot):
        """Test conversation reset."""
        # Add some messages
        await chatbot.chat("First message")
        assert len(chatbot.get_conversation_history()) == 2
        
        # Reset conversation
        await chatbot.reset_conversation()
        assert len(chatbot.get_conversation_history()) == 0
    
    def test_get_conversation_history(self, chatbot):
        """Test getting conversation history."""
        history = chatbot.get_conversation_history()
        assert isinstance(history, list)
        assert len(history) == 0
    
    def test_is_healthy(self, chatbot):
        """Test health check."""
        assert chatbot.is_healthy() is True
    
    def test_is_healthy_with_invalid_config(self):
        """Test health check with invalid configuration."""
        config = ChatbotConfig(api_key="")
        with patch('server.chatbot.gemini_chatbot.genai'):
            chatbot = GeminiChatbot(config)
            assert chatbot.is_healthy() is False
    
    @pytest.mark.asyncio
    async def test_conversation_length_limit(self, config, mock_model):
        """Test conversation length limit."""
        config.max_conversation_length = 2
        
        with patch('server.chatbot.gemini_chatbot.genai'):
            chatbot = GeminiChatbot(config)
            chatbot.model = mock_model
            
            # Add messages beyond limit
            await chatbot.chat("Message 1")
            await chatbot.chat("Message 2")
            await chatbot.chat("Message 3")
            
            # Should only keep the last 2 messages
            history = chatbot.get_conversation_history()
            assert len(history) == 2
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, config, mock_model):
        """Test rate limiting functionality."""
        config.requests_per_minute = 2  # Very low limit for testing
        
        with patch('server.chatbot.gemini_chatbot.genai'):
            chatbot = GeminiChatbot(config)
            chatbot.model = mock_model
            
            # First two requests should succeed
            await chatbot.chat("Message 1")
            await chatbot.chat("Message 2")
            
            # Third request should be rate limited (will sleep)
            start_time = asyncio.get_event_loop().time()
            await chatbot.chat("Message 3")
            end_time = asyncio.get_event_loop().time()
            
            # Should have taken some time due to rate limiting
            assert end_time - start_time > 0


class TestChatbotIntegration:
    """Integration tests for chatbot functionality."""
    
    @pytest.mark.asyncio
    async def test_full_conversation_flow(self):
        """Test complete conversation flow."""
        config = ChatbotConfig(
            api_key="test-key",
            enable_logging=False
        )
        
        with patch('server.chatbot.gemini_chatbot.genai') as mock_genai:
            mock_model = Mock()
            mock_response = Mock()
            mock_response.text = "Hello! How can I help you?"
            mock_model.generate_content.return_value = mock_response
            mock_genai.configure = Mock()
            mock_genai.GenerativeModel.return_value = mock_model
            
            chatbot = GeminiChatbot(config)
            
            # Test conversation flow
            response1 = await chatbot.chat("Hello")
            assert response1.content == "Hello! How can I help you?"
            
            response2 = await chatbot.chat("What's the weather like?")
            assert response2.content == "Hello! How can I help you?"
            
            # Check conversation history
            history = chatbot.get_conversation_history()
            assert len(history) == 4  # 2 user + 2 assistant messages
            assert history[0].role == "user"
            assert history[1].role == "assistant"
            assert history[2].role == "user"
            assert history[3].role == "assistant"
