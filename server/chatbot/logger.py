"""
Logging utilities for chatbot module.

This module provides structured logging capabilities for the chatbot system,
including request/response logging, error tracking, and performance metrics.
"""

import logging
import json
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class LogEntry:
    """Structured log entry for chatbot operations."""
    timestamp: str
    level: str
    component: str
    operation: str
    message: str
    metadata: Optional[Dict[str, Any]] = None
    duration_ms: Optional[float] = None
    error: Optional[str] = None


class ChatbotLogger:
    """
    Structured logger for chatbot operations.
    
    This class provides methods for logging different types of chatbot
    operations with consistent formatting and metadata.
    """
    
    def __init__(self, name: str = "chatbot", level: str = "INFO"):
        """
        Initialize the chatbot logger.
        
        Args:
            name: Logger name
            level: Logging level
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Add console handler if not already present
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
    
    def log_request(self, message: str, user_id: Optional[str] = None, 
                   conversation_id: Optional[str] = None) -> None:
        """
        Log an incoming request.
        
        Args:
            message: User message
            user_id: Optional user identifier
            conversation_id: Optional conversation identifier
        """
        entry = LogEntry(
            timestamp=datetime.utcnow().isoformat(),
            level="INFO",
            component="request",
            operation="incoming",
            message=f"Received message: {message[:100]}...",
            metadata={
                "user_id": user_id,
                "conversation_id": conversation_id,
                "message_length": len(message)
            }
        )
        
        self.logger.info(json.dumps(asdict(entry), default=str))
    
    def log_response(self, response: str, duration_ms: float, 
                    model: str, tokens_used: Optional[int] = None) -> None:
        """
        Log an outgoing response.
        
        Args:
            response: Generated response
            duration_ms: Response generation time in milliseconds
            model: Model used for generation
            tokens_used: Number of tokens used
        """
        entry = LogEntry(
            timestamp=datetime.utcnow().isoformat(),
            level="INFO",
            component="response",
            operation="outgoing",
            message=f"Generated response: {response[:100]}...",
            metadata={
                "model": model,
                "tokens_used": tokens_used,
                "response_length": len(response)
            },
            duration_ms=duration_ms
        )
        
        self.logger.info(json.dumps(asdict(entry), default=str))
    
    def log_error(self, error: Exception, operation: str, 
                 context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an error.
        
        Args:
            error: Exception that occurred
            operation: Operation that failed
            context: Additional context information
        """
        entry = LogEntry(
            timestamp=datetime.utcnow().isoformat(),
            level="ERROR",
            component="error",
            operation=operation,
            message=str(error),
            metadata=context,
            error=type(error).__name__
        )
        
        self.logger.error(json.dumps(asdict(entry), default=str))
    
    def log_performance(self, operation: str, duration_ms: float, 
                       metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Log performance metrics.
        
        Args:
            operation: Operation name
            duration_ms: Duration in milliseconds
            metadata: Additional metadata
        """
        entry = LogEntry(
            timestamp=datetime.utcnow().isoformat(),
            level="INFO",
            component="performance",
            operation=operation,
            message=f"Operation completed in {duration_ms:.2f}ms",
            metadata=metadata,
            duration_ms=duration_ms
        )
        
        self.logger.info(json.dumps(asdict(entry), default=str))
