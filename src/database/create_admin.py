"""
Script tạo tài khoản Admin

Script này giúp tạo tài khoản admin mới trong database PostgreSQL.
Password sẽ được hash bằng bcrypt giống như trong auth_service.py

Usage:
    python create_admin.py
"""

import sys
import os
from pathlib import Path
import bcrypt
import psycopg2
from datetime import datetime

# Add backend to path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

# PostgreSQL Configuration
PG_CONFIG = {
    "host": os.getenv("PG_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5433)),
    "database": os.getenv("POSTGRES_DB", "travel_db"),
    "user": os.getenv("POSTGRES_USER", "admin"),
    "password": os.getenv("POSTGRES_PASSWORD", "123456")
}


def hash_password(password: str) -> str:
    """
    Hash password using bcrypt (same as auth_middleware)
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def create_admin_user(full_name: str, email: str, password: str):
    """
    Tạo tài khoản admin trong database
    
    Args:
        full_name: Tên đầy đủ của admin
        email: Email của admin
        password: Password (plain text - sẽ được hash tự động)
    """
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        
        # Hash password
        password_hash = hash_password(password)
        
        # Check if email already exists
        cursor.execute("SELECT id, email FROM users WHERE email = %s", (email,))
        existing = cursor.fetchone()
        
        if existing:
            print(f"❌ Email '{email}' đã tồn tại trong database (User ID: {existing[0]})")
            return False
        
        # Insert admin user
        # role_id = 1 là admin (theo init.sql)
        current_time = datetime.utcnow()
        
        cursor.execute("""
            INSERT INTO users (
                full_name, 
                email, 
                password_hash, 
                role_id, 
                is_active, 
                reputation_score,
                created_at,
                updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            full_name,
            email,
            password_hash,
            1,  # role_id = 1 là admin
            True,  # is_active
            100,  # reputation_score cao hơn user thường
            current_time,
            current_time
        ))
        
        user_id = cursor.fetchone()[0]
        conn.commit()
        
        print(f"✅ Đã tạo tài khoản admin thành công!")
        print(f"   ID: {user_id}")
        print(f"   Tên: {full_name}")
        print(f"   Email: {email}")
        print(f"   Role: admin (role_id=1)")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Lỗi database: {e}")
        return False
    except Exception as e:
        print(f"❌ Lỗi không xác định: {e}")
        return False


def main():
    """Hàm chính"""
    print("=" * 60)
    print("🔧 TẠO TÀI KHOẢN ADMIN")
    print("=" * 60)
    print()
    
    # Nhập thông tin admin
    print("Nhập thông tin tài khoản admin:")
    full_name = input("  Tên đầy đủ: ").strip()
    email = input("  Email: ").strip()
    password = input("  Password: ").strip()
    
    # Validate input
    if not full_name or not email or not password:
        print("❌ Vui lòng nhập đầy đủ thông tin!")
        return
    
    if '@' not in email:
        print("❌ Email không hợp lệ!")
        return
    
    if len(password) < 6:
        print("❌ Password phải có ít nhất 6 ký tự!")
        return
    
    # Confirm
    print()
    print("Xác nhận thông tin:")
    print(f"  Tên: {full_name}")
    print(f"  Email: {email}")
    print(f"  Password: {'*' * len(password)}")
    print()
    
    confirm = input("Tạo tài khoản admin này? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("❌ Đã hủy!")
        return
    
    # Create admin
    print()
    create_admin_user(full_name, email, password)
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
