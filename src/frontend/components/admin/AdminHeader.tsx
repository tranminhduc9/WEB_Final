import { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuthContext } from '../../contexts';
import logo from '../../assets/images/logo.png';
import '../../assets/styles/components/AdminHeader.css';

function AdminHeader() {
    const [showUserMenu, setShowUserMenu] = useState(false);
    const { user, logout } = useAuthContext();
    const navigate = useNavigate();
    const location = useLocation();

    // Đóng menu khi click outside
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            const target = event.target as HTMLElement;
            if (showUserMenu && !target.closest('.admin-user-menu-container')) {
                setShowUserMenu(false);
            }
        };

        if (showUserMenu) {
            document.addEventListener('mousedown', handleClickOutside);
        }

        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [showUserMenu]);

    // Xử lý đăng xuất
    const handleLogout = async () => {
        setShowUserMenu(false);
        await logout();
        navigate('/');
    };

    // Check active link
    const isActiveLink = (path: string) => {
        // /admin và /admin/statistics đều hiển thị AdminHomePage
        if (path === '/admin/statistics' && (location.pathname === '/admin' || location.pathname === '/admin/')) {
            return true;
        }
        return location.pathname === path || location.pathname.startsWith(path + '/');
    };

    return (
        <header className="admin-header">
            {/* Logo */}
            <div className="admin-header__logo">
                <Link to="/admin">
                    <img src={logo} alt="Logo" />
                </Link>
            </div>

            {/* Navigation */}
            <nav className="admin-header__nav">
                <Link
                    to="/admin/posts"
                    className={`admin-nav-link ${isActiveLink('/admin/posts') ? 'active' : ''}`}
                >
                    Duyệt bài
                </Link>
                <Link
                    to="/admin/statistics"
                    className={`admin-nav-link ${isActiveLink('/admin/statistics') ? 'active' : ''}`}
                >
                    Thống kê Tổng quan
                </Link>
                <Link
                    to="/admin/locations"
                    className={`admin-nav-link ${isActiveLink('/admin/locations') ? 'active' : ''}`}
                >
                    Quản lý Địa điểm
                </Link>
                <Link
                    to="/admin/reports"
                    className={`admin-nav-link ${isActiveLink('/admin/reports') ? 'active' : ''}`}
                >
                    Quản lý Báo cáo
                </Link>
                <Link
                    to="/admin/users"
                    className={`admin-nav-link ${isActiveLink('/admin/users') ? 'active' : ''}`}
                >
                    Quản lý Người dùng
                </Link>
            </nav>

            {/* User Menu */}
            <div className="admin-user-menu-container">
                <div
                    className="admin-user-menu-trigger"
                    onClick={() => setShowUserMenu(!showUserMenu)}
                >
                    <div className="admin-user-avatar">
                        {user?.avatar ? (
                            <img src={user.avatar} alt={user.name} />
                        ) : (
                            <div className="admin-avatar-placeholder">
                                {user?.name?.[0]?.toUpperCase() || 'A'}
                            </div>
                        )}
                    </div>
                </div>

                {showUserMenu && (
                    <div className="admin-user-menu-dropdown">
                        <Link
                            to="/profile"
                            className="admin-user-menu-item"
                            onClick={() => setShowUserMenu(false)}
                        >
                            Hồ sơ
                        </Link>
                        <div className="admin-user-menu-divider"></div>
                        <button
                            className="admin-user-menu-item admin-logout-btn"
                            onClick={handleLogout}
                        >
                            Đăng xuất
                        </button>
                    </div>
                )}
            </div>
        </header>
    );
}

export default AdminHeader;
