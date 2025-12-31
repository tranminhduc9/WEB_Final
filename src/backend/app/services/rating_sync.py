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
    Tính toán rating và review count cho một place từ posts trong MongoDB.
    
    Logic:
    - review_count = đếm TẤT CẢ posts approved (bao gồm cả posts không có rating)
    - rating_average = trung bình của những posts CÓ rating
    - rating_count = số posts có rating (để tính average)
    
    Args:
        place_id: ID của place trong PostgreSQL
        mongo_client: MongoDB client instance
        
    Returns:
        Dict với rating_average, rating_count, rating_total, review_count
    """
    try:
        # Query 1: Đếm TẤT CẢ posts approved cho place này (review_count)
        all_posts = await mongo_client.find_many(
            "posts",
            {
                "$or": [
                    {"related_place_id": place_id},
                    {"related_place_id": str(place_id)}
                ],
                "status": "approved"
            }
        )
        review_count = len(all_posts) if all_posts else 0
        
        # Query 2: Lấy posts CÓ rating để tính trung bình
        posts_with_rating = await mongo_client.find_many(
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
        
        # Tính toán rating từ những posts có rating
        ratings = []
        for post in posts_with_rating:
            rating = post.get("rating")
            if rating is not None:
                try:
                    rating_val = float(rating)
                    # Validate range (bao gồm cả 0)
                    if 0 <= rating_val <= 5:
                        ratings.append(rating_val)
                except (TypeError, ValueError):
                    continue
        
        rating_count = len(ratings)
        rating_total = sum(ratings)
        rating_average = round(rating_total / rating_count, 2) if rating_count > 0 else 0.0
        
        logger.info(f"[RATING_SYNC] place_id={place_id}: review_count={review_count}, rating_count={rating_count}, avg={rating_average}")
        
        return {
            "rating_average": rating_average,
            "rating_count": rating_count,  # Số posts có rating
            "rating_total": rating_total,
            "review_count": review_count   # Tổng số posts (bao gồm cả không có rating)
        }
        
    except Exception as e:
        logger.error(f"[RATING_SYNC] Error calculating rating for place {place_id}: {e}")
        return {
            "rating_average": 0.0,
            "rating_count": 0,
            "rating_total": 0.0,
            "review_count": 0
        }



async def sync_places_ratings_batch(
    place_ids: List[int],
    db: Session,
    mongo_client
) -> Dict[int, Dict[str, Any]]:
    """
    Sync ratings cho một list các place IDs (OPTIMIZED).
    Sử dụng một aggregation query duy nhất thay vì query từng place.
    
    - rating_count = tổng số posts (= review_count)
    - rating_average = trung bình của những posts có rating
    
    Args:
        place_ids: List các place ID cần sync
        db: PostgreSQL session
        mongo_client: MongoDB client instance
        
    Returns:
        Dict mapping place_id -> rating_data
    """
    if not place_ids:
        return {}
    
    results = {}
    
    try:
        # Convert place_ids to include both int and string versions
        place_id_conditions = []
        for pid in place_ids:
            place_id_conditions.append(pid)
            place_id_conditions.append(str(pid))
        
        # Single aggregation query for ALL places
        pipeline = [
            {
                "$match": {
                    "related_place_id": {"$in": place_id_conditions},
                    "status": "approved"
                }
            },
            {
                "$group": {
                    "_id": "$related_place_id",
                    "review_count": {"$sum": 1},
                    "ratings": {
                        "$push": {
                            "$cond": [
                                {"$and": [
                                    {"$ne": ["$rating", None]},
                                    {"$gte": ["$rating", 0]},
                                    {"$lte": ["$rating", 5]}
                                ]},
                                "$rating",
                                "$$REMOVE"
                            ]
                        }
                    }
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "review_count": 1,
                    "rating_total": {"$sum": "$ratings"},
                    "rating_count_for_avg": {"$size": "$ratings"},
                    "rating_average": {
                        "$cond": [
                            {"$gt": [{"$size": "$ratings"}, 0]},
                            {"$round": [{"$divide": [{"$sum": "$ratings"}, {"$size": "$ratings"}]}, 2]},
                            0
                        ]
                    }
                }
            }
        ]
        
        # Execute aggregation
        aggregation_results = await mongo_client.aggregate("posts", pipeline)
        
        # Process results
        place_data_map = {}
        for doc in aggregation_results:
            place_id = doc["_id"]
            # Convert string place_id to int
            if isinstance(place_id, str):
                try:
                    place_id = int(place_id)
                except ValueError:
                    continue
            
            place_data_map[place_id] = {
                "rating_average": doc.get("rating_average", 0.0),
                "review_count": doc.get("review_count", 0),
                "rating_total": doc.get("rating_total", 0.0),
                "rating_count": doc.get("review_count", 0)  # For compatibility
            }
        
        # Build results for all requested place_ids
        for place_id in place_ids:
            if place_id in place_data_map:
                results[place_id] = place_data_map[place_id]
            else:
                # Place has no posts
                results[place_id] = {
                    "rating_average": 0.0,
                    "rating_count": 0,
                    "rating_total": 0.0,
                    "review_count": 0
                }
            
            # Update PostgreSQL
            try:
                rating_data = results[place_id]
                update_query = text("""
                    UPDATE places 
                    SET rating_average = :rating_average,
                        rating_count = :review_count,
                        rating_total = :rating_total,
                        updated_at = NOW()
                    WHERE id = :place_id
                """)
                
                db.execute(update_query, {
                    "place_id": place_id,
                    "rating_average": rating_data["rating_average"],
                    "review_count": rating_data["review_count"],
                    "rating_total": rating_data["rating_total"]
                })
            except Exception as e:
                logger.warning(f"[RATING_SYNC] Failed to update place {place_id}: {e}")
        
        db.commit()
        logger.info(f"[RATING_SYNC] Batch synced {len(place_ids)} places (optimized)")
        
    except Exception as e:
        logger.error(f"[RATING_SYNC] Batch sync error: {e}")
        db.rollback()
    
    return results


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
    Đồng bộ rating cho TẤT CẢ places trong database.
    - Places có posts sẽ được tính rating từ MongoDB
    - Places không có posts sẽ được reset về 0
    
    Logic tính toán:
    - rating_count = tổng số posts approved (bao gồm cả posts không có rating)
    - rating_average = trung bình của những posts CÓ rating
    
    Args:
        db: PostgreSQL session
        mongo_client: MongoDB client instance
        
    Returns:
        Dict với thống kê kết quả sync
    """
    try:
        from config.database import Place
        
        # Lấy tất cả place IDs từ PostgreSQL
        all_places = db.query(Place.id).filter(Place.deleted_at == None).all()
        all_place_ids = set(p.id for p in all_places)
        logger.info(f"[RATING_SYNC] Total places in database: {len(all_place_ids)}")
        
        # Query 1: Lấy TẤT CẢ posts approved (để đếm review_count)
        all_approved_posts = await mongo_client.find_many(
            "posts",
            {"status": "approved"}
        )
        
        logger.info(f"[RATING_SYNC] Found {len(all_approved_posts)} total approved posts")
        
        # Group TẤT CẢ posts by place_id (để đếm review_count)
        place_review_counts: Dict[int, int] = {}
        place_ratings: Dict[int, List[float]] = {}
        
        for post in all_approved_posts:
            place_id = post.get("related_place_id")
            
            # Skip nếu không có place_id
            if not place_id:
                continue
            
            # Convert place_id to int
            if isinstance(place_id, str):
                try:
                    place_id = int(place_id)
                except ValueError:
                    continue
            
            # Đếm review_count (tất cả posts)
            place_review_counts[place_id] = place_review_counts.get(place_id, 0) + 1
            
            # Thu thập ratings (chỉ từ posts có rating)
            rating = post.get("rating")
            if rating is not None:
                try:
                    rating_val = float(rating)
                    if 0 <= rating_val <= 5:
                        if place_id not in place_ratings:
                            place_ratings[place_id] = []
                        place_ratings[place_id].append(rating_val)
                except (TypeError, ValueError):
                    pass
        
        logger.info(f"[RATING_SYNC] Found reviews for {len(place_review_counts)} places")
        logger.info(f"[RATING_SYNC] Found ratings for {len(place_ratings)} places")
        
        updated_count = 0
        reset_count = 0
        failed_count = 0
        
        # Cập nhật places có reviews
        for place_id, review_count in place_review_counts.items():
            # Tính rating_average chỉ từ posts có rating
            ratings = place_ratings.get(place_id, [])
            rating_total = sum(ratings)
            rating_average = round(rating_total / len(ratings), 2) if ratings else 0.0
            
            # Cập nhật PostgreSQL - rating_count = review_count (tổng số posts)
            try:
                update_query = text("""
                    UPDATE places 
                    SET rating_average = :rating_average,
                        rating_count = :review_count,
                        rating_total = :rating_total,
                        updated_at = NOW()
                    WHERE id = :place_id
                """)
                
                result = db.execute(update_query, {
                    "place_id": place_id,
                    "rating_average": rating_average,
                    "review_count": review_count,  # Tổng số posts
                    "rating_total": rating_total
                })
                
                if result.rowcount > 0:
                    updated_count += 1
                    logger.info(f"[RATING_SYNC] Updated place {place_id}: avg={rating_average}, review_count={review_count}")
                else:
                    logger.warning(f"[RATING_SYNC] Place {place_id} not found in database")
                    failed_count += 1
                
            except Exception as e:
                logger.error(f"[RATING_SYNC] Failed to update place {place_id}: {e}")
                failed_count += 1
        
        # Reset places không có reviews
        places_with_reviews = set(place_review_counts.keys())
        places_without_reviews = all_place_ids - places_with_reviews
        
        if places_without_reviews:
            logger.info(f"[RATING_SYNC] Resetting {len(places_without_reviews)} places without reviews")
            for place_id in places_without_reviews:
                try:
                    reset_query = text("""
                        UPDATE places 
                        SET rating_average = 0,
                            rating_count = 0,
                            rating_total = 0,
                            updated_at = NOW()
                        WHERE id = :place_id
                    """)
                    
                    result = db.execute(reset_query, {"place_id": place_id})
                    if result.rowcount > 0:
                        reset_count += 1
                except Exception as e:
                    logger.warning(f"[RATING_SYNC] Failed to reset place {place_id}: {e}")
        
        db.commit()
        
        summary = {
            "total_places": len(all_place_ids),
            "total_posts": len(all_approved_posts),
            "places_with_reviews": len(place_review_counts),
            "places_without_reviews": len(places_without_reviews),
            "updated_count": updated_count,
            "reset_count": reset_count,
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
    
    # Chỉ skip nếu không có related_place_id HOẶC rating là None
    # BAO GỒM CẢ rating = 0 trong tính toán
    if not related_place_id or rating is None:
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
