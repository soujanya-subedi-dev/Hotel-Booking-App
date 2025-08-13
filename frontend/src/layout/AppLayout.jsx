// AppLayout.jsx
import { Outlet } from "react-router-dom";
import { useAuth } from "../lib/auth";
import Sidebar from "../components/Sidebar";

export default function AppLayout() {
  const { user } = useAuth();

  if (!user) return <Outlet />; // No sidebar for guests

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 bg-gray-50 p-6 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}
