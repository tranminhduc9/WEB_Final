"""
MongoDB Client Middleware

Module này xử lý kết nối và thao tác với MongoDB
cho các collections: posts_mongo, post_likes_mongo, post_comments_mongo,
chatbot_logs_mongo, reports_mongo.
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import logging
import os
import json
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

logger = logging.getLogger(__name__)


class MongoConfig:
    """Cấu hình cho MongoDB connection"""

    # Connection settings
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "hanoi_travel_mongo")
    MONGO_TIMEOUT = int(os.getenv("MONGO_TIMEOUT", "5000"))  # ms

    # Collections
    COLLECTIONS = {
        "posts": "posts_mongo",
        "post_likes": "post_likes_mongo",
        "post_comments": "post_comments_mongo",
        "chatbot_logs": "chatbot_logs_mongo",
        "reports": "reports_mongo",
        "audit_logs": "audit_logs_mongo"  # NEW
    }

    # Index configurations
    INDEXES = {
        "posts_mongo": [
            [("author_id", ASCENDING)],
            [("related_place_id", ASCENDING)],
            [("created_at", DESCENDING)],
            [("tags", ASCENDING)],
            [("status", ASCENDING)],
            [("title", "text"), ("content", "text")]  # Text search
        ],
        "post_likes_mongo": [
            [("post_id", ASCENDING)],
            [("user_id", ASCENDING)],
            [("post_id", ASCENDING), ("user_id", ASCENDING)],  # Compound index
            [("created_at", DESCENDING)]
        ],
        "post_comments_mongo": [
            [("post_id", ASCENDING)],
            [("user_id", ASCENDING)],
            [("parent_id", ASCENDING)],  # For nested comments
            [("depth", ASCENDING)],  # NEW: For comment tree queries
            [("path", ASCENDING)],  # NEW: For nested comment path queries
            [("created_at", DESCENDING)]
        ],
        "chatbot_logs_mongo": [
            [("conversation_id", ASCENDING)],
            [("user_id", ASCENDING)],
            [("created_at", DESCENDING)]
        ],
        "reports_mongo": [
            [("target_type", ASCENDING)],
            [("target_id", ASCENDING)],
            [("reporter_id", ASCENDING)],
            [("created_at", DESCENDING)]
        ],
        "audit_logs_mongo": [  # NEW
            [("user_id", ASCENDING)],
            [("action", ASCENDING)],
            [("resource_type", ASCENDING)],
            [("resource_id", ASCENDING)],
            [("timestamp", DESCENDING)],
            [("user_id", ASCENDING), ("timestamp", DESCENDING)],  # Compound index
            [("resource_type", ASCENDING), ("resource_id", ASCENDING)]  # Compound index
        ]
    }


class MongoDBClient:
    """
    MongoDB client với các phương thức tiện ích

    Cung cấp các phương thức thao tác với MongoDB collections
    cho hệ thống Hanoi Travel.
    """

    def __init__(self, mongo_uri: str = None, db_name: str = None):
        """
        Khởi tạo MongoDB client

        Args:
            mongo_uri: MongoDB connection URI
            db_name: Database name
        """
        self.config = MongoConfig()
        self.mongo_uri = mongo_uri or self.config.MONGO_URI
        self.db_name = db_name or self.config.MONGO_DB_NAME

        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        self.is_connected = False

    async def connect(self) -> bool:
        """
        Kết nối đến MongoDB

        Returns:
            bool: True nếu kết nối thành công
        """
        try:
            # Create MongoDB client
            self.client = AsyncIOMotorClient(
                self.mongo_uri,
                serverSelectionTimeoutMS=self.config.MONGO_TIMEOUT
            )

            # Test connection
            await self.client.admin.command('ping')

            # Get database
            self.db = self.client[self.db_name]

            # Setup indexes
            await self._setup_indexes()

            self.is_connected = True
            logger.info(f"Connected to MongoDB: {self.mongo_uri}")
            return True

        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            self.is_connected = False
            return False
        except Exception as e:
            logger.error(f"MongoDB connection error: {str(e)}")
            self.is_connected = False
            return False

    async def disconnect(self):
        """Đóng kết nối MongoDB"""
        if self.client:
            self.client.close()
            self.is_connected = False
            logger.info("Disconnected from MongoDB")

    async def _setup_indexes(self):
        """Setup indexes cho collections"""
        if not self.db:
            return

        try:
            for collection_name, indexes in self.config.INDEXES.items():
                collection = self.db[collection_name]

                for index_spec in indexes:
                    if isinstance(index_spec[0], list) and len(index_spec[0]) > 1:
                        # Compound index
                        await collection.create_index(index_spec[0])
                    else:
                        # Single index
                        await collection.create_index(index_spec)

            logger.info("MongoDB indexes setup completed")

        except Exception as e:
            logger.error(f"Failed to setup MongoDB indexes: {str(e)}")

    # Generic CRUD operations
    async def insert_one(self, collection: str, document: Dict[str, Any]) -> str:
        """
        Insert document vào collection

        Args:
            collection: Tên collection
            document: Document cần insert

        Returns:
            str: Document ID
        """
        if not self.is_connected:
            raise Exception("MongoDB not connected")

        collection_name = self.config.COLLECTIONS.get(collection, collection)
        coll = self.db[collection_name]

        # Add timestamps
        document["created_at"] = datetime.utcnow()
        document["updated_at"] = datetime.utcnow()

        result = await coll.insert_one(document)
        return str(result.inserted_id)

    async def find_one(self, collection: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Tìm một document

        Args:
            collection: Tên collection
            query: Query conditions

        Returns:
            Dict: Document nếu tìm thấy
        """
        if not self.is_connected:
            raise Exception("MongoDB not connected")

        collection_name = self.config.COLLECTIONS.get(collection, collection)
        coll = self.db[collection_name]

        document = await coll.find_one(query)
        if document and "_id" in document:
            document["_id"] = str(document["_id"])

        return document

    async def find_many(
        self,
        collection: str,
        query: Dict[str, Any] = None,
        sort: List[tuple] = None,
        limit: int = None,
        skip: int = None
    ) -> List[Dict[str, Any]]:
        """
        Tìm nhiều documents

        Args:
            collection: Tên collection
            query: Query conditions
            sort: Sort conditions
            limit: Số documents tối đa
            skip: Số documents bỏ qua

        Returns:
            List: Danh sách documents
        """
        if not self.is_connected:
            raise Exception("MongoDB not connected")

        collection_name = self.config.COLLECTIONS.get(collection, collection)
        coll = self.db[collection_name]

        cursor = coll.find(query or {})

        if sort:
            cursor = cursor.sort(sort)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)

        documents = []
        async for doc in cursor:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
            documents.append(doc)

        return documents

    async def update_one(
        self,
        collection: str,
        query: Dict[str, Any],
        update: Dict[str, Any]
    ) -> bool:
        """
        Update một document

        Args:
            collection: Tên collection
            query: Query conditions
            update: Update data

        Returns:
            bool: True nếu update thành công
        """
        if not self.is_connected:
            raise Exception("MongoDB not connected")

        collection_name = self.config.COLLECTIONS.get(collection, collection)
        coll = self.db[collection_name]

        # Add updated_at timestamp
        update["updated_at"] = datetime.utcnow()

        result = await coll.update_one(query, {"$set": update})
        return result.modified_count > 0

    async def delete_one(self, collection: str, query: Dict[str, Any]) -> bool:
        """
        Xóa một document

        Args:
            collection: Tên collection
            query: Query conditions

        Returns:
            bool: True nếu xóa thành công
        """
        if not self.is_connected:
            raise Exception("MongoDB not connected")

        collection_name = self.config.COLLECTIONS.get(collection, collection)
        coll = self.db[collection_name]

        result = await coll.delete_one(query)
        return result.deleted_count > 0

    async def count(self, collection: str, query: Dict[str, Any] = None) -> int:
        """
        Đếm số documents

        Args:
            collection: Tên collection
            query: Query conditions

        Returns:
            int: Số documents
        """
        if not self.is_connected:
            raise Exception("MongoDB not connected")

        collection_name = self.config.COLLECTIONS.get(collection, collection)
        coll = self.db[collection_name]

        return await coll.count_documents(query or {})

    # Specialized methods for posts
    async def create_post(self, post_data: Dict[str, Any]) -> str:
        """
        Tạo bài viết mới

        Args:
            post_data: Dữ liệu bài viết

        Returns:
            str: Post ID
        """
        return await self.insert_one("posts", post_data)

    async def get_post(self, post_id: str) -> Optional[Dict[str, Any]]:
        """
        Lấy bài viết theo ID

        Args:
            post_id: ID của bài viết

        Returns:
            Dict: Post data
        """
        return await self.find_one("posts", {"_id": post_id})

    async def get_posts(
        self,
        limit: int = 10,
        skip: int = 0,
        sort: str = "newest",
        tag: str = None,
        keyword: str = None
    ) -> List[Dict[str, Any]]:
        """
        Lấy danh sách bài viết

        Args:
            limit: Số bài viết tối đa
            skip: Số bài viết bỏ qua
            sort: Sắp xếp (newest, popular)
            tag: Tag filter
            keyword: Keyword search

        Returns:
            List: Danh sách bài viết
        """
        query = {"status": "approved"}  # Chỉ lấy bài đã duyệt

        if tag:
            query["tags"] = {"$in": [tag]}

        if keyword:
            query["$text"] = {"$search": keyword}

        # Sort logic
        if sort == "popular":
            sort_list = [("likes_count", DESCENDING), ("comments_count", DESCENDING)]
        else:  # newest
            sort_list = [("created_at", DESCENDING)]

        return await self.find_many("posts", query, sort=sort_list, limit=limit, skip=skip)

    # Specialized methods for likes
    async def toggle_like(self, post_id: str, user_id: int) -> Dict[str, Any]:
        """
        Toggle like bài viết

        Args:
            post_id: ID bài viết
            user_id: ID user

        Returns:
            Dict: {liked: bool, total_likes: int}
        """
        # Check if already liked
        existing_like = await self.find_one(
            "post_likes",
            {"post_id": post_id, "user_id": user_id}
        )

        if existing_like:
            # Unlike
            await self.delete_one("post_likes", {"post_id": post_id, "user_id": user_id})
            total_likes = await self.count("post_likes", {"post_id": post_id})
            return {"liked": False, "total_likes": total_likes}
        else:
            # Like
            like_data = {
                "post_id": post_id,
                "user_id": user_id,
                "created_at": datetime.utcnow()
            }
            await self.insert_one("post_likes", like_data)
            total_likes = await self.count("post_likes", {"post_id": post_id})
            return {"liked": True, "total_likes": total_likes}

    # Specialized methods for comments (with Tree Structure support)
    async def create_comment(self, comment_data: Dict[str, Any]) -> str:
        """
        Tạo comment mới (Root comment hoặc Nested reply)

        Args:
            comment_data: Dữ liệu comment
                - post_id: ID bài viết
                - user_id: ID user
                - content: Nội dung comment
                - parent_id: ID parent comment (null cho root comment)
                - images: List ảnh (optional)

        Returns:
            str: Comment ID
        """
        return await self.insert_one("post_comments", comment_data)

    async def create_nested_reply(
        self,
        parent_id: str,
        user_id: int,
        content: str,
        post_id: str = None,
        images: List[str] = None
    ) -> str:
        """
        Tạo nested reply cho comment (Tree structure)

        Args:
            parent_id: ID của parent comment
            user_id: ID user
            content: Nội dung reply
            post_id: ID bài viết (optional, sẽ tự động lấy từ parent)
            images: List ảnh (optional)

        Returns:
            str: Reply comment ID
        """
        # Get parent comment to extract post_id
        parent = await self.find_one("post_comments", {"_id": parent_id})
        if not parent:
            raise Exception("Parent comment not found")

        reply_data = {
            "post_id": post_id or parent.get("post_id"),
            "user_id": user_id,
            "content": content,
            "parent_id": parent_id,  # Nested reply
            "images": images or [],
            "depth": (parent.get("depth", 0) + 1),  # Track depth for nesting
            "path": parent.get("path", []) + [parent_id]  # Track path for queries
        }

        return await self.insert_one("post_comments", reply_data)

    async def get_root_comments(
        self,
        post_id: str,
        limit: int = 10,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Lấy root comments (top-level comments) của bài viết

        Args:
            post_id: ID bài viết
            limit: Số comments tối đa
            skip: Số comments bỏ qua

        Returns:
            List: Danh sách root comments
        """
        query = {
            "post_id": post_id,
            "parent_id": None  # Chỉ lấy root comments
        }
        sort = [("created_at", DESCENDING)]

        return await self.find_many("post_comments", query, sort=sort, limit=limit, skip=skip)

    async def get_nested_replies(
        self,
        parent_id: str,
        limit: int = 10,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Lấy nested replies cho một comment (Tree structure)

        Args:
            parent_id: ID parent comment
            limit: Số replies tối đa
            skip: Số replies bỏ qua

        Returns:
            List: Danh sách nested replies
        """
        query = {"parent_id": parent_id}
        sort = [("created_at", ASCENDING)]  # Oldest first for replies

        return await self.find_many("post_comments", query, sort=sort, limit=limit, skip=skip)

    async def get_comment_tree(
        self,
        post_id: str,
        max_depth: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Lấy toàn bộ comment tree của bài viết (Root + Nested replies)

        Args:
            post_id: ID bài viết
            max_depth: Độ sâu tối đa của nesting

        Returns:
            List: Comment tree structure
        """
        # Lấy tất cả comments của post
        query = {"post_id": post_id, "depth": {"$lte": max_depth}}
        sort = [("created_at", DESCENDING)]

        all_comments = await self.find_many("post_comments", query, sort=sort)

        # Build tree structure
        def build_tree(comments, parent_id=None):
            """Recursive function để build comment tree"""
            tree = []
            for comment in comments:
                if comment.get("parent_id") == parent_id:
                    # Tạo node con
                    node = {
                        **comment,
                        "replies": build_tree(comments, comment.get("_id"))
                    }
                    tree.append(node)
            return tree

        return build_tree(all_comments)

    async def get_comments(self, post_id: str, limit: int = 10, skip: int = 0) -> List[Dict[str, Any]]:
        """
        Lấy danh sách comments của bài viết (Legacy - giữ cho compatibility)

        Args:
            post_id: ID bài viết
            limit: Số comments tối đa
            skip: Số comments bỏ qua

        Returns:
            List: Danh sách comments (root + replies flatten)
        """
        query = {"post_id": post_id}
        sort = [("created_at", DESCENDING)]

        return await self.find_many("post_comments", query, sort=sort, limit=limit, skip=skip)

    async def count_comments(self, post_id: str) -> Dict[str, int]:
        """
        Đếm comments của bài viết

        Args:
            post_id: ID bài viết

        Returns:
            Dict: {total_comments, root_comments, replies}
        """
        total = await self.count("post_comments", {"post_id": post_id})
        root = await self.count("post_comments", {"post_id": post_id, "parent_id": None})
        replies = total - root

        return {
            "total_comments": total,
            "root_comments": root,
            "replies": replies
        }

    # Specialized methods for chatbot logs
    async def save_chatbot_log(self, log_data: Dict[str, Any]) -> str:
        """
        Lưu chatbot conversation log

        Args:
            log_data: Dữ liệu conversation

        Returns:
            str: Log ID
        """
        return await self.insert_one("chatbot_logs", log_data)

    async def get_chatbot_history(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Lấy lịch sử chatbot của user

        Args:
            user_id: ID user
            limit: Số logs tối đa

        Returns:
            List: Danh sách conversation logs
        """
        query = {"user_id": user_id}
        sort = [("created_at", DESCENDING)]

        return await self.find_many("chatbot_logs", query, sort=sort, limit=limit)

    # Specialized methods for reports
    async def create_report(self, report_data: Dict[str, Any]) -> str:
        """
        Tạo báo cáo mới

        Args:
            report_data: Dữ liệu báo cáo

        Returns:
            str: Report ID
        """
        return await self.insert_one("reports", report_data)

    # Specialized methods for Audit Logs
    async def create_audit_log(
        self,
        user_id: int,
        action: str,
        resource_type: str,
        resource_id: str = None,
        details: Dict[str, Any] = None,
        ip_address: str = None,
        user_agent: str = None
    ) -> str:
        """
        Tạo audit log

        Args:
            user_id: ID user
            action: Hành động (create, update, delete, login, logout, etc.)
            resource_type: Loại resource (post, comment, place, user, etc.)
            resource_id: ID của resource
            details: Chi tiết bổ sung
            ip_address: IP address của user
            user_agent: User agent string

        Returns:
            str: Log ID
        """
        log_data = {
            "user_id": user_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details or {},
            "ip_address": ip_address,
            "user_agent": user_agent,
            "timestamp": datetime.utcnow()
        }

        return await self.insert_one("audit_logs", log_data)

    async def get_audit_logs(
        self,
        user_id: int = None,
        action: str = None,
        resource_type: str = None,
        resource_id: str = None,
        start_date: datetime = None,
        end_date: datetime = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Lấy audit logs với filters

        Args:
            user_id: Filter theo user
            action: Filter theo hành động
            resource_type: Filter theo loại resource
            resource_id: Filter theo resource ID
            start_date: Lọc logs từ ngày
            end_date: Lọc logs đến ngày
            limit: Số logs tối đa
            skip: Số logs bỏ qua

        Returns:
            List: Danh sách audit logs
        """
        query = {}

        if user_id:
            query["user_id"] = user_id
        if action:
            query["action"] = action
        if resource_type:
            query["resource_type"] = resource_type
        if resource_id:
            query["resource_id"] = resource_id
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = start_date
            if end_date:
                query["timestamp"]["$lte"] = end_date

        sort = [("timestamp", DESCENDING)]

        return await self.find_many("audit_logs", query, sort=sort, limit=limit, skip=skip)

    async def get_user_activity_summary(
        self,
        user_id: int,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Lấy tổng hợp hoạt động của user

        Args:
            user_id: ID user
            days: Số ngày cần phân tích

        Returns:
            Dict: Activity summary
        """
        from datetime import timedelta

        start_date = datetime.utcnow() - timedelta(days=days)

        # Lấy tất cả logs của user trong khoảng thời gian
        logs = await self.get_audit_logs(
            user_id=user_id,
            start_date=start_date,
            limit=10000
        )

        # Aggregate data
        summary = {
            "user_id": user_id,
            "period_days": days,
            "total_actions": len(logs),
            "actions_by_type": {},
            "resources_by_type": {},
            "daily_activity": {}
        }

        for log in logs:
            # Count by action type
            action = log.get("action", "unknown")
            summary["actions_by_type"][action] = summary["actions_by_type"].get(action, 0) + 1

            # Count by resource type
            resource_type = log.get("resource_type", "unknown")
            summary["resources_by_type"][resource_type] = summary["resources_by_type"].get(resource_type, 0) + 1

            # Daily activity
            timestamp = log.get("timestamp")
            if timestamp:
                date_key = timestamp.strftime("%Y-%m-%d")
                summary["daily_activity"][date_key] = summary["daily_activity"].get(date_key, 0) + 1

        return summary

    async def cleanup_old_audit_logs(self, retention_days: int = 90) -> int:
        """
        Xóa audit logs cũ (theo retention policy)

        Args:
            retention_days: Số ngày giữ logs

        Returns:
            int: Số logs đã xóa
        """
        from datetime import timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

        collection_name = "audit_logs"
        coll = self.db[collection_name]

        result = await coll.delete_many({"timestamp": {"$lt": cutoff_date}})

        logger.info(f"Cleaned up {result.deleted_count} audit logs older than {retention_days} days")
        return result.deleted_count


# Global MongoDB client instance
mongo_client = MongoDBClient()


# Context manager for MongoDB connection
async def get_mongodb():
    """Get MongoDB client with connection check"""
    if not mongo_client.is_connected:
        await mongo_client.connect()
    return mongo_client


# Decorators for MongoDB operations
def require_mongodb_connection(func):
    """Decorator đòi hỏi MongoDB connection"""
    async def wrapper(*args, **kwargs):
        if not mongo_client.is_connected:
            await mongo_client.connect()
        return await func(*args, **kwargs)
    return wrapper


# Utility functions
def convert_objectid_to_str(data: Union[Dict, List]) -> Union[Dict, List]:
    """
    Convert ObjectId trong MongoDB data sang string

    Args:
        data: Data cần convert

    Returns:
        Data đã convert
    """
    if isinstance(data, dict):
        return {
            key: str(value) if key == "_id" else convert_objectid_to_str(value)
            for key, value in data.items()
        }
    elif isinstance(data, list):
        return [convert_objectid_to_str(item) for item in data]
    else:
        return data


def create_aggregation_pipeline(
    match_query: Dict[str, Any] = None,
    lookup_stages: List[Dict[str, Any]] = None,
    group_stage: Dict[str, Any] = None,
    sort_stage: List[tuple] = None,
    limit_stage: int = None
) -> List[Dict[str, Any]]:
    """
    Tạo aggregation pipeline cho MongoDB

    Args:
        match_query: $match stage
        lookup_stages: List của $lookup stages
        group_stage: $group stage
        sort_stage: Sort conditions
        limit_stage: Limit

    Returns:
        List: Aggregation pipeline
    """
    pipeline = []

    if match_query:
        pipeline.append({"$match": match_query})

    if lookup_stages:
        pipeline.extend(lookup_stages)

    if group_stage:
        pipeline.append({"$group": group_stage})

    if sort_stage:
        sort_dict = {field: direction for field, direction in sort_stage}
        pipeline.append({"$sort": sort_dict})

    if limit_stage:
        pipeline.append({"$limit": limit_stage})

    return pipeline