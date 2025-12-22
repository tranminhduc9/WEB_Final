/**
 * Admin Types - Các types cho Admin Dashboard
 */

import type { User, UserRole } from './auth';
import type { PaginatedResponse } from './common';

// User management
export interface AdminUserListParams {
  page?: number;
  limit?: number;
  search?: string;
  role?: UserRole | 'all';
  is_active?: boolean | 'all';
  sort_by?: 'name' | 'email' | 'created_at' | 'role';
  sort_order?: 'asc' | 'desc';
}

export interface AdminUser extends User {
  last_login?: string;
  login_count?: number;
  is_verified?: boolean;
}

export type AdminUserListResponse = PaginatedResponse<AdminUser>;

// Create user (admin)
export interface CreateUserRequest {
  email: string;
  password: string;
  name: string;
  role: UserRole;
  phone?: string;
  is_active?: boolean;
}

// Update user (admin)
export interface UpdateUserRequest {
  name?: string;
  email?: string;
  role?: UserRole;
  phone?: string;
  is_active?: boolean;
}

// Delete user
export interface DeleteUserResponse {
  message: string;
  deleted_user_id: string;
}

// Dashboard stats
export interface DashboardStats {
  total_users: number;
  active_users: number;
  new_users_today: number;
  new_users_this_week: number;
  total_posts: number;
  total_comments: number;
  user_growth: {
    date: string;
    count: number;
  }[];
}

// Audit logs
export interface AuditLog {
  id: string;
  user_id: string;
  user_email: string;
  action: string;
  resource_type: string;
  resource_id?: string;
  ip_address: string;
  user_agent: string;
  details?: Record<string, unknown>;
  created_at: string;
}

export type AuditLogListResponse = PaginatedResponse<AuditLog>;

