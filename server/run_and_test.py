"""
Run the chatbot API server and test all endpoints.
"""

import os
import subprocess
import time
import asyncio
import httpx
import sys
from pathlib import Path

# Add the server directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from chatbot.utils import build_chatbot_from_env


async def test_endpoints():
    """Test all API endpoints."""
    base_url = "http://localhost:8000"
    client = httpx.AsyncClient()
    
    print("Testing API endpoints...")
    
    # Test health
    try:
        response = await client.get(f"{base_url}/chatbot/health")
        print(f"Health: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Health test failed: {e}")
    
    # Test chat
    try:
        payload = {"message": "Hello! Tell me a short joke."}
        response = await client.post(
            f"{base_url}/chatbot/chat",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Chat: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Response: {data.get('content', 'No content')[:100]}...")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"Chat test failed: {e}")
    
    # Test history
    try:
        response = await client.get(f"{base_url}/chatbot/history")
        print(f"History: {response.status_code}")
        if response.status_code == 200:
            history = response.json()
            print(f"  History length: {len(history)}")
    except Exception as e:
        print(f"History test failed: {e}")
    
    # Test reset
    try:
        response = await client.post(f"{base_url}/chatbot/reset")
        print(f"Reset: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Reset test failed: {e}")
    
    await client.aclose()


def main():
    """Main function to run server and test."""
    # Set environment variable
    api_key = "AIzaSyBwGc5TQ14IpygA8FeJaKdGoIFC2sM238k"
    os.environ["GEMINI_API_KEY"] = api_key
    os.environ["CHATBOT_API_KEY"] = api_key
    
    print("Setting up environment...")
    print(f"API Key set: {bool(api_key)}")
    
    # Test direct chatbot first
    print("\nTesting direct chatbot...")
    try:
        chatbot = build_chatbot_from_env()
        print("Direct chatbot: OK")
    except Exception as e:
        print(f"Direct chatbot failed: {e}")
        return
    
    # Start server
    print("\nStarting server...")
    try:
        # Start server in background
        server_process = subprocess.Popen(
            [sys.executable, "app.py"],
            env=os.environ.copy(),
            cwd=Path(__file__).parent
        )
        
        # Wait for server to start
        print("Waiting for server to start...")
        time.sleep(3)
        
        # Test endpoints
        print("\nTesting endpoints...")
        asyncio.run(test_endpoints())
        
    except Exception as e:
        print(f"Server test failed: {e}")
    finally:
        # Clean up
        if 'server_process' in locals():
            server_process.terminate()
            server_process.wait()
            print("\nServer stopped.")


if __name__ == "__main__":
    main()
