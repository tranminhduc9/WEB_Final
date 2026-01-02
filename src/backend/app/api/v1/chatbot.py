"""
Chatbot API Routes

Module này định nghĩa các API endpoints cho AI Chatbot:
- POST /chatbot/message - Gửi tin nhắn
- GET /chatbot/history - Lấy lịch sử chat

Features:
- Dynamic place context injection
- Conversation history for context
- Suggested places from database

Swagger v1.1.0 Compatible - MongoDB Integration
"""

from fastapi import APIRouter, Depends, Request, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
import logging
import uuid

from config.database import get_db
from app.utils.place_helpers import get_place_compact
from app.utils.timezone_helper import to_iso_string
from middleware.auth import get_current_user
from middleware.response import success_response, error_response
from middleware.mongodb_client import mongo_client, get_mongodb

# Import chatbot services
from app.chatbot import get_chat_service, get_place_context_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])


# ==================== REQUEST SCHEMAS ====================

class ChatMessageRequest(BaseModel):
    """Schema gửi tin nhắn"""
    conversation_id: Optional[str] = None
    message: str = Field(..., min_length=1, max_length=2000)


# ==================== ENDPOINTS ====================

@router.post("/message", summary="Send Message")
async def send_message(
    request: Request,
    chat_data: ChatMessageRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Gửi tin nhắn đến AI chatbot
    
    Flow:
    1. Tìm địa điểm liên quan từ database dựa trên message
    2. Lấy conversation history từ MongoDB
    3. Gọi AI với context (places + history)
    4. Lưu conversation vào MongoDB
    5. Trả về response + suggested places
    
    Args:
        conversation_id: ID cuộc hội thoại (optional, tạo mới nếu không có)
        message: Nội dung tin nhắn
    
    Returns:
        conversation_id, bot_response, suggested_places
    """
    try:
        await get_mongodb()
        
        user_id = current_user.get("user_id")
        conversation_id = chat_data.conversation_id or str(uuid.uuid4())
        
        # 1. Search relevant places from database
        place_service = get_place_context_service()
        relevant_places = await place_service.search_relevant_places(
            message=chat_data.message,
            db=db,
            limit=5
        )
        
        # 2. Get conversation history for context
        history = await mongo_client.get_chatbot_history(
            user_id, 
            conversation_id=conversation_id,
            limit=10
        )
        
        # Convert history to list format for AI
        conversation_history = []
        for log in reversed(history):  # Oldest first
            conversation_history.append({
                "role": "user",
                "content": log.get("user_message", "")
            })
            conversation_history.append({
                "role": "assistant", 
                "content": log.get("bot_response", "")
            })
        
        # 3. Get AI response with places context
        chat_service = get_chat_service()
        ai_result = await chat_service.chat(
            message=chat_data.message,
            conversation_history=conversation_history,
            places=relevant_places  # Inject places context
        )
        
        # 4. Save to MongoDB (matching chatbot_logs_mongo schema)
        log_doc = {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "user_message": chat_data.message,
            "bot_response": ai_result["response"],
            "entities": ai_result.get("entities", {})
            # created_at is auto-added by insert_one
        }
        
        await mongo_client.save_chatbot_log(log_doc)

        
        # 5. Format suggested places for response (matching PlaceCompact interface)
        # place_context now returns: rating_average, main_image_url, district_name
        suggested_places = []
        for place in relevant_places[:3]:  # Max 3 suggested places
            rating = place.get("rating_average", 0)
            if rating is None:
                rating = 0
            suggested_places.append({
                "id": place["id"],
                "name": place["name"],
                "district_id": place.get("district_id"),
                "district_name": place.get("district_name"),
                "rating_average": float(rating),  # Ensure it's always a number
                "rating_count": place.get("rating_count", 0) or 0,
                "main_image_url": place.get("main_image_url"),
                "address": place.get("address"),
                "place_type_id": place.get("place_type_id"),
                "price_min": float(place.get("price_min", 0) or 0),
                "price_max": float(place.get("price_max", 0) or 0),
            })
        
        return {
            "success": True,
            "message": "Đã nhận phản hồi",
            "conversation_id": conversation_id,
            "bot_response": ai_result["response"],
            "suggested_places": suggested_places
        }
        
    except Exception as e:
        logger.error(f"Error in chatbot: {str(e)}")
        return error_response(
            message="Lỗi xử lý tin nhắn",
            error_code="INTERNAL_ERROR",
            status_code=500
        )


@router.get("/history", summary="Get History")
async def get_chat_history(
    request: Request,
    conversation_id: Optional[str] = Query(None, description="ID cuộc hội thoại"),
    limit: int = Query(20, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lấy lịch sử chat
    
    Args:
        conversation_id: ID cuộc hội thoại (optional, lấy tất cả nếu không có)
        limit: Số tin nhắn tối đa
    """
    try:
        await get_mongodb()
        
        user_id = current_user.get("user_id")
        
        # Get history
        history = await mongo_client.get_chatbot_history(
            user_id, 
            conversation_id=conversation_id,
            limit=limit
        )
        
        # Format response (matching chatbot_logs_mongo schema)
        formatted_history = []
        for log in history:
            formatted_history.append({
                "conversation_id": log.get("conversation_id"),
                "user_message": log.get("user_message"),
                "bot_response": log.get("bot_response"),
                "entities": log.get("entities", {}),
                "created_at": to_iso_string(log.get("created_at"))
            })
        
        return success_response(
            message="Lấy lịch sử chat thành công",
            data=formatted_history
        )
        
    except Exception as e:
        logger.error(f"Error getting chat history: {str(e)}")
        return error_response(
            message="Lỗi lấy lịch sử chat",
            error_code="INTERNAL_ERROR",
            status_code=500
        )


@router.get("/health", summary="Health Check")
async def chatbot_health():
    """
    Kiểm tra trạng thái chatbot service
    """
    chat_service = get_chat_service()
    return {
        "healthy": chat_service.is_healthy,
        "service": "chatbot",
        "version": "1.1.0",
        "features": [
            "gemini_ai",
            "place_context",
            "conversation_history"
        ]
    }


# ==================== END OF CHATBOT ROUTES ====================
