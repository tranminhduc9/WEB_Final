"""
Test Full Chatbot Graph Flow

Tests for the complete LangGraph chatbot including:
- Intent detection (VECTOR_SEARCH vs CHIT_CHAT)
- RAG retrieval flow
- Generation with context
- Grader evaluation
- Resample loop

NOTE: These tests make actual LLM calls, so they:
- Enable LangSmith tracing for debugging
- Include delays (15-20s) to avoid rate limits
"""

import pytest
import asyncio
import time
import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

# Delay between LLM calls
DELAY_SECONDS = 17


def delay_for_rate_limit():
    """Add delay to avoid rate limit."""
    print(f"\n⏳ Waiting {DELAY_SECONDS}s for rate limit...")
    time.sleep(DELAY_SECONDS)


class TestIntentDetection:
    """Test intent detection node."""
    
    @pytest.mark.asyncio
    async def test_travel_query_intent(self):
        """Travel query should be classified as VECTOR_SEARCH."""
        from chatbot.graph import intent_detection_node
        
        state = {
            "user_query": "Địa điểm du lịch nổi tiếng ở Hà Nội",
            "messages": [],
            "safety_violation": False,
        }
        
        result = await intent_detection_node(state)
        
        print(f"\n📊 Intent Result:")
        print(f"   Intent: {result.get('intent')}")
        print(f"   Refined Query: {result.get('refined_query')}")
        
        assert result.get("intent") == "VECTOR_SEARCH"
        assert result.get("refined_query") != ""
        print("✅ Travel query correctly classified as VECTOR_SEARCH")
        
        delay_for_rate_limit()
    
    @pytest.mark.asyncio
    async def test_chitchat_intent(self):
        """Chitchat query should be classified as CHIT_CHAT."""
        from chatbot.graph import intent_detection_node
        
        state = {
            "user_query": "Xin chào, bạn khỏe không?",
            "messages": [],
            "safety_violation": False,
        }
        
        result = await intent_detection_node(state)
        
        print(f"\n📊 Intent Result:")
        print(f"   Intent: {result.get('intent')}")
        print(f"   Refined Query: {result.get('refined_query')}")
        
        assert result.get("intent") == "CHIT_CHAT"
        print("✅ Chitchat query correctly classified as CHIT_CHAT")
        
        delay_for_rate_limit()
    
    @pytest.mark.asyncio
    async def test_context_resolution(self):
        """Query with reference should resolve from context."""
        from chatbot.graph import intent_detection_node
        
        # Simulate conversation about Hồ Hoàn Kiếm
        state = {
            "user_query": "Nó nằm ở đâu?",  # "Nó" = Hồ Hoàn Kiếm
            "messages": [
                {"role": "user", "content": "Hồ Hoàn Kiếm có gì hay?"},
                {"role": "assistant", "content": "Hồ Hoàn Kiếm là biểu tượng của Hà Nội..."}
            ],
            "safety_violation": False,
        }
        
        result = await intent_detection_node(state)
        
        print(f"\n📊 Context Resolution:")
        print(f"   Original: 'Nó nằm ở đâu?'")
        print(f"   Refined: {result.get('refined_query')}")
        
        # The refined query should mention Hồ Hoàn Kiếm
        refined = result.get("refined_query", "").lower()
        assert "hồ" in refined or "hoàn" in refined or "kiếm" in refined
        print("✅ Context correctly resolved")
        
        delay_for_rate_limit()


class TestGenerationNode:
    """Test generation node."""
    
    @pytest.mark.asyncio
    async def test_generation_with_documents(self):
        """Generation should use documents context."""
        from chatbot.graph import generation_node
        
        state = {
            "intent": "VECTOR_SEARCH",
            "refined_query": "Hồ Hoàn Kiếm có gì hay?",
            "messages": [],
            "documents": [
                {
                    "title": "Hồ Hoàn Kiếm - Trái tim Hà Nội",
                    "content": "Hồ Hoàn Kiếm nằm ở trung tâm Hà Nội, là biểu tượng của thủ đô với đền Ngọc Sơn và tháp Rùa.",
                    "rating": 4.8
                }
            ],
        }
        
        result = await generation_node(state)
        generation = result.get("generation", "")
        
        print(f"\n📝 Generation Result:")
        print(f"   {generation[:200]}...")
        
        assert len(generation) > 50
        print("✅ Generation produced response from documents")
        
        delay_for_rate_limit()
    
    @pytest.mark.asyncio
    async def test_chitchat_generation(self):
        """Chitchat should generate friendly response."""
        from chatbot.graph import generation_node
        
        state = {
            "intent": "CHIT_CHAT",
            "refined_query": "Xin chào!",
            "messages": [],
            "documents": [],
        }
        
        result = await generation_node(state)
        generation = result.get("generation", "")
        
        print(f"\n📝 Chitchat Response:")
        print(f"   {generation[:200]}...")
        
        assert len(generation) > 10
        print("✅ Chitchat generated friendly response")
        
        delay_for_rate_limit()


class TestFullGraphFlow:
    """Test complete graph execution."""
    
    @pytest.mark.asyncio
    async def test_full_travel_flow(self):
        """Test complete flow for travel query."""
        from chatbot.graph import run_chatbot
        
        result = await run_chatbot(
            user_query="Cho tôi biết về phở Hà Nội",
            session_id="test-session-1",
            messages=[],
            user_id=1
        )
        
        print(f"\n🔄 Full Travel Flow Result:")
        print(f"   Intent: {result.get('intent')}")
        print(f"   Documents: {len(result.get('documents', []))}")
        print(f"   Retries: {result.get('retry_count')}")
        print(f"   Response: {result.get('generation', '')[:150]}...")
        
        assert result.get("safety_violation") is False
        assert result.get("intent") == "VECTOR_SEARCH"
        assert len(result.get("generation", "")) > 50
        print("✅ Full travel flow completed successfully")
        
        delay_for_rate_limit()
    
    @pytest.mark.asyncio
    async def test_full_chitchat_flow(self):
        """Test complete flow for chitchat query."""
        from chatbot.graph import run_chatbot
        
        result = await run_chatbot(
            user_query="Chào bạn, hôm nay thời tiết đẹp quá!",
            session_id="test-session-2",
            messages=[],
            user_id=1
        )
        
        print(f"\n🔄 Full Chitchat Flow Result:")
        print(f"   Intent: {result.get('intent')}")
        print(f"   Response: {result.get('generation', '')[:150]}...")
        
        assert result.get("safety_violation") is False
        assert result.get("intent") == "CHIT_CHAT"
        assert len(result.get("generation", "")) > 10
        print("✅ Full chitchat flow completed successfully")
        
        delay_for_rate_limit()
    
    @pytest.mark.asyncio
    async def test_guardrail_blocks_unsafe(self):
        """Guardrail should block unsafe queries."""
        from chatbot.graph import run_chatbot
        
        result = await run_chatbot(
            user_query="dm thằng ngu",  # Profanity
            session_id="test-session-3",
            messages=[],
            user_id=1
        )
        
        print(f"\n🛡️ Guardrail Block Result:")
        print(f"   Safety Violation: {result.get('safety_violation')}")
        print(f"   Response: {result.get('generation', '')[:100]}...")
        
        assert result.get("safety_violation") is True
        assert "ngôn ngữ không phù hợp" in result.get("generation", "")
        print("✅ Guardrail correctly blocked unsafe query")
        
        # No delay needed - guardrail doesn't call LLM
    
    @pytest.mark.asyncio
    async def test_conversation_context(self):
        """Test multi-turn conversation with context."""
        from chatbot.graph import run_chatbot
        
        # First turn
        result1 = await run_chatbot(
            user_query="Hồ Gươm có gì hay?",
            session_id="test-session-4",
            messages=[],
            user_id=1
        )
        
        print(f"\n💬 Turn 1: Hồ Gươm có gì hay?")
        print(f"   Response: {result1.get('generation', '')[:100]}...")
        
        delay_for_rate_limit()
        
        # Second turn with reference
        messages = [
            {"role": "user", "content": "Hồ Gươm có gì hay?"},
            {"role": "assistant", "content": result1.get("generation", "")[:200]}
        ]
        
        result2 = await run_chatbot(
            user_query="Nên đi vào lúc nào?",  # "Nên đi" refers to Hồ Gươm
            session_id="test-session-4",
            messages=messages,
            user_id=1
        )
        
        print(f"\n💬 Turn 2: Nên đi vào lúc nào?")
        print(f"   Refined: {result2.get('refined_query', '')}")
        print(f"   Response: {result2.get('generation', '')[:100]}...")
        
        assert len(result2.get("generation", "")) > 30
        print("✅ Multi-turn conversation handled correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--tb=short"])
