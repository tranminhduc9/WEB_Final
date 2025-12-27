import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authService } from '../../services';
import logo from '../../assets/images/logo.png';
import image_login from '../../assets/images/login-register-image.png';
import '../../assets/styles/pages/ForgotPasswordPage.css';

export default function ForgotPassword() {
    const [email, setEmail] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState(false);

    const navigate = useNavigate();

    const validateForm = (): string | null => {
        if (!email.trim()) {
            return 'Vui lòng nhập email';
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
        setError(null);

        const validationError = validateForm();
        if (validationError) {
            setError(validationError);
            return;
        }

        setIsLoading(true);

        try {
            // Call forgot password API
            await authService.forgotPassword(email.trim());
            setSuccess(true);
        } catch (err: unknown) {
            // Handle error
            if (err instanceof Error) {
                setError(err.message || 'Có lỗi xảy ra. Vui lòng thử lại.');
            } else {
                setError('Có lỗi xảy ra. Vui lòng thử lại.');
            }
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="forgot-password-container">
            <div className="forgot-password-form-section">
                <div className="form-wrapper">
                    <h2>QUÊN MẬT KHẨU</h2>
                    <Link to="/"><img src={logo} alt="forgot password" className="forgot-password-logo" /></Link>

                    {success ? (
                        <div className="success-section">
                            <div className="success-message">
                                <p>Chúng tôi đã gửi email hướng dẫn đặt lại mật khẩu đến:</p>
                                <p className="email-sent"><strong>{email}</strong></p>
                                <p>Vui lòng kiểm tra hộp thư của bạn.</p>
                            </div>
                            <button
                                type="button"
                                className="forgot-password-button"
                                onClick={() => navigate('/login')}
                            >
                                Quay lại đăng nhập
                            </button>
                        </div>
                    ) : (
                        <form onSubmit={onSubmit}>
                            <div className="input-group subheading">
                                <label htmlFor="email">E-mail đăng nhập</label>
                                <input
                                    type="email"
                                    id="email"
                                    value={email}
                                    onChange={(e) => {
                                        setEmail(e.target.value);
                                        if (error) setError(null);
                                    }}
                                    placeholder="example@email.com"
                                    disabled={isLoading}
                                    autoComplete="email"
                                />
                            </div>

                            {error && (
                                <div className="error-message">{error}</div>
                            )}

                            <button
                                type="submit"
                                className="forgot-password-button"
                                disabled={isLoading}
                            >
                                {isLoading ? 'Đang xử lý...' : 'Quên mật khẩu'}
                            </button>

                            <div className="back-to-login">
                                <Link to="/login">← Quay lại đăng nhập</Link>
                            </div>
                        </form>
                    )}
                </div>
            </div>
            <div className="forgot-password-image-section">
                <img src={image_login} alt="Forgot password illustration" />
            </div>
        </div>
    );
}
