/**
 * Admin API - Các API endpoints cho Admin Dashboard
 */

import axiosClient from './axiosClient';
import type {
  ApiResponse,
  AdminUserListParams,
  AdminUserListResponse,
  AdminUser,
  CreateUserRequest,
  UpdateUserRequest,
  DeleteUserResponse,
  DashboardStats,
  AuditLogListResponse,
} from '../types';

const ADMIN_ENDPOINTS = {
  USERS: '/admin/users',
  DASHBOARD: '/admin/dashboard',
  AUDIT_LOGS: '/admin/audit-logs',
};

export const adminApi = {
  /**
   * Lấy danh sách users (có phân trang, search, filter)
   */
  getUsers: async (params: AdminUserListParams = {}): Promise<ApiResponse<AdminUserListResponse>> => {
    const response = await axiosClient.get<any, ApiResponse<AdminUserListResponse>>(
      ADMIN_ENDPOINTS.USERS,
      { params }
    );
    return response;
  },

  /**
   * Lấy thông tin 1 user
   */
  getUserById: async (userId: string): Promise<ApiResponse<AdminUser>> => {
    const response = await axiosClient.get<any, ApiResponse<AdminUser>>(
      `${ADMIN_ENDPOINTS.USERS}/${userId}`
    );
    return response;
  },

  /**
   * Tạo user mới
   */
  createUser: async (data: CreateUserRequest): Promise<ApiResponse<AdminUser>> => {
    const response = await axiosClient.post<any, ApiResponse<AdminUser>>(
      ADMIN_ENDPOINTS.USERS,
      data
    );
    return response;
  },

  /**
   * Cập nhật user
   */
  updateUser: async (userId: string, data: UpdateUserRequest): Promise<ApiResponse<AdminUser>> => {
    const response = await axiosClient.put<any, ApiResponse<AdminUser>>(
      `${ADMIN_ENDPOINTS.USERS}/${userId}`,
      data
    );
    return response;
  },

  /**
   * Xóa user
   */
  deleteUser: async (userId: string): Promise<ApiResponse<DeleteUserResponse>> => {
    const response = await axiosClient.delete<any, ApiResponse<DeleteUserResponse>>(
      `${ADMIN_ENDPOINTS.USERS}/${userId}`
    );
    return response;
  },

  /**
   * Kích hoạt/Vô hiệu hóa user
   */
  toggleUserStatus: async (userId: string, isActive: boolean): Promise<ApiResponse<AdminUser>> => {
    const response = await axiosClient.patch<any, ApiResponse<AdminUser>>(
      `${ADMIN_ENDPOINTS.USERS}/${userId}/status`,
      { is_active: isActive }
    );
    return response;
  },

  /**
   * Lấy thống kê dashboard
   */
  getDashboardStats: async (): Promise<ApiResponse<DashboardStats>> => {
    const response = await axiosClient.get<any, ApiResponse<DashboardStats>>(
      ADMIN_ENDPOINTS.DASHBOARD
    );
    return response;
  },

  /**
   * Lấy audit logs
   */
  getAuditLogs: async (params: {
    page?: number;
    limit?: number;
    user_id?: string;
    action?: string;
    from_date?: string;
    to_date?: string;
  } = {}): Promise<ApiResponse<AuditLogListResponse>> => {
    const response = await axiosClient.get<any, ApiResponse<AuditLogListResponse>>(
      ADMIN_ENDPOINTS.AUDIT_LOGS,
      { params }
    );
    return response;
  },
};

export default adminApi;

