"""
Simple demo for testing the simplified Gemini chatbot.

This script demonstrates the basic usage of the chatbot with real API calls.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the server directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from chatbot.config import ChatbotConfig
from chatbot.gemini_chatbot import GeminiChatbot


async def simple_chat_demo():
    """Simple chat demo with real API."""
    print("=== Simple Gemini Chatbot Demo ===")
    
    # Get API key from environment or use the one from test file
    api_key = os.getenv("GEMINI_API_KEY") or "AIzaSyBwGc5TQ14IpygA8FeJaKdGoIFC2sM238k"
    
    try:
        # Create simple configuration
        config = ChatbotConfig(
            api_key=api_key,
            model="gemini-2.5-flash",  # Use the latest model
            temperature=0.7,
            max_tokens=500,
            system_prompt="You are a helpful AI assistant. Keep responses concise.",
            enable_logging=True
        )
        
        # Create chatbot
        chatbot = GeminiChatbot(config)
        
        print(f"Chatbot initialized with model: {config.model}")
        print("Type 'quit' to exit, 'reset' to clear history")
        print("-" * 50)
        
        # Test basic functionality
        print("\nTesting basic chat...")
        response = await chatbot.chat("Hello! Can you tell me a short joke?")
        print(f"Bot: {response.content}")
        
        print("\nTesting conversation history...")
        response = await chatbot.chat("What was my previous question?")
        print(f"Bot: {response.content}")
        
        print(f"\nConversation history length: {len(chatbot.get_conversation_history())}")
        
        # Interactive chat loop
        print("\nStarting interactive chat...")
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                elif user_input.lower() == 'reset':
                    await chatbot.reset_conversation()
                    print("Conversation history cleared!")
                    continue
                elif not user_input:
                    print("Please enter a message.")
                    continue
                
                # Get response
                print("Bot: ", end="", flush=True)
                response = await chatbot.chat(user_input)
                print(response.content)
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
        
    except Exception as e:
        print(f"Failed to initialize chatbot: {e}")


async def test_api_connection():
    """Test API connection without full chatbot."""
    print("=== Testing API Connection ===")
    
    api_key = os.getenv("GEMINI_API_KEY") or "AIzaSyBwGc5TQ14IpygA8FeJaKdGoIFC2sM238k"
    
    try:
        from google import genai
        
        # Test direct API call
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Say hello in English"
        )
        
        print(f"API Response: {response.text}")
        print("[OK] API connection successful!")
        
    except Exception as e:
        print(f"[ERROR] API connection failed: {e}")


async def main():
    """Run the demo."""
    print("Gemini Chatbot Simple Demo")
    print("=" * 40)
    
    # Test API connection first
    await test_api_connection()
    
    # Ask user if they want to try interactive chat
    print("\nWould you like to try interactive chat? (y/n): ", end="")
    try:
        choice = input().strip().lower()
        if choice in ['y', 'yes']:
            await simple_chat_demo()
        else:
            print("Demo completed!")
    except (KeyboardInterrupt, EOFError):
        print("\nDemo completed!")


if __name__ == "__main__":
    asyncio.run(main())
