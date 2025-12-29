"""
╔══════════════════════════════════════════════════════════════════╗
║          HANOI TRAVEL - MONGODB DATA GENERATOR                   ║
║                                                                   ║
║  Script để khởi tạo và sinh dữ liệu cho MongoDB collections      ║
║  Thiết kế: Hybrid SQL (PostgreSQL) + NoSQL (MongoDB)             ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import random
import time
import uuid
import requests
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import numpy as np

# MongoDB
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, OperationFailure

# PostgreSQL
import psycopg2
from psycopg2.extras import RealDictCursor

# Google Gemini AI
import google.generativeai as genai

# Image scraping - Bing Image Downloader
from bing_image_downloader import downloader
import shutil

# Load environment variables
from dotenv import load_dotenv

# Load .env file from src directory
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

# ============================================================
# CONFIGURATION
# ============================================================

# MongoDB Atlas Connection
MONGO_URI = os.getenv("MONGO_URI_ATLAS", "mongodb+srv://ocococ2005:123456aA@webserver.lyvsqx8.mongodb.net/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "hanoi_travel_mongo")

# PostgreSQL Connection - Đọc từ .env
# Khi chạy NGOÀI Docker: host=localhost, port=5433
# Khi chạy TRONG Docker: host=db, port=5432
PG_CONFIG = {
    "host": os.getenv("PG_HOST", "localhost"),  # Mặc định localhost khi chạy ngoài Docker
    "port": int(os.getenv("DB_PORT", 5433)),    # Port được map ra ngoài
    "database": os.getenv("POSTGRES_DB", "travel_db"),
    "user": os.getenv("POSTGRES_USER", "admin"),
    "password": os.getenv("POSTGRES_PASSWORD", "123456")
}

# Gemini AI Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBZiRpUz9E6EjA_bVNBJXvY8RVQC8n0wCQ")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")  # Model mới nhất
GEMINI_DELAY_SECONDS = 4  # Delay between API calls to avoid rate limit

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOADS_DIR = BASE_DIR / "uploads" / "posts"

# ============================================================
# VIETNAMESE COMMENTS POOL
# ============================================================

VIETNAMESE_COMMENTS = [
    "Địa điểm này đẹp quá! Mình rất thích!",
    "Cảm ơn bạn đã chia sẻ, rất hữu ích!",
    "Mình đã đến đây rồi, đúng là tuyệt vời!",
    "Lần sau mình sẽ ghé thăm nơi này",
    "Ảnh đẹp quá, chụp bằng điện thoại gì vậy?",
    "Thức ăn ở đây có ngon không bạn?",
    "Giá cả có đắt lắm không ạ?",
    "Mình bookmark lại để cuối tuần đi",
    "Đi vào mùa nào đẹp nhất vậy bạn?",
    "Cảnh quan ở đây thật sự rất ấn tượng",
    "Bạn đi một mình hay đi cùng gia đình?",
    "Có chỗ đậu xe không bạn ơi?",
    "Mình cũng muốn đến đây quá!",
    "Review rất chi tiết, cảm ơn bạn!",
    "Thời điểm nào trong ngày đẹp nhất?",
    "Có nên đặt vé trước không bạn?",
    "Mình thấy nơi này rất phù hợp để chụp ảnh",
    "Đồ ăn ở đây có nhiều lựa chọn không?",
    "Nhân viên phục vụ có thân thiện không?",
    "Mình sẽ giới thiệu cho bạn bè biết!",
    "Đường đi có khó tìm không bạn?",
    "Trẻ em có được vào không ạ?",
    "Thời tiết hôm đó có đẹp không?",
    "Bạn ở lại bao lâu?",
    "Có wifi miễn phí không bạn?",
    "Nơi này có phù hợp cho người già không?",
    "Mình cũng đang lên kế hoạch đi đây",
    "Cảm giác thật bình yên và thư giãn",
    "Đã follow bạn để xem thêm review!",
    "Bạn có thể chia sẻ thêm địa chỉ chi tiết không?",
    "Hay quá! Mình phải đi ngay thôi!",
    "Ảnh chụp đẹp quá, mình thích góc này!",
    "Không khí ở đây có trong lành không?",
    "Mình nghe nói nơi này rất nổi tiếng",
    "Có tour hướng dẫn không bạn?",
    "Thật sự rất đáng để đến thăm!",
    "Bạn có tips gì cho người mới đến không?",
    "Nên đi vào buổi sáng hay chiều?",
    "Mình sẽ rủ cả nhà đi cuối tuần này",
    "Có nhà vệ sinh công cộng không bạn?"
]

# ============================================================
# DATABASE CONNECTIONS
# ============================================================

def get_mongo_client() -> MongoClient:
    """Kết nối MongoDB Atlas"""
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # Test connection
        client.admin.command('ping')
        return client
    except ConnectionFailure as e:
        print(f"❌ Không thể kết nối MongoDB: {e}")
        raise

def get_postgres_connection():
    """Kết nối PostgreSQL"""
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        return conn
    except Exception as e:
        print(f"❌ Không thể kết nối PostgreSQL: {e}")
        raise

# ============================================================
# GEMINI AI
# ============================================================

def setup_gemini():
    """Cấu hình Gemini AI"""
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel(GEMINI_MODEL)

def generate_post_content(model, place_name: str, place_description: str, place_type: str) -> Tuple[str, str]:
    """
    Sinh nội dung bài viết bằng Gemini AI
    Returns: (title, content)
    """
    prompt = f"""Bạn là một du khách Việt Nam vừa đến thăm địa điểm "{place_name}" ở Hà Nội.
    
Thông tin về địa điểm:
- Tên: {place_name}
- Loại: {place_type}
- Mô tả: {place_description}

Hãy viết một bài review ngắn gọn (150-250 từ) dưới góc nhìn của một du khách thực sự. Bài viết cần:
1. Có tiêu đề hấp dẫn (1 dòng)
2. Chia sẻ trải nghiệm cá nhân
3. Đề cập đến điểm ấn tượng
4. Đưa ra lời khuyên cho người muốn đến
5. Viết tự nhiên, không quá quảng cáo

Format output:
TIÊU ĐỀ: [tiêu đề bài viết]
NỘI DUNG: [nội dung bài viết]"""

    try:
        response = model.generate_content(prompt)
        text = response.text
        
        # Parse title and content
        title_match = re.search(r'TIÊU ĐỀ:\s*(.+?)(?=NỘI DUNG:|$)', text, re.DOTALL)
        content_match = re.search(r'NỘI DUNG:\s*(.+)', text, re.DOTALL)
        
        title = title_match.group(1).strip() if title_match else f"Review {place_name}"
        content = content_match.group(1).strip() if content_match else text
        
        return title, content
    except Exception as e:
        print(f"⚠️ Lỗi Gemini API: {e}")
        # Fallback content
        return (
            f"Trải nghiệm tuyệt vời tại {place_name}",
            f"Hôm nay mình đã có dịp ghé thăm {place_name}. Đây thực sự là một điểm đến không thể bỏ qua khi đến Hà Nội. {place_description} Mình rất ấn tượng với không gian và dịch vụ ở đây. Recommend mọi người nên đến thử!"
        )

# ============================================================
# IMAGE SCRAPING - BING IMAGE DOWNLOADER
# ============================================================

# Temporary download directory
TEMP_DOWNLOAD_DIR = Path(__file__).resolve().parent / "temp_download"

# Paraphrase templates for retry when images not found
SEARCH_TEMPLATES = [
    "{place_name} Hanoi Vietnam tourism",
    "{place_name} Hà Nội scenery",
    "{place_name} Vietnam travel photography",
    "địa điểm {place_name} Hà Nội đẹp",
    "{place_name} Vietnam beautiful landscape",
]

def scrape_images_for_place(place_name: str, place_id: int, user_id: int, num_images: int = 2) -> List[str]:
    """
    Cào ảnh từ Bing Image Search dựa trên tên địa điểm
    Sử dụng bing_image_downloader với cơ chế retry
    Returns: List of saved image paths (relative for DB storage)
    """
    saved_paths = []
    
    # Tạo thư mục nếu chưa tồn tại
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"   📷 Đang tải {num_images} ảnh cho '{place_name}'...")
    
    # Thử với các search query khác nhau cho đến khi đủ ảnh
    for template_idx, template in enumerate(SEARCH_TEMPLATES):
        if len(saved_paths) >= num_images:
            break
            
        search_query = template.format(place_name=place_name)
        
        # Số ảnh còn thiếu
        remaining = num_images - len(saved_paths)
        
        if template_idx > 0:
            print(f"      🔄 Retry với query: '{search_query[:40]}...'")
        
        try:
            # Xóa thư mục tạm nếu tồn tại
            if TEMP_DOWNLOAD_DIR.exists():
                shutil.rmtree(TEMP_DOWNLOAD_DIR)
            
            # Tải ảnh vào thư mục tạm
            downloader.download(
                search_query,
                limit=remaining + 2,  # Tải thêm một chút để có dư
                output_dir=str(TEMP_DOWNLOAD_DIR),
                adult_filter_off=True,
                force_replace=False,
                timeout=10,
                verbose=False
            )
            
            # Tìm thư mục chứa ảnh đã tải
            downloaded_folder = TEMP_DOWNLOAD_DIR / search_query
            
            if downloaded_folder.exists():
                # Lọc chỉ lấy file jpg/png với kích thước > 10KB (ảnh thật)
                valid_extensions = ('.jpg', '.jpeg', '.png')
                files = [
                    f for f in downloaded_folder.iterdir() 
                    if f.suffix.lower() in valid_extensions and f.stat().st_size > 10000
                ]
                
                # Di chuyển ảnh vào thư mục uploads
                for file in files:
                    if len(saved_paths) >= num_images:
                        break
                    
                    # Xác định extension
                    ext = file.suffix.lower()
                    if ext == '.jpeg':
                        ext = '.jpg'
                    
                    # Format tên file: {userid}_{placeid}_{index}.jpg
                    img_index = len(saved_paths)
                    new_filename = f"{user_id}_{place_id}_{img_index}{ext}"
                    dest_path = UPLOADS_DIR / new_filename
                    
                    try:
                        # Copy file (không dùng move vì có thể bị lock)
                        shutil.copy2(file, dest_path)
                        
                        # Verify file
                        if dest_path.exists() and dest_path.stat().st_size > 10000:
                            db_path = f"static/uploads/posts/{new_filename}"
                            saved_paths.append(db_path)
                            size_kb = dest_path.stat().st_size // 1024
                            print(f"      ✅ Đã lưu: {new_filename} ({size_kb}KB)")
                    except Exception as e:
                        print(f"      ⚠️ Không thể lưu {file.name}: {str(e)[:30]}")
            
        except Exception as e:
            print(f"      ⚠️ Lỗi tải ảnh: {str(e)[:50]}")
        
        # Cleanup temp folder
        try:
            if TEMP_DOWNLOAD_DIR.exists():
                shutil.rmtree(TEMP_DOWNLOAD_DIR)
        except:
            pass
        
        time.sleep(0.5)  # Delay giữa các query
    
    # Thông báo kết quả
    if len(saved_paths) < num_images:
        print(f"      ⚠️ Chỉ tải được {len(saved_paths)}/{num_images} ảnh")
    
    return saved_paths

# ============================================================
# DATA FETCHING FROM POSTGRESQL
# ============================================================

def fetch_users() -> List[Dict]:
    """Lấy danh sách users từ PostgreSQL"""
    conn = get_postgres_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id, full_name, email FROM users WHERE is_active = true")
            users = cur.fetchall()
            return [dict(u) for u in users]
    finally:
        conn.close()

def fetch_places() -> List[Dict]:
    """Lấy danh sách places từ PostgreSQL"""
    conn = get_postgres_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT p.id, p.name, p.description, pt.name as place_type
                FROM places p
                JOIN place_types pt ON p.place_type_id = pt.id
                WHERE p.deleted_at IS NULL
            """)
            places = cur.fetchall()
            return [dict(p) for p in places]
    finally:
        conn.close()

# ============================================================
# OPTION 1: INITIALIZE DATABASE & COLLECTIONS
# ============================================================

def init_database():
    """Khởi tạo database và collections với indexes"""
    print("\n" + "="*60)
    print("🚀 KHỞI TẠO DATABASE & COLLECTIONS")
    print("="*60)
    
    client = get_mongo_client()
    db = client[MONGO_DB_NAME]
    
    # Collection definitions with indexes
    collections_config = {
        "posts_mongo": [
            ("author_id", ASCENDING),
            ("related_place_id", ASCENDING),
            ("status", ASCENDING),
            ("created_at", DESCENDING),
            ("type", ASCENDING),
        ],
        "post_likes_mongo": [
            ("post_id", ASCENDING),
            ("user_id", ASCENDING),
            [("post_id", ASCENDING), ("user_id", ASCENDING)],  # Compound unique
        ],
        "post_comments_mongo": [
            ("post_id", ASCENDING),
            ("user_id", ASCENDING),
            ("parent_id", ASCENDING),
            ("created_at", DESCENDING),
        ],
        "reports_mongo": [
            ("target_type", ASCENDING),
            ("target_id", ASCENDING),
            ("reporter_id", ASCENDING),
            ("created_at", DESCENDING),
        ],
        "chatbot_logs_mongo": [
            ("conversation_id", ASCENDING),
            ("user_id", ASCENDING),
            ("created_at", DESCENDING),
        ]
    }
    
    for collection_name, indexes in collections_config.items():
        print(f"\n📁 Tạo collection: {collection_name}")
        
        # Tạo collection (nếu chưa tồn tại)
        if collection_name not in db.list_collection_names():
            db.create_collection(collection_name)
            print(f"   ✅ Đã tạo collection")
        else:
            print(f"   ℹ️ Collection đã tồn tại")
        
        # Tạo indexes
        collection = db[collection_name]
        for idx in indexes:
            try:
                if isinstance(idx, list):
                    # Compound index
                    collection.create_index(idx, unique=True)
                    print(f"   📇 Index compound: {idx}")
                else:
                    collection.create_index([(idx[0], idx[1])])
                    print(f"   📇 Index: {idx[0]}")
            except Exception as e:
                print(f"   ⚠️ Index có thể đã tồn tại: {e}")
    
    print("\n" + "="*60)
    print("✅ KHỞI TẠO HOÀN TẤT!")
    print("="*60)
    
    client.close()

# ============================================================
# OPTION 2: GENERATE DATA
# ============================================================

def generate_data(num_posts: int, num_comments: int, total_likes: int, images_per_post: int = 2):
    """Sinh dữ liệu cho posts, likes, comments"""
    print("\n" + "="*60)
    print("🔄 SINH DỮ LIỆU")
    print("="*60)
    
    # Kết nối databases
    client = get_mongo_client()
    db = client[MONGO_DB_NAME]
    
    # Setup Gemini
    print("\n⚙️ Đang kết nối Gemini AI...")
    gemini_model = setup_gemini()
    
    # Fetch data from PostgreSQL
    print("📊 Đang lấy dữ liệu từ PostgreSQL...")
    users = fetch_users()
    places = fetch_places()
    
    if not users:
        print("❌ Không tìm thấy users trong PostgreSQL!")
        return
    if not places:
        print("❌ Không tìm thấy places trong PostgreSQL!")
        return
    
    print(f"   → {len(users)} users")
    print(f"   → {len(places)} places")
    
    # Collections
    posts_col = db["posts_mongo"]
    likes_col = db["post_likes_mongo"]
    comments_col = db["post_comments_mongo"]
    
    # -------------------- GENERATE POSTS --------------------
    print(f"\n📝 Đang tạo {num_posts} bài viết...")
    created_posts = []
    
    for i in range(num_posts):
        user = random.choice(users)
        place = random.choice(places)
        
        print(f"\n   [{i+1}/{num_posts}] Đang tạo bài viết về '{place['name']}'...")
        
        # Generate content with Gemini
        title, content = generate_post_content(
            gemini_model,
            place['name'],
            place['description'] or "Một địa điểm thú vị tại Hà Nội",
            place['place_type']
        )
        
        # Scrape images using Bing Image Downloader
        images = scrape_images_for_place(
            place['name'],
            place['id'],
            user['id'],
            num_images=images_per_post
        )
        
        # Create post document
        post_id = str(uuid.uuid4())
        post_type = random.choice(['post', 'review'])
        rating = round(random.uniform(3.5, 5.0), 1) if post_type == 'review' else None
        
        tags = random.sample([
            "hanoi", "dulich", "amthuc", "checkin", "travel", 
            "vietnam", "photography", "foodie", "explore"
        ], k=random.randint(2, 4))
        
        created_at = datetime.now() - timedelta(days=random.randint(0, 30))
        
        post = {
            "_id": post_id,
            "type": post_type,
            "author_id": user['id'],
            "related_place_id": place['id'],
            "title": title,
            "content": content,
            "rating": rating,
            "tags": tags,
            "images": images,
            "likes_count": 0,  # Will be updated later
            "comments_count": 0,  # Will be updated later
            "status": "approved",
            "created_at": created_at,
            "updated_at": created_at
        }
        
        posts_col.insert_one(post)
        created_posts.append(post)
        print(f"   ✅ Đã tạo bài viết: {title[:50]}...")
        
        # Delay to avoid rate limit
        if i < num_posts - 1:
            print(f"   ⏳ Đợi {GEMINI_DELAY_SECONDS}s để tránh rate limit...")
            time.sleep(GEMINI_DELAY_SECONDS)
    
    # -------------------- GENERATE LIKES --------------------
    print(f"\n❤️ Đang phân phối {total_likes} likes (phân phối chuẩn)...")
    
    if created_posts:
        # Phân phối likes theo phân phối chuẩn
        # Một số bài có nhiều likes, đa số có ít hơn
        likes_distribution = np.random.normal(
            loc=total_likes / len(created_posts),
            scale=total_likes / (len(created_posts) * 2),
            size=len(created_posts)
        )
        likes_distribution = np.abs(likes_distribution).astype(int)
        
        # Normalize để tổng = total_likes
        likes_distribution = (likes_distribution / likes_distribution.sum() * total_likes).astype(int)
        
        total_created_likes = 0
        
        for post, num_likes in zip(created_posts, likes_distribution):
            # Lấy random users để like (không trùng)
            available_users = [u for u in users if u['id'] != post['author_id']]
            liking_users = random.sample(available_users, min(num_likes, len(available_users)))
            
            for user in liking_users:
                like = {
                    "_id": str(uuid.uuid4()),
                    "post_id": post['_id'],
                    "user_id": user['id'],
                    "created_at": post['created_at'] + timedelta(hours=random.randint(1, 72))
                }
                try:
                    likes_col.insert_one(like)
                    total_created_likes += 1
                except:
                    pass  # Skip duplicates
            
            # Update likes_count in post
            posts_col.update_one(
                {"_id": post['_id']},
                {"$set": {"likes_count": len(liking_users)}}
            )
        
        print(f"   ✅ Đã tạo {total_created_likes} likes")
    
    # -------------------- GENERATE COMMENTS --------------------
    print(f"\n💬 Đang tạo {num_comments} comments gốc...")
    
    if created_posts:
        comments_per_post = max(1, num_comments // len(created_posts))
        total_created_comments = 0
        
        for post in created_posts:
            # Random number of comments for this post
            n_comments = random.randint(
                max(1, comments_per_post - 2),
                comments_per_post + 3
            )
            
            for _ in range(n_comments):
                if total_created_comments >= num_comments:
                    break
                
                # Random user (not the author)
                available_users = [u for u in users if u['id'] != post['author_id']]
                user = random.choice(available_users)
                
                comment = {
                    "_id": str(uuid.uuid4()),
                    "post_id": post['_id'],
                    "user_id": user['id'],
                    "content": random.choice(VIETNAMESE_COMMENTS),
                    "parent_id": None,  # Root comment
                    "created_at": post['created_at'] + timedelta(hours=random.randint(1, 168))
                }
                
                comments_col.insert_one(comment)
                total_created_comments += 1
            
            # Update comments_count in post
            actual_count = comments_col.count_documents({"post_id": post['_id']})
            posts_col.update_one(
                {"_id": post['_id']},
                {"$set": {"comments_count": actual_count}}
            )
        
        print(f"   ✅ Đã tạo {total_created_comments} comments")
    
    print("\n" + "="*60)
    print("✅ SINH DỮ LIỆU HOÀN TẤT!")
    print(f"   📝 Posts: {len(created_posts)}")
    print(f"   ❤️ Likes: {total_created_likes}")
    print(f"   💬 Comments: {total_created_comments}")
    print("="*60)
    
    client.close()

# ============================================================
# OPTION 3: DELETE ALL DATA
# ============================================================

def delete_all_data():
    """Xóa toàn bộ dữ liệu trong tất cả collections"""
    print("\n" + "="*60)
    print("⚠️ XÓA TOÀN BỘ DỮ LIỆU")
    print("="*60)
    
    confirm = input("\n❓ Bạn có chắc chắn muốn xóa TẤT CẢ dữ liệu? (gõ 'YES' để xác nhận): ")
    
    if confirm != "YES":
        print("❌ Đã hủy thao tác xóa.")
        return
    
    client = get_mongo_client()
    db = client[MONGO_DB_NAME]
    
    collections = [
        "posts_mongo",
        "post_likes_mongo", 
        "post_comments_mongo",
        "reports_mongo",
        "chatbot_logs_mongo"
    ]
    
    for col_name in collections:
        if col_name in db.list_collection_names():
            result = db[col_name].delete_many({})
            print(f"   🗑️ {col_name}: {result.deleted_count} documents đã xóa")
        else:
            print(f"   ℹ️ {col_name}: collection không tồn tại")
    
    # Optional: Delete uploaded images
    delete_images = input("\n❓ Có muốn xóa cả ảnh đã upload? (y/n): ").lower()
    if delete_images == 'y':
        if UPLOADS_DIR.exists():
            import shutil
            shutil.rmtree(UPLOADS_DIR)
            UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
            print("   🗑️ Đã xóa tất cả ảnh trong uploads/posts/")
    
    print("\n" + "="*60)
    print("✅ XÓA DỮ LIỆU HOÀN TẤT!")
    print("="*60)
    
    client.close()

# ============================================================
# MAIN MENU
# ============================================================

def print_menu():
    """In menu chính"""
    print("\n")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║       HANOI TRAVEL - MONGODB DATA GENERATOR              ║")
    print("╠══════════════════════════════════════════════════════════╣")
    print("║  1. Khởi tạo Database & Collections                      ║")
    print("║  2. Sinh dữ liệu (posts, likes, comments)                ║")
    print("║  3. Xóa sạch Database                                    ║")
    print("║  0. Thoát                                                ║")
    print("╚══════════════════════════════════════════════════════════╝")

def main():
    """Hàm chính"""
    print("\n" + "="*60)
    print("🌟 WELCOME TO HANOI TRAVEL MONGODB DATA GENERATOR 🌟")
    print("="*60)
    print(f"📍 MongoDB: {MONGO_DB_NAME}")
    print(f"📍 PostgreSQL: {PG_CONFIG['database']}@{PG_CONFIG['host']}:{PG_CONFIG['port']}")
    print(f"📍 Gemini Model: {GEMINI_MODEL}")
    
    while True:
        print_menu()
        choice = input("\n👉 Chọn chức năng (0-3): ").strip()
        
        if choice == "1":
            init_database()
            
        elif choice == "2":
            print("\n📋 NHẬP THÔNG SỐ SINH DỮ LIỆU:")
            try:
                num_posts = int(input("   Số lượng bài viết (posts): "))
                total_images = int(input("   Tổng số ảnh cần cào (chia đều cho posts): "))
                num_comments = int(input("   Số lượng comments gốc: "))
                total_likes = int(input("   Tổng số likes (phân phối chuẩn): "))
                
                if num_posts <= 0 or num_comments <= 0 or total_likes <= 0 or total_images <= 0:
                    print("❌ Số lượng phải lớn hơn 0!")
                    continue
                
                # Tính số ảnh mỗi bài
                images_per_post = max(1, total_images // num_posts)
                print(f"\n   📊 Phân phối: ~{images_per_post} ảnh/bài viết")
                
                generate_data(num_posts, num_comments, total_likes, images_per_post)
                
            except ValueError:
                print("❌ Vui lòng nhập số hợp lệ!")
                
        elif choice == "3":
            delete_all_data()
            
        elif choice == "0":
            print("\n👋 Tạm biệt! Hẹn gặp lại!")
            break
            
        else:
            print("❌ Lựa chọn không hợp lệ! Vui lòng chọn 0-3.")

if __name__ == "__main__":
    main()
