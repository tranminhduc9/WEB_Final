/**
 * Auth Service - Business logic cho authentication
 * Strict TypeScript - No `any` types
 * API Base URL: http://localhost:8080/api/v1
 */

import axiosClient, { tokenStorage } from '../api/axiosClient';
import type {
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  BaseResponse,
  User,
  ChangePasswordRequest,
  ForgotPasswordRequest,
  ResetPasswordRequest,
  RefreshTokenResponse,
  LogoutRequest,
} from '../types/auth';
import {
  isApiErrorResponse,
  getValidationErrors,
} from '../types/auth';

// User storage key
const USER_STORAGE_KEY = 'user';

// ============================
// AUTH SERVICE
// ============================
export const authService = {
  /**
   * Đăng nhập
   * POST /auth/login
   * Body: { email, password }
   * Returns: { success: true, access_token: "...", user: { ... } }
   */
  login: async (credentials: LoginRequest): Promise<AuthResponse> => {
    const response = await axiosClient.post<
      LoginRequest,
      AuthResponse
    >('/auth/login', credentials);

    // Lưu tokens và user info
    if (response.success && response.access_token) {
      tokenStorage.setTokens(response.access_token, response.refresh_token);

      // Normalize user data với alias fields cho backward compatibility
      const normalizedUser = {
        ...response.user,
        name: response.user.full_name || response.user.name,
        avatar: response.user.avatar_url || response.user.avatar,
      };
      localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(normalizedUser));

      // Dispatch event để components khác biết
      window.dispatchEvent(new CustomEvent('auth:login', { detail: normalizedUser }));
    }

    return response;
  },

  /**
   * Đăng ký
   * POST /auth/register
   * Body: { full_name, email, password }
   * Returns: 201 { success: true, message: "..." }
   */
  register: async (data: RegisterRequest): Promise<BaseResponse> => {
    const response = await axiosClient.post<
      RegisterRequest,
      BaseResponse
    >('/auth/register', data);

    return response;
  },

  /**
   * Đăng xuất
   * POST /auth/logout
   * Body: { refresh_token: string }
   * Returns: BaseResponse
   */
  logout: async (data?: LogoutRequest): Promise<BaseResponse> => {
    try {
      const refreshToken = data?.refresh_token || tokenStorage.getRefreshToken();

      const response = await axiosClient.post<
        LogoutRequest,
        BaseResponse
      >('/auth/logout', {
        refresh_token: refreshToken || '',
      });

      return response;
    } catch (error) {
      // Log error but still clear local data
      console.warn('Logout API failed:', error);
      throw error;
    } finally {
      // Always clear local tokens and user data
      tokenStorage.clearTokens();
      localStorage.removeItem(USER_STORAGE_KEY);
      window.dispatchEvent(new CustomEvent('auth:logout'));
    }
  },

  /**
   * Refresh access token
   * POST /auth/refresh
   * Returns: AuthResponse with new access_token and user
   */
  refreshToken: async (): Promise<RefreshTokenResponse> => {
    const refreshToken = tokenStorage.getRefreshToken();

    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await axiosClient.post<
      { refresh_token: string },
      RefreshTokenResponse
    >('/auth/refresh', { refresh_token: refreshToken });

    // Lưu tokens mới và update user nếu có
    if (response.success && response.access_token) {
      tokenStorage.setTokens(response.access_token, response.refresh_token);

      // Update user in localStorage if returned
      if (response.user) {
        // Normalize user data với alias fields
        const normalizedUser = {
          ...response.user,
          name: response.user.full_name || response.user.name,
          avatar: response.user.avatar_url || response.user.avatar,
        };
        localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(normalizedUser));
        window.dispatchEvent(new CustomEvent('user:updated', { detail: normalizedUser }));
      }
    }

    return response;
  },

  /**
   * Lấy user hiện tại từ localStorage
   */
  getCurrentUser: (): User | null => {
    const userStr = localStorage.getItem(USER_STORAGE_KEY);
    if (!userStr) return null;

    try {
      const user = JSON.parse(userStr) as User;

      // Normalize: đảm bảo có cả alias fields cho backward compatibility
      if (user && !user.avatar && user.avatar_url) {
        user.avatar = user.avatar_url;
      }
      if (user && !user.name && user.full_name) {
        user.name = user.full_name;
      }

      return user;
    } catch {
      return null;
    }
  },

  /**
   * Fetch user profile từ server
   * GET /auth/me
   */
  fetchCurrentUser: async (): Promise<User | null> => {
    const token = tokenStorage.getAccessToken();
    if (!token) return null;

    try {
      interface UserMeResponse {
        success: boolean;
        user: User;
      }

      const response = await axiosClient.get<never, UserMeResponse>('/auth/me');

      if (response.success && response.user) {
        // Normalize user data với alias fields
        const normalizedUser = {
          ...response.user,
          name: response.user.full_name || response.user.name,
          avatar: response.user.avatar_url || response.user.avatar,
        };
        localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(normalizedUser));
        return normalizedUser;
      }
      return null;
    } catch {
      return null;
    }
  },

  /**
   * Kiểm tra đã đăng nhập chưa
   */
  isAuthenticated: (): boolean => {
    const token = tokenStorage.getAccessToken();
    if (!token) return false;

    return !tokenStorage.isTokenExpired(token);
  },

  /**
   * Kiểm tra có phải admin không
   * role_id: 1 = admin
   */
  isAdmin: (): boolean => {
    const user = authService.getCurrentUser();
    return user?.role_id === 1;
  },

  /**
   * Kiểm tra có phải moderator không
   * role_id: 1 = admin, 2 = moderator
   */
  isModerator: (): boolean => {
    const user = authService.getCurrentUser();
    return user?.role_id === 1 || user?.role_id === 2;
  },

  /**
   * Quên mật khẩu
   * POST /auth/forgot-password
   * Body: { email }
   */
  forgotPassword: async (email: string): Promise<BaseResponse> => {
    const response = await axiosClient.post<
      ForgotPasswordRequest,
      BaseResponse
    >('/auth/forgot-password', { email });

    return response;
  },

  /**
   * Reset mật khẩu
   * POST /auth/reset-password
   * Body: { email, token, new_password }
   */
  resetPassword: async (data: ResetPasswordRequest): Promise<BaseResponse> => {
    const response = await axiosClient.post<
      ResetPasswordRequest,
      BaseResponse
    >('/auth/reset-password', data);

    return response;
  },

  /**
   * Đổi mật khẩu (khi đã đăng nhập)
   * PUT /users/change-password
   * Body: { current_password, new_password }
   */
  changePassword: async (data: ChangePasswordRequest): Promise<BaseResponse> => {
    const response = await axiosClient.put<
      ChangePasswordRequest,
      BaseResponse
    >('/users/change-password', data);

    return response;
  },

  /**
   * Verify email
   * GET /auth/verify-email?token=xxx
   */
  verifyEmail: async (token: string): Promise<BaseResponse> => {
    const response = await axiosClient.get<never, BaseResponse>(
      `/auth/verify-email?token=${encodeURIComponent(token)}`
    );

    return response;
  },
};

// ============================
// ERROR HELPERS (re-export từ types)
// ============================
export { isApiErrorResponse, getValidationErrors };

export default authService;
