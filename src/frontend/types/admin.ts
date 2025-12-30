/**
 * Admin Types - Types cho Admin module
 * Theo WEB_CK.md và db.md
 */

// ============================
// DASHBOARD
// ============================

export interface DashboardStats {
  total_users: number;
  total_posts: number;
  total_places: number;
  total_reports: number;
  pending_posts: number;
  new_users_today: number;
  new_posts_today: number;
}

export interface DashboardResponse {
  success: boolean;
  data: DashboardStats;
}

// ============================
// USER MANAGEMENT
// ============================

export interface AdminUser {
  id: number;
  email: string;
  full_name: string;
  avatar_url?: string | null;
  bio?: string | null;
  role_id: number;           // 1=admin, 2=moderator, 3=user
  is_active: boolean;
  ban_reason?: string | null;
  reputation_score: number;
  last_login_at?: string | null;
  created_at: string;
  updated_at?: string;
}

export interface AdminUserListParams {
  status?: 'active' | 'banned';
  page?: number;
}

// ============================
// COMMENT MANAGEMENT
// ============================

export interface AdminComment {
  _id: string;
  post_id: string;
  user: {
    id: number;
    full_name: string;
    avatar_url?: string;
  };
  content: string;
  parent_id?: string | null;  // null = root comment, có ID = reply
  created_at: string;
}

// ============================
// REPORT MANAGEMENT
// ============================

export interface AdminReport {
  _id: string;
  target_type: 'post' | 'comment';
  target_id: string;
  reporter: {
    id: number;
    full_name: string;
  };
  reason: string;
  description?: string;
  created_at: string;
}

// ============================
// PLACE MANAGEMENT
// ============================

export interface PlaceCreateRequest {
  name: string;
  district_id: number;
  place_type_id: number;
  description?: string;
  address_detail?: string;
  latitude: number;
  longitude: number;
  open_hour?: string;   // Format: "HH:MM"
  close_hour?: string;
  price_min?: number;
  price_max?: number;
  images?: string[];
}

// PlaceUpdateRequest is same as PlaceCreateRequest
export type PlaceUpdateRequest = PlaceCreateRequest;

// ============================
// POST MANAGEMENT
// ============================

export interface AdminPostListParams {
  status?: 'pending' | 'published' | 'rejected';
  page?: number;
}

export interface UpdatePostStatusRequest {
  status: 'published' | 'rejected';
  reason?: string;
}
