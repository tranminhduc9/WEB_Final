/**
 * Protected Route - Yêu cầu đăng nhập để truy cập
 */

import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthContext } from '../contexts';

interface ProtectedRouteProps {
  children: React.ReactNode;
  redirectTo?: string;
}

/**
 * Route component yêu cầu user phải đăng nhập
 * Nếu chưa đăng nhập, redirect về login page
 */
export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  redirectTo = '/login'
}) => {
  const { isAuthenticated, isLoading } = useAuthContext();
  const location = useLocation();

  // Đang loading, hiển thị loading indicator
  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  // Chưa đăng nhập, redirect về login
  if (!isAuthenticated) {
    // Lưu current location để redirect lại sau khi login
    return <Navigate to={redirectTo} state={{ from: location }} replace />;
  }

  // Đã đăng nhập, render children
  return <>{children}</>;
};

export default ProtectedRoute;

