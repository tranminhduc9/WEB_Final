/**
 * User Types - Các types liên quan đến user profile
 * Synced with database.py Schema v3.1
 */

import type { User } from './auth';

// Update profile request - matches db.md users table
// Fields that can be updated: full_name, bio, avatar_url
export interface UpdateProfileRequest {
  full_name?: string;
  bio?: string;
  avatar_url?: string;
}

export interface UpdateProfileResponse {
  user: User;
  message: string;
}

// User profile extended - bio is now in base User
export interface UserProfile extends User {
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

