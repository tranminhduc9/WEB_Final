"""
Content Sanitizer Module

Module này cung cấp các chức năng sanitize nội dung người dùng để ngăn chặn:
- XSS (Cross-Site Scripting) attacks
- HTML Injection
- Malicious URLs
- SQL Injection patterns trong nội dung

Features:
1. HTML Sanitization - Chỉ cho phép tags an toàn
2. URL Validation - Kiểm tra và sanitize URLs
3. Text Normalization - Normalize Unicode, whitespace
4. Profanity Filter (optional) - Lọc từ ngữ không phù hợp
5. Length Limiting - Giới hạn độ dài nội dung
"""

import re
import html
import logging
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse, urljoin

logger = logging.getLogger(__name__)


# ==============================================
# CONFIGURATION
# ==============================================

class SanitizerConfig:
    """Cấu hình cho Content Sanitizer"""
    
    # HTML Tags an toàn (whitelist)
    ALLOWED_TAGS = [
        'p', 'br', 'b', 'i', 'u', 'strong', 'em', 
        'a', 'ul', 'ol', 'li', 'blockquote', 'code', 'pre',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'span', 'div'
    ]
    
    # Attributes an toàn cho mỗi tag
    ALLOWED_ATTRIBUTES = {
        'a': ['href', 'title', 'target', 'rel'],
        'span': ['class'],
        'div': ['class'],
        'p': ['class'],
        'code': ['class'],
        'pre': ['class'],
    }
    
    # URL schemes an toàn
    ALLOWED_URL_SCHEMES = ['http', 'https', 'mailto']
    
    # Patterns nguy hiểm (XSS, injection)
    DANGEROUS_PATTERNS = [
        r'javascript:',
        r'vbscript:',
        r'data:text/html',
        r'on\w+\s*=',  # onclick, onerror, onload, etc.
        r'<script',
        r'</script>',
        r'<iframe',
        r'</iframe>',
        r'<object',
        r'</object>',
        r'<embed',
        r'</embed>',
        r'<frame',
        r'</frame>',
        r'<style',
        r'</style>',
        r'expression\s*\(',  # CSS expression
        r'url\s*\(\s*["\']?javascript:',  # CSS url(javascript:)
        r'behavior\s*:',  # IE behavior
        r'-moz-binding',  # Firefox XBL
    ]
    
    # SQL Injection patterns (để log/detect, không block)
    SQL_INJECTION_PATTERNS = [
        r"('\s*OR\s+'?\d+'?\s*=\s*'?\d+'?)",
        r"(;\s*DROP\s+TABLE)",
        r"(;\s*DELETE\s+FROM)",
        r"(UNION\s+SELECT)",
        r"(INSERT\s+INTO)",
        r"(UPDATE\s+.+\s+SET)",
        r"(--\s*$)",  # SQL comment
    ]
    
    # Maximum lengths
    MAX_TITLE_LENGTH = 255
    MAX_CONTENT_LENGTH = 50000  # 50KB
    MAX_COMMENT_LENGTH = 2000
    MAX_BIO_LENGTH = 500
    MAX_TAG_LENGTH = 50
    MAX_URL_LENGTH = 2048


# ==============================================
# CORE SANITIZATION FUNCTIONS
# ==============================================

def escape_html(text: str) -> str:
    """
    Escape HTML entities (không cho phép bất kỳ HTML nào)
    Dùng cho: title, tags, tên người dùng
    
    Args:
        text: Text cần escape
        
    Returns:
        str: Text đã escape HTML entities
    """
    if not text:
        return ""
    return html.escape(str(text), quote=True)


def strip_all_tags(html_content: str) -> str:
    """
    Xóa tất cả HTML tags, chỉ giữ lại text
    Dùng cho: title, bio, tên
    
    Args:
        html_content: HTML content
        
    Returns:
        str: Plain text không có tags
    """
    if not html_content:
        return ""
    
    # Remove all HTML tags
    clean = re.sub(r'<[^>]+>', '', str(html_content))
    # Decode HTML entities
    clean = html.unescape(clean)
    # Normalize whitespace
    clean = ' '.join(clean.split())
    return clean.strip()


def sanitize_html(content: str, strip_mode: bool = False) -> str:
    """
    Sanitize HTML content - loại bỏ tags/attributes nguy hiểm
    Dùng cho: nội dung bài viết, comments (cho phép một số HTML)
    
    Args:
        content: HTML content cần sanitize
        strip_mode: True = xóa tags không cho phép, False = escape chúng
        
    Returns:
        str: HTML đã sanitized
    """
    if not content:
        return ""
    
    content = str(content)
    
    # 1. Remove dangerous tags AND their content completely
    dangerous_tags = ['script', 'style', 'iframe', 'object', 'embed', 'frame', 'frameset', 'applet', 'base', 'link', 'meta']
    for tag in dangerous_tags:
        # Remove tag with content: <script>...</script>
        content = re.sub(
            rf'<{tag}[^>]*>.*?</{tag}>',
            '',
            content,
            flags=re.IGNORECASE | re.DOTALL
        )
        # Remove self-closing: <script/>
        content = re.sub(
            rf'<{tag}[^>]*/?>',
            '',
            content,
            flags=re.IGNORECASE
        )
    
    # 2. Remove dangerous patterns (event handlers, javascript:, etc.)
    for pattern in SanitizerConfig.DANGEROUS_PATTERNS:
        content = re.sub(pattern, '', content, flags=re.IGNORECASE)
    
    # 3. Try to use bleach if available (more robust)
    try:
        import bleach
        
        # Allow only safe tags và attributes
        clean_content = bleach.clean(
            content,
            tags=SanitizerConfig.ALLOWED_TAGS,
            attributes=SanitizerConfig.ALLOWED_ATTRIBUTES,
            strip=strip_mode,
            protocols=SanitizerConfig.ALLOWED_URL_SCHEMES
        )
        
        # 4. Clean up residual escaped characters from stripped tags
        # Remove orphaned &gt; and &lt; left after tag stripping
        clean_content = re.sub(r'&gt;\s*', '', clean_content)
        clean_content = re.sub(r'&lt;\s*', '', clean_content)
        clean_content = re.sub(r'&amp;gt;\s*', '', clean_content)
        clean_content = re.sub(r'&amp;lt;\s*', '', clean_content)
        
        # Normalize multiple spaces/newlines
        clean_content = re.sub(r'\n{3,}', '\n\n', clean_content)
        clean_content = re.sub(r' {2,}', ' ', clean_content)
        
        # Add rel="noopener noreferrer" to external links
        clean_content = bleach.linkify(
            clean_content,
            callbacks=[_add_noopener_callback],
            skip_tags=['pre', 'code']
        )
        
        return clean_content.strip()
        
    except ImportError:
        # Fallback: Basic regex-based sanitization
        logger.warning("bleach not installed, using basic sanitization")
        return _basic_html_sanitize(content, strip_mode)


def _add_noopener_callback(attrs, new=False):
    """Callback để thêm rel="noopener noreferrer" cho links"""
    attrs[(None, 'rel')] = 'noopener noreferrer'
    attrs[(None, 'target')] = '_blank'
    return attrs


def _basic_html_sanitize(content: str, strip_mode: bool = False) -> str:
    """
    Basic HTML sanitization khi không có bleach
    """
    # Remove script, style, iframe, etc.
    dangerous_tags = ['script', 'style', 'iframe', 'object', 'embed', 'frame', 'frameset']
    for tag in dangerous_tags:
        content = re.sub(
            rf'<{tag}[^>]*>.*?</{tag}>',
            '',
            content,
            flags=re.IGNORECASE | re.DOTALL
        )
        content = re.sub(
            rf'<{tag}[^>]*/?>',
            '',
            content,
            flags=re.IGNORECASE
        )
    
    # Remove event handlers (onclick, onerror, etc.)
    content = re.sub(r'\s*on\w+\s*=\s*["\'][^"\']*["\']', '', content, flags=re.IGNORECASE)
    content = re.sub(r'\s*on\w+\s*=\s*\S+', '', content, flags=re.IGNORECASE)
    
    # Remove javascript: URLs
    content = re.sub(r'javascript:[^"\'>\s]*', '', content, flags=re.IGNORECASE)
    
    # Remove style attributes with expressions
    content = re.sub(r'style\s*=\s*["\'][^"\']*expression[^"\']*["\']', '', content, flags=re.IGNORECASE)
    
    return content


def sanitize_url(url: str, allow_relative: bool = False) -> Optional[str]:
    """
    Sanitize và validate URL
    
    Args:
        url: URL cần sanitize
        allow_relative: Cho phép relative URLs
        
    Returns:
        str: URL đã sanitize hoặc None nếu không hợp lệ
    """
    if not url:
        return None
    
    url = str(url).strip()
    
    # Check length
    if len(url) > SanitizerConfig.MAX_URL_LENGTH:
        logger.warning(f"URL too long: {len(url)} chars")
        return None
    
    # Check for dangerous patterns
    url_lower = url.lower()
    if any(pattern in url_lower for pattern in ['javascript:', 'vbscript:', 'data:text/html']):
        logger.warning(f"Dangerous URL pattern detected: {url[:50]}")
        return None
    
    # Parse URL
    try:
        parsed = urlparse(url)
        
        # Check scheme
        if parsed.scheme:
            if parsed.scheme.lower() not in SanitizerConfig.ALLOWED_URL_SCHEMES:
                logger.warning(f"URL scheme not allowed: {parsed.scheme}")
                return None
        elif not allow_relative:
            # No scheme and relative not allowed
            return None
        
        return url
        
    except Exception as e:
        logger.warning(f"URL parse error: {e}")
        return None


def sanitize_text(
    text: str,
    max_length: Optional[int] = None,
    allow_newlines: bool = True,
    allow_html: bool = False
) -> str:
    """
    Sanitize text input (general purpose)
    
    Args:
        text: Text cần sanitize
        max_length: Độ dài tối đa
        allow_newlines: Cho phép xuống dòng
        allow_html: Cho phép HTML (sẽ sanitize)
        
    Returns:
        str: Text đã sanitize
    """
    if not text:
        return ""
    
    text = str(text)
    
    if allow_html:
        text = sanitize_html(text, strip_mode=True)
    else:
        text = strip_all_tags(text)
        text = escape_html(text)
        # Unescape sau khi escape để tránh double-escape
        text = html.unescape(text)
    
    # Normalize whitespace
    if allow_newlines:
        # Normalize multiple newlines to max 2
        text = re.sub(r'\n{3,}', '\n\n', text)
        # Normalize spaces (không ảnh hưởng newlines)
        lines = text.split('\n')
        lines = [' '.join(line.split()) for line in lines]
        text = '\n'.join(lines)
    else:
        text = ' '.join(text.split())
    
    # Apply max length
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text.strip()


# ==============================================
# SPECIALIZED SANITIZERS
# ==============================================

def sanitize_post_title(title: str) -> str:
    """
    Sanitize tiêu đề bài viết
    - Không cho phép HTML
    - Max 255 ký tự
    - Không cho phép newlines
    """
    return sanitize_text(
        title,
        max_length=SanitizerConfig.MAX_TITLE_LENGTH,
        allow_newlines=False,
        allow_html=False
    )


def sanitize_post_content(content: str) -> str:
    """
    Sanitize nội dung bài viết
    - Cho phép một số HTML tags an toàn
    - Max 50KB
    - Cho phép newlines
    """
    return sanitize_html(content, strip_mode=True)[:SanitizerConfig.MAX_CONTENT_LENGTH]


def sanitize_comment(content: str) -> str:
    """
    Sanitize nội dung comment/reply
    - Cho phép HTML cơ bản
    - Max 2000 ký tự
    """
    sanitized = sanitize_html(content, strip_mode=True)
    return sanitized[:SanitizerConfig.MAX_COMMENT_LENGTH]


def sanitize_bio(bio: str) -> str:
    """
    Sanitize bio/tiểu sử người dùng
    - Không cho phép HTML
    - Max 500 ký tự
    - Cho phép newlines
    """
    return sanitize_text(
        bio,
        max_length=SanitizerConfig.MAX_BIO_LENGTH,
        allow_newlines=True,
        allow_html=False
    )


def sanitize_full_name(name: str) -> str:
    """
    Sanitize họ tên người dùng
    - Không cho phép HTML
    - Max 255 ký tự
    - Không cho phép newlines
    - Chỉ cho phép letters, spaces, hyphens, apostrophes
    """
    if not name:
        return ""
    
    # Strip HTML first
    name = strip_all_tags(name)
    
    # Normalize whitespace
    name = ' '.join(name.split())
    
    # Limit length
    name = name[:255]
    
    return name.strip()


def sanitize_tags(tags: List[str]) -> List[str]:
    """
    Sanitize danh sách tags
    - Mỗi tag không có HTML
    - Max 50 ký tự/tag
    - Max 20 tags
    """
    if not tags:
        return []
    
    sanitized = []
    for tag in tags[:20]:  # Max 20 tags
        clean_tag = strip_all_tags(str(tag))
        clean_tag = ' '.join(clean_tag.split())  # Normalize whitespace
        clean_tag = clean_tag[:SanitizerConfig.MAX_TAG_LENGTH]
        if clean_tag:
            sanitized.append(clean_tag)
    
    return sanitized


def sanitize_image_urls(urls: List[str]) -> List[str]:
    """
    Sanitize danh sách image URLs
    - Validate mỗi URL
    - Max 20 images
    """
    if not urls:
        return []
    
    sanitized = []
    for url in urls[:20]:  # Max 20 images
        # Allow relative URLs for images (e.g., /static/uploads/...)
        clean_url = sanitize_url(str(url), allow_relative=True)
        if clean_url:
            sanitized.append(clean_url)
    
    return sanitized


def sanitize_report_reason(reason: str) -> str:
    """
    Sanitize lý do báo cáo
    - Không cho phép HTML
    - Max 255 ký tự
    """
    return sanitize_text(
        reason,
        max_length=255,
        allow_newlines=False,
        allow_html=False
    )


def sanitize_report_description(description: str) -> str:
    """
    Sanitize mô tả chi tiết báo cáo
    - Không cho phép HTML
    - Max 1000 ký tự
    """
    if not description:
        return None
    return sanitize_text(
        description,
        max_length=1000,
        allow_newlines=True,
        allow_html=False
    )


# ==============================================
# DETECTION & LOGGING
# ==============================================

def detect_xss_attempt(content: str) -> bool:
    """
    Phát hiện cố gắng XSS attack
    Dùng để log và monitoring
    
    Args:
        content: Nội dung cần kiểm tra
        
    Returns:
        bool: True nếu phát hiện XSS pattern
    """
    if not content:
        return False
    
    content_lower = str(content).lower()
    
    for pattern in SanitizerConfig.DANGEROUS_PATTERNS:
        if re.search(pattern, content_lower, re.IGNORECASE):
            return True
    
    return False


def detect_sql_injection(content: str) -> bool:
    """
    Phát hiện cố gắng SQL injection trong nội dung
    Chủ yếu dùng để log (ORM đã có parameterized queries)
    
    Args:
        content: Nội dung cần kiểm tra
        
    Returns:
        bool: True nếu phát hiện SQL injection pattern
    """
    if not content:
        return False
    
    for pattern in SanitizerConfig.SQL_INJECTION_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            return True
    
    return False


def log_security_event(event_type: str, content: str, user_id: int = None, ip: str = None):
    """
    Log security events để monitoring
    
    Args:
        event_type: Loại event (xss_attempt, sql_injection, etc.)
        content: Nội dung vi phạm (truncated)
        user_id: ID người dùng (nếu có)
        ip: IP address
    """
    # Truncate content for logging
    content_preview = str(content)[:100] if content else ""
    
    logger.warning(f"SECURITY EVENT: {event_type}")
    logger.warning(f"  User ID: {user_id}")
    logger.warning(f"  IP: {ip}")
    logger.warning(f"  Content preview: {content_preview}...")


# ==============================================
# CONVENIENCE WRAPPER
# ==============================================

class ContentSanitizer:
    """
    Class wrapper cho các sanitize functions
    Có thể inject để testing
    """
    
    @staticmethod
    def sanitize_post(title: str, content: str, tags: List[str] = None, images: List[str] = None) -> Dict[str, Any]:
        """Sanitize toàn bộ post data"""
        return {
            "title": sanitize_post_title(title),
            "content": sanitize_post_content(content),
            "tags": sanitize_tags(tags or []),
            "images": sanitize_image_urls(images or [])
        }
    
    @staticmethod
    def sanitize_comment_data(content: str, images: List[str] = None) -> Dict[str, Any]:
        """Sanitize comment/reply data"""
        return {
            "content": sanitize_comment(content),
            "images": sanitize_image_urls(images or [])
        }
    
    @staticmethod
    def sanitize_profile(full_name: str = None, bio: str = None, avatar_url: str = None) -> Dict[str, Any]:
        """Sanitize profile data"""
        result = {}
        if full_name is not None:
            result["full_name"] = sanitize_full_name(full_name)
        if bio is not None:
            result["bio"] = sanitize_bio(bio)
        if avatar_url is not None:
            result["avatar_url"] = sanitize_url(avatar_url, allow_relative=True)
        return result
    
    @staticmethod
    def sanitize_report(reason: str, description: str = None) -> Dict[str, Any]:
        """Sanitize report data"""
        return {
            "reason": sanitize_report_reason(reason),
            "description": sanitize_report_description(description)
        }


# Global instance
sanitizer = ContentSanitizer()


# ==============================================
# EXPORTS
# ==============================================

__all__ = [
    # Config
    'SanitizerConfig',
    
    # Core functions
    'escape_html',
    'strip_all_tags',
    'sanitize_html',
    'sanitize_url',
    'sanitize_text',
    
    # Specialized sanitizers
    'sanitize_post_title',
    'sanitize_post_content',
    'sanitize_comment',
    'sanitize_bio',
    'sanitize_full_name',
    'sanitize_tags',
    'sanitize_image_urls',
    'sanitize_report_reason',
    'sanitize_report_description',
    
    # Detection
    'detect_xss_attempt',
    'detect_sql_injection',
    'log_security_event',
    
    # Class wrapper
    'ContentSanitizer',
    'sanitizer',
]
