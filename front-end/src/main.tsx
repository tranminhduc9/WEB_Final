import { StrictMode } from 'react'
import { createBrowserRouter, RouterProvider } from 'react-router'
import ReactDOM from 'react-dom/client'
import Login from './pages/Login.tsx'
import Register from './pages/Register.tsx'
import SearchResultsPage from './pages/SearchResultsPage.tsx'
import './index.css'
import App from './App.tsx'

const router = createBrowserRouter([
  { path: '/', element: <App /> },
  { path: '/login', element: <Login /> },
  { path: '/register', element: <Register /> },
  { path: '/search', element: <SearchResultsPage /> },
]);

ReactDOM.createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>
);