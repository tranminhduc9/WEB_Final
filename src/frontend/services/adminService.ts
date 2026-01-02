/**
 * Admin Service - API calls cho Admin module
 * Base URL: http://localhost:8080/api/v1
 * 
 * Endpoints theo WEB_CK.md:
 * - POST /admin/login, /admin/logout
 * - GET /admin/dashboard
 * - GET /admin/users, DELETE /admin/users/{id}, PATCH /admin/users/{id}/ban, /admin/users/{id}/unban
 * - GET /admin/posts, POST /admin/posts, PUT /admin/posts/{id}, DELETE /admin/posts/{id}, PATCH /admin/posts/{id}/status
 * - GET /admin/comments, DELETE /admin/comments/{id}
 * - GET /admin/reports
 * - GET /admin/places, POST /admin/places, PUT /admin/places/{id}, DELETE /admin/places/{id}
 */

import axiosClient from '../api/axiosClient';
import type {
  DashboardResponse,
  AdminUser,
  AdminComment,
  AdminReport,
  PlaceCreateRequest,
  AdminUserListParams,
  AdminPostListParams,
  AdminPlaceListParams,
  AdminReportListParams,
} from '../types/admin';
import type {
  ListResponse,
  PostDetail,
  CreatePostRequest,
  PlaceDetail,
} from '../types/models';
import type {
  AuthResponse,
  BaseResponse,
  LoginRequest,
} from '../types/auth';

// ============================
// ADMIN SERVICE
// ============================

export const adminService = {
  // ===== AUTH =====
  /**
   * Admin đăng nhập
   * POST /admin/login
   */
  login: async (credentials: LoginRequest): Promise<AuthResponse> => {
    return axiosClient.post<LoginRequest, AuthResponse>('/admin/login', credentials);
  },

  /**
   * Admin đăng xuất
   * POST /admin/logout
   */
  logout: async (refreshToken: string): Promise<BaseResponse> => {
    return axiosClient.post<{ refresh_token: string }, BaseResponse>(
      '/admin/logout',
      { refresh_token: refreshToken }
    );
  },

  // ===== DASHBOARD =====
  /**
   * Lấy thống kê dashboard
   * GET /admin/dashboard
   */
  getDashboardStats: async (): Promise<DashboardResponse> => {
    return axiosClient.get<never, DashboardResponse>('/admin/dashboard');
  },

  // ===== USER MANAGEMENT =====
  /**
   * Lấy danh sách users
   * GET /admin/users?status=active|banned&page=1
   */
  getUsers: async (params?: AdminUserListParams): Promise<ListResponse<AdminUser>> => {
    const query = new URLSearchParams();
    if (params?.status) query.append('status', params.status);
    if (params?.page) query.append('page', String(params.page));
    const queryString = query.toString();
    return axiosClient.get<never, ListResponse<AdminUser>>(
      queryString ? `/admin/users?${queryString}` : '/admin/users'
    );
  },

  /**
   * Xóa user
   * DELETE /admin/users/{id}
   */
  deleteUser: async (id: number): Promise<BaseResponse> => {
    return axiosClient.delete<never, BaseResponse>(`/admin/users/${id}`);
  },

  /**
   * Ban user
   * PATCH /admin/users/{id}/ban
   * Body: { reason: string }
   */
  banUser: async (id: number, reason: string): Promise<BaseResponse> => {
    return axiosClient.patch<{ reason: string }, BaseResponse>(
      `/admin/users/${id}/ban`,
      { reason }
    );
  },

  /**
   * Unban user
   * PATCH /admin/users/{id}/unban
   */
  unbanUser: async (id: number): Promise<BaseResponse> => {
    return axiosClient.patch<never, BaseResponse>(`/admin/users/${id}/unban`);
  },

  // ===== POST MANAGEMENT =====
  /**
   * Lấy danh sách posts
   * GET /admin/posts?status=pending|published|rejected&page=1
   */
  getPosts: async (params?: AdminPostListParams): Promise<ListResponse<PostDetail>> => {
    const query = new URLSearchParams();
    if (params?.status) query.append('status', params.status);
    if (params?.page) query.append('page', String(params.page));
    const queryString = query.toString();
    return axiosClient.get<never, ListResponse<PostDetail>>(
      queryString ? `/admin/posts?${queryString}` : '/admin/posts'
    );
  },

  /**
   * Tạo bài viết (Admin)
   * POST /admin/posts
   */
  createPost: async (data: CreatePostRequest): Promise<BaseResponse> => {
    return axiosClient.post<CreatePostRequest, BaseResponse>('/admin/posts', data);
  },

  /**
   * Cập nhật bài viết
   * PUT /admin/posts/{id}
   */
  updatePost: async (id: string, data: CreatePostRequest): Promise<BaseResponse> => {
    return axiosClient.put<CreatePostRequest, BaseResponse>(`/admin/posts/${id}`, data);
  },

  /**
   * Xóa bài viết
   * DELETE /admin/posts/{id}
   * Body: { reason?: string }
   */
  deletePost: async (id: string, reason?: string): Promise<BaseResponse> => {
    return axiosClient.delete<{ reason?: string }, BaseResponse>(
      `/admin/posts/${id}`,
      { data: { reason } }
    );
  },

  /**
   * Duyệt/Từ chối bài viết
   * PATCH /admin/posts/{id}/status
   * Body: { status: 'published'|'rejected', reason?: string }
   */
  updatePostStatus: async (
    id: string,
    status: 'published' | 'rejected',
    reason?: string
  ): Promise<BaseResponse> => {
    return axiosClient.patch<{ status: string; reason?: string }, BaseResponse>(
      `/admin/posts/${id}/status`,
      { status, reason }
    );
  },

  // ===== COMMENT MANAGEMENT =====
  /**
   * Lấy danh sách comments
   * GET /admin/comments
   */
  getComments: async (): Promise<ListResponse<AdminComment>> => {
    return axiosClient.get<never, ListResponse<AdminComment>>('/admin/comments');
  },

  /**
   * Xóa comment
   * DELETE /admin/comments/{id}
   */
  deleteComment: async (id: string): Promise<BaseResponse> => {
    return axiosClient.delete<never, BaseResponse>(`/admin/comments/${id}`);
  },

  // ===== REPORT MANAGEMENT =====
  /**
   * Lấy danh sách reports
   * GET /admin/reports?page=1&limit=20
   */
  getReports: async (params?: AdminReportListParams): Promise<ListResponse<AdminReport>> => {
    const query = new URLSearchParams();
    if (params?.page) query.append('page', String(params.page));
    if (params?.limit) query.append('limit', String(params.limit));
    const queryString = query.toString();
    return axiosClient.get<never, ListResponse<AdminReport>>(
      queryString ? `/admin/reports?${queryString}` : '/admin/reports'
    );
  },

  /**
   * Dismiss/Delete một report
   * DELETE /admin/reports/{id}
   */
  dismissReport: async (id: string): Promise<BaseResponse> => {
    return axiosClient.delete<never, BaseResponse>(`/admin/reports/${id}`);
  },

  // ===== PLACE MANAGEMENT =====
  /**
   * Lấy danh sách places
   * GET /admin/places?page=1&limit=20
   */
  getPlaces: async (params?: AdminPlaceListParams): Promise<ListResponse<PlaceDetail>> => {
    const query = new URLSearchParams();
    if (params?.page) query.append('page', String(params.page));
    if (params?.limit) query.append('limit', String(params.limit));
    const queryString = query.toString();
    return axiosClient.get<never, ListResponse<PlaceDetail>>(
      queryString ? `/admin/places?${queryString}` : '/admin/places'
    );
  },

  /**
   * Tạo địa điểm mới
   * POST /admin/places
   */
  createPlace: async (data: PlaceCreateRequest): Promise<BaseResponse> => {
    return axiosClient.post<PlaceCreateRequest, BaseResponse>('/admin/places', data);
  },

  /**
   * Cập nhật địa điểm
   * PUT /admin/places/{id}
   */
  updatePlace: async (id: number, data: PlaceCreateRequest): Promise<BaseResponse> => {
    return axiosClient.put<PlaceCreateRequest, BaseResponse>(`/admin/places/${id}`, data);
  },

  /**
   * Xóa địa điểm
   * DELETE /admin/places/{id}
   */
  deletePlace: async (id: number): Promise<BaseResponse> => {
    return axiosClient.delete<never, BaseResponse>(`/admin/places/${id}`);
  },

  // ===== AUDIT LOGS =====
  /**
   * Lấy danh sách audit logs
   * GET /api/v1/logs/audit
   */
  getAuditLogs: async (params?: {
    limit?: number;
    offset?: number;
    user_id?: number;
    action_type?: string;
  }): Promise<{
    success: boolean;
    message?: string;
    data?: {
      logs: Array<{
        id: number;
        user_id: number;
        user?: { id: number; full_name: string; email: string };
        action: string;
        details?: string;
        ip_address?: string;
        created_at: string;
      }>;
      total: number;
      limit: number;
      offset: number;
    };
  }> => {
    const query = new URLSearchParams();
    if (params?.limit) query.append('limit', String(params.limit));
    if (params?.offset) query.append('offset', String(params.offset));
    if (params?.user_id) query.append('user_id', String(params.user_id));
    if (params?.action_type) query.append('action_type', params.action_type);
    const queryString = query.toString();
    return axiosClient.get(queryString ? `/logs/audit?${queryString}` : '/logs/audit');
  },

  // ===== ANALYTICS =====
  /**
   * Lấy thống kê truy cập cho admin dashboard
   * GET /api/v1/logs/analytics
   */
  getVisitAnalytics: async (days: number = 30): Promise<{
    success: boolean;
    message?: string;
    data?: {
      visits: {
        success: boolean;
        period_days: number;
        summary: {
          total_visits: number;
          unique_visitors: number;
          logged_in_visitors: number;
        };
        top_places: Array<{
          place_id: number;
          place_name: string;
          visit_count: number;
        }>;
        top_posts: Array<{
          post_id: string;
          visit_count: number;
        }>;
        visits_trend: Array<{
          date: string;
          count: number;
        }>;
      };
      activities: {
        success: boolean;
        period_days: number;
        summary: {
          logins_today: number;
          new_registrations: number;
        };
        activities_breakdown: Array<{
          action: string;
          count: number;
        }>;
        most_active_users: Array<{
          user_id: number;
          full_name: string;
          activity_count: number;
        }>;
      };
    };
  }> => {
    return axiosClient.get(`/logs/analytics?days=${days}`);
  },
};

export default adminService;
