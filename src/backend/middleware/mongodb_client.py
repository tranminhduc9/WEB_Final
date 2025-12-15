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
        "reports": "reports_mongo"
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

    # Specialized methods for comments
    async def create_comment(self, comment_data: Dict[str, Any]) -> str:
        """
        Tạo comment mới

        Args:
            comment_data: Dữ liệu comment

        Returns:
            str: Comment ID
        """
        return await self.insert_one("post_comments", comment_data)

    async def get_comments(self, post_id: str, limit: int = 10, skip: int = 0) -> List[Dict[str, Any]]:
        """
        Lấy danh sách comments của bài viết

        Args:
            post_id: ID bài viết
            limit: Số comments tối đa
            skip: Số comments bỏ qua

        Returns:
            List: Danh sách comments
        """
        query = {"post_id": post_id}
        sort = [("created_at", DESCENDING)]

        return await self.find_many("post_comments", query, sort=sort, limit=limit, skip=skip)

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