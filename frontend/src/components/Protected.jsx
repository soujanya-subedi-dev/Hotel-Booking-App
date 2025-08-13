import { Navigate, Outlet } from 'react-router-dom';
import { isLoggedIn, getUser } from '../lib/auth';

export function Protected() {
  const ok = isLoggedIn();
  if (!ok) return <Navigate to="/login" replace />;
  return <Outlet />;
}

export function AdminOnly() {
  const user = getUser();
  if (!user) return <Navigate to="/login" replace />;
  if (user.role !== 'admin') return <Navigate to="/" replace />;
  return <Outlet />;
}
