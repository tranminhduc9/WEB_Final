/**
 * Auth Types - Định nghĩa types cho authentication theo API Spec
 * Base URL: http://localhost:8080/api/v1
 */

// User roles
export type UserRole = 'user' | 'admin' | 'moderator';

// User model
export interface User {
  id: string;
  email: string;
  name: string;
  full_name?: string;
  avatar?: string | null;
  role: UserRole;
  phone?: string;
  address?: string;
  created_at?: string;
  updated_at?: string;
  is_active?: boolean;
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
