/**
 * useAuth Hook - Wrapper cho AuthContext với thêm utilities
 */

import { useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthContext } from '../contexts';
import { getUserRole, hasRole as checkHasRole, hasAnyRole as checkHasAnyRole } from '../types/auth';
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
    return checkHasRole(context.user, role);
  }, [context.user]);

  /**
   * Kiểm tra user có một trong các roles
   */
  const hasAnyRole = useCallback((roles: UserRole[]): boolean => {
    return checkHasAnyRole(context.user, roles);
  }, [context.user]);

  /**
   * Kiểm tra có phải admin
   */
  const isAdmin = useMemo(() => {
    return getUserRole(context.user) === 'admin';
  }, [context.user]);

  /**
   * Kiểm tra có phải moderator hoặc admin
   */
  const isModerator = useMemo(() => {
    const role = getUserRole(context.user);
    return role === 'moderator' || role === 'admin';
  }, [context.user]);

  /**
   * Kiểm tra user có thể access resource
   */
  const canAccess = useCallback((resourceOwnerId: number): boolean => {
    if (!context.user) return false;
    if (getUserRole(context.user) === 'admin') return true;
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

