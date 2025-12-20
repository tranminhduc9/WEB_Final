/**
 * Admin Route - Yêu cầu quyền admin để truy cập
 */

import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthContext } from '../contexts';
import type { UserRole } from '../types';

interface AdminRouteProps {
  children: React.ReactNode;
  allowedRoles?: UserRole[];
  redirectTo?: string;
  unauthorizedRedirect?: string;
}

/**
 * Route component yêu cầu user phải có quyền admin hoặc roles được chỉ định
 * - Nếu chưa đăng nhập: redirect về login
 * - Nếu đăng nhập nhưng không đủ quyền: redirect về trang unauthorized
 */
export const AdminRoute: React.FC<AdminRouteProps> = ({ 
  children, 
  allowedRoles = ['admin'],
  redirectTo = '/login',
  unauthorizedRedirect = '/'
}) => {
  const { user, isAuthenticated, isLoading } = useAuthContext();
  const location = useLocation();

  // Đang loading
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  // Chưa đăng nhập
  if (!isAuthenticated) {
    return <Navigate to={redirectTo} state={{ from: location }} replace />;
  }

  // Kiểm tra quyền
  if (!user || !allowedRoles.includes(user.role)) {
    // Không đủ quyền, redirect về trang chủ hoặc trang unauthorized
    return <Navigate to={unauthorizedRedirect} replace />;
  }

  // Đủ quyền, render children
  return <>{children}</>;
};

/**
 * Shorthand cho Admin only route
 */
export const AdminOnlyRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return <AdminRoute allowedRoles={['admin']}>{children}</AdminRoute>;
};

/**
 * Shorthand cho Moderator route (admin + moderator)
 */
export const ModeratorRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return <AdminRoute allowedRoles={['admin', 'moderator']}>{children}</AdminRoute>;
};

export default AdminRoute;

