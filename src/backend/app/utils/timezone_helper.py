"""
Timezone Helper Module

Cung cấp các hàm tiện ích để xử lý timezone một cách nhất quán.
Best practice: Lưu trữ tất cả datetime dưới dạng UTC với timezone-aware,
frontend sẽ convert sang local timezone khi hiển thị.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, Union


# Vietnam timezone (UTC+7)
VIETNAM_TZ = timezone(timedelta(hours=7))


def utc_now() -> datetime:
    """
    Trả về thời gian hiện tại dưới dạng UTC timezone-aware.
    Thay thế cho datetime.utcnow() (deprecated trong Python 3.12+)
    
    Returns:
        datetime: Current time in UTC with timezone info
    """
    return datetime.now(timezone.utc)


def vietnam_now() -> datetime:
    """
    Trả về thời gian hiện tại theo timezone Việt Nam (UTC+7).
    
    Returns:
        datetime: Current time in Vietnam timezone
    """
    return datetime.now(VIETNAM_TZ)


def to_utc(dt: datetime) -> datetime:
    """
    Convert datetime sang UTC.
    
    Args:
        dt: datetime object (có thể naive hoặc aware)
        
    Returns:
        datetime: UTC timezone-aware datetime
    """
    if dt is None:
        return None
    
    if dt.tzinfo is None:
        # Naive datetime - assume it's UTC
        return dt.replace(tzinfo=timezone.utc)
    else:
        # Aware datetime - convert to UTC
        return dt.astimezone(timezone.utc)


def to_vietnam(dt: datetime) -> datetime:
    """
    Convert datetime sang Vietnam timezone.
    
    Args:
        dt: datetime object
        
    Returns:
        datetime: Vietnam timezone datetime
    """
    if dt is None:
        return None
    
    if dt.tzinfo is None:
        # Naive datetime - assume it's UTC, then convert
        dt = dt.replace(tzinfo=timezone.utc)
    
    return dt.astimezone(VIETNAM_TZ)


def to_iso_string(dt: datetime, include_timezone: bool = True) -> Optional[str]:
    """
    Convert datetime sang ISO 8601 string.
    
    Args:
        dt: datetime object
        include_timezone: Có bao gồm timezone info không
        
    Returns:
        str: ISO format string (e.g. "2024-01-01T12:00:00+00:00")
    """
    if dt is None:
        return None
    
    if include_timezone:
        # Ensure timezone-aware
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()
    else:
        return dt.replace(tzinfo=None).isoformat()


def from_iso_string(iso_string: str) -> Optional[datetime]:
    """
    Parse ISO 8601 string thành datetime.
    
    Args:
        iso_string: ISO format string
        
    Returns:
        datetime: Parsed datetime (timezone-aware if timezone was in string)
    """
    if not iso_string:
        return None
    
    try:
        # Python 3.11+ supports fromisoformat with timezone
        return datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
    except ValueError:
        return None


def format_vietnam_datetime(dt: datetime, format_str: str = "%H:%M:%S ngày %d/%m/%Y") -> str:
    """
    Format datetime theo định dạng Vietnam friendly.
    
    Args:
        dt: datetime object
        format_str: Format string
        
    Returns:
        str: Formatted datetime string
    """
    if dt is None:
        return ""
    
    vn_time = to_vietnam(dt)
    return vn_time.strftime(format_str)


def get_today_start_utc() -> datetime:
    """
    Lấy thời điểm bắt đầu ngày hôm nay (00:00:00) theo UTC.
    
    Returns:
        datetime: Start of today in UTC
    """
    now = utc_now()
    return now.replace(hour=0, minute=0, second=0, microsecond=0)


def get_today_start_vietnam() -> datetime:
    """
    Lấy thời điểm bắt đầu ngày hôm nay (00:00:00) theo Vietnam timezone,
    nhưng trả về dưới dạng UTC để lưu vào database.
    
    Returns:
        datetime: Start of today (Vietnam) in UTC
    """
    vn_now = vietnam_now()
    vn_start = vn_now.replace(hour=0, minute=0, second=0, microsecond=0)
    return to_utc(vn_start)


# Export for convenience
__all__ = [
    'utc_now',
    'vietnam_now', 
    'to_utc',
    'to_vietnam',
    'to_iso_string',
    'from_iso_string',
    'format_vietnam_datetime',
    'get_today_start_utc',
    'get_today_start_vietnam',
    'VIETNAM_TZ'
]
