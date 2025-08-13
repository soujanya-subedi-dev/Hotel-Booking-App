//main.jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import './index.css'

import AppLayout from './layout/AppLayout.jsx'
import App from './App.jsx'
import Home from './pages/Home.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import HotelDetail from './pages/HotelDetail.jsx'
import MyBookings from './pages/MyBookings.jsx'
import Profile from './pages/Profile.jsx'
import AdminLayout from './pages/admin/AdminLayout.jsx'
import AdminHotels from './pages/admin/AdminHotels.jsx'
import AdminHotelDetail from './pages/admin/AdminHotelDetail.jsx'
import { Protected, AdminOnly } from './components/Protected.jsx'

const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      { index: true, element: <Home /> },
      { path: 'login', element: <Login /> },
      { path: 'register', element: <Register /> },
      { path: 'hotels/:id', element: <HotelDetail /> },
      {
        element: <Protected />,
        children: [
          {
            element: <AppLayout />, // ✅ Sidebar for logged-in users
            children: [
              { path: 'my-bookings', element: <MyBookings /> },
              { path: 'profile', element: <Profile /> },
            ]
          }
        ]
      },
      {
        element: <AdminOnly />,
        children: [
          {
            path: 'admin',
            element: <AdminLayout />, // ✅ AdminLayout should import Sidebar
            children: [
              { index: true, element: <AdminHotels /> },
              { path: 'hotels', element: <AdminHotels /> },
              { path: 'hotels/:id', element: <AdminHotelDetail /> },
            ]
          }
        ]
      },
    ]
  }
])

const qc = new QueryClient()
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <QueryClientProvider client={qc}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  </React.StrictMode>
)
