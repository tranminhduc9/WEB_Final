/**
 * Auth Types - Định nghĩa types cho authentication theo API Spec
 * Base URL: http://localhost:8080/api/v1
 */

// User roles
export type UserRole = 'user' | 'admin' | 'moderator';

// Role ID mapping: 1 = admin, 2 = moderator, 3 = user
export type RoleId = 1 | 2 | 3;

// User model - Synced with database.py Schema v3.1
export interface User {
  // Primary key
  id: number;

  // Thông tin cơ bản
  full_name: string;
  email: string;

  // Thông tin bổ sung
  avatar_url?: string | null;
  bio?: string | null;

  // Role (FK to roles table: 1=admin, 2=moderator, 3=user)
  role_id: RoleId;
  role?: UserRole;  // Computed from role_id for backward compatibility

  // Status
  reputation_score?: number;
  is_active?: boolean;
  ban_reason?: string | null;

  // Soft delete
  deleted_at?: string | null;

  // Timestamps
  last_login_at?: string | null;
  created_at?: string;
  updated_at?: string;

  // Legacy fields (for backward compatibility with existing code)
  name?: string;           // Alias for full_name
  avatar?: string | null;  // Alias for avatar_url
}

// ============================
// REQUEST TYPES
// ============================

// Login Request
export interface LoginRequest {
  email: string;
  password: string;
}

// Register Request - theo API spec: { full_name, email, password }
export interface RegisterRequest {
  full_name: string;
  email: string;
  password: string;
}

// Legacy support - nếu cần tương thích với code cũ
export interface LegacyRegisterRequest {
  email: string;
  password: string;
  name: string;
  phone?: string;
}

// Refresh Token
export interface RefreshTokenRequest {
  refresh_token: string;
}

// Logout Request
export interface LogoutRequest {
  refresh_token: string;
}

// Password
export interface ForgotPasswordRequest {
  email: string;
}

export interface ResetPasswordRequest {
  email: string;
  token: string;
  new_password: string;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

// ============================
// RESPONSE TYPES
// ============================

// Base Response - cho các API trả về đơn giản
export interface BaseResponse {
  success: boolean;
  message: string;
}

// Auth Response - cho login, trả về token và user
export interface AuthResponse {
  success: boolean;
  access_token: string;
  refresh_token?: string;
  token_type?: string;
  expires_in?: number;
  user: User;
}

// Register Response - API trả về 201 { success: true, message: "..." }
export interface RegisterResponse extends BaseResponse {
  user?: User;
}

// Login Response (legacy support)
export interface LoginResponse {
  user: User;
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

// Refresh Token Response - theo API spec trả về AuthResponse
export interface RefreshTokenResponse {
  success: boolean;
  access_token: string;
  refresh_token?: string;
  expires_in?: number;
  user?: User;
}

// ============================
// ERROR TYPES - Theo API Spec 422
// ============================

// Chi tiết lỗi validation cho từng field
export interface ValidationErrorDetail {
  field: string;
  message: string;
}

// Error object structure
export interface ApiErrorObject {
  code: string;
  message: string;
  details?: ValidationErrorDetail[];
}

// API Error Response - cho 422 Validation Errors
export interface ApiErrorResponse {
  success: false;
  error: ApiErrorObject;
}

// Generic API Error (cho các trường hợp khác)
export interface ApiError {
  success: false;
  message: string;
  error_code?: string;
  data?: null;
}

// ============================
// TOKEN TYPES
// ============================

export interface TokenPayload {
  user_id: string;
  email: string;
  role: UserRole;
  exp: number;
  iat: number;
}

// ============================
// AUTH STATE (for Context)
// ============================

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

// ============================
// HELPER TYPE GUARDS
// ============================

// Type guard để check ApiErrorResponse
export function isApiErrorResponse(error: unknown): error is ApiErrorResponse {
  return (
    typeof error === 'object' &&
    error !== null &&
    'success' in error &&
    (error as ApiErrorResponse).success === false &&
    'error' in error &&
    typeof (error as ApiErrorResponse).error === 'object'
  );
}

// Type guard để check ValidationErrorDetail array
export function hasValidationDetails(
  error: ApiErrorResponse
): error is ApiErrorResponse & { error: { details: ValidationErrorDetail[] } } {
  return Array.isArray(error.error.details) && error.error.details.length > 0;
}

// Helper để extract validation messages
export function getValidationErrors(error: ApiErrorResponse): Record<string, string> {
  const errors: Record<string, string> = {};
  if (hasValidationDetails(error)) {
    error.error.details.forEach((detail) => {
      errors[detail.field] = detail.message;
    });
  }
  return errors;
}

// ============================
// ROLE HELPERS
// ============================

// Role ID to Role name mapping
const ROLE_ID_MAP: Record<RoleId, UserRole> = {
  1: 'admin',
  2: 'moderator',
  3: 'user',
};

// Convert role_id to UserRole
export function getRoleFromId(roleId: RoleId | number): UserRole {
  return ROLE_ID_MAP[roleId as RoleId] || 'user';
}

// Get user role safely (handles both role and role_id)
export function getUserRole(user: User | null | undefined): UserRole {
  if (!user) return 'user';
  if (user.role) return user.role;
  return getRoleFromId(user.role_id);
}

// Check if user has specific role
export function hasRole(user: User | null | undefined, role: UserRole): boolean {
  return getUserRole(user) === role;
}

// Check if user has any of the specified roles
export function hasAnyRole(user: User | null | undefined, roles: UserRole[]): boolean {
  return roles.includes(getUserRole(user));
}
