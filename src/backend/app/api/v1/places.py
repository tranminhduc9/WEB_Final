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
from app.utils.image_helpers import get_main_image_url
from middleware.auth import get_current_user, get_optional_user
from middleware.response import (
    success_response,
    error_response,
    not_found_response,
    server_error_response
)

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
    
    Swagger PlaceCompact chỉ có 8 fields:
    - id, name, district_id, place_type_id
    - rating_average, price_min, price_max, main_image_url
    """
    place_id = row.id
    rating_average = float(row.rating_average) if row.rating_average else 0.0
    price_min = float(row.price_min) if row.price_min else 0
    price_max = float(row.price_max) if row.price_max else 0
    
    # Auto-swap nếu giá trị bị đảo ngược trong database
    if price_min > price_max and price_max > 0:
        price_min, price_max = price_max, price_min
    
    # Lấy ảnh từ database hoặc local uploads
    image_url = get_main_image_url(place_id, db)
    
    # Chỉ trả về 8 fields theo Swagger spec
    return {
        "id": place_id,
        "name": row.name,
        "district_id": row.district_id,
        "place_type_id": row.place_type_id,
        "rating_average": rating_average,
        "price_min": price_min,
        "price_max": price_max,
        "main_image_url": image_url
    }


def place_row_to_horizontal(row, db: Session = None, user_lat: float = None, user_long: float = None) -> Dict[str, Any]:
    """
    Chuyển đổi row sang horizontal format - trả về PlaceCompact theo Swagger.
    Nearby places endpoint vẫn trả về PlaceCompact format.
    """
    place_id = row.id
    rating_average = float(row.rating_average) if row.rating_average else 0.0
    price_min = float(row.price_min) if row.price_min else 0
    price_max = float(row.price_max) if row.price_max else 0
    
    # Auto-swap nếu giá trị bị đảo ngược trong database
    if price_min > price_max and price_max > 0:
        price_min, price_max = price_max, price_min
    
    # Lấy ảnh
    image_url = get_main_image_url(place_id, db)
    
    # Trả về PlaceCompact format theo Swagger
    return {
        "id": place_id,
        "name": row.name,
        "district_id": row.district_id,
        "place_type_id": row.place_type_id,
        "rating_average": rating_average,
        "price_min": price_min,
        "price_max": price_max,
        "main_image_url": image_url
    }


# ==================== ENDPOINTS ====================

@router.get("", summary="Get Outstanding Places")
async def get_outstanding_places(
    request: Request,
    page: int = Query(1, ge=1, description="Số trang"),
    limit: int = Query(10, ge=1, le=50, description="Số lượng mỗi trang"),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách địa điểm nổi bật cho Homepage (rating_average >= 4.0)
    """
    try:
        # Count total outstanding places
        count_query = text("""
            SELECT COUNT(*) as total 
            FROM places 
            WHERE rating_average >= 4.0 AND deleted_at IS NULL
        """)
        count_result = db.execute(count_query).fetchone()
        total_items = count_result.total if count_result else 0
        
        offset, pagination = paginate_query(page, limit, total_items)
        
        # Lấy places với district name
        query = text("""
            SELECT p.*, d.name as district_name
            FROM places p
            LEFT JOIN districts d ON p.district_id = d.id
            WHERE p.rating_average >= 4.0 AND p.deleted_at IS NULL
            ORDER BY p.rating_average DESC, p.name ASC
            LIMIT :limit OFFSET :offset
        """)
        
        result = db.execute(query, {"limit": limit, "offset": offset}).fetchall()
        
        data = [place_row_to_compact(row, db) for row in result]
        
        logger.info(f"[PLACES] Get outstanding places - Found {len(data)} places (page {page})")
        
        return {
            "success": True,
            "data": data,
            "pagination": pagination,
            "message": "Lấy danh sách địa điểm nổi bật thành công"
        }
        
    except Exception as e:
        logger.error(f"[PLACES] Error getting outstanding places: {str(e)}")
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
        
        data = [place_row_to_compact(row, db) for row in result]
        
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
        
        data = [place_row_to_horizontal(row, db, lat, long) for row in result]
        
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
        
        # Lấy images
        images_query = text("""
            SELECT image_url FROM place_images 
            WHERE place_id = :place_id 
            ORDER BY is_main DESC, id ASC
        """)
        images_result = db.execute(images_query, {"place_id": place_id}).fetchall()
        
        # Transform relative URLs to full URLs
        import os
        backend_host = os.getenv("BACKEND_HOST", "127.0.0.1")
        backend_port = os.getenv("BACKEND_PORT", "8080")
        base_url = f"http://{backend_host}:{backend_port}"
        
        if images_result:
            images = []
            for img in images_result:
                url = img.image_url
                if url and not url.startswith('http'):
                    url = f"{base_url}{url}"
                images.append(url)
        else:
            images = [get_main_image_url(place_id, db)]
        
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
        
        # Response theo Swagger PlaceDetailResponse schema
        data = {
            "id": row.id,
            "name": row.name,
            "description": row.description or "",
            "address_detail": address,
            "rating_average": rating,
            "latitude": latitude,
            "longitude": longitude,
            "details": details,
            "images": images,
            "nearby": nearby_places,
            "related_posts": []
        }

        # Log visit
        try:
            user_id = int(current_user.get("user_id")) if current_user else None
            visit_log = VisitLog(
                user_id=user_id,
                place_id=place_id,
                page_url=str(request.url),
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent")
            )
            db.add(visit_log)
            db.commit()
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
        else:
            # Chưa yêu thích -> Thêm yêu thích
            new_fav = UserPlaceFavorite(user_id=user_id, place_id=place_id)
            db.add(new_fav)
            db.commit()
            is_favorited = True
            message = "Đã thêm vào yêu thích"
        
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
