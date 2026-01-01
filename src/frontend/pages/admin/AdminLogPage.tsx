/**
 * Admin Log Page - Quản lý log hoạt động
 * Route: /admin/log
 */

import { useState, useEffect } from 'react';
import AdminHeader from '../../components/admin/AdminHeader';
import Footer from '../../components/client/Footer';
import { adminService } from '../../services';
import '../../assets/styles/pages/AdminLogPage.css';

interface AuditLog {
    id: number;
    user_id: number;
    user?: {
        id: number;
        full_name: string;
        email: string;
    };
    action: string;
    details?: string;
    ip_address?: string;
    created_at: string;
}

interface PaginationInfo {
    total: number;
    limit: number;
    offset: number;
}

function AdminLogPage() {
    const [logs, setLogs] = useState<AuditLog[]>([]);
    const [pagination, setPagination] = useState<PaginationInfo>({ total: 0, limit: 10, offset: 0 });
    const [currentPage, setCurrentPage] = useState(1);
    const [isLoading, setIsLoading] = useState(true);
    const [actionFilter, setActionFilter] = useState<string>('');
    const [userIdFilter, setUserIdFilter] = useState<string>('');

    const itemsPerPage = 10;

    // Format time
    const formatTime = (dateStr: string): string => {
        const date = new Date(dateStr);
        return date.toLocaleString('vi-VN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    // Fetch logs from API
    useEffect(() => {
        const fetchLogs = async () => {
            setIsLoading(true);
            try {
                const offset = (currentPage - 1) * itemsPerPage;
                const response = await adminService.getAuditLogs({
                    limit: itemsPerPage,
                    offset,
                    user_id: userIdFilter ? parseInt(userIdFilter) : undefined,
                    action_type: actionFilter || undefined
                });

                if (response.success && response.data) {
                    setLogs(response.data.logs || []);
                    setPagination({
                        total: response.data.total || 0,
                        limit: response.data.limit || itemsPerPage,
                        offset: response.data.offset || 0
                    });
                }
            } catch (error) {
                console.error('Error fetching logs:', error);
            } finally {
                setIsLoading(false);
            }
        };

        fetchLogs();
    }, [currentPage, actionFilter, userIdFilter]);

    // Pagination
    const totalPages = Math.ceil(pagination.total / itemsPerPage) || 1;

    const handlePageChange = (page: number) => {
        if (page >= 1 && page <= totalPages) {
            setCurrentPage(page);
        }
    };

    // Generate page numbers
    const getPageNumbers = () => {
        const pages: (number | string)[] = [];
        if (totalPages <= 5) {
            for (let i = 1; i <= totalPages; i++) pages.push(i);
        } else {
            pages.push(1);
            if (currentPage > 3) pages.push('...');

            const start = Math.max(2, currentPage - 1);
            const end = Math.min(totalPages - 1, currentPage + 1);
            for (let i = start; i <= end; i++) pages.push(i);

            if (currentPage < totalPages - 2) pages.push('...');
            pages.push(totalPages);
        }
        return pages;
    };

    // Action types for filter
    const actionTypes = [
        { value: '', label: 'Tất cả' },
        { value: 'login', label: 'Đăng nhập' },
        { value: 'logout', label: 'Đăng xuất' },
        { value: 'register', label: 'Đăng ký' },
        { value: 'password_change', label: 'Đổi mật khẩu' },
        { value: 'profile_update', label: 'Cập nhật profile' },
        { value: 'create_post', label: 'Tạo bài viết' },
        { value: 'like_post', label: 'Like bài viết' },
        { value: 'create_comment', label: 'Tạo comment' },
        { value: 'report_content', label: 'Báo cáo' },
    ];

    return (
        <div className="admin-log-page">
            <AdminHeader />

            <main className="admin-log-main">
                {/* Title Section */}
                <div className="admin-log-header">
                    <div className="admin-section__accent"></div>
                    <h1 className="admin-log-title">Log hoạt động</h1>
                </div>

                {/* Filter */}
                <div className="admin-log-filters">
                    <input
                        type="number"
                        className="admin-log-filter-input"
                        placeholder="Lọc theo User ID"
                        value={userIdFilter}
                        onChange={(e) => {
                            setUserIdFilter(e.target.value);
                            setCurrentPage(1);
                        }}
                    />
                    <select
                        className="admin-log-filter-select"
                        value={actionFilter}
                        onChange={(e) => {
                            setActionFilter(e.target.value);
                            setCurrentPage(1);
                        }}
                    >
                        {actionTypes.map(type => (
                            <option key={type.value} value={type.value}>{type.label}</option>
                        ))}
                    </select>
                    <span className="admin-log-count">
                        {isLoading ? 'Đang tải...' : `Tổng: ${pagination.total} logs`}
                    </span>
                </div>

                {/* Table */}
                <div className="admin-log-table-container">
                    <table className="admin-log-table">
                        <thead>
                            <tr>
                                <th>user_id</th>
                                <th>action</th>
                                <th>ip</th>
                                <th>time</th>
                                <th>details</th>
                            </tr>
                        </thead>
                        <tbody>
                            {isLoading ? (
                                <tr>
                                    <td colSpan={5} className="admin-log-loading">Đang tải...</td>
                                </tr>
                            ) : logs.length === 0 ? (
                                <tr>
                                    <td colSpan={5} className="admin-log-empty">Không có log nào</td>
                                </tr>
                            ) : (
                                logs.map((log) => (
                                    <tr key={log.id}>
                                        <td>{log.user_id}</td>
                                        <td>{log.action}</td>
                                        <td>{log.ip_address || '-'}</td>
                                        <td>{formatTime(log.created_at)}</td>
                                        <td className="admin-log-details">{log.details || '-'}</td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>

                {/* Pagination */}
                {totalPages > 1 && (
                    <div className="admin-log-pagination">
                        <button
                            className="admin-log-pagination__nav"
                            onClick={() => handlePageChange(1)}
                            disabled={currentPage === 1}
                        >
                            «
                        </button>

                        {getPageNumbers().map((page, index) => (
                            <button
                                key={index}
                                className={`admin-log-pagination__page ${page === currentPage ? 'active' : ''
                                    } ${page === '...' ? 'ellipsis' : ''}`}
                                onClick={() => typeof page === 'number' && handlePageChange(page)}
                                disabled={page === '...'}
                            >
                                {page}
                            </button>
                        ))}

                        <button
                            className="admin-log-pagination__nav"
                            onClick={() => handlePageChange(totalPages)}
                            disabled={currentPage === totalPages}
                        >
                            »
                        </button>
                    </div>
                )}
            </main>

            <Footer />
        </div>
    );
}

export default AdminLogPage;
