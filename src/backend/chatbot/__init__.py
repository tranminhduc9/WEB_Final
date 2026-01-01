"""
Adaptive RAG Chatbot Module

Hệ thống Chatbot Tư vấn Du lịch sử dụng kiến trúc Adaptive RAG với LangGraph.

Components:
- config: Cấu hình chatbot (LLM, Embedding, MongoDB)
- models: Pydantic models cho State, Post, Review, ChatLog
- utils: Guardrail utilities, profanity filter, PII detection
- embeddings: Embedding manager với caching
- graph: LangGraph StateGraph với các nodes xử lý
"""

from .config import ChatbotConfig
from .models import AgentState, ChatLog
from .graph import create_chatbot_graph, run_chatbot

__all__ = [
    "ChatbotConfig",
    "AgentState", 
    "ChatLog",
    "create_chatbot_graph",
    "run_chatbot",
]
