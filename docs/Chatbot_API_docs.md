# Chatbot API Documentation

This document describes the HTTP API exposed by the FastAPI app for the Gemini-based chatbot.

Base URL: `/chatbot`

## Environment Setup

Set your Gemini API key as an environment variable. The app looks for `GEMINI_API_KEY` first, otherwise `CHATBOT_API_KEY`.

Windows PowerShell:
```
$env:GEMINI_API_KEY = "<your_api_key>"
$env:CHATBOT_MODEL = "gemini-2.5-flash"  # optional
$env:CHATBOT_TEMPERATURE = "0.7"         # optional
$env:CHATBOT_MAX_TOKENS = "1024"         # optional
$env:CHATBOT_SYSTEM_PROMPT = "You are a helpful AI assistant."  # optional
$env:CHATBOT_ENABLE_LOGGING = "true"     # optional
$env:CHATBOT_LOG_LEVEL = "INFO"          # optional
```

Linux/macOS (bash):
```
export GEMINI_API_KEY="<your_api_key>"
export CHATBOT_MODEL="gemini-2.5-flash"
export CHATBOT_TEMPERATURE="0.7"
export CHATBOT_MAX_TOKENS="1024"
export CHATBOT_SYSTEM_PROMPT="You are a helpful AI assistant."
export CHATBOT_ENABLE_LOGGING="true"
export CHATBOT_LOG_LEVEL="INFO"
```

Run server:
```
uvicorn server.app:app --reload
```

## Schemas

Chat message object:
```
{
  "role": "user|assistant|system",
  "content": "string",
  "timestamp": 1710000000.0,
  "metadata": {"k": "v"}
}
```

Chat request:
```
{
  "message": "string",
  "conversation_history": [<chat message>, ...]
}
```

Chat response:
```
{
  "content": "string",
  "metadata": {"model": "...", "temperature": 0.7, "timestamp": 1710000000.0},
  "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
  "model": "gemini-2.5-flash"
}
```

Error response:
```
{ "detail": "error message" }
```

## Endpoints

### POST /chatbot/chat
Send a message to the chatbot.

Request body:
```
{
  "message": "Hello",
  "conversation_history": [
    {"role":"user","content":"Hi"},
    {"role":"assistant","content":"Hello!"}
  ]
}
```

Responses:
- 200: Chat response
- 400: Validation error
- 429: Rate limit
- 500/502: API/internal error

Curl example:
```
curl -X POST http://localhost:8000/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello"}'
```

### POST /chatbot/reset
Clear the current conversation history.

Response 200:
```
{ "healthy": true }
```

### GET /chatbot/history
Return the current conversation history.

Response 200: array of chat messages.

### GET /chatbot/health
Readiness check for the chatbot.

Response 200:
```
{ "healthy": true }
```

## Notes
- The chatbot is lazy-initialized on first use; no startup hook required.
- Configuration is read from environment variables via `ChatbotConfig.from_env` inside `build_chatbot_from_env()`.
- Structured logging is enabled via `ChatbotLogger`. Adjust log level with `CHATBOT_LOG_LEVEL`.
