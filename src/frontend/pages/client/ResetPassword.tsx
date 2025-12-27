import { useState, useEffect } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { authService } from '../../services';
import logo from '../../assets/images/logo.png';
import image_login from '../../assets/images/login-register-image.png';
import '../../assets/styles/pages/ResetPasswordPage.css';

export default function ResetPassword() {
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState(false);
    const [tokenValid, setTokenValid] = useState(true);

    const navigate = useNavigate();
    const [searchParams] = useSearchParams();

    // Get token and email from URL params
    const token = searchParams.get('token');
    const email = searchParams.get('email');

    // Check if token exists
    useEffect(() => {
        if (!token || !email) {
            setTokenValid(false);
        }
    }, [token, email]);

    const validateForm = (): string | null => {
        if (!newPassword) {
            return 'Vui lòng nhập mật khẩu mới';
        }
        if (newPassword.length < 6) {
            return 'Mật khẩu phải có ít nhất 6 ký tự';
        }
        if (!confirmPassword) {
            return 'Vui lòng xác nhận mật khẩu';
        }
        if (newPassword !== confirmPassword) {
            return 'Mật khẩu xác nhận không khớp';
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

        if (!token || !email) {
            setError('Link đặt lại mật khẩu không hợp lệ');
            return;
        }

        setIsLoading(true);

        try {
            await authService.resetPassword({
                email,
                token,
                new_password: newPassword,
            });
            setSuccess(true);
        } catch (err: unknown) {
            if (err instanceof Error) {
                setError(err.message || 'Có lỗi xảy ra. Vui lòng thử lại.');
            } else {
                setError('Có lỗi xảy ra. Vui lòng thử lại.');
            }
        } finally {
            setIsLoading(false);
        }
    };

    // Invalid token state
    if (!tokenValid) {
        return (
            <div className="reset-password-container">
                <div className="reset-password-form-section">
                    <div className="form-wrapper">
                        <h2>ĐỔI MẬT KHẨU</h2>
                        <Link to="/"><img src={logo} alt="reset password" className="reset-password-logo" /></Link>

                        <div className="error-section">
                            <div className="error-message">
                                Link đặt lại mật khẩu không hợp lệ hoặc đã hết hạn.
                            </div>
                            <Link to="/forgot-password" className="reset-password-button">
                                Yêu cầu link mới
                            </Link>
                        </div>
                    </div>
                </div>
                <div className="reset-password-image-section">
                    <img src={image_login} alt="Reset password illustration" />
                </div>
            </div>
        );
    }

    return (
        <div className="reset-password-container">
            <div className="reset-password-form-section">
                <div className="form-wrapper">
                    <h2>ĐỔI MẬT KHẨU</h2>
                    <Link to="/"><img src={logo} alt="reset password" className="reset-password-logo" /></Link>

                    {success ? (
                        <div className="success-section">
                            <div className="success-message">
                                <p>Mật khẩu của bạn đã được đổi thành công!</p>
                                <p>Bạn có thể đăng nhập với mật khẩu mới.</p>
                            </div>
                            <button
                                type="button"
                                className="reset-password-button"
                                onClick={() => navigate('/login')}
                            >
                                Đăng nhập ngay
                            </button>
                        </div>
                    ) : (
                        <form onSubmit={onSubmit}>
                            <div className="input-group subheading">
                                <label htmlFor="newPassword">Mật khẩu mới</label>
                                <input
                                    type="password"
                                    id="newPassword"
                                    value={newPassword}
                                    onChange={(e) => {
                                        setNewPassword(e.target.value);
                                        if (error) setError(null);
                                    }}
                                    placeholder="••••••••"
                                    disabled={isLoading}
                                    autoComplete="new-password"
                                />
                            </div>

                            <div className="input-group subheading">
                                <label htmlFor="confirmPassword">Xác nhận mật khẩu</label>
                                <input
                                    type="password"
                                    id="confirmPassword"
                                    value={confirmPassword}
                                    onChange={(e) => {
                                        setConfirmPassword(e.target.value);
                                        if (error) setError(null);
                                    }}
                                    placeholder="••••••••"
                                    disabled={isLoading}
                                    autoComplete="new-password"
                                />
                            </div>

                            {error && (
                                <div className="error-message">{error}</div>
                            )}

                            <button
                                type="submit"
                                className="reset-password-button"
                                disabled={isLoading}
                            >
                                {isLoading ? 'Đang xử lý...' : 'Đổi mật khẩu'}
                            </button>

                            <div className="back-to-login">
                                <Link to="/login">← Quay lại đăng nhập</Link>
                            </div>
                        </form>
                    )}
                </div>
            </div>
            <div className="reset-password-image-section">
                <img src={image_login} alt="Reset password illustration" />
            </div>
        </div>
    );
}
