"""
LangGraph Adaptive RAG Chatbot

Định nghĩa StateGraph với các nodes:
1. guardrail_node - Kiểm tra an toàn (algorithmic, no LLM)
2. intent_detection_node - Phân loại ý định + merge context
3. retrieval_node - Vector search MongoDB Atlas
4. generation_node - Sinh câu trả lời với Gemini
5. grader_node - Đánh giá chất lượng câu trả lời
6. resample_node - Xử lý retry loop
"""

import logging
from typing import Dict, Any, List, Optional, Literal
from datetime import datetime

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from .config import get_config, ChatbotConfig
from .models import AgentState
from .utils import is_safe_query, format_documents_for_context, clean_text
from .embeddings import get_embedding_manager

logger = logging.getLogger(__name__)


# ===========================================
# Node Implementations
# ===========================================

async def guardrail_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node 1: Guardrail - Kiểm tra an toàn.
    
    KHÔNG sử dụng LLM. Dùng thuật toán/regex để kiểm tra:
    - Tục tĩu (Profanity list tiếng Việt/Anh)
    - Thông tin nhạy cảm (PII: SĐT, Email)
    
    Output:
    - Nếu vi phạm: safety_violation=True, generation=rejection_message
    - Nếu sạch: Giữ nguyên state
    """
    user_query = state.get("user_query", "")
    
    logger.info(f"[Guardrail] Checking query: {user_query[:50]}...")
    
    is_safe, rejection_message = is_safe_query(user_query)
    
    if not is_safe:
        logger.warning(f"[Guardrail] Safety violation detected")
        return {
            "safety_violation": True,
            "generation": rejection_message
        }
    
    logger.info("[Guardrail] Query is safe")
    return {"safety_violation": False}


async def intent_detection_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node 2: Intent Detection - Phân loại ý định và merge context.
    
    Sử dụng Gemini 2.5 Flash để:
    1. Gộp user_query + messages (lịch sử) → refined_query
    2. Phân loại intent: VECTOR_SEARCH hoặc CHIT_CHAT
    
    Ví dụ: "Nó giá bao nhiêu?" + context "Khách sạn X" → "Khách sạn X giá bao nhiêu?"
    """
    config = get_config()
    user_query = state.get("user_query", "")
    messages = state.get("messages", [])
    
    logger.info(f"[Intent] Detecting intent for: {user_query[:50]}...")
    
    # Build context from recent messages
    context_str = ""
    if messages:
        recent_messages = messages[-6:]  # Last 3 exchanges
        context_parts = []
        for msg in recent_messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")[:200]
            context_parts.append(f"{role}: {content}")
        context_str = "\n".join(context_parts)
    
    # Create LLM
    llm = ChatGoogleGenerativeAI(
        model=config.llm_model,
        google_api_key=config.google_api_key,
        temperature=0.3,  # Lower for classification
    )
    
    # Intent detection prompt
    prompt = f"""Bạn là bộ phân loại ý định cho chatbot du lịch Hà Nội.

Lịch sử hội thoại:
{context_str if context_str else "(Không có lịch sử)"}

Câu hỏi hiện tại: {user_query}

NHIỆM VỤ:
1. Viết lại câu hỏi thành câu hoàn chỉnh, rõ nghĩa (resolve references từ lịch sử nếu có)
2. Phân loại ý định:
   - VECTOR_SEARCH: Hỏi về địa điểm, nhà hàng, khách sạn, du lịch, ẩm thực Hà Nội
   - CHIT_CHAT: Chào hỏi, xã giao, câu hỏi không liên quan du lịch

TRẢ LỜI THEO FORMAT (chỉ 2 dòng):
REFINED_QUERY: [câu hỏi đã viết lại]
INTENT: [VECTOR_SEARCH hoặc CHIT_CHAT]"""

    try:
        response = await llm.ainvoke(prompt)
        response_text = response.content
        
        # Parse response
        refined_query = user_query  # Default
        intent = "VECTOR_SEARCH"  # Default
        
        for line in response_text.split("\n"):
            line = line.strip()
            if line.startswith("REFINED_QUERY:"):
                refined_query = line.replace("REFINED_QUERY:", "").strip()
            elif line.startswith("INTENT:"):
                intent_str = line.replace("INTENT:", "").strip().upper()
                if intent_str in ["VECTOR_SEARCH", "CHIT_CHAT"]:
                    intent = intent_str
        
        logger.info(f"[Intent] Detected: {intent}, Refined: {refined_query[:50]}...")
        
        return {
            "refined_query": refined_query,
            "intent": intent
        }
        
    except Exception as e:
        logger.error(f"[Intent] Error: {e}")
        # Fallback: use original query, assume travel-related
        return {
            "refined_query": user_query,
            "intent": "VECTOR_SEARCH"
        }


async def retrieval_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node 3: Retrieval - Tìm kiếm vector trên MongoDB Atlas.
    
    Thực hiện:
    1. Tạo embedding cho refined_query
    2. $vectorSearch trên posts_mongo
    3. $lookup để lấy reviews liên quan
    """
    config = get_config()
    refined_query = state.get("refined_query", state.get("user_query", ""))
    
    logger.info(f"[Retrieval] Searching for: {refined_query[:50]}...")
    
    # Get embedding manager
    embedding_manager = get_embedding_manager()
    await embedding_manager.connect()
    
    try:
        # Create query embedding
        query_embedding = embedding_manager.create_query_embedding(refined_query)
        
        # MongoDB aggregation pipeline with $vectorSearch
        pipeline = [
            {
                "$vectorSearch": {
                    "index": config.vector_index_name,
                    "path": config.vector_field_name,
                    "queryVector": query_embedding,
                    "numCandidates": config.vector_num_candidates,
                    "limit": config.vector_limit,
                    "filter": {"status": "approved"}
                }
            },
            {
                "$lookup": {
                    "from": config.comments_collection,
                    "localField": "_id",
                    "foreignField": "post_id",
                    "as": "reviews"
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "title": 1,
                    "content": 1,
                    "rating": 1,
                    "related_place_id": 1,
                    "author_id": 1,
                    "tags": 1,
                    "reviews": {"$slice": ["$reviews", 3]},  # Limit reviews
                    "score": {"$meta": "vectorSearchScore"}
                }
            }
        ]
        
        # Execute search
        collection = embedding_manager.db[config.posts_collection]
        cursor = collection.aggregate(pipeline)
        
        documents = []
        async for doc in cursor:
            # Convert ObjectId to string
            doc["_id"] = str(doc["_id"])
            documents.append(doc)
        
        logger.info(f"[Retrieval] Found {len(documents)} documents")
        
        return {"documents": documents}
        
    except Exception as e:
        logger.error(f"[Retrieval] Error: {e}")
        # Return empty documents on error
        return {"documents": []}


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=3, max=30),
    retry=retry_if_exception_type((Exception,)),
)
async def _call_llm_with_retry(llm, prompt: str) -> str:
    """Helper function to call LLM with retry."""
    response = await llm.ainvoke(prompt)
    return response.content


async def generation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node 4: Generation - Sinh câu trả lời với Gemini.
    
    Xử lý 2 trường hợp:
    1. CHIT_CHAT: Trả lời xã giao
    2. VECTOR_SEARCH: Trả lời dựa trên documents
    
    Sử dụng tenacity retry để xử lý rate limit.
    """
    config = get_config()
    intent = state.get("intent", "VECTOR_SEARCH")
    refined_query = state.get("refined_query", state.get("user_query", ""))
    documents = state.get("documents", [])
    messages = state.get("messages", [])
    
    logger.info(f"[Generation] Generating response for intent: {intent}")
    
    # Create LLM
    llm = ChatGoogleGenerativeAI(
        model=config.llm_model,
        google_api_key=config.google_api_key,
        temperature=config.llm_temperature,
        max_output_tokens=config.llm_max_tokens,
    )
    
    if intent == "CHIT_CHAT":
        # Simple chitchat response
        prompt = f"""{config.chitchat_prompt}

Câu hỏi: {refined_query}

Trả lời ngắn gọn, thân thiện:"""
    
    else:
        # RAG response with documents
        context = format_documents_for_context(documents)
        
        # Build conversation history
        history_str = ""
        if messages:
            recent = messages[-4:]
            history_parts = [f"{m['role']}: {m['content'][:150]}" for m in recent]
            history_str = "\n".join(history_parts)
        
        prompt = f"""{config.travel_assistant_prompt}

LỊCH SỬ HỘI THOẠI:
{history_str if history_str else "(Không có)"}

THÔNG TIN TỪ CƠ SỞ DỮ LIỆU:
{context}

CÂU HỎI: {refined_query}

TRẢ LỜI (dựa trên thông tin trên, trả lời bằng tiếng Việt):"""
    
    try:
        response = await _call_llm_with_retry(llm, prompt)
        generation = clean_text(response)
        
        logger.info(f"[Generation] Generated response: {generation[:100]}...")
        
        return {"generation": generation}
        
    except Exception as e:
        logger.error(f"[Generation] Error: {e}")
        return {
            "generation": "Xin lỗi, tôi gặp sự cố khi xử lý yêu cầu của bạn. Vui lòng thử lại sau."
        }


async def grader_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node 5: Grader - Đánh giá chất lượng câu trả lời.
    
    Sử dụng LLM để kiểm tra:
    1. Hallucination: Câu trả lời có dựa trên documents không?
    2. Relevancy: Câu trả lời có đúng trọng tâm câu hỏi không?
    
    Output: grader_passed = True/False
    """
    config = get_config()
    generation = state.get("generation", "")
    documents = state.get("documents", [])
    refined_query = state.get("refined_query", "")
    intent = state.get("intent", "")
    
    # Skip grading for chitchat
    if intent == "CHIT_CHAT":
        logger.info("[Grader] Skipping grading for chitchat")
        return {"grader_passed": True}
    
    # Skip grading if no documents (already fallback response)
    if not documents:
        logger.info("[Grader] No documents, accepting response")
        return {"grader_passed": True}
    
    logger.info("[Grader] Evaluating response quality...")
    
    # Create LLM for grading
    llm = ChatGoogleGenerativeAI(
        model=config.llm_model,
        google_api_key=config.google_api_key,
        temperature=0.1,  # Low temperature for consistent grading
    )
    
    # Format documents for grading
    doc_content = "\n".join([
        f"- {d.get('title', '')}: {d.get('content', '')[:200]}"
        for d in documents[:3]
    ])
    
    prompt = f"""Bạn là người đánh giá chất lượng câu trả lời của chatbot du lịch.

DOCUMENTS (thông tin nguồn):
{doc_content}

CÂU HỎI: {refined_query}

CÂU TRẢ LỜI CỦA CHATBOT:
{generation}

ĐÁNH GIÁ:
1. Câu trả lời có dựa trên documents không? (không bịa thông tin)
2. Câu trả lời có liên quan đến câu hỏi không?

TRẢ LỜI: PASS hoặc FAIL (chỉ 1 từ)"""

    try:
        response = await llm.ainvoke(prompt)
        result = response.content.strip().upper()
        
        passed = "PASS" in result
        logger.info(f"[Grader] Result: {'PASS' if passed else 'FAIL'}")
        
        return {"grader_passed": passed}
        
    except Exception as e:
        logger.error(f"[Grader] Error: {e}")
        # On error, accept the response
        return {"grader_passed": True}


async def resample_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node 6: Resample - Xử lý retry loop.
    
    Logic:
    - Tăng retry_count
    - Nếu retry_count < 3: Viết lại refined_query
    - Nếu retry_count >= 3: Giữ nguyên generation hiện tại (trả lời dù không đạt chuẩn)
    
    LƯU Ý: Không add câu trả lời failed vào context, chỉ dùng lịch sử cũ
    """
    config = get_config()
    retry_count = state.get("retry_count", 0) + 1
    refined_query = state.get("refined_query", "")
    
    logger.info(f"[Resample] Retry count: {retry_count}/{config.max_grader_retries}")
    
    if retry_count >= config.max_grader_retries:
        # Max retries reached - accept current response
        logger.info("[Resample] Max retries reached, accepting current response")
        return {
            "retry_count": retry_count,
            "grader_passed": True  # Force pass to exit loop
        }
    
    # Rewrite query for next attempt
    llm = ChatGoogleGenerativeAI(
        model=config.llm_model,
        google_api_key=config.google_api_key,
        temperature=0.5,
    )
    
    prompt = f"""Câu hỏi sau không tìm được kết quả tốt:
"{refined_query}"

Hãy viết lại câu hỏi với từ khóa khác để tìm kiếm tốt hơn.
Chỉ trả lời câu hỏi đã viết lại, không giải thích."""

    try:
        response = await llm.ainvoke(prompt)
        new_query = clean_text(response.content)
        
        logger.info(f"[Resample] New query: {new_query[:50]}...")
        
        return {
            "retry_count": retry_count,
            "refined_query": new_query
        }
        
    except Exception as e:
        logger.error(f"[Resample] Error: {e}")
        return {"retry_count": retry_count}


# ===========================================
# Router Functions (Conditional Edges)
# ===========================================

def route_after_guardrail(state: Dict[str, Any]) -> Literal["intent_detection", "end"]:
    """Route after guardrail check."""
    if state.get("safety_violation", False):
        return "end"
    return "intent_detection"


def route_after_intent(state: Dict[str, Any]) -> Literal["retrieval", "generation"]:
    """Route based on intent classification."""
    intent = state.get("intent", "VECTOR_SEARCH")
    if intent == "CHIT_CHAT":
        return "generation"
    return "retrieval"


def route_after_grader(state: Dict[str, Any]) -> Literal["resample", "end"]:
    """Route based on grader result."""
    if state.get("grader_passed", False):
        return "end"
    return "resample"


def route_after_resample(state: Dict[str, Any]) -> Literal["retrieval", "end"]:
    """Route after resample - retry or end."""
    config = get_config()
    retry_count = state.get("retry_count", 0)
    
    if retry_count >= config.max_grader_retries:
        return "end"
    return "retrieval"


# ===========================================
# Graph Builder
# ===========================================

# Define state schema as TypedDict for proper LangGraph state management
from typing import TypedDict

class ChatbotState(TypedDict, total=False):
    """State schema for chatbot graph."""
    user_query: str
    refined_query: str
    messages: List[Dict[str, Any]]
    documents: List[Dict[str, Any]]
    generation: str
    retry_count: int
    safety_violation: bool
    intent: str
    grader_passed: bool
    session_id: str
    user_id: int


def create_chatbot_graph() -> StateGraph:
    """
    Tạo LangGraph StateGraph cho Adaptive RAG Chatbot.
    
    Flow:
    START → guardrail → intent → (retrieval →) generation → grader → (resample →) END
    
    Returns:
        StateGraph: Compiled graph
    """
    # Create graph with proper state schema
    workflow = StateGraph(ChatbotState)
    
    # Add nodes
    workflow.add_node("guardrail", guardrail_node)
    workflow.add_node("intent_detection", intent_detection_node)
    workflow.add_node("retrieval", retrieval_node)
    workflow.add_node("generation", generation_node)
    workflow.add_node("grader", grader_node)
    workflow.add_node("resample", resample_node)
    
    # Set entry point
    workflow.set_entry_point("guardrail")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "guardrail",
        route_after_guardrail,
        {
            "end": END,
            "intent_detection": "intent_detection"
        }
    )
    
    workflow.add_conditional_edges(
        "intent_detection",
        route_after_intent,
        {
            "retrieval": "retrieval",
            "generation": "generation"
        }
    )
    
    # Retrieval → Generation
    workflow.add_edge("retrieval", "generation")
    
    # Generation → Grader
    workflow.add_edge("generation", "grader")
    
    # Grader conditional
    workflow.add_conditional_edges(
        "grader",
        route_after_grader,
        {
            "resample": "resample",
            "end": END
        }
    )
    
    # Resample conditional
    workflow.add_conditional_edges(
        "resample",
        route_after_resample,
        {
            "retrieval": "retrieval",
            "end": END
        }
    )
    
    # Compile graph
    graph = workflow.compile()
    
    return graph


# ===========================================
# Main Entry Point
# ===========================================

async def run_chatbot(
    user_query: str,
    session_id: str,
    messages: List[Dict[str, str]] = None,
    user_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Chạy chatbot với một query.
    
    Args:
        user_query: Câu hỏi của user
        session_id: Session ID
        messages: Lịch sử chat (không bao gồm câu trả lời failed)
        user_id: User ID (optional)
        
    Returns:
        Dict với kết quả: {
            generation: str,
            intent: str,
            safety_violation: bool,
            documents: List,
            retry_count: int
        }
    """
    logger.info(f"[Chatbot] Processing query: {user_query[:50]}...")
    
    # Create initial state
    initial_state = {
        "user_query": user_query,
        "refined_query": "",
        "messages": messages or [],
        "documents": [],
        "generation": "",
        "retry_count": 0,
        "safety_violation": False,
        "intent": "",
        "grader_passed": None,
        "session_id": session_id,
        "user_id": user_id,
    }
    
    # Create and run graph
    graph = create_chatbot_graph()
    
    # Run graph
    final_state = await graph.ainvoke(initial_state)
    
    logger.info(f"[Chatbot] Completed. Intent: {final_state.get('intent')}, "
                f"Retries: {final_state.get('retry_count')}")
    
    return {
        "generation": final_state.get("generation", ""),
        "intent": final_state.get("intent", ""),
        "safety_violation": final_state.get("safety_violation", False),
        "documents": final_state.get("documents", []),
        "retry_count": final_state.get("retry_count", 0),
        "refined_query": final_state.get("refined_query", ""),
    }
