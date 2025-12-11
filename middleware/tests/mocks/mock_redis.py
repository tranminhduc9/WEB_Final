"""
Mock Redis implementation cho middleware testing - Simplified version
"""

import time
from typing import Dict, Any, Optional


class MockRedis:
    """Simplified mock Redis client for testing"""

    def __init__(self):
        self.data: Dict[str, Any] = {}
        self.expire_times: Dict[str, float] = {}
        self.connection_error = False

    async def get(self, key: str) -> Optional[str]:
        """Get value by key"""
        if self.connection_error:
            raise Exception("Redis connection failed")

        self._cleanup_expired()
        value = self.data.get(key)
        return str(value) if value is not None else None

    def get_sync(self, key: str) -> Optional[str]:
        """Get value by key (sync version for compatibility)"""
        if self.connection_error:
            raise Exception("Redis connection failed")

        self._cleanup_expired()
        value = self.data.get(key)
        return str(value) if value is not None else None

    async def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Set value with optional expiration"""
        if self.connection_error:
            raise Exception("Redis connection failed")

        self.data[key] = value
        if ex:
            self.expire_times[key] = time.time() + ex
        return True

    async def incr(self, key: str) -> int:
        """Increment value by key (async version)"""
        if self.connection_error:
            raise Exception("Redis connection failed")

        self._cleanup_expired()
        current_value = self.data.get(key, 0)
        self.data[key] = current_value + 1
        return self.data[key]

    def incr_sync(self, key: str) -> int:
        """Increment value by key (sync version)"""
        if self.connection_error:
            raise Exception("Redis connection failed")

        self._cleanup_expired()
        current_value = self.data.get(key, 0)
        self.data[key] = current_value + 1
        return self.data[key]

    async def delete(self, key: str) -> int:
        """Delete key"""
        if self.connection_error:
            raise Exception("Redis connection failed")

        if key in self.data:
            del self.data[key]
            if key in self.expire_times:
                del self.expire_times[key]
            return 1
        return 0

    def exists(self, key: str) -> bool:
        """Check if key exists"""
        self._cleanup_expired()
        return key in self.data

    def _cleanup_expired(self):
        """Remove expired keys"""
        now = time.time()
        expired_keys = [
            key for key, expire_time in self.expire_times.items()
            if expire_time <= now
        ]
        for key in expired_keys:
            if key in self.data:
                del self.data[key]
            if key in self.expire_times:
                del self.expire_times[key]

    def reset(self):
        """Reset all data"""
        self.data.clear()
        self.expire_times.clear()
        self.connection_error = False

    def simulate_connection_error(self, enabled: bool = True):
        """Simulate connection error"""
        self.connection_error = enabled

    def pipeline(self):
        """Mock pipeline for Redis operations"""
        return MockPipeline(self)


class MockPipeline:
    """Mock Redis pipeline"""

    def __init__(self, redis_client):
        self.redis_client = redis_client
        self.commands = []

    def incr(self, key: str):
        """Add increment command to pipeline"""
        self.commands.append(("incr", key))
        return self

    def expire(self, key: str, seconds: int):
        """Add expire command to pipeline"""
        self.commands.append(("expire", key, seconds))
        return self

    def execute(self):
        """Execute pipeline commands"""
        results = []
        for cmd in self.commands:
            if cmd[0] == "incr":
                result = self.redis_client.incr_sync(cmd[1])
                results.append(result)
            elif cmd[0] == "expire":
                # Mock expire command - always return True
                results.append(True)
        self.commands.clear()
        return results

    async def execute_async(self):
        """Execute pipeline commands (async version)"""
        return self.execute()


def create_mock_redis():
    """Factory function to create mock Redis"""
    return MockRedis()