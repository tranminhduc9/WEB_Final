/**
 * Auth Service - Business logic cho authentication
 */

import { authApi, tokenStorage } from '../api';
import type {
  LoginRequest,
  RegisterRequest,
  User,
  ChangePasswordRequest,
  ForgotPasswordRequest,
  ResetPasswordRequest,
} from '../types';

// User storage key
const USER_STORAGE_KEY = 'user';

// Demo mode - set to false when backend is ready
const DEMO_MODE = true;

// Demo accounts for testing
const DEMO_ACCOUNTS: Record<string, { password: string; user: User }> = {
  'admin@demo.com': {
    password: '123456',
    user: {
      id: 'demo-admin-001',
      email: 'admin@demo.com',
      name: 'Admin User',
      role: 'admin',
      avatar: null,
    },
  },
  'user@demo.com': {
    password: '123456',
    user: {
      id: 'demo-user-001',
      email: 'user@demo.com',
      name: 'Test User',
      role: 'user',
      avatar: null,
    },
  },
  'mod@demo.com': {
    password: '123456',
    user: {
      id: 'demo-mod-001',
      email: 'mod@demo.com',
      name: 'Moderator',
      role: 'moderator',
      avatar: null,
    },
  },
};

export const authService = {
  /**
   * Đăng nhập
   */
  login: async (credentials: LoginRequest): Promise<User> => {
    // Demo mode - không cần backend
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 500)); // Simulate network delay
      
      const account = DEMO_ACCOUNTS[credentials.email.toLowerCase()];
      if (account && account.password === credentials.password) {
        const user = account.user;
        const fakeToken = btoa(JSON.stringify({ user_id: user.id, exp: Date.now() + 3600000 }));
        
        tokenStorage.setTokens(fakeToken, fakeToken);
        localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user));
        
        window.dispatchEvent(new CustomEvent('auth:login', { detail: user }));
        return user;
      }
      throw new Error('Email hoặc mật khẩu không đúng');
    }
    
    // Production mode - call real API
    const response = await authApi.login(credentials);
    
    if (!response.success || !response.data) {
      throw new Error(response.message || 'Đăng nhập thất bại');
    }
    
    const { user, access_token, refresh_token } = response.data;
    
    // Lưu tokens và user info
    tokenStorage.setTokens(access_token, refresh_token);
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user));
    
    // Dispatch event để components khác biết
    window.dispatchEvent(new CustomEvent('auth:login', { detail: user }));
    
    return user;
  },

  /**
   * Đăng ký
   */
  register: async (data: RegisterRequest): Promise<User> => {
    // Demo mode
    if (DEMO_MODE) {
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Check if email already exists
      if (DEMO_ACCOUNTS[data.email.toLowerCase()]) {
        throw new Error('Email đã được sử dụng');
      }
      
      // Create demo user (in real app, this would be saved to backend)
      const newUser: User = {
        id: `demo-user-${Date.now()}`,
        email: data.email,
        name: data.name,
        role: 'user',
        phone: data.phone,
        avatar: null,
      };
      
      console.log('Demo: User registered:', newUser);
      return newUser;
    }
    
    // Production mode
    const response = await authApi.register(data);
    
    if (!response.success || !response.data) {
      throw new Error(response.message || 'Đăng ký thất bại');
    }
    
    return response.data.user;
  },

  /**
   * Đăng xuất
   */
  logout: async (): Promise<void> => {
    try {
      await authApi.logout();
    } catch (error) {
      // Ignore error, still clear local data
      console.warn('Logout API failed:', error);
    } finally {
      tokenStorage.clearTokens();
      localStorage.removeItem(USER_STORAGE_KEY);
      window.dispatchEvent(new CustomEvent('auth:logout'));
    }
  },

  /**
   * Lấy user hiện tại từ localStorage
   */
  getCurrentUser: (): User | null => {
    const userStr = localStorage.getItem(USER_STORAGE_KEY);
    if (!userStr) return null;
    
    try {
      return JSON.parse(userStr) as User;
    } catch {
      return null;
    }
  },

  /**
   * Fetch user mới nhất từ server
   */
  fetchCurrentUser: async (): Promise<User | null> => {
    const token = tokenStorage.getAccessToken();
    if (!token) return null;
    
    try {
      const response = await authApi.getCurrentUser();
      if (response.success && response.data) {
        localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(response.data));
        return response.data;
      }
      return null;
    } catch {
      return null;
    }
  },

  /**
   * Kiểm tra đã đăng nhập chưa
   */
  isAuthenticated: (): boolean => {
    const token = tokenStorage.getAccessToken();
    if (!token) return false;
    
    return !tokenStorage.isTokenExpired(token);
  },

  /**
   * Kiểm tra có phải admin không
   */
  isAdmin: (): boolean => {
    const user = authService.getCurrentUser();
    return user?.role === 'admin';
  },

  /**
   * Kiểm tra có phải moderator không
   */
  isModerator: (): boolean => {
    const user = authService.getCurrentUser();
    return user?.role === 'moderator' || user?.role === 'admin';
  },

  /**
   * Quên mật khẩu
   */
  forgotPassword: async (email: string): Promise<string> => {
    const response = await authApi.forgotPassword({ email });
    
    if (!response.success) {
      throw new Error(response.message || 'Gửi yêu cầu thất bại');
    }
    
    return response.data?.message || 'Đã gửi OTP đến email';
  },

  /**
   * Reset mật khẩu với OTP
   */
  resetPassword: async (data: ResetPasswordRequest): Promise<string> => {
    const response = await authApi.resetPassword(data);
    
    if (!response.success) {
      throw new Error(response.message || 'Reset mật khẩu thất bại');
    }
    
    return response.data?.message || 'Đổi mật khẩu thành công';
  },

  /**
   * Đổi mật khẩu (khi đã đăng nhập)
   */
  changePassword: async (data: ChangePasswordRequest): Promise<string> => {
    const response = await authApi.changePassword(data);
    
    if (!response.success) {
      throw new Error(response.message || 'Đổi mật khẩu thất bại');
    }
    
    return response.data?.message || 'Đổi mật khẩu thành công';
  },
};

export default authService;

