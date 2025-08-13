// src/components/Sidebar.jsx
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../lib/auth";
import {
  HomeIcon,
  CalendarDaysIcon,
  UserIcon,
  BuildingOfficeIcon,
  ArrowRightEndOnRectangleIcon,
} from "@heroicons/react/24/outline"; // ✅ replaced deprecated icon

export default function Sidebar({ onClose }) {
  const { user, logout } = useAuth();
  const location = useLocation();

  const navItems = [
    { to: "/", label: "Home", icon: HomeIcon },
    { to: "/my-bookings", label: "My Bookings", icon: CalendarDaysIcon },
    { to: "/profile", label: "Profile", icon: UserIcon },
  ];

  if (user?.role === "admin") {
    navItems.push({
      to: "/admin/hotels",
      label: "Manage Hotels",
      icon: BuildingOfficeIcon,
    });
  }

  return (
    <aside className="bg-gray-900 text-white w-64 min-h-screen flex flex-col shadow-lg">
      <div className="p-4 border-b border-gray-700 text-lg font-bold tracking-wide">
        Hotel Booking
      </div>

      <nav className="flex-1 p-2 space-y-1">
        {navItems.map(({ to, label, icon: Icon }) => {
          const isActive =
            location.pathname === to || location.pathname.startsWith(to + "/");
          return (
            <Link
              key={to}
              to={to}
              className={`flex items-center gap-3 px-4 py-2 rounded-md transition ${
                isActive
                  ? "bg-indigo-600 text-white"
                  : "hover:bg-gray-800 text-gray-300"
              }`}
              onClick={onClose}
            >
              {Icon && <Icon className="w-5 h-5" />}
              {label}
            </Link>
          );
        })}
      </nav>

      <button
        onClick={() => {
          logout();
          onClose?.();
        }}
        className="flex items-center gap-3 px-4 py-3 border-t border-gray-800 hover:bg-gray-800 transition text-gray-300"
      >
        <ArrowRightEndOnRectangleIcon className="w-5 h-5" />
        Logout
      </button>
    </aside>
  );
}
