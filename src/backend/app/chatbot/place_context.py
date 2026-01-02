"""
Place Context Service for Chatbot

Service tìm kiếm địa điểm liên quan để inject context vào chatbot prompt.
Giúp chatbot gợi ý chính xác các địa điểm có trong database.

Dynamic features:
- Districts: Lấy từ database (bảng districts)
- Place Types: Lấy từ database (bảng place_types)
- Keywords: Mapping động với place_type names
"""

import logging
import re
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

logger = logging.getLogger(__name__)


# Keyword aliases để map nhiều từ đến cùng một concept
# Format: "keyword": "normalized_concept"
KEYWORD_ALIASES = {
    # Food aliases
    "ăn": "restaurant",
    "phở": "restaurant",
    "bún": "restaurant",
    "cơm": "restaurant",
    "quán ăn": "restaurant",
    "nhà hàng": "restaurant",
    "ẩm thực": "restaurant",
    "đồ ăn": "restaurant",
    "món ăn": "restaurant",
    "buffet": "restaurant",
    "hải sản": "restaurant",
    "lẩu": "restaurant",
    "nướng": "restaurant",
    "bánh": "restaurant",
    "chè": "restaurant",
    "kem": "restaurant",
    "trà sữa": "restaurant",
    "quán": "restaurant",
    
    # Coffee/Drinks
    "cà phê": "cafe",
    "cafe": "cafe",
    "coffee": "cafe",
    "quán nước": "cafe",
    
    # Hotel/Accommodation
    "khách sạn": "hotel",
    "hotel": "hotel",
    "homestay": "hotel",
    "nhà nghỉ": "hotel",
    "resort": "hotel",
    "ở đâu": "hotel",
    "nghỉ ngơi": "hotel",
    "lưu trú": "hotel",
    
    # Tourist Attractions
    "tham quan": "tourist",
    "du lịch": "tourist",
    "di tích": "tourist",
    "đền": "tourist",
    "chùa": "tourist",
    "bảo tàng": "tourist",
    "hồ": "tourist",
    "công viên": "tourist",
    "phố cổ": "tourist",
    "lăng": "tourist",
    "thắng cảnh": "tourist",
    "danh lam": "tourist",
    "điểm đến": "tourist",
    
    # Shopping
    "mua sắm": "shopping",
    "chợ": "shopping",
    "shopping": "shopping",
    "trung tâm thương mại": "shopping",
}


class PlaceContextService:
    """
    Service tìm kiếm địa điểm liên quan để inject vào chatbot.
    
    Dynamic features:
    - Load districts từ database
    - Load place_types từ database
    - Cache để tối ưu performance
    """
    
    def __init__(self):
        # Cache for database data
        self._districts_cache: Dict[str, int] = {}  # name -> id
        self._place_types_cache: Dict[str, int] = {}  # name -> id
        self._cache_loaded = False
    
    def _load_cache(self, db: Session) -> None:
        """
        Load districts và place_types từ database vào cache.
        Chỉ load một lần.
        """
        if self._cache_loaded:
            return
        
        try:
            from config.database import District, PlaceType
            
            # Load districts
            districts = db.query(District).all()
            for d in districts:
                # Store lowercase for matching
                self._districts_cache[d.name.lower()] = d.id
                # Also store original name
                self._districts_cache[d.name] = d.id
            
            # Load place types
            place_types = db.query(PlaceType).all()
            for pt in place_types:
                self._place_types_cache[pt.name.lower()] = pt.id
                self._place_types_cache[pt.name] = pt.id
            
            self._cache_loaded = True
            logger.info(f"Loaded {len(districts)} districts and {len(place_types)} place types into cache")
            
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
    
    def _sanitize_input(self, text: str) -> str:
        """
        Sanitize user input để ngăn chặn SQL injection.
        """
        if not text:
            return ""
        
        # Remove dangerous characters
        dangerous_chars = ["'", '"', ";", "--", "/*", "*/", "\\", "\x00"]
        result = text
        for char in dangerous_chars:
            result = result.replace(char, "")
        
        # Limit length and clean whitespace
        result = " ".join(result[:500].split())
        return result.strip()
    
    def _find_district(self, message: str) -> Optional[Dict[str, Any]]:
        """
        Tìm district trong message bằng cách so sánh với cache.
        
        Returns:
            Dict với id và name của district, hoặc None
        """
        message_lower = message.lower()
        
        for name, district_id in self._districts_cache.items():
            if name.lower() in message_lower:
                return {"id": district_id, "name": name}
        
        return None
    
    def _find_place_type(self, message: str) -> Optional[Dict[str, Any]]:
        """
        Tìm place_type trong message dựa trên keyword aliases và cache.
        
        Returns:
            Dict với id và name của place_type, hoặc None
        """
        message_lower = message.lower()
        
        # Tìm keyword match
        matched_concept = None
        for keyword, concept in KEYWORD_ALIASES.items():
            if keyword in message_lower:
                matched_concept = concept
                break
        
        if not matched_concept:
            return None
        
        # Map concept đến place_type trong database
        # Database có: Du lịch (1), Ẩm thực (2), Lưu trú (3)
        concept_to_type = {
            "restaurant": ["Ẩm thực", "ẩm thực"],
            "cafe": ["Ẩm thực", "ẩm thực"],
            "hotel": ["Lưu trú", "lưu trú"],
            "tourist": ["Du lịch", "du lịch"],
            "shopping": ["Du lịch", "du lịch"],  # Map shopping to Du lịch as fallback
        }
        
        type_names = concept_to_type.get(matched_concept, [])
        
        for type_name in type_names:
            if type_name.lower() in self._place_types_cache:
                return {
                    "id": self._place_types_cache[type_name.lower()],
                    "name": type_name
                }
            if type_name in self._place_types_cache:
                return {
                    "id": self._place_types_cache[type_name],
                    "name": type_name
                }
        
        # Fallback: tìm trực tiếp trong cache
        for type_name, type_id in self._place_types_cache.items():
            if matched_concept in type_name.lower():
                return {"id": type_id, "name": type_name}
        
        return None
    
    def _extract_keywords(self, message: str) -> List[str]:
        """Extract các từ khóa quan trọng từ message (đã sanitize)."""
        clean_message = self._sanitize_input(message)
        
        stop_words = {
            "tôi", "cho", "muốn", "hỏi", "xin", "được", "có",
            "là", "và", "của", "với", "trong", "nào", "ở",
            "đâu", "gì", "như", "thế", "này", "kia", "đó",
            "hay", "hoặc", "nhưng", "mà", "vì", "nên", "để",
            "thì", "sẽ", "đã", "đang", "rồi", "còn", "cũng",
            "rất", "quá", "lắm", "nhất", "hơn", "bằng", "một",
            "những", "các", "tất", "cả", "mọi", "đây", "kia"
        }
        
        words = re.findall(r'\b[\w]+\b', clean_message.lower())
        
        keywords = []
        for w in words:
            if w not in stop_words and 2 <= len(w) <= 50:
                if re.match(r'^[\w\u00C0-\u024F\u1E00-\u1EFF]+$', w):
                    keywords.append(w)
        
        return keywords[:5]
    
    def extract_context(self, message: str, db: Session = None) -> Dict[str, Any]:
        """
        Extract context từ message của user.
        
        Args:
            message: Tin nhắn từ user
            db: Database session (optional, để load cache)
            
        Returns:
            Dict với keys: place_type, district, keywords
        """
        # Load cache if db provided
        if db:
            self._load_cache(db)
        
        # Find place type
        place_type = self._find_place_type(message)
        
        # Find district
        district = self._find_district(message)
        
        # Extract keywords
        keywords = self._extract_keywords(message)
        
        return {
            "place_type": place_type,  # {"id": ..., "name": ...} or None
            "district": district,      # {"id": ..., "name": ...} or None
            "keywords": keywords,
            "original_message": message
        }
    
    async def search_relevant_places(
        self,
        message: str,
        db: Session,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Tìm kiếm địa điểm liên quan đến message.
        
        Strategy:
        1. Trước tiên tìm theo keyword trong tên địa điểm
        2. Nếu không có kết quả, fallback về tìm theo place_type
        3. Cuối cùng, nếu vẫn không có, lấy các địa điểm rating cao nhất
        
        Args:
            message: Tin nhắn từ user
            db: Database session
            limit: Số kết quả tối đa
            
        Returns:
            List các địa điểm compact
        """
        from config.database import Place, PlaceType, District
        
        # Load cache
        self._load_cache(db)
        
        # Extract context
        context = self.extract_context(message, db)
        
        # Helper function to format place results
        def format_places(places_list):
            from app.utils.image_helpers import get_main_image_url
            
            results = []
            for place in places_list:
                # Get main image URL using helper (returns full URL)
                main_image_url = get_main_image_url(place.id, db)
                
                # Get district name
                district = db.query(District).filter(
                    District.id == place.district_id
                ).first()
                
                # Get place type
                place_type = db.query(PlaceType).filter(
                    PlaceType.id == place.place_type_id
                ).first()
                
                results.append({
                    "id": place.id,
                    "name": place.name,
                    "district_id": place.district_id,
                    "district_name": district.name if district else None,
                    "place_type_id": place.place_type_id,
                    "rating_average": float(place.rating_average) if place.rating_average else 0,
                    "rating_count": place.rating_count or 0,
                    "address": place.address_detail,
                    "main_image_url": main_image_url,
                    "price_min": float(place.price_min) if place.price_min else 0,
                    "price_max": float(place.price_max) if place.price_max else 0,
                })
            return results
        
        # Các từ phổ biến không nên dùng để filter tên địa điểm
        generic_words = {
            "ngon", "vài", "quán", "nhà", "hàng", "nào", "cho", "tôi", 
            "đâu", "chỗ", "gì", "muốn", "tìm", "kiếm", "gợi", "ý"
        }
        
        # Filter keywords để chỉ giữ lại từ đặc trưng
        specific_keywords = [
            kw for kw in context.get("keywords", []) 
            if kw.lower() not in generic_words and len(kw) >= 2
        ]
        
        places = []
        
        # STRATEGY 1: Tìm theo keyword đặc trưng trong tên địa điểm
        if specific_keywords:
            query = db.query(Place).filter(Place.deleted_at.is_(None))
            
            # Filter by place_type if detected (e.g., nhà hàng)
            if context["place_type"]:
                query = query.filter(Place.place_type_id == context["place_type"]["id"])
            
            # Filter by district if detected
            if context["district"]:
                query = query.filter(Place.district_id == context["district"]["id"])
            
            # Search by specific keywords in name or description
            keyword_filters = []
            for kw in specific_keywords:
                safe_kw = self._sanitize_input(kw)
                if safe_kw:
                    keyword_filters.append(Place.name.ilike(f"%{safe_kw}%"))
            
            if keyword_filters:
                query = query.filter(or_(*keyword_filters))
            
            query = query.order_by(Place.rating_average.desc())
            places = query.limit(limit).all()
            
            if places:
                logger.info(f"Found {len(places)} places by keywords: {specific_keywords}")
        
        # STRATEGY 2: Fallback về tìm theo place_type nếu không có kết quả keywords
        if not places and context["place_type"]:
            query = db.query(Place).filter(
                Place.deleted_at.is_(None),
                Place.place_type_id == context["place_type"]["id"]
            )
            
            # Filter by district if detected
            if context["district"]:
                query = query.filter(Place.district_id == context["district"]["id"])
            
            query = query.order_by(Place.rating_average.desc())
            places = query.limit(limit).all()
            
            if places:
                logger.info(f"Found {len(places)} places by place_type: {context['place_type']['name']}")
        
        # STRATEGY 3: Fallback cuối - lấy các địa điểm rating cao nhất
        if not places:
            query = db.query(Place).filter(Place.deleted_at.is_(None))
            
            # Filter by district if detected
            if context["district"]:
                query = query.filter(Place.district_id == context["district"]["id"])
            
            query = query.order_by(Place.rating_average.desc())
            places = query.limit(limit).all()
            
            logger.info(f"Fallback: Found {len(places)} top-rated places")
        
        results = format_places(places)
        
        logger.info(f"Final result: {len(results)} places for context: place_type={context['place_type']}, district={context['district']}, keywords={specific_keywords}")
        return results
    
    def format_places_for_prompt(self, places: List[Dict]) -> str:
        """Format danh sách địa điểm thành text để inject vào prompt."""
        if not places:
            return ""
        
        lines = ["\n## Địa điểm có trong hệ thống (có thể gợi ý cho người dùng):"]
        
        for i, place in enumerate(places, 1):
            rating = place.get('rating_average') or place.get('rating', 0)
            rating_str = f"⭐{rating:.1f}" if rating else "Chưa có đánh giá"
            district = place.get('district_name') or place.get('district')
            district_str = f", {district}" if district else ""
            
            lines.append(f"{i}. **{place['name']}** ({rating_str}{district_str})")
            
            if place.get('address'):
                lines.append(f"   📍 {place['address']}")
        
        lines.append("\n*Hãy ưu tiên gợi ý các địa điểm trên nếu phù hợp với câu hỏi.*")
        
        return "\n".join(lines)
    
    def get_all_districts(self, db: Session) -> List[str]:
        """Get all district names from database."""
        self._load_cache(db)
        # Return unique names (not lowercase duplicates)
        return list(set(
            name for name in self._districts_cache.keys() 
            if not name.islower() or name == name.lower()
        ))
    
    def get_all_place_types(self, db: Session) -> List[str]:
        """Get all place type names from database."""
        self._load_cache(db)
        return list(set(
            name for name in self._place_types_cache.keys()
            if not name.islower() or name == name.lower()
        ))
    
    def clear_cache(self) -> None:
        """Clear the cache to reload from database."""
        self._districts_cache.clear()
        self._place_types_cache.clear()
        self._cache_loaded = False
        logger.info("Place context cache cleared")


# Singleton instance
_service: Optional[PlaceContextService] = None


def get_place_context_service() -> PlaceContextService:
    """Get singleton service instance."""
    global _service
    if _service is None:
        _service = PlaceContextService()
    return _service
