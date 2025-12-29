import { StrictMode } from 'react'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import ReactDOM from 'react-dom/client'

// Contexts
import { AuthProvider } from './contexts'

// Route Guards
import { ProtectedRoute, PublicRoute, AdminRoute } from './routes'

// Pages
import Login from './pages/client/Login'
import Register from './pages/client/Register'
import ForgotPassword from './pages/client/ForgotPassword'
import ResetPassword from './pages/client/ResetPassword'
import SearchResultsPage from './pages/client/SearchResultsPage'
import TrendPlacesPage from './pages/client/TrendPlacesPage'
import PlacesPage from './pages/client/PlacesPage'
import UserProfilePage from './pages/client/UserProfilePage'
import BlogPage from './pages/client/BlogPage'
import BlogDetailPage from './pages/client/BlogDetailPage'
import LocationInfoPage from './pages/client/LocationInfoPage'
import FavoritePlacesPage from './pages/client/FavoritePlacesPage'
import UserPostsPage from './pages/client/UserPostsPage'
import AdminHomePage from './pages/admin/AdminHomePage'
import AdminUsersPage from './pages/admin/AdminUsersPage'
import AdminLocationsPage from './pages/admin/AdminLocationsPage'
import AdminAddPlacePage from './pages/admin/AdminAddPlacePage'
import AdminReportsPage from './pages/admin/AdminReportsPage'
import AdminSQLPage from './pages/admin/AdminSQLPage'

// Components
import Chatbot from './components/client/Chatbot'

// Styles
import './index.css'
import App from './App'

const router = createBrowserRouter([
  // Public routes
  { path: '/', element: <App /> },
  { path: '/search', element: <SearchResultsPage /> },
  { path: '/trend-places', element: <TrendPlacesPage /> },
  { path: '/places', element: <PlacesPage /> },
  { path: '/blogs', element: <BlogPage /> },
  { path: '/blog/:id', element: <BlogDetailPage /> },
  { path: '/location/:id', element: <LocationInfoPage /> },

  // Auth routes (redirect if already logged in)
  {
    path: '/login',
    element: (
      <PublicRoute>
        <Login />
      </PublicRoute>
    )
  },
  {
    path: '/register',
    element: (
      <PublicRoute>
        <Register />
      </PublicRoute>
    )
  },
  {
    path: '/forgot-password',
    element: (
      <PublicRoute>
        <ForgotPassword />
      </PublicRoute>
    )
  },
  {
    path: '/reset-password',
    element: (
      <PublicRoute>
        <ResetPassword />
      </PublicRoute>
    )
  },

  // Protected routes (require authentication)
  {
    path: '/profile',
    element: (
      <ProtectedRoute>
        <UserProfilePage />
      </ProtectedRoute>
    )
  },
  {
    path: '/places/favourite',
    element: (
      <ProtectedRoute>
        <FavoritePlacesPage />
      </ProtectedRoute>
    )
  },
  {
    path: '/posts/user',
    element: (
      <ProtectedRoute>
        <UserPostsPage />
      </ProtectedRoute>
    )
  },

  // Public user profile route (view other users)
  { path: '/user/:id', element: <UserProfilePage /> },

  // Admin routes (require admin role)
  {
    path: '/admin',
    element: (
      <AdminRoute>
        <AdminHomePage />
      </AdminRoute>
    )
  },
  {
    path: '/admin/statistics',
    element: (
      <AdminRoute>
        <AdminHomePage />
      </AdminRoute>
    )
  },
  {
    path: '/admin/users',
    element: (
      <AdminRoute>
        <AdminUsersPage />
      </AdminRoute>
    )
  },
  {
    path: '/admin/locations',
    element: (
      <AdminRoute>
        <AdminLocationsPage />
      </AdminRoute>
    )
  },
  {
    path: '/admin/locations/add',
    element: (
      <AdminRoute>
        <AdminAddPlacePage />
      </AdminRoute>
    )
  },
  {
    path: '/admin/reports',
    element: (
      <AdminRoute>
        <AdminReportsPage />
      </AdminRoute>
    )
  },
  {
    path: '/admin/sql',
    element: (
      <AdminRoute>
        <AdminSQLPage />
      </AdminRoute>
    )
  },
]);

ReactDOM.createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AuthProvider>
      <RouterProvider router={router} />
      <Chatbot />
    </AuthProvider>
  </StrictMode>
);
