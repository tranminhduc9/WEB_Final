"""
Chatbot API Routes

Module này định nghĩa các API endpoints cho AI Chatbot:
- POST /chatbot/message - Gửi tin nhắn
- GET /chatbot/history - Lấy lịch sử chat

Swagger v1.0.5 Compatible - MongoDB Integration
"""

from fastapi import APIRouter, Depends, Request, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime
import logging
import uuid

from config.database import get_db, Place
from app.utils.image_helpers import get_main_image_url
from app.utils.place_helpers import get_place_compact
from middleware.auth import get_current_user, get_optional_user
from middleware.response import success_response, error_response
from middleware.mongodb_client import mongo_client, get_mongodb

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])


# ==================== REQUEST SCHEMAS ====================

class ChatMessageRequest(BaseModel):
    """Schema gửi tin nhắn"""
    conversation_id: Optional[str] = None
    message: str = Field(..., min_length=1, max_length=2000)



async def get_ai_response(message: str, conversation_history: List[Dict] = None) -> Dict:
    """
    Gọi AI để lấy response
    Tích hợp với Google Generative AI hoặc OpenAI
    """
    try:
        import os
        import google.generativeai as genai
        
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            return {
                "response": "Xin lỗi, hệ thống AI đang bảo trì. Vui lòng thử lại sau.",
                "entities": {},
                "suggested_place_ids": []
            }
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        # System prompt
        system_prompt = """Bạn là trợ lý du lịch Hà Nội thông minh. 
Hãy trả lời các câu hỏi về du lịch, ẩm thực, địa điểm tham quan ở Hà Nội.
Trả lời ngắn gọn, thân thiện và hữu ích bằng tiếng Việt.
Nếu được hỏi về địa điểm cụ thể, hãy đề xuất những nơi phổ biến."""
        
        # Build prompt
        full_prompt = f"{system_prompt}\n\nNgười dùng: {message}"
        
        response = model.generate_content(full_prompt)
        
        return {
            "response": response.text if response.text else "Xin lỗi, tôi không hiểu câu hỏi của bạn.",
            "entities": {},
            "suggested_place_ids": []
        }
        
    except Exception as e:
        logger.error(f"AI error: {str(e)}")
        return {
            "response": "Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại sau.",
            "entities": {},
            "suggested_place_ids": []
        }


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
        
        # Get AI response
        ai_result = await get_ai_response(chat_data.message)
        
        # Save to MongoDB
        log_doc = {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "user_message": chat_data.message,
            "bot_response": ai_result["response"],
            "entities": ai_result["entities"]
        }
        
        await mongo_client.save_chatbot_log(log_doc)
        
        # Get suggested places
        suggested_places = []
        for place_id in ai_result.get("suggested_place_ids", []):
            place = get_place_compact(place_id, db)
            if place:
                suggested_places.append(place)
        
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
        
        # Build query
        query = {"user_id": user_id}
        if conversation_id:
            query["conversation_id"] = conversation_id
        
        # Get history
        history = await mongo_client.get_chatbot_history(user_id, limit=limit)
        
        # Format response
        formatted_history = []
        for log in history:
            formatted_history.append({
                "conversation_id": log.get("conversation_id"),
                "user_message": log.get("user_message"),
                "bot_response": log.get("bot_response"),
                "created_at": log.get("created_at").isoformat() if log.get("created_at") else None
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


# ==================== END OF CHATBOT ROUTES ====================
