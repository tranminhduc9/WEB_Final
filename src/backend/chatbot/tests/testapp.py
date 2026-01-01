"""
Chatbot Test Application

Ứng dụng test chatbot qua CLI với 2 lựa chọn:
1. Chat tương tác - Nhập câu hỏi và nhận response (JSON)
2. Chạy test tự động - Chạy các test cases có sẵn

USAGE:
    python chatbot/tests/testapp.py
"""

import os
import sys
import json
import asyncio
import time
from pathlib import Path
from datetime import datetime

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

# Load environment
env_files = [backend_dir.parent / ".env.prod", backend_dir.parent / ".env"]
for env_file in env_files:
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key and value and key not in os.environ:
                        os.environ[key] = value
        break

# Enable LangSmith tracing
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "hanoi-travel-chatbot-tests")


# ===========================================
# Test Cases
# ===========================================

TEST_CASES = [
    {
        "name": "Travel Query - Hồ Hoàn Kiếm",
        "query": "Cho tôi biết về Hồ Hoàn Kiếm",
        "expected_intent": "VECTOR_SEARCH",
        "description": "Test query về địa điểm du lịch nổi tiếng"
    },
    {
        "name": "Chitchat - Chào hỏi",
        "query": "Xin chào, bạn khỏe không?",
        "expected_intent": "CHIT_CHAT",
        "description": "Test câu chào hỏi xã giao"
    },
    {
        "name": "Guardrail - Profanity",
        "query": "dm thằng ngu",
        "expected_intent": None,
        "expected_violation": True,
        "description": "Test guardrail chặn ngôn ngữ thô tục"
    },
    {
        "name": "Guardrail - PII Phone",
        "query": "Số điện thoại tôi là 0912345678",
        "expected_intent": None,
        "expected_violation": True,
        "description": "Test guardrail chặn thông tin cá nhân"
    },
    {
        "name": "Travel Query - Restaurant",
        "query": "Nhà hàng ngon ở phố cổ Hà Nội",
        "expected_intent": "VECTOR_SEARCH",
        "description": "Test query về ẩm thực"
    },
    {
        "name": "Context Resolution",
        "query": "Nó nằm ở đâu?",
        "messages": [
            {"role": "user", "content": "Hồ Gươm có gì hay?"},
            {"role": "assistant", "content": "Hồ Gươm là biểu tượng của Hà Nội với đền Ngọc Sơn..."}
        ],
        "expected_intent": "VECTOR_SEARCH",
        "description": "Test context resolution - 'Nó' refers to previous topic"
    },
]


# ===========================================
# Utility Functions
# ===========================================

def print_header():
    """Print application header."""
    print("\n" + "=" * 60)
    print("🧪 CHATBOT TEST APPLICATION")
    print("=" * 60)
    print(f"📍 LangSmith Tracing: {os.getenv('LANGCHAIN_TRACING_V2')}")
    print(f"📍 Project: {os.getenv('LANGCHAIN_PROJECT')}")
    print(f"📍 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


def print_menu():
    """Print main menu."""
    print("\n📋 MENU:")
    print("  1. Chat tương tác (Interactive Chat)")
    print("  2. Chạy test tự động (Run Preset Tests)")
    print("  3. Chạy một test case cụ thể")
    print("  0. Thoát (Exit)")
    print()


def format_json(data: dict) -> str:
    """Format JSON with proper Vietnamese display."""
    return json.dumps(data, ensure_ascii=False, indent=2)


async def run_chatbot_query(query: str, messages: list = None, session_id: str = None):
    """Run a single chatbot query."""
    from chatbot.graph import run_chatbot
    
    session_id = session_id or f"test-{int(time.time())}"
    
    result = await run_chatbot(
        user_query=query,
        session_id=session_id,
        messages=messages or [],
        user_id=1
    )
    
    return result


# ===========================================
# Option 1: Interactive Chat
# ===========================================

async def interactive_chat():
    """Interactive chat mode."""
    print("\n" + "-" * 60)
    print("💬 INTERACTIVE CHAT MODE")
    print("-" * 60)
    print("Nhập câu hỏi để chat với bot.")
    print("Gõ 'exit' hoặc 'quit' để thoát.")
    print("Gõ 'clear' để xóa lịch sử chat.")
    print("-" * 60 + "\n")
    
    messages = []
    session_id = f"interactive-{int(time.time())}"
    
    while True:
        try:
            query = input("👤 Bạn: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['exit', 'quit', 'thoát']:
                print("\n👋 Tạm biệt!")
                break
            
            if query.lower() == 'clear':
                messages = []
                print("🗑️ Đã xóa lịch sử chat.\n")
                continue
            
            print("⏳ Đang xử lý...\n")
            start_time = time.time()
            
            result = await run_chatbot_query(query, messages, session_id)
            
            elapsed = time.time() - start_time
            
            # Print formatted response
            print("🤖 Bot Response:")
            print("-" * 40)
            
            response_data = {
                "intent": result.get("intent", ""),
                "safety_violation": result.get("safety_violation", False),
                "generation": result.get("generation", ""),
                "documents_used": len(result.get("documents", [])),
                "retry_count": result.get("retry_count", 0),
                "refined_query": result.get("refined_query", ""),
                "elapsed_seconds": round(elapsed, 2)
            }
            
            print(format_json(response_data))
            print("-" * 40 + "\n")
            
            # Add to history if not violation
            if not result.get("safety_violation"):
                messages.append({"role": "user", "content": query})
                messages.append({
                    "role": "assistant", 
                    "content": result.get("generation", "")[:500]
                })
            
            # Rate limit delay
            print("⏳ Đợi 15s để tránh rate limit...")
            await asyncio.sleep(15)
            print()
            
        except KeyboardInterrupt:
            print("\n\n👋 Đã dừng.")
            break
        except Exception as e:
            print(f"❌ Lỗi: {e}\n")


# ===========================================
# Option 2: Run Preset Tests
# ===========================================

async def run_preset_tests():
    """Run all preset test cases."""
    print("\n" + "-" * 60)
    print("🧪 RUNNING PRESET TESTS")
    print("-" * 60)
    print(f"Total test cases: {len(TEST_CASES)}")
    print("Delay between tests: 17 seconds (to avoid rate limit)")
    print("-" * 60 + "\n")
    
    passed = 0
    failed = 0
    results = []
    
    for i, test in enumerate(TEST_CASES, 1):
        print(f"\n[{i}/{len(TEST_CASES)}] {test['name']}")
        print(f"   📝 Query: {test['query']}")
        print(f"   📋 {test['description']}")
        
        try:
            messages = test.get("messages", [])
            
            start_time = time.time()
            result = await run_chatbot_query(test['query'], messages)
            elapsed = time.time() - start_time
            
            # Check expectations
            test_passed = True
            issues = []
            
            # Check safety violation
            if test.get("expected_violation"):
                if not result.get("safety_violation"):
                    test_passed = False
                    issues.append("Expected safety_violation=True but got False")
            else:
                if result.get("safety_violation"):
                    test_passed = False
                    issues.append(f"Unexpected safety_violation: {result.get('generation')[:50]}")
            
            # Check intent
            expected_intent = test.get("expected_intent")
            if expected_intent and not result.get("safety_violation"):
                actual_intent = result.get("intent")
                if actual_intent != expected_intent:
                    test_passed = False
                    issues.append(f"Expected intent={expected_intent} but got {actual_intent}")
            
            if test_passed:
                print(f"   ✅ PASSED ({elapsed:.1f}s)")
                passed += 1
            else:
                print(f"   ❌ FAILED ({elapsed:.1f}s)")
                for issue in issues:
                    print(f"      - {issue}")
                failed += 1
            
            # Show brief response
            if not result.get("safety_violation"):
                gen = result.get("generation", "")[:100]
                print(f"   💬 Response: {gen}...")
            
            results.append({
                "name": test['name'],
                "passed": test_passed,
                "elapsed": elapsed,
                "issues": issues
            })
            
            # Rate limit delay (skip for last test)
            if i < len(TEST_CASES):
                print(f"\n   ⏳ Waiting 17s for rate limit...")
                await asyncio.sleep(17)
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            failed += 1
            results.append({
                "name": test['name'],
                "passed": False,
                "error": str(e)
            })
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"   Total:  {len(TEST_CASES)}")
    print(f"   Passed: {passed} ✅")
    print(f"   Failed: {failed} ❌")
    print(f"   Rate:   {passed/len(TEST_CASES)*100:.1f}%")
    print("=" * 60)
    
    if failed > 0:
        print("\n❌ Failed Tests:")
        for r in results:
            if not r['passed']:
                print(f"   - {r['name']}")
                for issue in r.get('issues', []):
                    print(f"     {issue}")
    
    return passed, failed


# ===========================================
# Option 3: Run Specific Test
# ===========================================

async def run_specific_test():
    """Run a specific test case."""
    print("\n" + "-" * 60)
    print("📋 AVAILABLE TEST CASES:")
    print("-" * 60)
    
    for i, test in enumerate(TEST_CASES, 1):
        print(f"  {i}. {test['name']}")
        print(f"     Query: {test['query'][:50]}...")
    
    print("-" * 60)
    
    try:
        choice = input("\nChọn test case (1-6) hoặc 0 để quay lại: ").strip()
        idx = int(choice) - 1
        
        if idx < 0 or idx >= len(TEST_CASES):
            print("Quay lại menu chính.")
            return
        
        test = TEST_CASES[idx]
        print(f"\n🧪 Running: {test['name']}")
        print(f"   Query: {test['query']}")
        
        messages = test.get("messages", [])
        result = await run_chatbot_query(test['query'], messages)
        
        print("\n📊 Result:")
        print(format_json({
            "intent": result.get("intent"),
            "safety_violation": result.get("safety_violation"),
            "generation": result.get("generation"),
            "refined_query": result.get("refined_query"),
            "documents_count": len(result.get("documents", [])),
            "retry_count": result.get("retry_count", 0)
        }))
        
    except ValueError:
        print("Lựa chọn không hợp lệ.")
    except Exception as e:
        print(f"❌ Lỗi: {e}")


# ===========================================
# Main
# ===========================================

async def main():
    """Main entry point."""
    print_header()
    
    while True:
        print_menu()
        
        try:
            choice = input("👉 Chọn (0-3): ").strip()
            
            if choice == "1":
                await interactive_chat()
            elif choice == "2":
                await run_preset_tests()
            elif choice == "3":
                await run_specific_test()
            elif choice == "0":
                print("\n👋 Goodbye!")
                break
            else:
                print("❌ Lựa chọn không hợp lệ. Vui lòng chọn 0-3.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Đã dừng.")
            break
        except Exception as e:
            print(f"❌ Lỗi: {e}")


if __name__ == "__main__":
    asyncio.run(main())
