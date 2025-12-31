"""
Post Stats Sync Service

Module này đồng bộ likes_count và comments_count từ MongoDB collections thực tế
cho các posts. Tương tự như rating_sync.py đã làm cho places.

Các hàm chính:
- calculate_post_stats: Tính toán từ collections thực tế
- sync_post_stats: Sync cho một post
- sync_posts_stats_batch: Sync batch cho nhiều posts  
- on_like_toggled: Handler khi like được toggle
- on_comment_added: Handler khi comment được thêm
- on_comment_deleted: Handler khi comment bị xóa

Author: System
Date: 2024-12-31
"""

import logging
from typing import Dict, Any, List
from bson import ObjectId
from bson.errors import InvalidId

logger = logging.getLogger(__name__)


async def calculate_post_stats(
    post_id: str,
    mongo_client
) -> Dict[str, int]:
    """
    Tính toán likes_count và comments_count cho một post từ MongoDB collections thực tế.
    
    Args:
        post_id: ID của post (string)
        mongo_client: MongoDB client instance
        
    Returns:
        Dict với likes_count và comments_count
    """
    try:
        # Đếm likes từ post_likes collection
        likes_count = await mongo_client.count("post_likes", {"post_id": post_id})
        
        # Đếm comments từ post_comments collection
        comments_count = await mongo_client.count("post_comments", {"post_id": post_id})
        
        logger.debug(f"[POST_STATS] post_id={post_id}: likes={likes_count}, comments={comments_count}")
        
        return {
            "likes_count": likes_count,
            "comments_count": comments_count
        }
        
    except Exception as e:
        logger.error(f"[POST_STATS] Error calculating stats for post {post_id}: {e}")
        return {
            "likes_count": 0,
            "comments_count": 0
        }


async def _get_post_query(post_id: str, mongo_client):
    """Helper để tìm post và trả về query dict chính xác."""
    try:
        post_query = {"_id": ObjectId(post_id)}
        post = await mongo_client.find_one("posts", post_query)
        if post:
            return post_query, post
    except InvalidId:
        pass
    
    post_query = {"_id": post_id}
    post = await mongo_client.find_one("posts", post_query)
    return post_query if post else None, post


async def sync_post_stats(
    post_id: str,
    mongo_client
) -> Dict[str, int]:
    """
    Sync stats cho một post - tính lại và cập nhật likes_count và comments_count.
    
    Args:
        post_id: ID của post
        mongo_client: MongoDB client instance
        
    Returns:
        Dict với likes_count và comments_count đã sync
    """
    try:
        # Tính toán stats từ collections thực tế
        stats = await calculate_post_stats(post_id, mongo_client)
        
        # Tìm post
        post_query, post = await _get_post_query(post_id, mongo_client)
        
        if not post:
            logger.warning(f"[POST_STATS] Post {post_id} not found")
            return stats
        
        # Cập nhật MongoDB
        await mongo_client.update_one("posts", post_query, {
            "likes_count": stats["likes_count"],
            "comments_count": stats["comments_count"]
        })
        
        logger.info(f"[POST_STATS] Synced post {post_id}: likes={stats['likes_count']}, comments={stats['comments_count']}")
        return stats
        
    except Exception as e:
        logger.error(f"[POST_STATS] Error syncing post {post_id}: {e}")
        return {"likes_count": 0, "comments_count": 0}


async def sync_posts_stats_batch(
    post_ids: List[str],
    mongo_client
) -> Dict[str, Dict[str, int]]:
    """
    Sync stats cho một batch các posts (OPTIMIZED).
    Sử dụng aggregation để giảm số lượng queries.
    
    Args:
        post_ids: List các post ID cần sync
        mongo_client: MongoDB client instance
        
    Returns:
        Dict mapping post_id -> {likes_count, comments_count}
    """
    if not post_ids:
        return {}
    
    results = {}
    
    try:
        # Aggregation để đếm likes cho tất cả posts
        likes_pipeline = [
            {"$match": {"post_id": {"$in": post_ids}}},
            {"$group": {"_id": "$post_id", "count": {"$sum": 1}}}
        ]
        likes_results = await mongo_client.aggregate("post_likes", likes_pipeline)
        likes_map = {doc["_id"]: doc["count"] for doc in likes_results}
        
        # Aggregation để đếm comments cho tất cả posts
        comments_pipeline = [
            {"$match": {"post_id": {"$in": post_ids}}},
            {"$group": {"_id": "$post_id", "count": {"$sum": 1}}}
        ]
        comments_results = await mongo_client.aggregate("post_comments", comments_pipeline)
        comments_map = {doc["_id"]: doc["count"] for doc in comments_results}
        
        # Build results và update từng post
        for post_id in post_ids:
            likes_count = likes_map.get(post_id, 0)
            comments_count = comments_map.get(post_id, 0)
            
            results[post_id] = {
                "likes_count": likes_count,
                "comments_count": comments_count
            }
            
            # Update post document
            post_query, post = await _get_post_query(post_id, mongo_client)
            
            if post:
                # Chỉ update nếu giá trị khác
                current_likes = post.get("likes_count", 0)
                current_comments = post.get("comments_count", 0)
                
                if current_likes != likes_count or current_comments != comments_count:
                    await mongo_client.update_one("posts", post_query, {
                        "likes_count": likes_count,
                        "comments_count": comments_count
                    })
        
        logger.info(f"[POST_STATS] Batch synced {len(post_ids)} posts")
        
    except Exception as e:
        logger.error(f"[POST_STATS] Batch sync error: {e}")
        import traceback
        logger.error(f"[POST_STATS] Traceback: {traceback.format_exc()}")
    
    return results


# ==================== REAL-TIME UPDATE HANDLERS ====================

async def on_like_toggled(
    post_id: str,
    liked: bool,
    total_likes: int,
    mongo_client
) -> bool:
    """
    Handler được gọi khi like được toggle.
    Cập nhật likes_count ngay lập tức vào MongoDB.
    
    Args:
        post_id: ID của post
        liked: True nếu vừa like, False nếu vừa unlike
        total_likes: Số likes mới
        mongo_client: MongoDB client instance
        
    Returns:
        bool: True nếu cập nhật thành công
    """
    try:
        post_query, post = await _get_post_query(post_id, mongo_client)
        
        if not post:
            logger.warning(f"[POST_STATS] Post {post_id} not found for like update")
            return False
        
        await mongo_client.update_one("posts", post_query, {
            "likes_count": total_likes
        })
        
        logger.info(f"[POST_STATS] Updated likes_count for post {post_id}: {total_likes}")
        return True
        
    except Exception as e:
        logger.error(f"[POST_STATS] Error updating likes for post {post_id}: {e}")
        return False


async def on_comment_added(
    post_id: str,
    mongo_client
) -> bool:
    """
    Handler được gọi khi comment mới được thêm.
    Tăng comments_count lên 1 hoặc sync lại từ database.
    
    Args:
        post_id: ID của post
        mongo_client: MongoDB client instance
        
    Returns:
        bool: True nếu cập nhật thành công
    """
    try:
        # Đếm lại từ database để đảm bảo chính xác
        comments_count = await mongo_client.count("post_comments", {"post_id": post_id})
        
        post_query, post = await _get_post_query(post_id, mongo_client)
        
        if not post:
            logger.warning(f"[POST_STATS] Post {post_id} not found for comment update")
            return False
        
        await mongo_client.update_one("posts", post_query, {
            "comments_count": comments_count
        })
        
        logger.info(f"[POST_STATS] Updated comments_count for post {post_id}: {comments_count}")
        return True
        
    except Exception as e:
        logger.error(f"[POST_STATS] Error updating comments for post {post_id}: {e}")
        return False


async def on_comment_deleted(
    post_id: str,
    mongo_client
) -> bool:
    """
    Handler được gọi khi comment bị xóa.
    Sync lại comments_count từ database.
    
    Args:
        post_id: ID của post
        mongo_client: MongoDB client instance
        
    Returns:
        bool: True nếu cập nhật thành công
    """
    try:
        # Đếm lại từ database để đảm bảo chính xác
        comments_count = await mongo_client.count("post_comments", {"post_id": post_id})
        
        post_query, post = await _get_post_query(post_id, mongo_client)
        
        if not post:
            logger.warning(f"[POST_STATS] Post {post_id} not found for comment delete update")
            return False
        
        await mongo_client.update_one("posts", post_query, {
            "comments_count": comments_count
        })
        
        logger.info(f"[POST_STATS] Updated comments_count after delete for post {post_id}: {comments_count}")
        return True
        
    except Exception as e:
        logger.error(f"[POST_STATS] Error updating comments after delete for post {post_id}: {e}")
        return False


async def sync_all_posts_stats(
    mongo_client
) -> Dict[str, Any]:
    """
    Đồng bộ stats cho TẤT CẢ posts trong database.
    Dùng cho admin batch sync.
    
    Args:
        mongo_client: MongoDB client instance
        
    Returns:
        Dict với thống kê kết quả sync
    """
    try:
        # Lấy tất cả post IDs
        all_posts = await mongo_client.find_many("posts", {})
        post_ids = [str(post.get("_id")) for post in all_posts]
        
        logger.info(f"[POST_STATS] Starting batch sync for {len(post_ids)} posts")
        
        # Sync batch
        results = await sync_posts_stats_batch(post_ids, mongo_client)
        
        summary = {
            "total_posts": len(post_ids),
            "synced_count": len(results),
            "success": True
        }
        
        logger.info(f"[POST_STATS] Batch sync completed: {summary}")
        return summary
        
    except Exception as e:
        logger.error(f"[POST_STATS] Batch sync all failed: {e}")
        return {
            "total_posts": 0,
            "synced_count": 0,
            "success": False,
            "error": str(e)
        }
