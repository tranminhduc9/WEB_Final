import Container from './Container';
import logo from  '../assets/images/logo.png'
import '../../css/Header.css'; // Import tệp CSS vừa tạo
import { Link, useNavigate } from 'react-router-dom'
import FeaturedPlaces from './FeaturedPlaces';
import { useState } from 'react';

// Functional component Header
function Header() {
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  const handleSearchIconClick = () => {
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
      <form className="header-search" onSubmit={handleSearch}>
        <input 
          type="text" 
          className="search-input" 
          placeholder="Tìm kiếm du lịch, địa điểm" 
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
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
          onClick={handleSearchIconClick}
        >
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
      </form>

      {/* 3. Navigation */}
      <nav className="header-nav">
        <a href="#" className="nav-link">Blog trải nghiệm</a>
        <a href="#" className="nav-link">Chatbot thông minh</a>
        <a href="#featured-places" className="nav-link">Điểm đến phổ biến</a>
        <Link to="/register" className="nav-link">Đăng ký</Link>
        <Link to="/login" className="btn-login">Đăng nhập</Link>      </nav>
    </header>
  );
}
export default Header;
