/**
 * Time Utilities - Unified time formatting functions
 */

/**
 * Format a date string into a human-readable relative time string (Vietnamese)
 * Handles edge cases: negative time, future dates, invalid strings
 */
export function formatTimeAgo(isoString?: string): string {
    if (!isoString) return 'Vừa xong';

    try {
        const date = new Date(isoString);
        if (isNaN(date.getTime())) return 'Không rõ';

        const diffMs = Date.now() - date.getTime();

        // Handle negative time (future dates) or very recent posts
        if (diffMs < 60000) return 'Vừa xong';

        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);

        if (diffDays > 7) {
            return date.toLocaleDateString('vi-VN', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric'
            });
        }
        if (diffDays > 0) return `${diffDays} ngày trước`;
        if (diffHours > 0) return `${diffHours} giờ trước`;
        return `${diffMins} phút trước`;
    } catch {
        return 'Không rõ';
    }
}
