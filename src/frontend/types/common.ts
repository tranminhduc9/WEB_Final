/**
 * Common Types - Các types dùng chung trong toàn bộ ứng dụng
 */

// API Response chuẩn từ Backend
export interface ApiResponse<T = unknown> {
  success: boolean;
  message: string;
  data: T | null;
  error_code?: string;
}

// Pagination
export interface PaginationParams {
  page: number;
  limit: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

// Error types
export interface ApiError {
  success: false;
  message: string;
  error_code: string;
  data: null;
}

// Loading states
export type LoadingState = 'idle' | 'loading' | 'success' | 'error';

// Select options
export interface SelectOption<T = string> {
  label: string;
  value: T;
}

// Date range filter
export interface DateRange {
  from: Date | null;
  to: Date | null;
}

