# Chatbot API Documentation

## Overview

This document provides comprehensive API documentation for the Chatbot module, including all classes, methods, and their usage examples.

## Table of Contents

- [Core Interfaces](#core-interfaces)
- [Configuration](#configuration)
- [Chatbot Implementations](#chatbot-implementations)
- [Error Handling](#error-handling)
- [Factory Pattern](#factory-pattern)
- [Logging](#logging)
- [RAG Interface](#rag-interface)
- [Examples](#examples)

## Core Interfaces

### ChatbotInterface

Abstract base class that defines the contract for all chatbot implementations.

```python
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class ChatMessage:
    role: str                    # 'user', 'assistant', 'system'
    content: str                 # Message content
    timestamp: Optional[float]   # Unix timestamp
    metadata: Optional[Dict[str, Any]]  # Additional data

@dataclass
class ChatResponse:
    content: str                           # Response text
    metadata: Optional[Dict[str, Any]]     # Response metadata
    usage: Optional[Dict[str, Any]]        # Token usage info
    model: Optional[str]                   # Model used

class ChatbotInterface(ABC):
    @abstractmethod
    async def chat(self, message: str, conversation_history: Optional[List[ChatMessage]] = None) -> ChatResponse:
        """
        Process a user message and return a response.
        
        Args:
            message: The user's input message
            conversation_history: Optional list of previous messages in the conversation
            
        Returns:
            ChatResponse containing the assistant's response
            
        Raises:
            ChatbotError: If there's an error processing the message
        """
        pass
    
    @abstractmethod
    async def reset_conversation(self) -> None:
        """Reset the conversation state."""
        pass
    
    @abstractmethod
    def get_conversation_history(self) -> List[ChatMessage]:
        """Get the current conversation history."""
        pass
    
    @abstractmethod
    def is_healthy(self) -> bool:
        """Check if the chatbot is ready to process requests."""
        pass
```

## Configuration

### ChatbotConfig

Configuration class for chatbot settings with validation and environment variable support.

```python
@dataclass
class ChatbotConfig:
    # API Configuration
    api_key: str
    model: str = "gemini-1.5-flash"
    temperature: float = 0.7
    max_tokens: int = 2048
    
    # System Configuration
    system_prompt: str = "You are a helpful AI assistant."
    max_conversation_length: int = 50
    
    # Rate Limiting
    requests_per_minute: int = 60
    max_retries: int = 3
    
    # Additional settings
    timeout: float = 30.0
    enable_logging: bool = True
    log_level: str = "INFO"
    
    # RAG Configuration (for future extension)
    enable_rag: bool = False
    rag_config: Optional[Dict[str, Any]] = field(default_factory=dict)
    
    @classmethod
    def from_env(cls, prefix: str = "CHATBOT_") -> "ChatbotConfig":
        """Create configuration from environment variables."""
        pass
    
    def validate(self) -> None:
        """Validate the configuration parameters."""
        pass
```

### Configuration Methods

#### `from_env(prefix: str = "CHATBOT_") -> ChatbotConfig`

Creates a configuration instance from environment variables.

**Parameters:**
- `prefix` (str): Prefix for environment variable names (default: "CHATBOT_")

**Returns:**
- `ChatbotConfig`: Configuration instance loaded from environment

**Raises:**
- `ConfigurationError`: If required environment variables are missing

**Example:**
```python
# Set environment variables
export CHATBOT_API_KEY="your-api-key"
export CHATBOT_MODEL="gemini-1.5-pro"
export CHATBOT_TEMPERATURE="0.5"

# Load configuration
config = ChatbotConfig.from_env()
```

#### `validate() -> None`

Validates all configuration parameters.

**Raises:**
- `ConfigurationError`: If any configuration parameter is invalid

**Example:**
```python
config = ChatbotConfig(api_key="test-key", temperature=3.0)
config.validate()  # Raises ConfigurationError
```

## Chatbot Implementations

### GeminiChatbot

Concrete implementation using Google's Gemini AI API.

```python
class GeminiChatbot(ChatbotInterface):
    def __init__(self, config: ChatbotConfig):
        """
        Initialize the Gemini chatbot.
        
        Args:
            config: ChatbotConfig instance with all necessary settings
            
        Raises:
            ConfigurationError: If configuration is invalid
            AuthenticationError: If API key is invalid
        """
        pass
```

#### Methods

##### `async chat(message: str, conversation_history: Optional[List[ChatMessage]] = None) -> ChatResponse`

Process a user message and return a response.

**Parameters:**
- `message` (str): The user's input message
- `conversation_history` (Optional[List[ChatMessage]]): Optional list of previous messages

**Returns:**
- `ChatResponse`: Response containing the assistant's reply

**Raises:**
- `ValidationError`: If input validation fails
- `RateLimitError`: If rate limit is exceeded
- `APIError`: If there's an error with the API

**Example:**
```python
# Basic usage
response = await chatbot.chat("Hello, how are you?")
print(response.content)

# With conversation history
history = [
    ChatMessage(role="user", content="What's the weather?"),
    ChatMessage(role="assistant", content="I don't have access to weather data.")
]
response = await chatbot.chat("Can you help me with something else?", history)
```

##### `async reset_conversation() -> None`

Reset the conversation state.

**Example:**
```python
await chatbot.reset_conversation()
```

##### `get_conversation_history() -> List[ChatMessage]`

Get the current conversation history.

**Returns:**
- `List[ChatMessage]`: Copy of the conversation history

**Example:**
```python
history = chatbot.get_conversation_history()
for message in history:
    print(f"{message.role}: {message.content}")
```

##### `is_healthy() -> bool`

Check if the chatbot is ready to process requests.

**Returns:**
- `bool`: True if healthy, False otherwise

**Example:**
```python
if chatbot.is_healthy():
    response = await chatbot.chat("Hello!")
else:
    print("Chatbot is not healthy")
```

## Error Handling

### Exception Hierarchy

```
ChatbotError (Base Exception)
├── APIError
│   ├── AuthenticationError
│   └── RateLimitError
├── ConfigurationError
└── ValidationError
```

### Exception Types

#### `ChatbotError`

Base exception for all chatbot-related errors.

```python
class ChatbotError(Exception):
    """Base exception for all chatbot-related errors."""
    pass
```

#### `APIError`

Raised when there's an error communicating with external AI APIs.

```python
class APIError(ChatbotError):
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data
```

#### `AuthenticationError`

Raised when API authentication fails.

```python
class AuthenticationError(APIError):
    """Raised when API authentication fails."""
    pass
```

#### `RateLimitError`

Raised when API rate limits are exceeded.

```python
class RateLimitError(APIError):
    """Raised when API rate limits are exceeded."""
    pass
```

#### `ConfigurationError`

Raised when there's an error in chatbot configuration.

```python
class ConfigurationError(ChatbotError):
    """Raised when there's an error in chatbot configuration."""
    pass
```

#### `ValidationError`

Raised when input validation fails.

```python
class ValidationError(ChatbotError):
    """Raised when input validation fails."""
    pass
```

## Factory Pattern

### ChatbotFactory

Factory class for creating chatbot instances.

```python
class ChatbotFactory:
    @classmethod
    def create_chatbot(cls, config: ChatbotConfig, chatbot_type: str = "gemini") -> ChatbotInterface:
        """
        Create a chatbot instance based on the specified type.
        
        Args:
            config: ChatbotConfig instance
            chatbot_type: Type of chatbot to create ("gemini", etc.)
            
        Returns:
            ChatbotInterface instance
            
        Raises:
            ConfigurationError: If chatbot type is not supported
        """
        pass
    
    @classmethod
    def register_chatbot(cls, name: str, chatbot_class: Type[ChatbotInterface]) -> None:
        """
        Register a new chatbot implementation.
        
        Args:
            name: Name to register the chatbot under
            chatbot_class: ChatbotInterface implementation class
        """
        pass
    
    @classmethod
    def get_available_types(cls) -> list[str]:
        """Get list of available chatbot types."""
        pass
```

### Usage Examples

```python
# Create chatbot using factory
config = ChatbotConfig(api_key="your-key")
chatbot = ChatbotFactory.create_chatbot(config, "gemini")

# Register custom chatbot
class CustomChatbot(ChatbotInterface):
    # Implementation...

ChatbotFactory.register_chatbot("custom", CustomChatbot)

# Get available types
types = ChatbotFactory.get_available_types()
print(types)  # ['gemini', 'custom']
```

## Logging

### ChatbotLogger

Structured logger for chatbot operations.

```python
class ChatbotLogger:
    def __init__(self, name: str = "chatbot", level: str = "INFO"):
        """Initialize the chatbot logger."""
        pass
    
    def log_request(self, message: str, user_id: Optional[str] = None, 
                   conversation_id: Optional[str] = None) -> None:
        """Log an incoming request."""
        pass
    
    def log_response(self, response: str, duration_ms: float, 
                    model: str, tokens_used: Optional[int] = None) -> None:
        """Log an outgoing response."""
        pass
    
    def log_error(self, error: Exception, operation: str, 
                 context: Optional[Dict[str, Any]] = None) -> None:
        """Log an error."""
        pass
    
    def log_performance(self, operation: str, duration_ms: float, 
                       metadata: Optional[Dict[str, Any]] = None) -> None:
        """Log performance metrics."""
        pass
```

### Log Entry Structure

```python
@dataclass
class LogEntry:
    timestamp: str
    level: str
    component: str
    operation: str
    message: str
    metadata: Optional[Dict[str, Any]] = None
    duration_ms: Optional[float] = None
    error: Optional[str] = None
```

## RAG Interface

### RAGInterface

Abstract interface for RAG capabilities (future extension).

```python
@dataclass
class Document:
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None

@dataclass
class SearchResult:
    document: Document
    score: float
    relevance: float

class RAGInterface(ABC):
    @abstractmethod
    async def add_documents(self, documents: List[Document]) -> None:
        """Add documents to the knowledge base."""
        pass
    
    @abstractmethod
    async def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """Search for relevant documents."""
        pass
    
    @abstractmethod
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document from the knowledge base."""
        pass
    
    @abstractmethod
    async def clear_knowledge_base(self) -> None:
        """Clear all documents from the knowledge base."""
        pass
    
    @abstractmethod
    def get_knowledge_base_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base."""
        pass
```

## Examples

### Basic Chatbot Usage

```python
import asyncio
from server.chatbot import ChatbotConfig, GeminiChatbot

async def main():
    # Create configuration
    config = ChatbotConfig(
        api_key="your-gemini-api-key",
        model="gemini-1.5-flash",
        temperature=0.7,
        max_tokens=1000
    )
    
    # Create chatbot
    chatbot = GeminiChatbot(config)
    
    # Start conversation
    try:
        response = await chatbot.chat("Hello, how are you?")
        print(f"Assistant: {response.content}")
        
        # Continue conversation
        response = await chatbot.chat("What's the capital of France?")
        print(f"Assistant: {response.content}")
        
    except Exception as e:
        print(f"Error: {e}")

# Run the example
asyncio.run(main())
```

### Error Handling Example

```python
from server.chatbot import ChatbotConfig, GeminiChatbot
from server.chatbot.exceptions import ValidationError, APIError, RateLimitError

async def safe_chat(chatbot, message):
    try:
        response = await chatbot.chat(message)
        return response.content
    except ValidationError as e:
        return f"Invalid input: {e}"
    except RateLimitError as e:
        return f"Rate limit exceeded: {e}"
    except APIError as e:
        return f"API error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"
```

### Configuration from Environment

```python
import os
from server.chatbot import ChatbotConfig

# Set environment variables
os.environ["CHATBOT_API_KEY"] = "your-api-key"
os.environ["CHATBOT_MODEL"] = "gemini-1.5-pro"
os.environ["CHATBOT_TEMPERATURE"] = "0.5"

# Load configuration
config = ChatbotConfig.from_env()
```

### Factory Pattern Usage

```python
from server.chatbot import ChatbotConfig, ChatbotFactory

# Create configuration
config = ChatbotConfig(api_key="your-key")

# Create chatbot using factory
chatbot = ChatbotFactory.create_chatbot(config, "gemini")

# Use chatbot
response = await chatbot.chat("Hello!")
```

### Custom Chatbot Implementation

```python
from server.chatbot.interfaces import ChatbotInterface, ChatMessage, ChatResponse

class CustomChatbot(ChatbotInterface):
    def __init__(self, config):
        self.config = config
        self.conversation_history = []
    
    async def chat(self, message: str, conversation_history=None):
        # Custom implementation
        response_text = f"Echo: {message}"
        
        return ChatResponse(
            content=response_text,
            metadata={"custom": True}
        )
    
    async def reset_conversation(self):
        self.conversation_history.clear()
    
    def get_conversation_history(self):
        return self.conversation_history.copy()
    
    def is_healthy(self):
        return True

# Register custom chatbot
ChatbotFactory.register_chatbot("custom", CustomChatbot)
```

## Testing

### Running Tests

```bash
# Run all tests
pytest server/chatbot/tests/

# Run with coverage
pytest server/chatbot/tests/ --cov=server.chatbot

# Run specific test file
pytest server/chatbot/tests/test_gemini_chatbot.py

# Run with verbose output
pytest server/chatbot/tests/ -v
```

### Test Structure

```
tests/
├── __init__.py
├── test_gemini_chatbot.py    # GeminiChatbot tests
├── test_config.py            # Configuration tests
├── test_factory.py           # Factory pattern tests
└── test_exceptions.py        # Exception handling tests
```

## Performance Considerations

### Rate Limiting

The chatbot includes built-in rate limiting to prevent API quota exhaustion:

```python
config = ChatbotConfig(
    requests_per_minute=60,  # Maximum requests per minute
    max_retries=3            # Retry failed requests
)
```

### Memory Management

Conversation history is automatically trimmed to prevent memory issues:

```python
config = ChatbotConfig(
    max_conversation_length=50  # Keep only last 50 messages
)
```

### Async Operations

All I/O operations are async for better performance:

```python
# All chatbot methods are async
response = await chatbot.chat("Hello!")
await chatbot.reset_conversation()
```

## Security

### API Key Protection

- API keys are never logged
- Configuration validation prevents empty keys
- Environment variables are preferred over hardcoded keys

### Input Validation

- All inputs are validated before processing
- Empty messages are rejected
- Malformed data is handled gracefully

### Error Sanitization

- Error messages don't expose sensitive information
- Stack traces are not exposed to users
- Custom exceptions provide safe error information
