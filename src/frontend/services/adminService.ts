/**
 * Admin Service - Business logic cho Admin Dashboard
 */

import { adminApi } from '../api';
import type {
  AdminUserListParams,
  AdminUserListResponse,
  AdminUser,
  CreateUserRequest,
  UpdateUserRequest,
  DashboardStats,
  AuditLogListResponse,
  UserRole,
} from '../types';

export const adminService = {
  /**
   * Lấy danh sách users với phân trang và filter
   */
  getUsers: async (params: AdminUserListParams = {}): Promise<AdminUserListResponse> => {
    const response = await adminApi.getUsers({
      page: params.page || 1,
      limit: params.limit || 10,
      ...params,
    });
    
    if (!response.success || !response.data) {
      throw new Error(response.message || 'Không thể tải danh sách users');
    }
    
    return response.data;
  },

  /**
   * Tìm kiếm users
   */
  searchUsers: async (
    query: string,
    options: { role?: UserRole | 'all'; isActive?: boolean | 'all' } = {}
  ): Promise<AdminUserListResponse> => {
    return adminService.getUsers({
      search: query,
      role: options.role,
      is_active: options.isActive,
    });
  },

  /**
   * Lấy thông tin chi tiết 1 user
   */
  getUserById: async (userId: string): Promise<AdminUser> => {
    const response = await adminApi.getUserById(userId);
    
    if (!response.success || !response.data) {
      throw new Error(response.message || 'Không tìm thấy user');
    }
    
    return response.data;
  },

  /**
   * Tạo user mới
   */
  createUser: async (data: CreateUserRequest): Promise<AdminUser> => {
    // Validate
    if (!data.email || !data.password || !data.name) {
      throw new Error('Vui lòng điền đầy đủ thông tin bắt buộc');
    }
    
    const response = await adminApi.createUser(data);
    
    if (!response.success || !response.data) {
      throw new Error(response.message || 'Tạo user thất bại');
    }
    
    return response.data;
  },

  /**
   * Cập nhật user
   */
  updateUser: async (userId: string, data: UpdateUserRequest): Promise<AdminUser> => {
    const response = await adminApi.updateUser(userId, data);
    
    if (!response.success || !response.data) {
      throw new Error(response.message || 'Cập nhật user thất bại');
    }
    
    return response.data;
  },

  /**
   * Xóa user
   */
  deleteUser: async (userId: string): Promise<void> => {
    const response = await adminApi.deleteUser(userId);
    
    if (!response.success) {
      throw new Error(response.message || 'Xóa user thất bại');
    }
  },

  /**
   * Kích hoạt user
   */
  activateUser: async (userId: string): Promise<AdminUser> => {
    const response = await adminApi.toggleUserStatus(userId, true);
    
    if (!response.success || !response.data) {
      throw new Error(response.message || 'Kích hoạt user thất bại');
    }
    
    return response.data;
  },

  /**
   * Vô hiệu hóa user
   */
  deactivateUser: async (userId: string): Promise<AdminUser> => {
    const response = await adminApi.toggleUserStatus(userId, false);
    
    if (!response.success || !response.data) {
      throw new Error(response.message || 'Vô hiệu hóa user thất bại');
    }
    
    return response.data;
  },

  /**
   * Đổi role của user
   */
  changeUserRole: async (userId: string, role: UserRole): Promise<AdminUser> => {
    return adminService.updateUser(userId, { role });
  },

  /**
   * Lấy thống kê dashboard
   */
  getDashboardStats: async (): Promise<DashboardStats> => {
    const response = await adminApi.getDashboardStats();
    
    if (!response.success || !response.data) {
      throw new Error(response.message || 'Không thể tải thống kê');
    }
    
    return response.data;
  },

  /**
   * Lấy audit logs
   */
  getAuditLogs: async (params: {
    page?: number;
    limit?: number;
    userId?: string;
    action?: string;
    fromDate?: Date;
    toDate?: Date;
  } = {}): Promise<AuditLogListResponse> => {
    const response = await adminApi.getAuditLogs({
      page: params.page,
      limit: params.limit,
      user_id: params.userId,
      action: params.action,
      from_date: params.fromDate?.toISOString(),
      to_date: params.toDate?.toISOString(),
    });
    
    if (!response.success || !response.data) {
      throw new Error(response.message || 'Không thể tải audit logs');
    }
    
    return response.data;
  },
};

export default adminService;

