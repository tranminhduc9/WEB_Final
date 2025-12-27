import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthContext } from '../../contexts';
import logo from '../../assets/images/logo.png';
import image_register from '../../assets/images/login-register-image.png';
import '../../assets/styles/pages/RegisterPage.css';

export default function Register() {
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [localError, setLocalError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);

  const { register, error, clearError, isLoading } = useAuthContext();
  const navigate = useNavigate();

  const validateForm = (): string | null => {
    // Required fields
    if (!email.trim()) {
      return 'Vui lòng nhập email';
    }
    if (!name.trim()) {
      return 'Vui lòng nhập họ và tên';
    }
    if (!password) {
      return 'Vui lòng nhập mật khẩu';
    }
    if (!confirmPassword) {
      return 'Vui lòng xác nhận mật khẩu';
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return 'Email không hợp lệ';
    }

    // Password validation
    if (password.length < 6) {
      return 'Mật khẩu phải có ít nhất 6 ký tự';
    }

    // Password match
    if (password !== confirmPassword) {
      return 'Mật khẩu xác nhận không khớp';
    }

    return null;
  };

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    setLocalError('');

    const validationError = validateForm();
    if (validationError) {
      setLocalError(validationError);
      return;
    }

    setIsSubmitting(true);

    try {
      await register({
        email: email.trim(),
        password,
        full_name: name.trim(),
      });

      setSuccess(true);
      // Redirect to login after 2 seconds
      setTimeout(() => {
        navigate('/login', {
          state: { message: 'Đăng ký thành công! Vui lòng đăng nhập.' }
        });
      }, 2000);
    } catch (err) {
      // Error đã được xử lý trong AuthContext
      console.error('Register failed:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const displayError = localError || error;

  if (success) {
    return (
      <div className="register-container">
        <div className="register-form-section">
          <div className="form-wrapper" style={{ textAlign: 'center' }}>
            <h2>ĐĂNG KÝ THÀNH CÔNG!</h2>
            <Link to="/"><img src={logo} alt="register" className="register-logo" /></Link>
            <p style={{ marginTop: '1rem', color: '#4CAF50' }}>
              Tài khoản của bạn đã được tạo thành công.
            </p>
            <p style={{ marginTop: '0.5rem' }}>
              Đang chuyển hướng đến trang đăng nhập...
            </p>
          </div>
        </div>
        <div className="register-image-section">
          <img src={image_register} alt="Register illustration" />
        </div>
      </div>
    );
  }

  return (
    <div className="register-container">
      <div className="register-form-section">
        <div className="form-wrapper">
          <h2>ĐĂNG KÝ TÀI KHOẢN</h2>
          <Link to="/"><img src={logo} alt="register" className="register-logo" /></Link>

          <form onSubmit={onSubmit}>
            <div className="input-group subheading">
              <label htmlFor="email">Email *</label>
              <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  if (displayError) {
                    clearError();
                    setLocalError('');
                  }
                }}
                placeholder="example@email.com"
                disabled={isLoading}
                autoComplete="email"
              />
            </div>

            <div className="input-group subheading">
              <label htmlFor="name">Họ và tên *</label>
              <input
                type="text"
                id="name"
                value={name}
                onChange={(e) => {
                  setName(e.target.value);
                  if (displayError) {
                    clearError();
                    setLocalError('');
                  }
                }}
                placeholder="Nguyễn Văn A"
                disabled={isLoading}
                autoComplete="name"
              />
            </div>

            <div className="input-group subheading">
              <label htmlFor="password">Mật khẩu *</label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  if (displayError) {
                    clearError();
                    setLocalError('');
                  }
                }}
                placeholder="Tối thiểu 6 ký tự"
                disabled={isLoading}
                autoComplete="new-password"
              />
            </div>

            <div className="input-group subheading">
              <label htmlFor="confirm-password">Xác nhận mật khẩu *</label>
              <input
                type="password"
                id="confirm-password"
                value={confirmPassword}
                onChange={(e) => {
                  setConfirmPassword(e.target.value);
                  if (displayError) {
                    clearError();
                    setLocalError('');
                  }
                }}
                placeholder="Nhập lại mật khẩu"
                disabled={isLoading}
                autoComplete="new-password"
              />
            </div>

            {displayError && (
              <div className="error-message">{displayError}</div>
            )}

            <button
              type="submit"
              className="register-button"
              disabled={isLoading || isSubmitting}
            >
              {isLoading || isSubmitting ? 'Đang đăng ký...' : 'Đăng ký'}
            </button>

            <div className="forgot-password">
              <Link to="/login">Đã có tài khoản? Đăng nhập</Link>
            </div>
          </form>
        </div>
      </div>
      <div className="register-image-section">
        <img src={image_register} alt="Register illustration" />
      </div>
    </div>
  );
}
