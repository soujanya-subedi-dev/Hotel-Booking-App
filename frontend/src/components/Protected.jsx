import { Navigate, Outlet } from 'react-router-dom';
import { isLoggedIn, getUser } from '../lib/auth';

export function Protected() {
  if (!isLoggedIn()) return <Navigate to="/login" replace />;
  return <Outlet />;
}

export function AdminOnly() {
  if (!isLoggedIn()) return <Navigate to="/login" replace />;
  const u = getUser();
  if (u?.role !== 'admin') return <Navigate to="/" replace />;
  return <Outlet />;
}
