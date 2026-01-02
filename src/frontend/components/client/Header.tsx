import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthContext } from '../../contexts';
import { Icons } from '../../config/constants';
import logo from '../../assets/images/logo.png';
import '../../assets/styles/components/Header.css';

function Header() {
  const [searchQuery, setSearchQuery] = useState('');
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showMobileMenu, setShowMobileMenu] = useState(false);

  // Sử dụng AuthContext thay vì localStorage trực tiếp
  const { user, isAuthenticated, logout, isLoading } = useAuthContext();
  const navigate = useNavigate();

  // Đóng menu khi click outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (showUserMenu && !target.closest('.user-menu-container')) {
        setShowUserMenu(false);
      }
      if (showMobileMenu && !target.closest('.site-header')) {
        setShowMobileMenu(false);
      }
    };

    if (showUserMenu || showMobileMenu) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showUserMenu, showMobileMenu]);

  // Xử lý đăng xuất
  const handleLogout = async () => {
    setShowUserMenu(false);
    await logout();
    navigate('/');
  };

  // Xử lý tìm kiếm
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
      // Scroll to top khi search
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  return (
    <header className="site-header">
      {/* 1. Logo */}
      <div className="header-logo">
        <Link to="/" onClick={() => setShowMobileMenu(false)}>
          <img src={logo} alt="Logo" />
        </Link>
      </div>

      {/* 2. Search Bar */}
      <div className="header-search-wrapper">
        <form onSubmit={handleSubmit} className="header-search">
          <input
            type="text"
            className="search-input"
            placeholder="Tìm điểm du lịch, địa điểm"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <button type="submit" className="search-button">
            <Icons.Search />
          </button>
        </form>
      </div>

      {/* Mobile Menu Toggle */}
      <button 
        className="mobile-menu-toggle"
        onClick={() => setShowMobileMenu(!showMobileMenu)}
        aria-label="Toggle menu"
      >
        {showMobileMenu ? <Icons.Close /> : (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="3" y1="6" x2="21" y2="6"></line>
            <line x1="3" y1="12" x2="21" y2="12"></line>
            <line x1="3" y1="18" x2="21" y2="18"></line>
          </svg>
        )}
      </button>

      {/* 3. Navigation */}
      <nav className={`header-nav ${showMobileMenu ? 'header-nav--open' : ''}`}>
        <Link to="/blogs" className="nav-link" onClick={() => setShowMobileMenu(false)}>Blog trải nghiệm</Link>
        <Link to="/places" className="nav-link" onClick={() => setShowMobileMenu(false)}>Khám phá địa điểm</Link>
        <Link to="/trend-places" className="nav-link" onClick={() => setShowMobileMenu(false)}>Điểm đến phổ biến</Link>

        {isLoading ? (
          // Loading state
          <div className="nav-loading">
            <span className="loading-spinner"></span>
          </div>
        ) : isAuthenticated && user ? (
          // User Menu khi đã đăng nhập
          <div className="user-menu-container">
            <div
              className="user-menu-trigger"
              onClick={() => setShowUserMenu(!showUserMenu)}
            >
              <div className="user-avatar-wrapper">
                <div className="user-avatar">
                  {(user.avatar || user.avatar_url) ? (
                    <img src={user.avatar || user.avatar_url || ''} alt={user.name || user.full_name} />
                  ) : (
                    <div className="avatar-placeholder">
                      {(user.name || user.full_name)?.[0]?.toUpperCase() || 'U'}
                    </div>
                  )}
                </div>
                <svg
                  className="avatar-dropdown-icon"
                  xmlns="http://www.w3.org/2000/svg"
                  width="12"
                  height="12"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="3"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
              </div>
            </div>

            {showUserMenu && (
              <div className="user-menu-dropdown">
                <Link
                  to="/profile"
                  className="user-menu-item"
                  onClick={() => {
                    setShowUserMenu(false);
                    setShowMobileMenu(false);
                  }}
                >
                  Hồ sơ
                </Link>
                {user.role === 'admin' && (
                  <>
                    <div className="user-menu-divider"></div>
                    <Link
                      to="/admin"
                      className="user-menu-item"
                      onClick={() => {
                        setShowUserMenu(false);
                        setShowMobileMenu(false);
                      }}
                    >
                      Quản trị
                    </Link>
                  </>
                )}
                <div className="user-menu-divider"></div>
                <button
                  className="user-menu-item logout-btn"
                  onClick={() => {
                    handleLogout();
                    setShowMobileMenu(false);
                  }}
                >
                  Đăng xuất
                </button>
              </div>
            )}
          </div>
        ) : (
          // Đăng ký/Đăng nhập khi chưa đăng nhập
          <>
            <Link to="/register" className="nav-link" onClick={() => setShowMobileMenu(false)}>Đăng ký</Link>
            <Link to="/login" className="btn-login" onClick={() => setShowMobileMenu(false)}>Đăng nhập</Link>
          </>
        )}
      </nav>
    </header>
  );
}

export default Header;
