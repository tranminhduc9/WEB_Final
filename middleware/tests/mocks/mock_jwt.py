"""
Mock JWT service cho middleware testing
"""

import time
import jwt
from typing import Dict, Any, List


class MockJWTService:
    """Mock JWT service for testing"""

    def __init__(self, secret_key: str = "test-secret", algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.blacklisted_tokens: set = set()
        self.generated_tokens: List[Dict[str, Any]] = []

    def create_access_token(
        self,
        user_id: int,
        email: str,
        full_name: str = None,
        role_id: str = "user",
        **kwargs
    ) -> str:
        """Create access token"""
        payload = {
            "user_id": user_id,
            "email": email,
            "role_id": role_id,
            "full_name": full_name,
            "token_type": "access",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600,  # 1 hour
            **kwargs
        }
        token = jwt.encode(payload, self.secret_key, self.algorithm)
        self.generated_tokens.append({"token": token, "payload": payload})
        return token

    def create_expired_token(self, user_id: int) -> str:
        """Create expired token"""
        payload = {
            "user_id": user_id,
            "token_type": "access",
            "iat": int(time.time()) - 7200,  # 2 hours ago
            "exp": int(time.time()) - 3600   # 1 hour ago (expired)
        }
        return jwt.encode(payload, self.secret_key, self.algorithm)

    def create_invalid_token(self) -> str:
        """Create invalid token"""
        return "invalid.jwt.token"

    def reset(self):
        """Reset service state"""
        self.blacklisted_tokens.clear()
        self.generated_tokens.clear()