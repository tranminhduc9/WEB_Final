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
    const response = await axiosClient.post<any, ApiResponse<LoginResponse>>(
      AUTH_ENDPOINTS.LOGIN,
      data
    );
    return response;
  },

  /**
   * Đăng ký
   */
  register: async (data: RegisterRequest): Promise<ApiResponse<RegisterResponse>> => {
    const response = await axiosClient.post<any, ApiResponse<RegisterResponse>>(
      AUTH_ENDPOINTS.REGISTER,
      data
    );
    return response;
  },

  /**
   * Đăng xuất
   */
  logout: async (): Promise<ApiResponse<null>> => {
    const response = await axiosClient.post<any, ApiResponse<null>>(AUTH_ENDPOINTS.LOGOUT);
    return response;
  },

  /**
   * Refresh token
   */
  refreshToken: async (data: RefreshTokenRequest): Promise<ApiResponse<RefreshTokenResponse>> => {
    const response = await axiosClient.post<any, ApiResponse<RefreshTokenResponse>>(
      AUTH_ENDPOINTS.REFRESH,
      data
    );
    return response;
  },

  /**
   * Lấy thông tin user hiện tại
   */
  getCurrentUser: async (): Promise<ApiResponse<User>> => {
    const response = await axiosClient.get<any, ApiResponse<User>>(AUTH_ENDPOINTS.ME);
    return response;
  },

  /**
   * Quên mật khẩu - gửi OTP
   */
  forgotPassword: async (data: ForgotPasswordRequest): Promise<ApiResponse<{ message: string }>> => {
    const response = await axiosClient.post<any, ApiResponse<{ message: string }>>(
      AUTH_ENDPOINTS.FORGOT_PASSWORD,
      data
    );
    return response;
  },

  /**
   * Reset mật khẩu với OTP
   */
  resetPassword: async (data: ResetPasswordRequest): Promise<ApiResponse<{ message: string }>> => {
    const response = await axiosClient.post<any, ApiResponse<{ message: string }>>(
      AUTH_ENDPOINTS.RESET_PASSWORD,
      data
    );
    return response;
  },

  /**
   * Đổi mật khẩu (khi đã đăng nhập)
   */
  changePassword: async (data: ChangePasswordRequest): Promise<ApiResponse<{ message: string }>> => {
    const response = await axiosClient.post<any, ApiResponse<{ message: string }>>(
      AUTH_ENDPOINTS.CHANGE_PASSWORD,
      data
    );
    return response;
  },

  /**
   * Xác thực email
   */
  verifyEmail: async (token: string): Promise<ApiResponse<{ message: string }>> => {
    const response = await axiosClient.post<any, ApiResponse<{ message: string }>>(
      AUTH_ENDPOINTS.VERIFY_EMAIL,
      { token }
    );
    return response;
  },
};

export default authApi;

