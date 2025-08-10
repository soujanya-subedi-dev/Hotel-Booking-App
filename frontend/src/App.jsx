import { Outlet, Link, useNavigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { isLoggedIn, getUser, logout } from './lib/auth';

export default function App(){
  const _nav = useNavigate();
  const user = getUser();

  return (
    <div className="min-h-screen bg-gray-50">
      <Toaster position="top-right" />
      <header className="sticky top-0 z-40 border-b bg-white/80 backdrop-blur">
        <div className="max-w-6xl mx-auto flex items-center justify-between p-4">
          <Link to="/" className="text-xl font-semibold tracking-tight">Hotel Booking</Link>
          <nav className="flex items-center gap-3">
            <Link to="/" className="text-sm hover:underline">Home</Link>
            {isLoggedIn() ? (
              <>
                <Link to="/my-bookings" className="text-sm hover:underline">My Bookings</Link>
                <span className="text-xs text-gray-500 hidden sm:inline">({user?.email})</span>
                <button onClick={logout} className="text-sm px-3 py-1.5 border rounded">Logout</button>
              </>
            ) : (
              <>
                <Link to="/login" className="text-sm">Login</Link>
                <Link to="/register" className="text-sm px-3 py-1.5 border rounded">Register</Link>
              </>
            )}
          </nav>
        </div>
      </header>
      <main className="max-w-6xl mx-auto p-4">
        <Outlet />
      </main>
    </div>
  );
}
