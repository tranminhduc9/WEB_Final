import Container from './Container';
import logo from  '../assets/images/logo.png'
import '../../css/Header.css'; // Import tệp CSS vừa tạo
import { Link } from 'react-router-dom'

// Functional component Header
function Header() {
  return (
    <header className="site-header">
      {/* 1. Logo */}
      <div className="header-logo">
        <a href="#">
          <img src={logo} alt="Logo" />
        </a>
      </div>

      {/* 2. Search Bar */}
      <div className="header-search">
        <input 
          type="text" 
          className="search-input" 
          placeholder="Tìm kiếm du lịch, địa điểm" 
        />
        <svg 
          className="search-icon" 
          xmlns="http://www.w3.org/2000/svg" 
          viewBox="0 0 24 24" 
          fill="none" 
          stroke="currentColor" 
          strokeWidth="2.5" 
          strokeLinecap="round" 
          strokeLinejoin="round"
        >
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
      </div>

      {/* 3. Navigation */}
      <nav className="header-nav">
        <a href="#" className="nav-link">Blog trải nghiệm</a>
        <a href="#" className="nav-link">Chatbot thông minh</a>
        <a href="#" className="nav-link">Điểm đến phổ biến</a>
        <a href="#" className="nav-link">Đăng ký</a>
        <Link to="/login" className="btn-login">Đăng nhập</Link>      </nav>
    </header>
  );
}
export default Header;
