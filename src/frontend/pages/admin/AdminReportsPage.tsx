import { useState, useEffect, useCallback } from 'react';
import AdminHeader from '../../components/admin/AdminHeader';
import Footer from '../../components/client/Footer';
import { Icons } from '../../config/constants';
import { adminService } from '../../services';
import type { AdminReport } from '../../types/admin';
import type { Pagination } from '../../types/models';
import '../../assets/styles/pages/AdminReportsPage.css';

// Format date helper
const formatDate = (dateString?: string | null): string => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('vi-VN');
};

function AdminReportsPage() {
    const [reports, setReports] = useState<AdminReport[]>([]);
    const [pagination, setPagination] = useState<Pagination | null>(null);
    const [resolvedIds, setResolvedIds] = useState<Set<string>>(new Set());
    const [currentPage, setCurrentPage] = useState(1);
    const [isLoading, setIsLoading] = useState(true);
    const [actionLoading, setActionLoading] = useState<string | null>(null);

    const itemsPerPage = 10;

    // Fetch reports from API with server-side pagination
    const fetchReports = useCallback(async () => {
        setIsLoading(true);
        try {
            const response = await adminService.getReports({
                page: currentPage,
                limit: itemsPerPage
            });
            if (response.success && response.data) {
                setReports(response.data);
                if (response.pagination) {
                    setPagination(response.pagination);
                }
            } else {
                setReports([]);
            }
        } catch (error) {
            console.error('Error fetching reports:', error);
            setReports([]);
        } finally {
            setIsLoading(false);
        }
    }, [currentPage]);

    useEffect(() => {
        fetchReports();
    }, [fetchReports]);

    // Use server pagination
    const totalPages = pagination?.total_pages || 1;
    const totalItems = pagination?.total_items || reports.length;

    // Handle process violation - delete post/comment
    const handleProcessViolation = async (report: AdminReport) => {
        const confirmMsg = report.target_type === 'post'
            ? 'Bạn có chắc chắn muốn xóa bài viết này?'
            : 'Bạn có chắc chắn muốn xóa bình luận này?';

        if (!window.confirm(confirmMsg)) return;

        setActionLoading(report._id);
        try {
            let response;
            if (report.target_type === 'post') {
                response = await adminService.deletePost(report.target_id, `Xử lý báo cáo: ${report.reason}`);
            } else {
                response = await adminService.deleteComment(report.target_id);
            }

            if (response.success) {
                setResolvedIds(prev => new Set([...prev, report._id]));
                alert('Đã xử lý vi phạm thành công!');
            } else {
                alert('Không thể xử lý vi phạm');
            }
        } catch (error) {
            console.error('Error processing violation:', error);
            alert('Có lỗi xảy ra khi xử lý vi phạm');
        } finally {
            setActionLoading(null);
        }
    };

    // Handle mark as reviewed (dismiss)
    const handleMarkReviewed = async (reportId: string) => {
        setActionLoading(reportId);
        try {
            const response = await adminService.dismissReport(reportId);
            if (response.success) {
                setResolvedIds(prev => new Set([...prev, reportId]));
                alert('Đã bỏ qua báo cáo thành công!');
            } else {
                alert('Không thể bỏ qua báo cáo');
            }
        } catch (error) {
            console.error('Error dismissing report:', error);
            alert('Có lỗi xảy ra khi bỏ qua báo cáo');
        } finally {
            setActionLoading(null);
        }
    };

    // Check if report is resolved
    const isResolved = (reportId: string) => resolvedIds.has(reportId);

    // Handle page change
    const handlePageChange = (page: number) => {
        setCurrentPage(page);
        window.scrollTo({ top: 0, behavior: 'smooth' });
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

    return (
        <div className="admin-reports-page">
            <AdminHeader />

            <main className="admin-reports-main">
                {/* Title Section */}
                <div className="admin-reports-header">
                    <div className="admin-section__accent"></div>
                    <h1 className="admin-reports-title">Quản lý báo cáo</h1>
                </div>

                {/* Results Count */}
                <p className="admin-reports-count">
                    {isLoading ? 'Đang tải...' : `Có ${totalItems} báo cáo (Trang ${currentPage}/${totalPages})`}
                </p>

                {/* Reports Table */}
                <div className="admin-reports-table-container">
                    <table className="admin-reports-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Loại</th>
                                <th>Lý do</th>
                                <th>Chi tiết</th>
                                <th>Người báo cáo</th>
                                <th>Ngày tạo</th>
                                <th colSpan={2}>Chức năng</th>
                            </tr>
                        </thead>
                        <tbody>
                            {isLoading ? (
                                <tr>
                                    <td colSpan={8} className="admin-reports-loading">Đang tải...</td>
                                </tr>
                            ) : reports.length === 0 ? (
                                <tr>
                                    <td colSpan={8} className="admin-reports-empty">Không có báo cáo nào</td>
                                </tr>
                            ) : (
                                reports.map((report) => (
                                    <tr key={report._id} className={isResolved(report._id) ? 'resolved' : ''}>
                                        <td>{report._id.slice(-6)}</td>
                                        <td>
                                            <span className={`admin-reports__type admin-reports__type--${report.target_type}`}>
                                                {report.target_type === 'post' ? 'Bài viết' : 'Comment'}
                                            </span>
                                        </td>
                                        <td>{report.reason}</td>
                                        <td className="admin-reports__description">
                                            {report.description || <em className="text-muted">Không có mô tả</em>}
                                        </td>
                                        <td>{report.reporter?.full_name || 'N/A'}</td>
                                        <td>{formatDate(report.created_at)}</td>
                                        <td>
                                            <button
                                                className="admin-reports-action-btn"
                                                onClick={() => handleProcessViolation(report)}
                                                disabled={isResolved(report._id) || actionLoading === report._id}
                                            >
                                                <Icons.Ban className="admin-reports-action-icon" />
                                                {actionLoading === report._id ? '...' : 'Xử lý'}
                                            </button>
                                        </td>
                                        <td>
                                            <button
                                                className="admin-reports-action-btn admin-reports-action-btn--reviewed"
                                                onClick={() => handleMarkReviewed(report._id)}
                                                disabled={isResolved(report._id)}
                                            >
                                                <Icons.Check className="admin-reports-action-icon" />
                                                {isResolved(report._id) ? 'Đã xem' : 'Bỏ qua'}
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>

                {/* Pagination */}
                {totalPages > 1 && (
                    <div className="admin-reports-pagination">
                        <button
                            className="admin-reports-pagination__nav"
                            onClick={() => handlePageChange(1)}
                            disabled={currentPage === 1}
                        >
                            «
                        </button>
                        <button
                            className="admin-reports-pagination__nav"
                            onClick={() => handlePageChange(currentPage - 1)}
                            disabled={currentPage === 1}
                        >
                            ‹
                        </button>

                        {getPageNumbers().map((page, index) => (
                            <button
                                key={index}
                                className={`admin-reports-pagination__page ${page === currentPage ? 'active' : ''
                                    } ${page === '...' ? 'ellipsis' : ''}`}
                                onClick={() => typeof page === 'number' && handlePageChange(page)}
                                disabled={page === '...'}
                            >
                                {page}
                            </button>
                        ))}

                        <button
                            className="admin-reports-pagination__nav"
                            onClick={() => handlePageChange(currentPage + 1)}
                            disabled={currentPage === totalPages}
                        >
                            ›
                        </button>
                        <button
                            className="admin-reports-pagination__nav"
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

export default AdminReportsPage;
