"""
Utils package - Shared utilities for the application
"""

from .image_helpers import (
    get_main_image_url,
    get_all_place_images,
    get_all_place_images_relative,
    normalize_image_url,
    normalize_image_list,
    normalize_urls_to_relative_paths,
    extract_relative_path_from_url,
    get_avatar_url,
    get_post_images,
    format_place_compact_images
)
from .place_helpers import get_place_compact, get_user_compact
from .content_sanitizer import (
    sanitizer,
    sanitize_post_title,
    sanitize_post_content,
    sanitize_comment,
    sanitize_bio,
    sanitize_full_name,
    sanitize_tags,
    sanitize_image_urls,
    sanitize_report_reason,
    sanitize_report_description,
    detect_xss_attempt,
    log_security_event
)

__all__ = [
    # Image helpers
    'get_main_image_url',
    'get_all_place_images',
    'get_all_place_images_relative',
    'normalize_image_url',
    'normalize_image_list',
    'normalize_urls_to_relative_paths',
    'extract_relative_path_from_url',
    'get_avatar_url',
    'get_post_images',
    'format_place_compact_images',
    # Place helpers
    'get_place_compact',
    'get_user_compact',
    # Content sanitizer
    'sanitizer',
    'sanitize_post_title',
    'sanitize_post_content',
    'sanitize_comment',
    'sanitize_bio',
    'sanitize_full_name',
    'sanitize_tags',
    'sanitize_image_urls',
    'sanitize_report_reason',
    'sanitize_report_description',
    'detect_xss_attempt',
    'log_security_event'
]
