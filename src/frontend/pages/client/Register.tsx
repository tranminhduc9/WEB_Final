import '../../assets/styles/pages/RegisterPage.css';
import logo from '../../assets/images/logo.png';
import image_register from '../../assets/images/login-register-image.png';
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';


export default function Register() {
    const [username, setUsername] = useState('');
    const [fullname, setFullname] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');

    const onSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        if (!username || !password) return setError('Vui lòng nhập đủ thông tin');
    };

    return (
        <div className="register-container">
            <div className="register-form-section">
                <div className="form-wrapper">
                    <h2>ĐĂNG KÝ TÀI KHOẢN</h2>
                    <img src={logo} alt="register" className="logo" />
                    <form onSubmit={onSubmit}>
                        <div className="input-group subheading">
                            <label htmlFor="username">Tên đăng nhập</label>
                            <input type="text" id="username" value={username} onChange={(e) => setUsername(e.target.value)} />
                        </div>
                        <div className="input-group subheading">
                            <label htmlFor="fullname">Họ và tên</label>
                            <input type="text" id="fullname" value={fullname} onChange={(e) => setFullname(e.target.value)} />
                        </div>
                        <div className="input-group subheading">
                            <label htmlFor="password">Mật khẩu</label>
                            <input type="password" id="password" value={password} onChange={(e) => setPassword(e.target.value)} />
                        </div>
                        <div className="input-group subheading">
                            <label htmlFor="confirm-password">Xác nhận mật khẩu</label>
                            <input type="password" id="confirm-password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} />
                        </div>
                        {error && <div className="error-message">{error}</div>}
                        <button type="submit" className="register-button">Đăng ký</button>
                        <div className="forgot-password">
                            <Link to="/login">Đã có tài khoản? Đăng nhập</Link>
                        </div>
                    </form>
                    
                </div>
            </div>
            <div className="register-image-section" style={{ backgroundImage: `url(${image_register})` }}></div>
        </div>
    );
}
