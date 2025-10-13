"""
Test script for all chatbot API endpoints.

This script tests all endpoints with real API calls and handles environment setup.
"""

import asyncio
import os
import sys
import json
from pathlib import Path
from typing import Dict, Any

import httpx

# Add the server directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from chatbot.utils import build_chatbot_from_env


class ChatbotAPITester:
    """Test all chatbot API endpoints."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def test_health(self) -> bool:
        """Test /chatbot/health endpoint."""
        print("Testing /chatbot/health...")
        try:
            response = await self.client.get(f"{self.base_url}/chatbot/health")
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.json()}")
            return response.status_code == 200
        except Exception as e:
            print(f"  Error: {e}")
            return False
    
    async def test_chat(self, message: str = "Hello! Can you tell me a short joke?") -> bool:
        """Test /chatbot/chat endpoint."""
        print(f"Testing /chatbot/chat with message: '{message}'...")
        try:
            payload = {"message": message}
            response = await self.client.post(
                f"{self.base_url}/chatbot/chat",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  Response: {data.get('content', 'No content')[:100]}...")
                print(f"  Model: {data.get('model', 'Unknown')}")
                print(f"  Usage: {data.get('usage', {})}")
            else:
                print(f"  Error: {response.text}")
            return response.status_code == 200
        except Exception as e:
            print(f"  Error: {e}")
            return False
    
    async def test_chat_with_history(self) -> bool:
        """Test /chatbot/chat with conversation history."""
        print("Testing /chatbot/chat with conversation history...")
        try:
            payload = {
                "message": "What was my previous question?",
                "conversation_history": [
                    {"role": "user", "content": "Hello!"},
                    {"role": "assistant", "content": "Hi there! How can I help you today?"}
                ]
            }
            response = await self.client.post(
                f"{self.base_url}/chatbot/chat",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  Response: {data.get('content', 'No content')[:100]}...")
            else:
                print(f"  Error: {response.text}")
            return response.status_code == 200
        except Exception as e:
            print(f"  Error: {e}")
            return False
    
    async def test_history(self) -> bool:
        """Test /chatbot/history endpoint."""
        print("Testing /chatbot/history...")
        try:
            response = await self.client.get(f"{self.base_url}/chatbot/history")
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                history = response.json()
                print(f"  History length: {len(history)}")
                for i, msg in enumerate(history[-3:], 1):  # Show last 3 messages
                    print(f"    {i}. {msg.get('role', 'unknown')}: {msg.get('content', '')[:50]}...")
            else:
                print(f"  Error: {response.text}")
            return response.status_code == 200
        except Exception as e:
            print(f"  Error: {e}")
            return False
    
    async def test_reset(self) -> bool:
        """Test /chatbot/reset endpoint."""
        print("Testing /chatbot/reset...")
        try:
            response = await self.client.post(f"{self.base_url}/chatbot/reset")
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.json()}")
            return response.status_code == 200
        except Exception as e:
            print(f"  Error: {e}")
            return False
    
    async def test_error_handling(self) -> bool:
        """Test error handling with invalid requests."""
        print("Testing error handling...")
        
        # Test empty message
        try:
            payload = {"message": ""}
            response = await self.client.post(
                f"{self.base_url}/chatbot/chat",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            print(f"  Empty message - Status: {response.status_code}")
            if response.status_code != 200:
                print(f"    Error response: {response.json()}")
        except Exception as e:
            print(f"  Empty message error: {e}")
        
        # Test invalid JSON
        try:
            response = await self.client.post(
                f"{self.base_url}/chatbot/chat",
                content="invalid json",
                headers={"Content-Type": "application/json"}
            )
            print(f"  Invalid JSON - Status: {response.status_code}")
        except Exception as e:
            print(f"  Invalid JSON error: {e}")
        
        return True
    
    async def run_all_tests(self) -> Dict[str, bool]:
        """Run all tests and return results."""
        print("=" * 60)
        print("Chatbot API Test Suite")
        print("=" * 60)
        
        results = {}
        
        # Test health first
        results["health"] = await self.test_health()
        print()
        
        # Test chat
        results["chat"] = await self.test_chat()
        print()
        
        # Test chat with history
        results["chat_with_history"] = await self.test_chat_with_history()
        print()
        
        # Test history
        results["history"] = await self.test_history()
        print()
        
        # Test reset
        results["reset"] = await self.test_reset()
        print()
        
        # Test error handling
        results["error_handling"] = await self.test_error_handling()
        print()
        
        # Test history after reset
        results["history_after_reset"] = await self.test_history()
        print()
        
        return results
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


async def test_direct_chatbot():
    """Test chatbot directly without API."""
    print("Testing chatbot directly...")
    try:
        chatbot = build_chatbot_from_env()
        print("  Chatbot initialized successfully")
        
        # Test health
        is_healthy = chatbot.is_healthy()
        print(f"  Health check: {is_healthy}")
        
        # Test chat
        response = await chatbot.chat("Hello! This is a direct test.")
        print(f"  Direct chat response: {response.content[:100]}...")
        
        return True
    except Exception as e:
        print(f"  Direct test error: {e}")
        return False


async def check_environment():
    """Check environment variables."""
    print("Checking environment variables...")
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    chatbot_key = os.getenv("CHATBOT_API_KEY")
    
    print(f"  GEMINI_API_KEY: {'Set' if gemini_key else 'Not set'}")
    print(f"  CHATBOT_API_KEY: {'Set' if chatbot_key else 'Not set'}")
    
    if gemini_key:
        print(f"  GEMINI_API_KEY length: {len(gemini_key)}")
        print(f"  GEMINI_API_KEY starts with: {gemini_key[:10]}...")
    
    # Set CHATBOT_API_KEY if GEMINI_API_KEY is set
    if gemini_key and not chatbot_key:
        os.environ["CHATBOT_API_KEY"] = gemini_key
        print("  Set CHATBOT_API_KEY from GEMINI_API_KEY")
    
    return bool(gemini_key or chatbot_key)


async def main():
    """Run all tests."""
    print("Chatbot API Test Suite")
    print("=" * 60)
    
    # Check environment
    env_ok = await check_environment()
    if not env_ok:
        print("ERROR: No API key found in environment variables!")
        print("Please set GEMINI_API_KEY or CHATBOT_API_KEY")
        return
    
    print()
    
    # Test direct chatbot first
    direct_ok = await test_direct_chatbot()
    print()
    
    if not direct_ok:
        print("Direct chatbot test failed. Check your API key and configuration.")
        return
    
    # Test API endpoints
    tester = ChatbotAPITester()
    try:
        results = await tester.run_all_tests()
        
        # Summary
        print("=" * 60)
        print("Test Results Summary")
        print("=" * 60)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            status = "PASS" if result else "FAIL"
            print(f"  {test_name}: {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("All tests passed! 🎉")
        else:
            print("Some tests failed. Check the output above.")
            
    finally:
        await tester.close()


if __name__ == "__main__":
    asyncio.run(main())
