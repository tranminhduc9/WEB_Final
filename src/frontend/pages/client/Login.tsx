import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuthContext } from '../../contexts';
import logo from '../../assets/images/logo.png';
import image_login from '../../assets/images/login-register-image.png';
import '../../assets/styles/pages/LoginPage.css';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const { login, error, clearError, isLoading } = useAuthContext();
  const navigate = useNavigate();
  const location = useLocation();

  // Lấy redirect URL từ state (nếu có)
  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || '/';

  const validateForm = (): string | null => {
    if (!email.trim()) {
      return 'Vui lòng nhập email';
    }
    if (!password) {
      return 'Vui lòng nhập mật khẩu';
    }
    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return 'Email không hợp lệ';
    }
    return null;
  };

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    
    const validationError = validateForm();
    if (validationError) {
      return;
    }

    setIsSubmitting(true);
    
    try {
      await login({ email: email.trim(), password });
      // Redirect về trang trước đó hoặc trang chủ
      navigate(from, { replace: true });
    } catch (err) {
      // Error đã được xử lý trong AuthContext
      console.error('Login failed:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const displayError = error || (validateForm() && isSubmitting ? validateForm() : null);

  return (
    <div className="login-container">
      <div className="login-form-section">
        <div className="form-wrapper">
          <h2>ĐĂNG NHẬP TÀI KHOẢN</h2>
          <img src={logo} alt="login" className="logo" />
          
          <form onSubmit={onSubmit}>
            <div className="input-group subheading">
              <label htmlFor="email">Email</label>
              <input 
                type="email" 
                id="email" 
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  if (error) clearError();
                }}
                placeholder="example@email.com"
                disabled={isLoading}
                autoComplete="email"
              />
            </div>
            <div className="input-group subheading">
              <label htmlFor="password">Mật khẩu</label>
              <input 
                type="password" 
                id="password" 
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  if (error) clearError();
                }}
                placeholder="••••••••"
                disabled={isLoading}
                autoComplete="current-password"
              />
            </div>
            
            {displayError && (
              <div className="error-message">{displayError}</div>
            )}
            
            <button 
              type="submit" 
              className="login-button"
              disabled={isLoading || isSubmitting}
            >
              {isLoading || isSubmitting ? 'Đang đăng nhập...' : 'Đăng nhập'}
            </button>
            
            <div className="forgot-password">
              <Link to="/forgot-password">Quên mật khẩu?</Link>
            </div>
            
            <div className="register-link" style={{ textAlign: 'center', marginTop: '1rem' }}>
              <span>Chưa có tài khoản? </span>
              <Link to="/register">Đăng ký ngay</Link>
            </div>
          </form>
        </div>
      </div>
      <div className="login-image-section" style={{ backgroundImage: `url(${image_login})` }}></div>
    </div>
  );
}
