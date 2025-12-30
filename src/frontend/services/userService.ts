/**
 * User Service - Business logic cho user profile
 */

import { userApi } from '../api';
import type {
  UpdateProfileRequest,
} from '../types';
import type { UserDetailResponse } from '../types/models';

export const userService = {
  /**
   * Lấy profile của user hiện tại
   */
  getProfile: async (): Promise<UserDetailResponse> => {
    const response = await userApi.getProfile();

    if (!response.success || !response.data) {
      throw new Error(response.message || 'Không thể tải profile');
    }

    // Backend returns: { user: {...}, stats, recent_favorites, recent_posts }
    const data = response.data as {
      user?: UserDetailResponse;
      stats?: { posts_count?: number; favorites_count?: number };
      recent_favorites?: unknown[];
      recent_posts?: unknown[];
    };

    // If response has nested user object, spread it with other fields
    if (data.user) {
      return {
        ...data.user,
        recent_favorites: data.recent_favorites,
        recent_posts: data.recent_posts,
      } as UserDetailResponse;
    }

    // Fallback: response.data is already flat UserDetailResponse
    return response.data as UserDetailResponse;
  },

  /**
   * Lấy profile của user khác
   */
  getUserProfile: async (userId: string): Promise<UserDetailResponse> => {
    const response = await userApi.getUserById(userId);

    if (!response.success || !response.data) {
      throw new Error(response.message || 'Không tìm thấy user');
    }

    return response.data as UserDetailResponse;
  },

  /**
   * Cập nhật profile
   */
  updateProfile: async (data: UpdateProfileRequest): Promise<UserDetailResponse> => {
    const response = await userApi.updateProfile(data);

    if (!response.success || !response.data) {
      throw new Error(response.message || 'Cập nhật profile thất bại');
    }

    // Cập nhật localStorage
    const currentUser = localStorage.getItem('user');
    if (currentUser) {
      const user = JSON.parse(currentUser);
      localStorage.setItem('user', JSON.stringify({
        ...user,
        ...response.data.user,
      }));

      // Dispatch event
      window.dispatchEvent(new CustomEvent('user:updated', {
        detail: response.data.user
      }));
    }

    return response.data.user as UserDetailResponse;
  },

  /**
   * Upload avatar
   */
  uploadAvatar: async (file: File): Promise<string> => {
    // Validate file
    const maxSize = 5 * 1024 * 1024; // 5MB
    if (file.size > maxSize) {
      throw new Error('File quá lớn. Tối đa 5MB');
    }

    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      throw new Error('Chỉ chấp nhận file ảnh (JPEG, PNG, GIF, WebP)');
    }

    const response = await userApi.uploadAvatar(file);

    if (!response.success || !response.data) {
      throw new Error(response.message || 'Upload avatar thất bại');
    }

    // Cập nhật avatar trong localStorage
    const currentUser = localStorage.getItem('user');
    if (currentUser) {
      const user = JSON.parse(currentUser);
      user.avatar = response.data.url;
      localStorage.setItem('user', JSON.stringify(user));

      window.dispatchEvent(new CustomEvent('user:updated', { detail: user }));
    }

    return response.data.url;
  },

  /**
   * Xóa avatar
   */
  deleteAvatar: async (): Promise<void> => {
    const response = await userApi.deleteAvatar();

    if (!response.success) {
      throw new Error(response.message || 'Xóa avatar thất bại');
    }

    // Cập nhật localStorage
    const currentUser = localStorage.getItem('user');
    if (currentUser) {
      const user = JSON.parse(currentUser);
      user.avatar = null;
      localStorage.setItem('user', JSON.stringify(user));

      window.dispatchEvent(new CustomEvent('user:updated', { detail: user }));
    }
  },
};

export default userService;

