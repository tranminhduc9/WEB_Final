"""
╔══════════════════════════════════════════════════════════════════╗
║          HANOI TRAVEL - IMAGE CRAWLER TOOL                       ║
║                                                                   ║
║  Công cụ cào ảnh cho địa điểm (places) và avatar người dùng      ║
║  Sử dụng: Bing Image Downloader                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os
import shutil
from pathlib import Path
from bing_image_downloader import downloader
from sqlalchemy import create_engine, text
import pandas as pd
import random

# ============================================================
# CONFIGURATION
# ============================================================

# Database connection (local PostgreSQL - port 5432)
DB_CONNECTION_STR = 'postgresql://postgres:123456@localhost:5432/postgres'

# Paths
BASE_DIR = Path(__file__).resolve().parent / "src"
PLACES_IMAGE_DIR = BASE_DIR / "uploads" / "places"
AVATARS_IMAGE_DIR = BASE_DIR / "uploads" / "avatars"
TEMP_DOWNLOAD_DIR = Path(__file__).resolve().parent / "temp_download"

# DB path prefixes
DB_PLACES_PATH_PREFIX = '/static/uploads/places/'
DB_AVATARS_PATH_PREFIX = 'static/uploads/avatars/'

# Create directories if not exist
PLACES_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
AVATARS_IMAGE_DIR.mkdir(parents=True, exist_ok=True)

# Database engine
engine = create_engine(DB_CONNECTION_STR)

# ============================================================
# SEARCH TEMPLATES FOR PLACES
# ============================================================

# Template cho ảnh đầu tiên (overview/outside view)
FIRST_IMAGE_TEMPLATES = [
    "{place_name} Hanoi overview panorama",
    "{place_name} Hà Nội toàn cảnh",
    "{place_name} entrance outside view",
    "{place_name} Vietnam landmark aerial",
    "{place_name} sign board exterior",
]

# Template cho các ảnh còn lại
OTHER_IMAGE_TEMPLATES = [
    "{place_name} Hanoi Vietnam tourism",
    "{place_name} Hà Nội scenery",
    "{place_name} Vietnam travel photography",
    "địa điểm {place_name} Hà Nội đẹp",
    "{place_name} Vietnam beautiful landscape",
]

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def cleanup_temp():
    """Xóa thư mục tạm"""
    try:
        if TEMP_DOWNLOAD_DIR.exists():
            shutil.rmtree(TEMP_DOWNLOAD_DIR)
    except:
        pass

def download_images_with_retry(search_templates: list, place_name: str, num_images: int) -> list:
    """
    Tải ảnh với cơ chế retry sử dụng các template khác nhau
    Returns: List of downloaded file paths
    """
    downloaded_files = []
    
    for template in search_templates:
        if len(downloaded_files) >= num_images:
            break
            
        search_query = template.format(place_name=place_name)
        remaining = num_images - len(downloaded_files)
        
        try:
            cleanup_temp()
            
            downloader.download(
                search_query,
                limit=remaining + 2,
                output_dir=str(TEMP_DOWNLOAD_DIR),
                adult_filter_off=True,
                force_replace=False,
                timeout=10,
                verbose=False
            )
            
            downloaded_folder = TEMP_DOWNLOAD_DIR / search_query
            
            if downloaded_folder.exists():
                valid_extensions = ('.jpg', '.jpeg', '.png')
                files = [
                    f for f in downloaded_folder.iterdir()
                    if f.suffix.lower() in valid_extensions and f.stat().st_size > 10000
                ]
                downloaded_files.extend(files[:remaining])
                
        except Exception as e:
            print(f"      ⚠️ Lỗi với query '{search_query[:30]}...': {str(e)[:30]}")
    
    # NOTE: Không cleanup ở đây - để caller copy xong rồi cleanup
    return downloaded_files

# ============================================================
# OPTION 1: RESET PLACE IMAGES
# ============================================================

def reset_place_images():
    """Reset bảng place_images và xóa ảnh trong folder"""
    print("\n" + "="*60)
    print("🗑️ RESET PLACE IMAGES")
    print("="*60)
    
    confirm = input("\n❓ Bạn có chắc chắn muốn xóa TẤT CẢ ảnh địa điểm? (gõ 'YES'): ")
    
    if confirm != "YES":
        print("❌ Đã hủy thao tác.")
        return
    
    # Xóa dữ liệu trong DB
    with engine.connect() as conn:
        print("\n📊 Đang xóa dữ liệu trong bảng place_images...")
        conn.execute(text("TRUNCATE TABLE place_images RESTART IDENTITY CASCADE;"))
        conn.commit()
        print("   ✅ Đã xóa dữ liệu trong DB")
    
    # Xóa files trong folder
    if PLACES_IMAGE_DIR.exists():
        file_count = len(list(PLACES_IMAGE_DIR.glob("*")))
        shutil.rmtree(PLACES_IMAGE_DIR)
        PLACES_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
        print(f"   ✅ Đã xóa {file_count} files trong {PLACES_IMAGE_DIR}")
    
    print("\n" + "="*60)
    print("✅ RESET HOÀN TẤT!")
    print("="*60)

# ============================================================
# OPTION 2: CRAWL PLACE IMAGES
# ============================================================

def crawl_place_images():
    """Cào ảnh cho địa điểm du lịch"""
    print("\n" + "="*60)
    print("📷 CÀO ẢNH ĐỊA ĐIỂM DU LỊCH")
    print("="*60)
    
    # Lấy danh sách places
    try:
        df_places = pd.read_sql("SELECT id, name FROM places ORDER BY id ASC", engine)
    except Exception as e:
        print(f"❌ Lỗi kết nối DB: {e}")
        return
    
    num_places = len(df_places)
    print(f"\n📊 Tìm thấy {num_places} địa điểm trong database")
    
    # Nhập số lượng ảnh
    try:
        total_images = int(input("\n   Nhập tổng số ảnh cần cào: "))
        if total_images <= 0:
            print("❌ Số lượng phải lớn hơn 0!")
            return
    except ValueError:
        print("❌ Vui lòng nhập số hợp lệ!")
        return
    
    # Tính số ảnh mỗi địa điểm
    images_per_place = max(1, total_images // num_places)
    extra_images = total_images % num_places
    
    print(f"\n   📊 Phân phối: ~{images_per_place} ảnh/địa điểm")
    print(f"   📊 {extra_images} địa điểm đầu sẽ có thêm 1 ảnh")
    
    confirm = input("\n   Bắt đầu cào ảnh? (y/n): ").lower()
    if confirm != 'y':
        print("❌ Đã hủy.")
        return
    
    print("\n" + "-"*60)
    
    with engine.connect() as conn:
        for index, row in df_places.iterrows():
            p_id = int(row['id'])  # Convert numpy.int64 to Python int
            p_name = row['name']
            
            # Số ảnh cho địa điểm này
            num_imgs = images_per_place + (1 if index < extra_images else 0)
            
            print(f"\n[{index+1}/{num_places}] 📍 {p_name} - Cào {num_imgs} ảnh...")
            
            saved_count = 0
            
            # ===== ẢNH ĐẦU TIÊN: Overview/Panorama =====
            if num_imgs >= 1:
                print(f"   🖼️ Tải ảnh toàn cảnh (overview)...")
                first_images = download_images_with_retry(
                    FIRST_IMAGE_TEMPLATES, 
                    p_name, 
                    num_images=1
                )
                
                if first_images:
                    file = first_images[0]
                    ext = file.suffix.lower()
                    if ext == '.jpeg':
                        ext = '.jpg'
                    
                    new_filename = f"place_{p_id}_0{ext}"
                    dest_path = PLACES_IMAGE_DIR / new_filename
                    
                    try:
                        shutil.copy2(file, dest_path)
                        db_url = f"{DB_PLACES_PATH_PREFIX}{new_filename}"
                        
                        sql = text("""
                            INSERT INTO place_images (place_id, image_url, is_main)
                            VALUES (:pid, :url, :main)
                        """)
                        conn.execute(sql, {"pid": p_id, "url": db_url, "main": True})
                        saved_count += 1
                        print(f"      ✅ Đã lưu: {new_filename} (main)")
                    except Exception as e:
                        print(f"      ⚠️ Lỗi lưu ảnh đầu: {str(e)[:30]}")
            
            # ===== CÁC ẢNH CÒN LẠI =====
            remaining_imgs = num_imgs - saved_count
            if remaining_imgs > 0:
                print(f"   🖼️ Tải {remaining_imgs} ảnh bổ sung...")
                other_images = download_images_with_retry(
                    OTHER_IMAGE_TEMPLATES,
                    p_name,
                    num_images=remaining_imgs
                )
                
                for i, file in enumerate(other_images):
                    ext = file.suffix.lower()
                    if ext == '.jpeg':
                        ext = '.jpg'
                    
                    img_index = saved_count + i
                    new_filename = f"place_{p_id}_{img_index}{ext}"
                    dest_path = PLACES_IMAGE_DIR / new_filename
                    
                    try:
                        shutil.copy2(file, dest_path)
                        db_url = f"{DB_PLACES_PATH_PREFIX}{new_filename}"
                        
                        sql = text("""
                            INSERT INTO place_images (place_id, image_url, is_main)
                            VALUES (:pid, :url, :main)
                        """)
                        conn.execute(sql, {"pid": p_id, "url": db_url, "main": False})
                        saved_count += 1
                        print(f"      ✅ Đã lưu: {new_filename}")
                    except Exception as e:
                        print(f"      ⚠️ Lỗi lưu: {str(e)[:30]}")
            
            # Commit sau mỗi địa điểm
            conn.commit()
            
            if saved_count < num_imgs:
                print(f"   ⚠️ Chỉ tải được {saved_count}/{num_imgs} ảnh")
            
            cleanup_temp()
    
    print("\n" + "="*60)
    print("✅ CÀO ẢNH ĐỊA ĐIỂM HOÀN TẤT!")
    print("="*60)

# ============================================================
# OPTION 3: RESET USER AVATARS
# ============================================================

def reset_user_avatars():
    """Reset avatar_url trong bảng users và xóa ảnh trong folder"""
    print("\n" + "="*60)
    print("🗑️ RESET USER AVATARS")
    print("="*60)
    
    confirm = input("\n❓ Bạn có chắc chắn muốn xóa TẤT CẢ avatar? (gõ 'YES'): ")
    
    if confirm != "YES":
        print("❌ Đã hủy thao tác.")
        return
    
    # Reset avatar_url trong DB
    with engine.connect() as conn:
        print("\n📊 Đang reset avatar_url trong bảng users...")
        result = conn.execute(text("UPDATE users SET avatar_url = NULL;"))
        conn.commit()
        print(f"   ✅ Đã reset {result.rowcount} users")
    
    # Xóa files trong folder
    if AVATARS_IMAGE_DIR.exists():
        file_count = len(list(AVATARS_IMAGE_DIR.glob("*")))
        shutil.rmtree(AVATARS_IMAGE_DIR)
        AVATARS_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
        print(f"   ✅ Đã xóa {file_count} files trong {AVATARS_IMAGE_DIR}")
    
    print("\n" + "="*60)
    print("✅ RESET HOÀN TẤT!")
    print("="*60)

# ============================================================
# OPTION 4: CRAWL USER AVATARS
# ============================================================

def crawl_user_avatars():
    """Cào avatar cho người dùng theo chủ đề"""
    print("\n" + "="*60)
    print("🎭 CÀO AVATAR NGƯỜI DÙNG")
    print("="*60)
    
    # Lấy số lượng users
    try:
        df_users = pd.read_sql("SELECT id FROM users ORDER BY id ASC", engine)
    except Exception as e:
        print(f"❌ Lỗi kết nối DB: {e}")
        return
    
    num_users = len(df_users)
    print(f"\n📊 Tìm thấy {num_users} users trong database")
    
    # Nhập thông tin
    try:
        total_avatars = int(input("\n   Nhập số lượng avatar cần cào: "))
        if total_avatars <= 0:
            print("❌ Số lượng phải lớn hơn 0!")
            return
    except ValueError:
        print("❌ Vui lòng nhập số hợp lệ!")
        return
    
    theme = input("   Nhập chủ đề avatar (vd: dragonball, doraemon, anime): ").strip()
    if not theme:
        print("❌ Chủ đề không được để trống!")
        return
    
    print(f"\n   🎯 Sẽ cào {total_avatars} avatar với chủ đề '{theme}'")
    
    confirm = input("\n   Bắt đầu cào ảnh? (y/n): ").lower()
    if confirm != 'y':
        print("❌ Đã hủy.")
        return
    
    print("\n" + "-"*60)
    
    # Search templates cho avatar
    avatar_templates = [
        f"{theme} character icon",
        f"{theme} avatar profile picture",
        f"{theme} chibi cute",
        f"{theme} cartoon character",
        f"{theme} anime style icon",
    ]
    
    # Cào ảnh
    print(f"\n📷 Đang cào {total_avatars} avatar...")
    
    saved_avatars = []
    
    for template in avatar_templates:
        if len(saved_avatars) >= total_avatars:
            break
        
        remaining = total_avatars - len(saved_avatars)
        search_query = template
        
        print(f"   🔍 Search: '{search_query[:40]}...' - cần {remaining} ảnh")
        
        try:
            cleanup_temp()
            
            downloader.download(
                search_query,
                limit=remaining + 5,
                output_dir=str(TEMP_DOWNLOAD_DIR),
                adult_filter_off=True,
                force_replace=False,
                timeout=10,
                verbose=False
            )
            
            downloaded_folder = TEMP_DOWNLOAD_DIR / search_query
            
            if downloaded_folder.exists():
                valid_extensions = ('.jpg', '.jpeg', '.png')
                files = [
                    f for f in downloaded_folder.iterdir()
                    if f.suffix.lower() in valid_extensions and f.stat().st_size > 5000
                ]
                
                for file in files:
                    if len(saved_avatars) >= total_avatars:
                        break
                    
                    ext = file.suffix.lower()
                    if ext == '.jpeg':
                        ext = '.jpg'
                    
                    avatar_num = len(saved_avatars) + 1
                    new_filename = f"avatar_{avatar_num}{ext}"
                    dest_path = AVATARS_IMAGE_DIR / new_filename
                    
                    try:
                        shutil.copy2(file, dest_path)
                        saved_avatars.append(new_filename)
                        print(f"      ✅ Đã lưu: {new_filename}")
                    except Exception as e:
                        print(f"      ⚠️ Lỗi: {str(e)[:30]}")
                        
        except Exception as e:
            print(f"      ⚠️ Lỗi tải: {str(e)[:40]}")
    
    cleanup_temp()
    
    print(f"\n📊 Đã cào được {len(saved_avatars)} avatar")
    
    if not saved_avatars:
        print("❌ Không cào được ảnh nào!")
        return
    
    # Gắn avatar cho users
    print(f"\n🔗 Đang gắn avatar cho {num_users} users...")
    
    with engine.connect() as conn:
        for index, row in df_users.iterrows():
            user_id = int(row['id'])  # Convert numpy.int64 to Python int
            
            # Phân phối gần đều
            avatar_file = saved_avatars[index % len(saved_avatars)]
            avatar_url = f"{DB_AVATARS_PATH_PREFIX}{avatar_file}"
            
            sql = text("UPDATE users SET avatar_url = :url WHERE id = :uid")
            conn.execute(sql, {"url": avatar_url, "uid": user_id})
        
        conn.commit()
        print(f"   ✅ Đã gắn avatar cho {num_users} users")
    
    print("\n" + "="*60)
    print("✅ CÀO AVATAR HOÀN TẤT!")
    print("="*60)

# ============================================================
# MAIN MENU
# ============================================================

def print_menu():
    print("\n")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║         HANOI TRAVEL - IMAGE CRAWLER TOOL                ║")
    print("╠══════════════════════════════════════════════════════════╣")
    print("║  1. Reset Place Images (xóa DB + folder)                 ║")
    print("║  2. Crawl Place Images (cào ảnh địa điểm)                ║")
    print("║  3. Reset User Avatars (xóa avatar_url + folder)         ║")
    print("║  4. Crawl User Avatars (cào avatar theo chủ đề)          ║")
    print("║  0. Thoát                                                ║")
    print("╚══════════════════════════════════════════════════════════╝")

def main():
    print("\n" + "="*60)
    print("🌟 WELCOME TO HANOI TRAVEL IMAGE CRAWLER 🌟")
    print("="*60)
    print(f"📍 Database: {DB_CONNECTION_STR}")
    print(f"📍 Places folder: {PLACES_IMAGE_DIR}")
    print(f"📍 Avatars folder: {AVATARS_IMAGE_DIR}")
    
    while True:
        print_menu()
        choice = input("\n👉 Chọn chức năng (0-4): ").strip()
        
        if choice == "1":
            reset_place_images()
        elif choice == "2":
            crawl_place_images()
        elif choice == "3":
            reset_user_avatars()
        elif choice == "4":
            crawl_user_avatars()
        elif choice == "0":
            print("\n👋 Tạm biệt!")
            break
        else:
            print("❌ Lựa chọn không hợp lệ!")

if __name__ == "__main__":
    main()