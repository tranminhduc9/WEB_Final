/**
 * Auth API - Các API endpoints cho authentication
 */

import axiosClient from './axiosClient';
import type {
  ApiResponse,
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  RegisterResponse,
  RefreshTokenRequest,
  RefreshTokenResponse,
  ForgotPasswordRequest,
  ResetPasswordRequest,
  ChangePasswordRequest,
  User,
} from '../types';

const AUTH_ENDPOINTS = {
  LOGIN: '/auth/login',
  REGISTER: '/auth/register',
  LOGOUT: '/auth/logout',
  REFRESH: '/auth/refresh',
  ME: '/auth/me',
  FORGOT_PASSWORD: '/auth/forgot-password',
  RESET_PASSWORD: '/auth/reset-password',
  CHANGE_PASSWORD: '/auth/change-password',
  VERIFY_EMAIL: '/auth/verify-email',
};

export const authApi = {
  /**
   * Đăng nhập
   */
  login: async (data: LoginRequest): Promise<ApiResponse<LoginResponse>> => {
    const response = await axiosClient.post<ApiResponse<LoginResponse>>(
      AUTH_ENDPOINTS.LOGIN,
      data
    );
    return response.data;
  },

  /**
   * Đăng ký
   */
  register: async (data: RegisterRequest): Promise<ApiResponse<RegisterResponse>> => {
    const response = await axiosClient.post<ApiResponse<RegisterResponse>>(
      AUTH_ENDPOINTS.REGISTER,
      data
    );
    return response.data;
  },

  /**
   * Đăng xuất
   */
  logout: async (): Promise<ApiResponse<null>> => {
    const response = await axiosClient.post<ApiResponse<null>>(AUTH_ENDPOINTS.LOGOUT);
    return response.data;
  },

  /**
   * Refresh token
   */
  refreshToken: async (data: RefreshTokenRequest): Promise<ApiResponse<RefreshTokenResponse>> => {
    const response = await axiosClient.post<ApiResponse<RefreshTokenResponse>>(
      AUTH_ENDPOINTS.REFRESH,
      data
    );
    return response.data;
  },

  /**
   * Lấy thông tin user hiện tại
   */
  getCurrentUser: async (): Promise<ApiResponse<User>> => {
    const response = await axiosClient.get<ApiResponse<User>>(AUTH_ENDPOINTS.ME);
    return response.data;
  },

  /**
   * Quên mật khẩu - gửi OTP
   */
  forgotPassword: async (data: ForgotPasswordRequest): Promise<ApiResponse<{ message: string }>> => {
    const response = await axiosClient.post<ApiResponse<{ message: string }>>(
      AUTH_ENDPOINTS.FORGOT_PASSWORD,
      data
    );
    return response.data;
  },

  /**
   * Reset mật khẩu với OTP
   */
  resetPassword: async (data: ResetPasswordRequest): Promise<ApiResponse<{ message: string }>> => {
    const response = await axiosClient.post<ApiResponse<{ message: string }>>(
      AUTH_ENDPOINTS.RESET_PASSWORD,
      data
    );
    return response.data;
  },

  /**
   * Đổi mật khẩu (khi đã đăng nhập)
   */
  changePassword: async (data: ChangePasswordRequest): Promise<ApiResponse<{ message: string }>> => {
    const response = await axiosClient.post<ApiResponse<{ message: string }>>(
      AUTH_ENDPOINTS.CHANGE_PASSWORD,
      data
    );
    return response.data;
  },

  /**
   * Xác thực email
   */
  verifyEmail: async (token: string): Promise<ApiResponse<{ message: string }>> => {
    const response = await axiosClient.post<ApiResponse<{ message: string }>>(
      AUTH_ENDPOINTS.VERIFY_EMAIL,
      { token }
    );
    return response.data;
  },
};

export default authApi;

