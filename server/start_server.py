"""
Start the chatbot API server with proper environment setup.
"""

import os
import sys
from pathlib import Path

# Set API key
api_key = "AIzaSyBwGc5TQ14IpygA8FeJaKdGoIFC2sM238k"
os.environ["GEMINI_API_KEY"] = api_key
os.environ["CHATBOT_API_KEY"] = api_key

# Optional: Set other environment variables
os.environ["CHATBOT_MODEL"] = "gemini-2.5-flash"
os.environ["CHATBOT_TEMPERATURE"] = "0.7"
os.environ["CHATBOT_MAX_TOKENS"] = "1024"
os.environ["CHATBOT_SYSTEM_PROMPT"] = "You are a helpful AI assistant."
os.environ["CHATBOT_ENABLE_LOGGING"] = "true"
os.environ["CHATBOT_LOG_LEVEL"] = "INFO"

print("Starting Chatbot API Server...")
print(f"API Key: {api_key[:10]}...")
print("Server will run on http://localhost:8000")
print("API Documentation: http://localhost:8000/docs")
print("Press Ctrl+C to stop")

# Import and run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
