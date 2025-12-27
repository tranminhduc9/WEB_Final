import { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuthContext } from '../../contexts';
import logo from '../../assets/images/logo.png';
import image_login from '../../assets/images/login-register-image.png';
import '../../assets/styles/pages/LoginPage.css';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [localError, setLocalError] = useState<string | null>(null);

  const { login, error, clearError, isLoading, isAuthenticated } = useAuthContext();
  const navigate = useNavigate();
  const location = useLocation();

  // Lấy redirect URL từ state (nếu có)
  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || '/';

  // Redirect on successful authentication
  useEffect(() => {
    if (isAuthenticated) {
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, navigate, from]);

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
    setLocalError(null);

    const validationError = validateForm();
    if (validationError) {
      setLocalError(validationError);
      return;
    }

    // Login will set error in context if it fails
    await login({ email: email.trim(), password });
    // Redirect is handled by useEffect above when isAuthenticated changes
  };

  const displayError = localError || error;

  return (
    <div className="login-container">
      <div className="login-form-section">
        <div className="form-wrapper">
          <h2>ĐĂNG NHẬP TÀI KHOẢN</h2>
          <Link to="/"><img src={logo} alt="login" className="login-logo" /></Link>

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
              disabled={isLoading}
            >
              {isLoading ? 'Đang đăng nhập...' : 'Đăng nhập'}
            </button>

            <div className="forgot-password">
              <Link to="/forgot-password">Quên mật khẩu?</Link>
            </div>

            <div className="register-link">
              <span>Chưa có tài khoản? </span>
              <Link to="/register">Đăng ký ngay</Link>
            </div>
          </form>
        </div>
      </div>
      <div className="login-image-section">
        <img src={image_login} alt="Login illustration" />
      </div>
    </div>
  );
}
