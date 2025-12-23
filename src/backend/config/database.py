"""
Cấu hình Database cho PostgreSQL

Module này xử lý kết nối và quản lý database PostgreSQL,
cung cấp session và engine cho SQLAlchemy ORM.
"""

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, Float, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)

# Database URL të environment variables
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/hanoi_travel"
)

# T¡o SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # KiÃm tra k¿t nÑi tr°Ûc khi sí dång
    pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
    max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20")),
    pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30")),
    pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "3600")),
    echo=os.getenv("DEBUG", "false").lower() == "true"  # Log SQL queries trong debug mode
)

# T¡o SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class cho models
Base = declarative_base()


# ==================== MODELS ====================

class User(Base):
    """
    Model User - Thông tin ng°Ýi dùng

    L°u trï thông tin ng°Ýi dùng trong hÇ thÑng Hanoi Travel
    """

    __tablename__ = "users"

    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Thông tin c¡ b£n
    full_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    # Thông tin bÕ sung
    phone = Column(String(15), nullable=True)
    avatar = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)

    # Role và Status
    role = Column(String(20), nullable=False, default="user")  # user, admin, moderator
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False)  # Email verification

    # Reputation score
    reputation_score = Column(Float, default=0.0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"

    def to_dict(self, include_sensitive: bool = False) -> dict:
        """
        ChuyÃn Õi user object sang dictionary

        Args:
            include_sensitive: Có bao gÓm thông tin nh¡y c£m không

        Returns:
            dict: Thông tin user
        """
        data = {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email if include_sensitive else None,
            "phone": self.phone,
            "avatar": self.avatar,
            "bio": self.bio,
            "role": self.role,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "reputation_score": self.reputation_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }
        return data

    def to_compact_dict(self) -> dict:
        """
        ChuyÃn Õi sang compact format cho responses

        Returns:
            dict: Compact user info
        """
        return {
            "id": self.id,
            "full_name": self.full_name,
            "avatar_url": self.avatar,
            "role_id": 1 if self.role == "admin" else (2 if self.role == "moderator" else 3)
        }


# ==================== DATABASE DEPENDENCIES ====================

def get_db() -> Session:
    """
    Dependency Ã l¥y database session

    Sí dång trong FastAPI endpoints:
    @app.get("/users/{user_id}")
    def get_user(user_id: int, db: Session = Depends(get_db)):
        ...

    Yields:
        Session: Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Khßi t¡o database - T¡o t¥t c£ tables

    Hàm này nên °ãc gÍi khi éng dång khßi Ùng
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise


def test_connection():
    """
    Test kết nối database

    Returns:
        bool: True nếu kết nối thành công
    """
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

def create_admin_user(email: str, password: str, full_name: str = "Admin"):
    """
    T¡o admin user m·c Ënh (n¿u ch°a có)

    Args:
        email: Email cça admin
        password: M­t kh©u
        full_name: Tên §y ç

    Returns:
        User: Admin user vëa t¡o ho·c ã tÓn t¡i
    """
    from ..middleware.auth import auth_middleware

    db = SessionLocal()
    try:
        # KiÃm tra admin ã tÓn t¡i ch°a
        existing_admin = db.query(User).filter(User.email == email).first()
        if existing_admin:
            logger.info(f"Admin user already exists: {email}")
            return existing_admin

        # T¡o admin mÛi
        admin = User(
            full_name=full_name,
            email=email,
            password_hash=auth_middleware.hash_password(password),
            role="admin",
            is_active=True,
            is_verified=True
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
