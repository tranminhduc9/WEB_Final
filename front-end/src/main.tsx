import { StrictMode } from 'react'
import { createBrowserRouter, RouterProvider } from 'react-router'
import ReactDOM from 'react-dom/client'
import Login from './pages/Login.tsx'
import Register from './pages/Register.tsx'
import SearchResultsPage from './pages/SearchResultsPage.tsx'
import TrendPlacesPage from './pages/TrendPlacesPage.tsx'
import UserProfilePage from './pages/UserProfilePage.tsx'
import BlogPage from './pages/BlogPage.tsx'
import './index.css'
import App from './App.tsx'

const router = createBrowserRouter([
  { path: '/', element: <App /> },
  { path: '/login', element: <Login /> },
  { path: '/register', element: <Register /> },
  { path: '/search', element: <SearchResultsPage /> },
  { path: '/trend-places', element: <TrendPlacesPage /> },
  { path: '/profile', element: <UserProfilePage /> },
  { path: '/blogs', element: <BlogPage /> },
]);

ReactDOM.createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>
);