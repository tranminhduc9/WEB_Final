/**
 * Auth Types - Các types liên quan đến authentication
 */

// User roles
export type UserRole = 'user' | 'admin' | 'moderator';

// User model
export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string | null;
  role: UserRole;
  phone?: string;
  address?: string;
  created_at?: string;
  updated_at?: string;
  is_active?: boolean;
}

// Login
export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  user: User;
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

// Register
export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
  phone?: string;
}

export interface RegisterResponse {
  user: User;
  message: string;
}

// Token
export interface TokenPayload {
  user_id: string;
  email: string;
  role: UserRole;
  exp: number;
  iat: number;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface RefreshTokenResponse {
  access_token: string;
  refresh_token: string;
  expires_in: number;
}

// Password
export interface ForgotPasswordRequest {
  email: string;
}

export interface ResetPasswordRequest {
  email: string;
  otp: string;
  new_password: string;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

// Auth state
export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

