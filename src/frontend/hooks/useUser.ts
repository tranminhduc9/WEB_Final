/**
 * useUser Hook - Hook cho user profile operations
 */

import { useState, useCallback } from 'react';
import { userService } from '../services';
import { useAuthContext } from '../contexts';
import type { UserProfile, UpdateProfileRequest } from '../types';

interface UseUserReturn {
  profile: UserProfile | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  fetchProfile: () => Promise<void>;
  updateProfile: (data: UpdateProfileRequest) => Promise<void>;
  uploadAvatar: (file: File) => Promise<string>;
  deleteAvatar: () => Promise<void>;
  clearError: () => void;
}

/**
 * Custom hook cho user profile
 */
export const useUser = (): UseUserReturn => {
  const { user } = useAuthContext();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Fetch profile
   */
  const fetchProfile = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await userService.getProfile();
      // Cast to UserProfile - role_id from API is number, but RoleId expects 1 | 2 | 3
      setProfile(data as unknown as UserProfile);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Không thể tải profile';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Update profile
   */
  const updateProfile = useCallback(async (data: UpdateProfileRequest) => {
    setIsLoading(true);
    setError(null);

    try {
      const updatedProfile = await userService.updateProfile(data);
      setProfile(updatedProfile as unknown as UserProfile);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Cập nhật thất bại';
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Upload avatar
   */
  const uploadAvatar = useCallback(async (file: File): Promise<string> => {
    setIsLoading(true);
    setError(null);

    try {
      const avatarUrl = await userService.uploadAvatar(file);

      // Update profile state
      if (profile) {
        setProfile({ ...profile, avatar: avatarUrl });
      }

      return avatarUrl;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Upload thất bại';
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [profile]);

  /**
   * Delete avatar
   */
  const deleteAvatar = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      await userService.deleteAvatar();

      // Update profile state
      if (profile) {
        setProfile({ ...profile, avatar: null });
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Xóa avatar thất bại';
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [profile]);

  /**
   * Clear error
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    profile: profile || (user as UserProfile | null),
    isLoading,
    error,
    fetchProfile,
    updateProfile,
    uploadAvatar,
    deleteAvatar,
    clearError,
  };
};

export default useUser;

