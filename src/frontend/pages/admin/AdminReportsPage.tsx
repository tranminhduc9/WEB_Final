import { useState, useEffect } from 'react';
import AdminHeader from '../../components/admin/AdminHeader';
import Footer from '../../components/client/Footer';
import { Icons } from '../../config/constants';
import { adminService } from '../../services';
import type { AdminReport } from '../../types/admin';
import '../../assets/styles/pages/AdminReportsPage.css';

// Mock data for fallback
const mockReports: AdminReport[] = [
    { _id: '1', target_type: 'post', target_id: 'post-123', reason: 'Nội dung không phù hợp', reporter: { id: 1, full_name: 'nguyenvana' }, created_at: '2024-12-28' },
    { _id: '2', target_type: 'comment', target_id: 'cmt-456', reason: 'Spam', reporter: { id: 2, full_name: 'tranthib' }, created_at: '2024-12-27' },
    { _id: '3', target_type: 'post', target_id: 'post-789', reason: 'Thông tin sai lệch', reporter: { id: 3, full_name: 'levanc' }, created_at: '2024-12-26' },
    { _id: '4', target_type: 'comment', target_id: 'cmt-101', reason: 'Ngôn từ thù địch', reporter: { id: 4, full_name: 'phamthid' }, created_at: '2024-12-25' },
    { _id: '5', target_type: 'post', target_id: 'post-102', reason: 'Vi phạm bản quyền', reporter: { id: 5, full_name: 'hoangvane' }, created_at: '2024-12-24' },
];

function AdminReportsPage() {
    const [reports, setReports] = useState<AdminReport[]>([]);
    const [resolvedIds, setResolvedIds] = useState<Set<string>>(new Set());
    const [currentPage, setCurrentPage] = useState(1);
    const [isLoading, setIsLoading] = useState(true);
    const [actionLoading, setActionLoading] = useState<string | null>(null);
    const itemsPerPage = 10;

    // Fetch reports from API
    useEffect(() => {
        const fetchReports = async () => {
            setIsLoading(true);
            try {
                const response = await adminService.getReports();
                if (response.success && response.data && response.data.length > 0) {
                    setReports(response.data);
                } else {
                    console.log('No reports from API, using mock data');
                    setReports(mockReports);
                }
            } catch (error) {
                console.error('Error fetching reports:', error);
                setReports(mockReports);
            } finally {
                setIsLoading(false);
            }
        };

        fetchReports();
    }, []);

    // Pagination
    const totalPages = Math.ceil(reports.length / itemsPerPage);
    const startIndex = (currentPage - 1) * itemsPerPage;
    const paginatedReports = reports.slice(startIndex, startIndex + itemsPerPage);

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
    const handleMarkReviewed = (reportId: string) => {
        setResolvedIds(prev => new Set([...prev, reportId]));
    };

    // Check if report is resolved
    const isResolved = (reportId: string) => resolvedIds.has(reportId);

    // Generate page numbers
    const getPageNumbers = () => {
        const pages: (number | string)[] = [];
        if (totalPages <= 5) {
            for (let i = 1; i <= totalPages; i++) pages.push(i);
        } else {
            pages.push(1, 2, 3);
            if (totalPages > 4) pages.push('...');
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
                    {isLoading ? 'Đang tải...' : `Có ${reports.length} báo cáo`}
                </p>

                {/* Reports Table */}
                <div className="admin-reports-table-container">
                    <table className="admin-reports-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Loại</th>
                                <th>Lý do</th>
                                <th>Người báo cáo</th>
                                <th colSpan={2}>Chức năng</th>
                            </tr>
                        </thead>
                        <tbody>
                            {isLoading ? (
                                <tr>
                                    <td colSpan={6} className="admin-reports-loading">Đang tải...</td>
                                </tr>
                            ) : paginatedReports.length === 0 ? (
                                <tr>
                                    <td colSpan={6} className="admin-reports-empty">Không có báo cáo nào</td>
                                </tr>
                            ) : (
                                paginatedReports.map((report) => (
                                    <tr key={report._id} className={isResolved(report._id) ? 'resolved' : ''}>
                                        <td>{report._id.slice(-6)}</td>
                                        <td>{report.target_type === 'post' ? 'Bài viết' : 'Comment'}</td>
                                        <td>{report.reason}</td>
                                        <td>{report.reporter?.full_name || 'N/A'}</td>
                                        <td>
                                            <button
                                                className="admin-reports-action-btn"
                                                onClick={() => handleProcessViolation(report)}
                                                disabled={isResolved(report._id) || actionLoading === report._id}
                                            >
                                                <Icons.Ban className="admin-reports-action-icon" />
                                                {actionLoading === report._id ? 'Đang xử lý...' : 'Xử lý vi phạm'}
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
                            onClick={() => setCurrentPage(1)}
                            disabled={currentPage === 1}
                        >
                            «
                        </button>

                        {getPageNumbers().map((page, index) => (
                            <button
                                key={index}
                                className={`admin-reports-pagination__page ${page === currentPage ? 'active' : ''
                                    } ${page === '...' ? 'ellipsis' : ''}`}
                                onClick={() => typeof page === 'number' && setCurrentPage(page)}
                                disabled={page === '...'}
                            >
                                {page}
                            </button>
                        ))}

                        <button
                            className="admin-reports-pagination__nav"
                            onClick={() => setCurrentPage(totalPages)}
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

