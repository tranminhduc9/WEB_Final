import { useState, useEffect } from 'react';
import AdminHeader from '../../components/admin/AdminHeader';
import Footer from '../../components/client/Footer';
import { Icons } from '../../config/constants';
import { adminService } from '../../services';
import type { AdminUser } from '../../types/admin';
import '../../assets/styles/pages/AdminUsersPage.css';

// Mock data fallback
const mockUsers: AdminUser[] = [
    { id: 1, full_name: 'Nguyễn Văn A', email: 'nguyenvana@gmail.com', reputation_score: 45, is_active: true, role_id: 3, created_at: '2024-01-15' },
    { id: 2, full_name: 'Trần Thị B', email: 'tranthib@gmail.com', reputation_score: 38, is_active: true, role_id: 3, created_at: '2024-02-20' },
    { id: 3, full_name: 'Lê Văn C', email: 'levanc@gmail.com', reputation_score: 42, is_active: false, ban_reason: 'Vi phạm quy định', role_id: 3, created_at: '2024-03-10' },
    { id: 4, full_name: 'Phạm Thị D', email: 'phamthid@gmail.com', reputation_score: 47, is_active: true, role_id: 2, created_at: '2024-01-05' },
    { id: 5, full_name: 'Hoàng Văn E', email: 'hoangvane@gmail.com', reputation_score: 35, is_active: true, role_id: 3, created_at: '2024-04-12' },
];

// Role mapping
const getRoleName = (roleId: number): string => {
    switch (roleId) {
        case 1: return 'Admin';
        case 2: return 'Moderator';
        default: return 'User';
    }
};

function AdminUsersPage() {
    const [users, setUsers] = useState<AdminUser[]>([]);
    const [searchQuery, setSearchQuery] = useState('');
    const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'banned'>('all');
    const [currentPage, setCurrentPage] = useState(1);
    const [totalItems, setTotalItems] = useState(0);
    const [isLoading, setIsLoading] = useState(true);
    const [banModal, setBanModal] = useState<{ open: boolean; userId: number | null; userName: string }>({ open: false, userId: null, userName: '' });
    const [banReason, setBanReason] = useState('');
    const [actionLoading, setActionLoading] = useState<number | null>(null);

    const itemsPerPage = 10;

    // Fetch users from API
    useEffect(() => {
        const fetchUsers = async () => {
            setIsLoading(true);
            try {
                const response = await adminService.getUsers({
                    status: statusFilter === 'all' ? undefined : statusFilter,
                    page: currentPage,
                });

                if (response.success && response.data) {
                    setUsers(response.data);
                    setTotalItems(response.pagination?.total_items || response.data.length);
                } else {
                    setUsers(mockUsers);
                    setTotalItems(mockUsers.length);
                }
            } catch (error) {
                console.error('Error fetching users:', error);
                setUsers(mockUsers);
                setTotalItems(mockUsers.length);
            } finally {
                setIsLoading(false);
            }
        };

        fetchUsers();
    }, [statusFilter, currentPage]);

    // Filter users based on search (client-side search)
    const filteredUsers = users.filter(user =>
        user.full_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        user.email.toLowerCase().includes(searchQuery.toLowerCase())
    );

    // Pagination
    const totalPages = Math.ceil(totalItems / itemsPerPage);

    // Handle ban user
    const handleBan = async () => {
        if (!banModal.userId || !banReason.trim()) return;

        setActionLoading(banModal.userId);
        try {
            const response = await adminService.banUser(banModal.userId, banReason.trim());
            if (response.success) {
                setUsers(prev => prev.map(user =>
                    user.id === banModal.userId
                        ? { ...user, is_active: false, ban_reason: banReason.trim() }
                        : user
                ));
                setBanModal({ open: false, userId: null, userName: '' });
                setBanReason('');
            } else {
                alert('Không thể ban người dùng');
            }
        } catch (error) {
            console.error('Error banning user:', error);
            alert('Đã xảy ra lỗi khi ban người dùng');
        } finally {
            setActionLoading(null);
        }
    };

    // Handle unban user
    const handleUnban = async (userId: number) => {
        setActionLoading(userId);
        try {
            const response = await adminService.unbanUser(userId);
            if (response.success) {
                setUsers(prev => prev.map(user =>
                    user.id === userId
                        ? { ...user, is_active: true, ban_reason: null }
                        : user
                ));
            } else {
                alert('Không thể unban người dùng');
            }
        } catch (error) {
            console.error('Error unbanning user:', error);
            alert('Đã xảy ra lỗi khi unban người dùng');
        } finally {
            setActionLoading(null);
        }
    };

    // Handle delete user
    const handleDelete = async (userId: number) => {
        if (!window.confirm('Bạn có chắc chắn muốn xóa người dùng này?')) return;

        setActionLoading(userId);
        try {
            const response = await adminService.deleteUser(userId);
            if (response.success) {
                setUsers(prev => prev.filter(user => user.id !== userId));
                setTotalItems(prev => prev - 1);
            } else {
                alert('Không thể xóa người dùng');
            }
        } catch (error) {
            console.error('Error deleting user:', error);
            alert('Đã xảy ra lỗi khi xóa người dùng');
        } finally {
            setActionLoading(null);
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

                {/* Filters */}
                <div className="admin-users-filters">
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

                    {/* Status Filter */}
                    <select
                        className="admin-users-filter-select"
                        value={statusFilter}
                        onChange={(e) => {
                            setStatusFilter(e.target.value as 'all' | 'active' | 'banned');
                            setCurrentPage(1);
                        }}
                    >
                        <option value="all">Tất cả</option>
                        <option value="active">Đang hoạt động</option>
                        <option value="banned">Đã bị cấm</option>
                    </select>
                </div>

                {/* Results Count */}
                <p className="admin-users-count">
                    {isLoading ? 'Đang tải...' : `Có ${filteredUsers.length} kết quả`}
                </p>

                {/* Users Table */}
                <div className="admin-users-table-container">
                    <table className="admin-users-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Họ tên</th>
                                <th>Email</th>
                                <th>Vai trò</th>
                                <th>Trạng thái</th>
                                <th>Độ uy tín</th>
                                <th colSpan={2}>Chức năng</th>
                            </tr>
                        </thead>
                        <tbody>
                            {isLoading ? (
                                <tr>
                                    <td colSpan={8} className="admin-users-loading">Đang tải...</td>
                                </tr>
                            ) : filteredUsers.length === 0 ? (
                                <tr>
                                    <td colSpan={8} className="admin-users-empty">Không có người dùng nào</td>
                                </tr>
                            ) : (
                                filteredUsers.map((user) => (
                                    <tr key={user.id} className={!user.is_active ? 'admin-users-row--banned' : ''}>
                                        <td>{user.id}</td>
                                        <td>{user.full_name}</td>
                                        <td>{user.email}</td>
                                        <td>
                                            <span className={`admin-users-role admin-users-role--${user.role_id}`}>
                                                {getRoleName(user.role_id)}
                                            </span>
                                        </td>
                                        <td>
                                            <span className={`admin-users-status ${user.is_active ? 'admin-users-status--active' : 'admin-users-status--banned'}`}>
                                                {user.is_active ? 'Hoạt động' : 'Đã cấm'}
                                            </span>
                                        </td>
                                        <td>{user.reputation_score}</td>
                                        <td>
                                            {user.is_active ? (
                                                <button
                                                    className="admin-users-action-btn"
                                                    onClick={() => setBanModal({ open: true, userId: user.id, userName: user.full_name })}
                                                    disabled={actionLoading === user.id}
                                                >
                                                    <Icons.Ban className="admin-users-action-icon" />
                                                    Ban
                                                </button>
                                            ) : (
                                                <button
                                                    className="admin-users-action-btn admin-users-action-btn--unban"
                                                    onClick={() => handleUnban(user.id)}
                                                    disabled={actionLoading === user.id}
                                                >
                                                    <Icons.Ban className="admin-users-action-icon" />
                                                    Unban
                                                </button>
                                            )}
                                        </td>
                                        <td>
                                            <button
                                                className="admin-users-action-btn admin-users-action-btn--delete"
                                                onClick={() => handleDelete(user.id)}
                                                disabled={actionLoading === user.id}
                                            >
                                                <Icons.Ban className="admin-users-action-icon" />
                                                Xóa
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
                )}
            </main>

            {/* Ban Modal */}
            {banModal.open && (
                <div className="admin-users-modal-overlay" onClick={() => setBanModal({ open: false, userId: null, userName: '' })}>
                    <div className="admin-users-modal" onClick={(e) => e.stopPropagation()}>
                        <h3 className="admin-users-modal__title">Ban người dùng</h3>
                        <p className="admin-users-modal__desc">
                            Bạn đang ban: <strong>{banModal.userName}</strong>
                        </p>
                        <textarea
                            className="admin-users-modal__input"
                            placeholder="Nhập lý do ban (bắt buộc)"
                            value={banReason}
                            onChange={(e) => setBanReason(e.target.value)}
                            rows={3}
                        />
                        <div className="admin-users-modal__actions">
                            <button
                                className="admin-users-modal__btn admin-users-modal__btn--cancel"
                                onClick={() => {
                                    setBanModal({ open: false, userId: null, userName: '' });
                                    setBanReason('');
                                }}
                            >
                                Hủy
                            </button>
                            <button
                                className="admin-users-modal__btn admin-users-modal__btn--confirm"
                                onClick={handleBan}
                                disabled={!banReason.trim() || actionLoading !== null}
                            >
                                {actionLoading ? 'Đang xử lý...' : 'Xác nhận Ban'}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            <Footer />
        </div>
    );
}

export default AdminUsersPage;
