"""
Chatbot API Routes - Adaptive RAG

Module này định nghĩa các API endpoints cho AI Chatbot sử dụng Adaptive RAG:
- POST /chatbot/message - Gửi tin nhắn (với LangGraph processing)
- GET /chatbot/history - Lấy lịch sử chat
- POST /chatbot/embed-all - Chạy embedding cho tất cả posts (admin)

Swagger v2.0 - LangGraph Integration
"""

import logging
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime

from fastapi import APIRouter, Depends, Request, Query, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from config.database import get_db, Place
from app.utils.image_helpers import get_main_image_url
from app.utils.place_helpers import get_place_compact
from middleware.auth import get_current_user, get_optional_user
from middleware.response import success_response, error_response
from middleware.mongodb_client import mongo_client, get_mongodb

# Import chatbot module
from chatbot import run_chatbot, ChatbotConfig
from chatbot.embeddings import get_embedding_manager
from chatbot.models import ChatLog, ChatMessage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])


# ==================== REQUEST SCHEMAS ====================

class ChatMessageRequest(BaseModel):
    """Schema gửi tin nhắn"""
    session_id: Optional[str] = Field(None, description="Session ID (tạo mới nếu không có)")
    message: str = Field(..., min_length=1, max_length=2000, description="Nội dung tin nhắn")


class ChatMessageResponse(BaseModel):
    """Schema response tin nhắn"""
    success: bool = True
    session_id: str
    bot_response: str
    intent: str = ""
    safety_violation: bool = False
    suggested_places: List[Dict[str, Any]] = []
    documents_used: int = 0
    retry_count: int = 0


# ==================== HELPER FUNCTIONS ====================

async def load_chat_history(session_id: str, user_id: Optional[int] = None) -> List[Dict[str, str]]:
    """
    Load lịch sử chat từ MongoDB.
    
    Args:
        session_id: Session ID
        user_id: User ID (optional)
        
    Returns:
        List of messages for LangGraph context
    """
    await get_mongodb()
    
    collection = mongo_client.db["chatbot_logs_mongo"]
    
    # Find session
    query = {"session_id": session_id}
    if user_id:
        query["user_id"] = user_id
    
    session_doc = await collection.find_one(query)
    
    if session_doc and "messages" in session_doc:
        # Format messages for LangGraph
        messages = []
        for msg in session_doc["messages"][-10:]:  # Last 10 messages
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        return messages
    
    return []


async def save_chat_message(
    session_id: str,
    user_message: str,
    bot_response: str,
    user_id: Optional[int] = None,
    metadata: Optional[Dict] = None
) -> None:
    """
    Lưu tin nhắn vào MongoDB.
    
    Args:
        session_id: Session ID
        user_message: Tin nhắn của user
        bot_response: Phản hồi của bot
        user_id: User ID (optional)
        metadata: Additional metadata
    """
    await get_mongodb()
    
    collection = mongo_client.db["chatbot_logs_mongo"]
    
    now = datetime.utcnow()
    
    # Create message documents
    user_msg = {
        "role": "user",
        "content": user_message,
        "timestamp": now
    }
    
    bot_msg = {
        "role": "assistant",
        "content": bot_response,
        "timestamp": now,
        "metadata": metadata or {}
    }
    
    # Upsert session document
    await collection.update_one(
        {"session_id": session_id},
        {
            "$setOnInsert": {
                "session_id": session_id,
                "user_id": user_id,
                "created_at": now
            },
            "$push": {
                "messages": {"$each": [user_msg, bot_msg]}
            },
            "$set": {
                "updated_at": now
            },
            "$inc": {
                "total_messages": 2
            }
        },
        upsert=True
    )


# ==================== ENDPOINTS ====================

@router.post("/message", response_model=ChatMessageResponse, summary="Send Message")
async def send_message(
    request: Request,
    chat_data: ChatMessageRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Gửi tin nhắn đến AI chatbot sử dụng Adaptive RAG.
    
    Flow:
    1. Load lịch sử chat từ MongoDB
    2. Chạy LangGraph (guardrail → intent → retrieval → generation → grader)
    3. Lưu kết quả vào MongoDB
    4. Trả về response với suggested places
    
    Args:
        session_id: ID cuộc hội thoại (optional, tạo mới nếu không có)
        message: Nội dung tin nhắn
    
    Returns:
        ChatMessageResponse với bot_response, intent, suggested_places
    """
    try:
        user_id = current_user.get("user_id")
        session_id = chat_data.session_id or str(uuid.uuid4())
        user_message = chat_data.message.strip()
        
        logger.info(f"[Chatbot API] Processing message from user {user_id}, session {session_id}")
        
        # Step 1: Load chat history
        messages = await load_chat_history(session_id, user_id)
        
        # Step 2: Run LangGraph chatbot
        result = await run_chatbot(
            user_query=user_message,
            session_id=session_id,
            messages=messages,
            user_id=user_id
        )
        
        bot_response = result.get("generation", "")
        intent = result.get("intent", "")
        safety_violation = result.get("safety_violation", False)
        documents = result.get("documents", [])
        retry_count = result.get("retry_count", 0)
        
        # Step 3: Save to MongoDB (only if not safety violation)
        if not safety_violation:
            await save_chat_message(
                session_id=session_id,
                user_message=user_message,
                bot_response=bot_response,
                user_id=user_id,
                metadata={
                    "intent": intent,
                    "documents_count": len(documents),
                    "retry_count": retry_count
                }
            )
        
        # Step 4: Get suggested places from documents
        suggested_places = []
        seen_place_ids = set()
        
        for doc in documents[:5]:
            place_id = doc.get("related_place_id")
            if place_id and place_id not in seen_place_ids:
                place = get_place_compact(place_id, db)
                if place:
                    suggested_places.append(place)
                    seen_place_ids.add(place_id)
        
        return ChatMessageResponse(
            success=True,
            session_id=session_id,
            bot_response=bot_response,
            intent=intent,
            safety_violation=safety_violation,
            suggested_places=suggested_places,
            documents_used=len(documents),
            retry_count=retry_count
        )
        
    except Exception as e:
        logger.error(f"[Chatbot API] Error: {str(e)}", exc_info=True)
        return ChatMessageResponse(
            success=False,
            session_id=chat_data.session_id or "",
            bot_response="Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại sau.",
            safety_violation=False
        )


@router.get("/history", summary="Get Chat History")
async def get_chat_history(
    request: Request,
    session_id: Optional[str] = Query(None, description="ID cuộc hội thoại"),
    limit: int = Query(20, ge=1, le=100, description="Số tin nhắn tối đa"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lấy lịch sử chat.
    
    Args:
        session_id: ID cuộc hội thoại (optional, lấy tất cả nếu không có)
        limit: Số tin nhắn tối đa
    
    Returns:
        Danh sách các cuộc hội thoại và tin nhắn
    """
    try:
        await get_mongodb()
        
        user_id = current_user.get("user_id")
        collection = mongo_client.db["chatbot_logs_mongo"]
        
        # Build query
        query = {"user_id": user_id}
        if session_id:
            query["session_id"] = session_id
        
        # Get sessions
        cursor = collection.find(query).sort("updated_at", -1).limit(limit)
        
        sessions = []
        async for doc in cursor:
            # Format messages
            messages = []
            for msg in doc.get("messages", [])[-20:]:  # Last 20 per session
                messages.append({
                    "role": msg.get("role"),
                    "content": msg.get("content"),
                    "timestamp": msg.get("timestamp").isoformat() if msg.get("timestamp") else None
                })
            
            sessions.append({
                "session_id": doc.get("session_id"),
                "messages": messages,
                "total_messages": doc.get("total_messages", len(messages)),
                "created_at": doc.get("created_at").isoformat() if doc.get("created_at") else None,
                "updated_at": doc.get("updated_at").isoformat() if doc.get("updated_at") else None
            })
        
        return success_response(
            message="Lấy lịch sử chat thành công",
            data=sessions
        )
        
    except Exception as e:
        logger.error(f"[Chatbot API] Error getting history: {str(e)}")
        return error_response(
            message="Lỗi lấy lịch sử chat",
            error_code="INTERNAL_ERROR",
            status_code=500
        )


@router.post("/embed-all", summary="Embed All Posts (Admin)")
async def embed_all_posts(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Chạy embedding cho tất cả posts chưa có embedding.
    
    CHÚ Ý: 
    - Chỉ admin mới nên chạy
    - Có thể mất nhiều thời gian tùy số lượng posts
    - Có rate limit từ Google API
    
    Returns:
        Thống kê embedding: total, embedded, skipped, failed
    """
    try:
        # Check admin role
        role_id = current_user.get("role_id", 3)
        if role_id > 2:  # Not admin or moderator
            raise HTTPException(status_code=403, detail="Chỉ admin mới có thể thực hiện")
        
        logger.info("[Chatbot API] Starting embed all posts...")
        
        manager = get_embedding_manager()
        stats = await manager.embed_all_posts()
        
        return success_response(
            message="Hoàn thành embedding",
            data=stats
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Chatbot API] Error embedding: {str(e)}")
        return error_response(
            message=f"Lỗi embedding: {str(e)}",
            error_code="EMBEDDING_ERROR",
            status_code=500
        )


@router.get("/embedding-status", summary="Get Embedding Status")
async def get_embedding_status(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Kiểm tra trạng thái embedding của posts.
    
    Returns:
        Số posts chưa được embedding
    """
    try:
        manager = get_embedding_manager()
        pending_count = await manager.get_posts_without_embedding()
        
        return success_response(
            message="Trạng thái embedding",
            data={
                "posts_without_embedding": pending_count,
                "status": "ready" if pending_count == 0 else "pending"
            }
        )
        
    except Exception as e:
        logger.error(f"[Chatbot API] Error checking status: {str(e)}")
        return error_response(
            message="Lỗi kiểm tra trạng thái",
            error_code="INTERNAL_ERROR",
            status_code=500
        )


# ==================== END OF CHATBOT ROUTES ====================
