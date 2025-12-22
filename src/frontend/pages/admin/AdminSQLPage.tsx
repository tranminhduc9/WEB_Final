import { useState } from 'react';
import AdminHeader from '../../components/admin/AdminHeader';
import Footer from '../../components/client/Footer';
import '../../assets/styles/pages/AdminSQLPage.css';

// Mock columns for results
const mockColumns = ['id', 'name', 'email', 'created_at', 'status'];

// Mock data for query results
const mockResults = [
    { id: 1, name: 'Nguyễn Văn A', email: 'nguyenvana@gmail.com', created_at: '2024-01-15', status: 'active' },
    { id: 2, name: 'Trần Thị B', email: 'tranthib@gmail.com', created_at: '2024-01-16', status: 'active' },
    { id: 3, name: 'Lê Văn C', email: 'levanc@gmail.com', created_at: '2024-01-17', status: 'inactive' },
    { id: 4, name: 'Phạm Thị D', email: 'phamthid@gmail.com', created_at: '2024-01-18', status: 'active' },
    { id: 5, name: 'Hoàng Văn E', email: 'hoangvane@gmail.com', created_at: '2024-01-19', status: 'active' },
];

function AdminSQLPage() {
    const [sqlQuery, setSqlQuery] = useState('SELECT * FROM \nWHERE');
    const [results, setResults] = useState<typeof mockResults>([]);
    const [columns, setColumns] = useState<string[]>([]);
    const [currentPage, setCurrentPage] = useState(1);
    const [isExecuted, setIsExecuted] = useState(false);
    const itemsPerPage = 10;

    // Handle execute query
    const handleExecuteQuery = () => {
        // Mock execution - in real app, this would call API
        console.log('Executing query:', sqlQuery);

        // Simulate results
        setColumns(mockColumns);
        setResults(mockResults);
        setIsExecuted(true);
        setCurrentPage(1);
    };

    // Pagination
    const totalPages = Math.ceil(results.length / itemsPerPage);
    const startIndex = (currentPage - 1) * itemsPerPage;
    const paginatedResults = results.slice(startIndex, startIndex + itemsPerPage);

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
        <div className="admin-sql-page">
            <AdminHeader />

            <main className="admin-sql-main">
                {/* Title Section */}
                <div className="admin-sql-header">
                    <div className="admin-section__accent"></div>
                    <h1 className="admin-sql-title">Truy vấn SQL (Chỉ lấy dữ liệu)</h1>
                </div>

                {/* SQL Query Section */}
                <div className="admin-sql-query-section">
                    <h2 className="admin-sql-query-label">Truy vấn SQL</h2>
                    <div className="admin-sql-editor-container">
                        <textarea
                            className="admin-sql-editor"
                            value={sqlQuery}
                            onChange={(e) => setSqlQuery(e.target.value)}
                            placeholder="SELECT * FROM table_name WHERE condition"
                            spellCheck={false}
                        />
                        <button
                            className="admin-sql-execute-btn"
                            onClick={handleExecuteQuery}
                        >
                            Thực hiện truy vấn
                        </button>
                    </div>
                </div>

                {/* Results Section */}
                {isExecuted && (
                    <>
                        <p className="admin-sql-count">Có {results.length} kết quả</p>

                        <div className="admin-sql-table-container">
                            <table className="admin-sql-table">
                                <thead>
                                    <tr>
                                        {columns.map((col, index) => (
                                            <th key={index}>{col}</th>
                                        ))}
                                    </tr>
                                </thead>
                                <tbody>
                                    {paginatedResults.map((row, rowIndex) => (
                                        <tr key={rowIndex}>
                                            {columns.map((col, colIndex) => (
                                                <td key={colIndex}>{row[col as keyof typeof row]}</td>
                                            ))}
                                        </tr>
                                    ))}
                                    {/* Empty rows to fill table */}
                                    {Array.from({ length: Math.max(0, itemsPerPage - paginatedResults.length) }).map((_, index) => (
                                        <tr key={`empty-${index}`} className="admin-sql-table__empty-row">
                                            {columns.map((_, colIndex) => (
                                                <td key={colIndex}></td>
                                            ))}
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>

                        {/* Pagination */}
                        {totalPages > 0 && (
                            <div className="admin-sql-pagination">
                                <button
                                    className="admin-sql-pagination__nav"
                                    onClick={() => setCurrentPage(1)}
                                    disabled={currentPage === 1}
                                >
                                    «
                                </button>

                                {getPageNumbers().map((page, index) => (
                                    <button
                                        key={index}
                                        className={`admin-sql-pagination__page ${page === currentPage ? 'active' : ''
                                            } ${page === '...' ? 'ellipsis' : ''}`}
                                        onClick={() => typeof page === 'number' && setCurrentPage(page)}
                                        disabled={page === '...'}
                                    >
                                        {page}
                                    </button>
                                ))}

                                <button
                                    className="admin-sql-pagination__nav"
                                    onClick={() => setCurrentPage(totalPages)}
                                    disabled={currentPage === totalPages}
                                >
                                    »
                                </button>
                            </div>
                        )}
                    </>
                )}
            </main>

            <Footer />
        </div>
    );
}

export default AdminSQLPage;
