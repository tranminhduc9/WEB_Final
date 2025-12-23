/**
 * User Types - Các types liên quan đến user profile
 */

import type { User, UserRole } from './auth';

// Update profile
export interface UpdateProfileRequest {
  name?: string;
  phone?: string;
  address?: string;
  avatar?: string;
}

export interface UpdateProfileResponse {
  user: User;
  message: string;
}

// User profile extended
export interface UserProfile extends User {
  bio?: string;
  location?: string;
  website?: string;
  social_links?: {
    facebook?: string;
    instagram?: string;
    twitter?: string;
  };
  stats?: {
    posts_count: number;
    likes_count: number;
    comments_count: number;
  };
}

// User preferences
export interface UserPreferences {
  notifications_enabled: boolean;
  email_notifications: boolean;
  language: string;
  theme: 'light' | 'dark' | 'system';
}

// Avatar upload
export interface AvatarUploadResponse {
  url: string;
  message: string;
}

