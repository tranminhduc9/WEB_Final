import { StrictMode } from 'react'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import ReactDOM from 'react-dom/client'

// Contexts
import { AuthProvider } from './contexts'

// Route Guards
import { ProtectedRoute, PublicRoute } from './routes'

// Pages
import Login from './pages/client/Login'
import Register from './pages/client/Register'
import SearchResultsPage from './pages/client/SearchResultsPage'
import TrendPlacesPage from './pages/client/TrendPlacesPage'
import UserProfilePage from './pages/client/UserProfilePage'
import BlogPage from './pages/client/BlogPage'
import BlogDetailPage from './pages/client/BlogDetailPage'
import LocationInfoPage from './pages/client/LocationInfoPage'
import AdminHomePage from './pages/admin/AdminHomePage'
import AdminUsersPage from './pages/admin/AdminUsersPage'
import AdminLocationsPage from './pages/admin/AdminLocationsPage'
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

  // Protected routes (require authentication)
  {
    path: '/profile',
    element: (
      <ProtectedRoute>
        <UserProfilePage />
      </ProtectedRoute>
    )
  },

  // Admin routes
  { path: '/admin', element: <AdminHomePage /> },
  { path: '/admin/statistics', element: <AdminHomePage /> },
  { path: '/admin/users', element: <AdminUsersPage /> },
  { path: '/admin/locations', element: <AdminLocationsPage /> },
  { path: '/admin/reports', element: <AdminReportsPage /> },
  { path: '/admin/sql', element: <AdminSQLPage /> },
]);

ReactDOM.createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AuthProvider>
      <RouterProvider router={router} />
      <Chatbot />
    </AuthProvider>
  </StrictMode>
);
