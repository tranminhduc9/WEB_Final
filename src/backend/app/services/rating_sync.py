"""
Rating Sync Service

Module này đồng bộ rating từ MongoDB posts sang PostgreSQL places.
Tự động cập nhật rating_average và rating_count khi:
- Post mới được tạo với rating (và có related_place_id)
- Post được approve/reject
- Admin chạy batch sync

Author: System
Date: 2024-12-30
"""

import logging
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)


async def calculate_place_rating_from_mongodb(
    place_id: int,
    mongo_client
) -> Dict[str, Any]:
    """
    Tính toán rating cho một place từ tất cả posts trong MongoDB.
    Bao gồm cả posts có rating = 0 trong tính toán trung bình.
    
    Args:
        place_id: ID của place trong PostgreSQL
        mongo_client: MongoDB client instance
        
    Returns:
        Dict với rating_average, rating_count, rating_total
    """
    try:
        # Query tất cả posts có related_place_id = place_id và có rating (bao gồm cả 0)
        # Chỉ tính các posts đã approved
        posts = await mongo_client.find_many(
            "posts",
            {
                "$or": [
                    {"related_place_id": place_id},
                    {"related_place_id": str(place_id)}
                ],
                "status": "approved",
                "rating": {"$exists": True, "$ne": None}
            }
        )
        
        if not posts:
            return {
                "rating_average": 0.0,
                "rating_count": 0,
                "rating_total": 0.0
            }
        
        # Tính toán rating - BAO GỒM CẢ rating = 0
        ratings = []
        for post in posts:
            rating = post.get("rating")
            if rating is not None:
                try:
                    rating_val = float(rating)
                    # Validate range nhưng KHÔNG loại bỏ rating = 0
                    if 0 <= rating_val <= 5:
                        ratings.append(rating_val)
                except (TypeError, ValueError):
                    continue
        
        if not ratings:
            return {
                "rating_average": 0.0,
                "rating_count": 0,
                "rating_total": 0.0
            }
        
        rating_count = len(ratings)
        rating_total = sum(ratings)
        rating_average = round(rating_total / rating_count, 2) if rating_count > 0 else 0.0
        
        logger.info(f"[RATING_SYNC] place_id={place_id}: count={rating_count}, total={rating_total}, avg={rating_average}")
        
        return {
            "rating_average": rating_average,
            "rating_count": rating_count,
            "rating_total": rating_total
        }
        
    except Exception as e:
        logger.error(f"[RATING_SYNC] Error calculating rating for place {place_id}: {e}")
        return {
            "rating_average": 0.0,
            "rating_count": 0,
            "rating_total": 0.0
        }


async def update_place_rating(
    place_id: int,
    db: Session,
    mongo_client
) -> bool:
    """
    Cập nhật rating cho một place trong PostgreSQL từ MongoDB.
    
    Args:
        place_id: ID của place
        db: PostgreSQL session
        mongo_client: MongoDB client instance
        
    Returns:
        bool: True nếu cập nhật thành công
    """
    try:
        # Tính toán rating từ MongoDB
        rating_data = await calculate_place_rating_from_mongodb(place_id, mongo_client)
        
        # Cập nhật PostgreSQL
        update_query = text("""
            UPDATE places 
            SET rating_average = :rating_average,
                rating_count = :rating_count,
                rating_total = :rating_total,
                updated_at = NOW()
            WHERE id = :place_id
        """)
        
        db.execute(update_query, {
            "place_id": place_id,
            "rating_average": rating_data["rating_average"],
            "rating_count": rating_data["rating_count"],
            "rating_total": rating_data["rating_total"]
        })
        db.commit()
        
        logger.info(f"[RATING_SYNC] Updated place {place_id}: avg={rating_data['rating_average']}, count={rating_data['rating_count']}")
        return True
        
    except Exception as e:
        db.rollback()
        logger.error(f"[RATING_SYNC] Error updating place {place_id} rating: {e}")
        return False


async def sync_all_place_ratings(
    db: Session,
    mongo_client
) -> Dict[str, Any]:
    """
    Đồng bộ rating cho TẤT CẢ places có posts trong MongoDB.
    Chạy như batch job.
    
    Logic tính toán:
    - rating_count = số posts approved có rating (bao gồm cả rating = 0)
    - rating_average = trung bình cộng của TẤT CẢ ratings (bao gồm cả 0)
    
    Args:
        db: PostgreSQL session
        mongo_client: MongoDB client instance
        
    Returns:
        Dict với thống kê kết quả sync
    """
    try:
        # Lấy tất cả posts approved có rating (bao gồm cả rating = 0)
        all_posts = await mongo_client.find_many(
            "posts",
            {
                "status": "approved",
                "rating": {"$exists": True, "$ne": None}
            }
        )
        
        logger.info(f"[RATING_SYNC] Found {len(all_posts)} approved posts with rating")
        
        # Group posts by place_id và tính rating
        place_ratings: Dict[int, List[float]] = {}
        
        for post in all_posts:
            place_id = post.get("related_place_id")
            rating = post.get("rating")
            
            # Skip nếu không có place_id
            if not place_id:
                continue
            
            # Convert rating to float và validate (bao gồm cả 0)
            try:
                rating = float(rating)
                # Chỉ validate range, KHÔNG loại bỏ rating = 0
                if rating < 0 or rating > 5:
                    continue
            except (TypeError, ValueError):
                continue
            
            # Convert place_id to int
            if isinstance(place_id, str):
                try:
                    place_id = int(place_id)
                except ValueError:
                    logger.warning(f"[RATING_SYNC] Invalid place_id: {place_id}")
                    continue
            
            if place_id not in place_ratings:
                place_ratings[place_id] = []
            place_ratings[place_id].append(rating)
        
        logger.info(f"[RATING_SYNC] Found ratings for {len(place_ratings)} places")
        
        updated_count = 0
        failed_count = 0
        
        for place_id, ratings in place_ratings.items():
            # Tính rating_average = trung bình cộng (bao gồm cả rating = 0)
            rating_count = len(ratings)
            rating_total = sum(ratings)
            rating_average = round(rating_total / rating_count, 2) if rating_count > 0 else 0.0
            
            # Cập nhật PostgreSQL
            try:
                update_query = text("""
                    UPDATE places 
                    SET rating_average = :rating_average,
                        rating_count = :rating_count,
                        rating_total = :rating_total,
                        updated_at = NOW()
                    WHERE id = :place_id
                """)
                
                result = db.execute(update_query, {
                    "place_id": place_id,
                    "rating_average": rating_average,
                    "rating_count": rating_count,
                    "rating_total": rating_total
                })
                
                if result.rowcount > 0:
                    updated_count += 1
                    logger.info(f"[RATING_SYNC] Updated place {place_id}: avg={rating_average}, count={rating_count}")
                else:
                    logger.warning(f"[RATING_SYNC] Place {place_id} not found in database")
                    failed_count += 1
                
            except Exception as e:
                logger.error(f"[RATING_SYNC] Failed to update place {place_id}: {e}")
                failed_count += 1
        
        db.commit()
        
        summary = {
            "total_posts_with_rating": len(all_posts),
            "total_places_with_reviews": len(place_ratings),
            "updated_count": updated_count,
            "failed_count": failed_count
        }
        
        logger.info(f"[RATING_SYNC] Batch sync completed: {summary}")
        return summary
        
    except Exception as e:
        db.rollback()
        logger.error(f"[RATING_SYNC] Batch sync failed: {e}")
        import traceback
        logger.error(f"[RATING_SYNC] Traceback: {traceback.format_exc()}")
        return {
            "error": str(e),
            "total_places_with_reviews": 0,
            "updated_count": 0,
            "failed_count": 0
        }


async def on_post_approved(
    post: Dict[str, Any],
    db: Session,
    mongo_client
) -> bool:
    """
    Handler được gọi khi post được approve.
    Cập nhật rating của place liên quan.
    
    Args:
        post: Post document từ MongoDB
        db: PostgreSQL session
        mongo_client: MongoDB client instance
        
    Returns:
        bool: True nếu cập nhật thành công
    """
    related_place_id = post.get("related_place_id")
    rating = post.get("rating")
    
    if not related_place_id or not rating or rating <= 0:
        logger.debug(f"[RATING_SYNC] Post has no related_place_id or rating, skipping")
        return True
    
    # Convert to int nếu là string
    if isinstance(related_place_id, str):
        try:
            related_place_id = int(related_place_id)
        except ValueError:
            logger.warning(f"[RATING_SYNC] Invalid related_place_id: {related_place_id}")
            return False
    
    return await update_place_rating(related_place_id, db, mongo_client)


async def on_post_rejected_or_deleted(
    post: Dict[str, Any],
    db: Session,
    mongo_client
) -> bool:
    """
    Handler được gọi khi post bị reject hoặc xóa.
    Recalculate rating của place liên quan.
    
    Args:
        post: Post document từ MongoDB
        db: PostgreSQL session
        mongo_client: MongoDB client instance
        
    Returns:
        bool: True nếu cập nhật thành công
    """
    related_place_id = post.get("related_place_id")
    
    if not related_place_id:
        return True
    
    # Convert to int nếu là string
    if isinstance(related_place_id, str):
        try:
            related_place_id = int(related_place_id)
        except ValueError:
            return False
    
    return await update_place_rating(related_place_id, db, mongo_client)
