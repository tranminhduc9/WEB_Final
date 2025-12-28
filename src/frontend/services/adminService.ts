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
   * GET /admin/reports
   */
  getReports: async (): Promise<ListResponse<AdminReport>> => {
    return axiosClient.get<never, ListResponse<AdminReport>>('/admin/reports');
  },

  // ===== PLACE MANAGEMENT =====
  /**
   * Lấy danh sách places
   * GET /admin/places
   */
  getPlaces: async (): Promise<ListResponse<PlaceDetail>> => {
    return axiosClient.get<never, ListResponse<PlaceDetail>>('/admin/places');
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
};

export default adminService;
