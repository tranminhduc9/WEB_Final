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
  PROFILE: '/users/me',
  UPDATE_PROFILE: '/users/me',
  AVATAR: '/upload',
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
   * POST /upload - multipart/form-data with 'files' field
   * Response: { success: boolean, urls: string[] }
   */
  uploadAvatar: async (file: File): Promise<ApiResponse<AvatarUploadResponse>> => {
    const formData = new FormData();
    formData.append('files', file);

    const response = await axiosClient.post<any, ApiResponse<{ urls: string[] }>>(
      USER_ENDPOINTS.AVATAR,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );

    // Transform response to match AvatarUploadResponse
    const urls = response.data?.urls;
    if (response.success && urls && urls.length > 0) {
      return {
        success: true,
        data: { url: urls[0], message: 'Avatar uploaded successfully' },
        message: 'Avatar uploaded successfully'
      };
    }

    return response as unknown as ApiResponse<AvatarUploadResponse>;
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

