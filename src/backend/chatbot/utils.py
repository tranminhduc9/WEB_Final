"""
Chatbot Utility Functions

Cung cấp các utilities cho Adaptive RAG Chatbot:
- Guardrail functions (profanity, PII detection) - KHÔNG dùng LLM
- Vietnamese profanity list
- Text preprocessing
"""

import re
from typing import Tuple, List, Optional
from better_profanity import profanity


# ===========================================
# Vietnamese Profanity List
# ===========================================

# Danh sách từ ngữ tục tĩu tiếng Việt phổ biến
# CHÚ Ý: Chỉ dùng từ rõ ràng, tránh false positives
VIETNAMESE_PROFANITY = [
    # Từ ngữ thô tục rõ ràng (dùng word boundary)
    "địt", "dit me", "đụ", "đù",
    "lồn", "l0n", "buồi", "buoi", "cặc", "cac", "cặk",
    "đéo", "dcm", "đcm", "vcl", "vkl",
    "dm", "đm", "dmm", "đmm", "clgt", "cmnr", "wtf",
    "mẹ mày", "me may", "con mẹ mày",
    "đồ chó", "thằng chó",
    "óc chó",
    # English profanity
    "fuck", "shit", "bitch", "asshole",
]

# Patterns cho các biến thể - sử dụng word boundary \b
PROFANITY_PATTERNS = [
    r"\bđịt\b",
    r"\bdit\s+me\b",
    r"\bđụ\b",
    r"\blồn\b",
    r"\bcặc\b",
    r"\bbuồi\b",
    r"\bđéo\b",
    r"\bvcl\b",
    r"\bvkl\b",
    r"\bdm\b",
    r"\bđm\b",
    r"\bdmm\b",
    r"\bđmm\b",
]


# ===========================================
# PII Detection Patterns
# ===========================================

# Phone number patterns (Vietnamese)
PHONE_PATTERNS = [
    r"0[0-9]{9,10}",  # 09xxxxxxxx, 03xxxxxxxx, etc.
    r"\+84\s?[0-9]{9,10}",  # +84xxxxxxxxx or +84 xxxxxxxxx
    r"84\s?[0-9]{9,10}",  # 84xxxxxxxxx
    r"0[0-9]{2}[\s\.-][0-9]{3}[\s\.-][0-9]{4}",  # 0xx xxx xxxx (with separators)
]

# Email pattern
EMAIL_PATTERN = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

# ID card pattern (Vietnamese CCCD/CMND)
ID_PATTERNS = [
    r"\b[0-9]{9}\b",  # CMND 9 số
    r"\b[0-9]{12}\b",  # CCCD 12 số
]

# Bank account patterns
BANK_PATTERNS = [
    r"\b[0-9]{10,19}\b",  # Generic bank account
]


# ===========================================
# Guardrail Functions (Algorithmic - No LLM)
# ===========================================

def init_profanity_filter():
    """
    Khởi tạo profanity filter với custom word list.
    """
    profanity.load_censor_words()
    profanity.add_censor_words(VIETNAMESE_PROFANITY)


# Initialize on module load
init_profanity_filter()


def check_profanity(text: str) -> Tuple[bool, List[str]]:
    """
    Kiểm tra văn bản có chứa từ ngữ tục tĩu không.
    
    KHÔNG sử dụng LLM - chỉ dùng thuật toán/regex.
    
    Args:
        text: Văn bản cần kiểm tra
        
    Returns:
        Tuple[bool, List[str]]: (has_profanity, list_of_violations)
    """
    violations = []
    text_lower = text.lower()
    
    # Check using better_profanity library
    if profanity.contains_profanity(text):
        violations.append("profanity_detected")
    
    # Check Vietnamese profanity với regex patterns
    for pattern in PROFANITY_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            violations.append(f"pattern_match:{pattern}")
    
    # Check exact match với custom list
    for word in VIETNAMESE_PROFANITY:
        if word.lower() in text_lower:
            violations.append(f"word_match:{word}")
    
    # Remove duplicates
    violations = list(set(violations))
    
    return len(violations) > 0, violations


def check_pii(text: str) -> Tuple[bool, List[str]]:
    """
    Kiểm tra văn bản có chứa thông tin cá nhân nhạy cảm (PII) không.
    
    KHÔNG sử dụng LLM - chỉ dùng regex patterns.
    
    Phát hiện:
    - Số điện thoại
    - Email
    - CMND/CCCD (tùy chọn, có thể gây false positive)
    
    Args:
        text: Văn bản cần kiểm tra
        
    Returns:
        Tuple[bool, List[str]]: (has_pii, list_of_pii_types)
    """
    pii_found = []
    
    # Check phone numbers
    for pattern in PHONE_PATTERNS:
        if re.search(pattern, text):
            pii_found.append("phone_number")
            break
    
    # Check email
    if re.search(EMAIL_PATTERN, text, re.IGNORECASE):
        pii_found.append("email")
    
    # Note: Không check ID/Bank vì dễ false positive
    # Có thể enable nếu cần security cao hơn
    
    return len(pii_found) > 0, pii_found


def is_safe_query(text: str) -> Tuple[bool, str]:
    """
    Kiểm tra tổng hợp xem query có an toàn không.
    
    Kết hợp:
    - Profanity check
    - PII detection
    
    Args:
        text: Query cần kiểm tra
        
    Returns:
        Tuple[bool, str]: (is_safe, rejection_message_if_unsafe)
    """
    # Check profanity
    has_profanity, profanity_violations = check_profanity(text)
    if has_profanity:
        return False, "Xin lỗi, tôi không thể xử lý tin nhắn có chứa ngôn ngữ không phù hợp. Vui lòng sử dụng ngôn ngữ lịch sự."
    
    # Check PII
    has_pii, pii_types = check_pii(text)
    if has_pii:
        pii_str = ", ".join(pii_types)
        return False, f"Vì lý do bảo mật, vui lòng không chia sẻ thông tin cá nhân như {pii_str} trong cuộc trò chuyện."
    
    return True, ""


# ===========================================
# Text Preprocessing Utilities
# ===========================================

def clean_text(text: str) -> str:
    """
    Làm sạch văn bản trước khi xử lý.
    
    Args:
        text: Văn bản gốc
        
    Returns:
        str: Văn bản đã được làm sạch
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Trim
    text = text.strip()
    
    return text


def extract_keywords(text: str) -> List[str]:
    """
    Trích xuất keywords từ văn bản.
    
    Args:
        text: Văn bản đầu vào
        
    Returns:
        List[str]: Danh sách keywords
    """
    # Simple keyword extraction (có thể enhance với NLP)
    # Remove common Vietnamese stop words
    stop_words = {
        "tôi", "bạn", "của", "và", "là", "có", "không", "được",
        "cho", "với", "này", "đó", "một", "các", "những", "thì",
        "ở", "tại", "về", "trong", "ngoài", "trên", "dưới",
        "muốn", "cần", "hỏi", "biết", "xin", "vui", "lòng",
    }
    
    # Tokenize (simple split)
    words = text.lower().split()
    
    # Filter stop words and short words
    keywords = [w for w in words if w not in stop_words and len(w) > 2]
    
    return keywords


def format_documents_for_context(documents: List[dict], max_docs: int = 5) -> str:
    """
    Format danh sách documents thành context string cho LLM.
    
    Args:
        documents: Danh sách documents từ vector search
        max_docs: Số lượng documents tối đa
        
    Returns:
        str: Context string formatted
    """
    if not documents:
        return "Không tìm thấy thông tin liên quan trong cơ sở dữ liệu."
    
    context_parts = []
    for i, doc in enumerate(documents[:max_docs], 1):
        title = doc.get("title", "Không có tiêu đề")
        content = doc.get("content", "")[:500]  # Limit content length
        rating = doc.get("rating")
        
        part = f"[{i}] {title}\n{content}"
        if rating:
            part += f"\n(Đánh giá: {rating}/5)"
        
        # Include reviews if available
        reviews = doc.get("reviews", [])
        if reviews:
            review_texts = [r.get("content", "")[:100] for r in reviews[:2]]
            if review_texts:
                part += f"\nNhận xét: {'; '.join(review_texts)}"
        
        context_parts.append(part)
    
    return "\n\n---\n\n".join(context_parts)
