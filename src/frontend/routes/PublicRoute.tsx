/**
 * Public Route - Route dành cho khách (chưa đăng nhập)
 * Nếu đã đăng nhập thì redirect đi
 */

import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthContext } from '../contexts';

interface PublicRouteProps {
  children: React.ReactNode;
  redirectTo?: string;
}

/**
 * Route component cho các trang public (login, register)
 * Nếu user đã đăng nhập, redirect về trang chủ hoặc trang trước đó
 */
export const PublicRoute: React.FC<PublicRouteProps> = ({
  children,
  redirectTo = '/'
}) => {
  const { isAuthenticated, isLoading } = useAuthContext();
  const location = useLocation();

  // Đang loading
  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  // Đã đăng nhập, redirect đi
  if (isAuthenticated) {
    // Kiểm tra xem có location.state.from không (từ ProtectedRoute)
    const from = (location.state as { from?: { pathname: string } })?.from?.pathname || redirectTo;
    return <Navigate to={from} replace />;
  }

  // Chưa đăng nhập, render children
  return <>{children}</>;
};

export default PublicRoute;

