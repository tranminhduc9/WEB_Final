"""
System Prompts for Hanoivivu Chatbot

Các prompt được thiết kế để tạo trải nghiệm tốt nhất cho người dùng
khi tìm hiểu về du lịch Hà Nội.
"""

from typing import List, Dict, Optional


# Main system prompt for Hanoi travel assistant
HANOI_TRAVEL_PROMPT = """Bạn là **Hanoivivu Assistant** - trợ lý du lịch Hà Nội thông minh và thân thiện.

## 🎯 Nhiệm vụ:
- Trả lời câu hỏi về du lịch, ẩm thực, văn hóa, lịch sử Hà Nội
- Gợi ý địa điểm tham quan, nhà hàng, quán cà phê, khách sạn
- Cung cấp thông tin về di sản văn hóa, lễ hội truyền thống
- Hướng dẫn di chuyển, phương tiện công cộng
- Chia sẻ kinh nghiệm du lịch và mẹo hữu ích

## 💬 Phong cách:
- Thân thiện, nhiệt tình như người bạn địa phương
- Ngắn gọn, súc tích, đi thẳng vào vấn đề
- Sử dụng tiếng Việt tự nhiên, dễ hiểu
- Có thể dùng emoji phù hợp 🏛️🍜☕🏨
- Nếu không chắc chắn, hãy thành thật nói

## ⚠️ Lưu ý quan trọng:
- Luôn ưu tiên gợi ý các địa điểm có trong hệ thống (nếu được cung cấp)
- Khi gợi ý địa điểm, đề cập tên chính xác và rating nếu có
- Nếu không có địa điểm phù hợp trong hệ thống, có thể gợi ý địa điểm khác
- Tôn trọng văn hóa và truyền thống địa phương"""


def build_conversation_prompt(
    message: str, 
    history: List[Dict] = None,
    place_context: str = None
) -> str:
    """
    Build full conversation prompt with history and place context.
    
    Args:
        message: Current user message
        history: List of previous messages [{"role": "user/assistant", "content": "..."}]
        place_context: Formatted string of relevant places from database
    
    Returns:
        Full prompt string with system prompt, places, and conversation history
    """
    parts = [HANOI_TRAVEL_PROMPT]
    
    # Add place context if available
    if place_context:
        parts.append(place_context)
    
    # Add conversation history
    parts.append("\n\n## 💭 Hội thoại:\n")
    
    if history:
        # Keep last 10 messages for context (5 exchanges)
        for msg in history[-10:]:
            role = "👤 Người dùng" if msg.get("role") == "user" else "🤖 Trợ lý"
            content = msg.get("content", "")
            if content:
                parts.append(f"{role}: {content}\n")
    
    # Add current message
    parts.append(f"👤 Người dùng: {message}\n🤖 Trợ lý:")
    
    return "".join(parts)


def build_prompt_with_places(
    message: str,
    places: List[Dict],
    history: List[Dict] = None
) -> str:
    """
    Build prompt with places injected.
    
    Args:
        message: User message
        places: List of relevant places from database
        history: Conversation history
        
    Returns:
        Full prompt with places context
    """
    # Format places into context string
    place_context = None
    if places:
        lines = ["\n## 📍 Địa điểm có trong hệ thống:"]
        
        for i, place in enumerate(places[:5], 1):  # Max 5 places
            rating = place.get('rating_average', 0) or 0
            rating_str = f"⭐{rating:.1f}" if rating else "Chưa có đánh giá"
            district = place.get('district_name', '')
            district_str = f" - {district}" if district else ""
            
            lines.append(f"{i}. **{place['name']}** ({rating_str}{district_str})")
            
            if place.get('address'):
                lines.append(f"   📍 {place['address']}")
        
        lines.append("\n*Ưu tiên gợi ý các địa điểm trên nếu phù hợp với câu hỏi.*")
        place_context = "\n".join(lines)
    
    return build_conversation_prompt(message, history, place_context)


# Quick response prompt for simple answers
QUICK_RESPONSE_PROMPT = """Trả lời ngắn gọn trong 2-3 câu. Đi thẳng vào vấn đề, không cần giải thích dài dòng."""


# Greeting responses
GREETING_RESPONSES = [
    "Xin chào! 👋 Tôi là Hanoivivu Assistant. Bạn muốn khám phá gì ở Hà Nội hôm nay?",
    "Chào bạn! 🏛️ Tôi có thể giúp bạn tìm địa điểm du lịch, ẩm thực, hoặc khách sạn ở Hà Nội. Bạn cần gì?",
    "Hello! ☕ Bạn đang tìm kiếm trải nghiệm gì ở Hà Nội? Tôi sẵn sàng hỗ trợ!"
]


def is_greeting(message: str) -> bool:
    """Check if message is a greeting."""
    greetings = [
        "xin chào", "chào", "hello", "hi", "hey",
        "chào bạn", "xin chào bạn", "alo"
    ]
    message_lower = message.lower().strip()
    return any(g in message_lower for g in greetings) and len(message_lower) < 30
