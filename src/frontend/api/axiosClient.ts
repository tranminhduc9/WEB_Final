/**
 * Axios Client - Configured axios instance với interceptors
 * Base URL: http://localhost:8080/api/v1
 */

import axios, {
  AxiosInstance,
  AxiosError,
  InternalAxiosRequestConfig,
  AxiosResponse
} from 'axios';
import type { ApiErrorResponse, ApiErrorObject } from '../types/auth';

// API Base URL - theo API spec
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080/api/v1';

// Token storage keys
const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

// Token helpers
export const tokenStorage = {
  getAccessToken: (): string | null => localStorage.getItem(ACCESS_TOKEN_KEY),
  getRefreshToken: (): string | null => localStorage.getItem(REFRESH_TOKEN_KEY),

  setTokens: (accessToken: string, refreshToken?: string): void => {
    localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
    if (refreshToken) {
      localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
    }
  },

  setAccessToken: (accessToken: string): void => {
    localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  },

  clearTokens: (): void => {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem('user');
  },

  isTokenExpired: (token: string): boolean => {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.exp * 1000 < Date.now();
    } catch {
      return true;
    }
  }
};

// Create axios instance
const axiosClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Flag để tránh multiple refresh token requests
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: Error) => void;
}> = [];

const processQueue = (error: Error | null, token: string | null = null): void => {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error);
    } else if (token) {
      resolve(token);
    }
  });
  failedQueue = [];
};

// ============================
// REQUEST INTERCEPTOR
// Tự động attach Authorization: Bearer <token>
// ============================
axiosClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = tokenStorage.getAccessToken();

    // Attach token nếu có và chưa hết hạn
    if (token && !tokenStorage.isTokenExpired(token)) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// ============================
// RESPONSE INTERCEPTOR
// Trả về response.data trực tiếp
// Xử lý errors và refresh token
// ============================
axiosClient.interceptors.response.use(
  // Success: trả về response.data trực tiếp
  (response: AxiosResponse) => {
    return response.data;
  },

  // Error handling
  async (error: AxiosError<ApiErrorResponse>) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // Xử lý 401 Unauthorized - Refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({
            resolve: (token: string) => {
              originalRequest.headers.Authorization = `Bearer ${token}`;
              resolve(axiosClient(originalRequest));
            },
            reject: (err: Error) => {
              reject(err);
            },
          });
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refreshToken = tokenStorage.getRefreshToken();

      if (refreshToken && !tokenStorage.isTokenExpired(refreshToken)) {
        try {
          const response = await axios.post<{
            success: boolean;
            access_token: string;
            refresh_token?: string;
          }>(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });

          if (response.data.success && response.data.access_token) {
            const newAccessToken = response.data.access_token;
            const newRefreshToken = response.data.refresh_token;

            tokenStorage.setTokens(newAccessToken, newRefreshToken);
            processQueue(null, newAccessToken);

            originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
            return axiosClient(originalRequest);
          }
        } catch (refreshError) {
          processQueue(new Error('Refresh token failed'), null);
          tokenStorage.clearTokens();
          window.dispatchEvent(new CustomEvent('auth:logout'));
          return Promise.reject(refreshError);
        } finally {
          isRefreshing = false;
        }
      } else {
        tokenStorage.clearTokens();
        window.dispatchEvent(new CustomEvent('auth:logout'));
      }
    }

    // Xử lý 422 Validation Error - theo API spec
    if (error.response?.status === 422) {
      const errorData = error.response.data;
      if (errorData && errorData.error) {
        return Promise.reject({
          success: false,
          error: errorData.error,
          status: 422,
        } as ApiErrorResponse & { status: number });
      }
    }

    // Xử lý các lỗi khác
    const errorObject: ApiErrorObject = {
      code: error.response?.data?.error?.code || 'UNKNOWN_ERROR',
      message: error.response?.data?.error?.message || error.message || 'Có lỗi xảy ra',
      details: error.response?.data?.error?.details,
    };

    return Promise.reject({
      success: false,
      error: errorObject,
      status: error.response?.status,
    } as ApiErrorResponse & { status?: number });
  }
);

export default axiosClient;
