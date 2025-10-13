"""
Test script for the chatbot module.

This script demonstrates the chatbot functionality and runs basic tests
to verify everything is working correctly.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the server directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from chatbot.config import ChatbotConfig
from chatbot.gemini_chatbot import GeminiChatbot
from chatbot.factory import ChatbotFactory
from chatbot.exceptions import ValidationError, ConfigurationError


async def test_configuration():
    """Test configuration management."""
    print("Testing Configuration Management...")
    
    # Test valid configuration
    try:
        config = ChatbotConfig(
            api_key="test-api-key",
            model="gemini-1.5-flash",
            temperature=0.7,
            max_tokens=1000
        )
        config.validate()
        print("   [OK] Valid configuration created successfully")
    except Exception as e:
        print(f"   [ERROR] Configuration error: {e}")
        return False
    
    # Test invalid configuration
    try:
        config = ChatbotConfig(api_key="", temperature=5.0)
        config.validate()
        print("   [ERROR] Should have failed with invalid config")
        return False
    except ConfigurationError:
        print("   [OK] Invalid configuration properly rejected")
    
    # Test environment variable loading
    try:
        os.environ["CHATBOT_API_KEY"] = "env-test-key"
        os.environ["CHATBOT_MODEL"] = "gemini-1.5-pro"
        config = ChatbotConfig.from_env()
        print(f"   [OK] Environment config loaded: model={config.model}")
    except Exception as e:
        print(f"   [ERROR] Environment config error: {e}")
        return False
    
    return True


async def test_factory_pattern():
    """Test factory pattern."""
    print("\nTesting Factory Pattern...")
    
    try:
        config = ChatbotConfig(api_key="test-key")
        
        # Test creating chatbot
        chatbot = ChatbotFactory.create_chatbot(config, "gemini")
        print("   [OK] Chatbot created using factory")
        
        # Test getting available types
        types = ChatbotFactory.get_available_types()
        print(f"   [OK] Available types: {types}")
        
        return True
    except Exception as e:
        print(f"   [ERROR] Factory pattern error: {e}")
        return False


async def test_chatbot_interface():
    """Test chatbot interface methods."""
    print("\nTesting Chatbot Interface...")
    
    try:
        config = ChatbotConfig(api_key="test-key")
        
        # Mock the Gemini API to avoid actual API calls
        with unittest.mock.patch('chatbot.gemini_chatbot.genai') as mock_genai:
            mock_model = unittest.mock.Mock()
            mock_response = unittest.mock.Mock()
            mock_response.text = "Test response"
            mock_model.generate_content.return_value = mock_response
            mock_genai.configure = unittest.mock.Mock()
            mock_genai.GenerativeModel.return_value = mock_model
            
            chatbot = GeminiChatbot(config)
            
            # Test health check
            is_healthy = chatbot.is_healthy()
            print(f"   [OK] Health check: {is_healthy}")
            
            # Test conversation history
            history = chatbot.get_conversation_history()
            print(f"   [OK] Initial history length: {len(history)}")
            
            # Test reset conversation
            await chatbot.reset_conversation()
            history = chatbot.get_conversation_history()
            print(f"   [OK] After reset history length: {len(history)}")
            
            return True
    except Exception as e:
        print(f"   [ERROR] Interface test error: {e}")
        return False


async def test_error_handling():
    """Test error handling."""
    print("\nTesting Error Handling...")
    
    try:
        config = ChatbotConfig(api_key="test-key")
        
        with unittest.mock.patch('chatbot.gemini_chatbot.genai'):
            chatbot = GeminiChatbot(config)
            
            # Test empty message validation
            try:
                await chatbot.chat("")
                print("   [ERROR] Should have failed with empty message")
                return False
            except ValidationError:
                print("   [OK] Empty message properly rejected")
            
            # Test whitespace-only message
            try:
                await chatbot.chat("   ")
                print("   [ERROR] Should have failed with whitespace message")
                return False
            except ValidationError:
                print("   [OK] Whitespace message properly rejected")
            
            return True
    except Exception as e:
        print(f"   [ERROR] Error handling test error: {e}")
        return False


async def test_conversation_management():
    """Test conversation management."""
    print("\nTesting Conversation Management...")
    
    try:
        config = ChatbotConfig(
            api_key="test-key",
            max_conversation_length=3
        )
        
        with unittest.mock.patch('chatbot.gemini_chatbot.genai') as mock_genai:
            mock_model = unittest.mock.Mock()
            mock_response = unittest.mock.Mock()
            mock_response.text = "Test response"
            mock_model.generate_content.return_value = mock_response
            mock_genai.configure = unittest.mock.Mock()
            mock_genai.GenerativeModel.return_value = mock_model
            
            chatbot = GeminiChatbot(config)
            
            # Add multiple messages
            for i in range(5):
                response = await chatbot.chat(f"Message {i+1}")
                history_length = len(chatbot.get_conversation_history())
                print(f"   Message {i+1}: History length = {history_length}")
            
            # Should be limited to max_conversation_length
            final_history = chatbot.get_conversation_history()
            if len(final_history) <= config.max_conversation_length:
                print("   [OK] Conversation length properly limited")
            else:
                print(f"   [ERROR] Conversation length not limited: {len(final_history)}")
                return False
            
            return True
    except Exception as e:
        print(f"   [ERROR] Conversation management test error: {e}")
        return False


async def run_all_tests():
    """Run all tests."""
    print("Running Chatbot Module Tests")
    print("=" * 50)
    
    tests = [
        test_configuration,
        test_factory_pattern,
        test_chatbot_interface,
        test_error_handling,
        test_conversation_management
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            result = await test()
            if result:
                passed += 1
        except Exception as e:
            print(f"   [ERROR] Test failed with exception: {e}")
    
    print(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed!")
        return True
    else:
        print("Some tests failed!")
        return False


if __name__ == "__main__":
    import unittest.mock
    
    # Run the tests
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
