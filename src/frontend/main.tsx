import { StrictMode } from 'react'
import { createBrowserRouter, RouterProvider } from 'react-router'
import ReactDOM from 'react-dom/client'
import Login from './pages/client/Login.tsx'
import Register from './pages/client/Register.tsx'
import SearchResultsPage from './pages/client/SearchResultsPage.tsx'
import TrendPlacesPage from './pages/client/TrendPlacesPage.tsx'
import UserProfilePage from './pages/client/UserProfilePage.tsx'
import BlogPage from './pages/client/BlogPage.tsx'
import BlogDetailPage from './pages/client/BlogDetailPage.tsx'
import Chatbot from './components/client/Chatbot.tsx'
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
  { path: '/blog/:id', element: <BlogDetailPage /> },
]);

ReactDOM.createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <RouterProvider router={router} />
    <Chatbot />
  </StrictMode>
);