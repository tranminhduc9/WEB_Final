/**
 * User API - Các API endpoints cho user profile
 */

import axiosClient from './axiosClient';
import type {
  ApiResponse,

  UserProfile,
  UpdateProfileRequest,
  UpdateProfileResponse,
  AvatarUploadResponse,
} from '../types';

const USER_ENDPOINTS = {
  PROFILE: '/users/profile',
  UPDATE_PROFILE: '/users/profile',
  AVATAR: '/users/avatar',
  PREFERENCES: '/users/preferences',
};

export const userApi = {
  /**
   * Lấy profile của user hiện tại
   */
  getProfile: async (): Promise<ApiResponse<UserProfile>> => {
    const response = await axiosClient.get<any, ApiResponse<UserProfile>>(USER_ENDPOINTS.PROFILE);
    return response;
  },

  /**
   * Lấy profile của user khác (public)
   */
  getUserById: async (userId: string): Promise<ApiResponse<UserProfile>> => {
    const response = await axiosClient.get<any, ApiResponse<UserProfile>>(`/users/${userId}`);
    return response;
  },

  /**
   * Cập nhật profile
   */
  updateProfile: async (data: UpdateProfileRequest): Promise<ApiResponse<UpdateProfileResponse>> => {
    const response = await axiosClient.put<any, ApiResponse<UpdateProfileResponse>>(
      USER_ENDPOINTS.UPDATE_PROFILE,
      data
    );
    return response;
  },

  /**
   * Upload avatar
   */
  uploadAvatar: async (file: File): Promise<ApiResponse<AvatarUploadResponse>> => {
    const formData = new FormData();
    formData.append('avatar', file);

    const response = await axiosClient.post<any, ApiResponse<AvatarUploadResponse>>(
      USER_ENDPOINTS.AVATAR,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response;
  },

  /**
   * Xóa avatar
   */
  deleteAvatar: async (): Promise<ApiResponse<{ message: string }>> => {
    const response = await axiosClient.delete<any, ApiResponse<{ message: string }>>(
      USER_ENDPOINTS.AVATAR
    );
    return response;
  },
};

export default userApi;

