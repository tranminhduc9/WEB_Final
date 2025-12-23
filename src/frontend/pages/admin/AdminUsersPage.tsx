import { useState } from 'react';
import AdminHeader from '../../components/admin/AdminHeader';
import Footer from '../../components/client/Footer';
import { Icons } from '../../config/constants';
import '../../assets/styles/pages/AdminUsersPage.css';

// Mock data for users
const mockUsers = [
    { id: 1, username: 'nguyenvana', email: 'nguyenvana@gmail.com', reputation: 4.5, isBanned: false },
    { id: 2, username: 'tranthib', email: 'tranthib@gmail.com', reputation: 3.8, isBanned: false },
    { id: 3, username: 'levanc', email: 'levanc@gmail.com', reputation: 4.2, isBanned: true },
    { id: 4, username: 'phamthid', email: 'phamthid@gmail.com', reputation: 4.7, isBanned: false },
    { id: 5, username: 'hoangvane', email: 'hoangvane@gmail.com', reputation: 3.5, isBanned: false },
    { id: 6, username: 'ngothif', email: 'ngothif@gmail.com', reputation: 4.0, isBanned: false },
    { id: 7, username: 'vuthig', email: 'vuthig@gmail.com', reputation: 4.8, isBanned: false },
    { id: 8, username: 'doanvanh', email: 'doanvanh@gmail.com', reputation: 3.2, isBanned: true },
    { id: 9, username: 'lythii', email: 'lythii@gmail.com', reputation: 4.4, isBanned: false },
    { id: 10, username: 'tranvanj', email: 'tranvanj@gmail.com', reputation: 3.9, isBanned: false },
];

function AdminUsersPage() {
    const [searchQuery, setSearchQuery] = useState('');
    const [currentPage, setCurrentPage] = useState(1);
    const [users, setUsers] = useState(mockUsers);
    const itemsPerPage = 10;

    // Filter users based on search
    const filteredUsers = users.filter(user =>
        user.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
        user.email.toLowerCase().includes(searchQuery.toLowerCase())
    );

    // Pagination
    const totalPages = Math.ceil(filteredUsers.length / itemsPerPage);
    const startIndex = (currentPage - 1) * itemsPerPage;
    const paginatedUsers = filteredUsers.slice(startIndex, startIndex + itemsPerPage);

    // Handle ban/unban
    const handleBanToggle = (userId: number) => {
        setUsers(prevUsers =>
            prevUsers.map(user =>
                user.id === userId ? { ...user, isBanned: !user.isBanned } : user
            )
        );
    };

    // Handle delete
    const handleDelete = (userId: number) => {
        if (window.confirm('Bạn có chắc chắn muốn xóa người dùng này?')) {
            setUsers(prevUsers => prevUsers.filter(user => user.id !== userId));
        }
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
        <div className="admin-users-page">
            <AdminHeader />

            <main className="admin-users-main">
                {/* Title Section */}
                <div className="admin-users-header">
                    <div className="admin-section__accent"></div>
                    <h1 className="admin-users-title">Quản lý người dùng</h1>
                </div>

                {/* Search Bar */}
                <div className="admin-users-search">
                    <input
                        type="text"
                        placeholder="Tìm kiếm người dùng"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="admin-users-search__input"
                    />
                    <Icons.Search className="admin-users-search__icon" />
                </div>

                {/* Results Count */}
                <p className="admin-users-count">Có {filteredUsers.length} kết quả</p>

                {/* Users Table */}
                <div className="admin-users-table-container">
                    <table className="admin-users-table">
                        <thead>
                            <tr>
                                <th>user_id</th>
                                <th>user_name</th>
                                <th>email</th>
                                <th>Độ uy tín</th>
                                <th colSpan={2}>Chức năng</th>
                            </tr>
                        </thead>
                        <tbody>
                            {paginatedUsers.map((user) => (
                                <tr key={user.id}>
                                    <td>{user.id}</td>
                                    <td>{user.username}</td>
                                    <td>{user.email}</td>
                                    <td>{user.reputation}</td>
                                    <td>
                                        <button
                                            className="admin-users-action-btn"
                                            onClick={() => handleBanToggle(user.id)}
                                        >
                                            <Icons.Ban className="admin-users-action-icon" />
                                            {user.isBanned ? 'Unban' : 'Ban/Unban'}
                                        </button>
                                    </td>
                                    <td>
                                        <button
                                            className="admin-users-action-btn admin-users-action-btn--delete"
                                            onClick={() => handleDelete(user.id)}
                                        >
                                            <Icons.Ban className="admin-users-action-icon" />
                                            Delete
                                        </button>
                                    </td>
                                </tr>
                            ))}
                            {/* Empty rows to fill table */}
                            {Array.from({ length: Math.max(0, itemsPerPage - paginatedUsers.length) }).map((_, index) => (
                                <tr key={`empty-${index}`} className="admin-users-table__empty-row">
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
                <div className="admin-users-pagination">
                    <button
                        className="admin-users-pagination__nav"
                        onClick={() => setCurrentPage(1)}
                        disabled={currentPage === 1}
                    >
                        «
                    </button>

                    {getPageNumbers().map((page, index) => (
                        <button
                            key={index}
                            className={`admin-users-pagination__page ${page === currentPage ? 'active' : ''
                                } ${page === '...' ? 'ellipsis' : ''}`}
                            onClick={() => typeof page === 'number' && setCurrentPage(page)}
                            disabled={page === '...'}
                        >
                            {page}
                        </button>
                    ))}

                    <button
                        className="admin-users-pagination__nav"
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

export default AdminUsersPage;
