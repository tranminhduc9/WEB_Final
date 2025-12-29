"""
Script test kết nối MongoDB Atlas
Hiển thị danh sách databases và collections
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import sys


# ============================================
# CONFIGURATION - ĐIỀN CONNECTION STRING VÀO ĐÂY
# ============================================
# Lấy connection string từ MongoDB Atlas:
# 1. Đăng nhập vào MongoDB Atlas (https://cloud.mongodb.com/)
# 2. Vào Database -> Connect -> Connect your application
# 3. Copy connection string và thay thế <password> bằng mật khẩu thực tế
# ============================================
MONGO_URI = "mongodb+srv://ocococ2005:123456aA@webserver.lyvsqx8.mongodb.net/"

# Hoặc nếu đã có connection string đầy đủ, paste vào đây:
# MONGO_URI = "mongodb+srv://user:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Timeout cho kết nối (giây)
CONNECTION_TIMEOUT = 10


def test_connection():
    """Test kết nối và hiển thị thông tin MongoDB"""
    
    print("=" * 60)
    print("MongoDB Atlas Connection Test")
    print("=" * 60)
    
    # Ẩn password trong connection string khi hiển thị
    display_uri = MONGO_URI
    if "@" in MONGO_URI:
        parts = MONGO_URI.split("@")
        if len(parts) == 2:
            # Giấu username:password
            display_uri = "mongodb+srv://***:***@" + parts[1]
    
    print(f"\n🔗 Connection String: {display_uri}")
    print(f"⏱️  Connection Timeout: {CONNECTION_TIMEOUT}s\n")
    
    try:
        # Tạo MongoDB client
        print("📡 Đang kết nối đến MongoDB Atlas...")
        client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=CONNECTION_TIMEOUT * 1000
        )
        
        # Test kết nối bằng cách ping server
        client.admin.command('ping')
        print("✅ Kết nối thành công!\n")
        
        # ============================================
        # 1. Hiển thị danh sách DATABASES
        # ============================================
        print("=" * 60)
        print("📚 DANH SÁCH DATABASES")
        print("=" * 60)
        
        db_list = client.list_database_names()
        
        if not db_list:
            print("⚠️  Không có database nào trong cluster.")
        else:
            print(f"\nTổng số databases: {len(db_list)}\n")
            for idx, db_name in enumerate(db_list, 1):
                print(f"  {idx}. {db_name}")
        
        print()
        
        # ============================================
        # 2. Hiển thị danh sách COLLECTIONS trong mỗi database
        # ============================================
        print("=" * 60)
        print("📦 DANH SÁCH COLLECTIONS TRONG MỖI DATABASE")
        print("=" * 60)
        
        for db_name in db_list:
            db = client[db_name]
            collections = db.list_collection_names()
            
            print(f"\n🗄️  Database: {db_name}")
            if not collections:
                print("   ⚠️  Không có collection nào.")
            else:
                print(f"   Tổng số collections: {len(collections)}")
                for idx, collection_name in enumerate(collections, 1):
                    # Lấy số lượng documents trong collection
                    try:
                        doc_count = db[collection_name].count_documents({})
                        print(f"   {idx}. {collection_name} ({doc_count:,} documents)")
                    except Exception as e:
                        print(f"   {idx}. {collection_name} (Không thể đếm documents: {str(e)})")
        
        print("\n" + "=" * 60)
        print("✅ Hoàn thành!")
        print("=" * 60)
        
        # Đóng kết nối
        client.close()
        
    except ConnectionFailure as e:
        print(f"❌ Lỗi kết nối: {str(e)}")
        print("\n💡 Kiểm tra lại:")
        print("   - Connection string đã đúng chưa?")
        print("   - Username và password đã chính xác chưa?")
        print("   - Network có kết nối internet không?")
        print("   - IP address của bạn đã được whitelist trong MongoDB Atlas chưa?")
        sys.exit(1)
        
    except ServerSelectionTimeoutError as e:
        print(f"❌ Lỗi timeout: Không thể kết nối đến server trong {CONNECTION_TIMEOUT}s")
        print(f"   Chi tiết: {str(e)}")
        print("\n💡 Kiểm tra lại:")
        print("   - Connection string có đúng không?")
        print("   - IP address của bạn đã được whitelist chưa? (Network Access trong MongoDB Atlas)")
        print("   - Firewall có chặn kết nối không?")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Lỗi không xác định: {str(e)}")
        print(f"   Loại lỗi: {type(e).__name__}")
        sys.exit(1)


if __name__ == "__main__":
    # Kiểm tra xem đã điền connection string chưa
    if "<username>" in MONGO_URI or "<password>" in MONGO_URI or "<cluster>" in MONGO_URI:
        print("⚠️  CẢNH BÁO: Bạn chưa điền connection string!")
        print("\n📝 Hướng dẫn:")
        print("   1. Mở file test_mongo.py")
        print("   2. Tìm dòng: MONGO_URI = \"...\"")
        print("   3. Thay thế connection string mẫu bằng connection string thực tế từ MongoDB Atlas")
        print("\n🔗 Lấy connection string:")
        print("   - Đăng nhập MongoDB Atlas: https://cloud.mongodb.com/")
        print("   - Vào Database -> Connect -> Connect your application")
        print("   - Copy connection string và thay <password> bằng mật khẩu thực tế")
        print("\n" + "=" * 60)
        sys.exit(1)
    
    test_connection()

