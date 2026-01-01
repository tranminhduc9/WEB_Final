"""
Chatbot Pydantic Models

Định nghĩa các models cho:
- AgentState: Trạng thái của LangGraph
- Post, Review: Schema MongoDB documents
- ChatLog: Lịch sử chat
"""

import operator
from datetime import datetime
from typing import List, Dict, Any, Optional, Annotated, Literal
from pydantic import BaseModel, Field

# Optional import - may not be installed yet
try:
    from langchain_core.messages import AnyMessage
except ImportError:
    AnyMessage = Any  # Fallback type


# ===========================================
# LangGraph State Definition
# ===========================================

class AgentState(BaseModel):
    """
    Trạng thái của Adaptive RAG Agent.
    
    Quản lý toàn bộ ngữ cảnh trong quá trình xử lý:
    - messages: Lịch sử hội thoại (accumulates via operator.add)
    - user_query: Câu hỏi gốc của user
    - refined_query: Câu hỏi đã được viết lại để search DB
    - documents: Kết quả tìm kiếm từ MongoDB
    - generation: Câu trả lời sinh ra
    - retry_count: Đếm số lần lặp lại (max = 3)
    - safety_violation: Cờ đánh dấu vi phạm guardrail
    - intent: Ý định được phân loại (VECTOR_SEARCH hoặc CHIT_CHAT)
    - grader_passed: Kết quả đánh giá từ grader
    """
    
    # Conversation history - uses Annotated for LangGraph reducer
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Query processing
    user_query: str = ""
    refined_query: str = ""
    
    # Retrieval results
    documents: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Generation
    generation: str = ""
    
    # Control flow
    retry_count: int = 0
    safety_violation: bool = False
    intent: Literal["VECTOR_SEARCH", "CHIT_CHAT", ""] = ""
    grader_passed: Optional[bool] = None
    
    # Session info
    session_id: str = ""
    user_id: Optional[int] = None
    
    class Config:
        arbitrary_types_allowed = True


# ===========================================
# MongoDB Document Schemas
# ===========================================

class PostDocument(BaseModel):
    """
    Schema cho MongoDB posts_mongo collection.
    
    Bao gồm trường embedding cho vector search.
    """
    id: str = Field(alias="_id")
    title: str
    content: str
    type: str = "post"  # post hoặc review
    author_id: int
    related_place_id: Optional[int] = None
    rating: Optional[float] = None
    tags: List[str] = Field(default_factory=list)
    images: List[str] = Field(default_factory=list)
    likes_count: int = 0
    comments_count: int = 0
    status: str = "approved"
    
    # Vector embedding (768 dimensions for text-embedding-004)
    embedding: Optional[List[float]] = None
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True


class ReviewDocument(BaseModel):
    """
    Schema cho reviews/comments trong post_comments_mongo.
    """
    id: str = Field(alias="_id")
    post_id: str
    user_id: int
    content: str
    parent_id: Optional[str] = None
    created_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True


# ===========================================
# Chat Log Schema
# ===========================================

class ChatMessage(BaseModel):
    """Single chat message."""
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatLog(BaseModel):
    """
    Schema cho chatbot_logs_mongo collection.
    
    Lưu trữ lịch sử chat theo session.
    """
    session_id: str = Field(..., description="Unique session identifier")
    user_id: Optional[int] = None
    messages: List[ChatMessage] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Stats
    total_messages: int = 0
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to the chat log."""
        self.messages.append(ChatMessage(role=role, content=content))
        self.total_messages = len(self.messages)
        self.updated_at = datetime.utcnow()
    
    def get_history_for_context(self, max_messages: int = 10) -> List[Dict[str, str]]:
        """
        Get recent messages formatted for LLM context.
        
        Args:
            max_messages: Maximum number of recent messages to include
            
        Returns:
            List of message dicts with role and content
        """
        recent = self.messages[-max_messages:] if len(self.messages) > max_messages else self.messages
        return [{"role": msg.role, "content": msg.content} for msg in recent]


# ===========================================
# API Request/Response Models
# ===========================================

class ChatRequest(BaseModel):
    """Request model for chatbot API."""
    session_id: Optional[str] = None
    message: str = Field(..., min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    """Response model for chatbot API."""
    success: bool = True
    session_id: str
    bot_response: str
    intent: str = ""
    safety_violation: bool = False
    suggested_places: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Debug info (optional)
    documents_used: int = 0
    retry_count: int = 0
