/**
 * Auth Service Tests
 * Testing authService functions with mocked axios
 */
import { describe, it, expect, vi, beforeEach, afterEach, Mock } from 'vitest';

// Mock axiosClient module before importing authService
vi.mock('../../api/axiosClient', () => {
    return {
        default: {
            post: vi.fn(),
            get: vi.fn(),
            put: vi.fn(),
        },
        tokenStorage: {
            getAccessToken: vi.fn(() => null),
            getRefreshToken: vi.fn(() => null),
            setTokens: vi.fn(),
            setAccessToken: vi.fn(),
            clearTokens: vi.fn(),
            isTokenExpired: vi.fn(() => true),
        },
    };
});

// Import after mocking
import axiosClient, { tokenStorage } from '../../api/axiosClient';
import { authService } from '../authService';
import type {
    AuthResponse,
    BaseResponse,
} from '../../types/auth';

describe('authService', () => {
    const mockPost = axiosClient.post as Mock;
    const mockGet = axiosClient.get as Mock;
    const mockPut = axiosClient.put as Mock;

    beforeEach(() => {
        vi.clearAllMocks();
    });

    afterEach(() => {
        vi.restoreAllMocks();
    });

    // ================================
    // REGISTER TESTS
    // ================================
    describe('register', () => {
        it('should register successfully and return BaseResponse', async () => {
            const mockResponse: BaseResponse = {
                success: true,
                message: 'Đăng ký thành công! Vui lòng xác thực email.',
            };

            mockPost.mockResolvedValueOnce(mockResponse);

            const result = await authService.register({
                full_name: 'Test User',
                email: 'test@example.com',
                password: '123456',
            });

            expect(mockPost).toHaveBeenCalledWith('/auth/register', {
                full_name: 'Test User',
                email: 'test@example.com',
                password: '123456',
            });
            expect(result).toEqual(mockResponse);
            expect(result.success).toBe(true);
        });

        it('should handle 422 validation error', async () => {
            const mockError = {
                success: false,
                error: {
                    code: 'VALIDATION_ERROR',
                    message: 'Validation failed',
                    details: [
                        { field: 'email', message: 'Email đã được sử dụng' },
                    ],
                },
                status: 422,
            };

            mockPost.mockRejectedValueOnce(mockError);

            await expect(
                authService.register({
                    full_name: 'Test User',
                    email: 'existing@example.com',
                    password: '123456',
                })
            ).rejects.toMatchObject({
                success: false,
                error: expect.objectContaining({
                    code: 'VALIDATION_ERROR',
                }),
            });
        });
    });

    // ================================
    // LOGIN TESTS
    // ================================
    describe('login', () => {
        it('should login successfully and return AuthResponse', async () => {
            const mockResponse: AuthResponse = {
                success: true,
                access_token: 'mock-access-token',
                refresh_token: 'mock-refresh-token',
                user: {
                    id: 1,
                    email: 'test@example.com',
                    full_name: 'Test User',
                    role_id: 3,
                    role: 'user',
                },
            };

            mockPost.mockResolvedValueOnce(mockResponse);

            const result = await authService.login({
                email: 'test@example.com',
                password: '123456',
            });

            expect(mockPost).toHaveBeenCalledWith('/auth/login', {
                email: 'test@example.com',
                password: '123456',
            });
            expect(result).toEqual(mockResponse);
            expect(result.success).toBe(true);
            expect(result.access_token).toBe('mock-access-token');
            expect(result.user.email).toBe('test@example.com');
        });

        it('should dispatch auth:login event on successful login', async () => {
            const mockResponse: AuthResponse = {
                success: true,
                access_token: 'mock-access-token',
                user: {
                    id: 1,
                    email: 'test@example.com',
                    full_name: 'Test User',
                    role_id: 3,
                    role: 'user',
                },
            };

            mockPost.mockResolvedValueOnce(mockResponse);
            const dispatchSpy = vi.spyOn(window, 'dispatchEvent');

            await authService.login({
                email: 'test@example.com',
                password: '123456',
            });

            expect(dispatchSpy).toHaveBeenCalled();
        });

        it('should handle invalid credentials', async () => {
            const mockError = {
                success: false,
                error: {
                    code: 'INVALID_CREDENTIALS',
                    message: 'Email hoặc mật khẩu không đúng',
                },
                status: 401,
            };

            mockPost.mockRejectedValueOnce(mockError);

            await expect(
                authService.login({
                    email: 'test@example.com',
                    password: 'wrongpassword',
                })
            ).rejects.toMatchObject({
                success: false,
            });
        });
    });

    // ================================
    // VERIFY EMAIL TESTS
    // ================================
    describe('verifyEmail', () => {
        it('should verify email with token', async () => {
            const mockResponse: BaseResponse = {
                success: true,
                message: 'Email đã được xác thực thành công',
            };

            mockGet.mockResolvedValueOnce(mockResponse);

            const result = await authService.verifyEmail('verification-token-123');

            expect(mockGet).toHaveBeenCalledWith(
                '/auth/verify-email?token=verification-token-123'
            );
            expect(result.success).toBe(true);
        });

        it('should handle invalid/expired token', async () => {
            const mockError = {
                success: false,
                error: {
                    code: 'INVALID_TOKEN',
                    message: 'Token không hợp lệ hoặc đã hết hạn',
                },
                status: 400,
            };

            mockGet.mockRejectedValueOnce(mockError);

            await expect(authService.verifyEmail('invalid-token')).rejects.toMatchObject({
                success: false,
            });
        });
    });

    // ================================
    // FORGOT PASSWORD TESTS
    // ================================
    describe('forgotPassword', () => {
        it('should request password reset email', async () => {
            const mockResponse: BaseResponse = {
                success: true,
                message: 'Email đặt lại mật khẩu đã được gửi',
            };

            mockPost.mockResolvedValueOnce(mockResponse);

            const result = await authService.forgotPassword('test@example.com');

            expect(mockPost).toHaveBeenCalledWith('/auth/forgot-password', {
                email: 'test@example.com',
            });
            expect(result.success).toBe(true);
        });

        it('should handle non-existent email gracefully', async () => {
            const mockResponse: BaseResponse = {
                success: true,
                message: 'Nếu email tồn tại, bạn sẽ nhận được link đặt lại mật khẩu',
            };

            mockPost.mockResolvedValueOnce(mockResponse);

            const result = await authService.forgotPassword('nonexistent@example.com');

            expect(result.success).toBe(true);
        });
    });

    // ================================
    // RESET PASSWORD TESTS
    // ================================
    describe('resetPassword', () => {
        it('should reset password with valid token', async () => {
            const mockResponse: BaseResponse = {
                success: true,
                message: 'Mật khẩu đã được đặt lại thành công',
            };

            mockPost.mockResolvedValueOnce(mockResponse);

            const result = await authService.resetPassword({
                email: 'test@example.com',
                token: 'reset-token-123',
                new_password: 'newpassword123',
            });

            expect(mockPost).toHaveBeenCalledWith('/auth/reset-password', {
                email: 'test@example.com',
                token: 'reset-token-123',
                new_password: 'newpassword123',
            });
            expect(result.success).toBe(true);
        });

        it('should handle invalid reset token', async () => {
            const mockError = {
                success: false,
                error: {
                    code: 'INVALID_TOKEN',
                    message: 'Token đặt lại mật khẩu không hợp lệ',
                },
                status: 400,
            };

            mockPost.mockRejectedValueOnce(mockError);

            await expect(
                authService.resetPassword({
                    email: 'test@example.com',
                    token: 'invalid-token',
                    new_password: 'newpassword123',
                })
            ).rejects.toMatchObject({
                success: false,
            });
        });
    });

    // ================================
    // LOGOUT TESTS
    // ================================
    describe('logout', () => {
        it('should call logout endpoint and dispatch event', async () => {
            const mockResponse: BaseResponse = {
                success: true,
                message: 'Đăng xuất thành công',
            };

            mockPost.mockResolvedValueOnce(mockResponse);
            const dispatchSpy = vi.spyOn(window, 'dispatchEvent');

            const result = await authService.logout();

            expect(mockPost).toHaveBeenCalledWith('/auth/logout', {
                refresh_token: expect.any(String),
            });
            expect(result.success).toBe(true);
            expect(dispatchSpy).toHaveBeenCalled();
            expect(tokenStorage.clearTokens).toHaveBeenCalled();
        });

        it('should clear tokens even if API fails', async () => {
            mockPost.mockRejectedValueOnce(new Error('Network error'));
            const dispatchSpy = vi.spyOn(window, 'dispatchEvent');

            await expect(authService.logout()).rejects.toThrow();

            // Should still dispatch logout event and clear tokens (in finally block)
            expect(dispatchSpy).toHaveBeenCalled();
            expect(tokenStorage.clearTokens).toHaveBeenCalled();
        });

        it('should accept custom logout request data', async () => {
            const mockResponse: BaseResponse = {
                success: true,
                message: 'Đăng xuất thành công',
            };

            mockPost.mockResolvedValueOnce(mockResponse);

            await authService.logout({ refresh_token: 'custom-refresh-token' });

            expect(mockPost).toHaveBeenCalledWith('/auth/logout', {
                refresh_token: 'custom-refresh-token',
            });
        });
    });

    // ================================
    // REFRESH TOKEN TESTS
    // ================================
    describe('refreshToken', () => {
        it('should throw error if no refresh token available', async () => {
            await expect(authService.refreshToken()).rejects.toThrow(
                'No refresh token available'
            );
        });
    });

    // ================================
    // CHANGE PASSWORD TESTS
    // ================================
    describe('changePassword', () => {
        it('should change password successfully', async () => {
            const mockResponse: BaseResponse = {
                success: true,
                message: 'Mật khẩu đã được thay đổi',
            };

            mockPut.mockResolvedValueOnce(mockResponse);

            const result = await authService.changePassword({
                current_password: 'oldpassword',
                new_password: 'newpassword123',
            });

            expect(mockPut).toHaveBeenCalledWith('/users/change-password', {
                current_password: 'oldpassword',
                new_password: 'newpassword123',
            });
            expect(result.success).toBe(true);
        });

        it('should handle wrong current password', async () => {
            const mockError = {
                success: false,
                error: {
                    code: 'INVALID_PASSWORD',
                    message: 'Mật khẩu hiện tại không đúng',
                },
                status: 400,
            };

            mockPut.mockRejectedValueOnce(mockError);

            await expect(
                authService.changePassword({
                    current_password: 'wrongpassword',
                    new_password: 'newpassword123',
                })
            ).rejects.toMatchObject({
                success: false,
            });
        });
    });

    // ================================
    // HELPER FUNCTIONS TESTS
    // ================================
    describe('helper functions', () => {
        it('getCurrentUser should return null when no user in localStorage', () => {
            const user = authService.getCurrentUser();
            expect(user).toBeNull();
        });

        it('isAuthenticated should return false when no token', () => {
            const result = authService.isAuthenticated();
            expect(result).toBe(false);
        });

        it('isAdmin should return false for non-admin user', () => {
            expect(authService.isAdmin()).toBe(false);
        });

        it('isModerator should return false for regular user', () => {
            expect(authService.isModerator()).toBe(false);
        });
    });
});
