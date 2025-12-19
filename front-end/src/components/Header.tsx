import Container from './Container';
import logo from  '../assets/images/logo.png'
import '../../css/Header.css'; // Import tệp CSS vừa tạo
import { Link, useNavigate } from 'react-router-dom'
import FeaturedPlaces from './FeaturedPlaces';
import { useState, useEffect } from 'react';
import { Icons } from '../constants';

// Functional component Header
function Header() {
  const [searchQuery, setSearchQuery] = useState('');
  
  // Khởi tạo state từ localStorage ngay từ đầu
  const getInitialAuthState = () => {
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    
    if (token) {
      let user = { name: 'User', email: '' };
      if (userData) {
        try {
          user = JSON.parse(userData);
        } catch (e) {
          // Keep default user
        }
      }
      return { isLoggedIn: true, user };
    }
    return { isLoggedIn: false, user: null };
  };

  const initialAuth = getInitialAuthState();
  const [isLoggedIn, setIsLoggedIn] = useState(initialAuth.isLoggedIn);
  const [user, setUser] = useState<any>(initialAuth.user);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const navigate = useNavigate();

  // Kiểm tra trạng thái đăng nhập khi component mount và khi localStorage thay đổi
  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem('token');
      const userData = localStorage.getItem('user');
      
      if (token) {
        setIsLoggedIn(true);
        if (userData) {
          try {
            setUser(JSON.parse(userData));
          } catch (e) {
            setUser({ name: 'User', email: '' });
          }
        } else {
          setUser({ name: 'User', email: '' });
        }
      } else {
        setIsLoggedIn(false);
        setUser(null);
      }
    };

    // Lắng nghe sự kiện storage để cập nhật khi login/logout từ tab khác
    window.addEventListener('storage', checkAuth);
    
    // Custom event để cập nhật khi login trong cùng tab
    window.addEventListener('auth-change', checkAuth);

    return () => {
      window.removeEventListener('storage', checkAuth);
      window.removeEventListener('auth-change', checkAuth);
    };
  }, []);

  // Đóng menu khi click outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (showUserMenu && !target.closest('.user-menu-container')) {
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
  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setIsLoggedIn(false);
    setUser(null);
    setShowUserMenu(false);
    navigate('/');
    // Dispatch event để các component khác cập nhật
    window.dispatchEvent(new Event('auth-change'));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  return (
    <header className="site-header">
      {/* 1. Logo */}
      <div className="header-logo">
        <Link to="/">
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

      {/* 3. Navigation */}
      <nav className="header-nav">
        <Link to="/blogs" className="nav-link">Blog trải nghiệm</Link>
        <a href="#" className="nav-link">Chatbot thông minh</a>
        <Link to="/trend-places" className="nav-link">Điểm đến phổ biến</Link>
        
        {isLoggedIn ? (
          // User Menu khi đã đăng nhập
          <div className="user-menu-container">
            <div 
              className="user-menu-trigger" 
              onClick={() => setShowUserMenu(!showUserMenu)}
            >
              <div className="user-avatar-wrapper">
                <div className="user-avatar">
                  {user?.avatar ? (
                    <img src={user.avatar} alt={user.name} />
                  ) : (
                    <div className="avatar-placeholder">
                      {user?.name?.[0]?.toUpperCase() || 'U'}
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
                <Link to="/profile" className="user-menu-item" onClick={() => setShowUserMenu(false)}>
                  Hồ sơ
                </Link>
                <div className="user-menu-divider"></div>
                <button className="user-menu-item logout-btn" onClick={handleLogout}>
                  Đăng xuất
                </button>
              </div>
            )}
          </div>
        ) : (
          // Đăng ký/Đăng nhập khi chưa đăng nhập
          <>
            <Link to="/register" className="nav-link">Đăng ký</Link>
            <Link to="/login" className="btn-login">Đăng nhập</Link>
          </>
        )}
      </nav>
    </header>
  );
}

export default Header;
