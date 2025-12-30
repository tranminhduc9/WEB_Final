/**
 * Auth Context - Global state management cho authentication
 */

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  useMemo,
  type ReactNode
} from 'react';
import { authService } from '../services';
import type { User, LoginRequest, RegisterRequest } from '../types';
import { isApiErrorResponse } from '../types/auth';

// Auth Context State
interface AuthContextState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (credentials: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;
  refreshUser: () => Promise<void>;
}

// Create context
const AuthContext = createContext<AuthContextState | undefined>(undefined);

// Provider Props
interface AuthProviderProps {
  children: ReactNode;
}

/**
 * Auth Provider Component
 */
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Computed
  const isAuthenticated = useMemo(() => !!user, [user]);

  /**
   * Initialize auth state on mount
   */
  useEffect(() => {
    const initAuth = async () => {
      try {
        // Kiểm tra có token không
        if (authService.isAuthenticated()) {
          // Lấy user từ localStorage trước
          const storedUser = authService.getCurrentUser();
          if (storedUser) {
            setUser(storedUser);
          }

          // Fetch user mới nhất từ server (background)
          const freshUser = await authService.fetchCurrentUser();
          if (freshUser) {
            setUser(freshUser);
          } else if (!storedUser) {
            // Không có user nào, clear auth
            await authService.logout();
          }
        }
      } catch (err) {
        console.error('Auth init error:', err);
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  /**
   * Listen for auth events
   */
  useEffect(() => {
    const handleLogout = () => {
      setUser(null);
      setError(null);
    };

    const handleLogin = (event: CustomEvent<User>) => {
      setUser(event.detail);
    };

    const handleUserUpdated = (event: CustomEvent<User>) => {
      setUser(event.detail);
    };

    window.addEventListener('auth:logout', handleLogout);
    window.addEventListener('auth:login', handleLogin as EventListener);
    window.addEventListener('user:updated', handleUserUpdated as EventListener);

    return () => {
      window.removeEventListener('auth:logout', handleLogout);
      window.removeEventListener('auth:login', handleLogin as EventListener);
      window.removeEventListener('user:updated', handleUserUpdated as EventListener);
    };
  }, []);

  /**
   * Login
   */
  const login = useCallback(async (credentials: LoginRequest) => {
    // Guard against concurrent login attempts
    if (isLoading) {
      console.warn('Login already in progress');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await authService.login(credentials);
      // authService.login đã normalize và lưu vào localStorage
      // Lấy lại normalized user để đảm bảo có avatar alias
      if (response.user) {
        const normalizedUser = authService.getCurrentUser();
        setUser(normalizedUser || response.user);
      }
    } catch (err) {
      // Xử lý error từ axios interceptor (ApiErrorResponse object)
      let message = 'Đăng nhập thất bại';
      if (isApiErrorResponse(err)) {
        message = err.error?.message || message;
      } else if (err instanceof Error) {
        message = err.message;
      }
      setError(message);
      // Don't re-throw - let the component handle the error through context.error
    } finally {
      setIsLoading(false);
    }
  }, [isLoading]);

  /**
   * Register
   */
  const register = useCallback(async (data: RegisterRequest) => {
    // Guard against concurrent register attempts
    if (isLoading) {
      console.warn('Registration already in progress');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      await authService.register(data);
      // Không tự động login sau register, user cần verify email
    } catch (err) {
      // Xử lý error từ axios interceptor (ApiErrorResponse object)
      let message = 'Đăng ký thất bại';
      if (isApiErrorResponse(err)) {
        message = err.error?.message || message;
      } else if (err instanceof Error) {
        message = err.message;
      }
      setError(message);
      // Don't re-throw - let the component handle the error through context.error
    } finally {
      setIsLoading(false);
    }
  }, [isLoading]);

  /**
   * Logout
   */
  const logout = useCallback(async () => {
    setIsLoading(true);

    try {
      await authService.logout();
      setUser(null);
      setError(null);
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Clear error
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  /**
   * Refresh user data
   */
  const refreshUser = useCallback(async () => {
    const freshUser = await authService.fetchCurrentUser();
    if (freshUser) {
      setUser(freshUser);
    }
  }, []);

  // Context value
  const value = useMemo<AuthContextState>(() => ({
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    register,
    logout,
    clearError,
    refreshUser,
  }), [user, isAuthenticated, isLoading, error, login, register, logout, clearError, refreshUser]);

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

/**
 * Custom hook để sử dụng Auth Context
 */
export const useAuthContext = (): AuthContextState => {
  const context = useContext(AuthContext);

  if (context === undefined) {
    throw new Error('useAuthContext must be used within an AuthProvider');
  }

  return context;
};

export default AuthContext;

