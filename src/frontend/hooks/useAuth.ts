/**
 * useAuth Hook - Wrapper cho AuthContext với thêm utilities
 */

import { useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthContext } from '../contexts';
import { authService } from '../services';
import type { UserRole } from '../types';

/**
 * Custom hook cho authentication
 */
export const useAuth = () => {
  const context = useAuthContext();
  const navigate = useNavigate();

  /**
   * Login và redirect
   */
  const loginAndRedirect = useCallback(async (
    email: string,
    password: string,
    redirectTo: string = '/'
  ) => {
    await context.login({ email, password });
    navigate(redirectTo);
  }, [context, navigate]);

  /**
   * Logout và redirect về login
   */
  const logoutAndRedirect = useCallback(async () => {
    await context.logout();
    navigate('/login');
  }, [context, navigate]);

  /**
   * Kiểm tra user có role cụ thể
   */
  const hasRole = useCallback((role: UserRole): boolean => {
    return context.user?.role === role;
  }, [context.user]);

  /**
   * Kiểm tra user có một trong các roles
   */
  const hasAnyRole = useCallback((roles: UserRole[]): boolean => {
    return !!context.user && roles.includes(context.user.role);
  }, [context.user]);

  /**
   * Kiểm tra có phải admin
   */
  const isAdmin = useMemo(() => {
    return context.user?.role === 'admin';
  }, [context.user]);

  /**
   * Kiểm tra có phải moderator hoặc admin
   */
  const isModerator = useMemo(() => {
    return context.user?.role === 'moderator' || context.user?.role === 'admin';
  }, [context.user]);

  /**
   * Kiểm tra user có thể access resource
   */
  const canAccess = useCallback((resourceOwnerId: string): boolean => {
    if (!context.user) return false;
    if (context.user.role === 'admin') return true;
    return context.user.id === resourceOwnerId;
  }, [context.user]);

  return {
    // From context
    ...context,
    
    // Extended methods
    loginAndRedirect,
    logoutAndRedirect,
    hasRole,
    hasAnyRole,
    isAdmin,
    isModerator,
    canAccess,
  };
};

export default useAuth;

