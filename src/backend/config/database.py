"""
Cấu hình Database cho PostgreSQL

Module này xử lý kết nối và quản lý database PostgreSQL,
cung cấp session và engine cho SQLAlchemy ORM.

Database Schema v3.1 Compatible - UNIFIED DATABASE (Port 5433)
"""

from sqlalchemy import (
    create_engine, Column, Integer, String, Boolean, DateTime,
    Text, Float, Numeric, Time, ForeignKey, UniqueConstraint, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)

# Database URL từ environment variables - Sử dụng DATABASE_URL duy nhất
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://admin:123456@localhost:5433/travel_db"
)

# Tạo SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
    max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20")),
    pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30")),
    pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "3600")),
    echo=False  # Set to True only for debugging
)

# Tạo SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class cho models
Base = declarative_base()


# ==================== MODELS ====================

class Role(Base):
    """Model Role - Vai trò người dùng"""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    role_name = Column(String(50), unique=True, nullable=False)

    # Relationships
    users = relationship("User", back_populates="role")

    def __repr__(self):
        return f"<Role(id={self.id}, role_name={self.role_name})>"


class User(Base):
    """
    Model User - Thông tin người dùng
    Schema v3.1 Compatible
    """
    __tablename__ = "users"

    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Thông tin cơ bản
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    # Thông tin bổ sung
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)

    # Role (FK to roles table)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, default=3)  # 3 = user

    # Status
    reputation_score = Column(Integer, default=0)
    is_active = Column(Boolean, default=True, nullable=False)
    ban_reason = Column(String(500), nullable=True)

    # Soft delete
    deleted_at = Column(DateTime, nullable=True)

    # Timestamps
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    role = relationship("Role", back_populates="users")
    refresh_tokens = relationship("TokenRefresh", back_populates="user")
    place_favorites = relationship("UserPlaceFavorite", back_populates="user")
    visit_logs = relationship("VisitLog", back_populates="user")
    activity_logs = relationship("ActivityLog", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role_id={self.role_id})>"

    def to_dict(self, include_sensitive: bool = False) -> dict:
        """Chuyển đổi user object sang dictionary"""
        data = {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email if include_sensitive else None,
            "avatar_url": self.avatar_url,
            "bio": self.bio,
            "role_id": self.role_id,
            "is_active": self.is_active,
            "reputation_score": self.reputation_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None
        }
        return data

    def to_compact_dict(self) -> dict:
        """Chuyển đổi sang compact format cho responses"""
        return {
            "id": self.id,
            "full_name": self.full_name,
            "avatar_url": self.avatar_url,
            "role_id": self.role_id
        }

    @property
    def role_name(self) -> str:
        """Get role name from role relationship"""
        if self.role:
            return self.role.role_name
        role_map = {1: "admin", 2: "moderator", 3: "user"}
        return role_map.get(self.role_id, "user")


class TokenRefresh(Base):
    """Model TokenRefresh - Lưu trữ refresh tokens"""
    __tablename__ = "token_refresh"
    __table_args__ = (
        Index('idx_token_refresh_expires_at', 'expires_at'),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    refresh_token = Column(String(500), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="refresh_tokens")

    def __repr__(self):
        return f"<TokenRefresh(id={self.id}, user_id={self.user_id}, revoked={self.revoked})>"


class PlaceType(Base):
    """Model PlaceType - Loại địa điểm"""
    __tablename__ = "place_types"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)

    # Relationships
    places = relationship("Place", back_populates="place_type")

    def __repr__(self):
        return f"<PlaceType(id={self.id}, name={self.name})>"


class District(Base):
    """Model District - Quận/Huyện"""
    __tablename__ = "districts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)

    # Relationships
    places = relationship("Place", back_populates="district")

    def __repr__(self):
        return f"<District(id={self.id}, name={self.name})>"


class Place(Base):
    """Model Place - Địa điểm (Schema v3.1)"""
    __tablename__ = "places"
    __table_args__ = (
        Index('idx_places_location', 'latitude', 'longitude'),
        Index('idx_places_district', 'district_id'),
        Index('idx_places_type', 'place_type_id'),
        Index('idx_places_rating', 'rating_average'),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    place_type_id = Column(Integer, ForeignKey("place_types.id"), nullable=False)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    address_detail = Column(String(500), nullable=True)
    
    # Location
    latitude = Column(Numeric(9, 6), nullable=False)
    longitude = Column(Numeric(9, 6), nullable=False)
    
    # Rating
    rating_average = Column(Numeric(3, 2), default=0)
    rating_count = Column(Integer, default=0)
    rating_total = Column(Numeric(10, 2), default=0)
    
    # Business hours
    open_hour = Column(Time, nullable=True)
    close_hour = Column(Time, nullable=True)
    
    # Price
    price_min = Column(Numeric(10, 2), default=0)
    price_max = Column(Numeric(10, 2), default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    place_type = relationship("PlaceType", back_populates="places")
    district = relationship("District", back_populates="places")
    images = relationship("PlaceImage", back_populates="place")
    favorites = relationship("UserPlaceFavorite", back_populates="place")
    
    # Subtype relationships (1-to-1)
    restaurant = relationship("Restaurant", uselist=False, back_populates="place", cascade="all, delete-orphan")
    hotel = relationship("Hotel", uselist=False, back_populates="place", cascade="all, delete-orphan")
    tourist_attraction = relationship("TouristAttraction", uselist=False, back_populates="place", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Place(id={self.id}, name={self.name})>"

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "place_type_id": self.place_type_id,
            "district_id": self.district_id,
            "description": self.description,
            "address_detail": self.address_detail,
            "latitude": float(self.latitude) if self.latitude else None,
            "longitude": float(self.longitude) if self.longitude else None,
            "rating_average": float(self.rating_average) if self.rating_average else 0,
            "rating_count": self.rating_count or 0,
            "price_min": float(self.price_min) if self.price_min else 0,
            "price_max": float(self.price_max) if self.price_max else 0,
            "open_hour": str(self.open_hour) if self.open_hour else None,
            "close_hour": str(self.close_hour) if self.close_hour else None,
        }


class PlaceImage(Base):
    """Model PlaceImage - Ảnh địa điểm"""
    __tablename__ = "place_images"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    place_id = Column(Integer, ForeignKey("places.id"), nullable=False)
    image_url = Column(String(500), nullable=False)
    is_main = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    place = relationship("Place", back_populates="images")

    def __repr__(self):
        return f"<PlaceImage(id={self.id}, place_id={self.place_id}, is_main={self.is_main})>"


class UserPlaceFavorite(Base):
    """Model UserPlaceFavorite - User yêu thích địa điểm"""
    __tablename__ = "user_place_favorites"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    place_id = Column(Integer, ForeignKey("places.id"), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="place_favorites")
    place = relationship("Place", back_populates="favorites")

    def __repr__(self):
        return f"<UserPlaceFavorite(user_id={self.user_id}, place_id={self.place_id})>"


class ActivityLog(Base):
    """Model ActivityLog - Log hoạt động"""
    __tablename__ = "activity_logs"
    __table_args__ = (
        Index('idx_activity_logs_user', 'user_id'),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(100), nullable=False)
    details = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="activity_logs")

    def __repr__(self):
        return f"<ActivityLog(id={self.id}, user_id={self.user_id}, action={self.action})>"


class Restaurant(Base):
    """Model Restaurant - Nhà hàng (Extension of Place)"""
    __tablename__ = "restaurants"

    place_id = Column(Integer, ForeignKey("places.id", ondelete="CASCADE"), primary_key=True)
    cuisine_type = Column(String(100), nullable=True)
    avg_price_per_person = Column(Numeric(10, 2), nullable=True)

    # Relationships
    place = relationship("Place", back_populates="restaurant")

    def __repr__(self):
        return f"<Restaurant(place_id={self.place_id})>"


class Hotel(Base):
    """Model Hotel - Khách sạn (Extension of Place)"""
    __tablename__ = "hotels"

    place_id = Column(Integer, ForeignKey("places.id", ondelete="CASCADE"), primary_key=True)
    star_rating = Column(Integer, nullable=True)
    price_per_night = Column(Numeric(10, 2), nullable=True)
    check_in_time = Column(Time, nullable=True)
    check_out_time = Column(Time, nullable=True)

    # Relationships
    place = relationship("Place", back_populates="hotel")

    def __repr__(self):
        return f"<Hotel(place_id={self.place_id}, star_rating={self.star_rating})>"


class TouristAttraction(Base):
    """Model TouristAttraction - Điểm tham quan (Extension of Place)"""
    __tablename__ = "tourist_attractions"

    place_id = Column(Integer, ForeignKey("places.id", ondelete="CASCADE"), primary_key=True)
    ticket_price = Column(Numeric(10, 2), nullable=True)
    is_ticket_required = Column(Boolean, default=True)

    # Relationships
    place = relationship("Place", back_populates="tourist_attraction")

    def __repr__(self):
        return f"<TouristAttraction(place_id={self.place_id})>"


class UserPostFavorite(Base):
    """Model UserPostFavorite - User yêu thích bài viết/review"""
    __tablename__ = "user_post_favorites"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    post_id = Column(String(100), primary_key=True)  # MongoDB ID is string
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('user_id', 'post_id', name='uq_user_post_favorite'),
    )

    def __repr__(self):
        return f"<UserPostFavorite(user_id={self.user_id}, post_id={self.post_id})>"


class VisitLog(Base):
    """Model VisitLog - Lịch sử truy cập"""
    __tablename__ = "visit_logs"
    __table_args__ = (
        Index('idx_visit_logs_user', 'user_id'),
        Index('idx_visit_logs_place', 'place_id'),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    place_id = Column(Integer, ForeignKey("places.id"), nullable=True)
    post_id = Column(String(100), nullable=True)
    page_url = Column(String(500), nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(Text, nullable=True)
    visited_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="visit_logs")
    place = relationship("Place")

    def __repr__(self):
        return f"<VisitLog(id={self.id}, visited_at={self.visited_at})>"


# ==================== DATABASE DEPENDENCIES ====================

def get_db() -> Session:
    """
    Dependency để lấy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Khởi tạo database - Tạo tất cả tables CHƯA tồn tại

    Tạo từng bảng riêng lẻ để:
    - Xử lý lỗi index duplicate mà không ảnh hưởng bảng khác
    - Đảm bảo tất cả bảng được tạo dù có lỗi index

    LƯU Ý: KHÔNG tự động seed data. Data chỉ được load từ:
    1. Docker container's init.sql (khi container khởi tạo lần đầu)
    2. Data hiện có trong database (nếu container đã chạy trước đó)
    """
    try:
        from sqlalchemy import inspect
        from sqlalchemy.exc import ProgrammingError
        from sqlalchemy import text

        # Kiểm tra tables hiện có
        inspector = inspect(engine)
        existing_tables = set(inspector.get_table_names())
        logger.info(f"Các bảng hiện có trong database: {list(existing_tables)}")

        # Lấy danh sách bảng được định nghĩa trong code
        defined_tables = set(Base.metadata.tables.keys())
        missing_tables = defined_tables - existing_tables

        if missing_tables:
            logger.info(f"[WARN] Phat hien cac bang thieu: {list(missing_tables)}")
            
            # Xóa các orphan indexes (index tồn tại nhưng bảng không có)
            # Điều này xảy ra khi tạo bảng bị fail giữa chừng
            logger.info("Kiểm tra và xóa orphan indexes...")
            with engine.connect() as conn:
                for table_name in missing_tables:
                    # Các index patterns có thể tồn tại mà không có bảng
                    orphan_indexes = [
                        f"ix_{table_name}_id",
                        f"ix_{table_name}_email",
                        f"idx_{table_name}_user",
                        f"idx_{table_name}_place",
                    ]
                    for idx_name in orphan_indexes:
                        try:
                            conn.execute(text(f"DROP INDEX IF EXISTS {idx_name}"))
                            conn.commit()
                        except Exception:
                            pass  # Index không tồn tại hoặc không thể xóa
            
            logger.info("Đang tạo các bảng thiếu...")
            
            # Tạo tables theo đúng thứ tự FK dependency
            # Thứ tự: roles → users → các bảng phụ thuộc users
            # place_types, districts → places → subtypes
            table_order = [
                'roles', 'place_types', 'districts',
                'users',
                'token_refresh', 'activity_logs',
                'places',
                'place_images', 'restaurants', 'hotels', 'tourist_attractions',  # FK: places
                'user_place_favorites', 'user_post_favorites', 'visit_logs'  # FK: users, places
            ]
            
            created_count = 0
            for table_name in table_order:
                if table_name in missing_tables:
                    table = Base.metadata.tables.get(table_name)
                    if table is not None:
                        try:
                            table.create(bind=engine, checkfirst=True)
                            logger.info(f"  [OK] Da tao bang: {table_name}")
                            created_count += 1
                        except ProgrammingError as e:
                            error_msg = str(e)
                            if "already exists" in error_msg:
                                # Vẫn còn index/object trùng - thử xóa và tạo lại
                                logger.warning(f"Đang xóa object cũ và thử tạo lại: {table_name}")
                                try:
                                    with engine.connect() as conn:
                                        # Xóa tất cả objects liên quan
                                        conn.execute(text(f"DROP INDEX IF EXISTS ix_{table_name}_id CASCADE"))
                                        conn.execute(text(f"DROP INDEX IF EXISTS ix_{table_name}_email CASCADE"))
                                        conn.commit()
                                    # Thử tạo lại
                                    table.create(bind=engine, checkfirst=True)
                                    logger.info(f"  [OK] Da tao bang: {table_name} (sau khi xoa orphan objects)")
                                    created_count += 1
                                except Exception as retry_err:
                                    logger.error(f"  [FAIL] Khong the tao bang {table_name}: {str(retry_err)}")
                            elif "UndefinedTable" in error_msg:
                                # FK reference chưa tồn tại - sẽ thử lại sau
                                logger.warning(f"  [WAIT] Cho FK dependency: {table_name}")
                            else:
                                logger.error(f"  [FAIL] Loi tao bang {table_name}: {error_msg}")
            
            if created_count > 0:
                logger.info(f"[OK] Da tao thanh cong {created_count} bang moi")
            else:
                logger.info("[OK] Khong co bang moi nao duoc tao (co the da ton tai)")
        else:
            logger.info("[OK] Tat ca bang da ton tai, khong tao bang moi")

        # Verify kết quả
        inspector = inspect(engine)
        new_tables = set(inspector.get_table_names())
        created_tables = new_tables - existing_tables
        still_missing = defined_tables - new_tables

        if created_tables:
            logger.info(f"[OK] Ket qua: Da tao cac bang: {list(created_tables)}")
        
        if still_missing:
            logger.warning(f"[WARN] Van con thieu cac bang: {list(still_missing)}")
            logger.warning("   Vui lòng kiểm tra init.sql hoặc tạo bảng thủ công")
        else:
            logger.info("[OK] Database schema verification complete")

        return True

    except Exception as e:
        logger.error(f"Lỗi khởi tạo database: {str(e)}")
        # Không raise để app vẫn chạy tiếp
        return False


def test_connection():
    """Test kết nối database"""
    from sqlalchemy import text
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        logger.info("Database connection test: SUCCESS")
        return True
    except Exception as e:
        logger.error(f"Database connection test: FAILED - {str(e)}")
        return False


# ==================== UTILITY FUNCTIONS ====================

def get_or_create_default_roles(db: Session):
    """Tạo các roles mặc định nếu chưa có"""
    default_roles = [
        {"id": 1, "role_name": "admin"},
        {"id": 2, "role_name": "moderator"},
        {"id": 3, "role_name": "user"}
    ]
    
    for role_data in default_roles:
        existing = db.query(Role).filter(Role.id == role_data["id"]).first()
        if not existing:
            role = Role(**role_data)
            db.add(role)
    
    db.commit()
    logger.info("Default roles ensured")


def create_admin_user(email: str, password: str, full_name: str = "Admin"):
    """Tạo admin user mặc định (nếu chưa có)"""
    from middleware.auth import auth_middleware

    db = SessionLocal()
    try:
        # Ensure default roles exist
        get_or_create_default_roles(db)
        
        # Kiểm tra admin đã tồn tại chưa
        existing_admin = db.query(User).filter(User.email == email).first()
        if existing_admin:
            logger.info(f"Admin user already exists: {email}")
            return existing_admin

        # Tạo admin mới
        admin = User(
            full_name=full_name,
            email=email,
            password_hash=auth_middleware.hash_password(password),
            role_id=1,  # admin role
            is_active=True
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        logger.info(f"Admin user created: {email}")
        return admin

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating admin user: {str(e)}")
        raise
    finally:
        db.close()
