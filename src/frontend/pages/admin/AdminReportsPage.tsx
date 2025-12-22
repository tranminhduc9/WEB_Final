import { useState } from 'react';
import AdminHeader from '../../components/admin/AdminHeader';
import Footer from '../../components/client/Footer';
import { Icons } from '../../config/constants';
import '../../assets/styles/pages/AdminReportsPage.css';

// Mock data for reports
const mockReports = [
    { id: 1, type: 'Bài viết', reason: 'Nội dung không phù hợp', reporter: 'nguyenvana', isResolved: false },
    { id: 2, type: 'Comment', reason: 'Spam', reporter: 'tranthib', isResolved: false },
    { id: 3, type: 'Bài viết', reason: 'Thông tin sai lệch', reporter: 'levanc', isResolved: true },
    { id: 4, type: 'Comment', reason: 'Ngôn từ thù địch', reporter: 'phamthid', isResolved: false },
    { id: 5, type: 'Bài viết', reason: 'Vi phạm bản quyền', reporter: 'hoangvane', isResolved: false },
    { id: 6, type: 'Comment', reason: 'Quấy rối', reporter: 'ngothif', isResolved: true },
    { id: 7, type: 'Bài viết', reason: 'Nội dung bạo lực', reporter: 'vuthig', isResolved: false },
    { id: 8, type: 'Comment', reason: 'Spam', reporter: 'doanvanh', isResolved: false },
    { id: 9, type: 'Bài viết', reason: 'Thông tin cá nhân', reporter: 'lythii', isResolved: true },
    { id: 10, type: 'Comment', reason: 'Lừa đảo', reporter: 'tranvanj', isResolved: false },
];

function AdminReportsPage() {
    const [currentPage, setCurrentPage] = useState(1);
    const [reports, setReports] = useState(mockReports);
    const itemsPerPage = 10;

    // Pagination
    const totalPages = Math.ceil(reports.length / itemsPerPage);
    const startIndex = (currentPage - 1) * itemsPerPage;
    const paginatedReports = reports.slice(startIndex, startIndex + itemsPerPage);

    // Handle process violation
    const handleProcessViolation = (reportId: number) => {
        console.log('Process violation for report:', reportId);
        // TODO: Open modal or navigate to process page
    };

    // Handle mark as reviewed
    const handleMarkReviewed = (reportId: number) => {
        setReports(prevReports =>
            prevReports.map(report =>
                report.id === reportId ? { ...report, isResolved: true } : report
            )
        );
    };

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

                {/* Reports Table */}
                <div className="admin-reports-table-container">
                    <table className="admin-reports-table">
                        <thead>
                            <tr>
                                <th>report_id</th>
                                <th>type (Bài viết, comment)</th>
                                <th>Lý do</th>
                                <th>Người báo cáo</th>
                                <th colSpan={2}>Chức năng</th>
                            </tr>
                        </thead>
                        <tbody>
                            {paginatedReports.map((report) => (
                                <tr key={report.id} className={report.isResolved ? 'resolved' : ''}>
                                    <td>{report.id}</td>
                                    <td>{report.type}</td>
                                    <td>{report.reason}</td>
                                    <td>{report.reporter}</td>
                                    <td>
                                        <button
                                            className="admin-reports-action-btn"
                                            onClick={() => handleProcessViolation(report.id)}
                                            disabled={report.isResolved}
                                        >
                                            <Icons.Ban className="admin-reports-action-icon" />
                                            Xử lý vi phạm
                                        </button>
                                    </td>
                                    <td>
                                        <button
                                            className="admin-reports-action-btn admin-reports-action-btn--reviewed"
                                            onClick={() => handleMarkReviewed(report.id)}
                                            disabled={report.isResolved}
                                        >
                                            <Icons.Check className="admin-reports-action-icon" />
                                            {report.isResolved ? 'Đã xem' : 'Đã xem'}
                                        </button>
                                    </td>
                                </tr>
                            ))}
                            {/* Empty rows to fill table */}
                            {Array.from({ length: Math.max(0, itemsPerPage - paginatedReports.length) }).map((_, index) => (
                                <tr key={`empty-${index}`} className="admin-reports-table__empty-row">
                                    <td></td>
                                    <td></td>
                                    <td></td>
                                    <td></td>
                                    <td></td>
                                    <td></td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                {/* Pagination */}
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
            </main>

            <Footer />
        </div>
    );
}

export default AdminReportsPage;
