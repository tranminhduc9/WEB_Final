"""
Embedding Manager

Quản lý embeddings cho Adaptive RAG Chatbot:
- Sử dụng Google text-embedding-004 (miễn phí với rate limit)
- One-time embedding cho posts hiện có
- Incremental embedding cho posts mới
- Caching để tránh rate limit
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
import google.generativeai as genai
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from .config import get_config, ChatbotConfig

logger = logging.getLogger(__name__)


class EmbeddingManager:
    """
    Quản lý embeddings với Google Generative AI.
    
    Features:
    - Rate limit handling với tenacity retry
    - Batch embedding để tối ưu API calls
    - Check và skip documents đã có embedding
    """
    
    def __init__(self, config: Optional[ChatbotConfig] = None):
        """
        Khởi tạo EmbeddingManager.
        
        Args:
            config: ChatbotConfig instance (optional, uses singleton if not provided)
        """
        self.config = config or get_config()
        
        # Configure Google AI
        genai.configure(api_key=self.config.google_api_key)
        
        # MongoDB connection (will be set on connect)
        self.db: Optional[AsyncIOMotorDatabase] = None
        self._client: Optional[AsyncIOMotorClient] = None
    
    async def connect(self) -> None:
        """Kết nối MongoDB."""
        if self._client is None:
            self._client = AsyncIOMotorClient(self.config.mongo_uri)
            self.db = self._client[self.config.mongo_db_name]
            logger.info(f"EmbeddingManager connected to MongoDB: {self.config.mongo_db_name}")
    
    async def disconnect(self) -> None:
        """Đóng kết nối MongoDB."""
        if self._client:
            self._client.close()
            self._client = None
            self.db = None
    
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=3, max=60),
        retry=retry_if_exception_type((Exception,)),
        before_sleep=lambda retry_state: logger.warning(
            f"Embedding API rate limit, retrying in {retry_state.next_action.sleep} seconds..."
        )
    )
    def create_embedding(self, text: str) -> List[float]:
        """
        Tạo embedding cho một đoạn văn bản.
        
        Sử dụng tenacity để retry khi gặp rate limit.
        
        Args:
            text: Văn bản cần embedding
            
        Returns:
            List[float]: Vector embedding (768 dimensions)
        """
        if not text or not text.strip():
            # Return zero vector for empty text
            return [0.0] * self.config.embedding_dimensions
        
        # Clean text
        text = text.strip()[:8000]  # Limit text length
        
        # Create embedding using Google's API
        result = genai.embed_content(
            model=self.config.embedding_model,
            content=text,
            task_type="retrieval_document"
        )
        
        return result['embedding']
    
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=3, max=60),
        retry=retry_if_exception_type((Exception,)),
    )
    def create_query_embedding(self, query: str) -> List[float]:
        """
        Tạo embedding cho query (optimized for retrieval).
        
        Args:
            query: Query text
            
        Returns:
            List[float]: Query embedding vector
        """
        if not query or not query.strip():
            return [0.0] * self.config.embedding_dimensions
        
        query = query.strip()[:1000]  # Queries are typically shorter
        
        result = genai.embed_content(
            model=self.config.embedding_model,
            content=query,
            task_type="retrieval_query"  # Optimized for query
        )
        
        return result['embedding']
    
    async def embed_post(self, post_id: str, force: bool = False) -> bool:
        """
        Tạo embedding cho một post và update vào MongoDB.
        
        Args:
            post_id: ID của post
            force: Force re-embedding even if already exists
            
        Returns:
            bool: True nếu thành công
        """
        await self.connect()
        
        collection = self.db[self.config.posts_collection]
        
        # Get post
        post = await collection.find_one({"_id": post_id})
        if not post:
            logger.warning(f"Post not found: {post_id}")
            return False
        
        # Check if already embedded (skip to avoid rate limit)
        if not force and post.get("embedding"):
            logger.debug(f"Post {post_id} already has embedding, skipping")
            return True
        
        # Create embedding from title + content
        text = f"{post.get('title', '')} {post.get('content', '')}"
        
        try:
            embedding = self.create_embedding(text)
            
            # Update document
            await collection.update_one(
                {"_id": post_id},
                {
                    "$set": {
                        "embedding": embedding,
                        "embedding_updated_at": datetime.utcnow()
                    }
                }
            )
            
            logger.info(f"Embedded post: {post_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to embed post {post_id}: {e}")
            return False
    
    async def embed_all_posts(self, batch_size: int = 10) -> Dict[str, int]:
        """
        Embedding tất cả posts chưa có embedding.
        
        One-time operation để khởi tạo embeddings.
        
        Args:
            batch_size: Số posts xử lý mỗi batch (để tránh rate limit)
            
        Returns:
            Dict với thống kê: {total, embedded, skipped, failed}
        """
        await self.connect()
        
        collection = self.db[self.config.posts_collection]
        
        # Find posts without embedding
        cursor = collection.find(
            {"embedding": {"$exists": False}},
            {"_id": 1, "title": 1, "content": 1}
        )
        
        stats = {"total": 0, "embedded": 0, "skipped": 0, "failed": 0}
        
        async for post in cursor:
            stats["total"] += 1
            post_id = post["_id"]
            
            try:
                text = f"{post.get('title', '')} {post.get('content', '')}"
                
                if not text.strip():
                    stats["skipped"] += 1
                    continue
                
                embedding = self.create_embedding(text)
                
                await collection.update_one(
                    {"_id": post_id},
                    {
                        "$set": {
                            "embedding": embedding,
                            "embedding_updated_at": datetime.utcnow()
                        }
                    }
                )
                
                stats["embedded"] += 1
                logger.info(f"Embedded {stats['embedded']}/{stats['total']}: {post_id}")
                
            except Exception as e:
                stats["failed"] += 1
                logger.error(f"Failed to embed {post_id}: {e}")
        
        logger.info(f"Embedding complete: {stats}")
        return stats
    
    async def get_posts_without_embedding(self) -> int:
        """
        Đếm số posts chưa có embedding.
        
        Returns:
            int: Số lượng posts chưa được embed
        """
        await self.connect()
        
        collection = self.db[self.config.posts_collection]
        count = await collection.count_documents({"embedding": {"$exists": False}})
        
        return count


# ===========================================
# Convenience Functions
# ===========================================

_embedding_manager: Optional[EmbeddingManager] = None


def get_embedding_manager() -> EmbeddingManager:
    """
    Get singleton EmbeddingManager instance.
    
    Returns:
        EmbeddingManager: Singleton instance
    """
    global _embedding_manager
    if _embedding_manager is None:
        _embedding_manager = EmbeddingManager()
    return _embedding_manager


async def embed_query(query: str) -> List[float]:
    """
    Convenience function để embed một query.
    
    Args:
        query: Query text
        
    Returns:
        List[float]: Query embedding
    """
    manager = get_embedding_manager()
    return manager.create_query_embedding(query)


async def embed_text(text: str) -> List[float]:
    """
    Convenience function để embed một text.
    
    Args:
        text: Text to embed
        
    Returns:
        List[float]: Text embedding
    """
    manager = get_embedding_manager()
    return manager.create_embedding(text)
