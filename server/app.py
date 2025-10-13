"""
FastAPI application exposing chatbot endpoints under /chatbot.
"""
import uvicorn
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from chatbot.interfaces import ChatMessage
from chatbot.logger import ChatbotLogger
from chatbot.utils import (
    build_chatbot_from_env,
    to_domain_history,
    to_response_dict,
    map_exception,
)


# ---------- Pydantic Schemas ----------

class ChatMessageSchema(BaseModel):
    role: str = Field(..., pattern=r"^(user|assistant|system)$")
    content: str
    timestamp: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[ChatMessageSchema]] = None


class ChatbotResponse(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = None
    usage: Optional[Dict[str, Any]] = None
    model: Optional[str] = None


class HealthResponse(BaseModel):
    healthy: bool


class ErrorResponse(BaseModel):
    detail: str


# ---------- App & Chatbot Init ----------

app = FastAPI(title="Chatbot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


logger = ChatbotLogger(name="chatbot.api")


# Singleton chatbot instance
_chatbot = None


def get_chatbot():
    """Lazy-init and return the singleton chatbot instance."""
    global _chatbot
    if _chatbot is None:
        _chatbot = build_chatbot_from_env()
    return _chatbot


# ---------- Helpers ----------

def to_domain_history(history: Optional[List[ChatMessageSchema]]) -> Optional[List[ChatMessage]]:
    if history is None:
        return None
    domain: List[ChatMessage] = []
    for m in history:
        domain.append(ChatMessage(role=m.role, content=m.content, timestamp=m.timestamp, metadata=m.metadata))
    return domain


# ---------- Endpoints (/chatbot/...) ----------

@app.post("/chatbot/chat", response_model=ChatbotResponse, responses={400: {"model": ErrorResponse}, 429: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def chatbot_chat(req: ChatRequest, request: Request):
    bot = get_chatbot()
    try:
        logger.log_request(req.message)
        resp = await bot.chat(req.message, to_domain_history(req.conversation_history))
        data = to_response_dict(resp)
        logger.log_response(data.get("content", ""), duration_ms=0.0, model=data.get("model") or "unknown")
        return data
    except Exception as e:
        status, detail = map_exception(e)
        logger.log_error(e, operation="chat")
        raise HTTPException(status_code=status, detail=detail)


@app.post("/chatbot/reset", response_model=HealthResponse, responses={500: {"model": ErrorResponse}})
async def chatbot_reset():
    bot = get_chatbot()
    await bot.reset_conversation()
    return HealthResponse(healthy=True)


@app.get("/chatbot/history", response_model=List[ChatMessageSchema], responses={500: {"model": ErrorResponse}})
def chatbot_history():
    bot = get_chatbot()
    hist = bot.get_conversation_history()
    return [ChatMessageSchema(role=m.role, content=m.content, timestamp=m.timestamp, metadata=m.metadata) for m in hist]


@app.get("/chatbot/health", response_model=HealthResponse)
def chatbot_health():
    try:
        bot = get_chatbot()
        return HealthResponse(healthy=bot.is_healthy())
    except Exception:
        return HealthResponse(healthy=False)


# Local dev entrypoint: uvicorn server.app:app --reload

if __name__ == "__main__":
    # Run on localhost:8000
    uvicorn.run(app, host="127.0.0.1", port=8000)


