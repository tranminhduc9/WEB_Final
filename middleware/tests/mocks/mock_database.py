"""
Mock database service cho middleware testing
"""

from typing import Dict, Any, List
from datetime import datetime


class MockDatabase:
    """Mock database service for testing"""

    def __init__(self):
        self.activity_logs: List[Dict[str, Any]] = []
        self.connection_error = False

    async def save_audit_log(self, log_data: Dict[str, Any]):
        """Save audit log"""
        if self.connection_error:
            raise Exception("Database connection failed")

        log_entry = {
            "id": len(self.activity_logs) + 1,
            "created_at": datetime.utcnow().isoformat(),
            **log_data
        }
        self.activity_logs.append(log_entry)
        return log_entry

    def reset(self):
        """Reset database state"""
        self.activity_logs.clear()
        self.connection_error = False