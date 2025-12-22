/**
 * Axios Client - Configured axios instance với interceptors
 */

import axios, { 
  AxiosInstance, 
  AxiosError, 
  InternalAxiosRequestConfig,
  AxiosResponse 
} from 'axios';
import type { ApiResponse, ApiError } from '../types';

// API Base URL - lấy từ env hoặc default
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Token storage keys
const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

// Token helpers
export const tokenStorage = {
  getAccessToken: (): string | null => localStorage.getItem(ACCESS_TOKEN_KEY),
  getRefreshToken: (): string | null => localStorage.getItem(REFRESH_TOKEN_KEY),
  
  setTokens: (accessToken: string, refreshToken: string): void => {
    localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
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

// Request interceptor - Thêm token vào header
axiosClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = tokenStorage.getAccessToken();
    
    if (token && !tokenStorage.isTokenExpired(token)) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Xử lý errors và refresh token
axiosClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  async (error: AxiosError<ApiError>) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
    
    // Nếu lỗi 401 và chưa retry
    if (error.response?.status === 401 && !originalRequest._retry) {
      // Nếu đang refresh token, đợi
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
          // Gọi refresh token endpoint
          const response = await axios.post<ApiResponse<{
            access_token: string;
            refresh_token: string;
          }>>(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });
          
          if (response.data.success && response.data.data) {
            const { access_token, refresh_token } = response.data.data;
            tokenStorage.setTokens(access_token, refresh_token);
            
            processQueue(null, access_token);
            
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
            return axiosClient(originalRequest);
          }
        } catch (refreshError) {
          processQueue(new Error('Refresh token failed'), null);
          tokenStorage.clearTokens();
          
          // Dispatch event để AuthContext biết cần logout
          window.dispatchEvent(new CustomEvent('auth:logout'));
          
          return Promise.reject(refreshError);
        } finally {
          isRefreshing = false;
        }
      } else {
        // Không có refresh token hoặc đã hết hạn
        tokenStorage.clearTokens();
        window.dispatchEvent(new CustomEvent('auth:logout'));
      }
    }
    
    // Format error message
    const errorMessage = error.response?.data?.message || error.message || 'Có lỗi xảy ra';
    
    return Promise.reject({
      message: errorMessage,
      error_code: error.response?.data?.error_code || 'UNKNOWN_ERROR',
      status: error.response?.status,
      originalError: error,
    });
  }
);

export default axiosClient;

