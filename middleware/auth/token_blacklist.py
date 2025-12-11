"""
Token Blacklist Service.

Manages blacklisted tokens for logout functionality.
Implementation following task #13 requirements.
"""

import logging
from typing import Optional
import redis
from datetime import datetime, timedelta

# Safe import with fallback
try:
    from ..config.settings import MiddlewareSettings
except ImportError:
    # Fallback for standalone usage
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config.settings import MiddlewareSettings


logger = logging.getLogger(__name__)


class TokenBlacklist:
    """
    Token Blacklist Service for managing revoked tokens.

    Features:
    - Store blacklisted tokens in Redis with expiration
    - Auto-expire blacklisted tokens when original token expires
    - Fail-open strategy: if Redis fails, allow requests
    - TTL management based on token expiration time
    """

    def __init__(
        self,
        redis_client: Optional[redis.Redis] = None,
        settings: MiddlewareSettings = None,
        key_prefix: str = "blacklist:"
    ):
        """
        Initialize Token Blacklist Service.

        Args:
            redis_client: Redis client instance
            settings: Middleware settings object
            key_prefix: Redis key prefix for blacklisted tokens
        """
        self.redis_client = redis_client
        self.settings = settings or MiddlewareSettings()
        self.key_prefix = key_prefix
        self.default_ttl = self.settings.access_token_expire_minutes * 60  # Convert to seconds

        if not redis_client:
            logger.warning("Redis client not provided. Token blacklist will be disabled.")

    async def add_to_blacklist(self, token: str, expires_in: Optional[int] = None) -> bool:
        """
        Add token to blacklist.

        Args:
            token: JWT token to blacklist
            expires_in: TTL in seconds. If None, uses default TTL from settings

        Returns:
            True if successfully added to blacklist, False otherwise
        """
        if not self.redis_client:
            logger.warning("Cannot add token to blacklist: Redis not available")
            return False

        try:
            # Calculate TTL
            ttl = expires_in or self.default_ttl
            blacklist_key = f"{self.key_prefix}{token}"

            # Store in Redis with TTL
            result = await self.redis_client.setex(blacklist_key, ttl, "revoked")

            if result:
                logger.info(f"Token added to blacklist: {token[:20]}... (TTL: {ttl}s)")
                return True
            else:
                logger.error(f"Failed to add token to blacklist: {token[:20]}...")
                return False

        except Exception as e:
            logger.error(f"Error adding token to blacklist: {str(e)}")
            return False

    async def add_to_blacklist_with_exp(self, token: str, expiration_time: datetime) -> bool:
        """
        Add token to blacklist with specific expiration time.

        Args:
            token: JWT token to blacklist
            expiration_time: Token expiration datetime

        Returns:
            True if successfully added to blacklist, False otherwise
        """
        if not self.redis_client:
            logger.warning("Cannot add token to blacklist: Redis not available")
            return False

        try:
            # Calculate TTL until token expiration
            now = datetime.utcnow()
            if expiration_time <= now:
                # Token already expired, no need to blacklist
                logger.info(f"Token already expired, skipping blacklist: {token[:20]}...")
                return True

            ttl = int((expiration_time - now).total_seconds())
            return await self.add_to_blacklist(token, ttl)

        except Exception as e:
            logger.error(f"Error calculating token TTL: {str(e)}")
            # Fallback to default TTL
            return await self.add_to_blacklist(token)

    async def is_blacklisted(self, token: str) -> bool:
        """
        Check if token is blacklisted.

        Args:
            token: JWT token to check

        Returns:
            True if token is blacklisted, False otherwise
        """
        if not self.redis_client:
            # If Redis is not available, assume token is not blacklisted (fail-open)
            return False

        try:
            blacklist_key = f"{self.key_prefix}{token}"
            is_blacklisted = self.redis_client.exists(blacklist_key)
            return bool(is_blacklisted)

        except Exception as e:
            logger.error(f"Error checking token blacklist: {str(e)}")
            # If Redis fails, assume token is not blacklisted (fail-open)
            return False

    async def remove_from_blacklist(self, token: str) -> bool:
        """
        Remove token from blacklist (if needed for special cases).

        Args:
            token: JWT token to remove from blacklist

        Returns:
            True if successfully removed, False otherwise
        """
        if not self.redis_client:
            logger.warning("Cannot remove token from blacklist: Redis not available")
            return False

        try:
            blacklist_key = f"{self.key_prefix}{token}"
            result = self.redis_client.delete(blacklist_key)

            if result:
                logger.info(f"Token removed from blacklist: {token[:20]}...")
                return True
            else:
                logger.warning(f"Token not found in blacklist: {token[:20]}...")
                return False

        except Exception as e:
            logger.error(f"Error removing token from blacklist: {str(e)}")
            return False

    async def get_blacklist_ttl(self, token: str) -> Optional[int]:
        """
        Get remaining TTL for blacklisted token.

        Args:
            token: JWT token to check

        Returns:
            Remaining TTL in seconds, or None if token is not blacklisted
        """
        if not self.redis_client:
            return None

        try:
            blacklist_key = f"{self.key_prefix}{token}"
            ttl = await self.redis_client.ttl(blacklist_key)
            return ttl if ttl > 0 else None

        except Exception as e:
            logger.error(f"Error getting token TTL: {str(e)}")
            return None

    async def clear_blacklist(self) -> int:
        """
        Clear all blacklisted tokens (useful for maintenance).

        Returns:
            Number of tokens cleared, or -1 if error
        """
        if not self.redis_client:
            logger.warning("Cannot clear blacklist: Redis not available")
            return -1

        try:
            # Find all keys with blacklist prefix
            pattern = f"{self.key_prefix}*"
            keys = self.redis_client.keys(pattern)

            if keys:
                # Delete all blacklisted tokens
                result = self.redis_client.delete(*keys)
                logger.info(f"Cleared {result} tokens from blacklist")
                return result
            else:
                logger.info("No blacklisted tokens found")
                return 0

        except Exception as e:
            logger.error(f"Error clearing blacklist: {str(e)}")
            return -1

    async def get_blacklist_count(self) -> int:
        """
        Get count of blacklisted tokens.

        Returns:
            Number of blacklisted tokens
        """
        if not self.redis_client:
            return 0

        try:
            pattern = f"{self.key_prefix}*"
            keys = self.redis_client.keys(pattern)
            return len(keys)

        except Exception as e:
            logger.error(f"Error getting blacklist count: {str(e)}")
            return 0

    async def get_blacklisted_tokens(self) -> list:
        """
        Get list of all blacklisted tokens.

        Returns:
            List of blacklisted token strings
        """
        if not self.redis_client:
            return []

        try:
            pattern = f"{self.key_prefix}*"
            keys = self.redis_client.keys(pattern)

            # Remove the key prefix to get just the tokens
            tokens = [key.replace(self.key_prefix, '') for key in keys]
            return tokens

        except Exception as e:
            logger.error(f"Error getting blacklisted tokens: {str(e)}")
            return []

    async def get_statistics(self) -> dict:
        """
        Get blacklist statistics.

        Returns:
            Dictionary with blacklist statistics
        """
        try:
            total_tokens = await self.get_blacklist_count()

            # For simplicity, consider all tokens as active (non-expired)
            # In a real implementation, you might check TTL for each token
            active_tokens = total_tokens

            return {
                "total_tokens": total_tokens,
                "active_tokens": active_tokens
            }

        except Exception as e:
            logger.error(f"Error getting blacklist statistics: {str(e)}")
            return {
                "total_tokens": 0,
                "active_tokens": 0
            }

    def get_redis_info(self) -> Optional[dict]:
        """
        Get Redis connection information for monitoring.

        Returns:
            Redis info dictionary or None if not available
        """
        if not self.redis_client:
            return None

        try:
            info = self.redis_client.info()
            return {
                "connected": True,
                "redis_version": info.get("redis_version"),
                "used_memory": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "keyspace": {
                    db: info.get(f"db{db}")
                    for db in range(16)
                    if info.get(f"db{db}")
                }
            }
        except Exception as e:
            logger.error(f"Error getting Redis info: {str(e)}")
            return {"connected": False, "error": str(e)}