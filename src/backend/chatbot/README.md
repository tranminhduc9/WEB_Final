# Adaptive RAG Chatbot - Hướng dẫn Sử dụng

Hệ thống Chatbot Tư vấn Du lịch sử dụng kiến trúc Adaptive RAG với LangGraph.

## 📋 Mục lục

1. [Kiến trúc Hệ thống](#kiến-trúc-hệ-thống)
2. [Cấu hình Environment](#cấu-hình-environment)
3. [Setup MongoDB Atlas Vector Index](#setup-mongodb-atlas-vector-index)
4. [Chạy Embedding Lần Đầu](#chạy-embedding-lần-đầu)
5. [API Endpoints](#api-endpoints)
6. [Troubleshooting](#troubleshooting)

---

## 🏗️ Kiến trúc Hệ thống

```
┌─────────────────────────────────────────────────────────────────┐
│                    Adaptive RAG Flow                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  START → guardrail → intent → (retrieval) → generation → grader │
│              │           │          ↑              │       │     │
│              │           │          │              │       │     │
│              ↓           ↓          │              ↓       ↓     │
│           [REJECT]  [CHIT_CHAT]     └── resample ←─[FAIL]       │
│                          ↓                              ↓       │
│                    [RESPONSE]                      [PASS/MAX]   │
│                                                         ↓       │
│                                                     [RESPONSE]  │
└─────────────────────────────────────────────────────────────────┘
```

### Các Nodes:

| Node | Chức năng | Sử dụng LLM? |
|------|-----------|--------------|
| `guardrail` | Kiểm tra profanity, PII | ❌ (Algorithmic) |
| `intent_detection` | Phân loại ý định, merge context | ✅ Gemini |
| `retrieval` | Vector search MongoDB Atlas | ❌ (Embedding only) |
| `generation` | Sinh câu trả lời | ✅ Gemini |
| `grader` | Đánh giá chất lượng | ✅ Gemini |
| `resample` | Viết lại query nếu fail | ✅ Gemini |

---

## ⚙️ Cấu hình Environment

Thêm các biến sau vào file `.env`, `.env.prod`, `.env.production`:

```bash
# ===========================================
# CHATBOT - Adaptive RAG Configuration
# ===========================================

# Google Gemini API (BẮT BUỘC)
GOOGLE_API_KEY=your_google_api_key_here

# MongoDB Atlas (BẮT BUỘC)
MONGO_URI_ATLAS=mongodb+srv://username:password@cluster.mongodb.net/

# LangSmith Tracing (TÙY CHỌN - để debug)
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=hanoi-travel-chatbot

# Chatbot Settings (TÙY CHỌN - có default)
CHATBOT_LLM_MODEL=gemini-2.5-flash
CHATBOT_EMBEDDING_MODEL=models/text-embedding-004
CHATBOT_VECTOR_INDEX=vector_index
CHATBOT_LLM_TEMPERATURE=0.7
CHATBOT_LLM_MAX_TOKENS=2048
```

---

## 🔍 Setup MongoDB Atlas Vector Index

### Bước 1: Truy cập MongoDB Atlas

1. Đăng nhập [MongoDB Atlas](https://cloud.mongodb.com)
2. Chọn Cluster → Database → Collection `posts_mongo`

### Bước 2: Tạo Search Index

1. Click tab **"Atlas Search"**
2. Click **"Create Search Index"**
3. Chọn **"JSON Editor"**
4. Chọn collection: `hanoi_travel_mongo.posts_mongo`
5. Đặt tên index: `vector_index`

### Bước 3: Paste JSON Definition

```json
{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 768,
      "similarity": "cosine"
    },
    {
      "type": "filter",
      "path": "status"
    },
    {
      "type": "filter",
      "path": "related_place_id"
    }
  ]
}
```

### Bước 4: Create Index

Click **"Create Search Index"** và đợi status chuyển thành **"Active"** (khoảng 1-2 phút).

---

## 🚀 Chạy Embedding Lần Đầu

Trước khi chatbot hoạt động, cần embedding tất cả posts hiện có.

### Cách 1: Chạy Script

```bash
cd src/backend
python -c "
import asyncio
from chatbot.embeddings import EmbeddingManager

async def main():
    manager = EmbeddingManager()
    stats = await manager.embed_all_posts()
    print(f'Embedded: {stats}')

asyncio.run(main())
"
```

### Cách 2: Dùng API (sau khi server chạy)

```bash
curl -X POST http://localhost:8080/api/v1/chatbot/embed-all
```

### Kiểm tra tiến độ

```bash
python -c "
import asyncio
from chatbot.embeddings import EmbeddingManager

async def main():
    manager = EmbeddingManager()
    count = await manager.get_posts_without_embedding()
    print(f'Posts chưa embedding: {count}')

asyncio.run(main())
"
```

---

## 📡 API Endpoints

### POST `/api/v1/chatbot/message`

Gửi tin nhắn đến chatbot.

**Request:**
```json
{
  "session_id": "optional-session-id",
  "message": "Cho tôi biết về Hồ Hoàn Kiếm"
}
```

**Response:**
```json
{
  "success": true,
  "session_id": "abc-123",
  "bot_response": "Hồ Hoàn Kiếm là...",
  "intent": "VECTOR_SEARCH",
  "safety_violation": false,
  "documents_used": 3,
  "retry_count": 0
}
```

### GET `/api/v1/chatbot/history`

Lấy lịch sử chat.

**Query params:**
- `session_id` (optional): Lọc theo session
- `limit` (default: 20): Số tin nhắn tối đa

---

## 🔧 Troubleshooting

### 1. "GOOGLE_API_KEY is required"

→ Chưa cấu hình API key trong `.env`

### 2. Vector search trả về 0 kết quả

→ Kiểm tra:
- Index `vector_index` đã Active chưa?
- Posts đã có field `embedding` chưa?
- Filter `status: "approved"` có đúng không?

### 3. Rate limit errors

→ Chatbot đã có retry với exponential backoff. Nếu vẫn lỗi:
- Giảm `CHATBOT_LLM_MAX_TOKENS`
- Tăng delay giữa các requests

### 4. Lỗi "MongoDB not connected"

→ Kiểm tra `MONGO_URI_ATLAS` và whitelist IP trong Atlas

---

## 📁 Cấu trúc Module

```
chatbot/
├── __init__.py      # Package exports
├── config.py        # Configuration settings
├── models.py        # Pydantic models (AgentState, ChatLog)
├── utils.py         # Guardrail functions (profanity, PII)
├── embeddings.py    # Embedding manager
├── graph.py         # LangGraph StateGraph
└── README.md        # Tài liệu này
```
