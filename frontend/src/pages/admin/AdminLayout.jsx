// AdminLayout.jsx
import { Outlet } from 'react-router-dom';
import Sidebar from "../../components/Sidebar"; // adjust path if needed

export default function AdminLayout() {
  return (
    <div className="flex min-h-[70vh]">
      {/* Sidebar always visible */}
      <Sidebar role="admin" /> 
      <main className="flex-1 p-4 bg-gray-50 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}
