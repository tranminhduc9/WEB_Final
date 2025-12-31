"""
Places API Routes

Module này định nghĩa các API endpoints cho Places bao gồm:
- GET /places - Lấy danh sách địa điểm nổi bật (homepage)
- GET /places/search - Tìm kiếm địa điểm
- GET /places/suggest - Gợi ý tìm kiếm (autocomplete)
- GET /places/nearby - Địa điểm lân cận
- GET /places/districts - Danh sách quận/huyện
- GET /places/place-types - Danh sách loại địa điểm
- GET /places/{id} - Chi tiết địa điểm
- POST /places/{id}/favorite - Toggle yêu thích

Database Schema v3.1 Compatible
"""

import logging
import math
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import text
from sqlalchemy.orm import Session

from config.database import (
    get_db, Place, PlaceImage, PlaceType, District, UserPlaceFavorite,
    Restaurant, Hotel, TouristAttraction, VisitLog
)
from app.utils.image_helpers import get_main_image_url, get_all_place_images, normalize_image_list
from app.utils.place_helpers import get_user_compact
from middleware.auth import get_current_user, get_optional_user
from middleware.response import (
    success_response,
    error_response,
    not_found_response,
    server_error_response
)
from app.services.logging_service import log_visit, log_activity

logger = logging.getLogger(__name__)

# Tạo router cho places endpoints
router = APIRouter(prefix="/places", tags=["Places"])


# ==================== HELPER FUNCTIONS ====================

def get_place_type_name(place_type_id: int, db: Session) -> str:
    """Lấy tên loại địa điểm từ ID"""
    place_type = db.query(PlaceType).filter(PlaceType.id == place_type_id).first()
    if place_type:
        return place_type.name
    # Fallback mapping
    type_mapping = {1: "Du lịch", 2: "Khách sạn", 3: "Nhà hàng"}
    return type_mapping.get(place_type_id, "Khác")



def paginate_query(page: int, limit: int, total_items: int):
    """Helper function cho phân trang"""
    total_pages = math.ceil(total_items / limit) if total_items > 0 else 1
    offset = (page - 1) * limit
    
    pagination = {
        "page": page,
        "limit": limit,
        "total_items": total_items,
        "total_pages": total_pages
    }
    
    return offset, pagination


def place_row_to_compact(row, db: Session = None) -> Dict[str, Any]:
    """
    Chuyển đổi row từ database sang compact format theo Swagger PlaceCompact schema.
    
    Extended fields for frontend display:
    - id, name, district_id, district_name, address, place_type_id
    - rating_average, price_min, price_max, main_image_url, favorites_count
    """
    from config.database import UserPlaceFavorite
    
    place_id = row.id
    rating_average = float(row.rating_average) if row.rating_average else 0.0
    price_min = float(row.price_min) if row.price_min else 0
    price_max = float(row.price_max) if row.price_max else 0
    
    # Auto-swap nếu giá trị bị đảo ngược trong database
    # Swap khi price_min > price_max (dữ liệu bị lưu ngược)
    if price_min > price_max:
        price_min, price_max = price_max, price_min
    
    # Lấy ảnh từ database hoặc local uploads
    image_url = get_main_image_url(place_id, db)
    
    # Get district_name from row (requires LEFT JOIN in query)
    district_name = getattr(row, 'district_name', None) or f"Quận {row.district_id}"
    address = getattr(row, 'address_detail', None) or f"Quận {district_name}, Hà Nội"
    
    # Safely get rating_count using getattr (may not exist in all query results)
    rating_count = getattr(row, 'rating_count', 0) or 0
    
    # Get favorites_count
    favorites_count = 0
    if db is not None:
        try:
            favorites_count = db.query(UserPlaceFavorite).filter(
                UserPlaceFavorite.place_id == place_id
            ).count()
        except Exception:
            favorites_count = 0
    
    # Debug log for rating_count issue
    logger.debug(f"[PLACES] place_row_to_compact - place_id={place_id}, rating_count={rating_count}")
    
    return {
        "id": place_id,
        "name": row.name,
        "district_id": row.district_id,
        "district_name": district_name,
        "address": address,
        "place_type_id": row.place_type_id,
        "rating_average": rating_average,
        "rating_count": rating_count,
        "price_min": price_min,
        "price_max": price_max,
        "main_image_url": image_url,
        "favorites_count": favorites_count
    }


def place_row_to_horizontal(row, db: Session = None, user_lat: float = None, user_long: float = None) -> Dict[str, Any]:
    """
    Chuyển đổi row sang horizontal format - trả về PlaceCompact với district_name.
    Nearby places endpoint vẫn trả về PlaceCompact format kèm distance và favorites_count.
    """
    from config.database import UserPlaceFavorite
    
    place_id = row.id
    rating_average = float(row.rating_average) if row.rating_average else 0.0
    price_min = float(row.price_min) if row.price_min else 0
    price_max = float(row.price_max) if row.price_max else 0
    
    # Auto-swap nếu giá trị bị đảo ngược trong database
    # Swap khi price_min > price_max (dữ liệu bị lưu ngược)
    if price_min > price_max:
        price_min, price_max = price_max, price_min
    
    # Lấy ảnh
    image_url = get_main_image_url(place_id, db)
    
    # Get district_name from row (requires LEFT JOIN in query)
    district_name = getattr(row, 'district_name', None) or f"Quận {row.district_id}"
    address = getattr(row, 'address_detail', None) or f"Quận {district_name}, Hà Nội"
    
    # Safely get rating_count using getattr
    rating_count = getattr(row, 'rating_count', 0) or 0
    
    # Get distance from query result if available (distance_km column)
    distance_km = getattr(row, 'distance_km', None)
    distance_str = None
    if distance_km is not None:
        if distance_km < 1:
            distance_str = f"{int(distance_km * 1000)}m"
        else:
            distance_str = f"{distance_km:.1f}km"
    
    # Get favorites_count
    favorites_count = 0
    if db is not None:
        try:
            favorites_count = db.query(UserPlaceFavorite).filter(
                UserPlaceFavorite.place_id == place_id
            ).count()
        except Exception:
            favorites_count = 0
    
    # Trả về PlaceCompact format với district_name, distance và favorites_count
    return {
        "id": place_id,
        "name": row.name,
        "district_id": row.district_id,
        "district_name": district_name,
        "address": address,
        "place_type_id": row.place_type_id,
        "rating_average": rating_average,
        "rating_count": rating_count,
        "price_min": price_min,
        "price_max": price_max,
        "main_image_url": image_url,
        "distance": distance_str,
        "favorites_count": favorites_count
    }


# ==================== ENDPOINTS ====================

@router.get("", summary="Get Places with Filters")
async def get_places(
    request: Request,
    page: int = Query(1, ge=1, description="Số trang"),
    limit: int = Query(10, ge=1, le=50, description="Số lượng mỗi trang"),
    district_id: Optional[int] = Query(None, description="ID quận/huyện"),
    place_type_id: Optional[int] = Query(None, description="ID loại địa điểm"),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách địa điểm với bộ lọc
    - Nếu không có filter: trả về places có rating_average >= 4.0 (outstanding)
    - Nếu có filter: trả về tất cả places match với filter
    """
    try:
        # Build dynamic WHERE clause
        conditions = ["p.deleted_at IS NULL"]
        params = {"limit": limit}
        
        # Nếu có filter, không giới hạn rating
        if district_id:
            conditions.append("p.district_id = :district_id")
            params["district_id"] = district_id
        
        if place_type_id:
            conditions.append("p.place_type_id = :place_type_id")
            params["place_type_id"] = place_type_id
        
        # Nếu không có filter nào, chỉ lấy outstanding places
        if not district_id and not place_type_id:
            conditions.append("p.rating_average >= 4.0")
        
        where_clause = " AND ".join(conditions)
        
        # Count total
        count_query = text(f"""
            SELECT COUNT(*) as total 
            FROM places p
            WHERE {where_clause}
        """)
        count_result = db.execute(count_query, params).fetchone()
        total_items = count_result.total if count_result else 0
        
        offset, pagination = paginate_query(page, limit, total_items)
        params["offset"] = offset
        
        # Lấy places với district name
        query = text(f"""
            SELECT p.*, d.name as district_name
            FROM places p
            LEFT JOIN districts d ON p.district_id = d.id
            WHERE {where_clause}
            ORDER BY p.rating_average DESC, p.name ASC
            LIMIT :limit OFFSET :offset
        """)
        
        result = db.execute(query, params).fetchall()
        
        # Batch sync ratings from MongoDB for all places on screen (optimized - single query)
        place_ids = [row.id for row in result]
        synced_ratings = {}
        if place_ids:
            try:
                from middleware.mongodb_client import mongo_client, get_mongodb
                from app.services.rating_sync import sync_places_ratings_batch
                await get_mongodb()
                synced_ratings = await sync_places_ratings_batch(place_ids, db, mongo_client)
            except Exception as sync_error:
                logger.warning(f"[PLACES] Rating sync failed: {sync_error}")
        
        # Build data using synced ratings (no re-query needed)
        data = []
        for row in result:
            place_data = place_row_to_compact(row, db)
            # Override with synced values if available
            if row.id in synced_ratings:
                place_data["rating_average"] = synced_ratings[row.id].get("rating_average", place_data["rating_average"])
                place_data["rating_count"] = synced_ratings[row.id].get("review_count", place_data["rating_count"])
            data.append(place_data)
        
        filter_info = []
        if district_id:
            filter_info.append(f"district_id={district_id}")
        if place_type_id:
            filter_info.append(f"place_type_id={place_type_id}")
        filter_str = ", ".join(filter_info) if filter_info else "outstanding only"
        
        logger.info(f"[PLACES] Get places - {filter_str}, found {len(data)} places (page {page})")
        
        return {
            "success": True,
            "data": data,
            "pagination": pagination,
            "message": f"Tìm thấy {total_items} địa điểm"
        }
        
    except Exception as e:
        logger.error(f"[PLACES] Error getting places: {str(e)}")
        return server_error_response()


@router.get("/search", summary="Search Places")
async def search_places(
    request: Request,
    keyword: Optional[str] = Query(None, description="Từ khóa tìm kiếm"),
    district_id: Optional[int] = Query(None, description="ID quận/huyện"),
    place_type_id: Optional[int] = Query(None, description="ID loại địa điểm"),
    page: int = Query(1, ge=1, description="Số trang"),
    limit: int = Query(10, ge=1, le=50, description="Số lượng mỗi trang"),
    db: Session = Depends(get_db)
):
    """
    Tìm kiếm địa điểm với các bộ lọc
    """
    try:
        # Build dynamic WHERE clause
        conditions = ["p.deleted_at IS NULL"]
        params = {"limit": limit}
        
        if keyword:
            conditions.append("(LOWER(p.name) LIKE LOWER(:keyword) OR LOWER(p.description) LIKE LOWER(:keyword))")
            params["keyword"] = f"%{keyword}%"
        
        if district_id:
            conditions.append("p.district_id = :district_id")
            params["district_id"] = district_id
        
        if place_type_id:
            conditions.append("p.place_type_id = :place_type_id")
            params["place_type_id"] = place_type_id
        
        where_clause = " AND ".join(conditions)
        
        # Count total
        count_query = text(f"""
            SELECT COUNT(*) as total 
            FROM places p
            WHERE {where_clause}
        """)
        count_result = db.execute(count_query, params).fetchone()
        total_items = count_result.total if count_result else 0
        
        offset, pagination = paginate_query(page, limit, total_items)
        params["offset"] = offset
        
        # Get places
        query = text(f"""
            SELECT p.*, d.name as district_name
            FROM places p
            LEFT JOIN districts d ON p.district_id = d.id
            WHERE {where_clause}
            ORDER BY p.rating_average DESC, p.name ASC
            LIMIT :limit OFFSET :offset
        """)
        
        result = db.execute(query, params).fetchall()
        
        # Batch sync ratings from MongoDB for all places on screen
        place_ids = [row.id for row in result]
        synced_ratings = {}
        if place_ids:
            try:
                from middleware.mongodb_client import mongo_client, get_mongodb
                from app.services.rating_sync import sync_places_ratings_batch
                await get_mongodb()
                synced_ratings = await sync_places_ratings_batch(place_ids, db, mongo_client)
            except Exception as sync_error:
                logger.warning(f"[PLACES] Rating sync failed: {sync_error}")
        
        # Build data using synced ratings (no re-query needed)
        data = []
        for row in result:
            place_data = place_row_to_compact(row, db)
            if row.id in synced_ratings:
                place_data["rating_average"] = synced_ratings[row.id].get("rating_average", place_data["rating_average"])
                place_data["rating_count"] = synced_ratings[row.id].get("review_count", place_data["rating_count"])
            data.append(place_data)
        
        logger.info(f"[PLACES] Search places - keyword='{keyword}', district_id={district_id}, found {len(data)} places")
        
        return {
            "success": True,
            "data": data,
            "pagination": pagination,
            "message": f"Tìm thấy {total_items} địa điểm"
        }
        
    except Exception as e:
        logger.error(f"[PLACES] Error searching places: {str(e)}")
        return server_error_response()


@router.get("/suggest", summary="Search Suggestions")
async def get_search_suggestions(
    request: Request,
    keyword: str = Query(..., min_length=1, description="Từ khóa gợi ý"),
    db: Session = Depends(get_db)
):
    """
    Gợi ý tìm kiếm (autocomplete)
    """
    try:
        # Tìm các địa điểm có tên match
        query = text("""
            SELECT DISTINCT name 
            FROM places 
            WHERE LOWER(name) LIKE LOWER(:keyword) AND deleted_at IS NULL
            ORDER BY name
            LIMIT 10
        """)
        
        result = db.execute(query, {"keyword": f"%{keyword}%"}).fetchall()
        suggestions = [row.name for row in result]
        
        # Thêm tên quận nếu match
        district_query = text("""
            SELECT name 
            FROM districts 
            WHERE LOWER(name) LIKE LOWER(:keyword)
            LIMIT 5
        """)
        district_result = db.execute(district_query, {"keyword": f"%{keyword}%"}).fetchall()
        for row in district_result:
            if row.name not in suggestions:
                suggestions.append(f"Quận {row.name}")
        
        logger.info(f"[PLACES] Suggestions for '{keyword}' - Found {len(suggestions)} suggestions")
        
        return {
            "success": True,
            "data": suggestions[:10]
        }
        
    except Exception as e:
        logger.error(f"[PLACES] Error getting suggestions: {str(e)}")
        return server_error_response()


@router.get("/nearby", summary="Get Nearby Places")
async def get_nearby_places(
    request: Request,
    lat: float = Query(..., description="Vĩ độ"),
    long: float = Query(..., description="Kinh độ"),
    radius: float = Query(5.0, description="Bán kính (km)"),
    limit: int = Query(10, ge=1, le=20, description="Số lượng"),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách địa điểm lân cận
    """
    try:
        # Validate coordinates
        if not (-90 <= lat <= 90) or not (-180 <= long <= 180):
            return error_response(
                message="Tọa độ không hợp lệ",
                error_code="INVALID_COORDINATES",
                status_code=400
            )
        
        # Tính bounding box đơn giản
        lat_range = radius / 111  # 1 degree ≈ 111km
        long_range = radius / (111 * math.cos(math.radians(lat)))
        
        query = text("""
            SELECT p.*, d.name as district_name,
                   SQRT(POWER((p.latitude - :lat) * 111, 2) + POWER((p.longitude - :long) * 111 * COS(RADIANS(:lat)), 2)) as distance_km
            FROM places p
            LEFT JOIN districts d ON p.district_id = d.id
            WHERE p.latitude BETWEEN :lat_min AND :lat_max
              AND p.longitude BETWEEN :long_min AND :long_max
              AND p.deleted_at IS NULL
            ORDER BY distance_km ASC
            LIMIT :limit
        """)
        
        result = db.execute(query, {
            "lat": lat,
            "long": long,
            "lat_min": lat - lat_range,
            "lat_max": lat + lat_range,
            "long_min": long - long_range,
            "long_max": long + long_range,
            "limit": limit
        }).fetchall()
        
        # Batch sync ratings from MongoDB for all places on screen
        place_ids = [row.id for row in result]
        synced_ratings = {}
        if place_ids:
            try:
                from middleware.mongodb_client import mongo_client, get_mongodb
                from app.services.rating_sync import sync_places_ratings_batch
                await get_mongodb()
                synced_ratings = await sync_places_ratings_batch(place_ids, db, mongo_client)
            except Exception as sync_error:
                logger.warning(f"[PLACES] Rating sync failed: {sync_error}")
        
        # Build data using synced ratings (no re-query needed)
        data = []
        for row in result:
            place_data = place_row_to_horizontal(row, db, lat, long)
            if row.id in synced_ratings:
                place_data["rating_average"] = synced_ratings[row.id].get("rating_average", place_data["rating_average"])
                place_data["rating_count"] = synced_ratings[row.id].get("review_count", place_data["rating_count"])
            data.append(place_data)
        
        logger.info(f"[PLACES] Nearby places at ({lat}, {long}) - Found {len(data)} places")
        
        return success_response(
            data=data,
            message=f"Tìm thấy {len(data)} địa điểm lân cận"
        )
        
    except Exception as e:
        logger.error(f"[PLACES] Error getting nearby places: {str(e)}")
        return server_error_response()


@router.get("/districts", summary="Get Districts")
async def get_districts(request: Request, db: Session = Depends(get_db)):
    """
    Lấy danh sách quận/huyện
    """
    try:
        query = text("SELECT id, name FROM districts ORDER BY name")
        result = db.execute(query).fetchall()
        
        data = [{"id": row.id, "name": row.name} for row in result]
        
        logger.info(f"[PLACES] Get districts - Found {len(data)} districts")
        
        return success_response(
            data=data,
            message="Lấy danh sách quận/huyện thành công"
        )
        
    except Exception as e:
        logger.error(f"[PLACES] Error getting districts: {str(e)}")
        return server_error_response()


@router.get("/place-types", summary="Get Place Types")
async def get_place_types(request: Request, db: Session = Depends(get_db)):
    """
    Lấy danh sách loại địa điểm từ database
    """
    try:
        query = text("SELECT id, name FROM place_types ORDER BY id")
        result = db.execute(query).fetchall()
        
        if result:
            data = [{"id": row.id, "name": row.name} for row in result]
        else:
            # Fallback nếu chưa có data
            data = [
                {"id": 1, "name": "Du lịch"},
                {"id": 2, "name": "Khách sạn"},
                {"id": 3, "name": "Nhà hàng"}
            ]
        
        logger.info(f"[PLACES] Get place types - Found {len(data)} types")
        
        return success_response(
            data=data,
            message="Lấy danh sách loại địa điểm thành công"
        )
        
    except Exception as e:
        logger.error(f"[PLACES] Error getting place types: {str(e)}")
        return server_error_response()


@router.get("/{place_id}", summary="Get Place Details")
async def get_place_detail(
    request: Request,
    place_id: int,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Lấy chi tiết địa điểm
    """
    try:
        # Tìm địa điểm
        query = text("""
            SELECT p.*, d.name as district_name, pt.name as place_type_name,
                   r.cuisine_type, r.avg_price_per_person,
                   h.star_rating, h.price_per_night, h.check_in_time, h.check_out_time,
                   t.ticket_price, t.is_ticket_required
            FROM places p
            LEFT JOIN districts d ON p.district_id = d.id
            LEFT JOIN place_types pt ON p.place_type_id = pt.id
            LEFT JOIN restaurants r ON p.id = r.place_id
            LEFT JOIN hotels h ON p.id = h.place_id
            LEFT JOIN tourist_attractions t ON p.id = t.place_id
            WHERE p.id = :place_id AND p.deleted_at IS NULL
        """)
        
        result = db.execute(query, {"place_id": place_id}).fetchone()
        
        if not result:
            return not_found_response("địa điểm")
        
        row = result
        latitude = float(row.latitude) if row.latitude else None
        longitude = float(row.longitude) if row.longitude else None
        rating = float(row.rating_average) if row.rating_average else 0.0
        rating_count = row.rating_count or 0
        
        # Lấy images - chỉ cần gọi helper function
        images = get_all_place_images(place_id, db)
        
        # Lấy nearby places
        nearby_places = []
        if latitude and longitude:
            nearby_query = text("""
                SELECT p.*, d.name as district_name,
                       SQRT(POWER((p.latitude - :lat) * 111, 2) + POWER((p.longitude - :long) * 111, 2)) as distance_km
                FROM places p
                LEFT JOIN districts d ON p.district_id = d.id
                WHERE p.id != :place_id
                  AND p.latitude IS NOT NULL
                  AND p.deleted_at IS NULL
                ORDER BY distance_km ASC
                LIMIT 5
            """)
            
            nearby_result = db.execute(nearby_query, {
                "lat": latitude,
                "long": longitude,
                "place_id": place_id
            }).fetchall()
            
            nearby_places = [place_row_to_horizontal(r, db, latitude, longitude) for r in nearby_result]
        
        # Check if favorited
        is_favorited = False
        if current_user:
            user_id = int(current_user.get("user_id", 0))
            fav_check = db.query(UserPlaceFavorite).filter(
                UserPlaceFavorite.user_id == user_id,
                UserPlaceFavorite.place_id == place_id
            ).first()
            is_favorited = fav_check is not None
        
        # Get favorites count
        favorites_count = db.query(UserPlaceFavorite).filter(
            UserPlaceFavorite.place_id == place_id
        ).count()
        
        # Build response data theo Swagger PlaceDetailResponse
        address = row.address_detail or (f"Quận {row.district_name}, Hà Nội" if row.district_name else "Hà Nội")
        
        # details object cho thông tin chi tiết theo Swagger
        details = {}
        if row.cuisine_type or row.avg_price_per_person:
            details["restaurant_info"] = {
                "cuisine_type": row.cuisine_type,
                "avg_price_per_person": float(row.avg_price_per_person) if row.avg_price_per_person else None
            }
        if row.star_rating or row.price_per_night:
            details["hotel_info"] = {
                "star_rating": row.star_rating,
                "price_per_night": float(row.price_per_night) if row.price_per_night else None,
                "check_in_time": str(row.check_in_time) if row.check_in_time else None,
                "check_out_time": str(row.check_out_time) if row.check_out_time else None
            }
        if row.ticket_price is not None:
            details["tourist_attraction_info"] = {
                "ticket_price": float(row.ticket_price) if row.ticket_price else 0,
                "is_ticket_required": row.is_ticket_required
            }
        
        # Get price values with auto-swap logic
        price_min = float(row.price_min) if row.price_min else 0
        price_max = float(row.price_max) if row.price_max else 0
        
        # Auto-swap nếu giá trị bị đảo ngược trong database
        if price_min > price_max:
            price_min, price_max = price_max, price_min
        
        # Build opening_hours from open_hour and close_hour columns
        opening_hours = ""
        if row.open_hour and row.close_hour:
            opening_hours = f"{str(row.open_hour)[:5]} - {str(row.close_hour)[:5]}"
        elif row.open_hour:
            opening_hours = f"Mở cửa từ {str(row.open_hour)[:5]}"
        elif row.close_hour:
            opening_hours = f"Đóng cửa lúc {str(row.close_hour)[:5]}"
        
        # Fetch related posts from MongoDB
        from middleware.mongodb_client import mongo_client, get_mongodb
        from app.services.rating_sync import calculate_place_rating_from_mongodb
        
        related_posts = []
        # Real-time rating calculation from MongoDB (includes rating=0)
        real_time_rating_count = 0
        real_time_rating_average = 0.0
        
        try:
            await get_mongodb()
            
            # Calculate real-time rating from MongoDB posts (bao gồm cả rating=0)
            rating_data = await calculate_place_rating_from_mongodb(place_id, mongo_client)
            real_time_rating_count = rating_data.get("rating_count", 0)
            real_time_rating_average = rating_data.get("rating_average", 0.0)
            logger.info(f"[PLACES] Real-time rating for place {place_id}: count={real_time_rating_count}, avg={real_time_rating_average}")
            
            # Query posts with $or to match both int and string related_place_id
            logger.info(f"[PLACES] Fetching related posts for place_id={place_id}")
            posts = await mongo_client.find_many(
                "posts",
                {
                    "$or": [
                        {"related_place_id": place_id},
                        {"related_place_id": str(place_id)}
                    ],
                    "status": "approved"
                },
                sort=[("likes_count", -1), ("comments_count", -1)],
                limit=10
            )
            logger.info(f"[PLACES] Found {len(posts) if posts else 0} posts with related_place_id={place_id}")
            
            # Fallback 1: if no posts for this place, get general approved posts
            if not posts or len(posts) == 0:
                logger.info("[PLACES] No related posts found, trying general approved posts...")
                posts = await mongo_client.find_many(
                    "posts",
                    {"status": "approved"},
                    sort=[("likes_count", -1), ("comments_count", -1)],
                    limit=5
                )
                logger.info(f"[PLACES] Found {len(posts) if posts else 0} approved posts")
            
            # Fallback 2: if still no approved posts, get any posts (for development/testing)
            if not posts or len(posts) == 0:
                logger.info("[PLACES] No approved posts found, trying any posts...")
                posts = await mongo_client.find_many(
                    "posts",
                    {},  # Get all posts regardless of status
                    sort=[("created_at", -1)],
                    limit=5
                )
                logger.info(f"[PLACES] Found {len(posts) if posts else 0} total posts in MongoDB")
            
            # Format related posts - chỉ cần gọi helper function
            for post in posts:
                author = get_user_compact(post.get("author_id"), db)
                post_images = post.get("images", [])
                if not post_images:
                    post_images = images  # Fallback to place images
                
                related_posts.append({
                    "_id": str(post.get("_id")),
                    "author": author,
                    "title": post.get("title"),
                    "content": post.get("content"),
                    "rating": post.get("rating"),
                    "images": normalize_image_list(post_images),
                    "tags": post.get("tags", []),
                    "likes_count": post.get("likes_count", 0),
                    "comments_count": post.get("comments_count", 0),
                    "is_liked": False,
                    "status": post.get("status"),
                    "created_at": post.get("created_at").isoformat() if post.get("created_at") else None
                })
        except Exception as e:
            import traceback
            logger.error(f"Error fetching related posts: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            related_posts = []
        
        # Use real-time values if available, fallback to PostgreSQL
        if real_time_rating_count > 0 or rating_count == 0:
            rating_count = real_time_rating_count
            rating = real_time_rating_average
            
            # Sync back to PostgreSQL to keep data consistent
            try:
                from app.services.rating_sync import update_place_rating
                await update_place_rating(place_id, db, mongo_client)
                logger.info(f"[PLACES] Synced rating to PostgreSQL for place {place_id}")
            except Exception as sync_error:
                logger.warning(f"[PLACES] Failed to sync rating to PostgreSQL: {sync_error}")

        
        # Response theo Swagger PlaceDetailResponse schema
        # PlaceDetail extends PlaceCompact nên cần đầy đủ các trường
        data = {
            # PlaceCompact fields (required by frontend)
            "id": row.id,
            "name": row.name,
            "district_id": row.district_id,
            "place_type_id": row.place_type_id,
            "rating_average": rating,
            "price_min": price_min,
            "price_max": price_max,
            "main_image_url": images[0] if images else get_main_image_url(place_id, db),
            
            # PlaceDetail extended fields
            "description": row.description or "",
            "address": address,
            "address_detail": address,
            "latitude": latitude,
            "longitude": longitude,
            "opening_hours": opening_hours,
            "open_hour": str(row.open_hour)[:5] if row.open_hour else None,
            "close_hour": str(row.close_hour)[:5] if row.close_hour else None,
            "reviews_count": rating_count,
            "rating_count": rating_count,
            
            # Extended data
            "details": details,
            "images": images,
            "nearby": nearby_places,
            "related_posts": related_posts
        }

        # Log visit using centralized service
        try:
            user_id = int(current_user.get("user_id")) if current_user else None
            await log_visit(
                db=db,
                request=request,
                user_id=user_id,
                place_id=place_id
            )
        except Exception as e:
            logger.error(f"Error logging visit: {e}")
            # Don't fail the request if logging fails
        
        logger.info(f"[PLACES] Get place detail - id={place_id}, name='{row.name}'")
        
        return success_response(
            data=data,
            message="Lấy chi tiết địa điểm thành công"
        )
        
    except Exception as e:
        logger.error(f"[PLACES] Error getting place detail: {str(e)}")
        return server_error_response()


@router.post("/{place_id}/favorite", summary="Toggle Favorite Place")
async def toggle_favorite_place(
    request: Request,
    place_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Toggle yêu thích địa điểm - Lưu vào user_place_favorites table
    """
    try:
        # Tìm địa điểm
        place = db.query(Place).filter(Place.id == place_id, Place.deleted_at == None).first()
        
        if not place:
            return not_found_response("địa điểm")
        
        user_id = int(current_user.get("user_id", 0))
        
        # Kiểm tra đã favorite chưa
        existing_fav = db.query(UserPlaceFavorite).filter(
            UserPlaceFavorite.user_id == user_id,
            UserPlaceFavorite.place_id == place_id
        ).first()
        
        if existing_fav:
            # Đã yêu thích -> Bỏ yêu thích
            db.delete(existing_fav)
            db.commit()
            is_favorited = False
            message = "Đã bỏ yêu thích"
            
            # Log activity
            await log_activity(
                db=db,
                user_id=user_id,
                action="unfavorite_place",
                details=f"Bỏ yêu thích địa điểm: {place.name} (ID: {place_id})",
                request=request
            )
        else:
            # Chưa yêu thích -> Thêm yêu thích
            new_fav = UserPlaceFavorite(user_id=user_id, place_id=place_id)
            db.add(new_fav)
            db.commit()
            is_favorited = True
            message = "Đã thêm vào yêu thích"
            
            # Log activity
            await log_activity(
                db=db,
                user_id=user_id,
                action="favorite_place",
                details=f"Thêm yêu thích địa điểm: {place.name} (ID: {place_id})",
                request=request
            )
        
        logger.info(f"[PLACES] Toggle favorite - user_id={user_id}, place_id={place_id}, is_favorited={is_favorited}")
        
        return {
            "success": True,
            "is_favorited": is_favorited,
            "message": message
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"[PLACES] Error toggling favorite: {str(e)}")
        return server_error_response()


# ==================== END OF PLACES ROUTES ====================
