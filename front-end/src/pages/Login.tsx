import { useState } from 'react';
import logo from '../assets/images/logo.png';
import image_login from '../assets/images/login-register-image.png';
import '../../css/LoginPage.css';
export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (!username || !password) return setError('Vui lòng nhập đủ thông tin');

    // Fake login demo
    if (username === 'test@demo.com' && password === '123456') {
      localStorage.setItem('token', 'demo-token');
      window.location.href = '/';
    } else {
      setError('Email hoặc mật khẩu không đúng');
    }
  };

  return (
    <div className="login-container">
      <div className="login-form-section">
        <div className="form-wrapper">
          <h2>ĐĂNG NHẬP TÀI KHOẢN</h2>
          <img src={logo} alt="login" className="logo" />
          
          <form onSubmit={onSubmit}>
            <div className="input-group subheading">
              <label htmlFor="username">Tên đăng nhập</label>
              <input 
                type="text" 
                id="username" 
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>
            <div className="input-group subheading">
              <label htmlFor="password">Mật khẩu</label>
              <input 
                type="password" 
                id="password" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            {error && <div className="error-message">{error}</div>}
            <button type="submit" className="login-button">Đăng nhập</button>
            <div className="forgot-password">
              <a href="#">Quên mật khẩu?</a>
            </div>
          </form>
        </div>
      </div>
      <div className="login-image-section" style={{ backgroundImage: `url(${image_login})` }}></div>
    </div>
  );
}
