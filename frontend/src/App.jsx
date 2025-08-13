//app.jsx

import { Outlet, Link, useLocation } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { isLoggedIn, getUser, logout } from './lib/auth';

function NavLink({ to, children }) {
  const { pathname } = useLocation();
  const active = pathname === to;
  return (
    <Link
      to={to}
      className={`text-sm px-2 py-1.5 rounded-md hover:bg-gray-100 ${active ? 'bg-gray-100 font-medium' : ''}`}
    >
      {children}
    </Link>
  );
}

export default function App(){
  const user = getUser();

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <Toaster position="top-right" />
      <header className="sticky top-0 z-40 border-b bg-white/80 backdrop-blur">
        <div className="max-w-6xl mx-auto flex items-center justify-between p-4">
          <Link to="/" className="text-xl font-semibold tracking-tight">
            <span className="inline-block bg-gradient-to-r from-black to-gray-700 bg-clip-text text-transparent">Hotel Booking</span>
          </Link>
          <nav className="flex items-center gap-1">
            <NavLink to="/">Home</NavLink>

            {isLoggedIn() && (
              <>
                <NavLink to="/my-bookings">My Bookings</NavLink>
                <NavLink to="/profile">Profile</NavLink>
                {user?.role === 'admin' && <NavLink to="/admin">Admin</NavLink>}
                <span className="hidden sm:inline text-xs text-gray-500 px-2">({user?.email})</span>
                <button onClick={logout} className="text-sm px-3 py-1.5 border rounded-md hover:bg-gray-100">Logout</button>
              </>
            )}

            {!isLoggedIn() && (
              <>
                <NavLink to="/login">Login</NavLink>
                <Link to="/register" className="text-sm px-3 py-1.5 rounded-md border bg-white hover:bg-gray-50">
                  Register
                </Link>
              </>
            )}
          </nav>
        </div>
      </header>

      <main className="max-w-6xl mx-auto p-4">
        <Outlet />
      </main>

      <footer className="border-t mt-10">
        <div className="max-w-6xl mx-auto p-4 text-xs text-gray-500">
          © {new Date().getFullYear()} Hotel Booking — Crafted for performance.
        </div>
      </footer>
    </div>
  );
}
