"""
Chatbot Configuration

Cấu hình cho Adaptive RAG Chatbot bao gồm:
- LLM settings (Gemini 2.5 Flash)
- Embedding model (text-embedding-004)  
- MongoDB settings
- LangSmith tracing
- Rate limit parameters
"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ChatbotConfig:
    """
    Cấu hình chính cho Adaptive RAG Chatbot.
    
    Tất cả settings được load từ environment variables với fallback defaults.
    """
    
    # ===========================================
    # LLM Configuration (Gemini)
    # ===========================================
    google_api_key: str = field(
        default_factory=lambda: os.getenv("GOOGLE_API_KEY", "")
    )
    llm_model: str = field(
        default_factory=lambda: os.getenv("CHATBOT_LLM_MODEL", "gemini-2.5-flash")
    )
    llm_temperature: float = field(
        default_factory=lambda: float(os.getenv("CHATBOT_LLM_TEMPERATURE", "0.7"))
    )
    llm_max_tokens: int = field(
        default_factory=lambda: int(os.getenv("CHATBOT_LLM_MAX_TOKENS", "2048"))
    )
    
    # ===========================================
    # Embedding Configuration
    # ===========================================
    embedding_model: str = field(
        default_factory=lambda: os.getenv("CHATBOT_EMBEDDING_MODEL", "models/text-embedding-004")
    )
    embedding_dimensions: int = 768  # Fixed for text-embedding-004
    
    # ===========================================
    # MongoDB Configuration
    # ===========================================
    mongo_uri: str = field(
        default_factory=lambda: os.getenv(
            "MONGO_URI_ATLAS", 
            os.getenv("MONGO_URI", "mongodb://localhost:27017")
        )
    )
    mongo_db_name: str = field(
        default_factory=lambda: os.getenv("MONGO_DB_NAME", "hanoi_travel_mongo")
    )
    
    # Collection names
    posts_collection: str = "posts_mongo"
    comments_collection: str = "post_comments_mongo"
    chatlog_collection: str = "chatbot_logs_mongo"
    
    # Vector search settings
    vector_index_name: str = field(
        default_factory=lambda: os.getenv("CHATBOT_VECTOR_INDEX", "vector_index")
    )
    vector_field_name: str = "embedding"
    vector_num_candidates: int = 100
    vector_limit: int = 5
    
    # ===========================================
    # LangSmith Tracing (Optional)
    # ===========================================
    langsmith_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("LANGCHAIN_API_KEY")
    )
    langsmith_tracing: bool = field(
        default_factory=lambda: os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
    )
    langsmith_project: str = field(
        default_factory=lambda: os.getenv("LANGCHAIN_PROJECT", "hanoi-travel-chatbot")
    )
    
    # ===========================================
    # Retry & Rate Limit Settings
    # ===========================================
    max_retries: int = 3
    retry_min_wait: float = 3.0  # seconds
    retry_max_wait: float = 60.0  # seconds
    retry_multiplier: float = 2.0
    
    # ===========================================
    # Graph Settings
    # ===========================================
    max_grader_retries: int = 3  # Max retry count in resample loop
    
    # ===========================================
    # System Prompts
    # ===========================================
    travel_assistant_prompt: str = """Bạn là trợ lý du lịch Hà Nội thông minh và thân thiện.

NHIỆM VỤ:
- Trả lời các câu hỏi về du lịch, ẩm thực, địa điểm tham quan ở Hà Nội
- Sử dụng thông tin từ ngữ cảnh được cung cấp để trả lời chính xác
- Nếu không có thông tin trong ngữ cảnh, hãy nói rõ và đưa ra lời khuyên chung

PHONG CÁCH:
- Trả lời bằng tiếng Việt, thân thiện, nhiệt tình
- Ngắn gọn nhưng đầy đủ thông tin
- Đề xuất thêm các gợi ý liên quan nếu phù hợp
"""

    chitchat_prompt: str = """Bạn là trợ lý du lịch Hà Nội thân thiện.
Hãy trả lời câu hỏi xã giao một cách tự nhiên và vui vẻ.
Có thể gợi ý về du lịch Hà Nội nếu phù hợp với ngữ cảnh.
"""

    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.google_api_key:
            raise ValueError(
                "GOOGLE_API_KEY is required. Please set it in environment variables."
            )
        
        # Setup LangSmith tracing if enabled
        if self.langsmith_tracing and self.langsmith_api_key:
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_API_KEY"] = self.langsmith_api_key
            os.environ["LANGCHAIN_PROJECT"] = self.langsmith_project


# Singleton config instance
_config_instance: Optional[ChatbotConfig] = None


def get_config() -> ChatbotConfig:
    """
    Get singleton ChatbotConfig instance.
    
    Returns:
        ChatbotConfig: Configuration instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = ChatbotConfig()
    return _config_instance
